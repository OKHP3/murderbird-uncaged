"""Create a static diagnostic GLB from V12 attempt-02's reopened native copy."""
from pathlib import Path
import hashlib
import json
import runpy
import shutil
import struct
import bpy

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'assets/models/uncaged-cervical-envelope-v12/attempt-02/murderbird-cervical-envelope-v12.blend'
GLB = NATIVE.with_suffix('.glb')
AUDIT = ROOT / 'assets/audit/uncaged-cervical-envelope-v12/attempt-02'
EXECUTED = AUDIT / 'executed-export.py'
RECEIPT = AUDIT / 'export-receipt.json'
HELPER = ROOT / 'scripts/build-uncaged-alignment-v7.py'
NATIVE_SHA256 = '28b18c810784a1e6872ef3743f16e5cff36e5aac66c01c9299e5195064ac7c60'
HELPER_SHA256 = '39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def glb_document(path):
    raw = path.read_bytes()
    assert raw[:4] == b'glTF' and struct.unpack_from('<I', raw, 8)[0] == len(raw)
    json_length, json_type = struct.unpack_from('<II', raw, 12)
    assert json_type == 0x4E4F534A
    return json.loads(raw[20:20 + json_length])


assert sha(NATIVE) == NATIVE_SHA256, 'V12 native SHA mismatch'
assert sha(HELPER) == HELPER_SHA256, 'Reviewed V7 helper SHA mismatch'
assert Path(bpy.data.filepath).resolve() == NATIVE.resolve(), 'Wrong native opened'
assert not GLB.exists(), 'Refusing to overwrite existing diagnostic GLB'
assert not RECEIPT.exists(), 'Refusing to overwrite existing export receipt'
if EXECUTED.exists():
    assert sha(EXECUTED) == sha(__file__), 'Existing frozen exporter differs'
else:
    shutil.copy2(__file__, EXECUTED)
assert sha(EXECUTED) == sha(__file__)

helpers = runpy.run_path(str(HELPER), run_name='cervical_v12_export_helpers')
snapshot = helpers['scene_snapshot']()
pivots = snapshot['empties']
assert len(pivots) == 52, f'Expected 52 pivots, found {len(pivots)}'
mods = {obj.name: helpers['modifier_signature'](obj)
        for obj in bpy.data.objects if obj.type == 'MESH' and obj.modifiers}
helpers['export_from_reopened_native'](NATIVE, GLB, snapshot, mods)

native_after = sha(NATIVE)
assert native_after == NATIVE_SHA256, 'Native changed during export'
assert GLB.is_file() and GLB.stat().st_size > 100_000
nodes = glb_document(GLB).get('nodes', [])
node_names = {node.get('name') for node in nodes}
missing = sorted(set(pivots) - node_names)
assert not missing, f'GLB omitted pivot nodes: {missing}'

receipt = {
    'status': 'static diagnostic runtime derivative; not selected or accepted',
    'native': {'path': str(NATIVE.relative_to(ROOT)), 'sha256Before': NATIVE_SHA256,
               'sha256After': native_after, 'unchanged': native_after == NATIVE_SHA256,
               'bytes': NATIVE.stat().st_size},
    'glb': {'path': str(GLB.relative_to(ROOT)), 'sha256': sha(GLB), 'bytes': GLB.stat().st_size},
    'exporter': {'path': str(EXECUTED.relative_to(ROOT)), 'sha256': sha(EXECUTED)},
    'helper': {'path': str(HELPER.relative_to(ROOT)), 'sha256': sha(HELPER)},
    'checks': {'reopenedNativeSnapshotExact': True, 'modifierSignaturesCapturedBeforeExportCopy': len(mods),
               'pivotCountNative': len(pivots), 'pivotWorldMatricesUnchangedByExportCopy': True,
               'pivotNodeCountInGlb': sum(name in node_names for name in pivots), 'missingPivotNodesInGlb': missing},
    'limits': ['Only a static diagnostic export was produced.',
               'No native/export surface parity, pose, collision-clearance, shading, or likeness check was run.',
               'Pivot node name presence does not establish runtime motion behavior.'],
}
RECEIPT.write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'nativeUnchanged': receipt['native']['unchanged'],
                  'nativeSha256': native_after, 'glbSha256': receipt['glb']['sha256'],
                  'pivotCountNative': len(pivots), 'pivotNodesInGlb': receipt['checks']['pivotNodeCountInGlb']}, indent=2))
