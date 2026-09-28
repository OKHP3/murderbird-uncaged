"""Parity and proximity follow-up for only the two identified exterior blockers."""
from pathlib import Path
import hashlib
import json
import math

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[5]
NATIVE = ROOT / 'assets/models/uncaged-bill-root-fixing-study-v1/murderbird-bill-root-fixing-study-v1.blend'
NATIVE_SHA = '4d7568d1c2ba7cab716876f57a6c20cb6a788d4daeef1d5d34f85c1910ed2bbe'
VISIBILITY = Path(__file__).resolve().parent / 'visibility-audit.json'
VISIBILITY_SHA = '59ee59e117f27d8c45386229b224c87c72b2866aa1364b3df077103259fcb8dc'
OUT = Path(__file__).resolve().parent / 'blocker-parity.json'
PAIRS = [('Bill root fixing', 'Forged orbital mounting plate -1'),
         ('Bill root fixing.002', 'Forged orbital mounting plate 1')]
DIRECTIONS = [
    Vector((1, math.sqrt(2), math.sqrt(3))).normalized(),
    Vector((math.sqrt(5), -1, math.sqrt(7))).normalized(),
    Vector((-math.sqrt(11), math.sqrt(13), 1)).normalized(),
    Vector((-1, -math.sqrt(17), math.sqrt(19))).normalized(),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path):
    return {'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size, 'sha256': sha(path)}


def surface(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh(); mesh.calc_loop_triangles()
    matrix = evaluated.matrix_world.copy()
    points = [matrix @ v.co for v in mesh.vertices]
    triangles = [tuple(t.vertices) for t in mesh.loop_triangles]
    tree = BVHTree.FromPolygons(points, triangles, all_triangles=True, epsilon=0)
    centers = [sum((points[i] for i in poly.vertices), Vector()) / len(poly.vertices)
               for poly in mesh.polygons if len(poly.vertices)]
    topology = {'vertices': len(points), 'polygons': len(mesh.polygons), 'evaluatedLoopTriangles': len(triangles)}
    evaluated.to_mesh_clear()
    return points, centers, tree, topology


def hit_count(tree, point, direction):
    current = point + direction * 1e-5
    count = 0
    for _ in range(128):
        hit = tree.ray_cast(current, direction, 2.0)
        if hit[0] is None:
            break
        count += 1
        current = hit[0] + direction * 1e-6
    return count


def classify(tree, point):
    counts = [hit_count(tree, point, direction) for direction in DIRECTIONS]
    parity = [n % 2 for n in counts]
    state = ('inside' if parity[0] else 'outside') if len(set(parity)) == 1 else 'direction-disagreement'
    return {'pointWorldXYZM': [float(v) for v in point], 'rayHitCounts': counts,
            'oddEvenParities': parity, 'classification': state}


def quantile(values, fraction):
    ordered = sorted(values)
    return ordered[min(len(ordered)-1, math.ceil(fraction*len(ordered))-1)] if ordered else None


def main():
    assert sha(NATIVE) == NATIVE_SHA
    assert sha(VISIBILITY) == VISIBILITY_SHA, 'Pinned visibility audit changed'
    assert not OUT.exists(), 'Refusing to overwrite blocker parity receipt'
    bpy.ops.wm.open_mainfile(filepath=str(NATIVE)); bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    rows = []
    for pin_name, blocker_name in PAIRS:
        pin_points, pin_centers, _, pin_topology = surface(bpy.data.objects[pin_name], depsgraph)
        blocker_points, _, blocker_tree, blocker_topology = surface(bpy.data.objects[blocker_name], depsgraph)
        vertex_rows = [classify(blocker_tree, p) for p in pin_points]
        face_rows = [classify(blocker_tree, p) for p in pin_centers]
        center = sum(pin_points, Vector()) / len(pin_points)
        centroid_row = classify(blocker_tree, center)
        distances = [blocker_tree.find_nearest(point)[3] for point in pin_points]
        owner = bpy.data.objects[blocker_name].parent.name if bpy.data.objects[blocker_name].parent else None
        rows.append({'pin': pin_name, 'blocker': blocker_name, 'blockerOwner': owner,
                     'pinTopology': pin_topology, 'blockerTopology': blocker_topology,
                     'parityAgainstExactBlocker': {
                         'vertices': {state: sum(r['classification'] == state for r in vertex_rows)
                                      for state in ('inside','outside','direction-disagreement')},
                         'polygonCenters': {state: sum(r['classification'] == state for r in face_rows)
                                            for state in ('inside','outside','direction-disagreement')},
                         'centroid': centroid_row['classification'],
                         'ambiguousExamples': [r for r in vertex_rows + face_rows
                                               if r['classification'] == 'direction-disagreement'][:4]},
                     'nearestBlockerSurfaceDistanceFromPinVerticesM': {
                         'min': min(distances), 'median': quantile(distances, .5), 'p90': quantile(distances, .9),
                         'max': max(distances)}})
    result = {'status': 'targeted read-only parity/proximity for the only two exterior blockers identified by the v2 line-of-sight audit',
              'generatedAtUtc': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
              'blenderVersion': bpy.app.version_string,
              'native': artifact(NATIVE), 'visibilityAudit': artifact(VISIBILITY),
              'script': artifact(Path(__file__).resolve()),
              'directions': [[float(v) for v in d] for d in DIRECTIONS],
              'method': 'Parity and nearest evaluated surface distance use only the named pin/blocker pairs. Both evaluated surfaces are tessellated with calc_loop_triangles().',
              'pairs': rows,
              'limits': ['Finite odd/even parity samples do not prove absence of local triangle crossing when every sample is outside.',
                         'Nearest sampled pin-vertex distance is unsigned; it distinguishes a sampled gap from sampled coincidence but is not a complete surface separation certificate.',
                         'No other head geometry was swept or classified in this follow-up.']}
    with OUT.open('x') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    print(json.dumps({'pairs': [{'pin': r['pin'], 'blocker': r['blocker'],
                                 'parity': r['parityAgainstExactBlocker'],
                                 'distance': r['nearestBlockerSurfaceDistanceFromPinVerticesM']} for r in rows],
                      'receipt': str(OUT)}))


if __name__ == '__main__':
    main()
