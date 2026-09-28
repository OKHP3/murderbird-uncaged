"""Compare named native surfaces in hash-bound actual runtime pivot poses.

Read-only Blender diagnostic. A contract pins base/study/pose files and lists
changed mesh names and target owners. Overlap candidates require visual review;
this is neither a general collision solver nor an artistic acceptance test.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
C = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_bound(row):
    path = ROOT / row['path']
    assert sha(path) == row['sha256'], f'Changed input: {path}'
    return path


def converted(flat):
    assert len(flat) == 16
    browser = Matrix([[flat[col * 4 + row] for col in range(4)] for row in range(4)])
    return C.inverted() @ browser @ C


def error(a, b):
    return max(abs(a[r][c] - b[r][c]) for r in range(4) for c in range(4))


def depth(obj):
    return 0 if obj.parent is None else 1 + depth(obj.parent)


def surface(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
    faces = [tuple(t.vertices) for t in mesh.loop_triangles]
    evaluated.to_mesh_clear()
    if not faces:
        return None
    return {
        'tree': BVHTree.FromPolygons(points, faces, all_triangles=True, epsilon=0.0),
        'min': [min(p[i] for p in points) for i in range(3)],
        'max': [max(p[i] for p in points) for i in range(3)],
        'points': points, 'faces': faces,
    }


def bounds_overlap(a, b):
    return all(a['min'][i] <= b['max'][i] and b['min'][i] <= a['max'][i] for i in range(3))


def centroid(s, face):
    return [sum(s['points'][v][axis] for v in s['faces'][face]) / 3 for axis in range(3)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--contract', required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    contract_path = ROOT / args.contract
    contract = json.loads(contract_path.read_text())
    fixture = BVHTree.FromPolygons([(-1, -1, 0), (1, -1, 0), (0, 1, 0)], [(0, 1, 2)], all_triangles=True)
    crossing_points = [(0, -.5, -1), (0, -.5, 1), (0, .5, 0)]
    crossing_fixture = BVHTree.FromPolygons(crossing_points, [(0, 1, 2)], all_triangles=True)
    separated_fixture = BVHTree.FromPolygons([Vector(p) + Vector((0, 0, 3)) for p in crossing_points], [(0, 1, 2)], all_triangles=True)
    assert fixture.overlap(crossing_fixture) and not fixture.overlap(separated_fixture), 'BVH fixture failed'
    inputs = {key: read_bound(contract[key]) for key in ('base', 'study', 'poses')}
    pose_data = json.loads(inputs['poses'].read_text())
    poses = pose_data['poses']
    for pose in poses:
        if isinstance(pose['pivotMatrices'], list):
            rows = [row for row in pose['pivotMatrices'] if row.get('kind') != 'mesh']
            names = [row['name'] for row in rows]
            assert len(set(names)) == len(names), 'Ambiguous named runtime transforms'
            pose['pivotMatrices'] = {row['name']: {'local': row['localMatrix'], 'world': row['worldMatrix']} for row in rows}
    rest = next(p for p in poses if p['id'] == contract['restPoseId'])
    selected = [p for p in poses if p['id'] in contract['poseIds']]
    assert len(selected) == len(set(contract['poseIds'])) > 0
    out = ROOT / contract['outputDirectory']
    assert not out.exists(), 'Use a new evidence directory'
    reports = {}
    for variant in ('base', 'study'):
        bpy.ops.wm.open_mainfile(filepath=str(inputs[variant]))
        bpy.context.scene.frame_set(1)
        bpy.context.view_layer.update()
        pivots = {o.name: o for o in bpy.data.objects if o.type == 'EMPTY'}
        assert set(pivots) <= set(rest['pivotMatrices']), 'Missing native pivot in runtime snapshot'
        rest_errors = {name: error(obj.matrix_world, converted(rest['pivotMatrices'][name]['world']))
                       for name, obj in pivots.items()}
        assert max(rest_errors.values()) < 2e-6, f'Axis/rest conversion disagrees: {rest_errors}'
        pivot_order = sorted(pivots, key=lambda name: depth(pivots[name]))
        meshes = {o.name: o for o in bpy.data.objects if o.type == 'MESH'}
        subjects = [meshes[name] for name in contract['changedMeshes'] if name in meshes]
        assert len(subjects) > 0
        targets = [o for o in meshes.values() if o.parent and o.parent.name in contract['targetOwners']]
        rows = []
        for pose in selected:
            for name in pivot_order:
                pivots[name].matrix_world = converted(pose['pivotMatrices'][name]['world'])
                bpy.context.view_layer.update()
            achieved_error = max(error(pivots[n].matrix_world, converted(pose['pivotMatrices'][n]['world'])) for n in pivots)
            assert achieved_error < 2e-6, f'Pose application disagrees: {pose["id"]}/{achieved_error}'
            depsgraph = bpy.context.evaluated_depsgraph_get()
            surfaces = {o.name: surface(o, depsgraph) for o in set(subjects + targets)}
            considered = set()
            hits = []
            for subject in subjects:
                for target in targets:
                    if subject == target or subject.parent == target.parent:
                        continue
                    key = tuple(sorted((subject.name, target.name)))
                    if key in considered:
                        continue
                    considered.add(key)
                    a, b = surfaces[subject.name], surfaces[target.name]
                    if not a or not b or not bounds_overlap(a, b):
                        continue
                    overlaps = a['tree'].overlap(b['tree'])
                    if overlaps:
                        hits.append({'subject': subject.name, 'target': target.name,
                                     'subjectOwner': subject.parent.name, 'targetOwner': target.parent.name,
                                     'triangleOverlapCandidates': len(overlaps),
                                     'examples': [{'subjectTriangleCenter': centroid(a, x),
                                                   'targetTriangleCenter': centroid(b, y)} for x, y in overlaps[:3]]})
            rows.append({'poseId': pose['id'], 'achievedWorldMatrixMaxError': achieved_error,
                         'uniqueDifferentOwnerMeshPairs': len(considered), 'pairsWithOverlapCandidates': hits})
        reports[variant] = {'restConversionMaxError': max(rest_errors.values()),
                            'subjectMeshes': [o.name for o in subjects], 'targetMeshCount': len(targets), 'poses': rows}
    for key, path in inputs.items():
        assert sha(path) == contract[key]['sha256']
    out.mkdir(parents=True)
    shutil.copy2(Path(__file__), out / 'executed-diagnostic.py')
    shutil.copy2(contract_path, out / 'contract.json')
    result = {'inputs': {key: contract[key] for key in inputs}, 'reports': reports,
              'diagnosticSha256': sha(Path(__file__)), 'blenderVersion': bpy.app.version_string,
              'kernelFixtures': {'crossingTrianglesDetected': True, 'separatedTrianglesExcluded': True},
              'limits': ['Evaluated native mesh surface BVH overlap candidates at discrete actual-runtime pivot poses.',
                         'Different direct-owner pairs only; same-owner intended embedding is excluded.',
                         'Does not detect full containment, prove continuous clearance or model physical contact.',
                         'Counts require pair-level and visual interpretation; inherited overlaps are not newly introduced defects.',
                         'No source was saved or changed. No export, browser or artistic acceptance is established.']}
    (out / 'native-clearance-comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({variant: {row['poseId']: len(row['pairsWithOverlapCandidates']) for row in data['poses']}
                      for variant, data in reports.items()}))


if __name__ == '__main__':
    main()
