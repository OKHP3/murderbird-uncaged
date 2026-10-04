"""Independent saved-native binding inspection; no producer imports or scene writes."""
import argparse, datetime, hashlib, json, struct, sys, traceback
from pathlib import Path
import bpy

ROOT = Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
SOURCE = 'CGH17 frontal crown root'
SUCCESSOR = 'CGRS04 source-scale frontal crown appearance'
UV_NAME = 'head17-normalized-local'


def sha_bytes(v):
    return hashlib.sha256(bytes(v)).hexdigest()


def sha_file(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def original(v):
    return getattr(v, 'original', v) if v is not None else None


def identity(a, b):
    a, b = original(a), original(b)
    return a is not None and b is not None and a.as_pointer() == b.as_pointer()


def canonical(v):
    if v is None or isinstance(v, (str, int, float, bool)):
        return v
    try:
        return [canonical(x) for x in v]
    except TypeError:
        return str(v)


def digest_json(v):
    return sha_bytes(json.dumps(v, sort_keys=True, separators=(',', ':')).encode())


def uv_snapshot(mesh):
    return {'active': mesh.uv_layers.active.name if mesh.uv_layers.active else None,
            'layers': [{'name': layer.name, 'active_render': layer.active_render,
                        'values': [list(item.uv) for item in layer.data]} for layer in mesh.uv_layers]}


def cage_snapshot(obj):
    mesh = obj.data
    return {'vertices': [list(v.co) for v in mesh.vertices],
            'edges': [list(e.vertices) for e in mesh.edges],
            'polygons': [{'vertices': list(p.vertices), 'material_index': p.material_index,
                          'use_smooth': p.use_smooth} for p in mesh.polygons],
            'loops': [[l.vertex_index, l.edge_index] for l in mesh.loops],
            'uv': uv_snapshot(mesh), 'matrix_world': [list(r) for r in obj.matrix_world],
            'parent': obj.parent.name if obj.parent else None}


def graph_snapshot(mat):
    if not mat.use_nodes or not mat.node_tree:
        return {'use_nodes': mat.use_nodes}
    result = {'use_nodes': mat.use_nodes, 'nodes': [], 'links': []}
    for n in mat.node_tree.nodes:
        row = {'name': n.name, 'type': n.bl_idname,
               'inputs': [(s.identifier, canonical(getattr(s, 'default_value', None))) for s in n.inputs]}
        for key in ('operation', 'blend_type', 'mode', 'space', 'uv_map', 'extension', 'interpolation', 'is_active_output'):
            if hasattr(n, key): row[key] = canonical(getattr(n, key))
        if n.type == 'TEX_IMAGE':
            im = original(n.image)
            row['image'] = {'name': im.name if im else None,
                            'packed_sha256': sha_bytes(im.packed_file.data) if im and im.packed_file else None,
                            'colorspace': im.colorspace_settings.name if im else None}
        result['nodes'].append(row)
    for l in mat.node_tree.links:
        result['links'].append((l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier))
    return result


def incoming(node, name):
    sock = node.inputs.get(name)
    links = list(sock.links) if sock else []
    if len(links) != 1: raise ValueError('Expected one link into '+node.bl_idname+'.'+name)
    l = links[0]
    return l.from_node, l.from_socket.name


def prove_graph(mat, expected, predicates):
    nt = mat.node_tree
    outputs = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output]
    predicates['one_active_material_output'] = len(outputs) == 1
    if len(outputs) != 1: raise ValueError('No unique active material output')
    bsdf, bsdf_socket = incoming(outputs[0], 'Surface')
    predicates['active_output_uses_principled_BSDF'] = bsdf.type == 'BSDF_PRINCIPLED' and bsdf_socket == 'BSDF'
    base, base_socket = incoming(bsdf, 'Base Color')
    sep, rough_socket = incoming(bsdf, 'Roughness')
    metal_sep, metal_socket = incoming(bsdf, 'Metallic')
    orm, orm_socket = incoming(sep, 'Color')
    normal, normal_socket = incoming(bsdf, 'Normal')
    normal_tex, normal_tex_socket = incoming(normal, 'Color')
    predicates.update(basecolor_direct_color_link=base.type == 'TEX_IMAGE' and base_socket == 'Color',
                      orm_rgb_separate=sep.type == 'SEPARATE_COLOR' and sep.mode == 'RGB',
                      roughness_from_orm_green=rough_socket == 'Green',
                      metallic_from_same_orm_blue=metal_sep.as_pointer() == sep.as_pointer() and metal_socket == 'Blue',
                      orm_color_image_link=orm.type == 'TEX_IMAGE' and orm_socket == 'Color',
                      normal_map_color_link=normal.type == 'NORMAL_MAP' and normal_tex.type == 'TEX_IMAGE' and normal_tex_socket == 'Color',
                      normal_map_to_bsdf=normal_socket == 'Normal',
                      normal_tangent_selected_uv=normal.space == 'TANGENT' and normal.uv_map == UV_NAME)
    roles = {'basecolor': base, 'orm': orm, 'normal': normal_tex}
    bindings = {}
    for role, node in roles.items():
        record = expected[role]
        im = original(node.image)
        expected_image = bpy.data.images.get(record['name'])
        src, vector_socket = incoming(node, 'Vector')
        packed_hash = sha_bytes(im.packed_file.data) if im and im.packed_file else None
        predicates[role+'_evaluated_original_image_identity'] = identity(node.image, expected_image)
        predicates[role+'_actual_packed_bytes_match_record'] = packed_hash == record['sha256']
        predicates[role+'_expected_colorspace'] = bool(im) and im.colorspace_settings.name == record['colorspace']
        predicates[role+'_explicit_UV_vector_link'] = src.type == 'UVMAP' and vector_socket == 'UV' and src.uv_map == UV_NAME
        bindings[role] = {'expected_image': record['name'], 'evaluated_image_original': im.name if im else None,
                          'packed_sha256': packed_hash, 'recorded_sha256': record['sha256'],
                          'uv_source_type': src.bl_idname, 'uv_source_layer': getattr(src, 'uv_map', None),
                          'path': [src.bl_idname+'.'+vector_socket, node.bl_idname+'.Vector'],
                          'expected_original_pointer': expected_image.as_pointer() if expected_image else None,
                          'evaluated_original_pointer': im.as_pointer() if im else None}
    return {'links': [{'from_node_type': l.from_node.bl_idname, 'from_socket': l.from_socket.name,
                       'to_node_type': l.to_node.bl_idname, 'to_socket': l.to_socket.name} for l in nt.links],
            'bindings': bindings}


def root_relative(path):
    text = str(path)
    marker = '/assets/'
    return ROOT / ('assets/' + text.split(marker, 1)[1]) if marker in text else Path(path)


def run(era, packet, manifest):
    receipt_path = packet/era/'receipt.json'
    receipt = json.loads(receipt_path.read_text())
    module = next(v for v in receipt['module_results'].values() if v.get('newMaps'))
    expected = {v['role']: v for v in module['newMaps']}
    native = packet/era/('murderbird-recursive-'+era+'.blend')
    source = root_relative(receipt['source_native'])
    native_expected = next(f['sha256'] for f in manifest['files'] if f['path'].endswith('/'+era+'/'+native.name))
    initial_native_sha, initial_source_sha = sha_file(native), sha_file(source)
    map_paths = {role: root_relative(record['path']) for role, record in expected.items()}
    before_map_sha = {role: sha_file(p) for role, p in map_paths.items()}
    predicates = {'native_matches_frozen_manifest': initial_native_sha == native_expected,
                  'source_native_matches_record': initial_source_sha == receipt['source_native_sha256']}
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    old = bpy.data.objects.get(SOURCE)
    if old is None: raise ValueError('Original source crown not found in actual incoming native')
    original_cage = cage_snapshot(old)
    original_graphs = {m.name: digest_json(graph_snapshot(m)) for m in bpy.data.materials}
    original_images = {im.name: sha_bytes(im.packed_file.data) for im in bpy.data.images if im.packed_file}
    bpy.ops.wm.open_mainfile(filepath=str(native), load_ui=False, use_scripts=False)
    old = bpy.data.objects.get(SOURCE)
    obj = bpy.data.objects.get(SUCCESSOR)
    if old is None or obj is None: raise ValueError('Saved retired crown or successor not found')
    expected_mat_name = module['materials'][0]
    material = bpy.data.materials.get(expected_mat_name)
    predicates.update(successor_is_mesh=obj.type == 'MESH', successor_visible=not obj.hide_render and not obj.hide_get() and not obj.hide_viewport,
                      original_crown_retired=old.hide_render and old.hide_get(),
                      source_crown_cage_held=digest_json(cage_snapshot(old)) == digest_json(original_cage),
                      successor_cage_equals_retired_source=digest_json(cage_snapshot(obj)) == digest_json(cage_snapshot(old)),
                      active_uv_selected=obj.data.uv_layers.active is not None and obj.data.uv_layers.active.name == UV_NAME,
                      object_slot2_DATA=obj.material_slots[2].link == 'DATA',
                      data_slot2_original_material_identity=identity(obj.data.materials[2], material),
                      original_material_graphs_held=all(bpy.data.materials.get(name) is not None and digest_json(graph_snapshot(bpy.data.materials[name])) == h for name,h in original_graphs.items()),
                      original_packed_image_bytes_held=all(bpy.data.images.get(name) is not None and bpy.data.images[name].packed_file is not None and sha_bytes(bpy.data.images[name].packed_file.data) == h for name,h in original_images.items()))
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    emat = evaluated.data.materials[2]
    eimage_graph = prove_graph(emat, expected, predicates)
    predicates.update(evaluated_faces_1912=len(evaluated.data.polygons) == 1912,
                      evaluated_all_faces_slot2=all(p.material_index == 2 for p in evaluated.data.polygons),
                      evaluated_slot2_DATA=evaluated.material_slots[2].link == 'DATA',
                      evaluated_slot2_original_material_identity=identity(emat, material),
                      evaluated_active_uv_selected=evaluated.data.uv_layers.active is not None and evaluated.data.uv_layers.active.name == UV_NAME)
    for role,record in expected.items():
        predicates[role+'_separate_FILE_image_datablock'] = bpy.data.images[record['name']].source == 'FILE'
    if 'original' in expected['normal'].get('byte_source', ''):
        # Discover the retired source normal image through its live graph, not its node name.
        oldmat = old.data.materials[2]
        outnodes = [n for n in oldmat.node_tree.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output]
        oldbsdf, _ = incoming(outnodes[0], 'Surface')
        pending = [l.from_node for l in oldbsdf.inputs['Normal'].links]
        visited = set(); normal_source_images = []
        while pending:
            n = pending.pop()
            if n.as_pointer() in visited: continue
            visited.add(n.as_pointer())
            if n.type == 'TEX_IMAGE' and n.image:
                normal_source_images.append(original(n.image))
            pending.extend(l.from_node for sock in n.inputs for l in sock.links)
        new_normal = bpy.data.images[expected['normal']['name']]
        predicates['normal_copy_has_original_source_graph_packed_bytes'] = any(im.packed_file and sha_bytes(im.packed_file.data) == expected['normal']['sha256'] for im in normal_source_images)
        predicates['normal_copy_is_distinct_original_ID_from_source_graph_images'] = bool(normal_source_images) and all(not identity(new_normal, im) for im in normal_source_images)
        eimage_graph['original_source_normal_graph_images'] = [{'name':im.name,'original_pointer':im.as_pointer(),'packed_sha256':sha_bytes(im.packed_file.data) if im.packed_file else None} for im in normal_source_images]
    for role,record in expected.items():
        predicates[role+'_actual_external_map_bytes_match_record'] = before_map_sha[role] == record['sha256']
        predicates[role+'_external_map_bytes_held'] = sha_file(map_paths[role]) == before_map_sha[role]
    predicates['candidate_native_bytes_held'] = sha_file(native) == initial_native_sha
    predicates['source_native_bytes_held'] = sha_file(source) == initial_source_sha
    return {'era': era, 'status': 'PASS' if all(predicates.values()) else 'FAIL', 'native': str(native),
            'native_sha256': initial_native_sha, 'source_native': str(source), 'source_native_sha256': initial_source_sha,
            'evaluated_faces': len(evaluated.data.polygons),
            'evaluated_face_material_indices': sorted({p.material_index for p in evaluated.data.polygons}),
            'material_identity': {'expected_original_pointer': material.as_pointer() if material else None,
                                  'evaluated_original_pointer': original(emat).as_pointer() if emat else None,
                                  'pointer_scope': 'Same saved-native Blender session only'},
            'source_cage_sha256': digest_json(original_cage),
            'original_material_graph_count': len(original_graphs), 'original_packed_image_count': len(original_images),
            'graph': eimage_graph, 'predicates': predicates}


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--packet',default='assets/audit/cg-recursive-finish04-crown/attempt03')
    p.add_argument('--manifest',default='assets/audit/cg-recursive-finish04-crown/attempt03-frozen-manifest.json')
    p.add_argument('--output',default='/tmp/cg-finish04-saved-binding-check.json')
    p.add_argument('--eras', nargs='+', choices=['builder','maker','mechanic'],default=['builder','maker','mechanic'])
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    packet=ROOT/args.packet;manifest=json.loads((ROOT/args.manifest).read_text())
    result={'schema_version':1,'scope':'Independent saved-native binding test only; source likeness unknown',
            'goal_commit_read':'251f2f0243181e97140179c2aff6eb057e165438',
            'no_scene_writes_or_producer_imports':True,'disabled_autoexec_requested':True,
            'blender_version':bpy.app.version_string,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'eras':[]}
    for era in args.eras:
        try: row=run(era,packet,manifest)
        except Exception as e: row={'era':era,'status':'ERROR','error':str(e),'traceback':traceback.format_exc()}
        result['eras'].append(row)
        print(json.dumps({'era':era,'status':row['status'],'predicates':row.get('predicates'),'error':row.get('error')},sort_keys=True),flush=True)
    result['status']='PASS' if all(r['status']=='PASS' for r in result['eras']) else 'FAIL'
    result['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    print('SAVED_BINDING_RESULT '+json.dumps({'status':result['status'],'output':args.output}),flush=True)
