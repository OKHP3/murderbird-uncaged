"""Derive a read-only mechanism socket proposal from the pinned V22 frame04 native."""
import bpy
import hashlib
import json
import math
import os
import shutil
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
BASE_REL = 'assets/models/whole-character-v21/attempt-construction06/murderbird-whole-character-v21.blend'
BASE_SHA = '79ad3e368e7b75edbbc758b1264a1ccaf34f284c6ca185ee8441875576a6f54c'
NATIVE_REL = 'assets/models/whole-character-v22/attempt-frame04/murderbird-whole-character-v22.blend'
NATIVE_SHA = 'b3ac4677d2e76a0e08544323306c07f2ed7e61cd381d274a944d8e5b87031d1f'
BUILDER_REL = 'assets/audit/whole-character-v22/attempt-frame04/executed-builder.py'
BUILDER_SHA = 'e454aa779470ec27a80941ca30ed6fbadb718ac4c31a2e0f66ef9cf09766f818'
BUILDER_RECEIPT_REL = 'assets/audit/whole-character-v22/attempt-frame04/receipt.json'
OUT_REL = 'assets/audit/whole-character-v22/attempt-frame04/socket-proposal'
OUT = ROOT / OUT_REL
FEET_SUBTREES = {'left-foot', 'right-foot'}
HEAD_SUBTREE = {'head'}
RING_SOURCES = {
    'bodyPoint': {'pattern': 'V21 neck root breast support bridge {sign}', 'owner': 'body', 'ringIndex': 1, 'ringCount': 3, 'verticesPerRing': 16},
    'neckPoint': {'pattern': 'V21 cervical root load bow {sign}', 'owner': 'neck', 'ringIndex': 2, 'ringCount': 4, 'verticesPerRing': 20},
}


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def artifact(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'bytes': path.stat().st_size}


def assert_pinned(path, expected):
    if not path.is_file() or sha(path) != expected:
        raise RuntimeError('Pinned hash mismatch: ' + str(path))


def ease(t):
    t = max(0.0, min(1.0, float(t)))
    return t * t * (3.0 - 2.0 * t)


def smooth(z, stops):
    if z <= stops[0][0]:
        return stops[0][1]
    for (z0, v0), (z1, v1) in zip(stops, stops[1:]):
        if z <= z1:
            return v0 + (v1 - v0) * ease((z - z0) / (z1 - z0))
    return stops[-1][1]


def frame_point(point, params):
    """Literal point mapping from the hash-pinned frame04 builder."""
    x, y, z = point
    shortening = (params['hipSource'] - params['footFixedTop']) * (1.0 - params['legScale'])
    if z <= params['footFixedTop']:
        nz = z
    elif z <= params['hipSource']:
        nz = params['footFixedTop'] + (z - params['footFixedTop']) * params['legScale']
    else:
        nz = z - shortening
    nz += params['neckRise'] * max(0.0, min(1.0, (z - 1.300) / 0.280))
    body_weight = smooth(z, [(0.60, 0.0), (0.875, 1.0), (1.30, 1.0), (1.58, 0.0)])
    nx = x * (1.0 + (params['bodyWidth'] - 1.0) * body_weight)
    if x != 0.0:
        nx -= math.copysign(params['shoulderTuck'] * ease((abs(x) - 0.20) / 0.15) * body_weight, x)
    ny = y * 0.92
    ny += smooth(z, [(1.30, 0.0), (1.455, 0.020), (1.58, -params['headForward'])])
    return Vector((nx, ny, nz))


def native_to_gltf(v):
    return [float(v.x), float(v.z), float(-v.y)]


def gltf_to_native(v):
    return Vector((float(v[0]), -float(v[2]), float(v[1])))


def ancestor_named(obj, wanted):
    cur = obj
    while cur:
        if cur.name in wanted:
            return True
        cur = cur.parent
    return False


def transformed_layout_point(old_value, owner_name, old_owner_matrix, new_owner_matrix, params, mapping_mode='frame'):
    old_local_native = gltf_to_native(old_value)
    old_world = old_owner_matrix @ old_local_native
    if mapping_mode == 'frame':
        mapped_world = frame_point(old_world, params)
    elif mapping_mode == 'head':
        mapped_world = old_world + Vector(params['headRigidDelta'])
    elif mapping_mode == 'fixed':
        mapped_world = old_world.copy()
    else:
        raise ValueError(mapping_mode)
    new_local_native = new_owner_matrix.inverted() @ mapped_world
    return {
        'sourceOwnerLocalGltf': [float(x) for x in old_value],
        'sourceOwnerLocalNative': list(old_local_native),
        'sourceWorldNative': list(old_world),
        'mappedWorldNative': list(mapped_world),
        'proposalOwnerLocalNative': list(new_local_native),
        'proposalOwnerLocalGltf': native_to_gltf(new_local_native),
        'mappingMode': mapping_mode,
    }


def section_center(obj, owner, ring_index=None, ring_count=None, vertices_per_ring=None):
    vertices = list(obj.data.vertices)
    if ring_index is not None:
        assert len(vertices) == ring_count * vertices_per_ring, (obj.name, len(vertices))
        selected = vertices[ring_index * vertices_per_ring:(ring_index + 1) * vertices_per_ring]
    else:
        selected = vertices
    world_points = [obj.matrix_world @ v.co for v in selected]
    world = sum(world_points, Vector()) / len(world_points)
    local = bpy.data.objects[owner].matrix_world.inverted() @ world
    return {
        'mesh': obj.name,
        'owner': owner,
        'ringIndexZeroBased': ring_index,
        'sampleCount': len(selected),
        'nativeWorldCenter': list(world),
        'nativeOwnerLocalCenter': list(local),
        'gltfOwnerLocalPoint': native_to_gltf(local),
        'method': 'Arithmetic centroid of the source mesh vertices in the specified authored section; this is a centerline proposal, not a fitted mounting face.',
    }


def main():
    base = ROOT / BASE_REL
    native = ROOT / NATIVE_REL
    builder = ROOT / BUILDER_REL
    builder_receipt_path = ROOT / BUILDER_RECEIPT_REL
    assert_pinned(base, BASE_SHA)
    assert_pinned(native, NATIVE_SHA)
    assert_pinned(builder, BUILDER_SHA)
    builder_receipt = json.loads(builder_receipt_path.read_text())
    assert builder_receipt['native']['sha256'] == NATIVE_SHA
    assert builder_receipt['source']['sha256'] == BUILDER_SHA
    params_in = builder_receipt['parameters']
    construction = builder_receipt['construction']
    params = {
        'footFixedTop': float(construction['footFixedTop']),
        'hipSource': float(construction['hipSource']),
        'legScale': float(params_in['leg_scale']),
        'neckRise': float(params_in['neck_rise']),
        'headForward': float(params_in['head_forward']),
        'bodyWidth': float(params_in['body_width']),
        'shoulderTuck': float(params_in['shoulder_tuck']),
        'torsoDrop': float(construction['torsoDrop']),
        'headRigidDelta': [float(v) for v in construction['headRigidDelta']],
    }
    assert abs(params['torsoDrop'] - (params['hipSource'] - params['footFixedTop']) * (1 - params['legScale'])) < 1e-9
    assert params['legScale'] == 0.84 and params['neckRise'] == 0.11 and params['headForward'] == 0.065
    assert params['bodyWidth'] == 0.90 and params['shoulderTuck'] == 0.032

    bpy.ops.wm.open_mainfile(filepath=str(base))
    base_body = bpy.data.objects['body']
    old_layout_raw = base_body.get('mechanismLayoutV1')
    if not old_layout_raw:
        raise RuntimeError('Pinned base has no mechanismLayoutV1')
    old_layout = json.loads(old_layout_raw) if isinstance(old_layout_raw, str) else dict(old_layout_raw)
    old_owner_mats = {name: bpy.data.objects[name].matrix_world.copy() for name in ['body', 'right-mantle', 'neck', 'left-thigh', 'right-thigh']}
    old_hip_spacing = abs(bpy.data.objects['left-thigh'].matrix_world.translation.x - bpy.data.objects['right-thigh'].matrix_world.translation.x)
    old_cradle_width = float(old_layout['makerCradleWidth'])

    bpy.ops.wm.open_mainfile(filepath=str(native))
    body = bpy.data.objects['body']
    if body.get('mechanismLayoutV1'):
        raise RuntimeError('Candidate unexpectedly reactivated old mechanismLayoutV1')
    if not body.get('priorV21_mechanismLayoutV1'):
        raise RuntimeError('Candidate lacks archived source mechanism layout')
    archived = json.loads(body['priorV21_mechanismLayoutV1'])
    assert archived == old_layout, 'Archived layout differs from pinned V21 base layout'
    new_owner_mats = {name: bpy.data.objects[name].matrix_world.copy() for name in old_owner_mats}

    # Keep explicitly rigid target trees untouched. Tail control offset here means
    # the maker horn point inside the rigid tail group, distinct from its body-local
    # group origin, which is transformed below.
    proposal = json.loads(json.dumps(old_layout))
    proposal.pop('cervicalSocketProvenanceV21', None)
    proposal['cervicalSocketProposalProvenanceV22'] = {
        'baseNativeSha256': BASE_SHA,
        'frame04NativeSha256': NATIVE_SHA,
        'frame04BuilderSha256': BUILDER_SHA,
        'status': 'separate authored-point proposal; not installed into runtime metadata',
        'refreshedFields': ['makerControlOffsets.neck', 'makerControlOffsets.wing', 'cervical', 'tailPosition', 'distributionPosition', 'transmissionPosition', 'makerCradleWidth'],
    }
    proposal['layoutProposalStatus'] = 'Frame04-derived socket placement proposal only; not active runtime metadata or clearance acceptance.'
    witnesses = []
    for key, owner in [('leg', 'left-foot'), ('tail', 'compact-articulated-tail'), ('jaw', 'jaw')]:
        proposal['makerControlOffsets'][key] = old_layout['makerControlOffsets'][key]
        witnesses.append({'field': 'makerControlOffsets.' + key, 'owner': owner, 'status': 'preserved source local offset because its target tree is rigid under the frame04 mapping'})

    # The wing horn targets right-mantle in src/scene/era-mechanisms.js.
    wing = transformed_layout_point(old_layout['makerControlOffsets']['wing'], 'right-mantle', old_owner_mats['right-mantle'], new_owner_mats['right-mantle'], params)
    proposal['makerControlOffsets']['wing'] = wing['proposalOwnerLocalGltf']
    witnesses.append({'field': 'makerControlOffsets.wing', 'owner': 'right-mantle', **wing})

    # The source helper uses the entire passive intermediate journal mesh centroid.
    journal_l = bpy.data.objects['V21 intermediate passive journal -1']
    journal_r = bpy.data.objects['V21 intermediate passive journal 1']
    neck_m = bpy.data.objects['neck'].matrix_world
    j_l = section_center(journal_l, 'neck')
    j_r = section_center(journal_r, 'neck')
    maker_neck_native = Vector(j_l['nativeOwnerLocalCenter'])
    proposal['makerControlOffsets']['neck'] = native_to_gltf(maker_neck_native)
    witnesses.append({'field': 'makerControlOffsets.neck', 'owner': 'neck', 'selectedMesh': journal_l.name, 'selectedMeshCenter': j_l, 'oppositeJournalCenter': j_r, 'status': 'proposal sampled from the full source mesh centroid, matching the V21 derivation method'})

    # Runtime groups these three origins under body, so map their old glTF-local
    # points through the saved frame04 field and express them in the new body frame.
    for field in ('tailPosition', 'distributionPosition', 'transmissionPosition'):
        mapped = transformed_layout_point(old_layout[field], 'body', old_owner_mats['body'], new_owner_mats['body'], params)
        proposal[field] = mapped['proposalOwnerLocalGltf']
        witnesses.append({'field': field, 'owner': 'body', **mapped})

    proposal['cervical'] = []
    cervical_witnesses = []
    for side, sign in [('left', 1), ('right', -1)]:
        points = {}
        for field, spec in RING_SOURCES.items():
            name = spec['pattern'].format(sign=sign)
            obj = bpy.data.objects[name]
            assert obj.parent.name == spec['owner'] and obj.type == 'MESH'
            points[field] = section_center(obj, spec['owner'], spec['ringIndex'], spec['ringCount'], spec['verticesPerRing'])
        proposal['cervical'].append({'side': side, 'bodyPoint': points['bodyPoint']['gltfOwnerLocalPoint'], 'neckPoint': points['neckPoint']['gltfOwnerLocalPoint']})
        cervical_witnesses.append({'side': side, **points})
    witnesses.append({'field': 'cervical', 'status': 'proposed centers from actual frame04 raw section vertices; no fit/contact proof', 'sides': cervical_witnesses})

    old_margin = old_cradle_width - old_hip_spacing
    new_hip_spacing = abs(bpy.data.objects['left-thigh'].matrix_world.translation.x - bpy.data.objects['right-thigh'].matrix_world.translation.x)
    proposal['makerCradleWidth'] = new_hip_spacing + old_margin
    witnesses.append({
        'field': 'makerCradleWidth',
        'method': 'candidate hip center spacing + retained base margin',
        'baseHipSpacingM': old_hip_spacing,
        'baseCradleWidthM': old_cradle_width,
        'retainedSupportMarginM': old_margin,
        'frame04HipSpacingM': new_hip_spacing,
        'proposalWidthM': proposal['makerCradleWidth'],
        'status': 'width-only layout proposal; support contact/fit not tested',
    })

    # Other rigidly attached control offsets are preserved unless explicitly
    # transformed above; record their target owner mapping for review.
    witnesses.append({'field': 'makerControlOffsets.leg', 'runtimeTarget': 'left-foot', 'status': 'preserved; target subtree remains at fixed world pose'})
    witnesses.append({'field': 'makerControlOffsets.tail', 'runtimeTarget': 'compact-articulated-tail', 'status': 'preserved target-local point; tail group origin above is separately re-mapped'})
    witnesses.append({'field': 'makerControlOffsets.jaw', 'runtimeTarget': 'jaw', 'status': 'preserved; head/jaw subtree receives rigid translation'})

    # The candidate layout is emitted separately and never assigned to body.
    layout_out = OUT / 'mechanism-layout-proposal.json'
    receipt_out = OUT / 'receipt.json'
    source_copy = OUT / 'executed-derive-mechanism-layout-v22.py'
    OUT.mkdir(parents=True, exist_ok=True)
    if layout_out.exists() or receipt_out.exists() or source_copy.exists():
        raise RuntimeError('Refusing to overwrite proposal artifact files')
    shutil.copyfile(__file__, source_copy)
    receipt = {
        'status': 'read-only socket derivation proposal; not copied to model metadata, not a clearance or functional-fit result',
        'inputs': {
            'baseNative': artifact(base),
            'frame04Native': artifact(native),
            'frame04Builder': artifact(builder),
            'frame04BuilderReceipt': artifact(builder_receipt_path),
        },
        'source': artifact(source_copy),
        'coordinateConversion': 'Native XYZ to glTF owner-local XYZ: (native X, native Z, -native Y); all recorded proposal points are owner-local.',
        'frame04Mapping': {
            'parameters': params,
            'formula': 'Exact continuous frame_point mapping transcribed from the SHA-pinned frame04 executed-builder.py; point targets first convert source glTF owner-local to source world native, map, then convert through candidate owner inverse to glTF owner-local.',
            'fixedRules': ['Points in left/right-foot subtrees remain fixed.', 'Points in head subtree use the declared rigid head delta.', 'Other mapped points use continuous frame_point including shoulder tuck and fore/aft/neck terms.'],
        },
        'historicalSourceMapping': old_layout,
        'proposal': proposal,
        'witnesses': witnesses,
        'limits': [
            'Proposal remains a separate JSON artifact; neither native model nor runtime was modified.',
            'Raw ring means identify authored geometric centers only; no mount surface, bearing fit, fastener, swept clearance, force path, or era-specific completeness is established.',
            'Unchanged offsets remain historical source values where the requested owner tree is rigid; no broader runtime socket audit is implied.',
        ],
    }
    layout_out.write_text(json.dumps(proposal, indent=2, sort_keys=True) + '\n')
    receipt['proposalArtifact'] = artifact(layout_out)
    receipt_out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'proposal': str(layout_out), 'receipt': str(receipt_out), 'proposalSha256': sha(layout_out), 'sourceSha256': sha(source_copy), 'neckMakerOffset': proposal['makerControlOffsets']['neck'], 'cervical': proposal['cervical'], 'makerCradleWidth': proposal['makerCradleWidth'], 'otherTransformed': {k: proposal[k] for k in ('tailPosition', 'distributionPosition', 'transmissionPosition')}}, indent=2))


main()
