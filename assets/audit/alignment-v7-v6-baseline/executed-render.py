"""Write-once neutral views of a hash-bound native candidate; no source edits."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--native', required=True)
parser.add_argument('--native-sha256', required=True)
parser.add_argument('--glb', required=True)
parser.add_argument('--glb-sha256', required=True)
parser.add_argument('--out', required=True)
parser.add_argument('--comparison-only', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


native = (ROOT / args.native).resolve()
glb = (ROOT / args.glb).resolve()
out = (ROOT / args.out).resolve()
assert digest(native) == args.native_sha256, 'Native source hash changed'
assert digest(glb) == args.glb_sha256, 'GLB hash changed'
assert not out.exists(), 'Preserve previous render output before another run'
out.mkdir(parents=True)
shutil.copy2(Path(__file__), out / 'executed-render.py')

bpy.ops.wm.open_mainfile(filepath=str(native))
scene = bpy.context.scene
scene.frame_set(1)
scene.render.engine = 'BLENDER_WORKBENCH'
shading = scene.display.shading
shading.light = 'STUDIO'
shading.studio_light = 'paint.sl'
shading.color_type = 'MATERIAL'
shading.show_shadows = True
shading.show_cavity = True
shading.cavity_type = 'BOTH'
shading.curvature_ridge_factor = 1.2
shading.curvature_valley_factor = 1.1
shading.background_type = 'WORLD'
scene.world.color = (.11, .12, .13)
scene.render.resolution_x = scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
camera_data = bpy.data.cameras.new('V7 neutral review camera')
camera = bpy.data.objects.new('V7 neutral review camera', camera_data)
scene.collection.objects.link(camera)
scene.camera = camera

# Same fixed cameras are used for both source and candidate. These are authored
# comparison views, not an assertion that an illustration's camera is measured.
views = [
    ('three-quarter', (-4.7, -6.5, 2.30), (0, -.1, 1.08), 2.4),
    ('front', (0, -6, 1.08), (0, -.1, 1.08), 2.4),
    ('side-right', (-6, 0, 1.08), (0, -.1, 1.08), 2.4),
    ('rear', (0, 6, 1.08), (0, .05, 1.08), 2.4),
    ('feet', (-4, -6, .6), (0, -.1, .31), .98),
    ('feet-side', (-6, -.10, .32), (0, -.1, .31), .98),
    ('head', (-6, -3, 2.4), (0, -.29, 1.78), .8),
]
if not args.comparison_only:
    views += [
        ('neck', (-4, -6, 1.7), (0, -.2, 1.58), .8),
        ('breast', (-2, -6, 1.5), (0, -.14, 1.32), 1.15),
        ('left-shoulder', (4, -.5, 1.8), (.32, .08, 1.26), .95),
    ]
records = []
for era in (['builder'] if args.comparison_only else ['maker', 'mechanic', 'builder']):
    for obj in scene.objects:
        if obj.type == 'MESH':
            obj.hide_render = era not in obj.get('exteriorEras', 'maker,mechanic,builder').split(',')
            obj.hide_set(False)
    for name, position, target, scale in views:
        camera.location = position
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
        camera_data.type = 'ORTHO'
        camera_data.ortho_scale = scale
        filename = out / f'{era}-{name}.png'
        scene.render.filepath = str(filename)
        bpy.ops.render.render(write_still=True)
        records.append({'path': str(filename.relative_to(ROOT)), 'bytes': filename.stat().st_size,
                        'sha256': digest(filename), 'era': era, 'view': name,
                        'camera': list(position), 'target': list(target),
                        'projection': 'ORTHO', 'orthoScale': scale, 'resolution': [1100, 1100]})

assert digest(native) == args.native_sha256 and digest(glb) == args.glb_sha256
report = {
    'status': 'rendered neutral authoring views; visual review required',
    'native': {'path': str(native.relative_to(ROOT)), 'sha256': args.native_sha256},
    'runtimeDerivative': {'path': str(glb.relative_to(ROOT)), 'sha256': args.glb_sha256},
    'rendererSha256': digest(Path(__file__)), 'blenderVersion': bpy.app.version_string,
    'lighting': 'neutral Workbench paint.sl studio; material display colors, no textures',
    'views': records,
    'limits': ['Native authoring render, not browser/export appearance proof.',
               'Hidden or rear details are reconstruction proposals.',
               'Fixed rest pose; no moving clearance or owner acceptance established.'],
}
(out / 'authoring-views.json').write_text(json.dumps(report, indent=2) + '\n')
print('RENDERED', len(records), str(out.relative_to(ROOT)))
