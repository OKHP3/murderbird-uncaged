"""Read-only exact binary/JSON comparison of the composer verification outputs."""
from pathlib import Path
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
INPUTS = [
    ('assets/models/uncaged-digit-envelope-study-v1/iterations/attempt-03/runtime/murderbird-digit-envelope-study-v1.glb',
     '574d9ca441216e8f481d019f4fda4d7e6dfa2edd7f545aacf3d2abc238d420c4'),
    ('assets/audit/alignment-composition-check/native/composition-check.glb',
     '981574f388bc324fa0cdd3feeccc134e76eaeece48c5c00c1b6b5672f7494d30'),
]


def read(record):
    relative, expected = record
    data = (ROOT / relative).read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected
    assert data[:4] == b'glTF' and struct.unpack_from('<I', data, 8)[0] == len(data)
    json_length, json_type = struct.unpack_from('<II', data, 12)
    assert json_type == 0x4E4F534A
    binary_length, binary_type = struct.unpack_from('<II', data, 20 + json_length)
    assert binary_type == 0x004E4942
    binary = data[28 + json_length:]
    assert len(binary) == binary_length
    return json.loads(data[20:20 + json_length]), binary


def difference(a, b, path=''):
    if type(a) is not type(b):
        return [{'path': path, 'source': a, 'composition': b}]
    if isinstance(a, dict):
        return [item for key in sorted(set(a) | set(b))
                for item in difference(a.get(key), b.get(key), path + '/' + key)]
    if isinstance(a, list):
        if len(a) != len(b):
            return [{'path': path, 'sourceLength': len(a), 'compositionLength': len(b)}]
        return [item for index, (x, y) in enumerate(zip(a, b))
                for item in difference(x, y, path + '/' + str(index))]
    return [] if a == b else [{'path': path, 'source': a, 'composition': b}]


source, source_binary = read(INPUTS[0])
composition, composition_binary = read(INPUTS[1])
differences = difference(source, composition)
assert source_binary == composition_binary, 'Exported binary payload differs'
assert len(differences) == 24
assert all(row['path'].startswith('/meshes/') and row['path'].endswith('/name')
           and row['composition'] == row['source'] + '.001' for row in differences)
report = {
    'status': 'pass within exact declared scope',
    'inputs': [{'path': path, 'sha256': digest} for path, digest in INPUTS],
    'binaryBytes': len(source_binary), 'binaryExactlyEqual': True,
    'jsonExactlyEqualExceptListedMeshDataNames': True, 'differences': differences,
    'meaning': 'All exported geometry buffers, normals, indices, materials, node names, transforms, hierarchy, semantic tags and accessor metadata are identical. The 24 transferred mesh-data names alone gained Blender copy suffix .001. This does not rename object/node identities.',
    'limits': ['Composer verification only, not a selected exhibit or artistic candidate.',
               'Does not independently validate source geometry, movement, clearance or artistic likeness.'],
    'comparatorSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
}
with (HERE / 'export-parity.json').open('x') as stream:
    stream.write(json.dumps(report, indent=2) + '\n')
print(json.dumps({key: report[key] for key in ('status', 'binaryBytes', 'binaryExactlyEqual')}))
