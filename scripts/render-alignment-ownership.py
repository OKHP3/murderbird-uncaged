"""Render actual rigid ownership without editing or saving the native model."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import bpy
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--head-pitch', type=float, default=0)
parser.add_argument('--head-yaw', type=float, default=0)
parser.add_argument('--jaw-open', type=float, default=0)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
source = ROOT / args.source
out = ROOT / args.output
out.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
scene.frame_set(1)
# Match Three's XYZ head pitch/yaw order after Y-up -> Z-up conversion.
# Compose matrices explicitly; Blender's default Euler order is different.
head = bpy.data.objects['head']
head.animation_data_clear()
head.rotation_mode = 'QUATERNION'
head.rotation_quaternion = (Matrix.Rotation(args.head_pitch, 4, 'X') @
                            Matrix.Rotation(args.head_yaw, 4, 'Z')).to_quaternion()
bpy.data.objects['jaw'].rotation_euler.x = args.jaw_open
bpy.context.view_layer.update()
scene.render.engine = 'BLENDER_WORKBENCH'
sh = scene.display.shading
sh.light = 'STUDIO'
sh.studio_light = 'paint.sl'
sh.color_type = 'OBJECT'
sh.show_shadows = True
sh.show_cavity = True
sh.background_type = 'WORLD'
scene.world.color = (.1, .11, .12)
palette = {'jaw': (.9, .07, .06, 1), 'head': (.95, .56, .04, 1),
           'neck': (.02, .65, .8, 1), 'other': (.32, .34, .36, 1)}
owners = {}
for obj in scene.objects:
    if obj.type != 'MESH':
        continue
    obj.hide_set(False)
    obj.hide_render = 'builder' not in obj.get('exteriorEras', 'maker,mechanic,builder').split(',')
    owner = obj.parent
    while owner and owner.name not in palette:
        owner = owner.parent
    key = owner.name if owner else 'other'
    obj.color = palette[key]
    owners[obj.name] = key
scene.render.resolution_x = 1100
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
camdata = bpy.data.cameras.new('Ownership diagnostic camera')
cam = bpy.data.objects.new('Ownership diagnostic camera', camdata)
scene.collection.objects.link(cam)
scene.camera = cam
camdata.type = 'ORTHO'
camdata.ortho_scale = .95
records = []
for name, position in [('side', (-6, -.25, 1.65)), ('three-quarter', (-4, -6, 2.01))]:
    target = Vector((0, -.29, 1.65))
    cam.location = position
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    image = out / ('ownership-' + name + '.png')
    assert not image.exists(), 'Preserve prior diagnostic instead of overwriting it'
    scene.render.filepath = str(image)
    bpy.ops.render.render(write_still=True)
    records.append({'path': str(image.relative_to(ROOT)), 'sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
                    'camera': list(position), 'target': list(target), 'orthoScale': .95})
with (out / 'ownership-views.json').open('x') as stream:
    json.dump({'source': str(source.relative_to(ROOT)), 'sourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
               'rendererSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'stressPose': {'headPitch': args.head_pitch, 'headYaw': args.head_yaw, 'jawOpen': args.jaw_open,
                              'scope': 'Direct independent joint sample, not asserted simultaneous runtime pose'},
               'legend': palette, 'rigidOwners': owners, 'views': records,
               'scope': 'Diagnostic object colors only; actual rigid parents, no native save, no surface or motion acceptance'}, stream, indent=2)
    stream.write('\n')
