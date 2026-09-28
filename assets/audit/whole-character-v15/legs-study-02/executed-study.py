"""Create and render one editable passive-leg construction study."""
from pathlib import Path
import datetime
import hashlib
import json
import runpy
import shutil

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'assets/models/uncaged-orbital-crown-v14/attempt-11/murderbird-orbital-crown-v14.blend'
BASE_SHA = '93cf7908906dab0746ec42ace88867b3c52cb0988c284cf6ae468eb2cce17a5a'
MODULE = ROOT / 'scripts/regions/whole-character-v15-legs.py'
OWNER_REFERENCE = ROOT / 'context/threads/assets/murderbird-owner-likeness-rejection-2026-09-28/2-Pasted-Image-2.jpg'
CURRENT_VIEW = ROOT / 'assets/audit/uncaged-orbital-crown-v14/attempt-11/after-reference-angle.png'
OUT_MODEL = ROOT / 'assets/models/whole-character-v15/legs-study-02'
OUT_AUDIT = ROOT / 'assets/audit/whole-character-v15/legs-study-02'
NATIVE = OUT_MODEL / 'murderbird-v15-legs-study-02.blend'
RECEIPT = OUT_AUDIT / 'receipt.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def art(path):
    return {'path': Path(path).resolve().relative_to(ROOT).as_posix(),
            'sha256': sha(path), 'bytes': Path(path).stat().st_size}


assert sha(BASE) == BASE_SHA, 'Pinned V14 attempt-11 native changed'
assert Path(bpy.data.filepath).resolve() == BASE.resolve(), 'Blender must open the pinned V14 native'
assert not NATIVE.exists() and not RECEIPT.exists(), 'Refusing to overwrite a prior legs study'
assert OWNER_REFERENCE.is_file() and CURRENT_VIEW.is_file()
assert sha(MODULE)

helper_path = ROOT / 'scripts/build-uncaged-alignment-v7.py'
assert sha(helper_path) == '39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'
helpers = runpy.run_path(str(helper_path), run_name='whole_character_v15_leg_snapshot_helpers')
before = helpers['scene_snapshot']()
before_materials = {material.name: helpers['material_signature'](material) for material in bpy.data.materials}
before_toe_hinges = sorted(obj.name for obj in bpy.data.objects
                           if obj.type == 'MESH' and obj.name.startswith('Toe hinge'))
assert len(before['empties']) == 52 and len(before_toe_hinges) == 12

module_api = runpy.run_path(str(MODULE), run_name='whole_character_v15_leg_region')
proposal = module_api['apply']()
bpy.context.view_layer.update()
after = helpers['scene_snapshot']()
assert before['empties'] == after['empties'], 'Pivots or parent transforms changed'
assert before['curves'] == after['curves'], 'Historical curves changed'
assert len(after['meshes']) == len(before['meshes']) - len(proposal['replacedObjects']) + len(proposal['changedOrAddedObjects'])
for name, record in before['meshes'].items():
    if name not in proposal['replacedObjects']:
        assert after['meshes'][name] == record, f'Inherited mesh changed: {name}'
after_materials = {material.name: helpers['material_signature'](material) for material in bpy.data.materials}
assert before_materials == after_materials, 'Material values or assignments changed'

new_objects = [bpy.data.objects[name] for name in proposal['changedOrAddedObjects']]
new_owner_names = {owner: sum(obj.parent.name == owner for obj in new_objects)
                   for owner in sorted({obj.parent.name for obj in new_objects})}
assert len(new_objects) == 18
assert all(obj.type == 'MESH' and obj.parent and obj.parent.name == obj['constructionOwner'] for obj in new_objects)
assert all(obj.get('exteriorEras') == 'maker,mechanic,builder' for obj in new_objects)
assert {obj.parent.name for obj in new_objects if 'open passive truss' in obj.name} == {
    'left-thigh', 'left-shin', 'left-foot', 'right-thigh', 'right-shin', 'right-foot'
}
assert len([obj for obj in new_objects if 'captive toe-bearing flanges' in obj.name]) == 12

OUT_MODEL.mkdir(parents=True, exist_ok=True)
OUT_AUDIT.mkdir(parents=True, exist_ok=True)
shutil.copy2(MODULE, OUT_AUDIT / 'executed-legs-module.py')
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE), check_existing=False)

# Reopen and confirm the additive candidate is exact before rendering.
bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
assert helpers['scene_snapshot']() == after, 'Saved/reopened study differs from in-memory candidate'
assert sha(BASE) == BASE_SHA


def configure_and_render(source_path, label):
    bpy.ops.wm.open_mainfile(filepath=str(source_path))
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    shading = scene.display.shading
    shading.light = 'STUDIO'
    shading.studio_light = 'paint.sl'
    shading.color_type = 'SINGLE'
    shading.single_color = (.58, .60, .62)
    shading.show_shadows = True
    shading.show_cavity = True
    shading.cavity_type = 'BOTH'
    scene.world.color = (.10, .11, .12)
    scene.render.resolution_x = scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    for obj in bpy.data.objects:
        obj.hide_set(False)
        if obj.type == 'MESH':
            obj.hide_render = False
    camera_data = bpy.data.cameras.new('Temporary V15 legs review camera')
    camera = bpy.data.objects.new(camera_data.name, camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera_data.type = 'ORTHO'
    views = [
        ('whole-three-quarter', (-3.5, -5.2, 1.9), (0, -.04, .98), 2.65),
        ('legs-front', (0, -3.0, .66), (0, -.06, .43), 1.05),
        ('legs-three-quarter', (-1.35, -2.15, .70), (0, -.06, .43), 1.00),
    ]
    records = []
    for name, position, target, scale in views:
        camera.location = position
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
        camera_data.ortho_scale = scale
        path = OUT_AUDIT / f'{label}-{name}.png'
        assert not path.exists(), f'Refusing to overwrite render {path.name}'
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        records.append({'view': name, **art(path),
                        'camera': {'position': position, 'target': target, 'orthographicScale': scale},
                        'lighting': 'neutral Blender Workbench; no material or texture treatment'})
    # Camera is temporary review infrastructure; do not save this render state.
    return records


before_views = configure_and_render(BASE, 'before')
after_views = configure_and_render(NATIVE, 'after')
receipt = {
    'schema': 'whole-character-v15-legs-study/v1',
    'status': 'single editable passive leg/foot construction proposal; not accepted or integrated',
    'generatedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'base': art(BASE),
    'native': art(NATIVE),
    'module': art(MODULE),
    'executedModuleSnapshot': art(OUT_AUDIT / 'executed-legs-module.py'),
    'ownerRejectionReference': art(OWNER_REFERENCE),
    'v14CurrentView': art(CURRENT_VIEW),
    'helper': {'path': helper_path.relative_to(ROOT).as_posix(), 'sha256': sha(helper_path)},
    'proposal': proposal,
    'preservation': {
        'all52PivotAndParentSnapshotsExact': True,
        'historicalCurvesExact': True,
        'allNonReplacedInheritedMeshesExact': True,
        'exactReplacedObjects': proposal['replacedObjects'],
        'materialsAndAssignmentsExact': True,
        'toeHingeMeshes': before_toe_hinges,
        'toeHingesUnchanged': len(before_toe_hinges) == 12,
        'newMeshes': len(new_objects),
        'newMeshesByOwner': new_owner_names,
        'savedAndReopenedSnapshotExact': True,
    },
    'views': {'before': before_views, 'after': after_views},
    'limits': [
        'This is a neutral visual construction proposal, not a mechanical load/fatigue analysis.',
        'Toe pivots and all inherited claw/contact meshes are preserved; no ground-contact or motion sweep was run.',
        'No exhaustive self-intersection or clearance diagnostic was run.',
        'The construction is passive across Maker, Mechanic, and Advanced; no new actuator, motor, sensor, or runtime behavior is introduced.',
        'The owner image is a whole-body target; this module addresses only legs and feet.',
    ],
}
assert sha(BASE) == BASE_SHA
with RECEIPT.open('x') as stream:
    stream.write(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'native': receipt['native'],
                  'newMeshes': len(new_objects), 'pivotCount': len(after['empties']),
                  'views': [x['path'] for x in before_views + after_views]}, indent=2))
