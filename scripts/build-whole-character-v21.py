"""Write-once V21 coordinated-envelope native and an early matched visual gate."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import runpy
import shutil
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'assets/models/whole-character-v20/attempt-runtime02/murderbird-whole-character-v20.blend'
BASE_SHA = 'eb15a9d87de56fb8a06004d9c69448c38089f0ecacd888e3e7fde921a353d42a'
SOURCE = ROOT / 'scripts/regions/whole-character-v21-envelope.py'
parser = argparse.ArgumentParser()
parser.add_argument('--attempt', required=True)
parser.add_argument('--articulation-views', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
assert args.attempt.replace('-', '').isalnum(), 'Use a plain attempt name'
AUDIT = ROOT / f'assets/audit/whole-character-v21/attempt-{args.attempt}'
OUT = ROOT / f'assets/models/whole-character-v21/attempt-{args.attempt}'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'bytes': path.stat().st_size}


def clear_in_memory_animation(scene):
    """Keep inherited authoring actions from replacing temporary pose edits."""
    cleared = []
    for obj in bpy.data.objects:
        if obj.animation_data is not None:
            obj.animation_data_clear()
            cleared.append(f'object:{obj.name}')
        data = getattr(obj, 'data', None)
        if data is not None and hasattr(data, 'animation_data') and data.animation_data is not None:
            data.animation_data_clear()
            cleared.append(f'data:{data.name}')
    if scene.animation_data is not None:
        scene.animation_data_clear()
        cleared.append(f'scene:{scene.name}')
    return cleared


assert sha(BASE) == BASE_SHA and not AUDIT.exists() and not OUT.exists()
AUDIT.mkdir(parents=True)
OUT.mkdir(parents=True)
shutil.copy2(__file__, AUDIT / 'executed-composition.py')
shutil.copy2(SOURCE, AUDIT / 'executed-envelope.py')
helpers = runpy.run_path(str(ROOT / 'scripts/build-uncaged-alignment-v7.py'))
bpy.ops.wm.open_mainfile(filepath=str(BASE))
before = helpers['scene_snapshot']()
old_world = {o.name: o.matrix_world.copy() for o in bpy.data.objects}
old_mesh = {o.name: [o.matrix_world @ v.co for v in o.data.vertices]
            for o in bpy.data.objects if o.type == 'MESH'}
materials = {m.name: helpers['material_signature'](m) for m in bpy.data.materials}
result = runpy.run_path(str(AUDIT / 'executed-envelope.py'))['apply']()
after = helpers['scene_snapshot']()
assert set(before['empties']) == set(after['empties'])
assert all(before['empties'][n]['parent'] == after['empties'][n]['parent'] for n in before['empties'])
assert materials == {m.name: helpers['material_signature'](m) for m in bpy.data.materials}
removed = {p['name'] for p in result['stagedOut']}
added = {p['name'] for p in result['added']}
assert set(before['meshes']) - set(after['meshes']) == removed
assert set(after['meshes']) - set(before['meshes']) == added
remaining = set(old_mesh) - removed
maximum_world_error = 0.0
for name in remaining:
    obj = bpy.data.objects[name]
    assert len(obj.data.vertices) == len(old_mesh[name])
    err = max(((obj.matrix_world @ v.co) - old_mesh[name][v.index]).length for v in obj.data.vertices)
    maximum_world_error = max(maximum_world_error, err)
assert maximum_world_error < 1e-6, f'Unrelated world geometry moved: {maximum_world_error}'
node_errors = {name: max(abs(bpy.data.objects[name].matrix_world[i][j] - old_world[name][i][j])
                        for i in range(4) for j in range(4)) for name in before['empties']}
assert {n for n, e in node_errors.items() if e > 1e-6} == set(result['changedPivots'])
evaluated = []
depsgraph = bpy.context.evaluated_depsgraph_get()
for name in sorted(after['meshes']):
    obj = bpy.data.objects[name]
    evaluated_obj = obj.evaluated_get(depsgraph)
    mesh = evaluated_obj.to_mesh()
    assert all(math.isfinite(c) for v in mesh.vertices for c in v.co), f'Nonfinite evaluated vertex: {name}'
    if name in added:
        copy = mesh.copy()
        repaired = copy.validate()
        bpy.data.meshes.remove(copy)
        evaluated.append({'name': name, 'vertices': len(mesh.vertices), 'faces': len(mesh.polygons),
                          'validationRepairedDisposableCopy': bool(repaired)})
        assert not repaired, f'Invalid new evaluated mesh: {name}'
    evaluated_obj.to_mesh_clear()
contract = AUDIT / 'construction-contract.json'
contract.write_text(json.dumps(result, indent=2) + '\n')
native = OUT / 'murderbird-whole-character-v21.blend'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(native), check_existing=False)
bpy.ops.wm.open_mainfile(filepath=str(native))
assert helpers['scene_snapshot']() == after, 'Save/reopen changed native state'
native_sha = sha(native)
receipt = {'status': 'coarse shared-envelope visual gate; no likeness, motion or engineering acceptance',
           'base': artifact(BASE), 'native': artifact(native),
           'composition': artifact(AUDIT / 'executed-composition.py'),
           'envelope': artifact(AUDIT / 'executed-envelope.py'), 'contract': artifact(contract),
           'checks': {'rigidNamesAndParents': len(after['empties']), 'changedWorldPivots': list(result['changedPivots']),
                      'removedSourceMeshesInDerivativeOnly': len(removed), 'newMeshes': len(added),
                      'retainedMeshWorldGeometry': len(remaining), 'maximumRetainedWorldErrorM': maximum_world_error,
                      'worldToleranceM': 1e-6, 'allEvaluatedMeshesFinite': len(after['meshes']),
                      'materialsExact': True, 'saveReopenExact': True, 'sourceNativeUnchanged': True},
           'newEvaluatedMeshes': evaluated, 'views': [],
           'limits': ['V20 mechanism socket metadata is stale under changed neck rests; no runtime export or selection.',
                      'Continuous mechanical clearance and visual likeness remain unverified.']}
receipt_path = AUDIT / 'receipt.json'
receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
views = [('reference-angle', (-6, -3.5, 2.75), (0, -.08, 1.02), 2.5),
         ('front', (0, -7, 1.65), (0, -.08, 1.02), 2.5),
         ('side', (-7, 0, 1.35), (0, -.08, 1.02), 2.5),
         ('neck', (-6, -3.5, 2.45), (0, -.27, 1.48), 1.30)]
for label, path in [('after', native), ('before', BASE)]:
    bpy.ops.wm.open_mainfile(filepath=str(path))
    scene = bpy.context.scene
    animation_cleared_on_open = clear_in_memory_animation(scene)
    scene.render.engine = 'BLENDER_WORKBENCH'
    shading = scene.display.shading
    shading.light = 'STUDIO'
    shading.studio_light = 'paint.sl'
    shading.color_type = 'SINGLE'
    shading.single_color = (.56, .58, .60)
    shading.show_shadows = False
    shading.show_cavity = True
    shading.cavity_type = 'BOTH'
    shading.background_type = 'WORLD'
    scene.world.color = (.12, .13, .14)
    scene.render.resolution_x = scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    for obj in bpy.data.objects:
        obj.hide_set(False)
        if obj.type == 'MESH':
            obj.hide_render = 'builder' not in obj.get('exteriorEras', 'maker,mechanic,builder').split(',')
        if obj.type == 'CURVE':
            obj.hide_render = True
    data = bpy.data.cameras.new('Temporary V21 neutral camera')
    data.type = 'ORTHO'
    camera = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    for name, position, target, scale in views:
        camera.location = position
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
        data.ortho_scale = scale
        image = AUDIT / f'{label}-{name}.png'
        scene.render.filepath = str(image)
        bpy.ops.render.render(write_still=True)
        receipt['views'].append({**artifact(image), 'era': 'builder', 'camera': {'position': position, 'target': target, 'scale': scale},
                                 'lighting': 'neutral native Workbench paint.sl; cast shadows off; authoring guides hidden'})
        receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    if label == 'after' and args.articulation_views:
        # The saved native's inherited actions can reset head counter-rotation
        # during frame evaluation. These are temporary authoring views only.
        cleared_immediately_before_override = clear_in_memory_animation(scene)
        rest_rotations = {name: bpy.data.objects[name].rotation_euler.copy()
                          for name in ('neck', 'cervical-upper', 'head', 'breastplate')}
        studies = [
            ('native-dip', {'neck': .2275, 'cervical-upper': .4225, 'head': -.65},
             (-6, -3.5, 2.45), (0, -.30, 1.38), 1.45),
            ('native-breast-open', {'breastplate': 1.1},
             (-6, -3.5, 2.75), (0, -.08, 1.02), 2.5),
        ]
        for name, angles, position, target, scale in studies:
            clear_in_memory_animation(scene)
            for node, rotation in rest_rotations.items():
                bpy.data.objects[node].rotation_euler = rotation.copy()
            for node, angle in angles.items():
                bpy.data.objects[node].rotation_euler.x += angle
            bpy.context.view_layer.update()
            camera.location = position
            camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
            data.ortho_scale = scale
            image = AUDIT / f'{name}.png'
            scene.render.filepath = str(image)
            bpy.ops.render.render(write_still=True)
            receipt['views'].append({**artifact(image), 'era': 'builder', 'nativeLocalXAngles': angles,
                                     'camera': {'position': position, 'target': target, 'scale': scale},
                                     'animationDatablocksClearedOnOpen': animation_cleared_on_open,
                                     'additionalAnimationDataClearedImmediatelyBeforeOverride': cleared_immediately_before_override,
                                     'status': 'authoring articulation illustration; no runtime/contact/collision acceptance'})
            receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
assert sha(BASE) == BASE_SHA and sha(native) == native_sha
print(json.dumps({'native': receipt['native'], 'checks': receipt['checks'], 'views': len(receipt['views'])}, indent=2))
