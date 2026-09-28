"""Read-only validation of alignment-v3 source/export and frozen v2 provenance.

A receipt is written only when --report is explicitly supplied. These checks
establish asset integrity and rigid interfaces, never likeness or biomechanics.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import struct

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = 'assets/models/uncaged-alignment-v3'
INVENTORY_PATH = f'{MODEL_DIR}/alignment-inventory.json'
MODEL_PATH = f'{MODEL_DIR}/murderbird-alignment-v3.glb'
SOURCE_PATH = f'{MODEL_DIR}/murderbird-alignment-v3.blend'
FROZEN_V2 = {
    'assets/models/uncaged-neutral-v2/murderbird-neutral-v2.blend':
        '64ea6d86504987357eb22c2e3c4036ec87da6432f15354f5d4a07d004fd6dec9',
    'assets/models/uncaged-neutral-v2/murderbird-neutral-v2.glb':
        '48229ba5526ccd7a227db56d225ef88643eb6b3388eb07662452cc2c67636ac7',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_file(relative):
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT), f'File escapes repository: {relative}')
    require(path.is_file(), f'Referenced file is missing: {relative}')
    raw = path.read_bytes()
    require(not raw.startswith(b'version https://git-lfs'), f'LFS pointer: {relative}')
    return raw


def validate_record(record):
    raw = source_file(record['path'])
    require(hashlib.sha256(raw).hexdigest() == record['sha256'], f'Hash mismatch: {record["path"]}')
    if 'bytes' in record:
        require(len(raw) == record['bytes'], f'Byte count mismatch: {record["path"]}')
    return raw


def hash_records(value):
    if isinstance(value, dict):
        if isinstance(value.get('path'), str) and 'sha256' in value:
            yield value
        for item in value.values():
            yield from hash_records(item)
    elif isinstance(value, list):
        for item in value:
            yield from hash_records(item)


def parse_glb(raw):
    require(raw[:4] == b'glTF', 'Runtime file must be a GLB')
    version, length = struct.unpack_from('<II', raw, 4)
    require(version == 2 and length == len(raw), 'GLB header length/version mismatch')
    chunks, offset = [], 12
    while offset < len(raw):
        require(offset + 8 <= len(raw), 'Truncated GLB chunk header')
        size, kind = struct.unpack_from('<II', raw, offset)
        offset += 8
        require(size % 4 == 0 and offset + size <= len(raw), 'Invalid GLB chunk bounds/alignment')
        chunks.append((kind, raw[offset:offset + size]))
        offset += size
    require([kind for kind, _ in chunks] == [0x4E4F534A, 0x004E4942], 'Expected JSON and embedded BIN GLB chunks')
    return json.loads(chunks[0][1]), chunks[1][1]


def validate():
    inventory = json.loads(source_file(INVENTORY_PATH))
    require(inventory['status'] == 'neutral geometry proposal awaiting owner review', 'Inventory must retain proposal status')
    records = inventory['generatedFiles']
    require(records, 'Generated file inventory is empty')
    names = [record['path'] for record in records]
    require(len(names) == len(set(names)), 'Duplicate generated paths')
    required = {MODEL_PATH, SOURCE_PATH}
    required.update(f'{MODEL_DIR}/{era}-preview.png' for era in ['maker', 'mechanic', 'builder'])
    require(required.issubset(set(names)), 'Missing native source, runtime GLB or per-era preview records')
    for record in records:
        require(record['path'].startswith(MODEL_DIR + '/'), f'Generated output outside v3 model tree: {record["path"]}')
        raw = validate_record(record)
        if record['path'].endswith('.png'):
            require(raw[:8] == b'\x89PNG\r\n\x1a\n', f'Invalid PNG: {record["path"]}')
            require(all(v > 0 for v in struct.unpack_from('>II', raw, 16)), f'Zero-size PNG: {record["path"]}')
    checks = ['Native source, runtime GLB and explicit previews match inventory bytes/SHA; actual binary files']
    for path, digest in FROZEN_V2.items():
        validate_record({'path': path, 'sha256': digest})
    # Freeze the whole old generated inventory too: fallback evidence must remain reproducible.
    v2_inventory = json.loads(source_file('assets/models/uncaged-neutral-v2/neutral-inventory.json'))
    for record in v2_inventory['generatedFiles']:
        validate_record(record)
    checks.append('Frozen v2 source/runtime hashes and all v2 generated asset hashes are unchanged')
    referenced = []
    packet = json.loads(source_file('assets/models/uncaged-neutral-v2/reference-packet.json'))
    for record in list(hash_records(packet)) + list(hash_records(inventory)):
        validate_record(record)
        if record['path'] not in names:
            referenced.append(record['path'])
    require(referenced, 'Source references are absent')
    checks.append(f'{len(set(referenced))} distinct provenance/reference files exist and match their recorded hashes')

    raw = source_file(MODEL_PATH)
    gltf, binary = parse_glb(raw)
    require(not gltf.get('skins') and not gltf.get('images') and not gltf.get('textures'), 'Neutral rigid export must not contain skinning or image maps')
    require(len(gltf.get('buffers', [])) == 1 and not gltf['buffers'][0].get('uri'), 'GLB must have one embedded buffer')
    require(gltf['buffers'][0]['byteLength'] <= len(binary), 'Embedded binary length is inconsistent')
    size_by_type = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT2': 4, 'MAT3': 9, 'MAT4': 16}
    for accessor in gltf['accessors']:
        require('sparse' not in accessor, 'Sparse accessors require separately implemented validation')
        if accessor['componentType'] != 5126:
            continue
        size = size_by_type[accessor['type']]
        view = gltf['bufferViews'][accessor['bufferView']]
        require(view.get('buffer', 0) == 0, 'Accessor must use embedded buffer')
        offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
        stride = view.get('byteStride', size * 4)
        require(stride >= size * 4, 'Float accessor stride too small')
        end = offset + (accessor['count'] - 1) * stride + size * 4 if accessor['count'] else offset
        require(end <= len(binary) and end <= view.get('byteOffset', 0) + view['byteLength'], 'Float accessor exceeds buffer bounds')
        for index in range(accessor['count']):
            require(all(math.isfinite(v) for v in struct.unpack_from('<' + 'f' * size, binary, offset + index * stride)), 'Non-finite float attribute')
    for node in gltf['nodes']:
        for key in ['translation', 'rotation', 'scale', 'matrix']:
            require(all(math.isfinite(v) for v in node.get(key, [])), f'Non-finite {key}: {node.get("name")}')
        require(all(abs(value - 1) <= 1e-5 for value in node.get('scale', [1, 1, 1])), f'Rigid node retains non-unit scale: {node.get("name")}')
        if 'rotation' in node:
            require(abs(sum(value * value for value in node['rotation']) - 1) <= 1e-5, f'Rigid node quaternion is not normalized: {node.get("name")}')
        if 'matrix' in node:
            matrix = node['matrix']
            require(len(matrix) == 16, f'Invalid node matrix: {node.get("name")}')
            require(all(abs(matrix[index]) <= 1e-5 for index in [3, 7, 11]) and abs(matrix[15] - 1) <= 1e-5, f'Non-affine rigid matrix: {node.get("name")}')
            basis = [[matrix[column * 4 + row] for row in range(3)] for column in range(3)]
            require(all(abs(sum(value * value for value in axis) - 1) <= 1e-5 for axis in basis), f'Rigid matrix contains scale: {node.get("name")}')
            require(all(abs(sum(a * b for a, b in zip(basis[first], basis[second]))) <= 1e-5 for first, second in [(0, 1), (0, 2), (1, 2)]), f'Rigid matrix contains shear: {node.get("name")}')
            a, b, c = basis
            determinant = a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])
            require(abs(determinant - 1) <= 1e-5, f'Rigid matrix contains reflection: {node.get("name")}')
    for mesh in gltf['meshes']:
        for primitive in mesh['primitives']:
            require(not any(key.startswith(('JOINTS_', 'WEIGHTS_')) for key in primitive['attributes']), 'Rigid mesh contains deforming attributes')
    checks.append('Rigid neutral geometry; no skinning, image maps or external buffers; finite attributes/transforms, unit node scales and orthonormal matrix bases')

    nodes = {node['name']: index for index, node in enumerate(gltf['nodes'])}
    require(len(nodes) == len(gltf['nodes']), 'Exported node names must be unique')
    parents = {}
    for index, node in enumerate(gltf['nodes']):
        for child in node.get('children', []):
            require(child not in parents, f'Multiple rigid owners: node {child}')
            require(0 <= child < len(gltf['nodes']), f'Invalid child index: {child}')
            parents[child] = index
    for child in parents:
        seen = {child}
        ancestor = parents[child]
        while True:
            require(ancestor not in seen, f'Cycle in rigid ownership: node {child}')
            seen.add(ancestor)
            if ancestor not in parents:
                break
            ancestor = parents[ancestor]
    required_parents = {'neck': 'body', 'head': 'neck', 'jaw': 'head', 'upper-bill': 'head',
                        'cranial-cover': 'head', 'breastplate': 'body',
                        'left-wing-shield': 'left-mantle', 'right-wing-shield': 'right-mantle'}
    for side in ['left', 'right']:
        for digit in [1, 2, 3]:
            name = f'{side}-digit-{digit}'
            required_parents[name + '-proximal'] = side + '-toes'
            required_parents[name + '-distal'] = name + '-proximal'
    for child, owner in required_parents.items():
        require(child in nodes and owner in nodes and parents.get(nodes[child]) == nodes[owner], f'Rigid ownership mismatch: {child} -> {owner}')
    for pivot in inventory['pivots']:
        require(pivot['name'] in nodes, f'Inventory pivot absent from export: {pivot["name"]}')
        if pivot.get('parent'):
            require(pivot['parent'] in nodes and parents.get(nodes[pivot['name']]) == nodes[pivot['parent']], f'Inventory/export parent mismatch: {pivot["name"]}')
        require(all(math.isfinite(v) for key in ['local', 'world', 'scale'] for v in pivot.get(key, [])), f'Non-finite inventory pivot: {pivot["name"]}')
        require(all(abs(value - 1) <= 1e-5 for value in pivot.get('scale', [1, 1, 1])), f'Inventory pivot retains non-unit scale: {pivot["name"]}')
    checks.append('Opening panels, cervical/skull joints, inventory pivots and 12 independent digit hinges have unique rigid ownership')
    require(inventory['parts'], 'Editable part inventory is empty')
    for part in inventory['parts']:
        require(part['parent'] in nodes, f'Editable part owner absent from export: {part["name"]}')
        require(part['eras'] and set(part['eras']).issubset({'maker', 'mechanic', 'builder'}), f'Invalid era membership: {part["name"]}')
    late = [part for part in inventory['parts'] if part['role'] == 'optic' or part['parent'] in ['processing', 'power-core', 'builder-optics']]
    require(late and all(part['eras'] == ['builder'] for part in late), 'Advanced systems leak into earlier eras')
    repair = [part for part in inventory['parts'] if part['class'] == 'later-repair']
    require(repair and all('maker' not in part['eras'] for part in repair), 'Later repairs leak into Maker era')
    for node in gltf['nodes']:
        extras = node.get('extras', {})
        eras = extras.get('exteriorEras', '').split(',')
        if extras.get('constructionClass') == 'later-repair':
            require('maker' not in eras, f'Exported later repair leaks into Maker: {node["name"]}')
        if extras.get('constructionClass') == 'advanced-system':
            require(eras == ['builder'], f'Exported advanced system leaks into early era: {node["name"]}')
    checks.append('Inventory and exported eligibility exclude Advanced systems and later repairs from earlier eras')
    triangles = sum(gltf['accessors'][primitive['indices']]['count'] // 3 for mesh in gltf['meshes'] for primitive in mesh['primitives'])
    return {'status': 'passed', 'modelPath': MODEL_PATH, 'modelSha256': hashlib.sha256(raw).hexdigest(),
            'modelBytes': len(raw), 'nodes': len(gltf['nodes']), 'meshes': len(gltf['meshes']),
            'triangles': triangles, 'editableParts': len(inventory['parts']),
            'referenceFiles': sorted(set(referenced)), 'checks': checks,
            'limits': 'No artistic likeness, swept collision, physical balance, force, acting or final surface certification'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, help='Explicit receipt path; omitted by default for read-only verification')
    args = parser.parse_args()
    report = validate()
    output = json.dumps(report, indent=2) + '\n'
    if args.report:
        destination = args.report.resolve()
        allowed = (ROOT / 'assets/audit/alignment-v3').resolve()
        require(destination.is_relative_to(allowed), '--report must remain under assets/audit/alignment-v3')
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output)
    print(output, end='')


if __name__ == '__main__':
    main()
