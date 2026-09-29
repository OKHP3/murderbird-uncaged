#!/usr/bin/env python3
"""Read-only standard-library inventory for a V19 glTF 2.0 binary export.

Counts metadata and accessor-declared triangles; does not decode geometry,
validate surface parity, motion, clearance, or artistic acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE_REL = Path('assets/models/whole-character-v18/attempt-01/murderbird-whole-character-v18.glb')
BASELINE_SHA256 = 'b59bf9dee1ff681c53b21aedfb1505c1fb944890d673a07b3e3b148fd95babf8'
REQUIRED_RIGID_NODE_COUNT = 52
ERAS = ('maker', 'mechanic', 'builder')
REQUIRED_V19_TAGS = ('region', 'surfaceRole', 'exteriorEras')


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_glb(path: Path) -> tuple[dict, dict]:
    data = path.read_bytes()
    if len(data) < 20:
        raise ValueError('File is too short to be a GLB 2.0 container')
    magic, version, total_length = struct.unpack_from('<III', data, 0)
    if magic != 0x46546C67 or version != 2 or total_length != len(data):
        raise ValueError('Invalid GLB magic/version/declared byte length')
    offset = 12
    json_doc = None
    chunks = []
    while offset < len(data):
        if offset + 8 > len(data):
            raise ValueError('Truncated GLB chunk header')
        length, chunk_type = struct.unpack_from('<II', data, offset)
        offset += 8
        end = offset + length
        if end > len(data):
            raise ValueError('Truncated GLB chunk payload')
        chunks.append({'length': length, 'type': chunk_type})
        if chunk_type == 0x4E4F534A:
            if json_doc is not None:
                raise ValueError('Multiple JSON chunks')
            json_doc = json.loads(data[offset:end].decode('utf-8').rstrip('\x00 \t\r\n'))
        offset = end
    if json_doc is None:
        raise ValueError('GLB has no JSON chunk')
    return json_doc, {'bytes': len(data), 'version': version, 'chunks': chunks}


def era_list(value) -> list[str]:
    if isinstance(value, str):
        values = value.split(',')
    elif isinstance(value, list):
        values = value
    else:
        return []
    return sorted({str(v).strip().lower() for v in values if str(v).strip()})


def triangle_count(primitive: dict, accessors: list[dict]) -> int:
    mode = primitive.get('mode', 4)
    if 'indices' in primitive:
        count = accessors[primitive['indices']].get('count', 0)
    else:
        position = primitive.get('attributes', {}).get('POSITION')
        count = accessors[position].get('count', 0) if position is not None else 0
    if mode == 4:
        return count // 3
    if mode in (5, 6):
        return max(0, count - 2)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--glb', required=True, help='V19 GLB path, relative to repository root or absolute')
    ap.add_argument('--sha256', required=True, help='Expected exact GLB SHA-256')
    ap.add_argument('--out', required=True, help='New JSON output path, relative to repository root or absolute')
    args = ap.parse_args()

    glb = Path(args.glb); glb = glb if glb.is_absolute() else ROOT / glb
    out = Path(args.out); out = out if out.is_absolute() else ROOT / out
    baseline = ROOT / BASELINE_REL
    if not glb.is_file():
        raise FileNotFoundError(glb)
    if out.exists():
        raise FileExistsError(f'Refusing to overwrite existing report: {out}')
    actual_sha = digest(glb)
    if actual_sha.lower() != args.sha256.lower():
        raise ValueError(f'GLB SHA-256 mismatch: expected {args.sha256}, got {actual_sha}')
    if digest(baseline) != BASELINE_SHA256:
        raise ValueError('Pinned V18 baseline GLB hash changed; refusing name-based comparison')

    doc, container = read_glb(glb)
    base, _ = read_glb(baseline)
    nodes = doc.get('nodes', [])
    base_nodes = base.get('nodes', [])
    mesh_nodes = [i for i, n in enumerate(nodes) if 'mesh' in n]
    base_mesh_names = {n.get('name') for n in base_nodes if 'mesh' in n and n.get('name')}

    parent_ids: dict[int, list[int]] = {i: [] for i in range(len(nodes))}
    for parent_i, node in enumerate(nodes):
        for child_i in node.get('children', []):
            if 0 <= child_i < len(nodes):
                parent_ids[child_i].append(parent_i)

    def parent_name(i: int):
        names = [nodes[p].get('name') for p in parent_ids[i]]
        return names[0] if len(names) == 1 else names or None

    rigid_names = sorted(n.get('name', f'node-{i}') for i, n in enumerate(nodes) if 'mesh' not in n)
    expected_rigid_names = sorted(n.get('name', f'node-{i}') for i, n in enumerate(base_nodes) if 'mesh' not in n)
    new_mesh_nodes = []
    for i in mesh_nodes:
        node = nodes[i]
        name = node.get('name', f'node-{i}')
        if name not in base_mesh_names or 'v19' in name.lower():
            new_mesh_nodes.append(i)

    meshes = doc.get('meshes', [])
    accessors = doc.get('accessors', [])
    era_totals = {era: {'visibleMeshNodes': 0, 'triangles': 0} for era in ERAS}
    untagged_mesh_nodes = []
    unknown_era_nodes = []
    uv_sets = set()
    uv_accessors = set()
    uv_primitive_count = 0
    for i in mesh_nodes:
        node = nodes[i]
        extras = node.get('extras') or {}
        eras = era_list(extras.get('exteriorEras'))
        mesh = meshes[node['mesh']]
        tris = sum(triangle_count(p, accessors) for p in mesh.get('primitives', []))
        if not eras:
            untagged_mesh_nodes.append(node.get('name', f'node-{i}'))
        for era in eras:
            if era not in era_totals:
                unknown_era_nodes.append({'node': node.get('name', f'node-{i}'), 'era': era})
                continue
            era_totals[era]['visibleMeshNodes'] += 1
            era_totals[era]['triangles'] += tris
        for primitive in mesh.get('primitives', []):
            for semantic, accessor_i in primitive.get('attributes', {}).items():
                if semantic.startswith('TEXCOORD_'):
                    uv_sets.add(semantic)
                    uv_accessors.add(accessor_i)
                    uv_primitive_count += 1

    v19_parts = []
    missing_tags = []
    for i in new_mesh_nodes:
        node = nodes[i]
        extras = node.get('extras') or {}
        item = {'name': node.get('name', f'node-{i}'), 'parent': parent_name(i),
                'meshIndex': node['mesh'], 'region': extras.get('region'),
                'surfaceRole': extras.get('surfaceRole'),
                'exteriorEras': era_list(extras.get('exteriorEras'))}
        v19_parts.append(item)
        absent = [key for key in REQUIRED_V19_TAGS if extras.get(key) in (None, '')]
        if absent:
            missing_tags.append({'name': item['name'], 'missing': absent})

    inspection_axes = []
    for i, node in enumerate(nodes):
        extras = node.get('extras') or {}
        if 'inspectionAxis' in extras or 'inspectionOpenRadians' in extras:
            inspection_axes.append({'node': node.get('name', f'node-{i}'),
                                    'inspectionAxis': extras.get('inspectionAxis'),
                                    'inspectionOpenRadians': extras.get('inspectionOpenRadians')})

    materials = doc.get('materials', [])
    images = doc.get('images', [])
    textures = doc.get('textures', [])
    material_texture_refs = Counter()
    for mat in materials:
        pbr = mat.get('pbrMetallicRoughness', {})
        for key in ('baseColorTexture', 'metallicRoughnessTexture'):
            if key in pbr: material_texture_refs[key] += 1
        for key in ('normalTexture', 'occlusionTexture', 'emissiveTexture'):
            if key in mat: material_texture_refs[key] += 1

    errors = []
    if len(rigid_names) != REQUIRED_RIGID_NODE_COUNT:
        errors.append(f'Expected {REQUIRED_RIGID_NODE_COUNT} rigid nodes, found {len(rigid_names)}')
    if rigid_names != expected_rigid_names:
        errors.append('Rigid-node names differ from the pinned V18 baseline')
    if missing_tags:
        errors.append(f'{len(missing_tags)} added/V19 mesh nodes lack required tags')

    script_path = Path(__file__).resolve()
    report = {
        'status': 'inventory-complete' if not errors else 'contract-failure',
        'glb': {'path': str(glb.relative_to(ROOT)) if glb.is_relative_to(ROOT) else str(glb),
                'sha256': actual_sha, **container},
        'baseline': {'path': BASELINE_REL.as_posix(), 'sha256': BASELINE_SHA256},
        'script': {'path': str(script_path.relative_to(ROOT)), 'sha256': digest(script_path)},
        'sceneInventory': {'nodeCount': len(nodes), 'rigidNodeCount': len(rigid_names),
                           'rigidNodeNames': rigid_names, 'meshNodeCount': len(mesh_nodes),
                           'meshDefinitionCount': len(meshes), 'skinsCount': len(doc.get('skins', [])),
                           'skinJointReferences': sum(len(s.get('joints', [])) for s in doc.get('skins', [])),
                           'uniqueJointNodeCount': len({j for s in doc.get('skins', []) for j in s.get('joints', [])})},
        'perEraMeshAndTriangleCounts': era_totals,
        'untaggedMeshNodes': sorted(untagged_mesh_nodes),
        'unknownEraTags': unknown_era_nodes,
        'newV19MeshParts': v19_parts,
        'missingRequiredV19PartTags': missing_tags,
        'materialsAndTextures': {'materialCount': len(materials), 'imageCount': len(images),
                                 'textureCount': len(textures), 'materialTextureReferences': dict(material_texture_refs),
                                 'uvSemanticCount': len(uv_sets), 'uvSemantics': sorted(uv_sets),
                                 'uvPrimitiveAttributeCount': uv_primitive_count,
                                 'uniqueUvAccessorCount': len(uv_accessors)},
        'inspectionAxisExtras': inspection_axes,
        'errors': errors,
        'limits': ['Metadata/accessor inventory only; triangle totals are inferred from glTF primitive index counts.',
                   'Does not decode positions, compare exported/native surfaces, or test browser assembly.',
                   'Does not test pose behavior, containment, collision clearance, physical validity, or likeness.',
                   'Passing this inventory is not artistic acceptance.']
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'glbSha256': actual_sha,
                      'rigidNodeCount': len(rigid_names), 'meshNodes': len(mesh_nodes),
                      'newV19Parts': len(v19_parts), 'errors': errors}, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f'inspect-v19-export: {exc}', file=sys.stderr)
        raise
