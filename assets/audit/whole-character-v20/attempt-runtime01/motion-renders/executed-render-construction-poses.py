"""Render selected whole-character poses from a supplied runtime matrix packet.

This is a native Blender illustration tool. It does not capture browser frames,
modify/save the native, change runtime code, or validate continuous motion.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import struct
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parents[1]
ERAS = {'maker', 'mechanic', 'builder'}
POSES_TO_RENDER = (
    'maker-jaw-control',
    'maker-wing-control-right-mantle',
    'mechanic-segment-turn-release',
    'advanced-contact',
    'advanced-recovery-entry',
    'advanced-jump-airborne',
    'advanced-thrust-brace',
    'inspection-open-1-separation-0',
)
CONVERSION = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))
RESOLUTION = 1200
ORTHO_SCALE = 4.35


def parse_args():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--native', required=True)
    parser.add_argument('--native-sha256', required=True)
    parser.add_argument('--glb', required=True)
    parser.add_argument('--glb-sha256', required=True)
    parser.add_argument('--poses', required=True)
    parser.add_argument('--poses-sha256', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--no-shadows', action='store_true',
                        help='Disable Workbench cast shadows; does not hide or change model geometry')
    args = parser.parse_args(argv)
    for key in ('native', 'glb', 'poses', 'out'):
        raw = Path(getattr(args, key))
        assert not raw.is_absolute(), f'--{key} must be repository-relative'
        resolved = (ROOT / raw).resolve()
        assert resolved == ROOT or ROOT in resolved.parents, f'--{key} escapes repository'
        setattr(args, key, resolved)
    return args


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def artifact(path):
    path = Path(path)
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'bytes': path.stat().st_size}


def converted(flat):
    browser = Matrix([[flat[col * 4 + row] for col in range(4)] for row in range(4)])
    return CONVERSION.inverted() @ browser @ CONVERSION


def depth(obj):
    count = 0
    while obj.parent is not None:
        count += 1
        obj = obj.parent
    return count


def matrix_error(a, b):
    return max(abs(float(a[r][c]) - float(b[r][c])) for r in range(4) for c in range(4))


def rows_by_name(pose):
    rows = {}
    for row in pose['pivotMatrices']:
        if row.get('kind') == 'transform':
            rows.setdefault(row['name'], []).append(row)
    return rows


def apply_pose(pose, pivots):
    rows = rows_by_name(pose)
    assert set(pivots) <= set(rows), f"{pose['id']} is missing native pivot rows: {sorted(set(pivots)-set(rows))}"
    assert all(len(rows[name]) == 1 for name in pivots), f"{pose['id']} has ambiguous native pivot rows"
    for name in sorted(pivots, key=lambda n: depth(pivots[n])):
        pivots[name].matrix_world = converted(rows[name][0]['worldMatrix'])
        bpy.context.view_layer.update()
    error = max(matrix_error(pivots[n].matrix_world, converted(rows[n][0]['worldMatrix'])) for n in pivots)
    assert error < 2e-6, f"{pose['id']} matrix application error {error}"
    return error, sorted(set(rows) - set(pivots))


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
    shade.curvature_ridge_factor = 1.15
    shade.curvature_valley_factor = 1.05
    shade.background_type = 'WORLD'
    scene.world.color = (.12, .13, .14)
    scene.render.resolution_x = scene.render.resolution_y = RESOLUTION
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.film_transparent = False


def glb_rest_worlds(path):
    raw = Path(path).read_bytes()
    assert raw[:4] == b'glTF' and struct.unpack_from('<I', raw, 4)[0] == 2
    length = struct.unpack_from('<I', raw, 12)[0]
    document = json.loads(raw[20:20 + length])
    result = {}

    def visit(index, parent):
        node = document['nodes'][index]
        if 'matrix' in node:
            local = Matrix([[node['matrix'][col * 4 + row] for col in range(4)] for row in range(4)])
        else:
            q = node.get('rotation', [0, 0, 0, 1])
            local = Matrix.LocRotScale(Vector(node.get('translation', [0, 0, 0])),
                                       Quaternion((q[3], q[0], q[1], q[2])),
                                       Vector(node.get('scale', [1, 1, 1])))
        world = parent @ local
        name = node.get('name')
        if name:
            assert name not in result, f'Duplicate GLB node name: {name}'
            result[name] = CONVERSION.inverted() @ world @ CONVERSION
        for child in node.get('children', []):
            visit(child, world)

    for root in document['scenes'][document.get('scene', 0)]['nodes']:
        visit(root, Matrix.Identity(4))
    return result


def add_camera_and_floor(scene):
    camera_data = bpy.data.cameras.new('Temporary construction pose camera')
    camera_data.type = 'ORTHO'
    camera_data.ortho_scale = ORTHO_SCALE
    camera_data.lens = 70
    camera_data.clip_start, camera_data.clip_end = .01, 100
    camera = bpy.data.objects.new(camera_data.name, camera_data)
    scene.collection.objects.link(camera)
    floor_mesh = bpy.data.meshes.new('Temporary native Z0 review floor mesh')
    floor_mesh.from_pydata([(-30, -30, 0), (30, -30, 0), (30, 30, 0), (-30, 30, 0)], [], [(0, 1, 2, 3)])
    floor = bpy.data.objects.new('Temporary native Z0 review floor', floor_mesh)
    scene.collection.objects.link(floor)
    floor['temporaryReviewFloor'] = True
    return camera, camera_data, floor, floor_mesh


def framing_bounds(objects, camera):
    inverse = camera.matrix_world.inverted()
    points = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            points.extend(inverse @ (evaluated.matrix_world @ v.co) for v in mesh.vertices)
        finally:
            evaluated.to_mesh_clear()
    assert points, 'No visible character meshes for framing'
    lo = [min(p[i] for p in points) for i in range(3)]
    hi = [max(p[i] for p in points) for i in range(3)]
    half = ORTHO_SCALE / 2
    assert lo[2] > -camera.data.clip_end and hi[2] < -camera.data.clip_start
    assert lo[0] > -half * .975 and hi[0] < half * .975, f'full-body horizontal crop: {lo[0]:.3f}..{hi[0]:.3f}'
    assert lo[1] > -half * .975 and hi[1] < half * .975, f'full-body vertical crop: {lo[1]:.3f}..{hi[1]:.3f}'
    return {'cameraLocalMin': lo, 'cameraLocalMax': hi,
            'minimumBorderMarginM': min(half - max(abs(lo[0]), abs(hi[0])),
                                        half - max(abs(lo[1]), abs(hi[1])))}


def main():
    args = parse_args()
    for path, expected, label in ((args.native, args.native_sha256, 'native'),
                                  (args.glb, args.glb_sha256, 'GLB'),
                                  (args.poses, args.poses_sha256, 'pose packet')):
        assert path.is_file() and sha(path) == expected, f'{label} missing or SHA-256 mismatch'
    assert not args.out.exists(), f'Refusing to overwrite output directory: {args.out}'
    pose_data = json.loads(args.poses.read_text())
    assert pose_data['model']['sha256'] == args.glb_sha256, 'pose packet is not bound to supplied GLB'
    assert pose_data.get('poseCount') == len(pose_data.get('poses', [])) == 21, 'expected the complete 21-pose packet'
    pose_map = {p['id']: p for p in pose_data['poses']}
    assert all(name in pose_map for name in POSES_TO_RENDER), 'pose packet is missing a selected pose'
    args.out.mkdir(parents=True)
    frozen = args.out / 'executed-render-construction-poses.py'
    frozen.write_bytes(Path(__file__).resolve().read_bytes())

    bpy.ops.wm.open_mainfile(filepath=str(args.native))
    scene = bpy.context.scene
    scene.frame_set(1)
    bpy.context.view_layer.update()
    pivots = {o.name: o for o in bpy.data.objects if o.type == 'EMPTY'}
    assert len(pivots) == 52, f'expected exactly 52 native pivots; found {len(pivots)}'
    exported = glb_rest_worlds(args.glb)
    assert set(pivots) <= set(exported), 'GLB missing one or more native pivots'
    export_error = max(matrix_error(pivots[n].matrix_world, exported[n]) for n in pivots)
    assert export_error < 2e-6, f'native rest differs from supplied GLB: {export_error}'

    # Historical authoring guides are preserved in the native, but are not
    # runtime cables and must not draw stray lines in pose illustrations.
    hidden_guides = [o.name for o in bpy.data.objects if o.type == 'CURVE']
    for name in hidden_guides:
        bpy.data.objects[name].hide_render = True
    base_hidden = {o.name: bool(o.hide_render) for o in bpy.data.objects if o.type == 'MESH'}
    mesh_objects = [o for o in bpy.data.objects if o.type == 'MESH']
    assert mesh_objects
    camera, camera_data, floor, floor_mesh = add_camera_and_floor(scene)
    floor.hide_render = False
    configure(scene)
    scene.display.shading.show_shadows = not args.no_shadows
    camera.rotation_euler = Vector((0, 0, 0)).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = camera
    records = []
    for pose_id in POSES_TO_RENDER:
        pose = pose_map[pose_id]
        error, packet_only = apply_pose(pose, pivots)
        era = pose.get('controller', {}).get('era') or pose.get('motionMetrics', {}).get('era')
        assert era in ERAS, f'{pose_id} has an unrecognized exhibit era: {era}'
        visible, hidden_era, hidden_source = [], [], []
        for obj in mesh_objects:
            declared = [x.strip() for x in obj.get('exteriorEras', 'maker,mechanic,builder').split(',')]
            assert set(declared) <= ERAS, f'unrecognized exterior era on {obj.name}: {declared}'
            if base_hidden[obj.name]:
                obj.hide_render = True
                hidden_source.append(obj.name)
            elif era not in declared:
                obj.hide_render = True
                hidden_era.append(obj.name)
            else:
                obj.hide_render = False
                visible.append(obj)
        root = pivots['murderbird'].matrix_world
        target = root @ Vector((0.0, 0.0, 1.0))
        offset = root.to_quaternion() @ Vector((-3.3, -4.4, 1.8))
        camera.location = target + offset
        camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
        bpy.context.view_layer.update()
        bounds = framing_bounds(visible, camera)
        path = args.out / f'{pose_id}-whole-character.png'
        assert not path.exists()
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        records.append({
            'poseId': pose_id, 'category': pose['category'], 'era': era,
            'controllerState': pose.get('controller', {}).get('state'),
            'elapsedSeconds': pose.get('elapsedSeconds'),
            'actionEvidence': {key: pose.get('controller', {}).get(key)
                               for key in ('articulation', 'routineRunning', 'powerMove', 'clawAction', 'inspection')},
            'motionMetrics': pose.get('motionMetrics'),
            'pivotMatrixMaxError': error, 'nativePivotCountApplied': len(pivots),
            'packetOnlyTransformNamesNotApplied': packet_only,
            'visibleMeshCount': len(visible), 'hiddenByEraCount': len(hidden_era),
            'hiddenBySourceVisibilityCount': len(hidden_source),
            'cameraTargetNative': list(target), 'cameraOffsetNative': list(offset),
            'orthographicScaleM': ORTHO_SCALE, 'floorPlane': 'temporary at native Z=0',
            'framing': bounds, 'image': artifact(path),
        })

    bpy.data.objects.remove(camera, do_unlink=True)
    bpy.data.cameras.remove(camera_data)
    bpy.data.objects.remove(floor, do_unlink=True)
    bpy.data.meshes.remove(floor_mesh)
    result = {
        'schema': 'murderbird-native-construction-pose-renders/v1',
        'status': 'packet-driven native pose illustrations; not live motion or acceptance evidence',
        'generatedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'native': artifact(args.native), 'glb': artifact(args.glb), 'posePacket': artifact(args.poses),
        'declaredPoseModel': pose_data['model'],
        'renderer': artifact(Path(__file__).resolve()),
        'frozenExecutedRenderer': artifact(frozen),
        'blenderVersion': bpy.app.version_string,
        'nativePivotCount': len(pivots), 'rawGlbRestMatrixMaxError': export_error,
        'historicalAuthoringGuidesHiddenInIllustration': hidden_guides,
        'eraVisibility': 'per-mesh exteriorEras evaluated against selected pose era; original hide_render flags retained',
        'render': {'engine': 'BLENDER_WORKBENCH', 'resolution': [RESOLUTION, RESOLUTION],
                   'lighting': 'neutral studio with cavity', 'castShadows': not args.no_shadows,
                   'camera': 'consistent root-relative full-body three-quarter',
                   'floor': 'temporary plane at native Z=0; excluded from character framing bounds'},
        'poseSelection': list(POSES_TO_RENDER), 'poses': records,
        'limits': [
            'These images replay deterministic runtime-module matrices on the native hierarchy; they are not browser captures or a live recording.',
            'Eight discrete poses only; no continuous collision, ground-contact, or mechanical clearance validation.',
            'No native save, runtime change, or GLB export is performed.',
            'Era visibility follows authored exteriorEras tags and each packet controller/motionMetrics era.'
        ]
    }
    manifest = args.out / 'pose-render-manifest.json'
    assert not manifest.exists()
    manifest.write_text(json.dumps(result, indent=2) + '\n')
    for path, expected in ((args.native, args.native_sha256), (args.glb, args.glb_sha256), (args.poses, args.poses_sha256)):
        assert sha(path) == expected, f'input changed while rendering: {path}'
    print(json.dumps({'status': result['status'], 'poses': len(records), 'nativePivotCount': len(pivots),
                      'nativeSha256': args.native_sha256, 'glbSha256': args.glb_sha256,
                      'posePacketSha256': args.poses_sha256, 'out': args.out.relative_to(ROOT).as_posix()}, indent=2))


main()
