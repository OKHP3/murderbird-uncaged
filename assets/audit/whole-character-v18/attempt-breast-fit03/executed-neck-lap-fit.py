"""Tuck the cervical free-edge laminae behind the V17 breast course.

This bounded neck-owned patch keeps all guard object identities, owners,
materials, pivots, and upper visible contours. It fits only the existing lower
flank/throat plate surfaces behind the actual solidified first breast course,
creating a rigid lapped seam that can move with the inherited neck pivots.
It does not add a driver, flexible joint, rail, or new mesh.
"""
from pathlib import Path
import hashlib

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


EXPECTED_NATIVE_SHA256 = "7d371907b279eb3d625e67164d84a78b2901a5cb6a79917def07f48ff8792d7b"
FLANK = tuple(f"Cervical flank lamina {side} {course}"
              for course in (5, 6) for side in (-1, 1))
THROAT = ("Throat formed lamina 4", "Throat formed lamina 5")
BREAST = tuple(f"V17 breast directional lamina 1 {column} {side}"
               for column in range(1, 5) for side in ("left", "right"))
TUCK_START = 0.08
TUCK_FULL = 0.42
CLEARANCE = 0.004


def _sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _pivots():
    return {o.name: (o.parent.name if o.parent else None, o.matrix_world.copy())
            for o in bpy.data.objects if o.type == "EMPTY"}


def _matrices_equal(a, b, eps=1e-8):
    return all(abs(a[r][c] - b[r][c]) <= eps for r in range(4) for c in range(4))


def _combined_breast_tree(objects):
    deps = bpy.context.evaluated_depsgraph_get()
    points, faces = [], []
    for obj in objects:
        evaluated = obj.evaluated_get(deps)
        mesh = evaluated.to_mesh()
        mesh.calc_loop_triangles()
        base = len(points)
        points.extend(evaluated.matrix_world @ v.co for v in mesh.vertices)
        faces.extend(tuple(base + i for i in tri.vertices) for tri in mesh.loop_triangles)
        evaluated.to_mesh_clear()
    assert points and faces
    return BVHTree.FromPolygons(points, faces, all_triangles=True, epsilon=0.0)


def _rear_surface(tree, x, z):
    # The breast plates face -Y; from the rear, the first hit is their back.
    loc, normal, _face, _distance = tree.ray_cast(Vector((x, 1.5, z)),
                                                  Vector((0.0, -1.0, 0.0)), 3.0)
    return loc, normal


def _smooth01(x):
    t = max(0.0, min(1.0, x))
    return t * t * (3.0 - 2.0 * t)


def _tuck(obj, breast_tree):
    assert obj.type == "MESH" and obj.parent and obj.parent.name in {"neck", "cervical-upper"}
    assert len(obj.data.vertices) == 169, f"Unexpected cervical grid for {obj.name}"
    assert len(obj.modifiers) >= 2 and any(m.type == "SOLIDIFY" for m in obj.modifiers), (
        f"Expected a finite-thickness formed plate: {obj.name}")
    inverse = obj.matrix_world.inverted()
    before = [obj.matrix_world @ v.co for v in obj.data.vertices]
    across = 13
    rows = []
    shifted = 0
    max_shift = 0.0
    moved = []
    for index, (vertex, point) in enumerate(zip(obj.data.vertices, before)):
        row = index // across
        t = row / 12.0
        weight = _smooth01((t - TUCK_START) / (TUCK_FULL - TUCK_START))
        if weight <= 0:
            moved.append(0.0)
            continue
        loc, normal = _rear_surface(breast_tree, point.x, point.z)
        if loc is None:
            moved.append(0.0)
            continue
        desired_y = loc.y + CLEARANCE
        delta = max(0.0, desired_y - point.y)
        shift = delta * weight
        if shift > 1e-7:
            vertex.co = inverse @ Vector((point.x, point.y + shift, point.z))
            shifted += 1
            max_shift = max(max_shift, shift)
        moved.append(shift)
        rows.append({"row": row, "t": t, "vertices": 1, "projected": True})
    obj.data.update()
    points_after = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return {"name": obj.name, "owner": obj.parent.name, "grid": [13, 13],
            "verticesShiftedPosterior": shifted, "maximumPosteriorShiftM": max_shift,
            "maximumInteriorOffsetM": CLEARANCE,
            "transition": {"startFractionTopToBottom": TUCK_START,
                           "fullyTuckedFractionTopToBottom": TUCK_FULL},
            "upperEdgeWorldBoundsBefore": [min(p.z for p in before[:13]), max(p.z for p in before[:13])],
            "upperEdgeMaxDisplacementM": max(moved[:13], default=0.0),
            "lowerEdgeMaxDisplacementM": max(moved[-13:], default=0.0),
            "worldBoundsAfter": [[min(p[i] for p in points_after) for i in range(3)],
                                 [max(p[i] for p in points_after) for i in range(3)]],
            "attachment": "existing rigid neck-owned plate; no new pivot or flexible metal"}


def apply():
    native = Path(bpy.data.filepath)
    assert native.is_file() and _sha(native) == EXPECTED_NATIVE_SHA256, (
        "V18 neck lap fit requires exact V17 attempt02 native")
    breast_objects = [bpy.data.objects.get(name) for name in BREAST]
    guards = [bpy.data.objects.get(name) for name in FLANK + THROAT]
    assert all(o and o.parent and o.parent.name == "breastplate" for o in breast_objects)
    assert all(o for o in guards), "An implicated neck plate is missing"
    assert all(o.parent and o.parent.name in {"neck", "cervical-upper"} for o in guards)
    pivots_before = _pivots()
    materials_before = sorted((m.name, len(m.node_tree.nodes) if m.node_tree else 0)
                              for m in bpy.data.materials)
    tree = _combined_breast_tree(breast_objects)
    results = [_tuck(obj, tree) for obj in guards]
    bpy.context.view_layer.update()
    pivots_after = _pivots()
    assert set(pivots_before) == set(pivots_after) and all(
        pivots_before[n][0] == pivots_after[n][0]
        and _matrices_equal(pivots_before[n][1], pivots_after[n][1]) for n in pivots_before), (
        "Neck lap fit changed articulation pivots")
    materials_after = sorted((m.name, len(m.node_tree.nodes) if m.node_tree else 0)
                             for m in bpy.data.materials)
    assert materials_before == materials_after, "Neck lap fit changed material definitions"
    return {
        "status": "V18 neck-owned lower-lap fit proposal; sampled pose clearance pending",
        "sourceNative": {"path": native.as_posix(), "sha256": EXPECTED_NATIVE_SHA256},
        "changedObjects": [o.name for o in guards],
        "fit": results,
        "breastTargets": list(BREAST),
        "ownership": "Only existing neck/cervical-upper passive guard mesh coordinates change; guards retain their original rigid owners and all-era tags.",
        "interface": "Lower guard surfaces tuck behind the evaluated solid breast-course back faces by a smooth rigid plate contour; the breast envelope and access pivot remain unchanged.",
        "preserved": ["all 52 pivots, parent graph and matrices", "all breast shell, plate and fixing meshes",
                      "all frame/backing rails", "all materials and mesh/object identities"],
        "limits": ["The underlap is a reconstructed sliding interface, not a measured reference dimension.",
                   "Discrete strict-pose checks and visual review are required before any integration decision.",
                   "No continuous articulation sweep or mechanical load validation is claimed."]
    }
