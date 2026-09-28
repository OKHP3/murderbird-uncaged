"""Read-only rest-frame V11 attempt-05 cervical-owner inventory."""
from pathlib import Path
import hashlib
import json
import bpy

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'package.json').is_file())
SOURCE = ROOT / 'assets/models/uncaged-silhouette-v11/attempt-05/murderbird-silhouette-v11.blend'
EXPECTED_SHA256 = '28cf0e70e46fca5ea07b1d583ad1ec6492201ed865a0858b1c1da4fc355f9c0f'
SCRIPT = Path(__file__).resolve()
OUTPUT = SCRIPT.with_name('source-neck-inventory.json')
OWNERS = {'neck', 'cervical-upper'}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def rv(values):
    return [round(float(value), 9) for value in values]


def bounds(vertices):
    return {'minM': rv([min(v[i] for v in vertices) for i in range(3)]),
            'maxM': rv([max(v[i] for v in vertices) for i in range(3)])}


assert sha(SOURCE) == EXPECTED_SHA256
assert Path(bpy.data.filepath).resolve() == SOURCE.resolve()
bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()

pivots = []
for obj in sorted((o for o in bpy.data.objects if o.type == 'EMPTY'), key=lambda o: o.name):
    pivots.append({'name': obj.name, 'parent': obj.parent.name if obj.parent else None,
                   'worldCenterM': rv(obj.matrix_world.translation)})

meshes = []
for obj in sorted((o for o in bpy.data.objects if o.type == 'MESH' and o.parent and o.parent.name in OWNERS), key=lambda o: o.name):
    assert obj.parent.name in OWNERS
    assert not any(parent.name == 'head' for parent in (obj.parent, obj.parent.parent) if parent)
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        matrix = evaluated.matrix_world.copy()
        vertices = [matrix @ vert.co for vert in mesh.vertices]
        mesh.calc_loop_triangles()
        meshes.append({
            'name': obj.name,
            'parent': obj.parent.name,
            'parentOfOwner': obj.parent.parent.name if obj.parent.parent else None,
            'exteriorEras': obj.get('exteriorEras'),
            'region': obj.get('region'),
            'surfaceRole': obj.get('surfaceRole'),
            'worldBoundsM': bounds(vertices) if vertices else None,
            'evaluatedVertexCount': len(vertices),
            'evaluatedTriangleCount': len(mesh.loop_triangles),
        })
    finally:
        evaluated.to_mesh_clear()

report = {
    'status': 'read-only evaluated source inventory; rest frame 1',
    'source': {'path': str(SOURCE.relative_to(ROOT)), 'sha256': EXPECTED_SHA256,
               'bytes': SOURCE.stat().st_size, 'blenderVersion': bpy.app.version_string,
               'frame': bpy.context.scene.frame_current},
    'extractor': {'path': str(SCRIPT.relative_to(ROOT)), 'sha256': sha(SCRIPT),
                  'units': 'meters, evaluated world coordinates'},
    'pivotWorldPositions': {'count': len(pivots), 'pivots': pivots},
    'neckOwnedMeshes': {'ownerNames': sorted(OWNERS), 'meshCount': len(meshes), 'meshes': meshes},
    'limits': ['Only direct mesh children of neck and cervical-upper are inventoried; head-owned meshes are excluded.',
               'Rest bounds do not establish moving clearance or mechanical fit.',
               'No model, runtime, or export files were changed.'],
}
OUTPUT.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'output': str(OUTPUT), 'outputSha256': sha(OUTPUT),
                  'sourceSha256': EXPECTED_SHA256, 'meshCount': len(meshes),
                  'pivotCount': len(pivots)}, indent=2))
