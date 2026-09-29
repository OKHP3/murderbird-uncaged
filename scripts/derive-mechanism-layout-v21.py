"""Derive proposed V21 sockets from actual saved frame mesh centerlines.
Read-only native inspection; write-once JSON only. No seating/clearance claim.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--native', required=True)
parser.add_argument('--native-sha256', required=True)
parser.add_argument('--out', required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
native = ROOT / args.native
out = ROOT / args.out
receipt_path = out.with_name(out.stem + '-receipt.json')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(native) == args.native_sha256 and not out.exists() and not receipt_path.exists()
bpy.ops.wm.open_mainfile(filepath=str(native))
layout = json.loads(bpy.data.objects['body']['mechanismLayoutV1'])
layout['cervicalSocketProvenanceV21'] = {
    'sourceNative': args.native,
    'sourceNativeSha256': args.native_sha256,
    'refreshedFields': ['makerControlOffsets.neck', 'cervical'],
    'inheritedProvenance': 'sourceMapping and sourceRigContract describe the retained V20 fields only; refreshed cervical fields are derived from the V21 native frame.',
    'status': 'authored frame-derived socket proposal, not a recovered mechanism',
}
witnesses = []


def socket(name, owner, ring=None, expected_rings=None):
    """The authored tubes use 16 vertices per section; journals use centroid."""
    obj = bpy.data.objects[name]
    assert obj.parent.name == owner and obj.type == 'MESH'
    vertices = list(obj.data.vertices)
    if ring is not None:
        assert len(vertices) == 16 * expected_rings
        vertices = vertices[16 * ring:16 * (ring + 1)]
    world = sum((obj.matrix_world @ v.co for v in vertices), Vector()) / len(vertices)
    local = bpy.data.objects[owner].matrix_world.inverted() @ world
    browser_local = [local.x, local.z, -local.y]
    witnesses.append({'mesh': name, 'owner': owner, 'ring': ring,
                      'sampleCount': len(vertices), 'nativeWorld': list(world),
                      'nativeOwnerLocal': list(local), 'browserOwnerLocal': browser_local,
                      'role': 'proposed attachment to retained rigid frame; mount and moving clearance need review'})
    return browser_local


# The other control owners and their retained geometry have not moved.
# Neck control attaches at its passive intermediate journal, not an old skirt.
layout['makerControlOffsets']['neck'] = socket('V21 intermediate passive journal -1', 'neck')
layout['cervical'] = []
for side, sign in [('left', 1), ('right', -1)]:
    body_point = socket(f'V21 neck root breast support bridge {sign}', 'body', 1, 3)
    neck_point = socket(f'V21 cervical root load bow {sign}', 'neck', 2, 4)
    layout['cervical'].append({'side': side, 'bodyPoint': body_point, 'neckPoint': neck_point})
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(layout, indent=2) + '\n')
receipt = {'status': 'frame-derived local socket proposal; no motion, contact or clearance acceptance',
           'native': {'path': args.native, 'sha256': args.native_sha256},
           'layout': {'path': args.out, 'sha256': sha(out)},
           'source': {'path': Path(__file__).relative_to(ROOT).as_posix(), 'sha256': sha(Path(__file__))},
           'coordinateConversion': '(native X, native Z, -native Y), glTF owner-local metres',
           'witnesses': witnesses,
           'inherited': ['Maker leg/wing/tail/jaw horn offsets', 'Maker cradle width', 'rear pivot',
                         'Mechanic rigid transmission origin', 'Advanced distribution origin'],
           'limits': ['Centers lie on the actual passive frame; dedicated mounting details remain proposals.',
                      'A valid layout is not proof of era-specific drive completeness or swept clearance.']}
receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
assert sha(native) == args.native_sha256
print(json.dumps(receipt, indent=2))
