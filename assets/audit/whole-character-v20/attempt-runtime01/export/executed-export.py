"""Export a pinned native Blender scene as a write-once diagnostic GLB.

Run through Blender with arguments after ``--``::

  blender -b path/to/model.blend --python-exit-code 1 \\
    --python scripts/export-native-diagnostic.py -- \\
    --native assets/models/example/model.blend \\
    --expected-native <sha256> --audit assets/audit/example

This creates the sibling GLB plus an immutable receipt and executed-script
snapshot in the audit directory. It does not select or publish the result.
"""
from pathlib import Path
import argparse
import hashlib
import json
import runpy
import shutil
import struct
import sys

import bpy


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'scripts/build-uncaged-alignment-v7.py'
HELPER_SHA256 = '39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'
SCRIPT = Path(__file__).resolve()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def repo_path(value, label, must_exist=False):
    candidate = Path(value)
    assert not candidate.is_absolute(), f'{label} must be repository-relative'
    resolved = (ROOT / candidate).resolve(strict=must_exist)
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise AssertionError(f'{label} escapes the repository root') from exc
    return resolved


def glb_document(path):
    raw = path.read_bytes()
    assert raw[:4] == b'glTF' and struct.unpack_from('<I', raw, 8)[0] == len(raw)
    json_length, json_type = struct.unpack_from('<II', raw, 12)
    assert json_type == 0x4E4F534A
    return json.loads(raw[20:20 + json_length])


def arguments():
    argv = sys.argv
    tail = argv[argv.index('--') + 1:] if '--' in argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', required=True, help='repository-relative .blend path')
    parser.add_argument('--expected-native', required=True, help='expected native SHA-256')
    parser.add_argument('--audit', required=True, help='repository-relative audit directory')
    args = parser.parse_args(tail)
    assert len(args.expected_native) == 64 and all(c in '0123456789abcdef' for c in args.expected_native), \
        '--expected-native must be a lowercase SHA-256 hex digest'
    return args


args = arguments()
native_arg = Path(args.native)
audit_arg = Path(args.audit)
NATIVE = repo_path(args.native, '--native', must_exist=True)
AUDIT = repo_path(args.audit, '--audit')
assert NATIVE.suffix.lower() == '.blend', '--native must name a .blend file'
assert AUDIT != ROOT, '--audit must not be the repository root'
GLB = NATIVE.with_suffix('.glb')
EXECUTED = AUDIT / 'executed-export.py'
RECEIPT = AUDIT / 'export-receipt.json'
NATIVE_SHA256 = args.expected_native

assert sha(NATIVE) == NATIVE_SHA256, 'Native SHA mismatch'
assert sha(HELPER) == HELPER_SHA256, 'Reviewed V7 helper SHA mismatch'
assert Path(bpy.data.filepath).resolve() == NATIVE, 'Wrong native opened in Blender'
assert not GLB.exists(), 'Refusing to overwrite existing diagnostic GLB'
assert not EXECUTED.exists(), 'Refusing to overwrite existing executed exporter snapshot'
assert not RECEIPT.exists(), 'Refusing to overwrite existing export receipt'

AUDIT.mkdir(parents=True, exist_ok=True)
# Exclusive create makes the exact executed source immutable at this path.
with EXECUTED.open('xb') as stream:
    stream.write(SCRIPT.read_bytes())

helpers = runpy.run_path(str(HELPER), run_name='native_diagnostic_export_helpers')
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
    'arguments': {
        'native': native_arg.as_posix(),
        'expectedNativeSha256': NATIVE_SHA256,
        'audit': audit_arg.as_posix(),
    },
    'native': {'path': NATIVE.relative_to(ROOT).as_posix(),
               'sha256Before': NATIVE_SHA256, 'sha256After': native_after,
               'unchanged': native_after == NATIVE_SHA256,
               'bytes': NATIVE.stat().st_size},
    'glb': {'path': GLB.relative_to(ROOT).as_posix(),
            'sha256': sha(GLB), 'bytes': GLB.stat().st_size},
    'exporter': {'path': EXECUTED.relative_to(ROOT).as_posix(), 'sha256': sha(EXECUTED)},
    'helper': {'path': HELPER.relative_to(ROOT).as_posix(), 'sha256': sha(HELPER)},
    'checks': {
        'reopenedNativeSnapshotExact': True,
        'modifierSignaturesCapturedBeforeExportCopy': len(mods),
        'pivotCountNative': len(pivots),
        'pivotWorldMatricesUnchangedByExportCopy': True,
        'pivotNodeCountInGlb': sum(name in node_names for name in pivots),
        'missingPivotNodesInGlb': missing,
    },
    'limits': [
        'Only a static diagnostic export was produced.',
        'No native/export surface parity, pose, collision-clearance, shading, or likeness check was run.',
        'Pivot node name presence does not establish runtime motion behavior.',
    ],
}
with RECEIPT.open('x') as stream:
    stream.write(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'nativeUnchanged': receipt['native']['unchanged'],
                  'nativeSha256': native_after, 'glbSha256': receipt['glb']['sha256'],
                  'pivotCountNative': len(pivots),
                  'pivotNodesInGlb': receipt['checks']['pivotNodeCountInGlb']}, indent=2))
