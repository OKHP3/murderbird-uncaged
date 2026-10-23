"""Render a frozen appearance candidate as a real-geometry orbit sequence."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
CLI = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--iteration', required=True,
                    help='Exact appearance iteration directory name.')
parser.add_argument('--frames', type=int, default=96)
parser.add_argument('--samples', type=int, default=16)
parser.add_argument('--era', choices=('maker', 'mechanic', 'builder'),
                    default='builder')
args = parser.parse_args(CLI)

if args.frames < 1:
    parser.error('--frames must be at least 1')
if args.samples < 1:
    parser.error('--samples must be at least 1')
if Path(args.iteration).name != args.iteration or args.iteration in {'.', '..'}:
    parser.error('--iteration must be one exact directory name')

source = (ROOT / 'assets/models/uncaged-appearance-v1/iterations' /
          args.iteration / 'murderbird-appearance.blend')
if not source.is_file():
    parser.error(f'iteration source does not exist: {source}')

OUT = ROOT / 'assets/audit/appearance-v1' / args.iteration / f'turntable-{args.era}'
OUT.mkdir(parents=True, exist_ok=True)
existing_frames = sorted(OUT.glob('frame-*.png'))
if existing_frames:
    raise SystemExit(
        f'Refusing to overwrite {len(existing_frames)} existing frame(s) in {OUT}'
    )
movie = OUT / f'turntable-{args.era}.mp4'
if movie.exists():
    raise SystemExit(f'Refusing to overwrite existing movie: {movie}')

bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
for obj in list(scene.objects):
    if obj.type in {'CAMERA', 'LIGHT'}:
        bpy.data.objects.remove(obj, do_unlink=True)

scene.render.engine = 'CYCLES'
scene.cycles.samples = args.samples
scene.cycles.use_denoising = True
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for device in prefs.devices:
        device.use = device.type == 'METAL'
    scene.cycles.device = 'GPU' if any(d.use for d in prefs.devices) else 'CPU'
except Exception:
    scene.cycles.device = 'CPU'

scene.render.resolution_x = 1080
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.world.use_nodes = True
world_background = scene.world.node_tree.nodes.get('Background')
world_background.inputs['Color'].default_value = (.18, .20, .23, 1)
world_background.inputs['Strength'].default_value = .35
scene.view_settings.view_transform = 'AgX'
scene.view_settings.exposure = .2

camera_data = bpy.data.cameras.new('Appearance turntable camera')
camera = bpy.data.objects.new('Appearance turntable camera', camera_data)
scene.collection.objects.link(camera)
scene.camera = camera


def area(name, position, power, size, color):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = power
    data.shape = 'DISK'
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    obj.rotation_euler = (
        Vector((0, -.1, 1.05)) - obj.location
    ).to_track_quat('-Z', 'Y').to_euler()
    return obj


area('Broad key', (-3, -4.5, 5), 700, 4, (1, .91, .78))
area('Cool fill', (3, -1, 3.3), 500, 3, (.70, .84, 1))
area('Back edge', (.6, 3, 3.5), 850, 2, (1, .78, .46))

bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.018))
floor = bpy.context.object
floor.name = 'Review floor'
floor['reviewOnly'] = True
floor_material = bpy.data.materials.new('Review floor')
floor_material.diffuse_color = (.12, .135, .14, 1)
floor_material.use_nodes = True
floor_bsdf = floor_material.node_tree.nodes.get('Principled BSDF')
floor_bsdf.inputs['Base Color'].default_value = (.12, .135, .14, 1)
floor_bsdf.inputs['Roughness'].default_value = .8
floor.data.materials.append(floor_material)

# The source remains at its authored frame throughout the orbit. Era filtering
# affects only tagged exterior meshes, leaving shared rig and internals intact.
for obj in scene.objects:
    if obj.type == 'MESH' and not obj.get('reviewOnly'):
        visible = args.era in obj.get(
            'exteriorEras', 'maker,mechanic,builder'
        ).split(',')
        obj.hide_set(not visible)
        obj.hide_render = not visible

target = Vector((0, -.1, 1.05))
radius = 4.8
camera_height = 2.1
camera_data.type = 'ORTHO'
camera_data.ortho_scale = 2.3
records = []
model_hash = hashlib.sha256(source.read_bytes()).hexdigest()
for frame in range(args.frames):
    theta = math.tau * frame / args.frames
    camera.location = (
        radius * math.sin(theta),
        -.1 - radius * math.cos(theta),
        camera_height,
    )
    camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
    filename = f'frame-{frame:04d}.png'
    destination = OUT / filename
    scene.render.filepath = str(destination)
    bpy.ops.render.render(write_still=True)
    records.append({
        'file': filename,
        'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
        'cameraLocation': list(camera.location),
        'target': list(target),
        'orthographicScale': camera_data.ortho_scale,
    })

ffmpeg = shutil.which('ffmpeg')
movie_status = 'ffmpeg unavailable; PNG sequence retained'
if ffmpeg:
    command = [
        ffmpeg, '-hide_banner', '-loglevel', 'error', '-n',
        '-framerate', '24', '-start_number', '0',
        '-i', str(OUT / 'frame-%04d.png'), '-frames:v', str(args.frames),
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
        str(movie),
    ]
    subprocess.run(command, check=True)
    movie_status = 'encoded at 24 fps with installed ffmpeg'

metadata = {
    'status': 'frozen real-geometry turntable render; artistic acceptance remains open',
    'iteration': args.iteration,
    'source': str(source.relative_to(ROOT)),
    'modelSha256': model_hash,
    'era': args.era,
    'frameCount': args.frames,
    'samples': args.samples,
    'resolution': [1080, 1080],
    'engine': 'Cycles',
    'device': scene.cycles.device,
    'camera': {
        'type': 'orthographic',
        'orbitCenter': list(target),
        'radius': radius,
        'height': camera_height,
        'scale': camera_data.ortho_scale,
        'orbitDegrees': 360,
        'objectFrameHeld': scene.frame_current,
    },
    'movie': movie_status,
    'frames': records,
}
(OUT / 'turntable-metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
print(f'TURNTABLE_SAVED {OUT} frames={args.frames} era={args.era} {movie_status}')
