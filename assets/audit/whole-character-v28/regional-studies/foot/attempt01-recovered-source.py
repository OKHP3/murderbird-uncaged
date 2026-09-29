"""Editable V28 local foot-presence study for the V27 Form01 native.

This is a geometry-only study module. It changes no object transforms, pivots,
hierarchy, contact markers, materials, era tags, or non-foot geometry.
"""

from mathutils import Vector
import bmesh


EXPECTED_SOURCE = "assets/models/whole-character-v27/attempt-form01/murderbird-whole-character-v27.blend"


def _bounds_world(obj):
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]


def _rings_for_claw(root, old_tip, min_z):
    # A compact, blunt-rooted hard talon, curved gently down toward the source
    # contact height. The last point preserves the original lowest Z exactly.
    delta = old_tip - root
    tip = root + delta * 0.68
    tip.z = min_z
    p0 = root
    p1 = root + delta * 0.30 + Vector((0.0, 0.0, 0.004))
    p2 = tip - delta * 0.22 + Vector((0.0, 0.0, 0.002))
    p3 = tip

    def bezier(t):
        s = 1.0 - t
        return p0 * (s ** 3) + p1 * (3 * s * s * t) + p2 * (3 * s * t * t) + p3 * (t ** 3)

    def tangent(t):
        s = 1.0 - t
        v = (p1 - p0) * (3 * s * s) + (p2 - p1) * (6 * s * t) + (p3 - p2) * (3 * t * t)
        return v.normalized()

    stations = (0.0, 0.07, 0.16, 0.28, 0.42, 0.56, 0.68, 0.78, 0.87, 0.94)
    radii = ((0.020, 0.017), (0.023, 0.019), (0.023, 0.019),
             (0.021, 0.017), (0.018, 0.014), (0.014, 0.011),
             (0.010, 0.008), (0.007, 0.0055), (0.004, 0.003), (0.0017, 0.0013))
    sides = 16
    verts = []
    faces = []
    for t, (rx, rv) in zip(stations, radii):
        c = bezier(t)
        axis = tangent(t)
        u = Vector((1.0, 0.0, 0.0))
        if abs(axis.dot(u)) > 0.95:
            u = Vector((0.0, 1.0, 0.0))
        u = (u - axis * axis.dot(u)).normalized()
        v = axis.cross(u).normalized()
        for j in range(sides):
            a = 2.0 * 3.141592653589793 * j / sides
            point = c + u * (rx * __import__('math').cos(a)) + v * (rv * __import__('math').sin(a))
            # Keep the sculpted tip at the old floor-contact height.
            point.z = max(point.z, min_z + 0.00025)
            verts.append(tuple(point))
    for r in range(len(stations) - 1):
        a0 = r * sides
        a1 = (r + 1) * sides
        for j in range(sides):
            jn = (j + 1) % sides
            faces.append((a0 + j, a0 + jn, a1 + jn, a1 + j))
    # Rounded root cap and single hard tip preserve a closed, simple mesh.
    verts.append(tuple(p0))
    root_index = len(verts) - 1
    for j in range(sides):
        faces.append((root_index, (j + 1) % sides, j))
    verts.append(tuple(p3))
    tip_index = len(verts) - 1
    last = (len(stations) - 1) * sides
    for j in range(sides):
        faces.append((last + j, last + (j + 1) % sides, tip_index))
    return verts, faces, tip


def _replace_geometry(obj, verts, faces):
    old = obj.data
    mesh = old.copy()
    mesh.name = old.name + " V28 foot-presence geometry"
    mesh.clear_geometry()
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj.data = mesh
    if old.users == 0:
        bpy_data = __import__('bpy').data
        bpy_data.meshes.remove(old)


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
    points = [v.co.copy() for v in obj.data.vertices]
    min_y = min(p.y for p in points)
    max_y = max(p.y for p in points)
    min_z = min(p.z for p in points)
    root_band = [p for p in points if p.y >= max_y - 0.008]
    tip_band = [p for p in points if p.y <= min_y + 0.008]
    root = sum(root_band, Vector()) / len(root_band)
    tip_candidates = [p for p in tip_band if p.z <= min_z + 0.004]
    old_tip = sum(tip_candidates or tip_band, Vector()) / len(tip_candidates or tip_band)
    verts, faces, new_tip = _rings_for_claw(root, old_tip, min_z)
    _replace_geometry(obj, verts, faces)
    return {
        "originalLength": round((old_tip - root).length, 6),
        "newCenterlineLength": round((new_tip - root).length, 6),
        "preservedLocalLowestZ": round(min_z, 6),
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
        obj["footPresenceRevision"] = "V28 short formed talon study"
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
