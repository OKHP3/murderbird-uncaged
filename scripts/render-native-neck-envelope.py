"""Render eight pinned V7 neck/breast poses for a bounded visual review.

Reads the native file and runtime pose receipt, changes only in-memory pivot
matrices/render settings, and never saves the Blender project.
"""
from pathlib import Path
import hashlib
import json
import math
import sys

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'assets/models/uncaged-alignment-v7/murderbird-alignment-v7.blend'
POSES = ROOT / 'assets/audit/neutral-runtime-clearance-poses-v1/pose-snapshot.json'
OUT = ROOT / 'assets/audit/native-neck-envelope-review-v1'
EXPECTED_NATIVE = 'a8fccaf024a096678415215029b34cae8270b348da2301b8872a34e72c75ed3f'
EXPECTED_POSES = '874396ede48a63d37d743a1a85ae885a10e614a4461f46c50f3a62744a9e2813'
POSE_IDS = [
    'inspection-open-0-separation-0',
    'advanced-strike-peak',
    'advanced-contact',
    'inspection-open-1-separation-0',
]
RESOLUTION = (1100, 1100)
ORTHO_SCALE = 1.26
C = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def converted(flat):
    browser = Matrix([[flat[col * 4 + row] for col in range(4)] for row in range(4)])
    return C.inverted() @ browser @ C


def depth(obj):
    count = 0
    while obj.parent is not None:
        count += 1
        obj = obj.parent
    return count


def error(a, b):
    return max(abs(a[r][c] - b[r][c]) for r in range(4) for c in range(4))


def set_pose(pose, pivots):
    matrices = pose['pivotMatrices']
    by_name = {}
    for row in matrices:
        if row.get('kind') == 'mesh':
            continue
        by_name.setdefault(row['name'], []).append(row)
    assert set(pivots) <= set(by_name), f"pose is missing native pivots: {sorted(set(pivots) - set(by_name))}"
    assert all(len(by_name[name]) == 1 for name in pivots), 'native pivot name is ambiguous in runtime pose rows'
    for name in sorted(pivots, key=lambda n: depth(pivots[n])):
        pivots[name].matrix_world = converted(by_name[name][0]['worldMatrix'])
        bpy.context.view_layer.update()
    max_error = max(error(pivots[name].matrix_world, converted(by_name[name][0]['worldMatrix'])) for name in pivots)
    assert max_error < 2e-6, f"pose application mismatch {pose['id']}: {max_error}"
    return max_error


def configure_scene(scene):
    scene.render.engine = 'BLENDER_WORKBENCH'
    shade = scene.display.shading
    shade.light = 'STUDIO'
    shade.studio_light = 'paint.sl'
    shade.color_type = 'SINGLE'
    shade.single_color = (.52, .55, .57)
    shade.show_shadows = True
    shade.show_cavity = True
    shade.cavity_type = 'BOTH'
    shade.curvature_ridge_factor = 1.25
    shade.curvature_valley_factor = 1.15
    shade.background_type = 'WORLD'
    scene.world.color = (.12, .13, .14)
    scene.render.resolution_x, scene.render.resolution_y = RESOLUTION
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = 'RGB'


def pose_target(pivots):
    a = pivots['neck'].matrix_world.translation
    b = pivots['breastplate'].matrix_world.translation
    return (a + b) * .5


def render_view(scene, camera, camera_data, pose_id, view, target):
    offsets = {
        'side': Vector((-5.5, 0, .15)),
        'three-quarter': Vector((-3.65, -4.8, 1.45)),
    }
    camera.location = target + offsets[view]
    camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera_data.type = 'ORTHO'
    camera_data.ortho_scale = ORTHO_SCALE
    camera_data.lens = 70
    scene.camera = camera
    bpy.context.view_layer.update()
    path = OUT / f'{pose_id}-{view}.png'
    assert not path.exists(), f'preserve existing render: {path}'
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return {
        'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'bytes': path.stat().st_size,
        'poseId': pose_id, 'view': view, 'targetWorld': list(target),
        'cameraMatrixWorldRows': [list(row) for row in camera.matrix_world],
        'cameraLocationWorld': list(camera.location), 'cameraEuler': list(camera.rotation_euler),
        'projection': camera_data.type, 'orthoScale': camera_data.ortho_scale,
        'resolution': list(RESOLUTION),
    }


def main():
    assert sha(NATIVE) == EXPECTED_NATIVE, 'V7 native input hash changed'
    assert sha(POSES) == EXPECTED_POSES, 'runtime pose packet hash changed'
    pose_data = json.loads(POSES.read_text())
    assert pose_data['model']['sha256'] == '1c82874b86af6b493ac380536de6af72a30fafa3a4b0ebb3d8790f56ffc03018'
    pose_map = {pose['id']: pose for pose in pose_data['poses']}
    assert all(name in pose_map for name in POSE_IDS)
    assert not OUT.exists(), f'write-once audit directory already exists: {OUT}'
    OUT.mkdir(parents=True)

    bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
    scene = bpy.context.scene
    scene.frame_set(1)
    configure_scene(scene)
    pivots = {obj.name: obj for obj in bpy.data.objects if obj.type == 'EMPTY'}
    assert len(pivots) == 51, f'expected exact V7 native pivot inventory of 51, found {len(pivots)}'
    assert 'neck' in pivots and 'breastplate' in pivots and 'head' in pivots and 'jaw' in pivots
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            eras = [value.strip() for value in obj.get('exteriorEras', 'maker,mechanic,builder').split(',')]
            obj.hide_render = 'builder' not in eras
            obj.hide_set(False)

    camera_data = bpy.data.cameras.new('Temporary V7 neck pose review camera')
    camera = bpy.data.objects.new('Temporary V7 neck pose review camera', camera_data)
    scene.collection.objects.link(camera)
    records = []
    pose_records = []
    for pose_id in POSE_IDS:
        pose = pose_map[pose_id]
        max_matrix_error = set_pose(pose, pivots)
        target = pose_target(pivots)
        pose_records.append({'poseId': pose_id, 'controllerState': pose['controller']['state'],
                             'controllerEra': pose['controller']['era'], 'worldPivotMatrixMaxError': max_matrix_error,
                             'neckPivotWorld': list(pivots['neck'].matrix_world.translation),
                             'headPivotWorld': list(pivots['head'].matrix_world.translation),
                             'breastplatePivotWorld': list(pivots['breastplate'].matrix_world.translation),
                             'jawPivotWorld': list(pivots['jaw'].matrix_world.translation),
                             'cameraTargetWorld': list(target)})
        for view in ('side', 'three-quarter'):
            records.append(render_view(scene, camera, camera_data, pose_id, view, target))

    script_path = Path(__file__).resolve()
    result = {
        'schema': 'native-neck-envelope-review/v1',
        'generatedAt': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
        'native': {'path': str(NATIVE.relative_to(ROOT)), 'sha256': sha(NATIVE), 'bytes': NATIVE.stat().st_size},
        'posePacket': {'path': str(POSES.relative_to(ROOT)), 'sha256': sha(POSES),
                       'declaredGlbSha256': pose_data['model']['sha256']},
        'executedScript': {'path': str(script_path.relative_to(ROOT)), 'sha256': sha(script_path)},
        'blenderVersion': bpy.app.version_string,
        'nativePivotCount': len(pivots), 'nativePivotNames': sorted(pivots),
        'renderConfiguration': {'engine': scene.render.engine, 'shading': 'Workbench single neutral gray, studio paint.sl, cavity and shadows',
                                'resolution': list(RESOLUTION), 'orthographicScale': ORTHO_SCALE,
                                'builderEraEligibility': True, 'nativeSavePerformed': False},
        'poses': pose_records, 'renders': records,
        'limits': ['Original V7 only; no study geometry was loaded.',
                   'Discrete exact runtime pivot samples; no continuous swept-volume or physical collision claim.',
                   'Neutral Workbench images are visual review evidence, not browser/WebGL or owner acceptance.'],
    }
    bpy.data.objects.remove(camera, do_unlink=True)
    bpy.data.cameras.remove(camera_data)
    (OUT / 'review-manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'rendered', 'poses': len(pose_records), 'images': len(records),
                      'nativeSha256': result['native']['sha256'], 'posePacketSha256': result['posePacket']['sha256']}))


if __name__ == '__main__':
    main()
