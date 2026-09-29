"""Refit retained breast access ribs to the pinned V17 attempt02 shell.

This bounded patch retains the shell/armor envelope, existing object names,
owners, materials, era tags, and every articulation transform. The transverse
ribs are drawn onto the cavity side of the actual rounded shell where they
previously crossed it. V17 exterior plates stay intact; a separate neck-owned
module handles their mating lower guard edge.
"""
from pathlib import Path
import hashlib

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


EXPECTED_NATIVE_SHA256 = "7d371907b279eb3d625e67164d84a78b2901a5cb6a79917def07f48ff8792d7b"
RIB_NAMES = ("Passive rib behind access cover.002", "Passive rib behind access cover.003")
RAIL_NAMES = ("Curved thoracic load rail", "Curved thoracic load rail.001")
RIB_CLEARANCE = 0.006
RING_SIDES = 12


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


def _fit_passive_rib(obj, shell_tree, rail_trees):
    assert obj.data.users == 1, f"Refusing to deform shared rib mesh: {obj.name}"
    assert len(obj.data.vertices) % RING_SIDES == 0, f"Unexpected tube ring layout: {obj.name}"
    original = [obj.matrix_world @ v.co for v in obj.data.vertices]
    inv = obj.matrix_world.inverted()
    moved_rings = 0
    anchored_rings = 0
    maximum = 0.0
    displacements = []
    ring_count = len(obj.data.vertices) // RING_SIDES
    for ring in range(ring_count):
        start = ring * RING_SIDES
        indices = range(start, start + RING_SIDES)
        points = [original[i] for i in indices]
        center = sum(points, Vector()) / RING_SIDES
        # The outer rail joints are the load path. Keep every point with real
        # contact to either rail fixed, and refit only unsupported cross-section
        # rings. Translation preserves the tube section and its load path.
        near_rail = False
        for rail in rail_trees:
            nearest = rail.find_nearest(center)
            if nearest[0] is not None and nearest[3] <= 0.005:
                near_rail = True
                break
        if near_rail:
            anchored_rings += 1
            displacements.append(0.0)
            continue
        loc, normal = _shell_back_hit(shell_tree, center.x, center.z)
        if loc is None:
            displacements.append(0.0)
            continue
        desired_y = loc.y + RIB_CLEARANCE
        delta_y = max(0.0, desired_y - center.y)
        if delta_y <= 1e-7:
            displacements.append(0.0)
            continue
        for i in indices:
            obj.data.vertices[i].co = inv @ (original[i] + Vector((0.0, delta_y, 0.0)))
        moved_rings += 1
        maximum = max(maximum, delta_y)
        displacements.append(delta_y)
    obj.data.update()
    assert anchored_rings > 0 and moved_rings > 0, f"No rib support contacts or fit points found for {obj.name}"
    radii_before=[];radii_after=[]
    for ring in range(ring_count):
        indices=range(ring*RING_SIDES,(ring+1)*RING_SIDES)
        before=[original[i] for i in indices]
        after=[obj.matrix_world @ obj.data.vertices[i].co for i in indices]
        cb=sum(before,Vector())/RING_SIDES;ca=sum(after,Vector())/RING_SIDES
        radii_before.extend((p-cb).length for p in before)
        radii_after.extend((p-ca).length for p in after)
    max_section_error=max(abs(a-b) for a,b in zip(radii_before,radii_after))
    return {"name": obj.name, "owner": obj.parent.name if obj.parent else None,
            "vertices": len(original), "crossSectionRings": ring_count,
            "ringsRigidlyTranslated": moved_rings, "railContactRingsPreserved": anchored_rings,
            "maximumPosteriorFitShiftM": maximum,
            "meanShiftAmongRefitRingsM": sum(d for d in displacements if d > 0) / max(1, moved_rings),
            "maximumCrossSectionRadiusChangeM": max_section_error,
            "railSupportOwners": list(RAIL_NAMES), "clearanceTargetM": RIB_CLEARANCE}


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
    bpy.context.view_layer.update()
    pivots_after = _scene_pivots()
    assert set(pivots_before) == set(pivots_after) and all(
        pivots_before[name][0] == pivots_after[name][0]
        and _same_matrix(pivots_before[name][1], pivots_after[name][1]) for name in pivots_before), (
        "V18 fit changed articulation pivots")
    materials_after = sorted((m.name, len(m.node_tree.nodes) if m.node_tree else 0)
                             for m in bpy.data.materials)
    assert materials_before == materials_after, "V18 fit changed material definitions"
    changed = [o.name for o in ribs]
    return {
        "status": "V18 breast/frame fit proposal; pending strict movement and visual review",
        "sourceNative": {"path": native.as_posix(), "sha256": EXPECTED_NATIVE_SHA256},
        "changedObjects": changed,
        "ribFit": rib_reports,
        "breastExterior": "All 78 plates and fixing geometry remain unchanged to preserve the rounded V17 envelope; neck-lap-fit owns the mating guard edge.",
        "ownership": {
            "passiveRibs": "body-owned frame retained; thoracic rail contact vertices preserved",
            "topCourseAndFasteners": "breastplate-owned passive surfaces retained and follow the existing inspection opening",
            "eraEligibility": "Existing maker,mechanic,builder tags preserved; no powered function added"
        },
        "preserved": ["all 52 pivots, parent graph and matrices", "material definitions and slots",
                      "historical authoring curves", "all mesh names, mesh counts and non-rib geometry",
                      "thoracic rail support-contact vertices", "breast shell and plate envelope"],
        "limits": ["The fit is based on the authored V17 shell and rib geometry, not art metrology.",
                   "Strict checks cover supplied discrete runtime samples, not continuous collision or strength.",
                   "The lower neck/breast transition may still need a separately owned neck guard adjustment."]
    }
