"""Create a diagnostic GLB from V11 attempt-03's reopened native copy.

The saved editable native is opened read-only. The verified V7 helper applies
modifiers/batches only in its in-memory reopened export copy.
"""
from pathlib import Path
import hashlib
import json
import runpy
import shutil
import struct
import bpy

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'assets/models/uncaged-silhouette-v11/attempt-03/murderbird-silhouette-v11.blend'
GLB = NATIVE.with_suffix('.glb')
AUDIT = ROOT / 'assets/audit/uncaged-silhouette-v11/attempt-03'
EXECUTED = AUDIT / 'executed-export.py'
RECEIPT = AUDIT / 'export-receipt.json'
HELPER = ROOT / 'scripts/build-uncaged-alignment-v7.py'
NATIVE_SHA256 = '8ffbc716afd230ab78e053b5a46ebb2334303af4a8d97b322c4516581781d756'
HELPER_SHA256 = '39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def glb_document(path):
    raw = path.read_bytes()
    assert raw[:4] == b'glTF' and struct.unpack_from('<I', raw, 8)[0] == len(raw)
    json_length, json_type = struct.unpack_from('<II', raw, 12)
    assert json_type == 0x4E4F534A
    return json.loads(raw[20:20 + json_length])


assert sha256(NATIVE) == NATIVE_SHA256, 'V11 native SHA mismatch'
assert sha256(HELPER) == HELPER_SHA256, 'Reviewed V7 helper SHA mismatch'
assert Path(bpy.data.filepath).resolve() == NATIVE.resolve(), 'Wrong native opened'
assert not GLB.exists(), f'Refusing to overwrite diagnostic export: {GLB}'
assert not RECEIPT.exists(), 'Refusing to replace existing export receipt'
if EXECUTED.exists():
    assert sha256(EXECUTED) == sha256(__file__), 'Existing frozen exporter differs; preserve it'
else:
    shutil.copy2(__file__, EXECUTED)
assert sha256(EXECUTED) == sha256(__file__)

helpers = runpy.run_path(str(HELPER), run_name='silhouette_v11_export_helpers')
snapshot = helpers['scene_snapshot']()
expected_pivots = snapshot['empties']
assert len(expected_pivots) == 52, f'Expected 52 pivots, found {len(expected_pivots)}'
mods = {obj.name: helpers['modifier_signature'](obj)
        for obj in bpy.data.objects if obj.type == 'MESH' and obj.modifiers}
helpers['export_from_reopened_native'](NATIVE, GLB, snapshot, mods)

native_after = sha256(NATIVE)
assert native_after == NATIVE_SHA256, 'Native changed during export'
assert GLB.is_file() and GLB.stat().st_size > 100_000

document = glb_document(GLB)
exported_node_names = [node.get('name') for node in document.get('nodes', [])]
exported_pivot_names = set(exported_node_names)
missing_pivots = sorted(set(expected_pivots) - exported_pivot_names)
assert not missing_pivots, f'GLB omitted pivots: {missing_pivots}'

report = {
    'status': 'diagnostic static runtime derivative; not selected or accepted',
    'native': {'path': str(NATIVE.relative_to(ROOT)), 'sha256Before': NATIVE_SHA256,
               'sha256After': native_after, 'unchanged': native_after == NATIVE_SHA256,
               'bytes': NATIVE.stat().st_size},
    'glb': {'path': str(GLB.relative_to(ROOT)), 'sha256': sha256(GLB), 'bytes': GLB.stat().st_size},
    'exporter': {'path': str(EXECUTED.relative_to(ROOT)), 'sha256': sha256(EXECUTED)},
    'helper': {'path': str(HELPER.relative_to(ROOT)), 'sha256': sha256(HELPER)},
    'checks': {
        'reopenedNativeSnapshotExact': True,
        'modifierSignaturesCapturedBeforeExportCopy': len(mods),
        'pivotCountInNative': len(expected_pivots),
        'pivotWorldMatricesUnchangedByExportCopy': True,
        'pivotNodeCountInGlb': sum(name in exported_pivot_names for name in expected_pivots),
        'missingPivotNodesInGlb': missing_pivots,
    },
    'limits': [
        'Static diagnostic export only; the source native is preserved unchanged.',
        'No native/export surface parity, pose motion, collision clearance, shading, or likeness check was run.',
        'A GLB node-name presence check establishes retention of pivot nodes, not runtime pose behavior.',
    ],
}
RECEIPT.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'status': report['status'], 'nativeUnchanged': report['native']['unchanged'],
                  'nativeSha256': native_after, 'glbSha256': report['glb']['sha256'],
                  'pivotCountNative': len(expected_pivots),
                  'pivotNodesInGlb': report['checks']['pivotNodeCountInGlb']}, indent=2))
