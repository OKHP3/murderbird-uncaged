"""Discrete owner-scoped surface screen for the V18 passive leg additions."""
from pathlib import Path
import hashlib, json, runpy
import bpy
from mathutils import Matrix
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[4]
NATIVE = ROOT / 'assets/models/whole-character-v18/attempt-leg-envelope06/murderbird-whole-character-v18.blend'
PACKET = ROOT / 'assets/audit/whole-character-v17/attempt-02/runtime-poses/pose-snapshot.json'
KERNEL = ROOT / 'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'
OUT = Path(__file__).resolve().parent / 'clearance'
NATIVE_SHA = '91ad0aa3dee8c31e2e52015771cd6a2da7a2a9994b8a5a8bf9aceb6e11f0608c'
PACKET_SHA = '1964918661da857878376ff95457f3b8e0bc73479bd83225a8419fb1e2a627f9'
C = Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
SUBJECTS = [name for side in ('left','right') for name in (
    f'V18 {side} split shin load web', f'V18 {side} ankle-to-foot-root yoke',
    f'{side.title()} metatarsus open passive truss')]
JOINTS = ('thigh','shin','foot','toes')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def converted(flat):
    return C.inverted() @ Matrix([[flat[col*4+row] for col in range(4)] for row in range(4)]) @ C


def depth(obj):
    return 0 if obj.parent is None else 1 + depth(obj.parent)


def world_surface(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        faces = [tuple(t.vertices) for t in mesh.loop_triangles]
        return {'tree': BVHTree.FromPolygons(points, faces, all_triangles=True, epsilon=0.0),
                'points': points, 'faces': faces}
    finally:
        evaluated.to_mesh_clear()


assert sha(NATIVE) == NATIVE_SHA, 'candidate native hash mismatch'
assert sha(PACKET) == PACKET_SHA, 'runtime pose packet hash mismatch'
kernel_sha = sha(KERNEL)
proper_crossing_receipt = runpy.run_path(str(KERNEL))['proper_crossing_receipt']
pose_data = json.loads(PACKET.read_text())
pose_by_id = {pose['id']: pose for pose in pose_data['poses']}
assert len(pose_by_id) == 21, f"expected pinned 21-pose packet, got {len(pose_by_id)}"
assert pose_data['model']['sha256'] == '52980d9578d985737dfe7595515be494d9b1bcfa2dc17d960f18ac6f6fe6049e'
claw_packet_path = ROOT / 'assets/audit/whole-character-v18/attempt-leg-envelope05/clearance/claw-pose-snapshot.json'
claw_data = json.loads(claw_packet_path.read_text())
claw_by_id = {pose['id']: pose for pose in claw_data['poses'] if pose['id'].startswith('advanced-claw-')}
assert len(claw_by_id) == 6, f"expected six claw stages, got {len(claw_by_id)}"

bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
scene = bpy.context.scene; scene.frame_set(1); bpy.context.view_layer.update()
pivots = {obj.name: obj for obj in bpy.data.objects if obj.type == 'EMPTY'}
assert len(pivots) == 52, f'expected 52 native pivots; found {len(pivots)}'
mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
subject_objects = {name: bpy.data.objects.get(name) for name in SUBJECTS}
assert all(subject_objects.values()), 'one or more V18 subject meshes are missing'
rest_mesh_world = {obj.name: obj.matrix_world.copy() for obj in mesh_objects}

rest_pose_id = 'inspection-open-0-separation-0'
rest_rows = {row['name']: row for row in pose_by_id[rest_pose_id]['pivotMatrices'] if row.get('kind') != 'mesh'}
assert len(rest_rows) >= 52 and set(pivots) <= set(rest_rows)
rest_world = {name: obj.matrix_world.copy() for name, obj in pivots.items()}
rest_error = max(abs(rest_world[n][r][c] - converted(rest_rows[n]['worldMatrix'])[r][c])
                 for n in pivots for r in range(4) for c in range(4))
assert rest_error < 2e-6, f'candidate rest and runtime packet differ: {rest_error}'


def apply_pose(pose):
    rows = {row['name']: row for row in pose['pivotMatrices'] if row.get('kind') != 'mesh'}
    assert set(pivots) <= set(rows), f"{pose['id']}: missing pivots"
    for name in sorted(pivots, key=lambda n: depth(pivots[n])):
        pivots[name].matrix_world = converted(rows[name]['worldMatrix'])
        bpy.context.view_layer.update()
    error = max(abs(pivots[n].matrix_world[r][c] - converted(rows[n]['worldMatrix'])[r][c])
                for n in pivots for r in range(4) for c in range(4))
    assert error < 2e-6, f"{pose['id']}: matrix replay mismatch {error}"
    return error


def owner_joint(obj):
    return obj.parent.name if obj.parent else ''


def scoped_targets(subject):
    side = 'left' if subject.name.startswith(('V18 left','Left')) else 'right'
    allowed = {f'{side}-{joint}' for joint in JOINTS}
    return [target for target in mesh_objects if target is not subject and target.parent
            and target.parent.name in allowed]


pose_inputs = list(pose_by_id.values()) + [claw_by_id['advanced-claw-' + stage]
    for stage in ('approach','lift','contact','scrape','release','recovery')]
rows = []
for pose in pose_inputs:
    matrix_error = apply_pose(pose)
    surfaces = {obj.name: world_surface(obj) for obj in subject_objects.values()}
    pair_rows = []
    for subject in subject_objects.values():
        a = surfaces[subject.name]
        for target in scoped_targets(subject):
            b = world_surface(target)
            overlaps = a['tree'].overlap(b['tree'])
            if not overlaps:
                continue
            proof = proper_crossing_receipt(a, b, overlaps, Matrix.Identity(4), Matrix.Identity(4))
            proof['subjectPoseWorldNativeXYZBounds'] = proof.pop('subjectCrossingRestWorldBoundsNativeXYZ')
            proof['targetPoseWorldNativeXYZBounds'] = proof.pop('targetCrossingRestWorldBoundsNativeXYZ')
            for example in proof['examples']:
                example['subjectPoseWorldNativeXYZ'] = example.pop('subjectRestWorldNativeXYZ')
                example['targetPoseWorldNativeXYZ'] = example.pop('targetRestWorldNativeXYZ')
            pair_rows.append({'subject': subject.name, 'target': target.name,
                'subjectOwner': owner_joint(subject), 'targetOwner': owner_joint(target),
                'category': 'same-rigid-owner-fit' if owner_joint(subject) == owner_joint(target) else 'adjacent-owner',
                'triangleOverlapCandidates': len(overlaps), 'strictProperCrossing': proof})
    rows.append({'poseId': pose['id'], 'poseCategory': pose.get('category'),
                 'runtimeMatrixMaxError': matrix_error, 'overlapPairs': pair_rows})

OUT.mkdir(exist_ok=True)
result = {
    'status': 'Discrete evaluated-surface screen only; not continuous clearance, containment, load, or physical-guide proof.',
    'native': {'path': str(NATIVE.relative_to(ROOT)), 'sha256': sha(NATIVE)},
    'baseNative': {'path':'assets/models/whole-character-v17/attempt-02/murderbird-whole-character-v17.blend',
                   'sha256':'7d371907b279eb3d625e67164d84a78b2901a5cb6a79917def07f48ff8792d7b'},
    'runtimePacket': {'path':str(PACKET.relative_to(ROOT)), 'sha256':sha(PACKET), 'poseCount':len(pose_by_id),
                      'modelSha256':pose_data['model']['sha256']},
    'clawPacket': {'path':str(claw_packet_path.relative_to(ROOT)),'sha256':sha(claw_packet_path),
                   'modelSha256':claw_data['model']['sha256'], 'stages':sorted(claw_by_id)},
    'kernel': {'path':str(KERNEL.relative_to(ROOT)), 'sha256':kernel_sha,
               'method':'Frozen proper_crossing_receipt: strict noncoplanar edge-through-face crossings only; tangent/coplanar excluded.'},
    'scope': {'subjects':SUBJECTS, 'adjacentOwnerMeshes':'same-side thigh, shin, foot, toes; all other owners excluded',
              'sameOwnerCrossings':'reported separately as fixed-fit evidence, not silently accepted mating contacts',
              'pivots':len(pivots), 'restMatrixMaxError':rest_error,
              'poseCoverage':'21 pinned runtime poses plus six claw-action stages generated from the same V17 GLB',
              'crossingLocations':'Strict-kernel triangle examples and bounds are reported in the evaluated sample pose world frame.'},
    'rows':rows,
}
(OUT/'leg-clearance.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({'poses':len(rows),
    'strictPairRows':sum(bool(p['strictProperCrossing']['examples']) for r in rows for p in r['overlapPairs']),
    'overlapPairRows':sum(len(r['overlapPairs']) for r in rows),'out':str(OUT/'leg-clearance.json')}))
