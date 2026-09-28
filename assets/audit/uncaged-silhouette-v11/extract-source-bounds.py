"""Read-only evaluated bounds extraction for V10 silhouette planning.

Run:
  Blender --background --threads 1 <V10 attempt-02 native> --python this-script
The source scene is never saved.
"""
from pathlib import Path
import hashlib
import json
import bpy
from mathutils import Vector

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'package.json').is_file())
SOURCE = ROOT / 'assets/models/uncaged-whole-body-v10/attempt-02/murderbird-whole-body-v10.blend'
EXPECTED_SHA256 = '6b2b43209d0474771010f3711f7d7ad2c00521f4d331c22a17d998f61a86c69f'
SCRIPT = Path(__file__).resolve()
OUTPUT = SCRIPT.with_name('source-bounds.json')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def rounded(v):
    return [round(float(x), 9) for x in v]


def bounds(vertices):
    return {'minM': rounded([min(v[i] for v in vertices) for i in range(3)]),
            'maxM': rounded([max(v[i] for v in vertices) for i in range(3)])}


def evaluated_world_vertices(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        matrix = evaluated.matrix_world.copy()
        return [matrix @ vertex.co for vertex in mesh.vertices], len(mesh.loop_triangles)
    finally:
        evaluated.to_mesh_clear()


assert digest(SOURCE) == EXPECTED_SHA256, 'Pinned V10 source SHA mismatch'
assert Path(bpy.data.filepath).resolve() == SOURCE.resolve(), 'Wrong native loaded'
bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()

pivots = []
for obj in sorted((o for o in bpy.data.objects if o.type == 'EMPTY'), key=lambda o: o.name):
    pivots.append({'name': obj.name, 'parent': obj.parent.name if obj.parent else None,
                   'worldCenterM': rounded(obj.matrix_world.translation),
                   'worldMatrix': [[round(float(value), 12) for value in row] for row in obj.matrix_world]})

head_owner_names = {'head', 'jaw', 'cranial-cover', 'upper-bill', 'builder-optics'}
head_meshes = []
owner_aggregates = {}
for obj in sorted((o for o in bpy.data.objects if o.type == 'MESH'), key=lambda o: o.name):
    owner = obj.parent.name if obj.parent else None
    region = obj.get('region')
    role = obj.get('surfaceRole')
    eras = obj.get('exteriorEras')
    vertices, triangle_count = evaluated_world_vertices(obj, depsgraph)
    if not vertices:
        continue
    row = {'name': obj.name, 'parent': owner, 'region': region, 'surfaceRole': role,
           'exteriorEras': eras, 'evaluatedVertexCount': len(vertices),
           'evaluatedTriangleCount': triangle_count, 'worldBounds': bounds(vertices)}
    if owner in head_owner_names or region in {'head', 'optic'}:
        head_meshes.append(row)
    owner_is_body = owner == 'body'
    owner_is_mantle = owner is not None and 'mantle' in owner
    owner_is_leg = (region in {'leg', 'foot'} or
                    (owner is not None and (owner.endswith(('-thigh', '-shin', '-foot', '-toes')) or
                     '-digit-' in owner)))
    if owner_is_body or owner_is_mantle or owner_is_leg:
        group = owner_aggregates.setdefault(owner, {'parent': obj.parent.parent.name if obj.parent and obj.parent.parent else None,
              'regions': set(), 'surfaceRoles': set(), 'exteriorEras': set(),
              'meshCount': 0, 'evaluatedVertexCount': 0, 'evaluatedTriangleCount': 0,
              'worldMin': [float('inf')] * 3, 'worldMax': [float('-inf')] * 3})
        if region: group['regions'].add(region)
        if role: group['surfaceRoles'].add(role)
        if eras: group['exteriorEras'].add(eras)
        group['meshCount'] += 1
        group['evaluatedVertexCount'] += len(vertices)
        group['evaluatedTriangleCount'] += triangle_count
        for i, value in enumerate(bounds(vertices)['minM']): group['worldMin'][i] = min(group['worldMin'][i], value)
        for i, value in enumerate(bounds(vertices)['maxM']): group['worldMax'][i] = max(group['worldMax'][i], value)

aggregates = {}
for owner, data in sorted(owner_aggregates.items()):
    aggregates[owner] = {'parent': data['parent'], 'regions': sorted(data['regions']),
        'surfaceRoles': sorted(data['surfaceRoles']), 'exteriorEras': sorted(data['exteriorEras']),
        'meshCount': data['meshCount'], 'evaluatedVertexCount': data['evaluatedVertexCount'],
        'evaluatedTriangleCount': data['evaluatedTriangleCount'],
        'worldBoundsM': {'min': rounded(data['worldMin']), 'max': rounded(data['worldMax'])}}

report = {
    'status': 'read-only evaluated native bounds for proportion planning',
    'source': {'path': str(SOURCE.relative_to(ROOT)), 'sha256': EXPECTED_SHA256,
        'bytes': SOURCE.stat().st_size, 'blenderVersion': bpy.app.version_string,
        'scene': bpy.context.scene.name, 'frame': bpy.context.scene.frame_current,
        'evaluation': 'scene.frame_set(1), view_layer.update(), evaluated_get(depsgraph), evaluated world matrices'},
    'extractor': {'path': str(SCRIPT.relative_to(ROOT)), 'sha256': digest(SCRIPT),
        'output': str(OUTPUT.relative_to(ROOT)), 'units': 'meters, evaluated world coordinates'},
    'headJawCranialCoverMeshes': {'selection': 'every evaluated mesh whose rigid parent is head/jaw/cranial-cover/upper-bill/builder-optics, or whose region is head/optic; grouped fields retain parent and region',
        'count': len(head_meshes), 'meshes': head_meshes},
    'allPivotCenters': {'count': len(pivots), 'pivots': pivots},
    'bodyMantleLegOwnerAggregates': {'selection': 'body owner, mantle owners, and meshes tagged leg/foot or parented to thigh/shin/foot/toes/digit rigid owners',
        'groupCount': len(aggregates), 'byRigidOwner': aggregates},
    'limits': ['Rest frame only; bounds are not pose envelopes or collision tests.',
        'Bounds report evaluated mesh vertices, not hidden internal construction, author intent, or reference-image measurements.',
        'No native save, geometry edit, application edit, or export was performed.']
}
OUTPUT.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'output': str(OUTPUT), 'outputSha256': digest(OUTPUT),
    'sourceSha256': EXPECTED_SHA256, 'headJawCranialCoverMeshCount': len(head_meshes),
    'pivotCount': len(pivots), 'bodyMantleLegOwnerAggregateCount': len(aggregates)}, indent=2))
