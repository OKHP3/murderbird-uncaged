"""Read-only clearance screen for one posterior actuator anchor proposal."""
from pathlib import Path
import hashlib, json
import bpy
from mathutils import Matrix, Vector, Euler
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
NATIVE = ROOT / 'assets/models/uncaged-cervical-construction-study-v1/attempt-14/murderbird-cervical-construction-study-v1.blend'
POSES = ROOT / 'assets/audit/cervical-runtime-study-v1/expanded-runtime-poses/pose-snapshot.json'
UPPER_SWEEP = ROOT / 'assets/audit/cervical-construction-study-v1/attempt-14/measured-upper-sweep.json'
OUT_FILE = OUT / 'posterior-drive-clearance-final.json'
EXPECTED_NATIVE = 'ef9e28ddbce9d62aabc8181a058640ea1e8b7a339b673df37b913d96699f9440'
EXPECTED_POSES = '1cb4a2f75ecae625a44c768ba543e9b99e1caa9791a3056e20f5d88bd73d2f26'
EXPECTED_GLTF = '5736ca592c5ebfa7da78315b136b53ad6a48050ede66f6d60b9ccf860afa8ecf'
EXPECTED_UPPER_SWEEP = '3ca72f0dfe5d8bde703cf30951f7fb85091e5bdd8e157032606d88c94ce15228'
if OUT_FILE.exists():
    raise RuntimeError(f'Refusing to overwrite {OUT_FILE}')

C = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))
REGIONAL_OWNERS = {'body', 'neck', 'cervical-upper', 'head', 'jaw', 'breastplate',
                   'left-mantle', 'right-mantle'}
NON_PANEL_OWNERS = REGIONAL_OWNERS - {'breastplate'}
HOUSING_RADIUS = 0.012


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def converted(flat):
    browser = flat if isinstance(flat, Matrix) else Matrix([[flat[col * 4 + row] for col in range(4)] for row in range(4)])
    return C.inverted() @ browser @ C


def depth(obj):
    return 0 if obj.parent is None else 1 + depth(obj.parent)


def set_pose(pose, pivots):
    rows = {r['name']: r for r in pose['pivotMatrices'] if r.get('kind') != 'mesh'}
    assert set(pivots) <= set(rows)
    for name in sorted(pivots, key=lambda n: depth(pivots[n])):
        pivots[name].matrix_world = converted(rows[name]['worldMatrix'])
        bpy.context.view_layer.update()
    return max(abs(pivots[n].matrix_world[r][c] - converted(rows[n]['worldMatrix'])[r][c])
               for n in pivots for r in range(4) for c in range(4))


def is_descendant(obj, root):
    current = obj
    while current is not None:
        if current == root:
            return True
        current = current.parent
    return False


def build_bvh(objects):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    verts, faces, face_objects = [], [], []
    counts = {}
    for obj in objects:
        ev = obj.evaluated_get(depsgraph)
        mesh = ev.to_mesh()
        mesh.calc_loop_triangles()
        start = len(verts)
        verts.extend(ev.matrix_world @ v.co for v in mesh.vertices)
        faces.extend(tuple(start + i for i in tri.vertices) for tri in mesh.loop_triangles)
        face_objects.extend([obj.name] * len(mesh.loop_triangles))
        counts[obj.name] = {'vertices': len(mesh.vertices), 'triangles': len(mesh.loop_triangles)}
        ev.to_mesh_clear()
    if not faces:
        return None, verts, faces, face_objects, counts
    return BVHTree.FromPolygons(verts, faces, all_triangles=True, epsilon=0.0), verts, faces, face_objects, counts


def segment_distance(tree, a, b, n=17):
    length = (b - a).length
    best = {'sampleDistanceM': float('inf'), 'nearestTriangle': None, 'samplePoint': None, 'nearestPoint': None}
    for i in range(n):
        point = a.lerp(b, i / (n - 1))
        hit = tree.find_nearest(point)
        if hit[0] is not None and hit[3] < best['sampleDistanceM']:
            best = {'sampleDistanceM': hit[3], 'nearestTriangle': hit[2],
                    'samplePoint': list(point), 'nearestPoint': list(hit[0])}
    lower = best['sampleDistanceM'] - length / (n - 1) / 2
    hit = tree.ray_cast(a, (b - a).normalized(), length) if length > 0 else (None, None, None, None)
    return {**best, 'centerlineRayPiercesSurface': hit[0] is not None,
            'rayPiercePoint': list(hit[0]) if hit[0] is not None else None,
            'rayPierceTriangle': hit[2], 'rayPierceDistanceM': hit[3],
            'segmentLengthM': length, 'sampleCount': n,
            'conservativeCenterlineLowerBoundM': lower,
            'sampled12mmHousingMarginM': best['sampleDistanceM'] - HOUSING_RADIUS,
            'conservative12mmHousingMarginM': lower - HOUSING_RADIUS}


def surface_groups(pivots, exclude_panel_descendants=False):
    breast = pivots['breastplate']
    groups = {owner: [] for owner in sorted(REGIONAL_OWNERS)}
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        on_panel = is_descendant(obj, breast)
        if exclude_panel_descendants and on_panel:
            continue
        if on_panel:
            groups['breastplate'].append(obj)
            continue
        if obj.parent and obj.parent.name in groups:
            groups[obj.parent.name].append(obj)
    return {owner: objects for owner, objects in groups.items() if objects}


assert bpy.data.filepath and Path(bpy.data.filepath).resolve() == NATIVE.resolve(), 'Open pinned attempt-14 native'
assert sha(NATIVE) == EXPECTED_NATIVE
assert sha(POSES) == EXPECTED_POSES
assert sha(UPPER_SWEEP) == EXPECTED_UPPER_SWEEP
pose_data = json.loads(POSES.read_text())
upper_sweep_data = json.loads(UPPER_SWEEP.read_text())
assert pose_data['model']['sha256'] == EXPECTED_GLTF and pose_data['poseCount'] == 21
assert len(pose_data['poses']) == 21
# Confirm attempt-14's native pivot-name set against exact attempt-07 source before packet replay.
source07 = ROOT / 'assets/models/uncaged-cervical-construction-study-v1/attempt-07/murderbird-cervical-construction-study-v1.blend'
assert source07.exists()
pivots = {obj.name: obj for obj in bpy.data.objects if obj.type == 'EMPTY'}
assert len(pivots) == 52, f'Expected exact 52 native pivots; got {len(pivots)}'
attempt14_pivot_names = sorted(pivots)
bpy.ops.wm.open_mainfile(filepath=str(source07))
attempt07_pivot_names = sorted(o.name for o in bpy.data.objects if o.type == 'EMPTY')
assert len(attempt07_pivot_names) == 52 and attempt07_pivot_names == attempt14_pivot_names, 'Attempt-14 pivot names differ from attempt-07 packet contract'
bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
pivots = {obj.name: obj for obj in bpy.data.objects if obj.type == 'EMPTY'}
assert sorted(pivots) == attempt14_pivot_names
assert REGIONAL_OWNERS <= set(pivots)
pose_by_id = {p['id']: p for p in pose_data['poses']}
assert len(pose_by_id) == 21

# Measure link length and signed moment arm over the stated absolute upper-pitch interval.
rest_pose = next(p for p in pose_data['poses'] if p['id'] == 'runtime-rest')
set_pose(rest_pose, pivots)
upper = pivots['cervical-upper']
neck = pivots['neck']
upper_rest_rot = upper.rotation_euler.copy()
upper_pitch_samples = []
for i in range(101):
    pitch = -0.091 + (0.4225 + 0.091) * i / 100
    upper.rotation_euler.x = pitch
    bpy.context.view_layer.update()
    upper_point = upper.matrix_world @ Vector((-0.160, 0.080, 0.015))
    lower_point = neck.matrix_world @ Vector((-0.160, 0.180, 0.060))
    line_force = (lower_point - upper_point).normalized()
    pitch_axis = upper.matrix_world.to_3x3() @ Vector((1, 0, 0))
    leverage = (upper_point - upper.matrix_world.translation).cross(line_force).dot(pitch_axis)
    upper_pitch_samples.append({'upperPitchRad': pitch, 'actuatorLengthM': (upper_point-lower_point).length, 'signedUpperPitchLeverageM': leverage})
upper.rotation_euler = upper_rest_rot
bpy.context.view_layer.update()

proposals = {
    'upper-horn-tip': {'owner': 'cervical-upper', 'localNativeXYZ': [-0.160, 0.080, 0.015]},
    'lower-drive-anchor': {'owner': 'neck', 'localNativeXYZ': [-0.160, 0.180, 0.060]},
}
for row in proposals.values():
    xyz = row['localNativeXYZ']
    row['localBrowserXYZ'] = [xyz[0], xyz[2], -xyz[1]]
assert proposals['upper-horn-tip']['localNativeXYZ'] == [-0.160, 0.080, 0.015]
assert proposals['lower-drive-anchor']['localNativeXYZ'] == [-0.160, 0.180, 0.060]

# Captured operating poses: replay all52 native pivots and test the proposed
# posterior straight centerline against actual regional owner surfaces.
operating_rows = []
operating_rest_errors = []
for pose in pose_data['poses']:
    err = set_pose(pose, pivots)
    operating_rest_errors.append(err)
    points = {n: pivots[row['owner']].matrix_world @ Vector(row['localNativeXYZ'])
              for n, row in proposals.items()}
    upper = pivots['cervical-upper']
    force = (points['lower-drive-anchor'] - points['upper-horn-tip']).normalized()
    axis = upper.matrix_world.to_3x3() @ Vector((1, 0, 0))
    signed_leverage = (points['upper-horn-tip'] - upper.matrix_world.translation).cross(force).dot(axis)
    groups = surface_groups(pivots)
    group_trees, group_faces = {}, {}
    for owner, objects in groups.items():
        tree, _, _, face_names, counts = build_bvh(objects)
        if tree is not None:
            group_trees[owner] = tree
            group_faces[owner] = face_names
    group_results = {}
    for owner, tree in group_trees.items():
        result = segment_distance(tree, points['lower-drive-anchor'], points['upper-horn-tip'])
        tri = result['nearestTriangle']
        result['nearestMesh'] = group_faces[owner][tri] if tri is not None else None
        hit_tri = result['rayPierceTriangle']
        result['rayPierceMesh'] = group_faces[owner][hit_tri] if hit_tri is not None and hit_tri < len(group_faces[owner]) else None
        group_results[owner] = result
    nearest = min(group_results.items(), key=lambda kv: kv[1]['sampleDistanceM']) if group_results else (None, None)
    operating_rows.append({'poseId': pose['id'], 'pivotApplicationMaxError': err,
                           'actuatorLengthM': (points['upper-horn-tip'] - points['lower-drive-anchor']).length,
                           'signedUpperPitchLeverageM': signed_leverage,
                           'endpointWorldNativeXYZ': {k: list(v) for k, v in points.items()},
                           'perOwnerClearance': group_results,
                           'nearestOwner': nearest[0], 'nearestSurface': nearest[1]})

# Separate canonical open sweep: hold every native owner at the captured rest
# pose and rotate only the breastplate through the standard production law.
rest_pose = pose_by_id['runtime-rest']
rest_err = set_pose(rest_pose, pivots)
assert rest_err < 2e-6
breast = pivots['breastplate']
panel_meshes = sorted([o for o in bpy.data.objects if o.type == 'MESH' and is_descendant(o, breast)], key=lambda o:o.name)
assert panel_meshes
panel_rest_tree, panel_verts_rest, panel_faces, panel_face_names, panel_mesh_stats = build_bvh(panel_meshes)
static_groups = surface_groups(pivots, exclude_panel_descendants=True)
static_trees, static_face_names = {}, {}
for owner, objects in static_groups.items():
    tree, _, _, names, _ = build_bvh(objects)
    if tree is not None:
        static_trees[owner] = tree
        static_face_names[owner] = names

rows = {r['name']: r for r in rest_pose['pivotMatrices'] if r.get('kind') != 'mesh'}
local_rt_flat = rows['breastplate']['localMatrix']
local_rt = Matrix([[local_rt_flat[col * 4 + row] for col in range(4)] for row in range(4)])
local_rest_blender = converted(local_rt_flat)
local_error = max(abs(breast.matrix_local[r][c] - local_rest_blender[r][c]) for r in range(4) for c in range(4))
assert local_error < 2e-5, f'Breast parent-local matrix mismatch {local_error}'
loc, quat, scale = local_rt.decompose()
rest_euler = quat.to_euler('XYZ')
scale_matrix = Matrix.Diagonal((scale.x, scale.y, scale.z, 1.0))
body_world = breast.parent.matrix_world.copy()
open_rows = []
for i in range(101):
    open_value = i / 100
    new_loc = loc
    euler = Euler((rest_euler.x, -1.35 * open_value, rest_euler.z), 'XYZ')
    local_new_rt = Matrix.Translation(new_loc) @ euler.to_quaternion().to_matrix().to_4x4() @ scale_matrix
    local_delta_blender = converted((local_new_rt @ local_rt.inverted()))
    world_delta = body_world @ local_delta_blender @ body_world.inverted()
    moved_verts = [world_delta @ v for v in panel_verts_rest]
    panel_tree = BVHTree.FromPolygons(moved_verts, panel_faces, all_triangles=True, epsilon=0.0)
    points = {n: pivots[row['owner']].matrix_world @ Vector(row['localNativeXYZ'])
              for n, row in proposals.items()}
    per_owner = {}
    panel_result = segment_distance(panel_tree, points['lower-drive-anchor'], points['upper-horn-tip'])
    tri = panel_result['nearestTriangle']
    panel_result['nearestMesh'] = panel_face_names[tri] if tri is not None else None
    hit_tri = panel_result['rayPierceTriangle']
    panel_result['rayPierceMesh'] = panel_face_names[hit_tri] if hit_tri is not None and hit_tri < len(panel_face_names) else None
    per_owner['breastplate'] = panel_result
    for owner, tree in static_trees.items():
        result = segment_distance(tree, points['lower-drive-anchor'], points['upper-horn-tip'])
        tri = result['nearestTriangle']
        result['nearestMesh'] = static_face_names[owner][tri] if tri is not None else None
        hit_tri = result['rayPierceTriangle']
        result['rayPierceMesh'] = static_face_names[owner][hit_tri] if hit_tri is not None and hit_tri < len(static_face_names[owner]) else None
        per_owner[owner] = result
    nearest = min(per_owner.items(), key=lambda kv:kv[1]['sampleDistanceM'])
    open_rows.append({'sampleIndex': i, 'open': open_value, 'runtimeBreastRotationYRad': -1.35 * open_value,
                      'separation': 0, 'onlyBreastplateMoved': True,
                      'perOwnerClearance': per_owner, 'nearestOwner': nearest[0], 'nearestSurface': nearest[1]})


def summarize(rows, keys):
    summaries = {}
    for owner in keys:
        vals = [(r.get('perOwnerClearance', {}).get(owner) if 'perOwnerClearance' in r else None, r) for r in rows]
        vals = [(v, r) for v, r in vals if v]
        if not vals:
            continue
        dmin, row = min(vals, key=lambda pair: pair[0]['sampleDistanceM'])
        bound, brow = min(vals, key=lambda pair: pair[0]['conservative12mmHousingMarginM'])
        summaries[owner] = {
            'minimumSampledCenterlineDistanceM': dmin['sampleDistanceM'],
            'minimumAt': {'poseId': row.get('poseId'), 'open': row.get('open'), 'slide': row.get('panelSlideScalar'), 'nearestMesh': dmin['nearestMesh']},
            'minimumConservative12mmHousingMarginM': bound['conservative12mmHousingMarginM'],
            'minimumConservativeAt': {'poseId': brow.get('poseId'), 'open': brow.get('open'), 'slide': brow.get('panelSlideScalar'), 'nearestMesh': bound['nearestMesh']},
            'samplesWithin12mmByDirectSample': sum(v['sampleDistanceM'] <= HOUSING_RADIUS for v, _ in vals),
            'samplesWithNegativeConservativeHousingMargin': sum(v['conservative12mmHousingMarginM'] < 0 for v, _ in vals)
        }
    return summaries


def pierced_summary(rows):
    summary = {}
    for owner in sorted(REGIONAL_OWNERS):
        hits = [(row, row['perOwnerClearance'][owner]) for row in rows
                if owner in row.get('perOwnerClearance', {}) and row['perOwnerClearance'][owner]['centerlineRayPiercesSurface']]
        if hits:
            summary[owner] = {
                'sampleCount': len(hits),
                'firstPoseOrOpen': hits[0][0].get('poseId', hits[0][0].get('open')),
                'lastPoseOrOpen': hits[-1][0].get('poseId', hits[-1][0].get('open')),
                'meshes': sorted({v['rayPierceMesh'] for _, v in hits if v.get('rayPierceMesh')})
            }
    return summary


result = {
    'schema': 'murderbird-posterior-actuator-clearance/v1',
    'status': 'read-only posterior actuator candidate screen; anchors are proposed and not built',
    'inputs': {
        'native': {'path': str(NATIVE.relative_to(ROOT)), 'sha256': sha(NATIVE), 'bytes': NATIVE.stat().st_size},
        'runtimePosePacket': {'path': str(POSES.relative_to(ROOT)), 'sha256': sha(POSES), 'modelSha256': pose_data['model']['sha256'], 'poseCount': pose_data['poseCount'], 'nativePivotCount': 52},
        'upperSweep': {'path': str(UPPER_SWEEP.relative_to(ROOT)), 'sha256': sha(UPPER_SWEEP)},
        'analyzer': {'path': str(Path(__file__).relative_to(ROOT)), 'sha256': sha(Path(__file__))},
        'proposedAnchors': proposals,
        'housingRadiusM': HOUSING_RADIUS,
        'operatingPoseRows': len(operating_rows),
        'openSweepRows': len(open_rows),
        'openSweepBreastAssemblyMeshes': len(panel_meshes),
        'openSweepBreastAssemblyTriangles': len(panel_faces),
        'nativeParentLocalRuntimeMatrixMaxError': local_error,
        'maxOperatingPivotApplicationError': max(operating_rest_errors)
    },
    'methods': {
        'operating': 'All52 native pivot world matrices from the captured21-pose packet replayed on attempt-14 after exact pivot-name-set equality was checked against attempt-07. Proposed posterior endpoints only; no panel transforms added beyond each captured pose. The straight segment is sampled at17 equally spaced points for each target owner group, with a BVH ray test for centerline surface piercing.',
        'openSweep': '101 open values 0..1 at separation0; captured runtime-rest pivot transforms applied first, then only breastplate rotation is changed by production formula rotation.y=-1.35*open. Other native owners remain at rest. Breastplate assembly is all native mesh descendants of breastplate.',
        'clearance': 'For each target group, min of17 point-to-evaluated-surface distances; conservative segment lower bound subtracts half the point spacing. A12mm envelope radius is subtracted separately. No actuator solid/fittings are present.',
        'upperPitch': 'With captured runtime-rest hierarchy, sample absolute cervical-upper local X pitch from -0.091 to +0.4225 rad at101 points; measure center-to-center link length and signed torque arm of unit link force about the upper pivot local-X axis. This is a kinematic line calculation only.' ,
        'coordinates': 'Packet pivot matrices are converted using the production Blender/runtime basis matrix; owner-local proposed mount coordinates are transformed by the actual owner pivots. Breast open sweep uses converted parent-local panel delta around actual native body parent.'
    },
    'meshPiercing': {'operatingPoses': pierced_summary(operating_rows), 'normalBreastOpening': pierced_summary(open_rows)},
    'upperPitchSweep': {'rangeRad': [-0.091, 0.4225], 'samples': upper_pitch_samples, 'strokeM': max(x['actuatorLengthM'] for x in upper_pitch_samples) - min(x['actuatorLengthM'] for x in upper_pitch_samples), 'minimumSignedLeverageM': min(x['signedUpperPitchLeverageM'] for x in upper_pitch_samples), 'maximumSignedLeverageM': max(x['signedUpperPitchLeverageM'] for x in upper_pitch_samples), 'signReversals': any(a['signedUpperPitchLeverageM'] * b['signedUpperPitchLeverageM'] < 0 for a,b in zip(upper_pitch_samples,upper_pitch_samples[1:]))},
    'operatingPoseSummary': summarize(operating_rows, REGIONAL_OWNERS),
    'openSweepSummary': summarize(open_rows, REGIONAL_OWNERS),
    'operatingPoses': operating_rows,
    'openSweep': open_rows,
    'limits': [
        'Native geometry and runtime pivots are read-only; reflected anchor locations are not built into the model.',
        'A centerline distance screen does not model full cylinder/rod ends, housing shape, brackets, supports, loads, or solid containment.',
        '17 line samples plus exact BVH ray casts screen the sampled straight centerline at each discrete pose/open value; there is no continuous interpolation proof between samples. A 12 mm envelope is a clearance proxy, not a modeled solid.',
        'No wing or wing restriction was changed. The regional line-clearance target set includes body, neck, upper neck, head, jaw, breastplate, and both mantle owners.',
        'No visual, hardware, runtime, or artistic acceptance is claimed.'
    ]
}
OUT_FILE.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'output': str(OUT_FILE), 'operatingSummary': result['operatingPoseSummary'], 'openSweepSummary': result['openSweepSummary']}, indent=2))
