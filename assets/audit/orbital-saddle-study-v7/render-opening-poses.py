"""Read-only neutral views of the proposed removable brow/crown opening."""
from pathlib import Path
import hashlib, json
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
NATIVE = ROOT / 'assets/models/uncaged-orbital-saddle-study-v7/murderbird-orbital-saddle-study-v7.blend'
SHA = 'e8169a3d685977f2f7dc62ab6f85d61fe456881aba06114d4169a31989de13d5'
assert hashlib.sha256(NATIVE.read_bytes()).hexdigest() == SHA
bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
sh = scene.display.shading
sh.light = 'STUDIO'; sh.studio_light = 'paint.sl'; sh.color_type = 'MATERIAL'
sh.show_shadows = True; sh.show_cavity = True; sh.cavity_type = 'BOTH'
sh.background_type = 'WORLD'; scene.world.color = (.11, .12, .13)
scene.render.resolution_x = scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.hide_render = 'builder' not in obj.get('exteriorEras', 'maker,mechanic,builder').split(',')
        obj.hide_set(False)
cd = bpy.data.cameras.new('Temporary opening camera')
cam = bpy.data.objects.new('Temporary opening camera', cd)
scene.collection.objects.link(cam); scene.camera = cam
cam.location = (-6, -3, 2.4)
cam.rotation_euler = (Vector((0, -.29, 1.78)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cd.type = 'ORTHO'; cd.ortho_scale = .88
cover = bpy.data.objects['cranial-cover']
rest = cover.location.copy()
records = []
for fraction in (0, .125, .5, 1):
    cover.location = rest.copy(); cover.location.z += fraction * .08
    bpy.context.view_layer.update()
    path = OUT / f'opening-{round(fraction*1000):04d}.png'
    assert not path.exists()
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    records.append({'openFraction': fraction, 'nativeLocalZLiftM': fraction * .08,
                    'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
assert hashlib.sha256(NATIVE.read_bytes()).hexdigest() == SHA
(OUT / 'opening-render-receipt.json').write_text(json.dumps({
    'nativeSha256': SHA, 'views': records, 'camera': {'position': [-6,-3,2.4], 'target': [0,-.29,1.78], 'ortho': .88},
    'method': 'Native replay of documented cover lift; all other pivots held at native rest; separation zero',
    'limits': ['Authoring renders only, not browser captures or continuous clearance proof.', 'Native source not saved or changed.']
}, indent=2) + '\n')
