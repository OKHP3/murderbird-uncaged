from pathlib import Path
import bpy, hashlib, json, runpy, shutil
from mathutils import Vector
ROOT = Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
BASE = ROOT / 'assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend'
BASE_SHA = 'd2c704ccf89f3f0e7dbeb3613dcdbdd964c4ba69991783783830803eecf59cb0'
MODULE = ROOT / 'scripts/regions/whole-character-v36-compact-feet.py'
EXPECTED_MODULE_SHA = 'cade48a05ff44f84506ae610497ab2d4cac96bf3a080453c18be480c4bef3393'
OUT = ROOT / 'assets/models/whole-character-v36/regional-studies/compact-feet/attempt02/murderbird-whole-character-v36-compact-feet.blend'
AUDIT = ROOT / 'assets/audit/whole-character-v36/regional-studies/compact-feet/attempt02'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(BASE) == BASE_SHA
assert sha(MODULE) == EXPECTED_MODULE_SHA
assert not OUT.exists()
shutil.copyfile(MODULE, AUDIT / 'executed-whole-character-v36-compact-feet.py')

scene = bpy.context.scene
scene.frame_set(1)
for obj in bpy.data.objects:
    if obj.animation_data:
        obj.animation_data_clear()
    if obj.get('authoringGuide'):
        obj.hide_render = True
    elif obj.type == 'MESH':
        obj.hide_render = 'builder' not in obj.get('exteriorEras', 'maker,mechanic,builder').split(',')
scene.render.engine = 'BLENDER_WORKBENCH'
shade = scene.display.shading
shade.light = 'STUDIO'; shade.studio_light = 'paint.sl'; shade.color_type = 'SINGLE'
shade.single_color = (.56, .58, .60); shade.show_shadows = False
shade.show_cavity = True; shade.cavity_type = 'BOTH'
shade.background_type = 'WORLD'; scene.world.color = (.12, .13, .14)
scene.render.resolution_x = scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
cam_data = bpy.data.cameras.new('V36 temporary matched neutral review camera')
cam_data.type = 'ORTHO'
camera = bpy.data.objects.new(cam_data.name, cam_data)
scene.collection.objects.link(camera)
scene.camera = camera
views = [
    ('reference-angle', (-6, -3.5, 2.75), (0, -.08, 1.02), 2.5),
    ('front', (0, -7, 1.65), (0, -.08, 1.02), 2.5),
    ('side', (-7, 0, 1.35), (0, -.08, 1.02), 2.5),
    ('feet-close-reference', (-1.35, -2.6, .85), (0, -.24, .15), 1.05),
    ('feet-close-side', (-2.2, 0, .80), (0, -.24, .15), 1.05),
]
render_receipts = []
def render(name, pos, target, scale, stage):
    camera.location = pos
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    cam_data.ortho_scale = scale
    scene.render.filepath = str(AUDIT / f'{stage}-{name}.png')
    bpy.ops.render.render(write_still=True)
    path = Path(scene.render.filepath)
    render_receipts.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'bytes': path.stat().st_size,
                            'camera': {'position': pos, 'target': target, 'orthoScale': scale},
                            'stage': stage, 'lighting': 'neutral V35 Workbench, no cast shadows'})

for name, pos, target, scale in views:
    render(name, pos, target, scale, 'before')
module = runpy.run_path(str(AUDIT / 'executed-whole-character-v36-compact-feet.py'))
result = module['apply']()
for name, pos, target, scale in views:
    render(name, pos, target, scale, 'after')
scene.objects.unlink if False else None
bpy.data.objects.remove(camera, do_unlink=True)
bpy.data.cameras.remove(cam_data)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), check_existing=False)
assert sha(BASE) == BASE_SHA
receipt = {
    'status': 'regional rest-shape study; owner acceptance pending',
    'sourceNative': {'path': str(BASE.relative_to(ROOT)), 'sha256': sha(BASE)},
    'regionalNative': {'path': str(OUT.relative_to(ROOT)), 'sha256': sha(OUT), 'bytes': OUT.stat().st_size},
    'sourceModule': {'path': str(MODULE.relative_to(ROOT)), 'sha256': sha(MODULE)},
    'executedModule': {'path': str((AUDIT / 'executed-whole-character-v36-compact-feet.py').relative_to(ROOT)),
                       'sha256': sha(AUDIT / 'executed-whole-character-v36-compact-feet.py')},
    'result': result,
    'views': render_receipts,
    'limits': result['scopeLimitations'] + [
        'Renders compare the exact V35 source and this regional candidate with the same neutral cameras; no runtime export was produced.',
        'The Maker leg-control default remains owner-local [0.065, 0.015, 0.045]; ankle receiver geometry and body mechanism layout are unchanged. Actual socket surface seating remains to be verified in composed runtime.',
    ],
}
(AUDIT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'native': receipt['regionalNative'], 'changedNodes': result['changedNodes'],
                  'changedFootMeshes': len(result['changedFootMeshes']), 'beforeAfterFootZ': result['numericInvariants']['lowestFootRegionZBeforeAfterM'],
                  'anklePivotsUnchanged': result['numericInvariants']['anklePivotsWorldMatricesUnchanged'],
                  'views': len(render_receipts)}))
