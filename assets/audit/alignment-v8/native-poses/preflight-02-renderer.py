"""Render six exact runtime poses from frozen V8 native without saving it."""
from pathlib import Path
import datetime
import hashlib
import json

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'assets/models/uncaged-alignment-v8/murderbird-alignment-v8.blend'
GLB = ROOT / 'assets/models/uncaged-alignment-v8/murderbird-alignment-v8.glb'
POSES = ROOT / 'assets/audit/neutral-runtime-clearance-poses-v1/pose-snapshot.json'
OUT = ROOT / 'assets/audit/alignment-v8/native-poses'
EXPECTED_NATIVE = 'b12c442e2f517b676cdd1fae1612730cc0ba83251d34f363285b08f2cd482478'
EXPECTED_GLB = 'c8c30cc46059cdd117baf9dce4ceb6ca47040f402618dda419b21acc9d984385'
EXPECTED_POSES = '874396ede48a63d37d743a1a85ae885a10e614a4461f46c50f3a62744a9e2813'
POSE_SOURCE_GLB = '1c82874b86af6b493ac380536de6af72a30fafa3a4b0ebb3d8790f56ffc03018'
POSE_IDS = ('advanced-attention', 'advanced-strike-peak', 'advanced-contact',
            'advanced-jump-airborne', 'advanced-thrust-brace',
            'inspection-open-1-separation-0.5')
DETAIL_POSES = ('advanced-strike-peak', 'inspection-open-1-separation-0.5')
RES = 1200
WHOLE_ORTHO = 2.85
DETAIL_ORTHO = 1.78
C = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))
WHOLE_TARGET = Vector((0.0, -0.10, 0.99))
WHOLE_OFFSET = Vector((-4.25, -5.9, 2.25))
DETAIL_TARGET = Vector((0.0, -0.12, 1.48))
DETAIL_OFFSET = Vector((-1.55, -2.50, .92))
DETAIL_REGIONS = {'head', 'neck', 'shoulder', 'breast'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def converted(flat):
    browser = Matrix([[flat[col * 4 + row] for col in range(4)] for row in range(4)])
    return C.inverted() @ browser @ C


def depth(obj):
    n = 0
    while obj.parent is not None:
        n += 1
        obj = obj.parent
    return n


def matrix_error(a, b):
    return max(abs(a[r][c] - b[r][c]) for r in range(4) for c in range(4))


def set_pose(pose, pivots):
    all_rows = {}
    for row in pose['pivotMatrices']:
        if row.get('kind') == 'mesh':
            continue
        all_rows.setdefault(row['name'], []).append(row)
    assert set(pivots) <= set(all_rows), f"pose misses native pivots: {sorted(set(pivots)-set(all_rows))}"
    assert len(pivots) == 51, f"expected exactly 51 native pivots, found {len(pivots)}"
    rows = {name: all_rows[name] for name in pivots}
    assert all(len(rows[name]) == 1 for name in pivots), 'ambiguous native pivot names in pose packet'
    for name in sorted(pivots, key=lambda n: depth(pivots[n])):
        pivots[name].matrix_world = converted(rows[name][0]['worldMatrix'])
        bpy.context.view_layer.update()
    err = max(matrix_error(pivots[name].matrix_world, converted(rows[name][0]['worldMatrix']))
              for name in pivots)
    assert err < 2e-6, f"pose application mismatch {pose['id']}: {err}"
    return err, sorted(set(all_rows) - set(pivots))


def configure(scene):
    scene.render.engine = 'BLENDER_WORKBENCH'
    shade = scene.display.shading
    shade.light = 'STUDIO'
    shade.studio_light = 'paint.sl'
    shade.color_type = 'SINGLE'
    shade.single_color = (.52, .55, .57)
    shade.show_shadows = True
    shade.show_cavity = True
    shade.cavity_type = 'BOTH'
    shade.curvature_ridge_factor = 1.2
    shade.curvature_valley_factor = 1.1
    shade.background_type = 'WORLD'
    scene.world.color = (.12, .13, .14)
    scene.render.resolution_x = scene.render.resolution_y = RES
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.film_transparent = False


def camera_create(scene, name, target, offset, ortho):
    data = bpy.data.cameras.new(name)
    data.type = 'ORTHO'
    data.ortho_scale = ortho
    data.lens = 70
    data.clip_start = .01
    data.clip_end = 100
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = target + offset
    obj.rotation_euler = (target - obj.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    return obj, data


def bounds_in_camera(objects, camera):
    inv = camera.matrix_world.inverted()
    points = []
    for obj in objects:
        if obj.type != 'MESH':
            continue
        points.extend(inv @ (obj.matrix_world @ vertex.co) for vertex in obj.data.vertices)
    assert points, 'no geometry selected for framing check'
    lo = [min(p[i] for p in points) for i in range(3)]
    hi = [max(p[i] for p in points) for i in range(3)]
    return lo, hi


def check_framing(objects, camera, ortho, margin=.035):
    lo, hi = bounds_in_camera(objects, camera)
    half = ortho / 2
    assert lo[2] > -camera.data.clip_end and hi[2] < -camera.data.clip_start, \
        f'camera-space depth outside clip range: {lo[2]:.4f}..{hi[2]:.4f}'
    # Square output; orthographic horizontal and vertical half-spans match.
    assert lo[0] > -half * (1 - margin) and hi[0] < half * (1 - margin), f'horizontal crop: {lo[0]:.3f}..{hi[0]:.3f}'
    assert lo[1] > -half * (1 - margin) and hi[1] < half * (1 - margin), f'vertical crop: {lo[1]:.3f}..{hi[1]:.3f}'
    return {'cameraLocalMin': lo, 'cameraLocalMax': hi,
            'minimumBorderMarginMeters': min(half - max(abs(lo[0]), abs(hi[0])),
                                             half - max(abs(lo[1]), abs(hi[1])))}


def main():
    assert sha(NATIVE) == EXPECTED_NATIVE, 'V8 native hash mismatch'
    assert sha(GLB) == EXPECTED_GLB, 'V8 GLB hash mismatch'
    assert sha(POSES) == EXPECTED_POSES, 'runtime pose packet hash mismatch'
    manifest = OUT / 'pose-review-manifest.json'
    assert not manifest.exists(), f'preserve existing pose review output: {manifest}'
    pose_data = json.loads(POSES.read_text())
    # The immutable packet was recorded against V7 GLB; exact rest-matrix
    # parity below verifies its 51 transforms against this preserved V8 rig.
    assert pose_data['model']['sha256'] == POSE_SOURCE_GLB
    pose_map = {pose['id']: pose for pose in pose_data['poses']}
    assert all(name in pose_map for name in (*POSE_IDS, 'inspection-open-0-separation-0'))
    assert all('category' in pose_map[name] and 'elapsedSeconds' in pose_map[name] for name in POSE_IDS)
    OUT.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
    scene = bpy.context.scene
    scene.frame_set(1)
    native_empties = {obj.name: obj for obj in bpy.data.objects if obj.type == 'EMPTY'}
    rest_packet_names = {row['name'] for row in pose_map['inspection-open-0-separation-0']['pivotMatrices']
                         if row.get('kind') != 'mesh'}
    pivots = native_empties
    assert len(pivots) == 51, f'expected exactly 51 V8 native pivots, found {len(pivots)}'
    assert set(pivots) <= rest_packet_names, 'pose packet misses one or more inherited V8 pivots'
    assert len(rest_packet_names) == 66, f'unexpected pose-packet transform rows: {len(rest_packet_names)}'
    raw_rest_rows = {row['name']: row for row in pose_map['inspection-open-0-separation-0']['pivotMatrices']
                     if row.get('kind') != 'mesh' and row['name'] in pivots}
    rest_error = max(matrix_error(pivots[name].matrix_world, converted(raw_rest_rows[name]['worldMatrix']))
                     for name in pivots)
    assert rest_error < 2e-6, f'V8 saved rest differs from raw pose packet rest: {rest_error}'
    excluded_packet_transforms = sorted(rest_packet_names - set(pivots))

    # The native is never saved. The builder-era visibility selection exists
    # only in this in-memory evidence scene.
    era_selected = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        eras = [value.strip() for value in obj.get('exteriorEras', 'maker,mechanic,builder').split(',')]
        eligible = 'builder' in eras
        obj.hide_render = not eligible
        obj.hide_set(False)
        if eligible:
            era_selected.append(obj.name)
    visible = [obj for obj in bpy.data.objects if obj.type == 'MESH' and not obj.hide_render]
    detail = [obj for obj in visible if obj.get('region') in DETAIL_REGIONS]
    configure(scene)
    whole_camera, whole_data = camera_create(scene, 'Temporary V8 whole-bird review camera',
                                             WHOLE_TARGET, WHOLE_OFFSET, WHOLE_ORTHO)
    detail_camera, detail_data = camera_create(scene, 'Temporary V8 head-shoulder review camera',
                                               DETAIL_TARGET, DETAIL_OFFSET, DETAIL_ORTHO)

    records, pose_rows = [], []
    for pose_id in POSE_IDS:
        pose = pose_map[pose_id]
        err, excluded = set_pose(pose, pivots)
        assert excluded == excluded_packet_transforms, 'packet-only transform inventory varied by pose'
        scene.camera = whole_camera
        whole_framing = check_framing(visible, whole_camera, WHOLE_ORTHO)
        path = OUT / f'{pose_id}-whole-bird-3q.png'
        assert not path.exists()
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        records.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'bytes': path.stat().st_size,
                        'poseId': pose_id, 'view': 'whole-bird 3/4', 'cameraMatrixWorld': [list(r) for r in whole_camera.matrix_world],
                        'orthoScale': WHOLE_ORTHO, 'framing': whole_framing})
        detail_record = None
        if pose_id in DETAIL_POSES:
            scene.camera = detail_camera
            detail_framing = check_framing(detail, detail_camera, DETAIL_ORTHO)
            detail_path = OUT / f'{pose_id}-head-shoulder-detail.png'
            assert not detail_path.exists()
            scene.render.filepath = str(detail_path)
            bpy.ops.render.render(write_still=True)
            detail_record = {'path': str(detail_path.relative_to(ROOT)), 'sha256': sha(detail_path),
                             'bytes': detail_path.stat().st_size, 'poseId': pose_id,
                             'view': 'head / neck / shoulder / breast detail',
                             'cameraMatrixWorld': [list(r) for r in detail_camera.matrix_world],
                             'orthoScale': DETAIL_ORTHO, 'framing': detail_framing,
                             'framingRegions': sorted(DETAIL_REGIONS)}
            records.append(detail_record)
        pose_rows.append({'id': pose_id, 'category': pose['category'], 'elapsedSeconds': pose['elapsedSeconds'],
                          'controller': pose['controller'], 'motionMetrics': pose['motionMetrics'],
                          'pivotMatrixMaxError': err, 'detailRendered': detail_record is not None})

    bpy.data.objects.remove(whole_camera, do_unlink=True)
    bpy.data.cameras.remove(whole_data)
    bpy.data.objects.remove(detail_camera, do_unlink=True)
    bpy.data.cameras.remove(detail_data)
    result = {
        'schema': 'alignment-v8-native-pose-review/v1',
        'status': 'native authoring review; not publication or owner acceptance',
        'generatedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'native': {'path': str(NATIVE.relative_to(ROOT)), 'sha256': sha(NATIVE), 'bytes': NATIVE.stat().st_size},
        'glb': {'path': str(GLB.relative_to(ROOT)), 'sha256': sha(GLB), 'bytes': GLB.stat().st_size},
        'posePacket': {'path': str(POSES.relative_to(ROOT)), 'sha256': sha(POSES),
                       'declaredSourceGlb': pose_data['model'],
                       'applicationLimit': 'The immutable controller samples were recorded against V7; the V8 native preserves that 51-pivot rig and passes exact raw-rest matrix comparison. These are pose-replayed native renders, not a V8 application runtime capture.'},
        'script': {'path': str(Path(__file__).resolve().relative_to(ROOT)), 'sha256': sha(Path(__file__).resolve())},
        'blenderVersion': bpy.app.version_string,
        'nativePivotCount': len(native_empties), 'sampledNativePivotCount': len(pivots),
        'nativePivotNames': sorted(native_empties),
        'posePacketTransformRowCount': len(rest_packet_names),
        'excludedPacketOnlyProceduralTransformRows': excluded_packet_transforms,
        'rawRestPoseId': 'inspection-open-0-separation-0', 'rawRestWorldMatrixMaxError': rest_error,
        'renderConfiguration': {'engine': 'BLENDER_WORKBENCH', 'neutralSingleColor': [.52, .55, .57],
                                'resolution': [RES, RES], 'builderEraOnly': True,
                                'builderVisibleMeshCount': len(era_selected),
                                'wholeBirdCamera': {'target': list(WHOLE_TARGET), 'offset': list(WHOLE_OFFSET), 'orthoScale': WHOLE_ORTHO},
                                'detailCamera': {'target': list(DETAIL_TARGET), 'offset': list(DETAIL_OFFSET), 'orthoScale': DETAIL_ORTHO}},
        'poses': pose_rows, 'renders': records,
        'limits': ['Six discrete production runtime packet states; all 51 native pivot matrices were applied exactly within tolerance.',
                   'Workbench stills are authoring views only; no browser or actual WebGL rendering was performed here.',
                   'The inspection sample is a snapshot, not a complete inspection transition.',
                   'No physical simulation, continuous clearance, likeness, owner, or publication acceptance is implied.',
                   'Native V8 was opened read-only and never saved.']
    }
    assert not manifest.exists()
    manifest.write_text(json.dumps(result, indent=2) + '\n')
    assert sha(NATIVE) == EXPECTED_NATIVE and sha(GLB) == EXPECTED_GLB and sha(POSES) == EXPECTED_POSES
    print(json.dumps({'status': 'rendered', 'poses': len(pose_rows), 'images': len(records),
                      'nativeSha256': result['native']['sha256'], 'glbSha256': result['glb']['sha256'],
                      'restMatrixMaxError': rest_error}))


if __name__ == '__main__':
    main()
