"""Read-only vertex/edge/face-centroid proximity query for bill-root interfaces."""
import bpy, os, json, hashlib, struct
from mathutils import Vector
from mathutils.bvhtree import BVHTree

FASTENERS = [f'Bill root fixing{suffix}' for suffix in ('', '.001', '.002', '.003')]
SURFACES = [
    'Profiled upper bill blade 0', 'Profiled upper bill blade 1',
    'Overlapping nasal hood', 'Cere root transition -1', 'Cere root transition 1',
]

def samples(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    matrix = evaluated.matrix_world
    vertices = [matrix @ vert.co for vert in mesh.vertices]
    faces = [tuple(poly.vertices) for poly in mesh.polygons if len(poly.vertices) >= 3]
    points = list(vertices)
    for poly in mesh.polygons:
        ids = list(poly.vertices)
        if len(ids) < 3:
            continue
        points.append(sum((vertices[index] for index in ids), Vector()) / len(ids))
        for index, next_index in zip(ids, ids[1:] + ids[:1]):
            points.append((vertices[index] + vertices[next_index]) * 0.5)
    tree = BVHTree.FromPolygons(vertices, faces, all_triangles=False, epsilon=0.0)
    evaluated.to_mesh_clear()
    return tree, points

def nearest_samples(points, tree):
    rows = []
    for point in points:
        nearest = tree.find_nearest(point)
        if nearest:
            rows.append((nearest[3], point, nearest[0]))
    return min(rows, key=lambda row: row[0])

def object_identity(obj):
    digest = hashlib.sha256()
    digest.update(obj.name.encode())
    digest.update((obj.parent.name if obj.parent else '').encode())
    for row in obj.matrix_world:
        digest.update(struct.pack('<4d', *(float(value) for value in row)))
    world_vertices = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    for vertex in obj.data.vertices:
        digest.update(struct.pack('<3d', *(float(value) for value in vertex.co)))
    for polygon in obj.data.polygons:
        digest.update(struct.pack('<I', len(polygon.vertices)))
        for index in polygon.vertices:
            digest.update(struct.pack('<I', int(index)))
    materials = [mat.name if mat else None for mat in obj.data.materials]
    digest.update(json.dumps(materials, separators=(',', ':')).encode())
    bounds_min = [min(float(v[i]) for v in world_vertices) for i in range(3)]
    bounds_max = [max(float(v[i]) for v in world_vertices) for i in range(3)]
    return {'parent': obj.parent.name if obj.parent else None, 'role': obj.get('surfaceRole'),
            'region': obj.get('region'), 'vertices': len(obj.data.vertices), 'polygons': len(obj.data.polygons),
            'worldBoundsBlenderXYZMetres': {'min': bounds_min, 'max': bounds_max},
            'materials': materials, 'worldMatrixRows': [[float(value) for value in row] for row in obj.matrix_world],
            'meshWorldTransformSha256': digest.hexdigest()}

def result(a, b, cache):
    tree_a, points_a = cache[a]
    tree_b, points_b = cache[b]
    ab = nearest_samples(points_a, tree_b)
    ba = nearest_samples(points_b, tree_a)
    return {
        'sampledSurfaceDistanceM': min(ab[0], ba[0]),
        'sampledNearestPairs': [
            {'from': a, 'to': b, 'distanceM': ab[0], 'fromPoint': list(ab[1]), 'targetPoint': list(ab[2])},
            {'from': b, 'to': a, 'distanceM': ba[0], 'fromPoint': list(ba[1]), 'targetPoint': list(ba[2])},
        ],
        'bvhFacePairCandidates': len(tree_a.overlap(tree_b)),
        'bvhCandidateLimit': 'Face-pair overlap is broad phase only; may include touching or coplanar candidates and is not a proper-crossing result.'
    }

depsgraph = bpy.context.evaluated_depsgraph_get()
objects = {obj.name: obj for obj in bpy.data.objects if obj.type == 'MESH'}
required = FASTENERS + SURFACES
missing = [name for name in required if name not in objects]
if missing:
    raise RuntimeError('Missing expected native mesh objects: ' + ', '.join(missing))
cache = {name: samples(objects[name], depsgraph) for name in required}
report = {
    'nativePath': bpy.data.filepath,
    'measuredAtBlenderVersion': bpy.app.version_string,
    'space': 'world-space Blender XYZ metres',
    'meshEvaluation': 'evaluated_get(depsgraph).to_mesh(); all source vertices plus each polygon centroid and edge midpoint queried against exact BVH triangles of the other evaluated mesh',
    'scope': {'fasteners': FASTENERS, 'stationaryBillSurfaces': SURFACES},
    'objectIdentity': {name: object_identity(objects[name]) for name in required},
    'fasteners': {pin: {surface: result(pin, surface, cache) for surface in SURFACES} for pin in FASTENERS},
    'stationarySurfaceJunctions': {f'{a} / {b}': result(a, b, cache) for index, a in enumerate(SURFACES) for b in SURFACES[index+1:]},
    'limits': [
        'Proximity is a finite vertex/edge-midpoint/polygon-centroid sample against exact target triangles, not an exhaustive closest-feature solver.',
        'BVH overlap counts are broad-phase candidates, not proof of a proper crossing; coplanar, boundary, and containment relations are not classified.',
        'Only bill-root fixings and five adjacent stationary upper-bill/cere plates are included; this is not a whole-head assembly or jaw-clearance test.'
    ]
}
path = os.environ['AUDIT_JSON_OUT']
with open(path, 'x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
print(json.dumps({'written': path, 'fastenerNames': FASTENERS, 'surfaceNames': SURFACES}))
