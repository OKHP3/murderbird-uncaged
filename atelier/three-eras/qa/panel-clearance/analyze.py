"""Measure exact observed triangle groups after the UI control path has positioned them."""
import json
import sys
from pathlib import Path
from collections import Counter
import numpy as np
from mathutils.bvhtree import BVHTree
scratch = Path(sys.argv[-2])
dest = Path(sys.argv[-1])
receipt = json.loads((scratch / 'capture.json').read_text())

def transformed(vertices, matrix):
    return vertices @ matrix[:3, :3].T + matrix[:3, 3]

def as_tree(points, faces):
    return BVHTree.FromPolygons(points.tolist(), faces.tolist(), all_triangles=True, epsilon=0.0)

def accumulate_geometry(leaves, matrices):
    coords = []
    tris = []
    names = []
    base = 0
    for (leaf, matrix) in zip(leaves, matrices):
        key = leaf['geom']
        points = np.fromfile(scratch / (key + '.positions'), np.float32).reshape(-1, 3)
        faces = np.fromfile(scratch / (key + '.indices'), np.uint32).reshape(-1, 3)
        coords.append(transformed(points, matrix))
        tris.append(faces + base)
        base += len(points)
        names.extend([leaf['name'] + ' / ' + leaf['mat']] * len(faces))
    return (np.concatenate(coords), np.concatenate(tris), names)

def proper_cross(tris1, tris2):
    """Count triangle pairs whose edge intersects the interior of the other triangle.
    Require segment and destination barycentric coordinates > 1e-5 from boundaries.
    Directional test is repeated in both directions, so disjoint/coplanar pairs cannot
    be counted as transverse penetrations. This is a digital surface-crossing test.
    """
    result = np.zeros(len(tris1), dtype=bool)
    first = np.full((len(tris1), 3), np.nan)
    lengths = np.zeros(len(tris1))
    for (source, dst) in ((tris1, tris2), (tris2, tris1)):
        (a, b, c) = (dst[:, 0], dst[:, 1], dst[:, 2])
        (e1, e2) = (b - a, c - a)
        for i in range(3):
            p = source[:, i]
            direction = source[:, (i + 1) % 3] - p
            h = np.cross(direction, e2)
            det = np.einsum('ij,ij->i', e1, h)
            valid = np.abs(det) > 1e-14
            inv = np.divide(1.0, det, out=np.zeros_like(det), where=valid)
            s = p - a
            u = np.einsum('ij,ij->i', s, h) * inv
            q = np.cross(s, e1)
            v = np.einsum('ij,ij->i', direction, q) * inv
            t = np.einsum('ij,ij->i', e2, q) * inv
            tol = 1e-05
            hit = valid & (u > tol) & (v > tol) & (1 - u - v > tol) & (t > tol) & (1 - t > tol)
            points = p + direction * t[:, None]
            prior = hit & result
            lengths[prior] = np.maximum(lengths[prior], np.linalg.norm(points[prior] - first[prior], axis=1))
            first[hit & ~result] = points[hit & ~result]
            result |= hit
    return (result, lengths, first)

def ring_geometry(case):
    keys = list(case['groups'])
    (a, b) = (case['groups'][s] for s in keys)
    matrices = np.asarray([s['mats'] for s in case['samples']]).reshape(len(case['samples']), len(a) + len(b), 4, 4).transpose(0, 1, 3, 2)
    original = matrices[0]
    moves = matrices @ np.linalg.inv(original)
    rigid = max(np.max(np.abs(moves[:, :len(a)] - moves[:, :1])), np.max(np.abs(moves[:, len(a):] - moves[:, len(a):len(a) + 1])))
    if rigid >= 1e-10:
        raise ValueError("Relative movement differed across leaves of a rigid group")
    (av, af, an) = accumulate_geometry(a, original[:len(a)])
    (bv, bf, bn) = accumulate_geometry(b, original[len(a):])
    ar = case['samples']
    movingTree = as_tree(av, af)
    witness = np.arange(0, len(bv), max(1, len(bv) // 2000))
    rows = []
    for (i, row) in enumerate(ar[:-1]):
        m = np.linalg.inv(moves[i, 0]) @ moves[i, len(a)]
        posed = transformed(bv, m)
        left = transformed(av, moves[i, 0])
        right = transformed(bv, moves[i, len(a)])
        lower = np.maximum(np.maximum(left.min(0) - right.max(0), right.min(0) - left.max(0)), 0)
        lo = float(np.linalg.norm(lower))
        out = {'percent': row['f'], 'axis_separation_lower_bound': lo, 'crossing_triangle_pairs': 0, 'bvh_overlap_pairs': 0}
        if lo > 1e-06:
            rows.append(out)
            continue
        inter = movingTree.overlap(as_tree(posed, bf))
        if inter:
            (ia, ib) = np.array(inter, dtype=int).T
            (proper, lengths, worldrest) = proper_cross(av[af[ia]], posed[bf[ib]])
            if lengths.size and lengths.max() > 0:
                ix = int(np.argmax(lengths))
                spot = transformed(worldrest[ix:ix + 1], moves[i, 0])[0]
                out['largest_observed_crossing_segment'] = {
                    'length': float(lengths[ix]),
                    'world_a': spot.tolist(),
                    'cover': an[ia[ix]],
                    'neighbor': bn[ib[ix]],
                    'cover_triangle': int(ia[ix]),
                    'neighbor_triangle': int(ib[ix]),
                }
            out['crossing_triangle_pairs'] = int(sum(proper))
            out['bvh_overlap_pairs'] = len(inter)
            out['crossing_part_pairs'] = [{'cover': k[0], 'neighbor': k[1], 'triangle_pairs': n} for (k, n) in Counter(((an[x], bn[y]) for (x, y) in zip(ia[proper], ib[proper]))).most_common(5)]
        out['nearest_sampled_neighbor_vertex_upper_bound'] = min((movingTree.find_nearest(tuple(posed[v]))[3] for v in witness))
        rows.append(out)
    positive = [r for r in rows if r['crossing_triangle_pairs']]
    endpoint = rows[-1]
    rel = moves[-2, 0, :3, :3]
    angle = float(np.degrees(np.arccos(np.clip((np.trace(rel) - 1) / 2, -1, 1))))
    return {
        'era': case['era'],
        'region': case['region'],
        'groups': keys,
        'triangles': {keys[0]: len(af), keys[1]: len(bf)},
        'far_endpoint_rotation_degrees': angle,
        'max_hinge_drift': case['pivotDrift'],
        'reassembled_matrix_error': case['returnMatrixError'],
        'within_group_max_delta_matrix_error': float(rigid),
        'positive_crossing_pose_count': len(positive),
        'crossing_at_percent': [r['percent'] for r in positive],
        'largest_number_crossing_pairs': max((r['crossing_triangle_pairs'] for r in rows)),
        'minimum_axis_separation': min((r['axis_separation_lower_bound'] for r in rows)),
        'full_open': endpoint,
        'poses': rows,
    }
results = []
for case in receipt['cases']:
    row = ring_geometry(case)
    results.append(row)
    print(case['era'], case['region'], row['positive_crossing_pose_count'], row['largest_number_crossing_pairs'], row['minimum_axis_separation'], flush=True)
result = {k: receipt[k] for k in ['portable', 'script', 'gpu', 'model', 'errors']}
result['blender_version'] = __import__('bpy').app.version_string
result['method'] = (
    'Closed registration and each 2% UI slider increment to 100%, then a 0% reassembly. '
    'Counts describe strict transverse triangle-pair intersections. For covers, the '
    'compared neighbor combines all rendered pieces in its era-specific compartment. The '
    'compartment group is hidden at zero; its transform was still checked as the limiting '
    'shut pose. Wing checks compare full imported left and right mantle surfaces, each '
    'opened in isolation. This boundedly tests selected digital meshes; inter-sample or '
    'untested pairs can still intersect.'
)
result['checks'] = results
dest.write_text(json.dumps(result, indent=2) + '\n')
