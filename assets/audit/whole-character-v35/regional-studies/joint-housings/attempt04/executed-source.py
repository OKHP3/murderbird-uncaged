"""V35 compact linked thigh/shin frames with seated receiving housings.

Compresses only the X width of existing meshes under thigh/shin owners. The
profile preserves the current hip and ankle interfaces and brings both sides
to the same narrower width at the knee. Native Z-up, -Y front, +X anatomical
left. This remains a visual reconstruction proposal, not engineering.
"""
import bpy
import math
import json
from pathlib import Path
import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri

OWNERS = ("left-thigh", "right-thigh", "left-shin", "right-shin")
MID_WIDTH = 0.72
RELIEF_MARGIN = 0.003
RELIEF_PAIRS = (
    ("V25 left shin load channel collar -1 0.72", "V25 left thigh load channel collar -1 0.72"),
    ("V25 left shin load channel collar -1 0.72", "V25 left thigh primary load member -1"),
    ("V25 left shin load channel collar 1 0.72", "V25 left thigh load channel collar 1 0.72"),
    ("V25 left shin primary load member 1", "V25 left thigh load channel collar 1 0.72"),
    ("V25 left shin primary load member 1", "V25 left thigh primary load member 1"),
    ("V25 left shin rear return member 1", "V25 left thigh load channel collar 1 0.72"),
    ("V25 left shin rear return member 1", "V25 left thigh primary load member 1"),
)


def _smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _width(owner, t):
    if owner.endswith("-thigh"):
        # Retain the full existing hip seat, taper through the thigh, and hold
        # the compact section through the shared knee.
        if t <= 0.15:
            return 1.0
        return 1.0 - (1.0 - MID_WIDTH) * _smoothstep((t - 0.15) / 0.35)
    # Begin at the same compact knee section, then restore the original width
    # before the unchanged ankle/foot receiving structure.
    if t <= 0.35:
        return MID_WIDTH
    return MID_WIDTH + (1.0 - MID_WIDTH) * _smoothstep((t - 0.35) / 0.40)


def _segment(owner_name):
    side, kind = owner_name.split("-")
    next_name = side + ("-shin" if kind == "thigh" else "-foot")
    return bpy.data.objects[owner_name].matrix_world.translation.copy(), \
        bpy.data.objects[next_name].matrix_world.translation.copy()


def _triangle_crosses(a, b):
    normal = (b[1] - b[0]).cross(b[2] - b[0])
    if normal.length < 1e-12:
        return False
    normal.normalize()
    for i in range(3):
        p, q = a[i], a[(i + 1) % 3]
        d0, d1 = normal.dot(p - b[0]), normal.dot(q - b[0])
        if not (d0 * d1 < 0 and abs(d0) > 1e-7 and abs(d1) > 1e-7):
            continue
        direction = q - p
        hit = intersect_ray_tri(*b, direction, p, True)
        if hit is None:
            continue
        t = (hit - p).dot(direction) / max(direction.length_squared, 1e-30)
        v0, v1, v2 = b[1] - b[0], b[2] - b[0], hit - b[0]
        d00, d01, d11 = v0.dot(v0), v0.dot(v1), v1.dot(v1)
        denom = d00 * d11 - d01 * d01
        if abs(denom) < 1e-18:
            continue
        u = (d11 * v2.dot(v0) - d01 * v2.dot(v1)) / denom
        v = (d00 * v2.dot(v1) - d01 * v2.dot(v0)) / denom
        if 1e-6 < t < 1 - 1e-6 and min(u, v, 1 - u - v) > 1e-6:
            return True
    return False


def _pose_matrix(row, axis_conversion):
    return axis_conversion.inverted() @ Matrix(
        [row["worldMatrix"][i::4] for i in range(4)]) @ axis_conversion


def _local_peak_reliefs():
    """Cut one shallow contact relief per affected shin surface, at Maker peak."""
    root = Path(__file__).resolve().parents[2]
    pose_path = root / "assets/audit/whole-character-v34/attempt-form01/leg-composition-screen/pose-matrices.json"
    poses = json.loads(pose_path.read_text())["poses"]
    pose = next(row for row in poses if row["id"] == "maker-leg-peak")
    conversion = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))
    transforms = {row["name"]: _pose_matrix(row, conversion) for row in pose["transforms"]}
    nodes = [o for o in bpy.data.objects if o.type == "EMPTY" and not o.get("authoringGuide")]
    original_world = {o.name: o.matrix_world.copy() for o in nodes}

    def depth(obj):
        value = 0
        while obj.parent:
            value += 1
            obj = obj.parent
        return value

    for obj in sorted(nodes, key=depth):
        obj.matrix_world = transforms[obj.name]
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    reports = []
    patches_by_target = {}
    for target_name, neighbor_name in RELIEF_PAIRS:
        target = bpy.data.objects[target_name]
        neighbor = bpy.data.objects[neighbor_name]
        te, ne = target.evaluated_get(depsgraph), neighbor.evaluated_get(depsgraph)
        tm, nm = te.to_mesh(), ne.to_mesh()
        tm.calc_loop_triangles(); nm.calc_loop_triangles()
        tv = [te.matrix_world @ v.co for v in tm.vertices]
        nv = [ne.matrix_world @ v.co for v in nm.vertices]
        tt = [tuple(f.vertices) for f in tm.loop_triangles]
        nt = [tuple(f.vertices) for f in nm.loop_triangles]
        te.to_mesh_clear(); ne.to_mesh_clear()
        tb = BVHTree.FromPolygons(tv, tt, all_triangles=True)
        nb = BVHTree.FromPolygons(nv, nt, all_triangles=True)
        patch, crossed = [], 0
        for ti, ni in tb.overlap(nb):
            a = [tv[index] for index in tt[ti]]
            b = [nv[index] for index in nt[ni]]
            if _triangle_crosses(a, b) or _triangle_crosses(b, a):
                patch.extend(b)
                crossed += 1
        assert crossed > 0, (target_name, neighbor_name, "expected Maker-peak crossing absent")
        patches_by_target.setdefault(target_name, []).extend(patch)
        reports.append({"target": target_name, "neighbor": neighbor_name,
                        "crossingTrianglePairs": crossed,
                        "patchBoundsWorldM": [[min(p[k] for p in patch) for k in range(3)],
                                              [max(p[k] for p in patch) for k in range(3)]]})

    results = []
    for target_name, points in sorted(patches_by_target.items()):
        target = bpy.data.objects[target_name]
        expanded = set()
        for point in points:
            p = target.matrix_world.inverted() @ point
            for direction in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0),
                              (0, 0, 1), (0, 0, -1)):
                expanded.add(tuple(round(float(c), 7) for c in p + Vector(direction) * RELIEF_MARGIN))
        bm = bmesh.new()
        for point in expanded:
            bm.verts.new(point)
        bmesh.ops.convex_hull(bm, input=list(bm.verts), use_existing_faces=False)
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context="VERTS")
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        cutter_mesh = bpy.data.meshes.new("V35 Maker-peak local receiving relief cutter")
        bm.to_mesh(cutter_mesh); bm.free()
        cutter = bpy.data.objects.new(cutter_mesh.name, cutter_mesh)
        bpy.context.scene.collection.objects.link(cutter)
        cutter.matrix_world = target.matrix_world.copy()

        before_bm = bmesh.new(); before_bm.from_mesh(target.data)
        before_volume = abs(float(before_bm.calc_volume(signed=True)))
        before_bm.free()
        temp = bpy.data.objects.new("V35 temporary local receiving relief target", target.data.copy())
        bpy.context.scene.collection.objects.link(temp)
        temp.matrix_world = target.matrix_world.copy()
        mod = temp.modifiers.new("Maker-peak thigh contact receiving relief", "BOOLEAN")
        mod.operation = "DIFFERENCE"; mod.solver = "EXACT"; mod.object = cutter
        bpy.context.view_layer.objects.active = temp
        temp.select_set(True); cutter.select_set(False)
        bpy.ops.object.modifier_apply(modifier=mod.name)
        target.data = temp.data
        # Exact booleans may append a null material slot for generated faces.
        # The relief is the same neutral/frame material already used by the
        # receiver, so remove only empty trailing slots and retain definitions.
        for index in reversed(range(len(target.data.materials))):
            if target.data.materials[index] is None:
                target.data.materials.pop(index=index)
        after_bm = bmesh.new(); after_bm.from_mesh(target.data)
        bmesh.ops.recalc_face_normals(after_bm, faces=list(after_bm.faces))
        assert all(edge.is_manifold for edge in after_bm.edges), target_name
        after_volume = abs(float(after_bm.calc_volume(signed=True)))
        seen, components = set(), 0
        for vert in after_bm.verts:
            if vert in seen:
                continue
            components += 1; seen.add(vert); todo = [vert]
            while todo:
                for edge in todo.pop().link_edges:
                    for neighbor in edge.verts:
                        if neighbor not in seen:
                            seen.add(neighbor); todo.append(neighbor)
        assert components == 1 and after_volume > 0, (target_name, components, after_volume)
        after_bm.to_mesh(target.data); after_bm.free()
        local_verts = [v.co for v in target.data.vertices]
        bounds = [[min(v[k] for v in local_verts) for k in range(3)],
                  [max(v[k] for v in local_verts) for k in range(3)]]
        results.append({"name": target_name, "owner": target.parent.name,
                        "reliefMarginM": RELIEF_MARGIN,
                        "volumeBeforeM3": before_volume, "volumeAfterM3": after_volume,
                        "retainedVolumeFraction": after_volume / before_volume,
                        "connectedComponents": components,
                        "minimumObjectLocalSpanM": min(bounds[1][k] - bounds[0][k] for k in range(3)),
                        "objectLocalBoundsM": bounds})
        bpy.data.objects.remove(temp, do_unlink=True)
        bpy.data.objects.remove(cutter, do_unlink=True)
        bpy.data.meshes.remove(cutter_mesh)

    for obj in sorted(nodes, key=depth):
        obj.matrix_world = original_world[obj.name]
    bpy.context.view_layer.update()
    return {"pose": "maker-leg-peak", "poseSource": str(pose_path.relative_to(root)),
            "exactContactPairs": reports, "targetReliefs": results}


def apply():
    bpy.context.view_layer.update()
    changed = []
    for obj in sorted(bpy.data.objects, key=lambda item: item.name):
        if obj.type != "MESH" or not obj.parent or obj.parent.name not in OWNERS:
            continue
        owner = obj.parent.name
        p0, p1 = _segment(owner)
        dy, dz = p1.y - p0.y, p1.z - p0.z
        length2 = dy * dy + dz * dz
        assert length2 > 1e-10, owner
        matrix = obj.matrix_world.copy()
        inverse = matrix.inverted()
        original = [matrix @ vertex.co for vertex in obj.data.vertices]
        # Joint races and captive axles are kept geometrically round/straight:
        # use one section factor for the complete mesh. Long frame members get
        # the continuous taper along their actual hip-knee-ankle centerline.
        joint_part = any(tag in obj.name.lower() for tag in (
            "journal", "retainer rim", "captive axle", "captive cheek",
            "journal keeper bolt"))
        moved = 0
        factors = []
        for vertex, point in zip(obj.data.vertices, original):
            t = max(0.0, min(1.0, ((point.y - p0.y) * dy +
                                  (point.z - p0.z) * dz) / length2))
            section_t = (sum(max(0.0, min(1.0,
                ((q.y - p0.y) * dy + (q.z - p0.z) * dz) / length2))
                for q in original) / len(original)) if joint_part else t
            factor = _width(owner, section_t)
            center_x = p0.x + t * (p1.x - p0.x)
            point.x = center_x + (point.x - center_x) * factor
            vertex.co = inverse @ point
            factors.append(factor)
            moved += factor < 0.999999
        if moved:
            obj.data.update()
            changed.append({
                "name": obj.name,
                "owner": owner,
                "widthFactorMin": round(min(factors), 6),
                "widthFactorMax": round(max(factors), 6),
                "materialNames": [mat.name if mat else None for mat in obj.data.materials],
            })
    relief = _local_peak_reliefs()
    changed_names = {row["name"] for row in changed}
    for row in relief["targetReliefs"]:
        if row["name"] not in changed_names:
            changed.append({"name": row["name"], "owner": row["owner"],
                            "localMakerPeakReceivingRelief": True,
                            "materialNames": [mat.name if mat else None for mat in bpy.data.objects[row["name"]].data.materials]})
    return {
        "region": "paired compact thigh/shin frames and receiving housings",
        "changedMeshes": changed,
        "added": [],
        "removed": [],
        "changedNodes": [],
        "localMakerPeakReliefs": relief,
        "status": "single bounded visual and receiving-relief proposal; discrete articulation screen pending",
        "limits": [
            "Existing hip interface is unchanged at the thigh proximal centerline.",
            "Both sides meet at a shared 0.72 transverse width at the knee.",
            "Shin frame restores original width at the unchanged ankle/foot interface.",
            "No body, foot, toe, runtime, era, or powered mesh is edited.",
            "Construction geometry does not certify strength, balance, or continuous clearance.",
        ],
    }
