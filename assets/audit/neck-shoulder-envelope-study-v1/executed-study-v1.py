"""Create a write-once native neck/shoulder envelope study from pinned V7.

This is an isolated geometry study. It edits only the explicit mesh allowlist
below, adds six neck-side plate meshes, and never changes an existing object
transform, pivot, material, or runtime/application file. It renders matched
neutral Builder views before and after for a bounded silhouette comparison.
"""
from pathlib import Path
import hashlib
import json
import math
import shutil
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/models/uncaged-alignment-v7/murderbird-alignment-v7.blend"
MODEL_DIR = ROOT / "assets/models/uncaged-neck-shoulder-envelope-study-v1"
AUDIT_DIR = ROOT / "assets/audit/neck-shoulder-envelope-study-v1"
BEFORE_BLEND = MODEL_DIR / "murderbird-v7-source-preserved.blend"
AFTER_BLEND = MODEL_DIR / "murderbird-neck-shoulder-envelope-study-v1.blend"
REPORT_PATH = AUDIT_DIR / "study-manifest.json"
EXPECTED_SOURCE_SHA256 = "a8fccaf024a096678415215029b34cae8270b348da2301b8872a34e72c75ed3f"

LEFT_BACKING = "left profiled mantle backing v4 left-mantle"
RIGHT_BACKING = "right profiled mantle backing v4 right-mantle"
LEFT_SADDLE = "left oblique shoulder saddle v4"
RIGHT_SADDLE = "right oblique shoulder saddle v4"
SHOULDER_MESHES = [
    LEFT_BACKING, RIGHT_BACKING, LEFT_SADDLE, RIGHT_SADDLE,
    *[f"{side} shoulder covert 0 {row}" for side in ("left", "right") for row in range(8)],
]
NECK_ADDITIONS = [f"Study cervical side guard {side} {index}"
                  for side in ("left", "right") for index in range(1, 4)]
NECK_SECTIONS = [
    (1.25, -.095, .205, .208),
    (1.325, -.15, .177, .19),
    (1.41, -.23, .147, .17),
    (1.48, -.283, .127, .148),
    (1.55, -.253, .109, .107),
    (1.60, -.218, .088, .086),
    (1.65, -.200, .082, .082),
]
NECK_GUARD_BANDS = [
    (1.292, 1.405),
    (1.394, 1.507),
    (1.496, 1.594),
]
MAX_CREST_DROP_M = .025
MAX_TUCK_M = .015
PIN_ZERO_RADIUS_M = .012
PIN_FULL_RADIUS_M = .030


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def smoothstep(value):
    t = max(0.0, min(1.0, value))
    return t * t * (3.0 - 2.0 * t)


def state_digest(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def matrix_record(matrix):
    return [[round(float(matrix[r][c]), 9) for c in range(4)] for r in range(4)]


def mesh_record(obj):
    mesh = obj.data
    return state_digest({
        "verts": [[round(float(c), 9) for c in vertex.co] for vertex in mesh.vertices],
        "edges": [list(edge.vertices) for edge in mesh.edges],
        "faces": [list(poly.vertices) for poly in mesh.polygons],
        "mats": [mat.name if mat else None for mat in mesh.materials],
    })


def object_state():
    result = {}
    for obj in bpy.data.objects:
        result[obj.name] = {
            "type": obj.type,
            "parent": obj.parent.name if obj.parent else None,
            "matrix": matrix_record(obj.matrix_world),
            "mesh": mesh_record(obj) if obj.type == "MESH" else None,
            "materialSlots": [slot.material.name if slot.material else None for slot in obj.material_slots],
        }
    return result


def material_content_signature(material):
    return state_digest({
        "diffuse": [round(float(v), 9) for v in material.diffuse_color],
        "metallic": round(float(material.metallic), 9),
        "roughness": round(float(material.roughness), 9),
        "useNodes": bool(material.use_nodes),
        "nodes": sorted((node.name, node.bl_idname) for node in material.node_tree.nodes) if material.use_nodes and material.node_tree else [],
        "links": sorted((link.from_node.name, link.from_socket.name, link.to_node.name, link.to_socket.name)
                         for link in material.node_tree.links) if material.use_nodes and material.node_tree else [],
    })


def sample_section(z):
    if z <= NECK_SECTIONS[0][0]:
        return NECK_SECTIONS[0][1:]
    if z >= NECK_SECTIONS[-1][0]:
        return NECK_SECTIONS[-1][1:]
    for a, b in zip(NECK_SECTIONS, NECK_SECTIONS[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            # Smoothly ease between authored control sections while staying
            # within the neighbouring controls; this is reconstruction data.
            t = smoothstep(t)
            return tuple(a[i] + (b[i] - a[i]) * t for i in range(1, 4))
    raise AssertionError(z)


def neck_surface(z, angle, radial_offset):
    cy, rx, ry = sample_section(z)
    return Vector((math.sin(angle) * (rx + radial_offset),
                   cy - math.cos(angle) * (ry + radial_offset), z))


def make_neck_guard(name, side, band, template):
    low, high = band
    across, along = 12, 8
    start_angle, end_angle = 1.43, 2.32
    vertices, faces = [], []
    for j in range(along + 1):
        t = j / along
        z = low + (high - low) * t
        for k in range(across + 1):
            u = k / across
            angle = start_angle + (end_angle - start_angle) * u
            # Each rigid plate has softened edges and a modest crown. Its
            # angular extent stays behind the documented forward/lateral jaw
            # recess; the outer stand-off follows the existing neck envelope.
            q = 2.0 * u - 1.0
            edge = abs(q)
            edge_fade = max(0.0, 1.0 - edge * edge)
            end_fade = smoothstep(min(t / .12, (1.0 - t) / .12))
            offset = .010 + .009 * edge_fade * end_fade
            angle *= side
            vertices.append(neck_surface(z, angle, offset))
    stride = across + 1
    for j in range(along):
        for k in range(across):
            i = j * stride + k
            face = (i, i + 1, i + stride + 1, i + stride)
            # Winding is corrected below by the signed face-normal test.
            faces.append(face)
    for index, face in enumerate(faces[:1]):
        p = [vertices[i] for i in face[:3]]
        center = sum(p, Vector()) / 3
        angle = math.atan2(center.x, -(center.y - sample_section(center.z)[0]))
        outward = Vector((math.sin(angle), -math.cos(angle), 0.0))
        if (p[1] - p[0]).cross(p[2] - p[0]).dot(outward) < 0:
            faces = [tuple(reversed(f)) for f in faces]
    neck = bpy.data.objects["neck"]
    world_to_neck = neck.matrix_world.inverted()
    local_vertices = [world_to_neck @ point for point in vertices]
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata(local_vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = bpy.data.objects["neck"]
    # Mesh vertices are local to the inherited neck pivot. Each guard remains
    # an independently owned rigid object with identity local transform.
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_basis = Matrix.Identity(4)
    obj["region"] = "neck"
    obj["surfaceRole"] = "plate"
    obj["eras"] = "maker,mechanic,builder"
    obj["eraClass"] = "inherited-passive"
    obj["geometryStatus"] = "bounded envelope study reconstruction"
    obj["studyParent"] = "neck"
    source_mat = next((mat for mat in template.data.materials if mat), None)
    if source_mat:
        mesh.materials.append(source_mat)
    solidify = obj.modifiers.new("Study rigid plate wall", "SOLIDIFY")
    solidify.thickness = .006
    solidify.offset = -1.0
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    return obj


def configure_neutral(scene):
    scene.frame_set(1)
    scene.render.engine = "BLENDER_WORKBENCH"
    shade = scene.display.shading
    shade.light = "STUDIO"
    shade.studio_light = "paint.sl"
    shade.color_type = "MATERIAL"
    shade.show_shadows = True
    shade.show_cavity = True
    shade.cavity_type = "BOTH"
    shade.curvature_ridge_factor = 1.2
    shade.curvature_valley_factor = 1.1
    shade.background_type = "WORLD"
    scene.world.color = (.11, .12, .13)
    scene.render.resolution_x = scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    camera_data = bpy.data.cameras.new("Envelope study comparison camera")
    camera = bpy.data.objects.new("Envelope study comparison camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    return camera, camera_data


def render_views(view_records, phase, views, out_dir):
    scene = bpy.context.scene
    camera, camera_data = configure_neutral(scene)
    saved_visibility = {obj.name: (bool(obj.hide_render), bool(obj.hide_get())) for obj in scene.objects}
    for obj in scene.objects:
        if obj.type == "MESH":
            obj.hide_render = "builder" not in obj.get("exteriorEras", "maker,mechanic,builder").split(",")
            obj.hide_set(False)
    for name, position, target, scale in views:
        camera.location = position
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera_data.type = "ORTHO"
        camera_data.ortho_scale = scale
        path = out_dir / f"{phase}-{name}.png"
        require(not path.exists(), f"Write-once render already exists: {path}")
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        view_records.append({"phase": phase, "view": name, "path": str(path.relative_to(ROOT)),
                             "bytes": path.stat().st_size, "sha256": sha256(path),
                             "camera": list(position), "target": list(target),
                             "projection": "ORTHO", "orthoScale": scale,
                             "resolution": [1100, 1100]})
    bpy.data.objects.remove(camera, do_unlink=True)
    bpy.data.cameras.remove(camera_data)
    for obj in scene.objects:
        if obj.name in saved_visibility:
            obj.hide_render = saved_visibility[obj.name][0]
            obj.hide_set(saved_visibility[obj.name][1])


def world_bounds(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    evaluated.to_mesh_clear()
    return {
        "min": [round(min(point[i] for point in points), 6) for i in range(3)],
        "max": [round(max(point[i] for point in points), 6) for i in range(3)],
    }


def world_bvh(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    vertices = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    polygons = [list(poly.vertices) for poly in mesh.polygons]
    tree = BVHTree.FromPolygons(vertices, polygons, all_triangles=False, epsilon=0.0)
    evaluated.to_mesh_clear()
    return tree


def main():
    require(sha256(SOURCE) == EXPECTED_SOURCE_SHA256, "Pinned V7 source hash mismatch")
    require(not MODEL_DIR.exists() and not AUDIT_DIR.exists(), "Write-once study output already exists")
    MODEL_DIR.mkdir(parents=True)
    AUDIT_DIR.mkdir(parents=True)
    script_copy = AUDIT_DIR / "executed-study-v1.py"
    shutil.copy2(Path(__file__), script_copy)
    require(sha256(script_copy) == sha256(Path(__file__).resolve()), "Executed generator copy does not match")
    shutil.copy2(SOURCE, BEFORE_BLEND)
    require(sha256(BEFORE_BLEND) == EXPECTED_SOURCE_SHA256, "Preserved source copy hash mismatch")

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    source_blender_version = bpy.app.version_string
    source_states = object_state()
    source_materials = {mat.name: material_content_signature(mat) for mat in bpy.data.materials}
    source_material_ids = list(bpy.data.materials)
    source_material_users = {mat.name: int(mat.users) for mat in source_material_ids}
    require(all(name in bpy.data.objects and bpy.data.objects[name].type == "MESH" for name in SHOULDER_MESHES),
            "An allowlisted shoulder mesh is missing or is not a mesh")
    neck = bpy.data.objects.get("neck")
    body = bpy.data.objects.get("body")
    require(neck and neck.type == "EMPTY" and body is not None, "Required neck/body pivot is absent")
    guard_template = bpy.data.objects.get("Cervical articulated inner guards")
    require(guard_template and guard_template.type == "MESH", "V7 cervical clearance template missing")

    views = [
        ("front", (0, -6, 1.08), (0, -.1, 1.08), 2.4),
        ("rear", (0, 6, 1.08), (0, .05, 1.08), 2.4),
        ("side-right", (-6, 0, 1.08), (0, -.1, 1.08), 2.4),
        ("side-left", (6, 0, 1.08), (0, -.1, 1.08), 2.4),
        ("left-three-quarter", (4.7, -6.5, 2.30), (0, -.1, 1.08), 2.4),
        ("neck", (-4, -6, 1.7), (0, -.2, 1.58), .8),
    ]
    view_records = []
    render_views(view_records, "before", views, AUDIT_DIR)

    # Snapshot the exact 50 shoulder-root pin object matrices. All are preserved;
    # each vertex field is additionally damped around these anchors.
    pin_objects = [obj for obj in bpy.data.objects
                   if obj.type == "MESH" and obj.get("region") == "shoulder"
                   and obj.name.startswith("Shoulder covert root pin")]
    require(len(pin_objects) == 50, f"Expected 50 shoulder covert root pins, found {len(pin_objects)}")
    pin_centers = [obj.matrix_world.translation.copy() for obj in pin_objects]
    pin_state = {obj.name: matrix_record(obj.matrix_world) for obj in pin_objects}
    shoulder_changes = []
    changed = set(SHOULDER_MESHES)
    for name in SHOULDER_MESHES:
        obj = bpy.data.objects[name]
        original_bounds = world_bounds(obj)
        inverse = obj.matrix_world.inverted()
        max_move = 0.0
        max_dz = 0.0
        max_dx = 0.0
        locked_vertices = 0
        for vertex in obj.data.vertices:
            world = obj.matrix_world @ vertex.co
            abs_x = abs(float(world.x))
            height_weight = smoothstep((float(world.z) - 1.29) / .13)
            crest_delta = -MAX_CREST_DROP_M * height_weight
            tuck_weight = smoothstep((abs_x - .37) / .11) * height_weight
            tuck_delta = -math.copysign(MAX_TUCK_M * tuck_weight, float(world.x))
            nearest_pin = min((world - center).length for center in pin_centers)
            pin_weight = smoothstep((nearest_pin - PIN_ZERO_RADIUS_M) /
                                    (PIN_FULL_RADIUS_M - PIN_ZERO_RADIUS_M))
            if nearest_pin <= PIN_ZERO_RADIUS_M:
                locked_vertices += 1
            delta = Vector((tuck_delta * pin_weight, 0.0, crest_delta * pin_weight))
            moved = world + delta
            vertex.co = inverse @ moved
            max_move = max(max_move, delta.length)
            max_dx = max(max_dx, abs(delta.x))
            max_dz = max(max_dz, abs(delta.z))
        obj.data.update()
        shoulder_changes.append({"name": name, "beforeBounds": original_bounds,
                                 "maxVertexDisplacementM": round(max_move, 6),
                                 "maxInwardXDisplacementM": round(max_dx, 6),
                                 "maxLoweringM": round(max_dz, 6),
                                 "verticesLockedNearRootPins": locked_vertices})

    added = []
    for side_name, side_sign in (("left", 1), ("right", -1)):
        for index, band in enumerate(NECK_GUARD_BANDS, start=1):
            name = f"Study cervical side guard {side_name} {index}"
            obj = make_neck_guard(name, side_sign, band, guard_template)
            added.append({"name": obj.name, "parent": obj.parent.name, "bandZ": list(band),
                          "worldBounds": world_bounds(obj), "verts": len(obj.data.vertices),
                          "faces": len(obj.data.polygons),
                          "materialSlots": [m.name if m else None for m in obj.data.materials],
                          "eraClass": obj.get("eraClass"), "eras": obj.get("eras")})
    require(set(x["name"] for x in added) == set(NECK_ADDITIONS), "Unexpected cervical guard addition set")

    # Preserve only known source orphan materials as explicit fake users. No
    # existing material data or slot assignment is changed.
    orphan_materials = []
    for material in source_material_ids:
        if source_material_users[material.name] == 0:
            material.use_fake_user = True
            orphan_materials.append(material.name)

    after_states = object_state()
    new_names = sorted(set(after_states) - set(source_states))
    require(new_names == sorted(NECK_ADDITIONS), f"Unexpected added object set: {new_names}")
    changed_existing = sorted(name for name in source_states
                              if source_states[name]["mesh"] != after_states[name]["mesh"]
                              or source_states[name]["matrix"] != after_states[name]["matrix"]
                              or source_states[name]["parent"] != after_states[name]["parent"]
                              or source_states[name]["materialSlots"] != after_states[name]["materialSlots"])
    require(changed_existing == sorted(SHOULDER_MESHES),
            "Unexpected changed existing object allowlist: " + repr(changed_existing))
    matrix_changes = [name for name in source_states if source_states[name]["matrix"] != after_states[name]["matrix"]]
    require(not matrix_changes, "Existing object transform/pivot changed: " + repr(matrix_changes))
    changed_materials = sorted(name for name, signature in source_materials.items()
                               if name not in bpy.data.materials or
                               material_content_signature(bpy.data.materials[name]) != signature)
    require(not changed_materials, "Existing material content changed: " + repr(changed_materials))
    require({obj.name: matrix_record(obj.matrix_world) for obj in pin_objects} == pin_state,
            "Shoulder attachment pin transforms changed")

    # Record the actual achieved envelope after mesh evaluation.
    for item in shoulder_changes:
        item["afterBounds"] = world_bounds(bpy.data.objects[item["name"]])
        item["beforeMeshSha256"] = source_states[item["name"]]["mesh"]
        item["afterMeshSha256"] = mesh_record(bpy.data.objects[item["name"]])

    # Probe intersections between each new external plate and the body/remaining
    # head-neck geometry at the inherited pose plus runtime cervical extremes.
    # These are surface-intersection diagnostics, not physics or general
    # continuous-collision proof.
    clearance_samples = []
    saved_neck = (neck.location.copy(), neck.rotation_euler.copy())
    for label, pitch, yaw in (("rest", 0.0, 0.0), ("contact-pitch-max", .65, 0.0),
                              ("contact-pitch-min", -.65, 0.0),
                              ("operator-yaw-left", -.14, .45),
                              ("operator-yaw-right", -.14, -.45)):
        neck.rotation_euler = (pitch, yaw, 0.0)
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        new_trees = [(name, world_bvh(bpy.data.objects[name], depsgraph)) for name in NECK_ADDITIONS]
        body_hits = 0
        neck_hits = 0
        for other in bpy.data.objects:
            if other.type != "MESH" or other.name in NECK_ADDITIONS:
                continue
            # Only the moving body/neck/head assembly can create study contact.
            if other.get("region") not in {"body", "neck", "head", "shoulder", "breast"}:
                continue
            tree = world_bvh(other, depsgraph)
            if tree is None:
                continue
            for name, new_tree in new_trees:
                if new_tree is None:
                    continue
                count = len(new_tree.overlap(tree))
                if other.get("region") in {"body", "breast"}:
                    body_hits += count
                else:
                    neck_hits += count
        clearance_samples.append({"pose": label, "neckPitchRad": pitch, "neckYawRad": yaw,
                                  "bodySurfaceTriangleOverlapPairs": body_hits,
                                  "headNeckShoulderSurfaceTriangleOverlapPairs": neck_hits})
    neck.location = saved_neck[0]
    neck.rotation_euler = saved_neck[1]
    bpy.context.view_layer.update()

    # Restore the visible Builder state and render identical comparison views.
    render_views(view_records, "after", views, AUDIT_DIR)
    bpy.ops.wm.save_as_mainfile(filepath=str(AFTER_BLEND), check_existing=False)
    require(sha256(BEFORE_BLEND) == EXPECTED_SOURCE_SHA256, "Preserved V7 source changed")
    require(sha256(AFTER_BLEND) != EXPECTED_SOURCE_SHA256, "Study file is identical to source")

    report = {
        "schemaVersion": 1,
        "status": "isolated neutral native geometry study; owner review required",
        "source": {"path": str(SOURCE.relative_to(ROOT)), "sha256": EXPECTED_SOURCE_SHA256,
                   "bytes": SOURCE.stat().st_size,
                   "preservedCopy": str(BEFORE_BLEND.relative_to(ROOT)),
                   "preservedCopySha256": sha256(BEFORE_BLEND),
                   "preservedCopyBytes": BEFORE_BLEND.stat().st_size},
        "study": {"path": str(AFTER_BLEND.relative_to(ROOT)), "sha256": sha256(AFTER_BLEND),
                  "bytes": AFTER_BLEND.stat().st_size,
                  "blenderVersion": source_blender_version},
        "executedGenerator": {"path": str(script_copy.relative_to(ROOT)),
                               "sha256": sha256(script_copy),
                               "executedPath": str(Path(__file__).resolve().relative_to(ROOT)),
                               "executedSha256": sha256(Path(__file__).resolve()),
                               "copyMatchesExecuted": sha256(script_copy) == sha256(Path(__file__).resolve())},
        "scope": {
            "changedExistingMeshes": SHOULDER_MESHES,
            "addedMeshes": added,
            "preservedExistingObjects": len(source_states) - len(SHOULDER_MESHES),
            "preservedAllExistingObjectTransforms": not matrix_changes,
            "preservedShoulderRootPinTransforms": True,
            "shoulderRootPins": len(pin_objects),
            "retainedUnassignedSourceMaterialsAsFakeUsers": orphan_materials,
            "existingMaterialContentChanged": changed_materials,
            "existingMaterialSlotsChanged": [],
            "existingGeometryOutsideAllowlistChanged": False,
            "pivotNamesAndWorldMatrices": {name: source_states[name]["matrix"] for name in
                ("neck", "head", "jaw", "left-mantle", "right-mantle", "left-wing-shield", "right-wing-shield")},
        },
        "shoulderEnvelope": {
            "authoredMaximumCrestDropM": MAX_CREST_DROP_M,
            "authoredMaximumInwardTuckM": MAX_TUCK_M,
            "rootAnchorZeroRadiusM": PIN_ZERO_RADIUS_M,
            "rootAnchorFullWeightRadiusM": PIN_FULL_RADIUS_M,
            "meshBoundsAndDisplacements": shoulder_changes,
        },
        "neckGuards": {
            "count": len(added),
            "bandsZ": [list(band) for band in NECK_GUARD_BANDS],
            "sideAngularBandRad": [1.43, 2.32],
            "authoredSurfaceOffsetM": [0.010, 0.019],
            "approach": "Three distinct overlapping rigid plate meshes per side follow the inherited cervical section envelope behind the documented forward/lateral jaw recess. The neck pivot, forks, inner guard, head, optic, jaw, and throat plates remain unchanged.",
            "clearanceDiagnostics": clearance_samples,
            "diagnosticLimit": "BVH surface triangle overlap at five sampled cervical pitch/yaw poses only; not a complete swept-clearance or physical performance test.",
        },
        "views": view_records,
        "sourceInterpretation": {
            "candidate03": "Qualitative oblique illustration; it shows a compact folded near mantle and fuller neck-to-breast contour but supplies no mesh, dimensions, hidden side topology, or precise structural construction.",
            "confirmedFromV7": "Pivot identities, object ownership, and current evaluated mesh extents are from pinned V7 native geometry.",
            "reconstructed": "The added neck plates and mirrored shoulder-envelope deformation are an authored shape study, not source-measured geometry or accepted final art.",
        },
        "limits": [
            "No GLB, materials, app files, runtime assets, or acceptance criteria were changed.",
            "The bilateral far-side contour is a symmetry-based reconstruction; candidate 03 depicts only one oblique side.",
            "Neutral Workbench views do not establish browser/export appearance or owner acceptance.",
            "Surface-overlap diagnostics do not establish continuous collision clearance, load capacity, or physical feasibility.",
        ],
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    print("STUDY", json.dumps({"source": EXPECTED_SOURCE_SHA256,
                              "study": sha256(AFTER_BLEND),
                              "changedMeshes": len(SHOULDER_MESHES),
                              "addedNeckGuards": len(added),
                              "renders": len(view_records),
                              "report": str(REPORT_PATH.relative_to(ROOT))}))


if __name__ == "__main__":
    main()
