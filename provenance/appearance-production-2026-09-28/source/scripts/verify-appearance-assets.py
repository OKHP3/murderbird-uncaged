"""Validate a generated appearance iteration's files and rigid GLB interface.

This reports asset and export facts only. It does not assess likeness, material
quality, physical behavior, motion clearance, or owner acceptance.
"""

from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import struct


ROOT = Path(__file__).resolve().parents[1]
ITERATION_ROOT = Path('assets/models/uncaged-appearance-v1/iterations')
BASELINE_PATH = Path('assets/models/uncaged-alignment-v3/murderbird-alignment-v3.glb')
BASELINE_SHA256 = 'c4dc308f77399410368b82443a1b21b9113cfedb258aa055906b4f13c92dda21'
ERAS = {'maker', 'mechanic', 'builder'}
ALLOWED_ROLES = {
    'plate', 'shell', 'head-plate', 'bearing', 'frame', 'inner', 'edge',
    'recess', 'optic', 'repair', 'bill', 'talon',
}
MAX_POSITION_COMPONENT_METERS = 4.0
POSITION_BOUNDS_TOLERANCE = 1e-5
REQUIRED_OWNERS = {
    'murderbird', 'body', 'neck', 'head', 'jaw', 'upper-bill',
    'cranial-cover', 'breastplate', 'winding-drive', 'power-core',
    'processing', 'industrial-repairs', 'builder-optics',
    'left-mantle', 'right-mantle', 'left-wing-shield', 'right-wing-shield',
    'left-thigh', 'left-shin', 'left-foot', 'left-toes',
    'right-thigh', 'right-shin', 'right-foot', 'right-toes',
}
for _side in ('left', 'right'):
    for _digit in (1, 2, 3):
        REQUIRED_OWNERS.add(f'{_side}-digit-{_digit}-proximal')
        REQUIRED_OWNERS.add(f'{_side}-digit-{_digit}-distal')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def repo_file(relative):
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT), f'Path escapes repository: {relative}')
    require(path.is_file(), f'Missing file: {relative}')
    raw = path.read_bytes()
    require(not raw.startswith(b'version https://git-lfs'),
            f'Expected binary file but found an LFS pointer: {relative}')
    return raw


def parse_glb(raw, label):
    require(len(raw) >= 20 and raw[:4] == b'glTF', f'{label}: not a GLB')
    version, total = struct.unpack_from('<II', raw, 4)
    require(version == 2 and total == len(raw), f'{label}: bad GLB version/length')
    chunks = []
    offset = 12
    while offset < total:
        require(offset + 8 <= total, f'{label}: truncated chunk header')
        size, kind = struct.unpack_from('<II', raw, offset)
        offset += 8
        require(size % 4 == 0 and offset + size <= total,
                f'{label}: invalid chunk length/alignment')
        chunks.append((kind, raw[offset:offset + size]))
        offset += size
    require(len(chunks) >= 2 and chunks[0][0] == 0x4E4F534A,
            f'{label}: JSON chunk missing or out of order')
    binary_chunks = [chunk for kind, chunk in chunks if kind == 0x004E4942]
    require(len(binary_chunks) == 1, f'{label}: expected one embedded BIN chunk')
    gltf = json.loads(chunks[0][1].decode('utf-8').rstrip(' \t\r\n\0'))
    return gltf, binary_chunks[0]


def parent_map(gltf):
    names = {}
    for index, node in enumerate(gltf.get('nodes', [])):
        name = node.get('name')
        require(name, f'Unnamed GLB node at index {index}')
        require(name not in names, f'Duplicate GLB node name: {name}')
        names[name] = index
    parents = {}
    for parent, node in enumerate(gltf.get('nodes', [])):
        for child in node.get('children', []):
            require(isinstance(child, int) and 0 <= child < len(gltf['nodes']),
                    f'Invalid child index under {node.get("name")}')
            require(child not in parents, f'Multiple node parents: {gltf["nodes"][child].get("name")}')
            parents[child] = parent
    return names, parents


def local_matrix(node):
    if 'matrix' in node:
        values = node['matrix']
        require(len(values) == 16, f'Invalid matrix on {node.get("name")}')
        return values
    t = node.get('translation', [0, 0, 0])
    q = node.get('rotation', [0, 0, 0, 1])
    s = node.get('scale', [1, 1, 1])
    require(len(t) == 3 and len(q) == 4 and len(s) == 3,
            f'Invalid TRS on {node.get("name")}')
    x, y, z, w = q
    sx, sy, sz = s
    # Column-major glTF matrix, including scale.
    return [
        (1 - 2*y*y - 2*z*z)*sx, (2*x*y + 2*w*z)*sx, (2*x*z - 2*w*y)*sx, 0,
        (2*x*y - 2*w*z)*sy, (1 - 2*x*x - 2*z*z)*sy, (2*y*z + 2*w*x)*sy, 0,
        (2*x*z + 2*w*y)*sz, (2*y*z - 2*w*x)*sz, (1 - 2*x*x - 2*y*y)*sz, 0,
        t[0], t[1], t[2], 1,
    ]


def checked_accessors(gltf, binary):
    size_by_type = {
        'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4,
        'MAT2': 4, 'MAT3': 9, 'MAT4': 16,
    }
    component_bytes = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
    accessors = gltf.get('accessors', [])
    views = gltf.get('bufferViews', [])
    for vi, view in enumerate(views):
        require(view.get('buffer', 0) == 0, f'Buffer view {vi} uses a non-embedded buffer')
        start = view.get('byteOffset', 0)
        length = view.get('byteLength')
        require(isinstance(start, int) and isinstance(length, int) and start >= 0 and length >= 0,
                f'Invalid buffer view range: {vi}')
        require(start + length <= len(binary), f'Buffer view exceeds embedded BIN chunk: {vi}')
    for ai, accessor in enumerate(accessors):
        require('sparse' not in accessor, f'Sparse accessor is unsupported: {ai}')
        require(accessor.get('type') in size_by_type, f'Invalid accessor type: {ai}')
        require(accessor.get('componentType') in component_bytes,
                f'Invalid accessor component type: {ai}')
        require(isinstance(accessor.get('count'), int) and accessor['count'] >= 0,
                f'Invalid accessor count: {ai}')
        vi = accessor.get('bufferView')
        require(isinstance(vi, int) and 0 <= vi < len(views), f'Accessor has no buffer view: {ai}')
        view = views[vi]
        require(view.get('buffer', 0) == 0, f'Accessor uses a non-embedded buffer: {ai}')
        component_size = component_bytes[accessor['componentType']]
        element_size = component_size * size_by_type[accessor['type']]
        view_start = view.get('byteOffset', 0)
        view_end = view_start + view.get('byteLength', 0)
        offset = view_start + accessor.get('byteOffset', 0)
        stride = view.get('byteStride', element_size)
        require(stride >= element_size, f'Accessor stride too small: {ai}')
        end = offset if accessor['count'] == 0 else offset + (accessor['count'] - 1) * stride + element_size
        require(offset >= view_start and end <= view_end and end <= len(binary),
                f'Accessor exceeds embedded buffer view: {ai}')
        if accessor['componentType'] == 5126:
            code = 'f'
        elif accessor['componentType'] in (5120, 5121):
            code = 'b' if accessor['componentType'] == 5120 else 'B'
        elif accessor['componentType'] in (5122, 5123):
            code = 'h' if accessor['componentType'] == 5122 else 'H'
        else:
            code = 'I'
        fmt = '<' + code * size_by_type[accessor['type']]
        for element in range(accessor['count']):
            values = struct.unpack_from(fmt, binary, offset + element * stride)
            require(all(math.isfinite(value) for value in values),
                    f'Non-finite accessor value: accessor {ai}, element {element}')
    return accessors, views


def validate_geometry(gltf, binary, require_texturing=True):
    require(not gltf.get('skins'), 'Appearance GLB must remain rigid and contain no skins')
    accessors, views = checked_accessors(gltf, binary)
    triangles = 0
    primitive_count = 0
    textured_primitives = 0
    attribute_names = set()
    index_values_checked = 0
    position_accessors_checked = set()
    position_values_checked = 0
    maximum_position_component = 0.0
    maximum_position_mesh = None
    for node in gltf.get('nodes', []):
        for key in ('translation', 'rotation', 'scale', 'matrix'):
            require(all(math.isfinite(value) for value in node.get(key, [])),
                    f'Non-finite node {key}: {node.get("name")}')
    for mesh_index, mesh in enumerate(gltf.get('meshes', [])):
        for primitive in mesh.get('primitives', []):
            primitive_count += 1
            attrs = primitive.get('attributes', {})
            attribute_names.update(attrs)
            require('POSITION' in attrs and 'NORMAL' in attrs,
                    f'Mesh {mesh.get("name")} lacks POSITION or NORMAL')
            require(all(isinstance(index, int) and 0 <= index < len(accessors)
                        for index in attrs.values()),
                    f'Mesh {mesh.get("name")} references an invalid attribute accessor')
            position = accessors[attrs['POSITION']]
            normal = accessors[attrs['NORMAL']]
            require(position['type'] == 'VEC3' and normal['type'] == 'VEC3',
                    f'Mesh {mesh.get("name")} has malformed POSITION/NORMAL')
            require(position['componentType'] == 5126,
                    f'Mesh {mesh.get("name")} POSITION must use float components')
            require(position['count'] == normal['count'],
                    f'Mesh {mesh.get("name")} POSITION/NORMAL counts differ')
            position_index = attrs['POSITION']
            if position_index not in position_accessors_checked:
                view = views[position['bufferView']]
                base = view.get('byteOffset', 0) + position.get('byteOffset', 0)
                stride = view.get('byteStride', 12)
                actual_min = [math.inf, math.inf, math.inf]
                actual_max = [-math.inf, -math.inf, -math.inf]
                for vertex in range(position['count']):
                    xyz = struct.unpack_from('<fff', binary, base + vertex * stride)
                    for axis, value in enumerate(xyz):
                        actual_min[axis] = min(actual_min[axis], value)
                        actual_max[axis] = max(actual_max[axis], value)
                        magnitude = abs(value)
                        if magnitude > maximum_position_component:
                            maximum_position_component = magnitude
                            maximum_position_mesh = mesh.get('name', f'mesh-{mesh_index}')
                        require(magnitude <= MAX_POSITION_COMPONENT_METERS,
                                f'Mesh {mesh.get("name")} POSITION runaway coordinate: '
                                f'vertex {vertex}, axis {"xyz"[axis]} = {value:.9g} m '
                                f'(limit {MAX_POSITION_COMPONENT_METERS:g} m)')
                declared_min = position.get('min')
                declared_max = position.get('max')
                require(isinstance(declared_min, list) and len(declared_min) == 3 and
                        isinstance(declared_max, list) and len(declared_max) == 3,
                        f'Mesh {mesh.get("name")} POSITION accessor {position_index} lacks VEC3 bounds')
                for axis in range(3):
                    require(declared_min[axis] <= actual_min[axis] + POSITION_BOUNDS_TOLERANCE and
                            declared_max[axis] >= actual_max[axis] - POSITION_BOUNDS_TOLERANCE,
                            f'Mesh {mesh.get("name")} POSITION accessor {position_index} declared bounds '
                            f'do not contain actual axis {"xyz"[axis]} range '
                            f'[{actual_min[axis]:.9g}, {actual_max[axis]:.9g}]')
                position_values_checked += position['count']
                position_accessors_checked.add(position_index)
            require(not any(key.startswith(('JOINTS_', 'WEIGHTS_')) for key in attrs),
                    f'Mesh {mesh.get("name")} contains skinning attributes')
            material_index = primitive.get('material')
            if material_index is not None:
                require(isinstance(material_index, int)
                        and 0 <= material_index < len(gltf.get('materials', [])),
                        f'Mesh {mesh.get("name")} references an invalid material')
                material = gltf['materials'][material_index]
                pbr = material.get('pbrMetallicRoughness', {})
                has_texture = bool(pbr.get('baseColorTexture') or pbr.get('metallicRoughnessTexture')
                                   or material.get('normalTexture') or material.get('occlusionTexture')
                                   or material.get('emissiveTexture'))
                if has_texture:
                    textured_primitives += 1
                    for required in ('TEXCOORD_0', 'COLOR_0'):
                        require(required in attrs,
                                f'Textured mesh {mesh.get("name")} lacks {required}')
                    uv = accessors[attrs['TEXCOORD_0']]
                    color = accessors[attrs['COLOR_0']]
                    require(uv['type'] == 'VEC2' and uv['count'] > 0,
                            f'Invalid TEXCOORD_0 on {mesh.get("name")}')
                    require(color['type'] in ('VEC3', 'VEC4') and color['count'] > 0,
                            f'Invalid COLOR_0 on {mesh.get("name")}')
            mode = primitive.get('mode', 4)
            if 'indices' in primitive:
                require(isinstance(primitive['indices'], int)
                        and 0 <= primitive['indices'] < len(accessors),
                        f'Mesh {mesh.get("name")} references an invalid index accessor')
            if mode == 4:
                if 'indices' in primitive:
                    index_accessor = accessors[primitive['indices']]
                    require(index_accessor['type'] == 'SCALAR',
                            f'Indices are not scalar: {mesh.get("name")}')
                    require(index_accessor['componentType'] in (5121, 5123, 5125),
                            f'Invalid index component type: {mesh.get("name")}')
                    require(index_accessor['count'] % 3 == 0,
                            f'Triangle index count is not divisible by three: {mesh.get("name")}')
                    triangles += index_accessor['count'] // 3
                    # Validate every index against the primitive vertex stream.
                    idx = index_accessor
                    component = {5121: ('B', 1), 5123: ('H', 2), 5125: ('I', 4)}[idx['componentType']]
                    vi = idx['bufferView']
                    view = gltf['bufferViews'][vi]
                    start = view.get('byteOffset', 0) + idx.get('byteOffset', 0)
                    stride = view.get('byteStride', component[1])
                    for i in range(idx['count']):
                        value = struct.unpack_from('<' + component[0], binary, start + i * stride)[0]
                        require(value < position['count'],
                                f'Index outside vertex stream: {mesh.get("name")}')
                    index_values_checked += idx['count']
                else:
                    require(position['count'] % 3 == 0,
                            f'Non-indexed triangle vertex count invalid: {mesh.get("name")}')
                    triangles += position['count'] // 3
            elif mode in (5, 6):
                count = accessors[primitive['indices']]['count'] if 'indices' in primitive else position['count']
                require(count >= 3, f'Triangle strip/fan too short: {mesh.get("name")}')
                triangles += count - 2
            else:
                require(mode in (0, 1, 2, 3), f'Unknown primitive mode {mode}')
    require(triangles > 0, 'GLB contains no triangle geometry')
    if require_texturing:
        require(textured_primitives > 0, 'No textured primitive has complete UV/color attributes')
    return {
        'meshes': len(gltf.get('meshes', [])),
        'primitives': primitive_count,
        'triangles': triangles,
        'texturedPrimitives': textured_primitives,
        'attributesPresent': sorted(attribute_names),
        'indexValuesChecked': index_values_checked,
        'positionAccessorsChecked': len(position_accessors_checked),
        'positionValuesChecked': position_values_checked,
        'maximumPositionComponentMeters': maximum_position_component,
        'maximumPositionComponentMesh': maximum_position_mesh,
        'positionCoordinateLimitMeters': MAX_POSITION_COMPONENT_METERS,
    }


def validate_materials(gltf, views):
    images = gltf.get('images', [])
    textures = gltf.get('textures', [])
    materials = gltf.get('materials', [])
    require(images and textures and materials,
            'Appearance GLB must include materials, textures, and embedded images')
    for index, image in enumerate(images):
        require('bufferView' in image and 'uri' not in image,
                f'Image {index} must be embedded in GLB')
        view_index = image['bufferView']
        require(isinstance(view_index, int) and 0 <= view_index < len(views),
                f'Image {index} references an invalid buffer view')
        require(image.get('mimeType') in ('image/png', 'image/jpeg'),
                f'Image {index} has unsupported/missing MIME type')
    for index, texture in enumerate(textures):
        source = texture.get('source')
        require(isinstance(source, int) and 0 <= source < len(images),
                f'Texture {index} has invalid image source')
    used_textures = set()
    for material in materials:
        pbr = material.get('pbrMetallicRoughness', {})
        for texture_info in (pbr.get('baseColorTexture'), pbr.get('metallicRoughnessTexture'),
                             material.get('normalTexture'), material.get('occlusionTexture'),
                             material.get('emissiveTexture')):
            if texture_info is None:
                continue
            index = texture_info.get('index')
            require(isinstance(index, int) and 0 <= index < len(textures),
                    f'Material {material.get("name")} references invalid texture')
            used_textures.add(index)
        require(pbr.get('baseColorTexture') and pbr.get('metallicRoughnessTexture'),
                f'Material {material.get("name")} lacks base-color or metallic-roughness texture')
    require(used_textures, 'No material uses the embedded textures')
    return {
        'materials': len(materials),
        'textures': len(textures),
        'images': len(images),
        'embeddedImages': len(images),
        'materialNames': [material.get('name', f'material-{i}') for i, material in enumerate(materials)],
        'textureReferencesUsed': len(used_textures),
        'imageNames': [image.get('name', f'image-{i}') for i, image in enumerate(images)],
    }


def validate_rigid_interface(candidate, baseline):
    cand_names, cand_parents = parent_map(candidate)
    base_names, base_parents = parent_map(baseline)
    missing = sorted(REQUIRED_OWNERS - set(cand_names))
    require(not missing, 'Required rigid owners missing: ' + ', '.join(missing))
    missing_base = sorted(REQUIRED_OWNERS - set(base_names))
    require(not missing_base, 'Frozen baseline lacks expected owners: ' + ', '.join(missing_base))
    compare_names = sorted(REQUIRED_OWNERS)
    for name in compare_names:
        ci, bi = cand_names[name], base_names[name]
        cp = cand_parents.get(ci)
        bp = base_parents.get(bi)
        cparent = candidate['nodes'][cp]['name'] if cp is not None else None
        bparent = baseline['nodes'][bp]['name'] if bp is not None else None
        require(cparent == bparent, f'Baseline rigid parent changed for {name}: {bparent} -> {cparent}')
        cm = local_matrix(candidate['nodes'][ci])
        bm = local_matrix(baseline['nodes'][bi])
        require(all(math.isfinite(v) for v in cm), f'Non-finite transform for {name}')
        require(max(abs(a - b) for a, b in zip(cm, bm)) <= 2e-5,
                f'Frozen baseline local transform changed for {name}')
    digit_owners = [name for name in REQUIRED_OWNERS if '-digit-' in name]
    require(len(digit_owners) == 12, 'Internal required digit owner set must contain 12 pivots')
    return {
        'requiredOwners': len(compare_names),
        'baselineOwnersCompared': compare_names,
        'digitHinges': len(digit_owners),
        'unchangedParentAndLocalTransformOwners': len(compare_names),
    }


def era_values(value):
    if isinstance(value, str):
        return [piece.strip() for piece in value.split(',') if piece.strip()]
    if isinstance(value, list):
        return value
    return []


def validate_eras(inventory, gltf):
    parts = inventory.get('parts', [])
    require(parts, 'Appearance inventory has no part records')
    names, _ = parent_map(gltf)
    for part in parts:
        era = part.get('era')
        require(era in ERAS, f'Invalid era on appearance part {part.get("name")}: {era}')
        require(part.get('owner'), f'Appearance part has no rigid owner: {part.get("name")}')
        require(part['owner'] in names,
                f'Appearance part owner is absent from GLB: {part.get("name")} -> {part["owner"]}')
        require(part.get('region'), f'Appearance part has no region: {part.get("name")}')
        require(part.get('role') in ALLOWED_ROLES,
                f'Invalid surface role on appearance part {part.get("name")}: {part.get("role")}')
        if part['owner'] in {'processing', 'power-core', 'builder-optics'} or part['role'] == 'optic':
            require(era == 'builder',
                    f'Advanced system or optic appears before Builder: {part.get("name")}')
        if part['role'] == 'repair':
            require(era != 'maker', f'Later repair appears in Maker: {part.get("name")}')
    nodes_with_mesh = [node for node in gltf.get('nodes', []) if 'mesh' in node]
    require(nodes_with_mesh, 'GLB has no mesh nodes')
    _, parents = parent_map(gltf)
    for node in nodes_with_mesh:
        extras = node.get('extras', {})
        values = era_values(extras.get('exteriorEras'))
        require(values and set(values).issubset(ERAS),
                f'Invalid or missing era eligibility on mesh node {node.get("name")}')
        require(extras.get('region'), f'Missing region tag on mesh node {node.get("name")}')
        require(extras.get('surfaceRole') in ALLOWED_ROLES,
                f'Invalid surface role tag on mesh node {node.get("name")}')
        index = names[node['name']]
        require(index in parents, f'Mesh node has no rigid owner: {node.get("name")}')
        owner = gltf['nodes'][parents[index]].get('name')
        require(owner in names, f'Mesh node owner missing from GLB: {node.get("name")}')
    return {
        'inventoryParts': len(parts),
        'inventoryPartCountsByEra': {era: sum(p.get('era') == era for p in parts) for era in sorted(ERAS)},
        'meshNodesChecked': len(nodes_with_mesh),
        'meshNodesWithValidEraTags': len(nodes_with_mesh),
    }


def validate():
    parser = argparse.ArgumentParser()
    parser.add_argument('--iteration', default='iteration-01')
    args = parser.parse_args()
    require(re.fullmatch(r'iteration-[a-z0-9][a-z0-9-]*', args.iteration) is not None,
            'Iteration must use iteration-<lowercase-label> form')
    model_dir = ITERATION_ROOT / args.iteration
    inventory_path = model_dir / 'appearance-inventory.json'
    inventory = json.loads(repo_file(inventory_path))
    require(inventory.get('status') == 'appearance candidate; owner artistic acceptance pending',
            'Inventory status must preserve pending artistic acceptance')
    generated = inventory.get('generatedFiles', [])
    by_path = {record.get('path'): record for record in generated}
    require(len(by_path) == len(generated), 'Duplicate generated file records')
    source_rel = str(model_dir / 'murderbird-appearance.blend')
    model_rel = str(model_dir / 'murderbird-appearance.glb')
    require(source_rel in by_path and model_rel in by_path,
            'Inventory must hash the native Blender source and runtime GLB')
    file_facts = {}
    for rel, record in by_path.items():
        raw = repo_file(rel)
        digest = hashlib.sha256(raw).hexdigest()
        require(digest == record.get('sha256'), f'Generated-file SHA mismatch: {rel}')
        require(record.get('bytes') == len(raw), f'Generated-file byte count mismatch: {rel}')
        file_facts[rel] = {'bytes': len(raw), 'sha256': digest}
    base_raw = repo_file(BASELINE_PATH)
    base_sha = hashlib.sha256(base_raw).hexdigest()
    require(base_sha == BASELINE_SHA256, 'Frozen alignment-v3 baseline hash changed')
    candidate_raw = repo_file(model_rel)
    candidate, binary = parse_glb(candidate_raw, 'appearance candidate')
    baseline, baseline_binary = parse_glb(base_raw, 'alignment-v3 baseline')
    require(len(candidate.get('buffers', [])) == 1 and not candidate['buffers'][0].get('uri'),
            'Appearance GLB must use one embedded buffer')
    require(candidate['buffers'][0].get('byteLength', 0) <= len(binary),
            'Appearance embedded buffer length exceeds BIN chunk')
    geometry = validate_geometry(candidate, binary)
    baseline_geometry = validate_geometry(baseline, baseline_binary, require_texturing=False)
    material_facts = validate_materials(candidate, candidate.get('bufferViews', []))
    interface = validate_rigid_interface(candidate, baseline)
    era_facts = validate_eras(inventory, candidate)
    report = {
        'status': 'passed',
        'iteration': args.iteration,
        'candidate': {
            'inventory': str(inventory_path),
            'model': model_rel,
            'modelBytes': len(candidate_raw),
            'modelSha256': hashlib.sha256(candidate_raw).hexdigest(),
            'nativeSource': source_rel,
            'generatedFiles': file_facts,
            **geometry,
            **material_facts,
            **interface,
            **era_facts,
        },
        'baseline': {
            'model': str(BASELINE_PATH), 'sha256': base_sha,
            'positionAccessorsChecked': baseline_geometry['positionAccessorsChecked'],
            'positionValuesChecked': baseline_geometry['positionValuesChecked'],
            'maximumPositionComponentMeters': baseline_geometry['maximumPositionComponentMeters'],
            'maximumPositionComponentMesh': baseline_geometry['maximumPositionComponentMesh'],
            'positionCoordinateLimitMeters': MAX_POSITION_COMPONENT_METERS,
        },
        'checks': [
            'Generated native/runtime files match the iteration inventory bytes and SHA-256 values',
            'GLB geometry attributes and node transforms are finite and embedded accessor bounds are valid',
            'Every candidate and frozen-baseline POSITION coordinate is within the 4 m component limit and declared bounds contain actual values',
            'Triangle streams use valid indices; skinned/deforming geometry is absent',
            'Textured primitives carry normals, UVs, and vertex colors; referenced images are embedded',
            'Required rigid owners and all 12 digit pivots retain baseline parent and local transforms',
            'Appearance parts and mesh-node region, role, and era tags use allowed values',
        ],
        'limits': [
            'Asset structure and provenance checks do not assess visual likeness, material quality, motion clearance, physical behavior, or owner acceptance.',
            'The triangle count is the exported primitive count; it is not a visual-quality score.',
        ],
    }
    return report


def main():
    report = validate()
    output = json.dumps(report, indent=2) + '\n'
    destination = (ROOT / 'assets/audit/appearance-v1' / report['iteration']
                   / 'asset-validation.json').resolve()
    allowed = (ROOT / 'assets/audit/appearance-v1').resolve()
    require(destination.is_relative_to(allowed), 'Receipt path must remain under assets/audit/appearance-v1')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(output)
    print(output, end='')


if __name__ == '__main__':
    main()
