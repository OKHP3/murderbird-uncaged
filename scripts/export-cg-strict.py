"""Strict derivative exporter, based on cg-supervised-export.py at fb4310c2fe4d3cf644204469575ecbe2379690f4.
Historical imported exporter remains byte-preserved for its provenance ledger.
This successor bypasses lossy custom-normal storage using a float vertex attribute.
The independent native parity checker remains the acceptance gate.
"""
"""Local review GLB export; run in Blender or call export(scene, output_path).

Evaluated visible meshes retain polygon material slots and every UV layer.
No joining, material rewriting, texture resizing, source baking or saving.
The native glTF exporter handles supported Principled PBR and transmission.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import struct
import math
import bpy

STRICT_NORMAL_L2_TOLERANCE = 2e-5


def verify_batched_normal_readback(mesh, expected):
    """Reject loss in Blender's custom-normal round trip before writing a GLB.

    Custom split normals are not an exact float store. UV readback and face
    counts cannot certify their fidelity. This check preserves the existing
    native/export tolerance; it does not repair or approve a failed batch.
    """
    actual = mesh.corner_normals
    if len(actual) != len(expected):
        raise AssertionError('Batched normal corner coverage changed')
    maximum = 0.0
    for corner, wanted in zip(actual, expected):
        vector = tuple(corner.vector)
        length = math.sqrt(sum(value * value for value in vector))
        wanted_length = math.sqrt(sum(value * value for value in wanted))
        if not math.isfinite(length) or length == 0 or not math.isfinite(wanted_length) or wanted_length == 0:
            raise AssertionError('Batched normal is not finite and nonzero')
        error = math.sqrt(sum((value / length - target / wanted_length) ** 2
                              for value, target in zip(vector, wanted)))
        maximum = max(maximum, error)
    if maximum > STRICT_NORMAL_L2_TOLERANCE:
        raise AssertionError(f'Batched normal fidelity failed for {mesh.name}: '
                             f'L2 {maximum:.12g} > {STRICT_NORMAL_L2_TOLERANCE}; '
                             'no derivative written; preserve native source')
    return maximum


def replace_exact_normal_accessors(path):
    """Rebind same-vertex float transport; no spatial matching or averaging.

    JSON changes only. The binary chunk (positions, UVs, images and transported
    values) remains byte-identical. No source model or historical export changes.
    """
    raw = Path(path).read_bytes()
    magic, version, total = struct.unpack_from('<4sII', raw)
    assert (magic, version, total) == (b'glTF', 2, len(raw))
    size, kind = struct.unpack_from('<II', raw, 12)
    assert kind == 0x4e4f534a
    doc = json.loads(raw[20:20 + size])
    assert not doc.get('skins') and not doc.get('animations'), 'static export only'
    binary_chunk = raw[20 + size:]
    binary_size, binary_kind = struct.unpack_from('<II', binary_chunk)
    assert binary_kind == 0x004e4942 and len(binary_chunk) == binary_size + 8
    blob = binary_chunk[8:]
    count = 0
    for mesh in doc.get('meshes', []):
        for primitive in mesh['primitives']:
            assert primitive.get('mode', 4) == 4 and 'TANGENT' not in primitive['attributes']
            attributes = primitive['attributes']
            index = attributes.pop('_CG_EXACT_NORMAL')
            accessor = doc['accessors'][index]
            assert accessor['type'] == 'VEC3' and accessor['componentType'] == 5126
            assert not accessor.get('sparse') and not accessor.get('normalized')
            assert accessor['count'] == doc['accessors'][attributes['POSITION']]['count'] > 0
            view = doc['bufferViews'][accessor['bufferView']]
            assert view.get('buffer', 0) == 0
            stride = view.get('byteStride', 12)
            start = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
            end = start + (accessor['count'] - 1) * stride + 12
            assert end <= view.get('byteOffset', 0) + view['byteLength'] <= len(blob)
            for i in range(accessor['count']):
                normal = struct.unpack_from('<3f', blob, start + i * stride)
                length = math.sqrt(sum(v * v for v in normal))
                assert math.isfinite(length) and abs(length - 1) < 2e-5, 'invalid exact normal'
            attributes['NORMAL'] = index
            count += 1
    assert count, 'empty export cannot establish normal fidelity'
    encoded = json.dumps(doc, separators=(',', ':')).encode()
    encoded += b' ' * (-len(encoded) % 4)
    result = struct.pack('<4sII', b'glTF', 2, 20 + len(encoded) + len(binary_chunk))
    result += struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + binary_chunk
    Path(path).write_bytes(result)


def _digest_mesh(mesh):
    digest = hashlib.sha256()
    for vertex in mesh.vertices:
        digest.update(struct.pack('<3f', *vertex.co))
    for polygon in mesh.polygons:
        digest.update(str((tuple(polygon.vertices), polygon.material_index)).encode())
    for layer in mesh.uv_layers:
        digest.update(layer.name.encode())
        for loop in layer.data:
            digest.update(struct.pack('<2f', *loop.uv))
    return digest.hexdigest()


def inspect_glb(path):
    """Independently decode JSON chunk and material-indexed triangle inventory."""
    raw = Path(path).read_bytes()
    magic, version, length = struct.unpack_from('<4sII', raw)
    if (magic, version, length) != (b'glTF', 2, len(raw)):
        raise AssertionError('Invalid GLB header')
    size, kind = struct.unpack_from('<II', raw, 12)
    if kind != 0x4e4f534a:
        raise AssertionError('Missing GLB JSON chunk')
    doc = json.loads(raw[20:20 + size])
    triangles = Counter()
    uv_primitives = 0
    object_triangles = {}
    for mesh in doc.get('meshes', []):
        for primitive in mesh['primitives']:
            if primitive.get('mode', 4) != 4:
                raise AssertionError('Expected triangles')
            count = doc['accessors'][primitive['indices']]['count']
            triangles[doc['materials'][primitive['material']]['name']] += count // 3
            uv_primitives += 'TEXCOORD_0' in primitive['attributes']
    for node in doc.get('nodes', []):
        if 'mesh' not in node:
            continue
        counts = Counter()
        for primitive in doc['meshes'][node['mesh']]['primitives']:
            counts[doc['materials'][primitive['material']]['name']] += doc['accessors'][primitive['indices']]['count'] // 3
        object_triangles[node['name']] = dict(counts)
    image_records = []
    for image in doc.get('images', []):
        if 'bufferView' not in image or 'uri' in image:
            raise AssertionError('Image is not embedded')
        image_records.append({'name': image.get('name'), 'mimeType': image.get('mimeType'),
                              'bytes': doc['bufferViews'][image['bufferView']]['byteLength']})
    return {'triangles_by_material': dict(triangles), 'images': image_records,
            'materials': [{'name': m.get('name'), 'extensions': m.get('extensions', {}),
                           'pbr': m.get('pbrMetallicRoughness', {})} for m in doc.get('materials', [])],
            'triangles_by_object': object_triangles, 'uv_primitives': uv_primitives, 'extensions_used': doc.get('extensionsUsed', []),
            'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


def _export_fidelity(scene, output_path):
    """Export visible evaluated geometry, returning source and GLB parity evidence.

    Requires scene to be the current Blender scene, object mode. Flattening world
    transforms is intentional: this is a static appearance review, not a rig.
    Unsupported native procedural shader nodes are not silently baked.
    """
    if scene != bpy.context.scene or bpy.context.mode != 'OBJECT':
        raise ValueError('Use the current scene in object mode')
    layer = bpy.context.view_layer
    depsgraph = bpy.context.evaluated_depsgraph_get()
    sources = [o for o in scene.objects if o.type == 'MESH'
               and not o.hide_render and not o.hide_viewport and o.visible_get(view_layer=layer)
               and not o.hide_get(view_layer=layer) and not o.get('authoringGuide')]
    if not sources:
        raise ValueError('No visible character meshes')
    before_counts = tuple(len(x) for x in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.images))
    fingerprints = {o.name: _digest_mesh(o.data) for o in sources}
    selected, active = list(bpy.context.selected_objects), layer.objects.active
    collection = bpy.data.collections.new('Temporary supervised GLB export')
    scene.collection.children.link(collection)
    meshes, records, triangles, expected_images = [], [], Counter(), set()
    shader_warnings = []
    try:
        bpy.ops.object.select_all(action='DESELECT')
        for source in sources:
            evaluated = source.evaluated_get(depsgraph)
            mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
            meshes.append(mesh)
            mesh.calc_loop_triangles()
            counts = Counter(p.material_index for p in mesh.polygons)
            for index in counts:
                if index >= len(mesh.materials) or mesh.materials[index] is None:
                    raise ValueError(f'{source.name}: face slot {index} has no material')
            object_triangles = Counter()
            for tri in mesh.loop_triangles:
                object_triangles[mesh.materials[tri.material_index].name] += 1
                triangles[mesh.materials[tri.material_index].name] += 1
            for index in counts:
                material = mesh.materials[index]
                if material.use_nodes:
                    for node in material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE' and node.image:
                            if min(node.image.size) < 1:
                                raise ValueError('Missing image pixels: ' + node.image.name)
                            expected_images.add(node.image.name)
                        if node.type in {'TEX_NOISE', 'TEX_VORONOI', 'TEX_MUSGRAVE', 'BUMP'}:
                            shader_warnings.append(material.name + ': native ' + node.type + ' may not translate')
            records.append({'object': source.name, 'faces': len(mesh.polygons),
                'slots': [m.name if m else None for m in mesh.materials],
                'face_counts_by_slot': dict(counts), 'triangles_by_material': dict(object_triangles), 'evaluated_mesh_sha256': _digest_mesh(mesh),
                'uv_layers': [u.name for u in mesh.uv_layers],
                'uv_loops': len(mesh.loops) if mesh.uv_layers else 0})
            obj = bpy.data.objects.new('Review ' + source.name, mesh)
            collection.objects.link(obj)
            obj.matrix_world = evaluated.matrix_world.copy()
            obj.select_set(True)
        layer.objects.active = collection.objects[0]
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.export_scene.gltf(filepath=str(output_path), export_format='GLB',
            use_selection=True, export_extras=True, export_apply=False,
            export_materials='EXPORT', export_image_format='AUTO',
            export_texcoords=True, export_normals=True)
        inspection = inspect_glb(output_path)
        if dict(triangles) != inspection['triangles_by_material']:
            raise AssertionError('GLB triangle material assignment differs from evaluated source')
        for record in records:
            if inspection['triangles_by_object'].get('Review ' + record['object']) != record['triangles_by_material']:
                raise AssertionError('Per-object material triangle mismatch: ' + record['object'])
        receipt = {'source_meshes': records, 'triangles_by_material': dict(triangles),
                   'referenced_native_images': sorted(expected_images), 'glb': inspection,
                   'shader_parity_warnings': sorted(set(shader_warnings)),
                   'method': 'Unmodified evaluated mesh copies, original material slots and UVs; static world transforms',
                   'face_material_parity': True, 'texture_resizing': False}
    finally:
        for obj in list(collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(collection)
        for mesh in meshes:
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected:
            obj.select_set(True)
        layer.objects.active = active
    after_counts = tuple(len(x) for x in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.images))
    receipt['native_meshes_unchanged'] = fingerprints == {o.name: _digest_mesh(o.data) for o in sources}
    receipt['temporary_datablocks_removed'] = before_counts == after_counts
    if not receipt['native_meshes_unchanged'] or not receipt['temporary_datablocks_removed']:
        raise AssertionError('Export changed source or leaked temporary datablocks')
    return receipt


def export(scene, output_path, *, batched=True):
    """Default: exact-material batching, preserving evaluated triangle corner data.

    batched=False retains the individual-object audit baseline. Batching flattens
    world transforms and converts loop UVs/normals into independent triangle
    corners, so seams and face slots cannot collapse during joining.
    """
    if Path(output_path).exists():
        raise FileExistsError('Use a new derivative path; retained assets are immutable')
    pending_output = Path(output_path).with_name(Path(output_path).name + '.pending.glb')
    if pending_output.exists():
        raise FileExistsError('Preserve the incomplete derivative and choose a new path')
    if not batched:
        raise ValueError('Strict normal transport requires static batched export')
    if scene != bpy.context.scene or bpy.context.mode != 'OBJECT':
        raise ValueError('Use the current scene in object mode')
    layer = bpy.context.view_layer
    depsgraph = bpy.context.evaluated_depsgraph_get()
    sources = [o for o in scene.objects if o.type == 'MESH' and not o.hide_render
               and not o.hide_viewport and o.visible_get(view_layer=layer)
               and not o.hide_get(view_layer=layer) and not o.get('authoringGuide')]
    fingerprints = {o.name: _digest_mesh(o.data) for o in sources}
    before = tuple(len(x) for x in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.images))
    selected, active = list(bpy.context.selected_objects), layer.objects.active
    groups, records = {}, []
    for source in sources:
        evaluated = source.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
        try:
            mesh.calc_loop_triangles()
            world, normal_matrix = evaluated.matrix_world, evaluated.matrix_world.to_3x3().inverted().transposed()
            render_uv = next((u for u in mesh.uv_layers if u.active_render), mesh.uv_layers.active)
            counts = Counter()
            for triangle in mesh.loop_triangles:
                index = triangle.material_index
                material = mesh.materials[index] if index < len(mesh.materials) else None
                if material is None:
                    raise ValueError(source.name + ': missing assigned material')
                group = groups.setdefault(material, {'vertices': [], 'normals': [], 'uvs': {}, 'digest': hashlib.sha256()})
                counts[material.name] += 1
                # Negative scale requires reversed winding after baking transforms.
                loops = list(triangle.loops)
                if world.to_3x3().determinant() < 0:
                    loops.reverse()
                for loop_index in loops:
                    corner = mesh.loops[loop_index]
                    position = world @ mesh.vertices[corner.vertex_index].co
                    normal = (normal_matrix @ mesh.corner_normals[loop_index].vector).normalized()
                    group['vertices'].append(tuple(position)); group['normals'].append(tuple(normal))
                    count = len(group['vertices'])
                    required_uvs = {n.uv_map for n in material.node_tree.nodes if n.type == 'UVMAP' and n.uv_map} if material.use_nodes else set()
                    missing_uvs = required_uvs - {u.name for u in mesh.uv_layers}
                    if missing_uvs:
                        raise ValueError('Missing explicitly referenced UV layers: ' + str(missing_uvs))
                    corner_uvs = {u.name: tuple(u.data[loop_index].uv) for u in mesh.uv_layers if u.name in required_uvs}
                    if render_uv:
                        corner_uvs['cg-supervised-active-uv'] = tuple(render_uv.data[loop_index].uv)
                    for name in set(group['uvs']) | set(corner_uvs):
                        if name not in group['uvs']:
                            group['uvs'][name] = [(0., 0.)] * (count - 1)
                        values = group['uvs'][name]
                        values.append(corner_uvs.get(name, (0., 0.)))
                    group['digest'].update(struct.pack('<6f', *position, *normal))
                    for name, value in sorted(corner_uvs.items()):
                        group['digest'].update(name.encode()); group['digest'].update(struct.pack('<2f', *value))
            records.append({'object': source.name, 'faces': len(mesh.polygons), 'triangles_by_material': dict(counts), 'uv_layers': [u.name for u in mesh.uv_layers]})
        finally:
            evaluated.to_mesh_clear()
    collection = bpy.data.collections.new('Temporary supervised batched export')
    scene.collection.children.link(collection)
    created = []
    try:
        bpy.ops.object.select_all(action='DESELECT')
        for material, group in groups.items():
            mesh = bpy.data.meshes.new('Supervised ' + material.name); created.append(mesh)
            # Share equal positions while retaining independent loop normals/UVs.
            position_indices, positions, corner_indices, exact_normals = {}, [], [], []
            for i, position in enumerate(group['vertices']):
                key = (position, group['normals'][i], tuple((name, values[i]) for name, values in sorted(group['uvs'].items())))
                # Retain pre-existing zero-area triangles without collapsing their indices.
                triangle_start = (i // 3) * 3
                if len(set(group['vertices'][triangle_start:triangle_start + 3])) < 3:
                    key = (key, i)
                if key not in position_indices:
                    position_indices[key] = len(positions); positions.append(position)
                    x, y, z = group['normals'][i]
                    exact_normals.append((x, z, -y))
                corner_indices.append(position_indices[key])
            mesh.from_pydata(positions, [], [tuple(corner_indices[i:i + 3]) for i in range(0, len(corner_indices), 3)])
            mesh.materials.append(material)
            for face in mesh.polygons:
                face.use_smooth = True
            mesh.normals_split_custom_set(group['normals'])
            # Generic POINT float attributes avoid custom-normal corner-basis loss.
            attribute = mesh.attributes.new('_CG_EXACT_NORMAL', 'FLOAT_VECTOR', 'POINT')
            attribute.data.foreach_set('vector', [v for normal in exact_normals for v in normal])
            for name, values in sorted(group['uvs'].items(), key=lambda item: item[0] != 'cg-supervised-active-uv'):
                uv = mesh.uv_layers.new(name=name)
                uv.data.foreach_set('uv', [value for pair in values for value in pair])
                if name == 'cg-supervised-active-uv':
                    uv.active_render = True; mesh.uv_layers.active = uv
            # Read back copied corner attributes before export; exact float32 UVs.
            for name, values in group['uvs'].items():
                for actual, expected in zip(mesh.uv_layers[name].data, values):
                    if tuple(actual.uv) != expected:
                        raise AssertionError('UV corner changed while batching')
            obj = bpy.data.objects.new('Supervised ' + material.name, mesh)
            collection.objects.link(obj); obj.select_set(True)
        layer.objects.active = collection.objects[0]
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.export_scene.gltf(filepath=str(pending_output), export_format='GLB', use_selection=True,
            export_extras=True, export_apply=False, export_materials='EXPORT',
            export_image_format='AUTO', export_texcoords=True, export_normals=True,
            export_attributes=True, export_yup=True, export_tangents=False,
            export_draco_mesh_compression_enable=False)
        replace_exact_normal_accessors(pending_output)
        inspection = inspect_glb(pending_output)
        expected = {material.name: len(group['vertices']) // 3 for material, group in groups.items()}
        if inspection['triangles_by_material'] != expected:
            raise AssertionError('Batched GLB changed face material coverage')
        receipt = {'source_meshes': records, 'triangles_by_material': expected, 'glb': inspection,
                   'batched_meshes': len(groups), 'face_material_parity': True, 'uv_corner_readback': True,
                   'corner_attribute_sha256': {m.name: g['digest'].hexdigest() for m, g in groups.items()},
                   'normals': 'Evaluated inverse-transpose normals carried by float32 POINT attribute through vertex remapping; NORMAL accessor rebound after export; no tangent claim',
                   'method': 'Exact material grouping, world-space triangles with independent UV/normal corners',
                   'uv_policy': 'Active render UV normalized to channel zero; all explicit shader UVMap references retained; unused historical channels omitted',
                   'texture_resizing': False, 'scope': 'Static review only; no animation or hierarchy parity claimed'}
    finally:
        for obj in list(collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(collection)
        for mesh in created:
            bpy.data.meshes.remove(mesh)
        for obj in selected:
            obj.select_set(True)
        layer.objects.active = active
    after = tuple(len(x) for x in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.images))
    receipt['native_meshes_unchanged'] = fingerprints == {o.name: _digest_mesh(o.data) for o in sources}
    receipt['temporary_datablocks_removed'] = before == after
    if not receipt['native_meshes_unchanged'] or not receipt['temporary_datablocks_removed']:
        raise AssertionError('Source mutation or temporary datablock leak')
    pending_output.rename(output_path)
    return receipt


if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--receipt', required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    receipt = export(bpy.context.scene, args.output)
    Path(args.receipt).write_text(json.dumps(receipt, indent=2) + '\n')
