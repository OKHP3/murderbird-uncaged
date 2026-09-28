"""Render a small, isolated angle study of the frozen v6 authored head."""
from pathlib import Path
import bpy
import hashlib
import json
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/audit/alignment-v6/head-angle-study"
SOURCE = ROOT / "assets/models/uncaged-alignment-v6/murderbird-alignment-v6.blend"
MODEL = ROOT / "assets/audit/alignment-v6/rig-ce35024adda8/model-inputs/v6-sixth.glb"
REFERENCE = ROOT / "context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png"
EXPECTED = {
    "source": "5a7a51941423dd0efcb48b9641b7a49597dad117e218ccb4e94f26315c5e9ded",
    "model": "ce35024adda89681a0f37e7018e2563a74af67cd06558a887222df87b78a87fe",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_sha(path, expected):
    actual = sha(path)
    if actual != expected:
        raise RuntimeError(f"SHA-256 mismatch for {path}: expected {expected}, got {actual}")
    return actual


OUT.mkdir(parents=True, exist_ok=True)
if any(OUT.iterdir()):
    raise RuntimeError(f"Refusing to overwrite nonempty study directory: {OUT}")

source_sha = require_sha(SOURCE, EXPECTED["source"])
model_sha = require_sha(MODEL, EXPECTED["model"])
reference_sha = sha(REFERENCE)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
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
        eras = obj.get("exteriorEras", "maker,mechanic,builder").split(",")
        obj.hide_render = "builder" not in eras
        obj.hide_set(False)

camera_data = bpy.data.cameras.new("Head angle study camera")
camera = bpy.data.objects.new("Head angle study camera", camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
target = (0.0, -0.29, 1.78)
views = [
    {"name": "side-biased-three-quarter-a", "position": (-6.0, -3.0, 2.4), "orthoScale": 0.80},
    {"name": "side-biased-three-quarter-b", "position": (-6.0, -4.2, 2.1), "orthoScale": 0.80},
    {"name": "near-profile-three-quarter", "position": (-6.0, -1.8, 2.2), "orthoScale": 0.80},
]
records = []
for view in views:
    camera.location = view["position"]
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = view["orthoScale"]
    scene.render.filepath = str(OUT / f"{view['name']}.png")
    bpy.ops.render.render(write_still=True)
    camera_payload = {
        "position": view["position"],
        "target": target,
        "projection": "ORTHO",
        "orthoScale": view["orthoScale"],
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
    }
    camera_json = json.dumps(camera_payload, sort_keys=True, separators=(",", ":"))
    image = OUT / f"{view['name']}.png"
    records.append({
        "image": image.name,
        "imageSha256": sha(image),
        "bytes": image.stat().st_size,
        "camera": camera_payload,
        "cameraSha256": hashlib.sha256(camera_json.encode()).hexdigest(),
        "viewLabel": "approximate side-biased three-quarter; illustration is not exact camera metrology",
    })

manifest = {
    "title": "Frozen v6 head angle study",
    "status": "neutral authoring renders for viewpoint comparison; not runtime or art approval",
    "sourceBlend": {"path": str(SOURCE.relative_to(ROOT)), "sha256": source_sha},
    "sourceGlb": {"path": str(MODEL.relative_to(ROOT)), "sha256": model_sha},
    "reference": {"path": str(REFERENCE.relative_to(ROOT)), "sha256": reference_sha, "scope": "July reference: head only"},
    "renderer": {"engine": "BLENDER_WORKBENCH", "light": "STUDIO/paint.sl", "color": "MATERIAL", "eraVisibility": "builder eligible meshes", "textures": "not used"},
    "views": records,
    "limits": [
        "These camera angles approximate the illustrated view; they are not calibrated metrology.",
        "The renders show authored neutral geometry and do not establish runtime shader, animation, or final artistic acceptance.",
    ],
}
(OUT / "head-angle-study.json").write_text(json.dumps(manifest, indent=2) + "\n")
if sha(SOURCE) != source_sha or sha(MODEL) != model_sha:
    raise RuntimeError("A frozen source changed during the render study")
print(json.dumps({"study": str(OUT), "views": len(records), "sourceSha256": source_sha, "modelSha256": model_sha}))
