"""Export the pinned bill-root-fixing native study as a diagnostic GLB only."""
from pathlib import Path
import hashlib
import json
import runpy
import shutil
import struct

import bpy

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'assets/models/uncaged-bill-root-fixing-study-v1/murderbird-bill-root-fixing-study-v1.blend'
NATIVE_SHA = '4d7568d1c2ba7cab716876f57a6c20cb6a788d4daeef1d5d34f85c1910ed2bbe'
HELPER = ROOT / 'scripts/build-uncaged-alignment-v7.py'
HELPER_SHA = '39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'
EXPORT_SCRIPT = Path(__file__).resolve()
GLB = NATIVE.with_suffix('.glb')
AUDIT = ROOT / 'assets/audit/uncaged-bill-root-fixing-study-v1/runtime'
PINS = [f'Bill root fixing{s}' for s in ('', '.001', '.002', '.003')]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path):
    return {'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size, 'sha256': sha(path)}


def read_glb_json(path):
    data = path.read_bytes()
    magic, version, length = struct.unpack_from('<4sII', data, 0)
    assert magic == b'glTF' and version == 2 and length == len(data)
    chunk_length, chunk_type = struct.unpack_from('<II', data, 12)
    assert chunk_type == 0x4E4F534A
    return json.loads(data[20:20+chunk_length].decode('utf-8').rstrip(' \0'))


def main():
    assert sha(NATIVE) == NATIVE_SHA, 'Pinned authoring native changed'
    assert sha(HELPER) == HELPER_SHA, 'Frozen V7 exporter helper changed'
    assert not GLB.exists(), f'Refusing to overwrite diagnostic GLB: {GLB}'
    assert not AUDIT.exists(), f'Refusing to overwrite runtime receipt directory: {AUDIT}'

    h = runpy.run_path(str(HELPER), run_name='bill_root_export_helpers')
    bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
    bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
    snapshot = h['scene_snapshot']()
    assert len(snapshot['meshes']) == 699 and len(snapshot['empties']) == 51 and len(snapshot['curves']) == 462
    groups = {}
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        assert obj.parent and all(obj.get(k) for k in ('exteriorEras', 'region', 'surfaceRole')), obj.name
        key = (obj.parent.name, obj.get('exteriorEras'), obj.get('region'), obj.get('surfaceRole'))
        groups.setdefault(key, []).append(obj.name)
    assert len(PINS) == 4 and all(name in snapshot['meshes'] for name in PINS)
    pin_records = {name: {'parent': snapshot['meshes'][name]['parent'],
                          'worldMatrix': snapshot['meshes'][name]['matrix'],
                          'meshSignature': snapshot['meshes'][name]['mesh']} for name in PINS}

    AUDIT.mkdir(parents=True, exist_ok=False)
    copy_path = AUDIT / 'executed-exporter.py'
    shutil.copy2(EXPORT_SCRIPT, copy_path)
    h['export_from_reopened_native'](NATIVE, GLB, snapshot, {})
    assert sha(NATIVE) == NATIVE_SHA, 'Native bytes changed during export'
    glb_json = read_glb_json(GLB)
    node_names = {node.get('name') for node in glb_json.get('nodes', []) if node.get('name')}
    pivot_names = set(snapshot['empties'])
    assert pivot_names <= node_names, f'Export is missing pivot nodes: {sorted(pivot_names-node_names)}'
    for name in PINS:
        assert name not in node_names, f'Unbatched individual pin node unexpectedly exported: {name}'
    batch = [{'owner': key[0], 'eras': key[1], 'region': key[2], 'role': key[3],
              'members': sorted(names)} for key, names in sorted(groups.items())]
    glb_mesh_nodes = [node for node in glb_json.get('nodes', []) if 'mesh' in node]
    receipt = {
        'status': 'diagnostic native-derived GLB; no app selection, gallery selection, publication, or acceptance',
        'blenderVersion': bpy.app.version_string,
        'native': artifact(NATIVE), 'glb': artifact(GLB), 'helper': artifact(HELPER),
        'exporter': artifact(copy_path),
        'nativeCounts': {'meshObjects': 699, 'pivots': 51, 'guideCurves': 462,
                         'meshDataBatchesBeforeExport': len(groups)},
        'glbCounts': {'nodes': len(glb_json.get('nodes', [])),
                      'meshNodes': len(glb_mesh_nodes),
                      'meshes': len(glb_json.get('meshes', [])),
                      'pivotNodeNamesPresent': len(pivot_names & node_names)},
        'reseatedPinsInNative': pin_records,
        'batches': batch,
        'nativeBytesUnchangedAfterExport': sha(NATIVE) == NATIVE_SHA,
        'limits': ['The frozen alignment-v7 exporter applies mesh modifiers and batches only in its reopened export copy.',
                   'This receipt binds the diagnostic GLB to the native scene and checks pivot node names, not independent full GLB geometry parity.',
                   'No browser, app-selection, runtime motion, publication, or owner-acceptance claim.']
    }
    receipt_path = AUDIT / 'export-receipt.json'
    with receipt_path.open('x') as stream:
        json.dump(receipt, stream, indent=2); stream.write('\n')
    readme = AUDIT / 'README.md'
    with readme.open('x') as stream:
        stream.write('# Bill root fixing diagnostic export\n\n')
        stream.write('This GLB is an adjacent diagnostic derivative of the isolated native proposal. The frozen V7 export helper batches by owner, era, region, and role after saving the editable native. It does not select or publish the model.\n\n')
        stream.write('See [export-receipt.json](export-receipt.json) for input/output hashes, native inventory, batches, and limits.\n')
    print(json.dumps({'native': artifact(NATIVE), 'glb': artifact(GLB),
                      'receipt': artifact(receipt_path), 'nativeUnchanged': sha(NATIVE) == NATIVE_SHA,
                      'glbCounts': receipt['glbCounts'], 'batches': len(batch)}))


if __name__ == '__main__':
    main()
