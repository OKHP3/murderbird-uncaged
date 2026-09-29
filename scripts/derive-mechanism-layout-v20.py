"""Map historical mechanism sockets with the exact frozen V20 construction cage.

Run under Blender. This writes a proposal JSON for a NEW native composition;
it never opens, modifies or overwrites an existing native or runtime export.
The mapping preserves source relationships. It does not certify physical fit.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--source', required=True, help='Frozen executed-proportions.py')
parser.add_argument('--contract', required=True, help='Matching rig-shape-contract.json')
parser.add_argument('--out', required=True, help='New output JSON path')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
source, contract_path, out = [Path(p).resolve() for p in (args.source, args.contract, args.out)]
assert not out.exists(), f'Refusing to replace {out}'
contract = json.loads(contract_path.read_text())['rigContract']
module = {'__file__': str(source), '__name__': 'frozen_v20_socket_mapping', 'SOURCE_ROOT': ROOT}
exec(compile(source.read_text(), str(source), 'exec'), module)
map_point = module['map_point']
old = {name: Matrix(item['oldWorld']) for name, item in contract.items()}
new = {name: Matrix(item['newWorld']) for name, item in contract.items()}
assert set(old) == set(module['OLD']), 'Mapping and contract node inventories differ'
assert all(max(abs(old[n][i][j] - module['OLD'][n][i][j]) for i in range(4) for j in range(4)) < 1e-7 for n in old), 'Mapping inventory does not match contract'
assert all((map_point(n, old[n].translation) - new[n].translation).length < 1e-6 for n in old), 'Frozen mapping does not reproduce contract pivots'

# Blender native (X,Y,Z) becomes glTF/browser (X,Z,-Y).
C = Matrix(((1, 0, 0), (0, 0, 1), (0, -1, 0)))
def mapped_local(owner, browser_local):
    world_before = old[owner] @ (C.transposed() @ Vector(browser_local))
    world_after = map_point(owner, world_before)
    return C @ (new[owner].inverted() @ world_after)

def values(vector):
    return [round(float(x), 9) for x in vector]

tail_position = mapped_local('body', (0, .20, -.31))
tail_control_world_in_body = Vector((0, .20, -.31)) + Vector((-.07, 0, -.16))
controls = {
    'leg': values(mapped_local('left-foot', (.065, .015, .045))),
    'wing': values(mapped_local('right-mantle', (-.095, -.10, .10))),
    'tail': values(mapped_local('body', tail_control_world_in_body) - tail_position),
    'neck': values(mapped_local('neck', (-.16, .06, .02))),
    'jaw': values(mapped_local('jaw', (-.18, -.06, .20))),
}
old_neck_in_body = C @ (old['body'].inverted() @ old['neck'].translation)
cervical = []
for side, sign in [('left', 1), ('right', -1)]:
    cervical.append({
        'side': side,
        'bodyPoint': values(mapped_local('body', old_neck_in_body + Vector((sign * .105, .02, -.10)))),
        'neckPoint': values(mapped_local('neck', (sign * .055, .16, -.025))),
    })

def record(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

hip_left = new['body'].inverted() @ new['left-thigh'].translation
hip_right = new['body'].inverted() @ new['right-thigh'].translation
layout = {
    'version': 1,
    'status': 'Mapped attachment proposal; actual hardware fit and movement remain subject to review',
    'coordinateSpace': 'glTF owner-local metres; no object scale applied to runtime mechanisms',
    'sourceMapping': record(source),
    'sourceRigContract': record(contract_path),
    'makerControlOffsets': controls,
    'tailPosition': values(tail_position),
    'distributionPosition': values(mapped_local('body', (-.21, .29, .07))),
    'transmissionPosition': values(mapped_local('body', (0, 0, 0))),
    'cervical': cervical,
    'makerCradleWidth': round(abs(hip_left.x - hip_right.x) + .066, 9),
    'limits': [
        'Sockets are transformed source placements, not proven bearing seats.',
        'The Mechanic gearbox retains its rigid internal spacing; only its origin follows this contract.',
        'Maker floor rack and fixed guide support remain independent external apparatus.',
        'Advanced conduit routing still requires visual review against the revised body.',
    ],
}
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(layout, indent=2) + '\n')
print(json.dumps({'layout': record(out), 'status': layout['status']}))
