"""Make and render a tightly bounded upper-bill profile candidate from frozen v6."""
from pathlib import Path
import bpy
import hashlib
import json
import math
import struct
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/models/uncaged-alignment-v6/murderbird-alignment-v6.blend"
OUT_MODEL = ROOT / "assets/models/uncaged-bill-profile-study-v1"
OUT_AUDIT = ROOT / "assets/audit/bill-profile-study-v1"
CANDIDATE = OUT_MODEL / "murderbird-bill-profile-study-v1.blend"
REFERENCE = ROOT / "context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png"
EXPECTED_SOURCE_SHA = "5a7a51941423dd0efcb48b9641b7a49597dad117e218ccb4e94f26315c5e9ded"
EXPECTED_TARGETS = {"Profiled upper bill blade 0", "Profiled upper bill blade 1"}
TARGET_OFFSETS = (0.0, 0.0, 0.025, 0.035, 0.030, 0.012, 0.0, 0.0)
CAMERAS = [
    {"name": "side-biased-three-quarter-a", "position": (-6.0, -3.0, 2.4), "target": (0.0, -0.29, 1.78), "orthoScale": 0.80},
    {"name": "side-biased-three-quarter-b", "position": (-6.0, -4.2, 2.1), "target": (0.0, -0.29, 1.78), "orthoScale": 0.80},
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vertex_digest(mesh):
    digest = hashlib.sha256()
    for vertex in mesh.vertices:
        digest.update(struct.pack("<3d", *vertex.co))
    return digest.hexdigest()


def data_signature(obj):
    data = obj.data
    if data is None:
        return None
    signature = {"name": data.name, "type": data.__class__.__name__}
    if obj.type == "MESH":
        signature["vertices"] = [tuple(float(c) for c in v.co) for v in data.vertices]
        signature["edges"] = [tuple(e.vertices) for e in data.edges]
        signature["polygons"] = [
            (tuple(p.vertices), tuple(p.loop_indices), int(p.material_index), bool(p.use_smooth))
            for p in data.polygons
        ]
        signature["materials"] = [m.name if m else None for m in data.materials]
    elif obj.type == "CURVE":
        splines = []
        for spline in data.splines:
            points = []
            if spline.type == "BEZIER":
                points = [(tuple(p.co), tuple(p.handle_left), tuple(p.handle_right), p.handle_left_type, p.handle_right_type) for p in spline.bezier_points]
            else:
                points = [tuple(p.co) for p in spline.points]
            splines.append((spline.type, bool(spline.use_cyclic_u), points))
        signature["splines"] = splines
        signature["materials"] = [m.name if m else None for m in data.materials]
    return signature


def object_snapshot(obj):
    return {
        "type": obj.type,
        "data": data_signature(obj),
        "parent": obj.parent.name if obj.parent else None,
        "parentType": obj.parent_type,
        "matrixBasis": tuple(float(v) for row in obj.matrix_basis for v in row),
        "matrixParentInverse": tuple(float(v) for row in obj.matrix_parent_inverse for v in row),
        "rotationMode": obj.rotation_mode,
        "hideRender": bool(obj.hide_render),
        "customProperties": {key: obj[key] for key in sorted(obj.keys())},
    }


def snapshot():
    return {obj.name: object_snapshot(obj) for obj in bpy.context.scene.objects}


def curve(points, t):
    x = t * (len(points) - 1)
    i = min(len(points) - 2, int(x))
    u = x - i
    p0, p1 = points[max(0, i - 1)], points[i]
    p2, p3 = points[i + 1], points[min(len(points) - 1, i + 2)]
    return tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * u +
                        (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * u * u +
                        (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * u ** 3)
                 for k in range(len(p1)))


def expected_bill_inner_profiles():
    original = [(-.420, 1.706), (-.482, 1.694), (-.538, 1.674), (-.585, 1.643),
                (-.620, 1.602), (-.641, 1.554), (-.642, 1.503), (-.622, 1.463)]
    adjusted = [(point[0] + TARGET_OFFSETS[index], point[1]) for index, point in enumerate(original)]
    return original, adjusted


def make_candidate():
    if sha(SOURCE) != EXPECTED_SOURCE_SHA:
        raise RuntimeError("Frozen v6 BLEND hash does not match the approved study input")
    if CANDIDATE.exists() or OUT_AUDIT.exists():
        raise RuntimeError("Refusing to overwrite an existing bill-profile study artifact")
    OUT_MODEL.mkdir(parents=True)
    OUT_AUDIT.mkdir(parents=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    before = snapshot()
    targets = [bpy.data.objects.get(name) for name in sorted(EXPECTED_TARGETS)]
    if any(obj is None or obj.type != "MESH" for obj in targets):
        raise RuntimeError("Expected exactly two profiled upper-bill mesh objects")
    if len({obj.data.as_pointer() for obj in targets}) != 2:
        raise RuntimeError("Upper-bill sides unexpectedly share mesh data")

    original_inner, adjusted_inner = expected_bill_inner_profiles()
    per_target = {}
    for obj in targets:
        if len(obj.data.vertices) != 57 * 40:
            raise RuntimeError(f"Unexpected bill mesh vertex layout in {obj.name}: {len(obj.data.vertices)}")
        start = 0.0 if obj.name.endswith(" 0") else 0.25
        end = 0.245 if obj.name.endswith(" 0") else 1.0
        world_to_local = obj.matrix_world.inverted().to_3x3()
        for j in range(57):
            t = start + (end - start) * j / 56
            old_inner_y = curve(original_inner, t)[0]
            new_inner_y = curve(adjusted_inner, t)[0]
            for k in range(40):
                angle = k * math.tau / 40
                cross = 1 - 2 * abs((angle + math.pi) % math.tau - math.pi) / math.pi
                world_delta_y = (new_inner_y - old_inner_y) * (1 - cross) / 2
                if abs(world_delta_y) > 1e-12:
                    obj.data.vertices[j * 40 + k].co += world_to_local @ Vector((0.0, world_delta_y, 0.0))
        per_target[obj.name] = {
            "vertexCount": len(obj.data.vertices),
            "beforeVertexSha256": hashlib.sha256(json.dumps(before[obj.name]["data"]["vertices"], separators=(",", ":")).encode()).hexdigest(),
            "afterVertexSha256": vertex_digest(obj.data),
            "localInnerOffsetsByLandmarkMeters": list(TARGET_OFFSETS),
            "meshOwner": obj.parent.name if obj.parent else None,
            "objectTransformPreserved": True,
        }

    after = snapshot()
    assert set(before) == set(after), "Object inventory changed while forming the candidate"
    assert set(name for name in before if before[name] != after[name]) == EXPECTED_TARGETS, "Changes escaped the two-mesh allowlist"
    for name in EXPECTED_TARGETS:
        original, modified = before[name], after[name]
        assert original["type"] == modified["type"]
        assert original["parent"] == modified["parent"]
        assert original["matrixBasis"] == modified["matrixBasis"]
        assert original["matrixParentInverse"] == modified["matrixParentInverse"]
        assert original["customProperties"] == modified["customProperties"]
        for key in ("name", "type", "edges", "polygons", "materials"):
            assert original["data"][key] == modified["data"][key], f"Target mesh topology/identity changed: {name}/{key}"
    bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE), check_existing=False)
    candidate_sha = sha(CANDIDATE)
    if sha(SOURCE) != EXPECTED_SOURCE_SHA:
        raise RuntimeError("Frozen v6 source changed unexpectedly")

    expected_saved = snapshot()
    bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE))
    reloaded = snapshot()
    if expected_saved != reloaded:
        raise RuntimeError("Saved candidate did not preserve the exact allowlisted in-memory state")
    assert set(reloaded) == set(before)
    assert set(name for name in before if before[name] != reloaded[name]) == EXPECTED_TARGETS
    for name in set(before) - EXPECTED_TARGETS:
        assert before[name] == reloaded[name], f"Unchanged native object differs: {name}"
    return candidate_sha, before, reloaded, per_target


def configure_and_render(blend_path, phase):
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))
    scene = bpy.context.scene
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
    camera_data = bpy.data.cameras.new("Bill profile study camera")
    camera = bpy.data.objects.new("Bill profile study camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    rendered = []
    for spec in CAMERAS:
        camera.location = spec["position"]
        camera.rotation_euler = (Vector(spec["target"]) - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera_data.type = "ORTHO"
        camera_data.ortho_scale = spec["orthoScale"]
        image = OUT_AUDIT / f"{phase}-{spec['name']}.png"
        scene.render.filepath = str(image)
        bpy.ops.render.render(write_still=True)
        rendered.append({
            "image": str(image.relative_to(ROOT)),
            "sha256": sha(image),
            "bytes": image.stat().st_size,
            "camera": {**spec, "projection": "ORTHO", "resolution": [1100, 1100]},
        })
    return rendered


candidate_sha, before, candidate, target_records = make_candidate()
before_images = configure_and_render(SOURCE, "before")
after_images = configure_and_render(CANDIDATE, "after")
if sha(SOURCE) != EXPECTED_SOURCE_SHA or sha(CANDIDATE) != candidate_sha:
    raise RuntimeError("A source or candidate file changed during rendering")
script_path = Path(__file__).resolve()
manifest = {
    "title": "Isolated upper-bill profile study v1",
    "status": "editable static candidate only; no GLB, runtime switch, or artistic approval",
    "sourceBlend": {"path": str(SOURCE.relative_to(ROOT)), "sha256": EXPECTED_SOURCE_SHA},
    "candidateBlend": {"path": str(CANDIDATE.relative_to(ROOT)), "sha256": candidate_sha, "bytes": CANDIDATE.stat().st_size},
    "studyScript": {"path": str(script_path.relative_to(ROOT)), "sha256": sha(script_path)},
    "reference": {"path": str(REFERENCE.relative_to(ROOT)), "sha256": sha(REFERENCE), "scope": "July reference: head only"},
    "changeAllowlist": sorted(EXPECTED_TARGETS),
    "unchangedNativeCheck": {
        "objectInventoryPreserved": True,
        "onlyAllowlistedObjectDataChanged": True,
        "allNonTargetObjectsExactlyMatchAtInspectedNativeFields": True,
        "targetTopologyAndTransformsPreserved": True,
        "checkedFields": ["all object names/types/parents/transforms/custom properties/hide-render state", "all mesh vertex coordinates/topology/material slots", "curve spline coordinates/handles"],
        "note": "The allowlist modifies only the target meshes' vertex-coordinate fields; the original v6 source remains hash-identical.",
    },
    "targetMeshes": target_records,
    "profileAdjustment": {
        "method": "move existing inner-side samples posteriorly and blend the same displacement continuously to zero at the unchanged convex outer surface; preserve each existing 57x40 closed quad grid",
        "posteriorInnerStationOffsetsMeters": list(TARGET_OFFSETS),
        "stationOrder": "root to terminal tip; indices 0, 1, 6, and 7 stay fixed",
        "outerDorsalProfilePreserved": True,
        "transverseWidthPreserved": True,
        "sharpTerminalPointPreserved": True,
        "materialsSensorsOwnersAndRigidTransformsChanged": False,
    },
    "renders": {"before": before_images, "after": after_images},
    "limits": [
        "Render pair is a neutral Workbench authoring comparison at identical approximate three-quarter cameras.",
        "The July image guides head-only form; it does not provide exact dimensions or calibrated camera placement.",
        "The changed contour must be visually assessed for jaw-opening clearance before any further acceptance or export.",
    ],
}
(OUT_AUDIT / "bill-profile-study-v1.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({"candidate": str(CANDIDATE), "sha256": candidate_sha, "renders": len(before_images) + len(after_images), "changedObjects": sorted(EXPECTED_TARGETS)}))
