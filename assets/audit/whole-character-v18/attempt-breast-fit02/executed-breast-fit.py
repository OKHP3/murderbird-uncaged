"""Refit breast access ribs and the top course on the pinned V17 attempt02.

This bounded patch retains the shell/armor envelope, existing object names,
owners, materials, era tags, and every articulation transform. The transverse
ribs are drawn onto the cavity side of the actual rounded shell where they
previously crossed it. The first armor course is shortened toward its lower
edge while retaining its lower tips; its fixing heads follow that same fitted
surface so the crown/neck seam is exposed as a continuous shell margin.
"""
from pathlib import Path
import hashlib
import math

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


EXPECTED_NATIVE_SHA256 = "7d371907b279eb3d625e67164d84a78b2901a5cb6a79917def07f48ff8792d7b"
RIB_NAMES = ("Passive rib behind access cover.002", "Passive rib behind access cover.003")
RAIL_NAMES = ("Curved thoracic load rail", "Curved thoracic load rail.001")
TOP_COURSE_NAME = "V17 breast directional lamina 1"
TOP_COURSE_SCALE = 0.45
RIB_CLEARANCE = 0.006


def _sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _scene_pivots():
    return {o.name: (o.parent.name if o.parent else None, o.matrix_world.copy())
            for o in bpy.data.objects if o.type == "EMPTY"}


def _same_matrix(a, b, eps=1e-8):
    return all(abs(a[r][c] - b[r][c]) <= eps for r in range(4) for c in range(4))


def _surface(obj):
    deps = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(deps)
    mesh = ev.to_mesh()
    mesh.calc_loop_triangles()
    points = [ev.matrix_world @ v.co for v in mesh.vertices]
    tris = [tuple(t.vertices) for t in mesh.loop_triangles]
    ev.to_mesh_clear()
    return BVHTree.FromPolygons(points, tris, all_triangles=True, epsilon=0.0)


def _shell_back_hit(tree, x, z):
    # +Y is the cavity/rear side in the authored Blender coordinates.
    loc, normal, _face, _distance = tree.ray_cast(Vector((x, 1.0, z)),
                                                  Vector((0.0, -1.0, 0.0)), 3.0)
    return loc, normal


def _shell_front_hit(tree, x, z):
    loc, normal, _face, _distance = tree.ray_cast(Vector((x, -1.0, z)),
                                                  Vector((0.0, 1.0, 0.0)), 3.0)
    return loc, normal


def _fitted_point(tree, x, z, normal_offset):
    loc, normal = _shell_front_hit(tree, x, z)
    assert loc is not None and normal is not None, (
        f"The rounded access shell has no rear-side section at x={x:.5f}, z={z:.5f}")
    normal.normalize()
    # Preserve the front-facing exterior side, oriented toward -Y.
    if normal.y > 0:
        normal.negate()
    return loc + normal * normal_offset


def _fit_passive_rib(obj, shell_tree, rail_trees):
    assert obj.data.users == 1, f"Refusing to deform shared rib mesh: {obj.name}"
    original = [obj.matrix_world @ v.co for v in obj.data.vertices]
    inv = obj.matrix_world.inverted()
    moved = 0
    anchored = 0
    maximum = 0.0
    displacements = []
    for vertex, point in zip(obj.data.vertices, original):
        # The outer rail joints are the load path. Keep every point with real
        # contact to either rail fixed, and refit only the unsupported anterior
        # arc that was passing through the access shell.
        near_rail = False
        for rail in rail_trees:
            nearest = rail.find_nearest(point)
            if nearest[0] is not None and nearest[3] <= 0.005:
                near_rail = True
                break
        if near_rail:
            anchored += 1
            displacements.append(0.0)
            continue
        loc, normal = _shell_back_hit(shell_tree, point.x, point.z)
        if loc is None:
            displacements.append(0.0)
            continue
        desired_y = loc.y + RIB_CLEARANCE
        delta_y = max(0.0, desired_y - point.y)
        if delta_y <= 1e-7:
            displacements.append(0.0)
            continue
        fitted = Vector((point.x, desired_y, point.z))
        vertex.co = inv @ fitted
        moved += 1
        maximum = max(maximum, delta_y)
        displacements.append(delta_y)
    obj.data.update()
    assert anchored > 0 and moved > 0, f"No rib support contacts or fit points found for {obj.name}"
    return {"name": obj.name, "owner": obj.parent.name if obj.parent else None,
            "vertices": len(original), "verticesRefit": moved, "railContactVerticesPreserved": anchored,
            "maximumPosteriorFitShiftM": maximum,
            "meanShiftAmongRefitVerticesM": sum(displacements) / max(1, moved),
            "railSupportOwners": list(RAIL_NAMES), "clearanceTargetM": RIB_CLEARANCE}


def _fit_top_course(tree, obj):
    assert obj.data.users == 1 and obj.parent and obj.parent.name == "breastplate"
    original = [obj.matrix_world @ v.co for v in obj.data.vertices]
    low = min(p.z for p in original)
    high = max(p.z for p in original)
    inv = obj.matrix_world.inverted()
    for vertex, point in zip(obj.data.vertices, original):
        new_z = low + TOP_COURSE_SCALE * (point.z - low)
        old_loc, old_normal = _shell_front_hit(tree, point.x, point.z)
        assert old_loc is not None and old_normal is not None
        old_normal.normalize()
        # Store the authored plate stand-off relative to the actual shell, then
        # remap that point to the same shell at its shortened course height.
        offset = (point - old_loc).dot(old_normal)
        fitted = _fitted_point(tree, point.x, new_z, offset)
        vertex.co = inv @ fitted
    obj.data.update()
    new_points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return {"name": obj.name, "owner": obj.parent.name, "vertices": len(original),
            "originalZBoundsM": [low, high],
            "fittedZBoundsM": [min(p.z for p in new_points), max(p.z for p in new_points)],
            "heightScale": TOP_COURSE_SCALE,
            "intent": "upper edge recedes to a continuous shell margin; course lower tips remain anchored"}


def _fit_first_course_fasteners(tree, anchor_obj, plate_bounds):
    assert anchor_obj.data.users == 1 and anchor_obj.parent.name == "breastplate"
    sides_per_course = 8
    points = [anchor_obj.matrix_world @ v.co for v in anchor_obj.data.vertices]
    assert len(points) == 78 * 24, f"Unexpected fastener vertex grouping: {len(points)}"
    inv = anchor_obj.matrix_world.inverted()
    records = []
    group_cursor = 0
    # _anchor_geometry emits four columns, with two 24-vertex heads per column.
    for column in range(4):
        for side in ("left", "right"):
            lo, hi = group_cursor * 24, (group_cursor + 1) * 24
            group = points[lo:hi]
            low = plate_bounds[(column, side)][0]
            high = plate_bounds[(column, side)][1]
            fitted_group = []
            for point in group:
                new_z = low + TOP_COURSE_SCALE * (point.z - low)
                loc, normal = _shell_front_hit(tree, point.x, new_z)
                assert loc is not None and normal is not None
                normal.normalize()
                if normal.y > 0:
                    normal.negate()
                # A low-profile head remains seated on the shortened plate row.
                fitted_group.append(loc + normal * 0.008)
            for index, new_point in enumerate(fitted_group, start=lo):
                anchor_obj.data.vertices[index].co = inv @ new_point
            records.append({"column": column + 1, "side": side, "vertices": len(group),
                            "originalCourseZBoundsM": [low, high]})
            group_cursor += 1
    anchor_obj.data.update()
    assert group_cursor == sides_per_course
    return {"name": anchor_obj.name, "firstCourseHeadsRefit": sides_per_course,
            "allHeadGroups": 78, "firstCourseHeadVertices": sides_per_course * 24,
            "records": records}


def apply():
    native = Path(bpy.data.filepath)
    assert native.is_file() and _sha(native) == EXPECTED_NATIVE_SHA256, (
        "V18 breast fit requires exact V17 attempt02 native")
    shell = bpy.data.objects.get("Breast inner access shell")
    assert shell and shell.parent and shell.parent.name == "breastplate"
    ribs = [bpy.data.objects.get(name) for name in RIB_NAMES]
    rails = [bpy.data.objects.get(name) for name in RAIL_NAMES]
    assert all(o and o.type == "MESH" and o.parent and o.parent.name == "body" for o in ribs)
    assert all(o and o.type == "MESH" and o.parent and o.parent.name == "body" for o in rails)
    pivots_before = _scene_pivots()
    materials_before = sorted((m.name, len(m.node_tree.nodes) if m.node_tree else 0)
                              for m in bpy.data.materials)
    shell_tree = _surface(shell)
    rail_trees = [_surface(o) for o in rails]

    rib_reports = [_fit_passive_rib(obj, shell_tree, rail_trees) for obj in ribs]
    plate_reports = []
    plate_bounds = {}
    for column in range(4):
        for side in ("left", "right"):
            name = f"{TOP_COURSE_NAME} {column + 1} {side}"
            obj = bpy.data.objects.get(name)
            assert obj and obj.parent and obj.parent.name == "breastplate", f"Missing course mesh {name}"
            report = _fit_top_course(shell_tree, obj)
            plate_reports.append(report)
            plate_bounds[(column, side)] = report["originalZBoundsM"]
    fasteners = bpy.data.objects.get("V17 breast captive overlap fasteners")
    assert fasteners
    fastener_report = _fit_first_course_fasteners(shell_tree, fasteners, plate_bounds)

    bpy.context.view_layer.update()
    pivots_after = _scene_pivots()
    assert set(pivots_before) == set(pivots_after) and all(
        pivots_before[name][0] == pivots_after[name][0]
        and _same_matrix(pivots_before[name][1], pivots_after[name][1]) for name in pivots_before), (
        "V18 fit changed articulation pivots")
    materials_after = sorted((m.name, len(m.node_tree.nodes) if m.node_tree else 0)
                             for m in bpy.data.materials)
    assert materials_before == materials_after, "V18 fit changed material definitions"
    changed = [o.name for o in ribs + [bpy.data.objects[f"{TOP_COURSE_NAME} {c} {s}"]
              for c in range(1,5) for s in ("left","right")] + [fasteners]]
    return {
        "status": "V18 breast/frame fit proposal; pending strict movement and visual review",
        "sourceNative": {"path": native.as_posix(), "sha256": EXPECTED_NATIVE_SHA256},
        "changedObjects": changed,
        "ribFit": rib_reports,
        "topCourseFit": plate_reports,
        "fastenerFit": fastener_report,
        "ownership": {
            "passiveRibs": "body-owned frame retained; thoracic rail contact vertices preserved",
            "topCourseAndFasteners": "breastplate-owned passive surfaces retained and follow the existing inspection opening",
            "eraEligibility": "Existing maker,mechanic,builder tags preserved; no powered function added"
        },
        "preserved": ["all 52 pivots, parent graph and matrices", "material definitions and slots",
                      "historical authoring curves", "all mesh names and mesh counts",
                      "thoracic rail support-contact vertices", "breast shell visible envelope"],
        "limits": ["The fit is based on the authored V17 shell and rib geometry, not art metrology.",
                   "Strict checks cover supplied discrete runtime samples, not continuous collision or strength.",
                   "The lower neck/breast transition may still need a separately owned neck guard adjustment."]
    }
