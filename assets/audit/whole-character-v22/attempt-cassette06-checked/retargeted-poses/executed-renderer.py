"""Illustrate V21 packet rotations on V22 native rest translations only.

This is a read-only Blender render aid. It never copies packet world translations
into the candidate and never saves the native scene.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import math
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parents[1]
PACKET_GLB_SHA = '9ea5fad537369340fada9d4ae8c0110475f97d5f4bf71e70decbc704f6ae082d'
CONVERSION = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))
POSE_IDS = (
    'runtime-rest',
    'maker-neck-control',
    'maker-neck-and-jaw-combined',
    'advanced-attention',
    'advanced-contact',
    'advanced-recovery-entry',
    'advanced-thrust-brace',
)
WHOLE_CAMERA = Vector((-3.6, -4.2, 2.65))
WHOLE_TARGET = Vector((0.0, -0.10, 0.94))
NECK_CAMERA = Vector((-1.55, -2.35, 1.95))
NECK_TARGET = Vector((0.0, -0.225, 1.46))


def parse_args():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--native', required=True)
    parser.add_argument('--native-sha256', required=True)
    parser.add_argument('--poses', required=True)
    parser.add_argument('--poses-sha256', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--verify-only', action='store_true',
                        help='Apply and verify the packet poses without rendering images')
    args = parser.parse_args(argv)
    for key in ('native', 'poses', 'out'):
        path = Path(getattr(args, key))
        assert not path.is_absolute(), f'--{key} must be repository-relative'
        resolved = (ROOT / path).resolve()
        assert resolved == ROOT or ROOT in resolved.parents, f'--{key} escapes repository'
        setattr(args, key, resolved)
    return args


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def artifact(path):
    path = Path(path)
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'bytes': path.stat().st_size}


def matrix_from_three_flat(flat):
    return Matrix([[float(flat[col * 4 + row]) for col in range(4)] for row in range(4)])


def native_local_quaternion(row):
    # The packet matrix is THREE/glTF owner-local. Conjugate its rotation through
    # native->browser C; never read/use row['worldMatrix'] or its translation.
    browser_local = matrix_from_three_flat(row['localMatrix'])
    browser_rotation = browser_local.to_3x3().to_4x4()
    native_rotation = CONVERSION.inverted() @ browser_rotation @ CONVERSION
    return native_rotation.to_quaternion().normalized()


def axis_conversion_witnesses():
    # Independent unit-axis checks: browser X->native X, browser Y->native Z,
    # browser Z->native -Y, then verify conjugated rotations at a nontrivial angle.
    expected = {
        'browser-x': Vector((1, 0, 0)),
        'browser-y': Vector((0, 0, 1)),
        'browser-z': Vector((0, -1, 0)),
    }
    out = []
    angle = 0.371
    for label, browser_axis in [('browser-x', Vector((1, 0, 0))),
                                ('browser-y', Vector((0, 1, 0))),
                                ('browser-z', Vector((0, 0, 1)))]:
        native_axis = (CONVERSION.inverted() @ Vector((browser_axis.x, browser_axis.y, browser_axis.z, 0))).to_3d()
        assert (native_axis - expected[label]).length < 1e-9, (label, native_axis)
        browser_rot = Matrix.Rotation(angle, 4, browser_axis)
        native_rot = CONVERSION.inverted() @ browser_rot @ CONVERSION
        expected_rot = Matrix.Rotation(angle, 4, native_axis)
        error = max(abs(native_rot[r][c] - expected_rot[r][c]) for r in range(4) for c in range(4))
        assert error < 1e-8, (label, error)
        out.append({'browserAxis': label, 'mappedNativeAxis': list(native_axis), 'testAngleRadians': angle, 'rotationMatrixMaxError': error})
    return out


def depth(obj):
    n, cursor = 0, obj
    while cursor.parent:
        n += 1
        cursor = cursor.parent
    return n


def matrix_error(a, b):
    return max(abs(float(a[r][c]) - float(b[r][c])) for r in range(4) for c in range(4))


def clear_animations_in_memory():
    cleared = []
    for obj in bpy.data.objects:
        if obj.animation_data is not None:
            obj.animation_data_clear()
            cleared.append('object:' + obj.name)
        data = getattr(obj, 'data', None)
        if data is not None and getattr(data, 'animation_data', None) is not None:
            data.animation_data_clear()
            cleared.append('data:' + data.name)
    if bpy.context.scene.animation_data is not None:
        bpy.context.scene.animation_data_clear()
        cleared.append('scene:' + bpy.context.scene.name)
    return cleared


def rows_for_pose(pose):
    rows = {}
    for row in pose['pivotMatrices']:
        if row.get('kind') != 'transform':
            continue
        if row['name'] in rows:
            raise RuntimeError(f"Ambiguous transform row: {pose['id']}:{row['name']}")
        rows[row['name']] = row
    return rows


def q_from_obj_local(obj):
    return obj.matrix_local.to_quaternion().normalized()


def set_obj_local_quaternion(obj, desired_local_q):
    # matrix_local = matrix_parent_inverse * matrix_basis. Compensate for an
    # authored parent inverse while leaving object location and scale untouched.
    parent_inverse_q = obj.matrix_parent_inverse.to_3x3().to_quaternion().normalized()
    basis_q = (parent_inverse_q.inverted() @ desired_local_q).normalized()
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = basis_q


def install_half_followers(pivots, rows, rest_joint_quaternions, follower_specs, rest_cover_quaternions):
    records = []
    for cover_name, parent_name, joint_name in follower_specs:
        cover = bpy.data.objects.get(cover_name)
        if cover is None:
            records.append({'name': cover_name, 'status': 'optional cover absent from this native'})
            continue
        if cover.parent is None or cover.parent.name != parent_name:
            raise RuntimeError(f'{cover_name} expected parent {parent_name}, found {cover.parent.name if cover.parent else None}')
        if joint_name not in rows or joint_name not in rest_joint_quaternions:
            raise RuntimeError(f'Missing joint row for half follower: {joint_name}')
        rest_joint_q = rest_joint_quaternions[joint_name].copy()
        current_joint_q = native_local_quaternion(rows[joint_name])
        delta_q = (current_joint_q @ rest_joint_q.inverted()).normalized()
        rest_cover_q = rest_cover_quaternions[cover_name].copy().normalized()
        half_delta = Quaternion().slerp(delta_q, 0.5)
        desired_cover_q = (half_delta @ rest_cover_q).normalized()
        set_obj_local_quaternion(cover, desired_cover_q)
        records.append({
            'name': cover_name, 'parent': parent_name, 'relativeJoint': joint_name,
            'status': 'half-relative follower applied in memory',
            'restJointQuaternionNative': list(rest_joint_q),
            'currentJointQuaternionNative': list(current_joint_q),
            'deltaQuaternionNative': list(delta_q),
            'restCoverQuaternionNative': list(rest_cover_q),
            'appliedCoverLocalQuaternionNative': list(desired_cover_q),
            'appliedCoverLocalMatrixNative': [[float(cover.matrix_local[r][c]) for c in range(4)] for r in range(4)],
            'formula': 'slerp(identity, currentJointQ * inverse(restJointQ), 0.5) * restCoverQ',
        })
    return records


def configure_scene(scene):
    scene.render.engine = 'BLENDER_WORKBENCH'
    shade = scene.display.shading
    shade.light = 'STUDIO'
    shade.studio_light = 'paint.sl'
    shade.color_type = 'SINGLE'
    shade.single_color = (.53, .56, .58)
    shade.show_shadows = False
    shade.show_cavity = True
    shade.cavity_type = 'BOTH'
    shade.curvature_ridge_factor = 1.15
    shade.curvature_valley_factor = 1.0
    shade.background_type = 'WORLD'
    scene.world.color = (.12, .13, .14)
    scene.render.resolution_x = 900
    scene.render.resolution_y = 760
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.film_transparent = False


def look_at(camera, position, target):
    camera.location = position
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def create_camera(scene):
    data = bpy.data.cameras.new('V22 runtime-envelope temporary camera')
    data.type = 'ORTHO'
    data.ortho_scale = 2.7
    data.lens = 70
    data.clip_start, data.clip_end = .01, 100
    obj = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(obj)
    return obj


def make_floor(scene):
    mesh = bpy.data.meshes.new('V22 temporary native Z0 floor mesh')
    mesh.from_pydata([(-30, -30, 0), (30, -30, 0), (30, 30, 0), (-30, 30, 0)], [], [(0, 1, 2, 3)])
    mesh.update()
    floor = bpy.data.objects.new('V22 temporary native Z0 floor', mesh)
    floor.hide_select = True
    scene.collection.objects.link(floor)
    return floor


def visible_meshes():
    return [o for o in bpy.data.objects if o.type == 'MESH' and not o.hide_render]


def render_one(scene, camera, out_file, camera_kind):
    if camera_kind == 'whole':
        look_at(camera, WHOLE_CAMERA, WHOLE_TARGET)
        camera.data.ortho_scale = 2.75
    elif camera_kind == 'whole-right':
        look_at(camera, Vector((3.6, -4.2, 2.65)), WHOLE_TARGET)
        camera.data.ortho_scale = 2.75
    elif camera_kind == 'neck':
        look_at(camera, NECK_CAMERA, NECK_TARGET)
        camera.data.ortho_scale = 1.2
    scene.camera = camera
    bpy.context.view_layer.update()
    scene.render.filepath = str(out_file)
    bpy.ops.render.render(write_still=True)


def main():
    args = parse_args()
    if not args.native.is_file() or sha(args.native) != args.native_sha256:
        raise RuntimeError('Pinned native missing or hash mismatch')
    if not args.poses.is_file() or sha(args.poses) != args.poses_sha256:
        raise RuntimeError('Pinned pose packet missing or hash mismatch')
    packet = json.loads(args.poses.read_text())
    if packet.get('model', {}).get('sha256') != PACKET_GLB_SHA:
        raise RuntimeError('Pose packet source GLB hash mismatch')
    if args.out.exists():
        raise RuntimeError('Refusing to overwrite output directory: ' + str(args.out))
    poses = {p['id']: p for p in packet['poses']}
    missing_pose_ids = sorted(set(POSE_IDS) - set(poses))
    if missing_pose_ids:
        raise RuntimeError('Required packet poses missing: ' + ', '.join(missing_pose_ids))
    bpy.ops.wm.open_mainfile(filepath=str(args.native))
    scene = bpy.context.scene
    cleared_animations = clear_animations_in_memory()
    pivots = {o.name: o for o in bpy.data.objects if o.type == 'EMPTY'}
    packet_rest_rows = rows_for_pose(poses['runtime-rest'])
    derived_cover_names = {'cervical-root-cover', 'cervical-skull-cover'}
    if derived_cover_names & set(packet_rest_rows):
        raise RuntimeError('Derived V22 cover owners unexpectedly appear in the V21 pose packet')
    packet_pivots = {name: obj for name, obj in pivots.items() if name in packet_rest_rows}
    packetless = set(pivots) - set(packet_pivots)
    packet_only_rows = sorted(set(packet_rest_rows) - set(pivots))
    unexpected_packetless = sorted(packetless - derived_cover_names)
    if unexpected_packetless:
        raise RuntimeError('Pose packet missing unexplained native pivot rows: ' + ', '.join(unexpected_packetless))
    if len(packet_pivots) != 53:
        raise RuntimeError(f'Expected all 53 original native pivots in the packet, found {len(packet_pivots)}')
    for pose_id in POSE_IDS:
        rows = rows_for_pose(poses[pose_id])
        missing = sorted(set(packet_pivots) - set(rows))
        if missing:
            raise RuntimeError(f'{pose_id} lacks packet-driven native pivots: {missing}')
        packet_only = sorted(set(rows) - set(pivots))
        if packet_only != packet_only_rows:
            raise RuntimeError(f'{pose_id} packet-only runtime transform set differs from runtime-rest')

    follower_specs = (
        ('cervical-root-cover', 'body', 'neck'),
        ('cervical-joint-cover', 'neck', 'cervical-upper'),
        ('cervical-skull-cover', 'cervical-upper', 'head'),
    )
    follower_center_errors = {}
    for cover_name, parent_name, joint_name in follower_specs:
        cover = bpy.data.objects.get(cover_name)
        if cover is None:
            continue
        if cover.type != 'EMPTY':
            raise RuntimeError(f'{cover_name} must be an EMPTY owner transform, got {cover.type}')
        if cover.parent is None or cover.parent.name != parent_name:
            raise RuntimeError(f'{cover_name} expected parent {parent_name}, found {cover.parent.name if cover.parent else None}')
        joint = pivots.get(joint_name)
        if joint is None or joint.parent is None or joint.parent.name != parent_name:
            raise RuntimeError(f'{joint_name} must be a native pivot parented to {parent_name}')
        error = (cover.matrix_local.translation - joint.matrix_local.translation).length
        follower_center_errors[cover_name] = float(error)
        if error > 1e-5:
            raise RuntimeError(f'{cover_name} center differs from {joint_name} by {error:.9g}m')

    # Check the model's rest rotations against the packet rest rotations before
    # any pose application; the V22 native is expected to preserve those bases.
    rest_joint_quaternions = {name: q_from_obj_local(obj) for name, obj in packet_pivots.items()}
    rest_rotation_errors = {}
    for name, obj in packet_pivots.items():
        packet_q = native_local_quaternion(packet_rest_rows[name])
        native_q = q_from_obj_local(obj)
        rest_rotation_errors[name] = min((packet_q.rotation_difference(native_q).angle,
                                          packet_q.rotation_difference(-native_q).angle))

    original_local_positions = {name: tuple(obj.location) for name, obj in pivots.items()}
    original_local_scales = {name: tuple(obj.scale) for name, obj in pivots.items()}
    follower_base_quaternions = {
        name: bpy.data.objects[name].matrix_local.to_quaternion().normalized()
        for name, _, _ in follower_specs if bpy.data.objects.get(name) is not None
    }

    args.out.mkdir(parents=True, exist_ok=False)
    configure_scene(scene)
    camera = create_camera(scene)
    floor = make_floor(scene)
    curve_hidden = [o.name for o in bpy.data.objects if o.type == 'CURVE' and o.hide_render]
    outputs = []
    pose_records = []
    render_plan = [
        ('runtime-rest', 'whole'),
        ('maker-neck-control', 'whole'),
        ('maker-neck-and-jaw-combined', 'neck'),
        ('advanced-attention', 'whole'),
        ('advanced-attention', 'whole-right'),
        ('advanced-contact', 'neck'),
        ('advanced-recovery-entry', 'whole'),
        ('advanced-thrust-brace', 'neck'),
    ]

    for pose_id in POSE_IDS:
        pose = poses[pose_id]
        rows = rows_for_pose(pose)
        for name in sorted(packet_pivots, key=lambda n: depth(packet_pivots[n])):
            obj = packet_pivots[name]
            q = native_local_quaternion(rows[name])
            set_obj_local_quaternion(obj, q)
        bpy.context.view_layer.update()
        follower_records = install_half_followers(pivots, rows, rest_joint_quaternions, follower_specs, follower_base_quaternions)
        bpy.context.view_layer.update()

        expected_pivot_quaternions = {name: native_local_quaternion(rows[name]) for name in packet_pivots}
        for follower in follower_records:
            if follower.get('status') == 'half-relative follower applied in memory':
                expected_pivot_quaternions[follower['name']] = Quaternion(follower['appliedCoverLocalQuaternionNative'])

        # Candidate local positions and scales must remain exactly their V22 rest
        # values; no world/local translation from the source packet is applied.
        position_error = max((Vector(obj.location) - Vector(original_local_positions[name])).length for name, obj in pivots.items())
        scale_error = max((Vector(obj.scale) - Vector(original_local_scales[name])).length for name, obj in pivots.items())
        if position_error > 1e-8 or scale_error > 1e-8:
            raise RuntimeError(f'{pose_id} altered native rest position/scale: {position_error}, {scale_error}')

        applied_rows = []
        for name, obj in sorted(packet_pivots.items()):
            expected_q = expected_pivot_quaternions[name]
            actual_q = obj.matrix_local.to_quaternion().normalized()
            err = min(expected_q.rotation_difference(actual_q).angle,
                      expected_q.rotation_difference(-actual_q).angle)
            applied_rows.append({
                'name': name,
                'candidateLocalPositionNative': list(original_local_positions[name]),
                'packetLocalQuaternionNative': list(expected_q),
                'actualLocalMatrixNative': [[float(obj.matrix_local[r][c]) for c in range(4)] for r in range(4)],
                'rotationErrorRadians': float(err),
            })

        # Temporary skin plates follow the half relative joint rotation, with
        # each cover's own authored rest quaternion retained.
        for cover_name, _, joint_name in follower_specs:
            cover = bpy.data.objects.get(cover_name)
            if cover is None:
                continue
            follower = next(rec for rec in follower_records if rec['name'] == cover_name)
            if follower['status'] == 'half-relative follower applied in memory':
                expected_cover_q = Quaternion(follower['appliedCoverLocalQuaternionNative'])
                actual_cover_q = cover.matrix_local.to_quaternion().normalized()
                follower['postApplyLocalRotationErrorRadians'] = min(
                    expected_cover_q.rotation_difference(actual_cover_q).angle,
                    expected_cover_q.rotation_difference(-actual_cover_q).angle)
                follower['postApplyLocalPositionNative'] = list(cover.matrix_local.translation)

        applied_max_error = max(r['rotationErrorRadians'] for r in applied_rows)
        if applied_max_error > 2e-6:
            raise RuntimeError(f'{pose_id} local-rotation application error {applied_max_error}')
        post_apply_rotation_errors = []
        for name, expected in expected_pivot_quaternions.items():
            obj = pivots[name]
            actual = obj.matrix_local.to_quaternion().normalized()
            post_apply_rotation_errors.append(min(expected.rotation_difference(actual).angle,
                                                  expected.rotation_difference(-actual).angle))
        if max(post_apply_rotation_errors, default=0.0) > 2e-6:
            raise RuntimeError(f'{pose_id} post-application rotation error {max(post_apply_rotation_errors)}')
        outputs_for_pose = []
        pose_slug = pose_id.replace('.', '-')
        for camera_kind in [kind for pid, kind in render_plan if pid == pose_id]:
            if args.verify_only:
                continue
            filename = f'{pose_slug}-{camera_kind}.png'
            filepath = args.out / filename
            render_one(scene, camera, filepath, camera_kind)
            if not filepath.is_file() or filepath.stat().st_size == 0:
                raise RuntimeError('Render missing or empty: ' + str(filepath))
            rec = {'camera': camera_kind, 'image': artifact(filepath), 'candidateRestLocalPositionMaxErrorM': float(position_error)}
            outputs.append(rec)
            outputs_for_pose.append(rec)

        # Recheck all sampled pivots and derived followers after image rendering
        # (or verify-only pose evaluation), catching animation reapplication.
        post_location_error = max((Vector(obj.location) - Vector(original_local_positions[name])).length for name, obj in pivots.items())
        if post_location_error > 1e-8:
            raise RuntimeError(f'{pose_id} evaluation changed native pivot local position {post_location_error}')
        post_evaluation_rotation_errors = []
        for name, expected in expected_pivot_quaternions.items():
            obj = pivots[name]
            actual = obj.matrix_local.to_quaternion().normalized()
            error = min(expected.rotation_difference(actual).angle,
                        expected.rotation_difference(-actual).angle)
            post_evaluation_rotation_errors.append(error)
            for follower in follower_records:
                if follower.get('name') == name and follower.get('status') == 'half-relative follower applied in memory':
                    follower['postEvaluationLocalRotationErrorRadians'] = float(error)
                    follower['postEvaluationLocalMatrixNative'] = [[float(obj.matrix_local[r][c]) for c in range(4)] for r in range(4)]
        post_evaluation_max_error = max(post_evaluation_rotation_errors, default=0.0)
        if post_evaluation_max_error > 2e-6:
            raise RuntimeError(f'{pose_id} post-render/evaluation rotation error {post_evaluation_max_error}')
        for render_record in outputs_for_pose:
            render_record['pivotAndFollowerLocalRotationMaxErrorRadiansPostRender'] = float(post_evaluation_max_error)
        pose_records.append({
            'poseId': pose_id,
            'category': pose.get('category'),
            'elapsedSeconds': pose.get('elapsedSeconds'),
            'controllerState': pose.get('controller'),
            'motionMetrics': pose.get('motionMetrics'),
            'appliedPivotCount': len(applied_rows),
            'nativeEmptyCount': len(pivots),
            'packetlessDerivedFollowerNames': sorted(packetless),
            'packetOnlyRuntimeTransformNames': packet_only_rows,
            'appliedPivots': applied_rows,
            'halfFollowerCovers': follower_records,
            'maxLocalRotationErrorRadians': applied_max_error,
            'maxPostRenderLocalRotationErrorRadians': post_evaluation_max_error,
            'maxPoseEvaluationLocalRotationErrorRadians': post_evaluation_max_error,
            'nativeRestLocalPositionMaxErrorM': float(max(position_error, post_location_error)),
            'nativeRestLocalScaleMaxError': float(scale_error),
            'renders': outputs_for_pose,
        })

    receipt = {
        'status': 'retargeted native illustration only; not live V22 runtime, motion simulation, collision/clearance, or acceptance',
        'generatedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'inputs': {'native': artifact(args.native), 'posePacket': artifact(args.poses), 'packetSourceModel': packet['model']},
        'source': {'path': Path(__file__).resolve().relative_to(ROOT).as_posix(), 'sha256': sha(Path(__file__))},
        'conversion': {
            'nativeToBrowser': 'browser (x,y,z) = native (x,z,-y)',
            'rotationRetarget': 'C^-1 * packet localMatrix rotation * C; packet worldMatrix and packet translations are never used',
            'axisRotationWitnesses': axis_conversion_witnesses(),
            'candidateTranslationRule': 'Keep each V22 EMPTY location and scale from the reopened native; apply packet local quaternions only to packet-driven pivots and derive optional root/skull cover rotations from their matching joint-relative follower convention.',
            'nativeAuthoredRestVsPacketRuntimeSampleRotationDeltasRadians': {
                'max': max(rest_rotation_errors.values(), default=0.0),
                'largest': sorted([{'name': n, 'deltaRadians': e} for n, e in rest_rotation_errors.items()], key=lambda r:r['deltaRadians'], reverse=True)[:8],
                'interpretation': 'The packet runtime-rest state is an actual sampled runtime pose and includes IK/attention rotations; this is a difference from the V22 authored local rest basis, not an application error.',
            },
        },
        'animationDataClearedInMemory': cleared_animations,
        'nativeEmptyCount': len(pivots),
        'packetDrivenPivotCount': len(packet_pivots),
        'packetTransformRowsWithoutNativeEmpty': packet_only_rows,
        'packetlessDerivedFollowerNames': sorted(packetless),
        'followerCenterErrorsM': follower_center_errors,
        'curveObjectsAlreadyHiddenFromRender': curve_hidden,
        'renderLabel': 'Native V22 geometry with retargeted V21 pose rotations and V22 rest translations; source packet contains the 37 actual sampled runtime states, but this is not a V22 runtime execution.',
        'halfFollowerConvention': 'delta = currentJointQ * inverse(restJointQ) in shared parent axes; coverQ = slerp(identity, delta, 0.5) * restCoverQ. Optional newer cover objects are handled only when present.',
        'poses': pose_records,
        'images': outputs,
        'plannedImageCount': len(render_plan),
        'verificationOnlyNoImagesRendered': bool(args.verify_only),
        'limits': [
            'Pose packet was sampled from the V21 GLB; only local rotations are transferred to the V22 native, and rest translations intentionally remain V22-specific.',
            'New cover follower rotations are derived from corresponding joint-relative packet quaternions; this is an illustration convention, not proof of constructed hinge behavior.',
            'All native geometry is rendered together without runtime era visibility filtering.',
            'No scene is saved; no GLB, browser session, physical simulation, contact, swept clearance, or artistic acceptance is established.',
        ],
    }
    receipt_path = args.out / 'receipt.json'
    with receipt_path.open('x') as f:
        json.dump(receipt, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps({'out': str(args.out), 'imageCount': len(outputs), 'plannedImageCount': len(render_plan), 'receipt': artifact(receipt_path), 'maxNativeLocalRotationApplicationErrorRadians': max(p['maxLocalRotationErrorRadians'] for p in pose_records), 'maxPostRenderRotationErrorRadians': max(p['maxPostRenderLocalRotationErrorRadians'] for p in pose_records), 'poseIds': list(POSE_IDS)}, indent=2))


main()
