"""Render bounded in-memory surface variants against frozen iteration-08 native.

No source .blend, geometry, node graph, or production material module is saved or
modified. Each variant copies the packed images, adds only fine detail to those
copies, then remaps existing image-texture nodes by their original image names.
"""
from pathlib import Path
import hashlib
import json
import math
import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
ITERATION = "iteration-08"
SOURCE = ROOT / "assets/models/uncaged-appearance-v1/iterations" / ITERATION / "murderbird-appearance.blend"
OUT = ROOT / "assets/audit/appearance-v1" / ITERATION / "material-study"
EXPECTED_SHA256 = "ea6c9a235106810e8056401467a13863fdbb0a215589375321101d5894b53c33"

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

actual_sha = sha256(SOURCE)
if actual_sha != EXPECTED_SHA256:
    raise RuntimeError(f"Frozen iteration-08 source SHA mismatch: {actual_sha}")
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene

# Match scripts/render-appearance-v1.py camera, key/fill/rim lighting,
# environment, view transform, and ground. Keep this study quick but consistent.
for obj in list(scene.objects):
    if obj.type in {"CAMERA", "LIGHT"}:
        bpy.data.objects.remove(obj, do_unlink=True)
scene.render.engine = "CYCLES"
scene.cycles.samples = 8
scene.cycles.use_denoising = True
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for device in prefs.devices:
        device.use = device.type == "METAL"
    scene.cycles.device = "GPU" if any(device.use for device in prefs.devices) else "CPU"
except Exception:
    scene.cycles.device = "CPU"
scene.render.resolution_x = 880
scene.render.resolution_y = 880
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.world.use_nodes = True
scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value = (.18, .20, .23, 1)
scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value = .35
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = .2
camdata = bpy.data.cameras.new("Surface study camera")
cam = bpy.data.objects.new("Surface study camera", camdata)
scene.collection.objects.link(cam)
scene.camera = cam

def area(name, pos, power, size, color):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = power
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = pos
    obj.rotation_euler = (Vector((0, 0, 1.1)) - obj.location).to_track_quat("-Z", "Y").to_euler()

area("Broad key", (-3, -4.5, 5), 700, 4, (1, .91, .78))
area("Cool fill", (3, -1, 3.3), 500, 3, (.70, .84, 1))
area("Back edge", (.6, 3, 3.5), 850, 2, (1, .78, .46))
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.018))
floor = bpy.context.object
floor.name = "Review floor"
floor["reviewOnly"] = True
floor_mat = bpy.data.materials.new("Review floor")
floor_mat.diffuse_color = (.12, .135, .14, 1)
floor_mat.use_nodes = True
floor_bsdf = floor_mat.node_tree.nodes.get("Principled BSDF")
floor_bsdf.inputs["Base Color"].default_value = (.12, .135, .14, 1)
floor_bsdf.inputs["Roughness"].default_value = .8
floor.data.materials.append(floor_mat)

def select_era(value):
    for obj in scene.objects:
        if obj.type == "MESH" and not obj.get("reviewOnly"):
            obj.hide_set(False)
            obj.hide_render = value not in obj.get("exteriorEras", "maker,mechanic,builder").split(",")

views = {
    "advanced-head": ((-3.8, -6, 2.0), (0, -.30, 1.72), .77, "builder"),
    "advanced-three-quarter": ((-4.7, -6.5, 2.30), (0, -.1, 1.0), 2.23, "builder"),
    "maker-three-quarter": ((-4.7, -6.5, 2.30), (0, -.1, 1.0), 2.23, "maker"),
}

def _lines_mask(rng, size, count, min_length, max_length, min_width, max_width):
    mask = np.zeros((size, size), dtype=np.float32)
    # Rasterize each short score only inside its local bounding box.
    for _ in range(count):
        cx, cy = rng.uniform(0, size, size=2)
        angle = rng.uniform(0, math.tau)
        length = rng.uniform(min_length, max_length)
        width = rng.uniform(min_width, max_width)
        dx, dy = math.cos(angle), math.sin(angle)
        pad = width * 3 + 1
        x0 = max(0, int(cx - abs(dx) * length / 2 - abs(dy) * pad) - 1)
        x1 = min(size, int(cx + abs(dx) * length / 2 + abs(dy) * pad) + 2)
        y0 = max(0, int(cy - abs(dy) * length / 2 - abs(dx) * pad) - 1)
        y1 = min(size, int(cy + abs(dy) * length / 2 + abs(dx) * pad) + 2)
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        along = (xx-cx)*dx + (yy-cy)*dy
        across = -(xx-cx)*dy + (yy-cy)*dx
        stroke = np.exp(-.5*(across/width)**2) * (np.abs(along) <= length/2)
        mask[y0:y1, x0:x1] = np.maximum(mask[y0:y1, x0:x1], stroke.astype(np.float32))
    return mask

def _pit_mask(rng, size, count, max_strength):
    mask = np.zeros((size, size), dtype=np.float32)
    for _ in range(count):
        cx, cy = rng.uniform(0, size, size=2)
        radius = rng.uniform(.55, 1.35)
        x0, x1 = max(0, int(cx-radius*3)-1), min(size, int(cx+radius*3)+2)
        y0, y1 = max(0, int(cy-radius*3)-1), min(size, int(cy+radius*3)+2)
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        pit = np.exp(-((xx-cx)**2+(yy-cy)**2)/(2*radius*radius))*max_strength
        mask[y0:y1, x0:x1] = np.maximum(mask[y0:y1, x0:x1], pit.astype(np.float32))
    return mask

VARIANTS = {
    "modest": {"scratchCount": 7, "scratchMix": .24, "pitCount": 12,
               "pitDarken": .09, "baseMicro": .022, "rmMicro": .018,
               "normalScale": 1.45, "chasing": .009},
    "strong": {"scratchCount": 13, "scratchMix": .39, "pitCount": 24,
               "pitDarken": .16, "baseMicro": .038, "rmMicro": .032,
               "normalScale": 1.9, "chasing": .018},
}

original_images = {}
for material in bpy.data.materials:
    if not material.use_nodes:
        continue
    for node in material.node_tree.nodes:
        if node.type == "TEX_IMAGE" and node.image and node.image.name.startswith("appearance-"):
            original_images[node.image.name] = node.image
if not original_images:
    raise RuntimeError("No appearance material images found in iteration-08 native")

# Restore original node assignments by the literal source image datablock names.
def remap_images(replacements):
    for material in bpy.data.materials:
        if not material.use_nodes:
            continue
        for node in material.node_tree.nodes:
            if node.type == "TEX_IMAGE" and node.image:
                original_name = node.image.get("studyOriginalImage", node.image.name)
                if original_name in replacements:
                    node.image = replacements[original_name]

def make_variant(variant, parameters):
    replacements = {}
    for original_name, original in original_images.items():
        image = original.copy()
        image.name = f"study-{variant}__{original_name}"
        image["studyOriginalImage"] = original_name
        width, height = image.size
        if width != height or width != 1024:
            replacements[original_name] = image
            continue
        arr = np.asarray(image.pixels[:], dtype=np.float32).reshape((height, width, 4)).copy()
        seed = int.from_bytes(hashlib.sha256((variant+":"+original_name).encode()).digest()[:4], "little")
        rng = np.random.default_rng(seed)
        is_color = "base-color" in original_name
        is_rm = "roughness-metallic" in original_name
        is_normal = "normal" in original_name
        hero = "head-hero" in original_name
        cells = [(0, 0, 1024)] if hero else [(x*256, y*256, 256) for y in range(4) for x in range(4)]
        for x0, y0, cell in cells:
            sub = arr[y0:y0+cell, x0:x0+cell, :]
            # The atlas optic/recess cells stay optically dark and clean.
            cell_index = (y0//256)*4 + x0//256 if not hero else -1
            if is_color:
                if cell_index in {6, 7}:
                    continue
                scratch = _lines_mask(rng, cell, parameters["scratchCount"], 9, 30, .45, .95)
                pits = _pit_mask(rng, cell, parameters["pitCount"], parameters["pitDarken"])
                yy, xx = np.mgrid[0:cell, 0:cell].astype(np.float32)
                angle = rng.uniform(0, math.tau)
                frequency = rng.uniform(19, 34) * math.tau / cell
                chase = np.sin((xx*math.cos(angle)+yy*math.sin(angle))*frequency+rng.uniform(0,math.tau))
                noise = rng.standard_normal((cell, cell), dtype=np.float32)
                micro = np.clip(chase*.45+noise*.55,-1,1)*parameters["baseMicro"]
                rgb = sub[..., :3]
                rgb *= np.maximum(.86, 1+micro[...,None])
                # Brighten/warm hairline cuts relative to each local alloy color.
                alloy = np.stack((np.minimum(.65, rgb[...,0]*1.65+.035),
                                  np.minimum(.48, rgb[...,1]*1.42+.018),
                                  np.minimum(.28, rgb[...,2]*1.08+.006)), axis=-1)
                rgb[:] = rgb*(1-scratch[...,None]*parameters["scratchMix"]) + alloy*(scratch[...,None]*parameters["scratchMix"])
                rgb *= (1-pits[...,None])
            elif is_rm:
                yy, xx = np.mgrid[0:cell, 0:cell].astype(np.float32)
                angle = rng.uniform(0, math.tau)
                frequency = rng.uniform(19, 34) * math.tau / cell
                chase = np.sin((xx*math.cos(angle)+yy*math.sin(angle))*frequency+rng.uniform(0,math.tau))
                noise = rng.standard_normal((cell, cell), dtype=np.float32)
                variation = np.clip(chase*.55+noise*.45,-1,1)*parameters["rmMicro"]
                sub[...,1] = np.clip(sub[...,1]+variation, .05, .95)
                sub[...,2] = np.clip(sub[...,2]+variation*.42, .04, .98)
                if cell_index not in {6,7}:
                    scratch = _lines_mask(rng, cell, parameters["scratchCount"], 9, 30, .45, .95)
                    pits = _pit_mask(rng, cell, parameters["pitCount"], 1)
                    sub[...,1] = np.clip(sub[...,1] - scratch*.055 + pits*.035, .05, .95)
                    sub[...,2] = np.clip(sub[...,2] + scratch*.06 - pits*.035, .04, .98)
            elif is_normal:
                # Preserve the authored tangent direction while lifting fine relief.
                sub[...,:2] = np.clip(.5+(sub[...,:2]-.5)*parameters["normalScale"],0,1)
                yy, xx = np.mgrid[0:cell, 0:cell].astype(np.float32)
                angle = rng.uniform(0, math.tau)
                frequency = rng.uniform(22, 37)*math.tau/cell
                phase = rng.uniform(0, math.tau)
                wave = np.sin((xx*math.cos(angle)+yy*math.sin(angle))*frequency+phase)
                sub[...,0] = np.clip(sub[...,0]+wave*parameters["chasing"],0,1)
                sub[...,1] = np.clip(sub[...,1]+np.roll(wave,1,axis=1)*parameters["chasing"],0,1)
        image.pixels.foreach_set(arr.reshape(-1))
        replacements[original_name] = image
    remap_images(replacements)
    return replacements

select_era("builder")
records = {"source": str(SOURCE.relative_to(ROOT)), "sourceSha256": actual_sha,
           "engine":"Cycles", "device":scene.cycles.device, "samples":scene.cycles.samples,
           "resolution":[scene.render.resolution_x,scene.render.resolution_y],
           "note":"Non-destructive material-only study. Fine overlays are proposals; no likeness or measured-finish claim.",
           "variants":{}}
for variant, params in VARIANTS.items():
    replacements = make_variant(variant, params)
    variant_records=[]
    for view, (pos,target,scale,era) in views.items():
        select_era(era)
        cam.location=pos
        cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
        camdata.type="ORTHO"
        camdata.ortho_scale=scale
        scene.render.filepath=str(OUT/f"{variant}-{view}.png")
        bpy.ops.render.render(write_still=True)
        path=Path(scene.render.filepath)
        variant_records.append({"path":str(path.relative_to(ROOT)),"sha256":sha256(path),"camera":list(pos),"target":list(target),"orthoScale":scale,"era":era})
    records["variants"][variant]={"parameters":params,"imageRemap":{k:v.name for k,v in replacements.items()},"views":variant_records}
    remap_images(original_images)

(OUT/"study.json").write_text(json.dumps(records,indent=2)+"\n")
print(json.dumps({"sourceSha256":actual_sha,"output":str(OUT.relative_to(ROOT)),"variants":{k:v["parameters"] for k,v in records["variants"].items()}},indent=2))
