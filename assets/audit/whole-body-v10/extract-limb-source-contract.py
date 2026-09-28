"""Read-only evaluated lower-limb source contract extraction for V10 planning.

Run with Blender 5.2.1 LTS:
  Blender --background --threads 1 <V9 .blend> --python this-script
No native file is saved or modified.
"""
from pathlib import Path
import hashlib
import json
import math
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'assets/models/uncaged-alignment-v9/murderbird-alignment-v9.blend'
SOURCE_SHA256 = '4d7568d1c2ba7cab716876f57a6c20cb6a788d4daeef1d5d34f85c1910ed2bbe'
SCRIPT = Path(__file__).resolve()
OUTPUT = SCRIPT.with_name('limb-source-contract.json')


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def vec(v):
    return [round(float(c), 9) for c in v]


def dist(a, b):
    return round((Vector(a) - Vector(b)).length, 9)


def world_evaluated_vertices(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        matrix = evaluated.matrix_world.copy()
        return [matrix @ v.co for v in mesh.vertices]
    finally:
        evaluated.to_mesh_clear()


def matches(owner, name):
    n = name.lower()
    side = 'left' if owner.startswith('left') else 'right'
    if owner.endswith('thigh'):
        return ('tapered passive load rail' in n or 'articulated bearing core' in n or
                'open stepped bearing race' in n or 'bearing race pin' in n or
                'shaped thigh guard' in n or n.startswith('limb sheath fixing'))
    if owner.endswith('shin'):
        return ('tapered passive load rail' in n or 'articulated bearing core' in n or
                'open stepped bearing race' in n or 'bearing race pin' in n or
                'shaped shin guard' in n or n.startswith('limb sheath fixing'))
    if owner.endswith('foot'):
        return ('metatarsal passive rail' in n or 'articulated bearing core' in n or
                'open stepped bearing race' in n or 'bearing race pin' in n or
                'curved instep guard' in n or 'rear hallux sheath' in n)
    return False


def category(name):
    n = name.lower()
    if 'load rail' in n or 'metatarsal passive rail' in n:
        return 'load_member'
    if 'bearing core' in n or 'stepped bearing race' in n or 'bearing race pin' in n or n.startswith('limb sheath fixing'):
        return 'bearing'
    if 'guard' in n or 'sheath' in n:
        return 'guard'
    return 'other'


def object_record(obj, vertices, start, end):
    axis = end - start
    length = axis.length
    unit = axis.normalized()
    stations = [(v - start).dot(unit) for v in vertices]
    lo, hi = min(stations), max(stations)
    end_window = max(0.001, min(0.006, length * 0.02))
    low_group = [v for v, s in zip(vertices, stations) if s <= lo + end_window]
    high_group = [v for v, s in zip(vertices, stations) if s >= hi - end_window]
    low_center = sum(low_group, Vector()) / len(low_group)
    high_center = sum(high_group, Vector()) / len(high_group)
    bmin = [min(v[i] for v in vertices) for i in range(3)]
    bmax = [max(v[i] for v in vertices) for i in range(3)]
    closest_start = min(vertices, key=lambda v: (v - start).length)
    closest_end = min(vertices, key=lambda v: (v - end).length)
    props = {k: obj.get(k) for k in ('surfaceRole', 'exteriorEras') if obj.get(k) is not None}
    return {
        'name': obj.name,
        'category': category(obj.name),
        'owner': obj.parent.name if obj.parent else None,
        'rigidParent': obj.parent.name if obj.parent else None,
        'surfaceProperties': props,
        'vertexCountEvaluated': len(vertices),
        'worldBoundsM': {'min': vec(bmin), 'max': vec(bmax)},
        'segmentProjection': {
            'startPivot': vec(start), 'endPivot': vec(end),
            'lengthM': round(length, 9),
            'minStationM': round(lo, 9), 'maxStationM': round(hi, 9),
            'minStationFraction': round(lo / length, 9),
            'maxStationFraction': round(hi / length, 9),
            'lowCapMeanWorldM': vec(low_center),
            'highCapMeanWorldM': vec(high_center),
            'lowCapToStartPivotM': dist(low_center, start),
            'highCapToEndPivotM': dist(high_center, end),
            'nearestVertexToStartPivotM': dist(closest_start, start),
            'nearestVertexToEndPivotM': dist(closest_end, end),
        },
        'interpretationLimit': 'Vertex projection and nearest-vertex distances locate evaluated mesh relative to pivots; they are not surface-contact or collision proof.'
    }


assert sha256(SOURCE) == SOURCE_SHA256, 'V9 source hash mismatch'
assert bpy.data.filepath and Path(bpy.data.filepath).resolve() == SOURCE.resolve(), 'Loaded native is not exact V9 source'
bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()

sides = {}
for side in ('left', 'right'):
    pivots = {
        'hip': f'{side}-thigh',
        'knee': f'{side}-shin',
        'ankle': f'{side}-foot',
        'distalFoot': f'{side}-toes',
    }
    pivot_records = {}
    for role, name in pivots.items():
        obj = bpy.data.objects.get(name)
        assert obj and obj.type == 'EMPTY', f'Missing expected pivot {name}'
        pivot_records[role] = {
            'object': name,
            'parent': obj.parent.name if obj.parent else None,
            'worldCenterM': vec(obj.matrix_world.translation),
            'worldMatrix': [[round(float(c), 12) for c in row] for row in obj.matrix_world],
        }
    segment_pairs = {
        'thigh': (pivot_records['hip']['worldCenterM'], pivot_records['knee']['worldCenterM'], pivots['hip']),
        'shin': (pivot_records['knee']['worldCenterM'], pivot_records['ankle']['worldCenterM'], pivots['knee']),
        'ankle-foot': (pivot_records['ankle']['worldCenterM'], pivot_records['distalFoot']['worldCenterM'], pivots['ankle']),
    }
    sections = {}
    for section, (start_raw, end_raw, owner) in segment_pairs.items():
        start, end = Vector(start_raw), Vector(end_raw)
        records = []
        for obj in bpy.data.objects:
            if obj.type != 'MESH' or not obj.parent or obj.parent.name != owner or not matches(owner, obj.name):
                continue
            verts = world_evaluated_vertices(obj, depsgraph)
            if verts:
                records.append(object_record(obj, verts, start, end))
        records.sort(key=lambda row: (row['category'], row['name']))
        sections[section] = {
            'rigidOwner': owner,
            'ownerParent': bpy.data.objects[owner].parent.name if bpy.data.objects[owner].parent else None,
            'startPivot': pivots['hip'] if section == 'thigh' else (pivots['knee'] if section == 'shin' else pivots['ankle']),
            'endPivot': pivots['knee'] if section == 'thigh' else (pivots['ankle'] if section == 'shin' else pivots['distalFoot']),
            'existingMeshes': records,
        }
    sides[side] = {'pivots': pivot_records, 'sections': sections}

contract = {
    'status': 'read-only native source contract; evaluated rest-frame measurements',
    'source': {
        'path': str(SOURCE.relative_to(ROOT)),
        'sha256': SOURCE_SHA256,
        'loadedFile': str(Path(bpy.data.filepath).resolve()),
        'blenderVersion': bpy.app.version_string,
        'frame': bpy.context.scene.frame_current,
        'sceneName': bpy.context.scene.name,
        'evaluatedAfter': 'scene.frame_set(1); view_layer.update(); depsgraph evaluated_get/to_mesh; matrix_world applied to vertices',
    },
    'extractor': {
        'path': str(SCRIPT.relative_to(ROOT)),
        'sha256': sha256(SCRIPT),
        'outputPath': str(OUTPUT.relative_to(ROOT)),
        'measurementUnits': 'meters in evaluated world coordinates',
    },
    'sides': sides,
    'safeSameOwnerThicknessCandidates': {
        'confirmedOwnershipAndEra': [
            'left tapered passive load rail', 'left tapered passive load rail.001',
            'right tapered passive load rail', 'right tapered passive load rail.001',
            'left tapered passive load rail.002', 'left tapered passive load rail.003',
            'right tapered passive load rail.002', 'right tapered passive load rail.003',
            'left metatarsal passive rail', 'left metatarsal passive rail.001',
            'right metatarsal passive rail', 'right metatarsal passive rail.001',
        ],
        'basis': 'Each listed native mesh is rigid-parented to its own thigh/shin/foot assembly owner and declares exteriorEras maker,mechanic,builder. It can be thickened inward on that same owner while its evaluated end stations remain fixed.',
        'boundary': 'This is an ownership/end-station scope recommendation only. It does not establish clearance to guards, bearing pins, neighboring meshes, or dynamic pose envelopes. Keep pivot transforms and existing end-seat positions fixed; verify resulting surface clearance separately.',
        'notRecommendedForThickening': 'Bearing cores/races/pins and terminal joint/foot guards define bearing envelopes or articulated clearances; this extraction does not authorize changing their profiles.',
    },
    'limits': [
        'Native scene frame 1 is rest-state only; no browser pose, runtime pose packet, continuous motion, or swept clearance was sampled.',
        'Endpoint projections and vertex distances do not prove watertight attachment, contact, penetration, collision freedom, load capacity, or physical validity.',
        'No source geometry or transforms were edited; no native was saved.',
    ],
}
OUTPUT.write_text(json.dumps(contract, indent=2) + '\n')
print(json.dumps({'output': str(OUTPUT), 'outputSha256': sha256(OUTPUT), 'sourceSha256': SOURCE_SHA256, 'sidePivotCounts': {s: len(v['pivots']) for s, v in sides.items()}, 'meshCounts': {s: {sec: len(data['existingMeshes']) for sec, data in v['sections'].items()} for s, v in sides.items()}}, indent=2))
