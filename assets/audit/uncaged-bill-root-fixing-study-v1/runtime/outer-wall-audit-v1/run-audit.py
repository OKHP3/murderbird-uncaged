"""Read-only outside-in wall order and pin-vs-blade1 parity audit."""
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
GLB = ROOT / 'assets/models/uncaged-bill-root-fixing-study-v1/murderbird-bill-root-fixing-study-v1.glb'
GLB_SHA = 'f5c0f5ad99ace316ed84426d2a1148a093706612c9602d78b93023d46d989e6e'
OUT = Path(__file__).resolve().parent
PINS = [f'Bill root fixing{s}' for s in ('', '.001', '.002', '.003')]
TARGETS = ['Profiled upper bill blade 0', 'Profiled upper bill blade 1']
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


def evaluated_triangles(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    matrix = evaluated.matrix_world.copy()
    points = [matrix @ vertex.co for vertex in mesh.vertices]
    triangles = [tuple(loop_tri.vertices) for loop_tri in mesh.loop_triangles]
    edge_uses = {}
    for tri in triangles:
        for a, b in zip(tri, (tri[1], tri[2], tri[0])):
            key = (min(a, b), max(a, b))
            edge_uses[key] = edge_uses.get(key, 0) + 1
    tree = BVHTree.FromPolygons(points, triangles, all_triangles=True, epsilon=0)
    face_centers = []
    for polygon in mesh.polygons:
        ids = list(polygon.vertices)
        if ids:
            face_centers.append(sum((points[i] for i in ids), Vector()) / len(ids))
    topology = {'vertices': len(points), 'polygons': len(mesh.polygons), 'evaluatedLoopTriangles': len(triangles),
                'triangulatedBoundaryEdges': sum(count == 1 for count in edge_uses.values()),
                'triangulatedNonManifoldEdges': sum(count != 2 for count in edge_uses.values())}
    evaluated.to_mesh_clear()
    return {'points': points, 'triangles': triangles, 'faceCenters': face_centers,
            'tree': tree, 'topology': topology}


def ray_hits(tree, origin, direction, max_distance=1.0):
    hits = []
    current = origin.copy()
    remaining = max_distance
    traveled = 0.0
    for _ in range(128):
        loc, normal, tri_index, distance = tree.ray_cast(current, direction, remaining)
        if loc is None:
            break
        hits.append({'pointWorldXYZM': [float(v) for v in loc],
                     'normalWorldXYZ': [float(v) for v in normal],
                     'triangleIndex': int(tri_index), 'distanceFromRayOriginM': float(traveled + distance)})
        step = distance + 1e-6
        current = loc + direction * 1e-6
        traveled += step
        remaining -= step
        if remaining <= 1e-6:
            break
    return hits


def classify_point(tree, point):
    counts = []
    for direction in DIRECTIONS:
        intersections = ray_hits(tree, point + direction * 1e-5, direction, 2.0)
        counts.append(len(intersections))
    parities = [count % 2 for count in counts]
    classification = ('inside' if parities[0] else 'outside') if len(set(parities)) == 1 else 'direction-disagreement'
    return {'pointWorldXYZM': [float(v) for v in point], 'rayHitCounts': counts,
            'oddEvenParities': parities, 'classification': classification}


def count_states(rows):
    return {state: sum(row['classification'] == state for row in rows)
            for state in ('inside', 'outside', 'direction-disagreement')}


def main():
    assert sha(NATIVE) == NATIVE_SHA and sha(GLB) == GLB_SHA
    assert not (OUT / 'outer-wall-audit.json').exists(), 'Refusing to overwrite outer-wall receipt'
    bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
    bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    targets = {name: evaluated_triangles(bpy.data.objects[name], depsgraph) for name in TARGETS}
    rows = []
    for name in PINS:
        pin_obj = bpy.data.objects[name]
        pin = evaluated_triangles(pin_obj, depsgraph)
        centroid = sum(pin['points'], Vector()) / len(pin['points'])
        side = 1 if centroid.x > 0 else -1
        direction = Vector((-side, 0, 0))
        outside_origin = Vector((side * .4, centroid.y, centroid.z))
        per_target = {}
        combined = []
        for target_name, target in targets.items():
            hits = ray_hits(target['tree'], outside_origin, direction, .8)
            per_target[target_name] = hits
            if hits:
                combined.append({'mesh': target_name, **hits[0]})
        first = min(combined, key=lambda hit: hit['distanceFromRayOriginM']) if combined else None
        blade1_vertices = [classify_point(targets[TARGETS[1]]['tree'], p) for p in pin['points']]
        blade1_centers = [classify_point(targets[TARGETS[1]]['tree'], p) for p in pin['faceCenters']]
        blade1_centroid = classify_point(targets[TARGETS[1]]['tree'], centroid)
        blade0_vertices = [classify_point(targets[TARGETS[0]]['tree'], p) for p in pin['points']]
        blade0_centers = [classify_point(targets[TARGETS[0]]['tree'], p) for p in pin['faceCenters']]
        blade0_centroid = classify_point(targets[TARGETS[0]]['tree'], centroid)
        rows.append({
            'pin': name, 'anatomicalSide': 'left' if side > 0 else 'right',
            'centroidWorldXYZM': [float(v) for v in centroid],
            'outsideInRay': {'originWorldXYZM': [float(v) for v in outside_origin],
                             'directionWorldXYZ': [float(v) for v in direction],
                             'targetHits': per_target, 'firstHitAcrossTwoBlades': first},
            'blade1Containment': {'vertices': count_states(blade1_vertices),
                                  'polygonCenters': count_states(blade1_centers),
                                  'centroid': blade1_centroid['classification'],
                                  'ambiguousExamples': [row for row in blade1_vertices + blade1_centers
                                                        if row['classification'] == 'direction-disagreement'][:4]},
            'blade0ParityCrossCheck': {'vertices': count_states(blade0_vertices),
                                       'polygonCenters': count_states(blade0_centers),
                                       'centroid': blade0_centroid['classification']},
            'pinTopology': pin['topology']
        })
    result = {
        'status': 'read-only outside-in wall-order and blade1 containment diagnosis',
        'generatedAtUtc': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
        'blenderVersion': bpy.app.version_string,
        'native': artifact(NATIVE), 'glb': artifact(GLB), 'script': artifact(Path(__file__).resolve()),
        'sideConvention': '+X anatomical LEFT; -X anatomical RIGHT.',
        'surfaceRepresentation': 'Evaluated meshes from the pinned native, explicitly tessellated with Blender Mesh.calc_loop_triangles(); BVH and odd/even tests use those exact evaluated loop triangles. Polygon centers remain samples on original evaluated faces.',
        'targets': {name: {'parent': bpy.data.objects[name].parent.name if bpy.data.objects[name].parent else None,
                           'topology': surface['topology']}
                    for name, surface in targets.items()},
        'parityDirections': [[float(v) for v in direction] for direction in DIRECTIONS],
        'outsideInRayOriginAbsXM': .4,
        'pins': rows,
        'limits': ['Finite four-direction point parity is a sampled inside/outside classification, not a Boolean volume proof.',
                   'Outside-in axis rays identify the first wall on the pin YZ line; they do not establish design intent or fastening strength.',
                   'This checks only the two upper bill blades and the four root fixings. It is not a full head clearance or motion test.',
                   'The earlier V1 seating generator used its existing surface path; this independent audit uses explicit evaluated loop-triangle tessellation and does not overwrite or revise that historical receipt.']
    }
    output = OUT / 'outer-wall-audit.json'
    with output.open('x') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    print(json.dumps({'pins': {row['pin']: {'firstWall': row['outsideInRay']['firstHitAcrossTwoBlades']['mesh'] if row['outsideInRay']['firstHitAcrossTwoBlades'] else None,
                                         'blade1Vertices': row['blade1Containment']['vertices'],
                                         'blade1PolygonCenters': row['blade1Containment']['polygonCenters'],
                                         'blade1Centroid': row['blade1Containment']['centroid']}
                           for row in rows}, 'receipt': str(output)}))


if __name__ == '__main__':
    main()
