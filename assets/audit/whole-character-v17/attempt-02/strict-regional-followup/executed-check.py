"""Strictly recheck selected V17 attempt-02 BVH candidates in four actual poses.

Read-only Blender diagnostic. It applies exact runtime world matrices from the
hash-bound V17 packet, recomputes world-space BVH overlaps for the scoped pairs,
then calls the frozen proper-crossing kernel. Discrete surface evidence only.
"""
from pathlib import Path
import hashlib
import importlib.util
import json

import bpy
from mathutils import Matrix
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[5]
NATIVE = ROOT / 'assets/models/whole-character-v17/attempt-02/murderbird-whole-character-v17.blend'
POSES = ROOT / 'assets/audit/whole-character-v17/attempt-02/runtime-poses/pose-snapshot.json'
CANDIDATES = ROOT / 'assets/audit/whole-character-v17/attempt-02/regional-clearance-v2/native-clearance-comparison.json'
OUT = Path(__file__).resolve().parent
EXPECTED = {
    'native': '7d371907b279eb3d625e67164d84a78b2901a5cb6a79917def07f48ff8792d7b',
    'poses': '1964918661da857878376ff95457f3b8e0bc73479bd83225a8419fb1e2a627f9',
    'candidates': '5b407216acbb1a861f6042dffa5434598b8eb4c4bff727e2a48966920ef5e8e0',
}
POSE_IDS = ['inspection-open-0-separation-0', 'maker-neck-control', 'advanced-contact',
            'inspection-open-0.25-separation-0']

C = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def converted(flat):
    browser = Matrix([[flat[col * 4 + row] for col in range(4)] for row in range(4)])
    return C.inverted() @ browser @ C


def depth(obj):
    return 0 if obj.parent is None else 1 + depth(obj.parent)


def surface(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
    faces = [tuple(tri.vertices) for tri in mesh.loop_triangles]
    evaluated.to_mesh_clear()
    if not faces:
        return None
    return {'tree': BVHTree.FromPolygons(points, faces, all_triangles=True, epsilon=0.0),
            'points': points, 'faces': faces,
            'min': [min(p[i] for p in points) for i in range(3)],
            'max': [max(p[i] for p in points) for i in range(3)]}


def bounds_overlap(a, b):
    return all(a['min'][i] <= b['max'][i] and b['min'][i] <= a['max'][i] for i in range(3))


def pose_rows(pose):
    return {r['name']: r for r in pose['pivotMatrices'] if r.get('kind') != 'mesh'}


def category(subject, target):
    if (subject.startswith('Orbital passive retaining race') or
            subject.startswith('Passive orbital attachment form')) and (
            target.startswith('Swept temporal lamina') or target.startswith('Temporal lamina root pin')):
        return 'orbital-race-or-passive-form_vs_temporal-crown-or-root-pin'
    if subject == 'Breast inner access shell' and target in {
            'Passive rib behind access cover.002', 'Passive rib behind access cover.003'}:
        return 'breast-access-shell_vs_passive-rib'
    if subject.startswith('V17 breast directional lamina 1 ') and (
            target.startswith('Passive rib behind access cover.') or
            target.startswith('Cervical flank lamina') or target.startswith('Throat formed lamina')):
        return 'first-course-breast-plate_vs-rib-or-neck-lamina'
    return None


def main():
    inputs = {'native': NATIVE, 'poses': POSES, 'candidates': CANDIDATES}
    hashes = {name: sha(path) for name, path in inputs.items()}
    assert hashes == EXPECTED, f'Hash-bound input changed: {hashes}'
    packet = json.loads(POSES.read_text())
    cand_data = json.loads(CANDIDATES.read_text())
    assert cand_data['inputs']['study']['sha256'] == EXPECTED['native']
    assert cand_data['inputs']['poses']['sha256'] == EXPECTED['poses']
    pose_map = {p['id']: p for p in packet['poses']}
    assert all(pid in pose_map for pid in POSE_IDS)
    candidate_rows = {r['poseId']: r for r in cand_data['reports']['study']['poses']}
    assert all(pid in candidate_rows for pid in POSE_IDS)

    kernel_path = ROOT / 'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'
    kernel_spec = importlib.util.spec_from_file_location('frozen_crossing_kernel', kernel_path)
    kernel_module = importlib.util.module_from_spec(kernel_spec)
    kernel_spec.loader.exec_module(kernel_module)
    proper_crossing_receipt = kernel_module.proper_crossing_receipt

    bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    pivots = {o.name: o for o in bpy.data.objects if o.type == 'EMPTY'}
    meshes = {o.name: o for o in bpy.data.objects if o.type == 'MESH'}
    rest_rows = pose_rows(pose_map['inspection-open-0-separation-0'])
    assert set(pivots) <= set(rest_rows), 'Pose packet lacks one or more native pivots'
    rest_error = max(abs(pivots[n].matrix_world[r][c] - converted(rest_rows[n]['worldMatrix'])[r][c])
                     for n in pivots for r in range(4) for c in range(4))
    assert rest_error < 2e-6, f'Native/rest world-matrix mapping mismatch: {rest_error}'

    identity = Matrix.Identity(4)
    report_rows = []
    for pose_id in POSE_IDS:
        pr = pose_rows(pose_map[pose_id])
        for name in sorted(pivots, key=lambda n: depth(pivots[n])):
            pivots[name].matrix_world = converted(pr[name]['worldMatrix'])
        bpy.context.view_layer.update()
        pose_error = max(abs(pivots[n].matrix_world[r][c] - converted(pr[n]['worldMatrix'])[r][c])
                         for n in pivots for r in range(4) for c in range(4))
        assert pose_error < 2e-6, f'Pose application mismatch {pose_id}: {pose_error}'
        source_hits = candidate_rows[pose_id]['pairsWithOverlapCandidates']
        focus_hits = []
        for hit in source_hits:
            cat = category(hit['subject'], hit['target'])
            if cat:
                focus_hits.append((cat, hit))
        depsgraph = bpy.context.evaluated_depsgraph_get()
        surface_cache = {}
        out_hits = []
        for cat, hit in focus_hits:
            sn, tn = hit['subject'], hit['target']
            assert sn in meshes and tn in meshes, f'Missing candidate mesh: {sn} / {tn}'
            if sn not in surface_cache:
                surface_cache[sn] = surface(meshes[sn], depsgraph)
            if tn not in surface_cache:
                surface_cache[tn] = surface(meshes[tn], depsgraph)
            a, b = surface_cache[sn], surface_cache[tn]
            overlaps = [] if not bounds_overlap(a, b) else a['tree'].overlap(b['tree'])
            proofs = proper_crossing_receipt(a, b, overlaps, identity, identity)
            examples = []
            for ex in proofs['examples']:
                ai, bi = ex['subjectEvaluatedTriangle'], ex['targetEvaluatedTriangle']
                ta = [a['points'][v] for v in a['faces'][ai]]
                tb = [b['points'][v] for v in b['faces'][bi]]
                examples.append({'subjectEvaluatedTriangle': ai, 'targetEvaluatedTriangle': bi,
                                 'subjectTriangleWorldXYZ': [[round(float(q), 7) for q in p] for p in ta],
                                 'targetTriangleWorldXYZ': [[round(float(q), 7) for q in p] for p in tb]})
            out_hits.append({'category': cat, 'subject': sn, 'target': tn,
                             'subjectOwner': meshes[sn].parent.name if meshes[sn].parent else None,
                             'targetOwner': meshes[tn].parent.name if meshes[tn].parent else None,
                             'sourceBroadphaseCandidateCount': hit['triangleOverlapCandidates'],
                             'recheckedBroadphaseCandidateCount': len(overlaps),
                             'strictCrossing': proofs['confirmedSubjectTriangleCount'] > 0,
                             'strictSubjectTriangleCount': proofs['confirmedSubjectTriangleCount'],
                             'strictTargetTriangleCount': proofs['confirmedTargetTriangleCount'],
                             'subjectCrossingPoseWorldBoundsXYZ': proofs['subjectCrossingRestWorldBoundsNativeXYZ'],
                             'targetCrossingPoseWorldBoundsXYZ': proofs['targetCrossingRestWorldBoundsNativeXYZ'],
                             'strictTriangleExamplesPoseWorldXYZ': examples})
        report_rows.append({'poseId': pose_id, 'achievedWorldMatrixMaxError': pose_error,
                            'candidatePairsInScope': len(out_hits), 'pairs': out_hits})

    result = {
        'status': 'Read-only strict recheck of scoped BVH candidate pairs on V17 attempt-02 native at four exact sampled runtime poses.',
        'coordinateConvention': 'XYZ values and triangle bounds are Blender world metres at each applied sample pose; examples list full triangle vertices, not computed intersection-line points.',
        'executedChecker': {'path': str(Path(__file__).resolve().relative_to(ROOT)), 'sha256': sha(Path(__file__).resolve())},
        'blenderVersion': bpy.app.version_string,
        'inputs': {name: {'path': str(path.relative_to(ROOT)), 'sha256': hashes[name]} for name, path in inputs.items()},
        'strictKernel': {'path': str(kernel_path.relative_to(ROOT)), 'sha256': sha(kernel_path),
                         'function': 'proper_crossing_receipt',
                         'method': 'noncoplanar triangle-edge through opposite-triangle-face test; coplanar/tangent excluded'},
        'nativeRestMatrixMaxError': rest_error,
        'poses': report_rows,
        'limits': ['Pair search is restricted to stored broadphase candidates in the three requested geometric groups.',
                   'Strict crossings establish sampled surface penetration only; no containment depth or continuous sweep is tested.',
                   'The resulting pose matrices are hash-bound runtime samples, not browser screenshots or physical contact evidence.',
                   'No native scene was saved or modified.']
    }
    (OUT / 'strict-crossings.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'poses': {row['poseId']: {
        cat: {'strictCrossings': sum(x['strictCrossing'] for x in row['pairs'] if x['category'] == cat),
              'candidatePairs': sum(x['category'] == cat for x in row['pairs'])}
        for cat in sorted({x['category'] for x in row['pairs']})} for row in report_rows},
        'output': str(OUT / 'strict-crossings.json')}))


if __name__ == '__main__':
    main()
