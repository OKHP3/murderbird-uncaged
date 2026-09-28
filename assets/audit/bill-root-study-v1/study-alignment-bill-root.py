"""Build a four-mesh native-only head-root construction proposal from frozen v6."""
from pathlib import Path
import bpy
import bmesh
import hashlib
import json
import math
import shutil
import struct
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/models/uncaged-alignment-v6/murderbird-alignment-v6.blend"
HEAD_RECIPE = ROOT / "scripts/alignment-v6-head.py"
PRIOR_RECEIPT = ROOT / "assets/audit/bill-profile-study-v1/root-review.md"
JULY_REFERENCE = ROOT / "context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png"
INVENTORY = ROOT / "assets/models/uncaged-alignment-v6/alignment-inventory.json"
MODEL_DIR = ROOT / "assets/models/uncaged-bill-root-study-v1"
AUDIT_DIR = ROOT / "assets/audit/bill-root-study-v1"
CANDIDATE = MODEL_DIR / "murderbird-bill-root-study-v1.blend"
EXPECTED_SOURCE_SHA = "5a7a51941423dd0efcb48b9641b7a49597dad117e218ccb4e94f26315c5e9ded"
EXPECTED_HEAD_RECIPE_SHA = "a921130111ac27f14f1ddda10328f7dd21bf2cffa1d4e34aee8d1756fd738472"
EXPECTED_PRIOR_REVIEW_SHA = "8b092b7a41927b0a39438ea96f49423a3e9cabf83ad0be9c2f4b707f67d8b29c"
EXPECTED_INVENTORY_SHA = "2cdef42ccc9e96059d23252513321a5936b5b36717bc6a5c6409246ca6d2ca3b"
EXPECTED_TARGETS = {
    "Forged orbital brow -1", "Forged orbital brow 1",
    "Cere root transition -1", "Cere root transition 1",
}
CAMERAS = [
    {"name": "side-biased-three-quarter-a", "position": (-6.0, -3.0, 2.4), "target": (0.0, -0.29, 1.78), "orthoScale": 0.80},
    {"name": "side-biased-three-quarter-b", "position": (-6.0, -4.2, 2.1), "target": (0.0, -0.29, 1.78), "orthoScale": 0.80},
]
HEAD_SECTIONS = [
    (1.575, -.15, .065, .10), (1.65, -.20, .123, .185),
    (1.74, -.25, .149, .22), (1.825, -.265, .153, .20),
    (1.915, -.24, .119, .175), (1.955, -.17, .025, .075),
]
BROW_PATH = [
    (-.273, 1.847, .020, .010),
    (-.305, 1.899, .038, .014),
    (-.375, 1.926, .043, .017),
    (-.443, 1.901, .033, .014),
    (-.483, 1.858, .014, .008),
]
# The cheek-to-cere plate expands only within the existing bill-root envelope.
# Its deliberate faceted perimeter and inset face are actual closed geometry.
CERE_OUTLINE = [
    (-.423, 1.861), (-.443, 1.897), (-.486, 1.900), (-.527, 1.874),
    (-.546, 1.842), (-.530, 1.812), (-.493, 1.807), (-.462, 1.827),
]
FINAL_OUTPUTS = [
    CANDIDATE,
    AUDIT_DIR / "before-side-biased-three-quarter-a.png",
    AUDIT_DIR / "before-side-biased-three-quarter-b.png",
    AUDIT_DIR / "after-side-biased-three-quarter-a.png",
    AUDIT_DIR / "after-side-biased-three-quarter-b.png",
    AUDIT_DIR / "study-alignment-bill-root.py",
    AUDIT_DIR / "bill-root-study-v1.json",
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def serial(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if hasattr(value, "to_list"):
        return [serial(v) for v in value.to_list()]
    if hasattr(value, "keys") and hasattr(value, "__getitem__"):
        return {k: serial(value[k]) for k in sorted(value.keys())}
    try:
        return [serial(v) for v in value]
    except TypeError:
        return str(value)


def mesh_signature(mesh):
    coords = hashlib.sha256()
    for vertex in mesh.vertices:
        coords.update(struct.pack("<3d", *vertex.co))
    topology = hashlib.sha256()
    for edge in mesh.edges:
        topology.update(struct.pack("<2I", *edge.vertices))
    for polygon in mesh.polygons:
        topology.update(struct.pack("<I", len(polygon.vertices)))
        topology.update(struct.pack(f"<{len(polygon.vertices)}I", *polygon.vertices))
        topology.update(struct.pack("<i?", polygon.material_index, polygon.use_smooth))
    return {
        "name": mesh.name,
        "vertices": len(mesh.vertices),
        "edges": len(mesh.edges),
        "polygons": len(mesh.polygons),
        "coordinateSha256": coords.hexdigest(),
        "topologyAndFaceStateSha256": topology.hexdigest(),
        "materials": [material.name if material else None for material in mesh.materials],
    }


def curve_signature(curve):
    payload = []
    for spline in curve.splines:
        if spline.type == "BEZIER":
            points = [[list(p.co), list(p.handle_left), list(p.handle_right), p.handle_left_type, p.handle_right_type]
                      for p in spline.bezier_points]
        else:
            points = [list(p.co) for p in spline.points]
        payload.append({"type": spline.type, "cyclic": spline.use_cyclic_u, "points": points})
    return {"name": curve.name, "dimensions": curve.dimensions, "resolutionU": curve.resolution_u,
            "bevelDepth": curve.bevel_depth, "fillMode": curve.fill_mode, "splines": payload,
            "materials": [material.name if material else None for material in curve.materials]}


def material_signature(material):
    nodes = []
    links = []
    if material.use_nodes and material.node_tree:
        for node in material.node_tree.nodes:
            inputs = []
            for socket in node.inputs:
                if not socket.enabled or not hasattr(socket, "default_value"):
                    continue
                inputs.append([socket.identifier, serial(socket.default_value)])
            nodes.append({"name": node.name, "type": node.bl_idname, "inputs": sorted(inputs)})
        links = sorted([link.from_node.name, link.from_socket.name, link.to_node.name, link.to_socket.name]
                       for link in material.node_tree.links)
    payload = {
        "name": material.name, "diffuseColor": list(material.diffuse_color),
        "metallic": material.metallic, "roughness": material.roughness,
        "useNodes": material.use_nodes, "nodes": sorted(nodes, key=lambda node: node["name"]), "links": links,
    }
    return digest_bytes(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())


def matrix_signature(matrix):
    return [float(matrix[row][column]) for row in range(4) for column in range(4)]


def object_signature(obj):
    if obj.type == "MESH":
        data = mesh_signature(obj.data)
    elif obj.type == "CURVE":
        data = curve_signature(obj.data)
    elif obj.data is None:
        data = None
    else:
        data = {"name": obj.data.name, "type": obj.data.__class__.__name__}
    modifiers = []
    for modifier in obj.modifiers:
        attrs = {}
        for key in ("levels", "render_levels", "thickness", "offset", "width", "segments", "limit_method", "angle_limit", "use_clamp_overlap", "use_even_offset"):
            if hasattr(modifier, key):
                attrs[key] = serial(getattr(modifier, key))
        modifiers.append({"name": modifier.name, "type": modifier.type, "attributes": attrs})
    return {
        "type": obj.type, "data": data,
        "parent": obj.parent.name if obj.parent else None,
        "parentType": obj.parent_type,
        "matrixBasis": matrix_signature(obj.matrix_basis),
        "matrixParentInverse": matrix_signature(obj.matrix_parent_inverse),
        "rotationMode": obj.rotation_mode,
        "hideRender": bool(obj.hide_render),
        "customProperties": {key: serial(obj[key]) for key in sorted(obj.keys())},
        "modifiers": modifiers,
    }


def snapshot():
    objects = {obj.name: object_signature(obj) for obj in bpy.data.objects}
    materials = {mat.name: material_signature(mat) for mat in bpy.data.materials}
    return {"objects": objects, "materials": materials}


def open_polyline(rows, t):
    x = max(0.0, min(1.0, t)) * (len(rows) - 1)
    i = min(int(x), len(rows) - 2)
    u = x - i
    p0, p1 = rows[max(0, i - 1)], rows[i]
    p2, p3 = rows[i + 1], rows[min(len(rows) - 1, i + 2)]
    return tuple(0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * u +
                        (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * u * u +
                        (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * u * u * u)
                 for k in range(len(p1)))


def linear_sample(sections, z):
    for a, b in zip(sections, sections[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return tuple(a[i] + (b[i] - a[i]) * t for i in range(1, len(a)))
    return sections[0][1:] if z < sections[0][0] else sections[-1][1:]


def cranial_side_width(y, z):
    cy, rx, ry = linear_sample(HEAD_SECTIONS, z)
    q = (y - cy) / max(.05, ry)
    return rx * math.sqrt(max(.12, 1 - q * q))


def closed_brow_geometry(side):
    along, across = 40, 8
    stride = across + 1
    vertices, faces = [], []
    for skin in (0, 1):
        for j in range(along + 1):
            t = j / along
            y, z, width, depth = open_polyline(BROW_PATH, t)
            previous = open_polyline(BROW_PATH, max(0, t - 1 / along))
            following = open_polyline(BROW_PATH, min(1, t + 1 / along))
            dy, dz = following[0] - previous[0], following[1] - previous[1]
            magnitude = max(1e-8, math.hypot(dy, dz))
            for k in range(stride):
                u = k / across
                offset = (2 * u - 1) * max(.001, width)
                crown = .0025 * math.sin(math.pi * u)
                lateral = .030 + (crown if skin == 0 else -max(.003, depth))
                x = cranial_side_width(y - dz / magnitude * offset,
                                       z + dy / magnitude * offset) + lateral
                vertices.append((side * x, y - dz / magnitude * offset,
                                 z + dy / magnitude * offset))
    count = (along + 1) * stride
    for j in range(along):
        for k in range(across):
            a = j * stride + k
            b, c, d = a + 1, a + 1 + stride, a + stride
            faces.extend([(a, b, c, d), (count + d, count + c, count + b, count + a)])
        a, b = j * stride, (j + 1) * stride
        faces.append((a, b, count + b, count + a))
        a, b = j * stride + across, (j + 1) * stride + across
        faces.append((b, a, count + a, count + b))
    for k in range(across):
        faces.append((k + 1, k, count + k, count + k + 1))
        a = along * stride + k
        faces.append((a, a + 1, count + a + 1, count + a))
    return vertices, faces


def cere_plate_geometry(side):
    count = len(CERE_OUTLINE)
    center_y = sum(point[0] for point in CERE_OUTLINE) / count
    center_z = sum(point[1] for point in CERE_OUTLINE) / count
    inset = [(center_y + (y - center_y) * .84, center_z + (z - center_z) * .84)
             for y, z in CERE_OUTLINE]

    def point(yz, lateral):
        y, z = yz
        surface_x = .129 - .75 * max(0.0, -y - .425)
        return (side * (surface_x + lateral), y, z)

    vertices = []
    vertices.extend(point(yz, .003) for yz in CERE_OUTLINE)  # inset back
    vertices.extend(point(yz, .018) for yz in CERE_OUTLINE)  # raised outer rim
    vertices.extend(point(yz, .025) for yz in inset)         # bevel-to-face transition
    vertices.append(point((center_y, center_z), .003))       # back center
    vertices.append(point((center_y, center_z), .025))       # front center
    back_center, front_center = 3 * count, 3 * count + 1
    faces = []
    for i in range(count):
        nxt = (i + 1) % count
        back_i, back_n = i, nxt
        outer_i, outer_n = count + i, count + nxt
        inner_i, inner_n = 2 * count + i, 2 * count + nxt
        faces.append((outer_i, outer_n, inner_n, inner_i))
        faces.append((inner_i, inner_n, front_center))
        faces.append((back_i, back_n, outer_n, outer_i))
        faces.append((back_n, back_i, back_center))
    return vertices, faces


def replace_mesh_geometry(obj, world_vertices, faces, transform_smooth=False):
    inverse = obj.matrix_world.inverted()
    local_vertices = [inverse @ Vector(vertex) for vertex in world_vertices]
    mesh = obj.data
    materials = list(mesh.materials)
    mesh.clear_geometry()
    mesh.from_pydata(local_vertices, [], faces)
    mesh.materials.clear()
    for material in materials:
        mesh.materials.append(material)
    mesh.update(calc_edges=True)
    for polygon in mesh.polygons:
        polygon.use_smooth = transform_smooth
    mesh.validate(clean_customdata=False)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()


def build_candidate():
    if sha(SOURCE) != EXPECTED_SOURCE_SHA:
        raise RuntimeError("Frozen v6 BLEND changed; refusing to use a different source")
    if sha(HEAD_RECIPE) != EXPECTED_HEAD_RECIPE_SHA:
        raise RuntimeError("The bound v6 head recipe changed; reconcile before generating the study")
    if sha(PRIOR_RECEIPT) != EXPECTED_PRIOR_REVIEW_SHA:
        raise RuntimeError("The prior bill-study review changed; reconcile before generating the study")
    if sha(INVENTORY) != EXPECTED_INVENTORY_SHA:
        raise RuntimeError("The bound v6 native inventory changed; reconcile before generating the study")
    for directory in (MODEL_DIR, AUDIT_DIR):
        if directory.exists() and not directory.is_dir():
            raise RuntimeError(f"Study output path is not a directory: {directory}")
        directory.mkdir(parents=True, exist_ok=True)
    existing = [str(path) for path in FINAL_OUTPUTS if path.exists()]
    if existing:
        raise RuntimeError(f"Refusing to overwrite existing/manual study outputs: {existing}")
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    before = snapshot()
    targets = {name: bpy.data.objects.get(name) for name in EXPECTED_TARGETS}
    if any(obj is None or obj.type != "MESH" for obj in targets.values()):
        raise RuntimeError("Exact four-mesh allowlist is not present in the frozen v6 source")
    expected_parents = {
        "Forged orbital brow -1": "cranial-cover", "Forged orbital brow 1": "cranial-cover",
        "Cere root transition -1": "upper-bill", "Cere root transition 1": "upper-bill",
    }
    for name, obj in targets.items():
        if obj.parent is None or obj.parent.name != expected_parents[name]:
            raise RuntimeError(f"Unexpected owner for allowlisted target {name}")

    for side in (-1, 1):
        brow = targets[f"Forged orbital brow {side}"]
        brow_vertices, brow_faces = closed_brow_geometry(side)
        if len(brow.data.vertices) != len(brow_vertices) or len(brow.data.polygons) != len(brow_faces):
            raise RuntimeError(f"Unexpected native brow topology: {brow.name}")
        replace_mesh_geometry(brow, brow_vertices, brow_faces, transform_smooth=True)
        cere = targets[f"Cere root transition {side}"]
        cere_vertices, cere_faces = cere_plate_geometry(side)
        replace_mesh_geometry(cere, cere_vertices, cere_faces, transform_smooth=False)

    after = snapshot()
    assert set(before["objects"]) == set(after["objects"]), "Object inventory changed"
    assert before["materials"] == after["materials"], "A material changed"
    changed = {name for name in before["objects"] if before["objects"][name] != after["objects"][name]}
    assert changed == EXPECTED_TARGETS, f"Geometry changes escaped the exact allowlist: {sorted(changed ^ EXPECTED_TARGETS)}"
    for name in EXPECTED_TARGETS:
        old, new = before["objects"][name], after["objects"][name]
        for key in ("type", "parent", "parentType", "matrixBasis", "matrixParentInverse", "rotationMode", "hideRender", "customProperties", "modifiers"):
            assert old[key] == new[key], f"Allowlisted target metadata changed: {name}/{key}"
        assert old["data"]["materials"] == new["data"]["materials"], f"Material assignment changed: {name}"
    for name in set(before["objects"]) - EXPECTED_TARGETS:
        assert before["objects"][name] == after["objects"][name], f"Unmodified native object changed: {name}"

    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE), check_existing=False)
    candidate_sha = sha(CANDIDATE)
    expected_saved = snapshot()
    bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE))
    reloaded = snapshot()
    assert expected_saved == reloaded, "Reloaded study differs from the saved candidate"
    assert set(reloaded["objects"]) == set(before["objects"]), "Reload changed object membership"
    assert reloaded["materials"] == before["materials"], "Reload changed material inventory"
    for name in set(before["objects"]) - EXPECTED_TARGETS:
        assert before["objects"][name] == reloaded["objects"][name], f"Reload changed unmodified object: {name}"
    assert {name for name in before["objects"] if before["objects"][name] != reloaded["objects"][name]} == EXPECTED_TARGETS
    return before, reloaded, candidate_sha


def render_views(blend_path, phase):
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))
    scene = bpy.context.scene
    scene.frame_set(1)
    scene.render.engine = "BLENDER_WORKBENCH"
    shading = scene.display.shading
    shading.light = "STUDIO"
    shading.studio_light = "paint.sl"
    shading.color_type = "MATERIAL"
    shading.show_shadows = True
    shading.show_cavity = True
    shading.cavity_type = "BOTH"
    shading.curvature_ridge_factor = 1.2
    shading.curvature_valley_factor = 1.1
    shading.background_type = "WORLD"
    scene.world.color = (0.11, 0.12, 0.13)
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    for obj in scene.objects:
        if obj.type == "MESH":
            obj.hide_render = "builder" not in obj.get("exteriorEras", "maker,mechanic,builder").split(",")
            obj.hide_set(False)
    camera_data = bpy.data.cameras.new("Bill-root study camera")
    camera = bpy.data.objects.new("Bill-root study camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    rows = []
    for spec in CAMERAS:
        camera.location = spec["position"]
        camera.rotation_euler = (Vector(spec["target"]) - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera_data.type = "ORTHO"
        camera_data.ortho_scale = spec["orthoScale"]
        image = AUDIT_DIR / f"{phase}-{spec['name']}.png"
        scene.render.filepath = str(image)
        bpy.ops.render.render(write_still=True)
        rows.append({"path": str(image.relative_to(ROOT)), "sha256": sha(image), "bytes": image.stat().st_size,
                     "camera": {**spec, "projection": "ORTHO", "resolution": [1100, 1100]}})
    return rows


before, candidate, candidate_sha = build_candidate()
before_views = render_views(SOURCE, "before")
after_views = render_views(CANDIDATE, "after")
if sha(SOURCE) != EXPECTED_SOURCE_SHA or sha(CANDIDATE) != candidate_sha:
    raise RuntimeError("Frozen source or candidate changed during the study")
source_inventory = json.loads(INVENTORY.read_text())
inventory_targets = {item["name"]: item for item in source_inventory["parts"] if item["name"] in EXPECTED_TARGETS}
assert set(inventory_targets) == EXPECTED_TARGETS
script = Path(__file__).resolve()
script_snapshot = AUDIT_DIR / "study-alignment-bill-root.py"
shutil.copy2(script, script_snapshot)
manifest = {
    "title": "Isolated bill-root and brow construction study v1",
    "status": "editable native-only proposal; no GLB, runtime integration, or artistic acceptance",
    "source": {
        "nativeBlend": {"path": str(SOURCE.relative_to(ROOT)), "sha256": EXPECTED_SOURCE_SHA},
        "headRecipe": {"path": str(HEAD_RECIPE.relative_to(ROOT)), "sha256": EXPECTED_HEAD_RECIPE_SHA},
        "julyReference": {"path": str(JULY_REFERENCE.relative_to(ROOT)), "sha256": sha(JULY_REFERENCE), "scope": "head only"},
        "priorBillStudyReview": {"path": str(PRIOR_RECEIPT.relative_to(ROOT)), "sha256": EXPECTED_PRIOR_REVIEW_SHA},
        "nativeInventory": {"path": str(INVENTORY.relative_to(ROOT)), "sha256": EXPECTED_INVENTORY_SHA},
    },
    "candidate": {"path": str(CANDIDATE.relative_to(ROOT)), "sha256": candidate_sha, "bytes": CANDIDATE.stat().st_size},
    "scriptSnapshot": {"path": str(script_snapshot.relative_to(ROOT)), "sha256": sha(script_snapshot)},
    "changeAllowlist": sorted(EXPECTED_TARGETS),
    "targetContracts": {
        name: {"inventory": inventory_targets[name], "sourceTransformPreserved": True,
               "parentPreserved": True, "materialsPreserved": True, "customPropertiesPreserved": True}
        for name in sorted(EXPECTED_TARGETS)
    },
    "verification": {
        "objectNameInventoryPreserved": True,
        "onlyAllowlistedMeshGeometryChanged": True,
        "allOtherMeshAndCurveGeometryExactlyPreserved": True,
        "allObjectTransformsParentsPropertiesAndModifiersExactlyPreserved": True,
        "allMaterialSignaturesAndAssignmentsExactlyPreserved": True,
        "candidateReloadedAndSnapshotCompared": True,
        "beforeAfterViewsUseSameCameras": True,
        "changedGeometry": {
            "brow": "Wider, slightly deeper closed profile between fixed root/end stations; same 738-vertex/736-face topology and owner.",
            "cereRoot": "Replaced small rounded patch with a closed, faceted inset shield that overlaps brow and bill root; no new objects or materials.",
        },
    },
    "renders": {"before": before_views, "after": after_views},
    "limits": [
        "July illustration guides the head only and is not exact-dimensional evidence.",
        "Neutral Workbench images are static authoring views, not runtime shader or animation evidence.",
        "Intentional rigid plate overlap is proposed visually; no jaw/head, jaw/neck, optic-clearance, or strike-contact validation has been run on this new geometry.",
        "The candidate must be reviewed for broad silhouette and bill opening before any export or integration.",
    ],
}
(AUDIT_DIR / "bill-root-study-v1.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({"candidate": str(CANDIDATE), "sha256": candidate_sha,
                  "changedObjects": sorted(EXPECTED_TARGETS), "beforeViews": len(before_views), "afterViews": len(after_views)}))
