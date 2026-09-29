"""V36 bilateral fixed scapular receiver sweep; body-owned geometry only.

The six V35 scapular plates receive a restrained rear/upward crown sweep so
their upper return tucks beneath the existing moving mantle. The shoulder
journals, saddles, races, mantle, side guards, pivots, and all other geometry
remain unchanged. This is a shape proposal, not a clearance certification.
"""
from mathutils import Vector
import bpy
import bmesh
import math


PLATES = [f"V35 scapular receiving plate {side} {index}"
          for side in (-1, 1) for index in range(3)]
EXPECTED_OWNER = "body"


def _ease(a, b, value):
    t = max(0.0, min(1.0, (value - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def _bounds(obj):
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return [[min(p[k] for p in pts), max(p[k] for p in pts)] for k in range(3)]


def apply():
    bpy.context.view_layer.update()
    assert all(name in bpy.data.objects for name in PLATES)
    before = {name: bpy.data.objects[name] for name in PLATES}
    assert all(o.type == "MESH" and o.parent and o.parent.name == EXPECTED_OWNER
               and o.data.users == 1 for o in before.values())
    bounds_before = {name: _bounds(obj) for name, obj in before.items()}
    material_ids = {name: tuple(m.name if m else None for m in obj.data.materials)
                    for name, obj in before.items()}
    world_matrices = {name: obj.matrix_world.copy() for name, obj in before.items()}
    pivot_centers = {
        -1: bpy.data.objects["right-mantle"].matrix_world.translation.copy(),
        1: bpy.data.objects["left-mantle"].matrix_world.translation.copy(),
    }
    max_displacement = {}

    for name, obj in before.items():
        side = -1 if name.startswith("V35 scapular receiving plate -1 ") else 1
        inv = obj.matrix_world.inverted()
        pivot = pivot_centers[side]
        original = [obj.matrix_world @ v.co for v in obj.data.vertices]
        moved = []
        for p in original:
            # Concentrate the reshaping on the raised outer/rear edge. The
            # sternum-facing edge and a 55 mm neighborhood around the actual
            # mantle pivot remain unchanged, retaining the existing seats.
            upper = _ease(1.105, 1.265, p.z)
            lateral = _ease(0.185, 0.292, abs(p.x))
            aft = 0.24 + 0.76 * _ease(-0.205, -0.015, p.y)
            root_clear = _ease(0.045, 0.085, (p - pivot).length)
            weight = upper * lateral * aft * root_clear
            q = p.copy()
            q.y += 0.020 * weight
            q.z += 0.032 * weight
            q.x += side * 0.006 * weight
            moved.append(q)
        max_displacement[name] = max((a - b).length for a, b in zip(original, moved))
        for vert, point in zip(obj.data.vertices, moved):
            vert.co = inv @ point
        obj.data.update()
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
        assert obj.parent.name == EXPECTED_OWNER
        assert tuple(m.name if m else None for m in obj.data.materials) == material_ids[name]
        assert obj.matrix_world == world_matrices[name]
        assert all(math.isfinite(c) for v in obj.data.vertices for c in v.co)
        assert max_displacement[name] <= 0.041

    bpy.context.view_layer.update()
    return {
        "region": "bilateral scapular receiving plates",
        "status": "V36 bounded unapproved shape proposal",
        "changedMeshes": PLATES,
        "addedMeshes": [],
        "removedMeshes": [],
        "changedNodes": [],
        "changedMeshOwners": {name: EXPECTED_OWNER for name in PLATES},
        "changedMeshMaterialNames": material_ids,
        "unchangedShoulderHardware": [
            "left-mantle", "right-mantle", "left oblique shoulder saddle v4",
            "right oblique shoulder saddle v4", "left shouldered shoulder journal",
            "right shouldered shoulder journal", "left swept upper wing load member",
            "right swept upper wing load member",
        ],
        "otherSurfacesUnchanged": True,
        "maximumWorldVertexDisplacementM": max_displacement,
        "boundsBeforeWorld": bounds_before,
        "boundsAfterWorld": {name: _bounds(bpy.data.objects[name]) for name in PLATES},
        "construction": "Localized 20 mm aft and 32 mm upward crown sweep, with 6 mm outward taper at the raised mantle-facing plate edge; sternum-facing edge and near-pivot zone fixed.",
        "limits": [
            "No moving mantle geometry or receiver axes were changed.",
            "Preserved authored Boolean seats were not recomputed after deformation.",
            "Discrete visual/native study only; fresh shoulder-motion intersection check is required before treating the receiver as fitted.",
        ],
    }
