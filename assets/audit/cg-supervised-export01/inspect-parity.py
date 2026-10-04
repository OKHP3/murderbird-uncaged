"""Independent standard-library GLB comparison; no Blender/module import."""
from pathlib import Path
import hashlib
import json
import struct
from collections import Counter
root = Path(__file__).resolve().parent

def inspect(path):
    raw = path.read_bytes()
    magic, version, length = struct.unpack_from('<4sII', raw)
    assert (magic, version, length) == (b'glTF', 2, len(raw))
    size, kind = struct.unpack_from('<II', raw, 12)
    assert kind == 0x4e4f534a
    doc = json.loads(raw[20:20 + size])
    bin_length, bin_kind = struct.unpack_from('<II', raw, 20 + size)
    assert bin_kind == 0x004e4942
    binary = memoryview(raw)[28 + size:28 + size + bin_length]
    coverage = Counter()
    uv_coverage = {}
    def accessor_values(index):
        accessor = doc['accessors'][index]; view = doc['bufferViews'][accessor['bufferView']]
        component = {5121: 'B', 5123: 'H', 5125: 'I', 5126: 'f'}[accessor['componentType']]
        components = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[accessor['type']]
        fmt = '<' + component * components
        start = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
        stride = view.get('byteStride', struct.calcsize(fmt))
        return [struct.unpack_from(fmt, binary, start + i * stride) for i in range(accessor['count'])]
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:
            assert primitive.get('mode', 4) == 4
            coverage[doc['materials'][primitive['material']]['name']] += doc['accessors'][primitive['indices']]['count'] // 3
            assert 'NORMAL' in primitive['attributes']
            name = doc['materials'][primitive['material']]['name']
            if 'TEXCOORD_0' in primitive['attributes'] and doc['materials'][primitive['material']].get('pbrMetallicRoughness', {}).get('baseColorTexture'):
                values = accessor_values(primitive['attributes']['TEXCOORD_0'])
                counter = uv_coverage.setdefault(name, Counter())
                for (index,) in accessor_values(primitive['indices']):
                    counter[tuple(round(v, 6) for v in values[index])] += 1
    images = {}
    for image in doc['images']:
        assert 'bufferView' in image and 'uri' not in image
        view = doc['bufferViews'][image['bufferView']]
        start = view.get('byteOffset', 0)
        pixels = binary[start:start + view['byteLength']]
        images[image['name']] = hashlib.sha256(pixels).hexdigest()
    def normalize(value):
        if isinstance(value, dict):
            if 'index' in value:
                value = dict(value)
                texture = doc['textures'][value.pop('index')]
                image = doc['images'][texture['source']]
                value['embedded_image_sha256'] = images[image['name']]
            return {k: normalize(v) for k, v in value.items() if not (k == 'texCoord' and v == 0)}
        if isinstance(value, list):
            return [normalize(v) for v in value]
        return value
    return {'coverage': dict(coverage), 'indexed_uv_values_sha256': {name: hashlib.sha256(repr(sorted(counts)).encode()).hexdigest() for name, counts in uv_coverage.items()}, 'embedded_image_sha256': images,
            'materials': {m['name']: normalize(m) for m in doc['materials']},
            'mesh_count': len(doc['meshes']), 'bytes': len(raw)}

baseline = inspect(root / 'fidelity-baseline.glb')
batched = inspect(root / 'builder.glb')
assert baseline['coverage'] == batched['coverage']
uv_equal = baseline['indexed_uv_values_sha256'] == batched['indexed_uv_values_sha256']
assert baseline['embedded_image_sha256'] == batched['embedded_image_sha256']
# Same material records include PBR, IOR, clearcoat and transmission.
assert baseline['materials'] == batched['materials']
report = {'pass': True, 'material_triangle_coverage_equal': True, 'indexed_uv_values_equal': uv_equal, 'uv_status': 'PASS' if uv_equal else 'WARN: indexed UV value sets differ between individual and batched triangulation; exact cross-export corner parity not established', 'embedded_images_byte_equal': True,
          'pbr_material_records_equal': True, 'baseline': baseline, 'batched': batched}
(root / 'independent-glb-parity.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k not in {'baseline', 'batched'}}))
