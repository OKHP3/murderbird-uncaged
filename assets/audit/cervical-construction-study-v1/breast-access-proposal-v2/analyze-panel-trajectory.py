"""Read-only, staged panel-only clearance screen for proposed V4 actuator."""
from pathlib import Path
import hashlib, json, math
import bpy
from mathutils import Matrix, Vector, Euler
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
NATIVE = ROOT / 'assets/models/uncaged-cervical-construction-study-v1/attempt-07/murderbird-cervical-construction-study-v1.blend'
POSES = ROOT / 'assets/audit/cervical-runtime-study-v1/expanded-runtime-poses/pose-snapshot.json'
MOUNTS = ROOT / 'assets/audit/cervical-construction-study-v1/attempt-07/control-mount-proposal-v4/mounting-neighborhoods.json'
EXPECTED_NATIVE = '751d8149032941774c6ba31824c76f6fa840bb0d767e433bae8000535f3a2b98'
EXPECTED_POSES = '1cb4a2f75ecae625a44c768ba543e9b99e1caa9791a3056e20f5d88bd73d2f26'
EXPECTED_GLTF = '5736ca592c5ebfa7da78315b136b53ad6a48050ede66f6d60b9ccf860afa8ecf'
EXPECTED_MOUNTS = '9957fefb1edbcbc1d9cc65d6c73f234a4eb33c327189f61664e0ff3dfb272c85'
POSE_OUTPUT = OUT / 'panel-trajectory-clearance.json'
if POSE_OUTPUT.exists():
    raise RuntimeError(f'Refusing to overwrite {POSE_OUTPUT}')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rt_matrix(flat):
    return Matrix([[flat[col * 4 + row] for col in range(4)] for row in range(4)])


def blender_matrix_from_runtime(m):
    # Same Blender-to-runtime basis conversion bound in the pose packet.
    c = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))
    return c.inverted() @ m @ c


def descendants_of(obj, ancestor):
    current = obj
    while current is not None:
        if current == ancestor:
            return True
        current = current.parent
    return False


def nearest_named_owner(obj, names):
    current = obj.parent
    while current is not None:
        if current.name in names:
            return current.name
        current = current.parent
    return None


def build_bvh(objects):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    verts, faces, face_objects = [], [], []
    per_object = {}
    for obj in objects:
        ev = obj.evaluated_get(depsgraph)
        mesh = ev.to_mesh()
        mesh.calc_loop_triangles()
        start = len(verts)
        verts.extend(ev.matrix_world @ v.co for v in mesh.vertices)
        obj_face_count = len(mesh.loop_triangles)
        faces.extend(tuple(start + i for i in tri.vertices) for tri in mesh.loop_triangles)
        face_objects.extend([obj.name] * obj_face_count)
        per_object[obj.name] = {'vertices': len(mesh.vertices), 'triangles': obj_face_count}
        ev.to_mesh_clear()
    if not faces:
        raise RuntimeError('Cannot build BVH from empty mesh collection')
    return BVHTree.FromPolygons(verts, faces, all_triangles=True), verts, faces, face_objects, per_object


def build_transformed_bvh(rest_verts, faces, face_objects, delta):
    verts = [delta @ v for v in rest_verts]
    return BVHTree.FromPolygons(verts, faces, all_triangles=True), verts


def segment_to_tree(tree, a, b, n=17):
    length = (b - a).length
    best = {'sampleDistanceM': float('inf'), 'sampleIndex': None, 'nearestTriangle': None,
            'samplePoint': None, 'nearestPoint': None}
    for i in range(n):
        p = a.lerp(b, i / (n - 1))
        hit = tree.find_nearest(p)
        if hit[0] is not None and hit[3] < best['sampleDistanceM']:
            best = {'sampleDistanceM': hit[3], 'sampleIndex': i,
                    'nearestTriangle': hit[2], 'samplePoint': list(p),
                    'nearestPoint': list(hit[0])}
    half_step = length / (n - 1) / 2
    lower = best['sampleDistanceM'] - half_step
    return {**best, 'segmentLengthM': length, 'sampleCount': n,
            'halfSampleStepM': half_step, 'conservativeCenterlineLowerBoundM': lower,
            'conservative12mmHousingMarginM': lower - 0.012,
            'sampled12mmHousingMarginM': best['sampleDistanceM'] - 0.012}


def pose_specs():
    for i in range(101):
        t = i / 100
        if t <= 1 / 3:
            q = t * 3
            stage, progress = 'A', q
            angle, slide = -0.675 * q, 0.0
        elif t <= 2 / 3:
            q = (t - 1 / 3) * 3
            stage, progress = 'B', q
            angle, slide = -0.675, 0.5 * q
        else:
            q = (t - 2 / 3) * 3
            stage, progress = 'C', q
            angle, slide = -0.675 - 0.675 * q, 0.5
        yield {'routeIndex': i, 'routeProgress': t, 'stage': stage,
               'stageProgress': progress, 'timelineOpen': t,
               'runtimeOpenAngleRad': angle, 'panelSlideScalar': slide}


assert bpy.data.filepath and Path(bpy.data.filepath).resolve() == NATIVE.resolve(), 'Blender was not opened on the pinned attempt-07 native'
assert sha(NATIVE) == EXPECTED_NATIVE, 'Unexpected native hash'
assert sha(POSES) == EXPECTED_POSES, 'Unexpected pose packet hash'
assert sha(MOUNTS) == EXPECTED_MOUNTS, 'Unexpected V4 mount proposal hash'
pose_data = json.loads(POSES.read_text())
mount_data = json.loads(MOUNTS.read_text())
assert pose_data['model']['sha256'] == EXPECTED_GLTF and pose_data['poseCount'] == 21
rest_pose = next(p for p in pose_data['poses'] if p['id'] == 'runtime-rest')
rows = {r['name']: r for r in rest_pose['pivotMatrices'] if r.get('kind') != 'mesh'}
assert len(rows) == 67 and len([r for r in rows.values() if r['name'] not in {'Scene', 'murderbird'}]) == 65
for pid in ('inspection-open-0-separation-0', 'inspection-open-0.25-separation-0',
            'inspection-open-0.5-separation-0', 'inspection-open-0.75-separation-0',
            'inspection-open-1-separation-0', 'inspection-open-1-separation-0.5',
            'inspection-open-1-separation-1'):
    assert any(p['id'] == pid for p in pose_data['poses']), f'Missing pinned pose {pid}'

breast = bpy.data.objects['breastplate']
panel_meshes = sorted([o for o in bpy.data.objects if o.type == 'MESH' and descendants_of(o, breast)], key=lambda o:o.name)
assert panel_meshes, 'No breastplate assembly meshes were found'
TARGET_OWNERS = {'body', 'neck', 'cervical-upper', 'head', 'jaw', 'upper-bill',
                 'cranial-cover', 'builder-optics', 'processing', 'left-mantle',
                 'right-mantle', 'left-wing-shield', 'right-wing-shield'}
for owner in TARGET_OWNERS:
    assert owner in bpy.data.objects, f'Required stationary regional owner absent: {owner}'
stationary_by_owner = {owner: [] for owner in sorted(TARGET_OWNERS)}
excluded_stationary = []
for obj in bpy.data.objects:
    if obj.type != 'MESH' or descendants_of(obj, breast):
        continue
    owner = nearest_named_owner(obj, TARGET_OWNERS)
    if owner:
        stationary_by_owner[owner].append(obj)
    else:
        excluded_stationary.append(obj.name)
stationary_by_owner = {k:v for k,v in stationary_by_owner.items() if v}

depsgraph = bpy.context.evaluated_depsgraph_get()
panel_tree_rest, panel_verts_rest, panel_faces, panel_face_objects, panel_stats = build_bvh(panel_meshes)
static_trees, static_stats = {}, {}
for owner, objects in stationary_by_owner.items():
    static_trees[owner], _, _, _, stats = build_bvh(objects)
    static_stats[owner] = stats

rest_rows = {r['name']: r for r in rows.values()}
breast_world_rt = rt_matrix(rest_rows['breastplate']['worldMatrix'])
breast_local_rt = rt_matrix(rest_rows['breastplate']['localMatrix'])
parent_world_rt = rt_matrix(rest_rows['body']['worldMatrix'])
assert rest_rows['breastplate']['parent'] == 'body'
loc, quat, scale = breast_local_rt.decompose()
rest_euler = quat.to_euler('XYZ')
scale_matrix = Matrix.Diagonal((scale.x, scale.y, scale.z, 1.0))
body = bpy.data.objects['body']
native_rest_breast_local = blender_matrix_from_runtime(breast_local_rt)
matrix_err = max(abs(breast.matrix_local[r][c] - native_rest_breast_local[r][c]) for r in range(4) for c in range(4))
if matrix_err >= 2e-5:
    print('native breast local', [list(r) for r in breast.matrix_local])
    print('packet converted breast local', [list(r) for r in native_rest_breast_local])
    raise AssertionError(f'Native breastplate parent-local rest transform disagrees with pinned runtime transform ({matrix_err})')

mounts = mount_data['mounts']
upper_obj = bpy.data.objects[mounts['upper-horn-tip']['owner']]
lower_obj = bpy.data.objects[mounts['lower-drive-anchor']['owner']]
upper_a = upper_obj.matrix_world @ Vector(mounts['upper-horn-tip']['localNativeXYZ'])
lower_a = lower_obj.matrix_world @ Vector(mounts['lower-drive-anchor']['localNativeXYZ'])
for key, actual in [('upper-horn-tip', upper_a), ('lower-drive-anchor', lower_a)]:
    expected = Vector(mounts[key]['restWorldNativeXYZ'])
    assert (actual - expected).length < 2e-5, f'Pinned local mount conversion mismatch for {key}'

results = []
for spec in pose_specs():
    # Runtime inspection operates in browser coordinates. Set only the
    # breastplate-local translation/rotation and map its delta back into native
    # Blender coordinates; all other owners remain at the native rest pose.
    local_position = loc + Vector((-0.70, -0.12, 0.18)) * spec['panelSlideScalar']
    euler = Euler((rest_euler.x, spec['runtimeOpenAngleRad'], rest_euler.z), 'XYZ')
    rotation = euler.to_quaternion().to_matrix().to_4x4()
    local_new = Matrix.Translation(local_position) @ rotation @ scale_matrix
    local_delta_blender = blender_matrix_from_runtime(local_new @ breast_local_rt.inverted())
    # Native and exported packet roots use different common scene translations.
    # Apply the exact parent-local runtime delta around the actual native parent,
    # so the moving panel and stationary native owners share one world frame.
    parent_world_native = breast.parent.matrix_world.copy()
    delta_blender = parent_world_native @ local_delta_blender @ parent_world_native.inverted()
    panel_tree, moved_panel_verts = build_transformed_bvh(panel_verts_rest, panel_faces, panel_face_objects, delta_blender)
    clearance = segment_to_tree(panel_tree, lower_a, upper_a)
    hit_idx = clearance['nearestTriangle']
    clearance['nearestBreastMesh'] = panel_face_objects[hit_idx] if hit_idx is not None else None
    overlap_owners = {}
    for owner, target_tree in static_trees.items():
        pairs = panel_tree.overlap(target_tree)
        if pairs:
            overlap_owners[owner] = len(pairs)
    results.append({**spec, 'actuatorEnvelope': clearance,
                    'stationaryRegionalOverlapCandidates': overlap_owners,
                    'stationaryCandidatePairCount': sum(overlap_owners.values())})

stage_summaries = {}
for stage in ('A', 'B', 'C'):
    rows_stage = [r for r in results if r['stage'] == stage]
    best = min(rows_stage, key=lambda r:r['actuatorEnvelope']['conservative12mmHousingMarginM'])
    sampled_best = min(rows_stage, key=lambda r:r['actuatorEnvelope']['sampled12mmHousingMarginM'])
    stage_summaries[stage] = {
        'sampleCount': len(rows_stage),
        'minimumConservative12mmHousingMarginM': best['actuatorEnvelope']['conservative12mmHousingMarginM'],
        'minimumAt': {'routeIndex': best['routeIndex'], 'stageProgress': best['stageProgress'], 'timelineOpen': best['timelineOpen'],
                      'angleRad': best['runtimeOpenAngleRad'], 'slideScalar': best['panelSlideScalar'],
                      'nearestBreastMesh': best['actuatorEnvelope']['nearestBreastMesh'],
                      'sampledCenterlineDistanceM': best['actuatorEnvelope']['sampleDistanceM']},
        'minimumSampled12mmHousingMarginM': sampled_best['actuatorEnvelope']['sampled12mmHousingMarginM'],
        'minimumSampledAt': {'routeIndex': sampled_best['routeIndex'], 'stageProgress': sampled_best['stageProgress'],
                             'slideScalar': sampled_best['panelSlideScalar'],
                             'nearestBreastMesh': sampled_best['actuatorEnvelope']['nearestBreastMesh'],
                             'sampledCenterlineDistanceM': sampled_best['actuatorEnvelope']['sampleDistanceM']},
        'posesWithSampled12mmEnvelopeProximity': sum(r['actuatorEnvelope']['sampleDistanceM'] <= .012 for r in rows_stage),
        'posesWithConservative12mmBoundBelowZero': sum(r['actuatorEnvelope']['conservative12mmHousingMarginM'] < 0 for r in rows_stage),
        'stationaryRegionalOverlapCandidatePoseCount': sum(bool(r['stationaryRegionalOverlapCandidates']) for r in rows_stage),
        'stationaryRegionalOverlapOwners': sorted(set(owner for r in rows_stage for owner in r['stationaryRegionalOverlapCandidates']))
    }

slide_rows = [r for r in results if r['stage'] == 'B']
safe_samples = [r for r in slide_rows if r['actuatorEnvelope']['conservative12mmHousingMarginM'] >= 0]
def scalar_intervals(rows, predicate):
    selected = [r['panelSlideScalar'] for r in rows if predicate(r)]
    if not selected:
        return []
    intervals = [[selected[0], selected[0]]]
    step = (rows[-1]['panelSlideScalar'] - rows[0]['panelSlideScalar']) / max(1, len(rows) - 1)
    for value in selected[1:]:
        if abs(value - intervals[-1][1] - step) <= 1e-8:
            intervals[-1][1] = value
        else:
            intervals.append([value, value])
    return intervals
safe_slide = {
    'sampleCount': len(safe_samples),
    'firstSampledScalarWithNonnegativeConservativeHousingMargin': safe_samples[0]['panelSlideScalar'] if safe_samples else None,
    'allLaterSamplesRemainNonnegative': bool(safe_samples) and all(r['actuatorEnvelope']['conservative12mmHousingMarginM'] >= 0 for r in slide_rows if r['panelSlideScalar'] >= safe_samples[0]['panelSlideScalar']),
    'safeScalarIntervalsAmongRouteSamples': scalar_intervals(slide_rows, lambda r:r['actuatorEnvelope']['conservative12mmHousingMarginM'] >= 0),
    'possibleHousingConflictScalarIntervalsFromConservativeBound': scalar_intervals(slide_rows, lambda r:r['actuatorEnvelope']['conservative12mmHousingMarginM'] < 0),
    'sampled12mmEnvelopeProximityScalars': [r['panelSlideScalar'] for r in slide_rows if r['actuatorEnvelope']['sampleDistanceM'] <= .012],
    'note': 'These are only sampled scalars on the single stage-B path, not certified carriage support or continuous clearance.'
}

report = {
    'schema': 'murderbird-panel-only-staged-access-clearance/v1',
    'status': 'candidate trajectory diagnostic; not runtime integration or continuous clearance acceptance',
    'inputs': {
        'native': {'path': str(NATIVE.relative_to(ROOT)), 'sha256': sha(NATIVE), 'bytes': NATIVE.stat().st_size},
        'posePacket': {'path': str(POSES.relative_to(ROOT)), 'sha256': sha(POSES), 'modelSha256': pose_data['model']['sha256'], 'poseCount': pose_data['poseCount'], 'nativePivotCount': 52, 'packetTransformRowsPerPose': 67},
        'mountProposal': {'path': str(MOUNTS.relative_to(ROOT)), 'sha256': sha(MOUNTS)},
        'actuatorRadiusM': .012,
        'actuatorOwnerEndpoints': {'lowerOwner': mounts['lower-drive-anchor']['owner'], 'lowerXYZ': list(lower_a), 'upperOwner': mounts['upper-horn-tip']['owner'], 'upperXYZ': list(upper_a)},
        'breastAssemblyMeshes': sorted(panel_stats), 'breastMeshTriangleCount': len(panel_faces),
        'stationaryOwners': {owner: sorted(stats) for owner,stats in static_stats.items()},
        'excludedStationaryMeshesNotInNamedRegionalOwnerSet': sorted(excluded_stationary),
        'nativeParentLocalToPinnedRuntimeBreastMatrixMaxError': matrix_err,
        'nativeParentWorld': [list(r) for r in parent_world_native]
    },
    'trajectory': {
        'stageA': {'samples': 34, 'routeIndices': [0, 33], 'timelineOpen': [0, 1/3], 'angleRad': [0, -.675], 'panelSlideScalar': 0},
        'stageB': {'samples': 35, 'routeIndices': [33, 67], 'timelineOpen': [1/3, 2/3], 'angleRad': -.675, 'panelSlideScalar': [0, .5]},
        'stageC': {'samples': 34, 'routeIndices': [67, 100], 'timelineOpen': [2/3, 1], 'angleRad': [-.675, -1.35], 'panelSlideScalar': .5},
        'panelTranslationRuntimeLocalPerUnit': [-.70, -.12, .18],
        'totalDiscreteSamples': len(results),
        'samplingNote': '101 uniformly spaced route samples; exact stage boundaries at open=1/3 and 2/3 fall between sample indices, with the piecewise path functions continuous at both boundaries.',
        'otherNativeOwners': 'held at attempt-07 rest transforms for all samples',
        'closedTransformRestoredAt': {'timelineOpen': 0, 'angleRad': 0, 'panelSlideScalar': 0}
    },
    'method': {
        'actuator': 'V4 proposal anchor endpoints transformed by actual pinned native owners; centerline sampled at17 equal intervals against entire evaluated breastplate mesh assembly. Conservative distance lower bound is min sampled distance minus half the segment sample step (1-Lipschitz distance-to-surface bound); 12mm housing radius subtracted separately.',
        'stationaryPanelScreen': 'Per-sample Blender BVHTree triangle overlap candidate pairs between the transformed breastplate assembly and stationary meshes grouped under named regional owners. Candidate counts can include intended contact/coplanarity; they are not classified as confirmed collision.',
        'poseMapping': 'Rest breastplate world matrix is checked against packet after Blender/runtime basis conversion. Panel-only transform applies in runtime local coordinates, then maps its delta to native coordinates. No global separation offset or transform is applied to other assemblies.'
    },
    'stageSummaries': stage_summaries,
    'stageBPanelSlideScalarScreen': safe_slide,
    'samples': results,
    'limits': [
        'This is 303 discrete samples of a proposed panel-only route, not a continuous swept-volume proof.',
        'Actuator brackets, fittings, bearing support, load, and physical feasibility are unbuilt and untested.',
        'BVH triangle overlap output is a candidate screen; coplanar or intended lap contacts need dedicated interpretation.',
        'Only the declared regional owner groups are included in the stationary assembly screen; excluded meshes are listed.',
        'No app/runtime/model file was edited, no geometry saved, and no visual or human acceptance is claimed.'
    ]
}
POSE_OUTPUT.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'output': str(POSE_OUTPUT), 'samples': len(results), 'stageSummaries': stage_summaries, 'stageBPanelSlideScalarScreen': safe_slide}, indent=2))
