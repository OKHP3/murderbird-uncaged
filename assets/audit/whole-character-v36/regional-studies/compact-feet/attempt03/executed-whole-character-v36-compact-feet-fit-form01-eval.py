"""V36 passive foot-interface fit relief, composable after compact-feet.py.

Assumes V36 compact foot construction is already applied. Reverts the 22 mm
arch lift implicated by landing witnesses and relieves only six hinge-facing
dorsal guards. It does not move pivots, reshape bearings, or repeat compacting.
Native Z-up, -Y front, +X anatomical left.
"""
import bpy

ARCH_TOKENS = ("metatarsal passive rail", "metatarsus open passive truss", "curved instep guard")
GUARD_NAMES = (
    "left digit 1 proximal dorsal guard", "left digit 2 distal dorsal guard",
    "left digit 3 proximal dorsal guard", "right digit 1 proximal dorsal guard",
    "right digit 2 distal dorsal guard", "right digit 3 proximal dorsal guard",
)
ARCH_LIFT_M = 0.022
GUARD_SPAN = 0.56


def _world_vertices(obj):
    return [obj.matrix_world @ v.co for v in obj.data.vertices]


def _signature(obj):
    return (tuple(tuple(round(float(c), 10) for c in v.co) for v in obj.data.vertices),
            tuple(tuple(int(i) for i in p.vertices) for p in obj.data.polygons),
            tuple(m.name if m else None for m in obj.data.materials),
            tuple(round(float(obj.matrix_world[r][c]), 10) for r in range(4) for c in range(4)))


def apply():
    bpy.context.view_layer.update()
    changed = []
    arch_changes = []
    guard_changes = []
    for obj in sorted((o for o in bpy.data.objects if o.type == "MESH" and o.parent), key=lambda o: o.name):
        name = obj.name
        if not any(token in name.lower() for token in ARCH_TOKENS) and name not in GUARD_NAMES:
            continue
        before = _signature(obj)
        points = _world_vertices(obj)
        inverse = obj.matrix_world.inverted()
        if any(token in name.lower() for token in ARCH_TOKENS):
            moved = 0
            for vertex, point in zip(obj.data.vertices, points):
                t = (point.y + 0.168) / 0.234
                if 0.0 < t < 1.0:
                    point.z -= ARCH_LIFT_M * __import__("math").sin(__import__("math").pi * t)
                    vertex.co = inverse @ point
                    moved += 1
            obj.data.update()
            arch_changes.append({"name": name, "owner": obj.parent.name,
                                 "verticesReverted": moved, "maximumLiftRemovedM": ARCH_LIFT_M})
        else:
            pivot_y = obj.parent.matrix_world.translation.y
            for vertex, point in zip(obj.data.vertices, points):
                point.y = pivot_y + (point.y - pivot_y) * GUARD_SPAN
                vertex.co = inverse @ point
            obj.data.update()
            guard_changes.append({"name": name, "owner": obj.parent.name,
                                  "axialSpanFactor": GUARD_SPAN,
                                  "interpretation": "existing guard span shortened around unchanged owner pivot"})
        if _signature(obj) != before:
            changed.append({"name": name, "owner": obj.parent.name, "vertices": len(obj.data.vertices),
                            "polygons": len(obj.data.polygons), "surfaceRole": obj.get("surfaceRole", "")})
    assert len(arch_changes) == 8 and len(guard_changes) == 6 and len(changed) == 14
    return {
        "region": "passive foot arch and six hinge-facing dorsal guards",
        "changedNodes": [],
        "changedFootMeshes": changed,
        "added": [], "removed": [],
        "rationale": "The strict landing witnesses attribute five shin/instep pairs to the 22 mm raised passive arch. Rest/scrape/landing witnesses attribute hinge crossings to six specific dorsal guards. This correction restores original arch elevation and shortens only those six existing guard spans around their unchanged pivots; bearings, links, toes, and all other meshes remain as composed.",
        "archChanges": arch_changes,
        "guardChanges": guard_changes,
        "scopeLimitations": [
            "Region-only geometric fit proposal; not whole-model engineering, force, balance, or continuous-motion validation.",
            "Guard shaping uses axial span relief around the retained owner pivot; strict discrete screen and visual review are required.",
            "Owner likeness acceptance remains pending.",
        ],
    }
