"""Bounded directional breast-course proposal for V21 envelope03.

Apply to the exact envelope03 native in memory. Replaces its three broad
breast guards with one recessed continuous backing and thirty finite,
breastplate-owned plates. The shared envelope, hinge, materials, pivots, and
all other scene objects remain untouched. Dimensions are reconstruction
proposals guided by the owner whole-bird image and selected Maker reference;
the images do not provide recoverable measurements.
"""

import hashlib
import math
from pathlib import Path

import bpy
from mathutils.bvhtree import BVHTree
from mathutils import Matrix, Vector


EXPECTED_NATIVE_SHA256 = "720c343645ef2de298a50e53c82fad66448c187b1eaf9311de2514cac079f280"
SOURCE_NATIVE = "assets/models/whole-character-v21/attempt-envelope03/murderbird-whole-character-v21.blend"
OWNER_REFERENCE = "context/threads/assets/murderbird-owner-likeness-rejection-2026-09-28/2-Pasted-Image-2.jpg"
MAKER_REFERENCE = "assets/img/library/murderbird-unified-maker-clean-candidate-2026-09-06.png"
STAGED_OUT = (
    "V21 breast central opening keel",
    "V21 anterior breast guard -1",
    "V21 anterior breast guard 1",
)
COURSE_COUNTS = (4, 5, 6, 6, 5, 4)
COURSE_Z = (1.350, 1.260, 1.170, 1.080, .990, .900)
ANGLE_LIMIT = 1.20
MAX_RELIEF = .012
ERAS = "maker,mechanic,builder"
PROFILE = ((.80, -.175, .130, .205), (.88, -.235, .160, .240),
           (1.00, -.370, .150, .285), (1.16, -.445, .120, .285),
           (1.30, -.420, .050, .255), (1.40, -.385, -.095, .170),
           (1.48, -.360, -.155, .120), (1.56, -.385, -.175, .105),
           (1.63, -.400, -.170, .110))


def _hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _pivot_signature():
    return {
        obj.name: (obj.parent.name if obj.parent else None, obj.matrix_world.copy())
        for obj in bpy.data.objects if obj.type == "EMPTY"
    }


def _same_pivots(before, tolerance=1e-8):
    after = _pivot_signature()
    if set(before) != set(after):
        return False
    return all(before[name][0] == after[name][0] and all(
        abs(before[name][1][row][column] - after[name][1][row][column]) <= tolerance
        for row in range(4) for column in range(4)) for name in before)


def _sample(z, column):
    """Canonical shape-preserving cubic interpolation from envelope03."""
    xs = [row[0] for row in PROFILE]
    ys = [row[column] for row in PROFILE]
    if z <= xs[0]:
        return ys[0]
    if z >= xs[-1]:
        return ys[-1]
    h = [b - a for a, b in zip(xs, xs[1:])]
    slopes = [(b - a) / width for a, b, width in zip(ys, ys[1:], h)]
    tangents = [slopes[0]]
    for index in range(1, len(xs) - 1):
        if slopes[index - 1] * slopes[index] <= 0:
            tangents.append(0.0)
        else:
            w1 = 2 * h[index] + h[index - 1]
            w2 = h[index] + 2 * h[index - 1]
            tangents.append((w1 + w2) / (w1 / slopes[index - 1]
                                          + w2 / slopes[index]))
    tangents.append(slopes[-1])
    for index in range(len(xs) - 1):
        if xs[index] <= z <= xs[index + 1]:
            t = (z - xs[index]) / h[index]
            return ((2*t**3 - 3*t**2 + 1) * ys[index]
                    + (t**3 - 2*t**2 + t) * h[index] * tangents[index]
                    + (-2*t**3 + 3*t**2) * ys[index + 1]
                    + (t**3 - t**2) * h[index] * tangents[index + 1])
    raise AssertionError("canonical profile interpolation failed")


def _shared_edges(angle):
    # These are the original backing edges, not newly chosen coverage bounds.
    value = max(0.0, min(1.0, (abs(angle) - .46) / .74))
    weight = value * value * (3 - 2 * value)
    return 1.395 - .035 * weight, .890 + .005 * weight


def _surface_point(z, angle, radial_offset):
    front, rear, width = (_sample(z, field) for field in (1, 2, 3))
    center_y = (front + rear) * .5
    radius_y = (rear - front) * .5
    return Vector(((width + radial_offset) * math.sin(angle),
                   center_y - (radius_y + radial_offset) * math.cos(angle), z))


def _material_and_owner():
    owner = bpy.data.objects.get("breastplate")
    if owner is None or owner.type != "EMPTY":
        raise RuntimeError("Expected breastplate articulation owner is absent")
    for name in STAGED_OUT:
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != "MESH" or obj.parent != owner:
            raise RuntimeError("Unexpected breast guard ownership: " + name)
        if not obj.data.materials:
            raise RuntimeError("Breast guard has no inherited material: " + name)
    material = bpy.data.objects[STAGED_OUT[0]].data.materials[0]
    if any(bpy.data.objects[name].data.materials[0] != material for name in STAGED_OUT):
        raise RuntimeError("Expected shared material on the three replaced guards")
    return owner, material


def _make_surface(name, owner, material, vertices, faces, role, wall, layer):
    inverse = owner.matrix_world.inverted()
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata([inverse @ point for point in vertices], [], faces)
    mesh.update()
    if not mesh.vertices or not mesh.polygons:
        bpy.data.meshes.remove(mesh)
        raise RuntimeError("Generated empty breast surface: " + name)
    if any(not math.isfinite(value) for vertex in mesh.vertices for value in vertex.co):
        bpy.data.meshes.remove(mesh)
        raise RuntimeError("Non-finite vertex in " + name)
    if any(poly.area <= 1e-10 for poly in mesh.polygons):
        bpy.data.meshes.remove(mesh)
        raise RuntimeError("Degenerate polygon in " + name)
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = owner
    obj.matrix_parent_inverse = Matrix.Identity(4)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    shell = obj.modifiers.new("Finite formed breast wall", "SOLIDIFY")
    shell.thickness = wall
    shell.offset = -1.0
    shell.use_even_offset = True
    bevel = obj.modifiers.new("Rounded plate edge", "BEVEL")
    bevel.width = .00005
    bevel.segments = 2
    obj["region"] = "breast"
    obj["surfaceRole"] = role
    obj["exteriorEras"] = ERAS
    obj["constructionClass"] = "inherited-passive"
    obj["proposal"] = True
    obj["layer"] = layer
    obj["geometryStatus"] = "V21 breast-course proposal; visual and clearance review pending"
    obj["sourceEnvelope"] = "V21 attempt-envelope03 shared profile"
    return obj


def _backing(owner, material):
    rows, columns = 52, 40
    vertices, faces = [], []
    for row in range(rows + 1):
        t = row / rows
        for col in range(columns + 1):
            angle = -ANGLE_LIMIT + 2 * ANGLE_LIMIT * col / columns
            top, bottom = _shared_edges(angle)
            z = top + (bottom - top) * t
            vertices.append(_surface_point(z, angle, .0002))
    for row in range(rows):
        for col in range(columns):
            i = row * (columns + 1) + col
            faces.append((i, i + columns + 1, i + columns + 2, i + 1))
    return _make_surface("V21 recessed breast course backing", owner, material,
                         vertices, faces, "inner-backing", .001, "recessed opening backing")


def _course_boundaries(count, course):
    """Staggered bins with broader forward plates and narrower flank plates."""
    widths = []
    for index in range(count):
        nominal_center = -ANGLE_LIMIT + (index + .5) * (2 * ANGLE_LIMIT / count)
        widths.append(1.0 - .28 * abs(nominal_center) / ANGLE_LIMIT)
    scale = 2 * ANGLE_LIMIT / sum(widths)
    boundaries = [-ANGLE_LIMIT]
    for width in widths[:-1]:
        boundaries.append(boundaries[-1] + width * scale)
    boundaries.append(ANGLE_LIMIT)
    if course % 2:
        for index in range(1, len(boundaries) - 1):
            boundaries[index] += .025 * math.sin(math.pi * index / count)
    return boundaries


def _plate(owner, material, course, column, count, left_edge, right_edge):
    gap = .018 + .012 * max(abs(left_edge), abs(right_edge)) / ANGLE_LIMIT
    angle_start = left_edge + gap * .5
    angle_end = right_edge - gap * .5
    if angle_end <= angle_start:
        raise AssertionError("Panel angular bin collapsed")
    flank = abs(.5 * (angle_start + angle_end)) / ANGLE_LIMIT
    offset = .0012 + .0018 * course
    crown = .0002
    if offset + crown > MAX_RELIEF:
        raise AssertionError("Plate relief exceeds the 12mm proposal envelope")

    # Neighboring panels in one course occupy disjoint angular bins, leaving a
    # narrow backed reveal. Vertical courses lap 20mm while stepping radially
    # by 1.8mm; each formed wall is 1mm thick, so the lap is not a collision.
    rows, cols = 20, 14
    vertices, faces = [], []
    for row in range(rows + 1):
        v = row / rows
        for col in range(cols + 1):
            u = 2 * col / cols - 1
            angle = angle_start + (angle_end - angle_start) * col / cols
            top_edge, bottom_edge = _shared_edges(angle)
            pitch = (top_edge - bottom_edge) / len(COURSE_COUNTS)
            band_top = top_edge - course * pitch
            band_bottom = top_edge - (course + 1) * pitch
            if course < len(COURSE_COUNTS) - 1:
                band_bottom -= .020
            # Edge waves stay inside each panel's assigned vertical band.
            edge_wave = .006 * (1 - u*u) * (.65 + .35 * flank)
            upper = band_top - edge_wave
            lower = band_bottom + edge_wave
            z = upper + (lower - upper) * v
            radial = offset + crown * (1 - u*u) * math.sin(math.pi * v)
            vertices.append(_surface_point(z, angle, radial))
    for row in range(rows):
        for col in range(cols):
            i = row * (cols + 1) + col
            faces.append((i, i + cols + 1, i + cols + 2, i + 1))
    name = f"V21 breast course {course + 1:02d} panel {column + 1:02d}"
    obj = _make_surface(name, owner, material, vertices, faces, "plate", .001,
                        f"course-{course + 1}")
    obj["courseIndex"] = course + 1
    obj["coursePanelIndex"] = column + 1
    obj["radialReliefMaxM"] = offset + crown
    obj["radialStepM"] = .0018
    return obj


def _evaluated_bvh(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        points = [evaluated.matrix_world @ vert.co for vert in mesh.vertices]
        triangles = [tuple(tri.vertices) for tri in mesh.loop_triangles]
        return BVHTree.FromPolygons(points, triangles, all_triangles=True, epsilon=0.0), len(points), len(triangles)
    finally:
        evaluated.to_mesh_clear()


def _panel_intersections(panels):
    trees = []
    for panel in panels:
        tree, vertex_count, triangle_count = _evaluated_bvh(panel)
        if vertex_count == 0 or triangle_count == 0:
            raise RuntimeError("Evaluated panel is empty: " + panel.name)
        trees.append(tree)
    intersections = []
    for left in range(len(panels)):
        for right in range(left + 1, len(panels)):
            if trees[left].overlap(trees[right]):
                intersections.append((panels[left].name, panels[right].name))
    return intersections


def apply():
    """Replace three broad guards with a finite 30-panel breast hierarchy."""
    blend_path = bpy.data.filepath
    if not blend_path or _hash(blend_path) != EXPECTED_NATIVE_SHA256:
        raise RuntimeError("This proposal is pinned to exact V21 envelope03 native SHA256")
    for rel in (OWNER_REFERENCE, MAKER_REFERENCE):
        if not Path(rel).is_file():
            raise FileNotFoundError(rel)
    owner, material = _material_and_owner()
    pivots = _pivot_signature()
    staged_out = []
    for name in STAGED_OUT:
        obj = bpy.data.objects[name]
        staged_out.append({"name": obj.name, "owner": obj.parent.name,
                           "region": obj.get("region"), "surfaceRole": obj.get("surfaceRole")})
        bpy.data.objects.remove(obj, do_unlink=True)

    backing = _backing(owner, material)
    added = [backing]
    plate_specs = []
    for course, count in enumerate(COURSE_COUNTS):
        boundaries = _course_boundaries(count, course)
        for column in range(count):
            left_edge, right_edge = boundaries[column:column + 2]
            center = (left_edge + right_edge) * .5
            obj = _plate(owner, material, course, column, count, left_edge, right_edge)
            added.append(obj)
            plate_specs.append({"name": obj.name, "course": course + 1,
                                "panel": column + 1, "centerAngleRad": center,
                                "maxRadialReliefM": float(obj["radialReliefMaxM"])})

    bpy.context.view_layer.update()
    if not _same_pivots(pivots):
        raise AssertionError("Breast course proposal changed a named pivot")
    expected_count = 1 + sum(COURSE_COUNTS)
    if len(added) != expected_count or sum(COURSE_COUNTS) != 30:
        raise AssertionError("Unexpected breast surface count")
    for obj in added:
        if obj.parent != owner or obj.get("exteriorEras") != ERAS or not obj.get("proposal"):
            raise AssertionError("New surface has invalid owner or eligibility: " + obj.name)
    panels = [obj for obj in added if obj.get("surfaceRole") == "plate"]
    intersections = _panel_intersections(panels)
    if intersections:
        raise AssertionError("Evaluated panel/panel intersections: " + repr(intersections[:12]))
    return {
        "status": "V21 breast-course proposal; visual/clearance review pending",
        "sourceNativeSha256": EXPECTED_NATIVE_SHA256,
        "stagedOut": staged_out,
        "created": [obj.name for obj in added],
        "createdCount": len(added),
        "plateCount": len(plate_specs),
        "courseCounts": list(COURSE_COUNTS),
        "plateSpecs": plate_specs,
        "owner": owner.name,
        "rigidAttachment": "All backing and plates are breastplate-owned and move with its existing inspection hinge; no object bridges owners.",
        "eligibility": ERAS,
        "materialsChanged": False,
        "pivotsPreserved": True,
        "maxRadialReliefM": max(spec["maxRadialReliefM"] for spec in plate_specs),
        "courseLappingProposalM": {"vertical": .020, "radialStep": .0018,
                                    "plateWall": .001, "crownMax": .0002},
        "evaluatedPanelPairIntersections": intersections,
        "limits": [
            "The shell and hinge envelope are unchanged. Plates follow the canonical envelope03 PCHIP profile and exact shared backing edges.",
            "The evaluated BVH check covers plate-to-plate surface crossings only; it does not test backing contact, existing body/neck fit, containment, or movement.",
            "All dimensions and course arrangement are reconstruction proposals, not measured reference dimensions or owner acceptance.",
        ],
    }
