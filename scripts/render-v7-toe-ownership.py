"""Render temporary V7 foot ownership colors without saving the source scene."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/models/uncaged-alignment-v7/murderbird-alignment-v7.blend"
EXPECTED_SOURCE_SHA = "a8fccaf024a096678415215029b34cae8270b348da2301b8872a34e72c75ed3f"
OUT = ROOT / "assets/audit/alignment-v7/toe-ownership"
THREE_QUARTER = (-4.0, -6.0, 0.6)
SIDE = (-6.0, -0.1, 0.32)
TARGET = (0.0, -0.1, 0.31)
ORTHO_SCALE = 0.98
PALETTE = {
    "digit-inner-link-frame": (0.02, 0.88, 0.24, 1.0),
    "toe-hinge-bearing": (0.06, 0.32, 1.0, 1.0),
    "tapered-claw-sheath": (1.0, 0.34, 0.02, 1.0),
    "curved-instep-guard": (0.72, 0.05, 0.92, 1.0),
    "other": (0.48, 0.50, 0.52, 1.0),
}
TALONS = {f"{side} digit {digit} tapered claw sheath"
          for side in ("left", "right") for digit in (1, 2, 3)}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


require(SOURCE.is_file(), f"Missing pinned V7 native: {SOURCE}")
require(sha256(SOURCE) == EXPECTED_SOURCE_SHA, "V7 native SHA differs from requested diagnostic identity")
require(not OUT.exists(), f"Preserve existing ownership diagnostic instead of overwriting it: {OUT}")
OUT.mkdir(parents=True, exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene
scene.frame_set(1)
bpy.context.view_layer.update()

colored = {key: [] for key in PALETTE}
all_objects = {}
for obj in scene.objects:
    if obj.type != "MESH":
        continue
    obj.hide_set(False)
    obj.hide_render = False
    parent = obj.parent.name if obj.parent else None
    if obj.name.startswith("Digit inner link") and parent and "-digit-" in parent:
        key = "digit-inner-link-frame"
    elif obj.name.startswith("Toe hinge") and obj.get("surfaceRole") == "bearing":
        key = "toe-hinge-bearing"
    elif obj.name in TALONS:
        key = "tapered-claw-sheath"
    elif obj.name in {"left curved instep guard", "right curved instep guard"}:
        key = "curved-instep-guard"
    else:
        key = "other"
    obj.color = PALETTE[key]
    record = {"name": obj.name, "parent": parent, "region": obj.get("region"),
              "surfaceRole": obj.get("surfaceRole"), "colorKey": key}
    all_objects[obj.name] = record
    if key != "other":
        colored[key].append({"name": obj.name, "parent": parent})

require(len(colored["digit-inner-link-frame"]) == 12, "Expected 12 digit inner-link frame objects")
require(len(colored["toe-hinge-bearing"]) == 12, "Expected 12 toe hinge bearing objects")
require({item["name"] for item in colored["tapered-claw-sheath"]} == TALONS,
        "Six claw sheath objects do not match the exact V7 names")
require(len(colored["curved-instep-guard"]) == 2, "Expected two curved instep guards")

scene.render.engine = "BLENDER_WORKBENCH"
shading = scene.display.shading
shading.light = "STUDIO"
shading.studio_light = "paint.sl"
shading.color_type = "OBJECT"
shading.show_shadows = True
shading.show_cavity = True
shading.cavity_type = "BOTH"
shading.curvature_ridge_factor = 1.15
shading.curvature_valley_factor = 1.1
shading.background_type = "WORLD"
scene.world.color = (0.12, 0.13, 0.14)
scene.render.resolution_x = 1400
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False

camera_data = bpy.data.cameras.new("Temporary toe ownership camera")
camera = bpy.data.objects.new("Temporary toe ownership camera", camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
camera_data.type = "ORTHO"
camera_data.ortho_scale = ORTHO_SCALE

images = []
for view_name, position in (("feet-three-quarter", THREE_QUARTER), ("feet-side", SIDE)):
    camera.location = position
    camera.rotation_euler = (Vector(TARGET) - camera.location).to_track_quat("-Z", "Y").to_euler()
    image_path = OUT / f"{view_name}.png"
    require(not image_path.exists(), f"Refusing to overwrite diagnostic image: {image_path}")
    scene.render.filepath = str(image_path)
    bpy.ops.render.render(write_still=True)
    images.append({"path": str(image_path.relative_to(ROOT)), "bytes": image_path.stat().st_size,
                   "sha256": sha256(image_path), "camera": list(position), "target": list(TARGET),
                   "projection": "orthographic", "orthoScale": ORTHO_SCALE})

require(sha256(SOURCE) == EXPECTED_SOURCE_SHA, "Pinned V7 native changed during the render")
receipt = {
    "capturedAtUtc": datetime.now(timezone.utc).isoformat(),
    "source": {"path": str(SOURCE.relative_to(ROOT)), "sha256": EXPECTED_SOURCE_SHA,
               "bytes": SOURCE.stat().st_size},
    "renderer": {"path": str(Path(__file__).resolve().relative_to(ROOT)), "sha256": sha256(Path(__file__).resolve())},
    "blenderVersion": bpy.app.version_string,
    "temporaryColors": PALETTE,
    "coloredObjects": colored,
    "renderedViews": images,
    "scope": "Unsaved render-only ownership colors on exact V7 native. Colors reveal object ownership; no geometry, material, GLB, or saved native was changed.",
}
with (OUT / "ownership-receipt.json").open("x") as stream:
    json.dump(receipt, stream, indent=2)
    stream.write("\n")
print("V7_TOE_OWNERSHIP_RENDERED", json.dumps({"sourceSha256": EXPECTED_SOURCE_SHA, "images": images}, sort_keys=True))
