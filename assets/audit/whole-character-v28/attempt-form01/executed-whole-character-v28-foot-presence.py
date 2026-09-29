"""Editable V28 local foot-presence study for the V27 Form01 native.

This is a geometry-only study module. It changes no object transforms, pivots,
hierarchy, contact markers, materials, era tags, or non-foot geometry.
"""

EXPECTED_SOURCE = "assets/models/whole-character-v27/attempt-form01/murderbird-whole-character-v27.blend"


def _bounds_world(obj):
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]


def _reprofile_guard(obj):
    """Widen the existing toe saddle and deepen its wrapped section in-place."""
    mesh = obj.data
    ys = sorted(v.co.y for v in mesh.vertices)
    stations = []
    for y in ys:
        if not stations or abs(y - stations[-1]) > 0.0007:
            stations.append(y)
    centers = []
    for y in stations:
        ring = [v.co for v in mesh.vertices if abs(v.co.y - y) <= 0.0007]
        centers.append((sum(p.x for p in ring) / len(ring), sum(p.z for p in ring) / len(ring)))
    for v in mesh.vertices:
        k = min(range(len(stations)), key=lambda i: abs(stations[i] - v.co.y))
        cx, cz = centers[k]
        v.co.x = cx + (v.co.x - cx) * 1.18
        v.co.z = cz + 0.002 + (v.co.z - cz) * 1.58
    mesh.update()


def _reprofile_claw(obj):
    ys = [v.co.y for v in obj.data.vertices]
    max_y = max(ys)
    min_y = min(ys)
    factor = 0.80
    for v in obj.data.vertices:
        # Retain the source's curved, stout cross-section and exact X/Z profile;
        # shorten its forward reach from the broad root without changing the
        # foot's floor-contact height.
        v.co.y = max_y - (max_y - v.co.y) * factor
    obj.data.update()
    new_min_y = min(v.co.y for v in obj.data.vertices)
    return {
        "originalForeAftLength": round(max_y - min_y, 6),
        "newForeAftLength": round(max_y - new_min_y, 6),
        "foreAftScale": factor,
        "localXAndZProfilePreserved": True,
    }


def apply():
    import bpy

    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    before_pivots = {
        o.name: [round(float(o.matrix_world[r][c]), 8) for r in range(4) for c in range(4)]
        for o in bpy.data.objects if o.type == "EMPTY"
    }
    claw_names = [
        f"{side} digit {digit} tapered claw sheath"
        for side in ("left", "right") for digit in (1, 2, 3)
    ]
    guard_names = [
        f"{side} digit {digit} {segment} dorsal guard"
        for side in ("left", "right") for digit in (1, 2, 3)
        for segment in ("proximal", "distal")
    ]
    targets = claw_names + guard_names
    missing = [name for name in targets if bpy.data.objects.get(name) is None]
    if missing:
        raise RuntimeError("V27 foot study missing expected named meshes: " + ", ".join(missing))

    result = {"source": EXPECTED_SOURCE, "changedObjects": [], "claws": {}, "guards": []}
    for name in guard_names:
        obj = bpy.data.objects[name]
        if obj.type != "MESH" or obj.parent is None:
            raise RuntimeError(f"Unexpected dorsal guard object/owner: {name}")
        if obj.get("region") != "foot" or obj.get("surfaceRole") != "plate":
            raise RuntimeError(f"Unexpected dorsal guard tags: {name}")
        before = _bounds_world(obj)
        _reprofile_guard(obj)
        obj["footPresenceRevision"] = "V28 coarse articulated toe-cover study"
        result["guards"].append({"name": name, "owner": obj.parent.name, "beforeWorldBounds": before, "afterWorldBounds": _bounds_world(obj)})
        result["changedObjects"].append(name)

    for name in claw_names:
        obj = bpy.data.objects[name]
        if obj.type != "MESH" or obj.parent is None:
            raise RuntimeError(f"Unexpected claw object/owner: {name}")
        if obj.get("region") != "foot" or obj.get("surfaceRole") != "edge":
            raise RuntimeError(f"Unexpected claw tags: {name}")
        before = _bounds_world(obj)
        metric = _reprofile_claw(obj)
        obj["footPresenceRevision"] = "V28 native-profile shortened talon study"
        obj.data.update()
        result["claws"][name] = {"owner": obj.parent.name, **metric, "beforeWorldBounds": before, "afterWorldBounds": _bounds_world(obj)}
        result["changedObjects"].append(name)

    bpy.context.view_layer.update()
    after_pivots = {
        o.name: [round(float(o.matrix_world[r][c]), 8) for r in range(4) for c in range(4)]
        for o in bpy.data.objects if o.type == "EMPTY"
    }
    if before_pivots != after_pivots:
        raise RuntimeError("Foot study changed at least one pivot transform")
    result["protectedPivots"] = {"count": len(before_pivots), "allWorldMatricesUnchanged": True}
    result["classification"] = "existing passive foot-owner meshes; maker, mechanic, builder"
    result["scopeLimits"] = ["rest authoring study only", "no movement or collision clearance proof"]
    return result
