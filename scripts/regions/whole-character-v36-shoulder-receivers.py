"""V36 bilateral fixed scapular receiver sweep; body-owned geometry only.

The six V35 scapular plates and paired upper thoracic guards receive a
localized rear/upward sweep to form a fixed shoulder-root receiver under the
existing moving mantle. The shoulder journals, saddles, races, mantle, pivots,
and all other geometry remain unchanged. This is a shape proposal, not a
clearance certification.
"""
from mathutils import Vector
import bpy
import bmesh
import math


RECEIVERS = ([f"V35 scapular receiving plate {side} {index}"
              for side in (-1, 1) for index in range(3)]
             + [f"V35 oblique thoracic side guard {side} 0" for side in (-1, 1)])
EXPECTED_OWNER = "body"


def _ease(a, b, value):
    t = max(0.0, min(1.0, (value - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def _bounds(obj):
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return [[min(p[k] for p in pts), max(p[k] for p in pts)] for k in range(3)]


def apply():
    bpy.context.view_layer.update()
    assert all(name in bpy.data.objects for name in RECEIVERS)
    before = {name: bpy.data.objects[name] for name in RECEIVERS}
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
        side = -1 if name.startswith("V35 scapular receiving plate -1 ") or name.endswith(" -1 0") else 1
        inv = obj.matrix_world.inverted()
        pivot = pivot_centers[side]
        is_scapular = name.startswith("V35 scapular receiving plate ")
        original = [obj.matrix_world @ v.co for v in obj.data.vertices]
        moved = []
        for p in original:
            # Concentrate the reshaping on the raised outer/rear edge. The
            # sternum-facing edge and a 55 mm neighborhood around the actual
            # mantle pivot remain unchanged, retaining the existing seats.
            if is_scapular:
                upper = _ease(1.105, 1.265, p.z)
                lateral = _ease(0.185, 0.292, abs(p.x))
                aft = 0.24 + 0.76 * _ease(-0.205, -0.015, p.y)
                travel = (0.030, 0.048, 0.008)
            else:
                upper = _ease(1.055, 1.150, p.z)
                lateral = _ease(0.205, 0.295, abs(p.x))
                aft = 0.38 + 0.62 * _ease(-0.205, -0.055, p.y)
                travel = (0.018, 0.028, 0.005)
            root_clear = _ease(0.045, 0.085, (p - pivot).length)
            weight = upper * lateral * aft * root_clear
            q = p.copy()
            q.y += travel[0] * weight
            q.z += travel[1] * weight
            q.x += side * travel[2] * weight
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
        assert max_displacement[name] <= 0.061

    bpy.context.view_layer.update()
    return {
        "region": "bilateral fixed shoulder-root receiver",
        "status": "V36 bounded unapproved shape proposal",
        "changedMeshes": RECEIVERS,
        "addedMeshes": [],
        "removedMeshes": [],
        "changedNodes": [],
        "changedMeshOwners": {name: EXPECTED_OWNER for name in RECEIVERS},
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
        "boundsAfterWorld": {name: _bounds(bpy.data.objects[name]) for name in RECEIVERS},
        "construction": "Six scapular plates sweep up to 48 mm, aft up to 30 mm, and outward up to 8 mm at the mantle-facing edge. The two upper side guards sweep up to 28 mm and aft up to 18 mm. Central/journal neighborhoods and inner breast margins stay fixed.",
        "limits": [
            "No moving mantle geometry or receiver axes were changed.",
            "Preserved authored Boolean seats were not recomputed after deformation.",
            "Discrete visual/native study only; fresh shoulder-motion intersection check is required before treating the receiver as fitted.",
        ],
    }
