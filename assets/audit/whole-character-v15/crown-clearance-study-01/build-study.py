"""Build one isolated sampled-sweep crown relief from frozen V15 attempt 02."""
from pathlib import Path
import datetime, hashlib, json, runpy, shutil
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'assets/models/whole-character-v15/attempt-02/murderbird-whole-character-v15.blend'
EXPECTED_SOURCE = 'a9ffe79aea67bac8f2ae5ebe2157c28ce02e5e0262d7a98bca10531674f95fe5'
MODULE = ROOT / 'scripts/regions/whole-character-v15-crown-clearance.py'
HELPER = ROOT / 'scripts/build-uncaged-alignment-v7.py'
AUDIT = ROOT / 'assets/audit/whole-character-v15/crown-clearance-study-01'
NATIVE = AUDIT / 'murderbird-v15-crown-clearance-study-01.blend'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


assert sha(SOURCE) == EXPECTED_SOURCE, 'Pinned V15 attempt-02 source changed'
assert not NATIVE.exists() and not (AUDIT / 'study-receipt.json').exists(), 'Refusing overwrite'
assert Path(bpy.data.filepath).resolve() == SOURCE.resolve(), 'Blender opened a different base'
AUDIT.mkdir(parents=True, exist_ok=True)
assert not (AUDIT / 'executed-crown-clearance-module.py').exists(), 'Refusing to overwrite frozen module copy'
assert not (AUDIT / 'executed-build-study.py').exists(), 'Refusing to overwrite frozen builder copy'
shutil.copy2(MODULE, AUDIT / 'executed-crown-clearance-module.py')
shutil.copy2(__file__, AUDIT / 'executed-build-study.py')
helper = runpy.run_path(str(HELPER), run_name='v15_crown_clearance_snapshot_helpers')
snapshot = helper['scene_snapshot']
before = snapshot()
result = runpy.run_path(str(MODULE), run_name='whole_character_v15_crown_clearance')['apply']()
after = snapshot()
changed = sorted(name for name in before['meshes'] if before['meshes'][name] != after['meshes'].get(name))
allowed = set(result['changedMeshes'])
assert set(changed).issubset(allowed) and changed, f'Unexpected geometry delta: {changed}'
assert before['empties'] == after['empties'], 'Pivot changed'
assert before['curves'] == after['curves'], 'Guide curve changed'
assert all(before['meshes'][n] == after['meshes'][n] for n in before['meshes'] if n not in allowed), 'Unlisted mesh changed'

bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE), check_existing=False)
bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
reloaded = snapshot()
assert reloaded == after, 'Saved/reopened scene snapshot differs'

# Matched V15 attempt-02 head close-up; render is observational only.
baseline = ROOT / 'assets/audit/whole-character-v15/attempt-02/after-head.png'
shutil.copy2(baseline, AUDIT / 'before-head.png')
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
shade = scene.display.shading
shade.light = 'STUDIO'; shade.studio_light = 'paint.sl'; shade.color_type = 'SINGLE'
shade.single_color = (.56, .58, .60); shade.show_shadows = True; shade.show_cavity = True
shade.cavity_type = 'BOTH'; shade.background_type = 'WORLD'; scene.world.color = (.12, .13, .14)
scene.render.resolution_x = scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100; scene.render.image_settings.file_format = 'PNG'
camera_data = bpy.data.cameras.new('Temporary V15 crown-clearance matched head camera')
camera = bpy.data.objects.new(camera_data.name, camera_data); scene.collection.objects.link(camera)
scene.camera = camera; camera_data.type = 'ORTHO'
camera.location = (-6, -3.5, 2.45)
target = Vector((0, -.27, 1.62))
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera_data.ortho_scale = 1.10
after_image = AUDIT / 'after-head.png'; scene.render.filepath = str(after_image)
bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(camera, do_unlink=True); bpy.data.cameras.remove(camera_data)

receipt = {
    'status': 'single sampled-sweep crown relief proposal; awaiting strict clearance review; not accepted or selected',
    'generatedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'source': {'path': rel(SOURCE), 'sha256': sha(SOURCE), 'bytes': SOURCE.stat().st_size},
    'native': {'path': rel(NATIVE), 'sha256': sha(NATIVE), 'bytes': NATIVE.stat().st_size},
    'inputs': {
        'module': {'path': rel(MODULE), 'sha256': sha(MODULE)},
        'executedModule': {'path': rel(AUDIT / 'executed-crown-clearance-module.py'), 'sha256': sha(AUDIT / 'executed-crown-clearance-module.py')},
        'snapshotHelper': {'path': rel(HELPER), 'sha256': sha(HELPER)},
        'executedBuilder': {'path': rel(AUDIT / 'executed-build-study.py'), 'sha256': sha(AUDIT / 'executed-build-study.py')},
    },
    'edit': result,
    'preservation': {
        'actualChangedMeshes': changed,
        'unexpectedChangedMeshes': sorted(set(changed) - allowed),
        'unchangedMeshes': len(before['meshes']) - len(changed),
        'pivotCountExact': len(before['empties']), 'curveCountExact': len(before['curves']),
        'unlistedMeshSignaturesExact': True, 'saveReopenSnapshotExact': True,
    },
    'comparison': {
        'beforeImage': {'path': rel(AUDIT / 'before-head.png'), 'sha256': sha(AUDIT / 'before-head.png'), 'sourceImage': rel(baseline)},
        'afterImage': {'path': rel(after_image), 'sha256': sha(after_image)},
        'camera': {'position': [-6, -3.5, 2.45], 'target': [0, -.27, 1.62], 'orthographicScale': 1.10},
    },
    'limits': ['The native screen is limited to seven discrete cranial-cover world-Z offsets.',
               'No continuous sweep, penetration-depth or complete-head collision claim.',
               'The candidate is an editable proposal; no export or runtime selection changed.'],
}
(AUDIT / 'study-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
assert sha(SOURCE) == EXPECTED_SOURCE, 'Pinned source changed during study'
print(json.dumps({'nativeSha256': receipt['native']['sha256'], 'changed': changed,
                  'preservation': receipt['preservation'], 'audit': rel(AUDIT)}, indent=2))
