"""Compare the evaluated native rest geometry with the normals in the actual GLB.

blender -b delivery/frozen/first-choice.blend --python-exit-code 1 \
  -P closeout/normals/check_normals.py -- delivery/frozen/first-choice.glb closeout/normals/result.json
"""
import hashlib
import json
import struct
import sys
from collections import defaultdict
from pathlib import Path

import bpy
import numpy as np
from mathutils import Quaternion
from mathutils.kdtree import KDTree

NORMAL_LIMIT = 2e-5
POSITION_WINDOW = 2e-6
NATIVE_HASHES = {
    '1e59785a11aadf491714ef1b5aa682ff1b9efa0a6a3b421414f3bb7de053a05b',  # Original authoring scene
    '019949c70a8aaff3314244b5fc222d9332dcaf23a24ff208576d52791395ae95',  # Published scene, packed paths normalized
}
GLB_SHA = '88ff5f671a7359c04177b77c3dc01630491189f58d24e6bc0d85d7ed98ccd12e'
TO_GLTF = np.array([[1., 0, 0], [0, 0, 1], [0, -1, 0]])
PERMS = np.array([[0, 1, 2], [1, 2, 0], [2, 0, 1]])


def unit(array):
    lengths = np.linalg.norm(array, axis=-1, keepdims=True)
    assert np.isfinite(lengths).all() and np.min(lengths) > 0
    return array / lengths


def column(collection, attribute, count, dtype):
    out = np.empty(len(collection) * count, dtype=dtype)
    collection.foreach_get(attribute, out)
    return out.reshape(-1, count) if count > 1 else out


def mesh_groups():
    groups = defaultdict(list)
    object_names = []
    scene = bpy.context.scene
    scene.frame_set(0)
    deps = bpy.context.evaluated_depsgraph_get()
    for ob in sorted(scene.objects, key=lambda item: item.name):
        if ob.type != 'MESH' or not ob.parent or 'fc_region' not in ob.parent:
            continue
        region = ob.get('first_choice_region') or ob.get('cg1cRegion') or ob.get('fc_region') or 'assembly'
        if ob.get('fc_rigid') == 'fixed' and region == 'fixed':
            region = 'foot'
        parent = ob.parent['fc_region']
        geometry = ob.evaluated_get(deps)
        mesh = geometry.to_mesh(preserve_all_data_layers=True, depsgraph=deps)
        mesh.calc_loop_triangles()
        points = column(mesh.vertices, 'co', 3, np.float32)
        corners = column(mesh.loops, 'vertex_index', 1, np.int32)
        normals = column(mesh.corner_normals, 'vector', 3, np.float32)
        assert len(normals) == len(corners)
        tri = column(mesh.loop_triangles, 'loops', 3, np.int32)
        polys = column(mesh.loop_triangles, 'polygon_index', 1, np.int32)
        slots = column(mesh.polygons, 'material_index', 1, np.int32)[polys]
        world = np.array(geometry.matrix_world)
        transform = TO_GLTF @ world[:3, :3]
        assert np.linalg.det(transform) > 0, ob.name
        points = points @ transform.T + TO_GLTF @ world[:3, 3]
        normals = unit(normals @ np.linalg.inv(transform))
        # A single source vertex can have multiple corner (split) normals.
        lo = np.full((len(points), 3), np.inf)
        hi = -lo.copy()
        np.minimum.at(lo, corners, normals)
        np.maximum.at(hi, corners, normals)
        split = np.any(hi - lo > 1e-7, axis=1)
        # Detect any distinct normals above a tiny numerical floor. This descriptive
        # classification is independent of the historical parity threshold.
        index = len(object_names)
        object_names.append(ob.name)
        for slot in np.unique(slots):
            selection = (slots == slot)
            subset = tri[selection]
            vertices = corners[subset]
            material = mesh.materials[int(slot)].name
            groups[(parent, str(region).lower(), material)].append((
                points[vertices], normals[subset], split[vertices],
                np.full(len(subset), index, dtype=np.int32)))
        geometry.to_mesh_clear()
    return groups, object_names


def gltf_groups(path, transforms=None):
    content = path.read_bytes()
    magic, version, length = struct.unpack_from('<4sII', content)
    assert magic == b'glTF' and version == 2 and length == len(content)
    size, kind = struct.unpack_from('<I4s', content, 12)
    assert kind == b'JSON'
    data = json.loads(content[20:20+size])
    start = 20 + size
    nbytes, typ = struct.unpack_from('<I4s', content, start)
    assert typ == b'BIN\0'
    blob = memoryview(content)[start+8:start+8+nbytes]

    def accessor(index):
        a = data['accessors'][index]
        bv = data['bufferViews'][a['bufferView']]
        assert not a.get('normalized') and 'sparse' not in a
        dtype = np.dtype({5126:'<f4', 5123:'<u2', 5125:'<u4', 5121:'u1'}[a['componentType']])
        width = {'VEC3':3, 'SCALAR':1}[a['type']]
        return np.ndarray((a['count'], width), dtype, buffer=blob,
                          offset=bv.get('byteOffset',0)+a.get('byteOffset',0),
                          strides=(bv.get('byteStride',width*dtype.itemsize),dtype.itemsize))

    groups = {}
    def visit(index, parent, pivot):
        node = data['nodes'][index]
        assert 'matrix' not in node
        world = np.eye(4)
        x,y,z,w = node.get('rotation',[0,0,0,1])
        rotation = np.array(Quaternion((w,x,y,z)).normalized().to_matrix())
        world[:3,:3] = rotation @ np.diag(node.get('scale',[1,1,1]))
        world[:3,3] = node.get('translation',[0,0,0])
        world = parent @ world
        pivot = node.get('extras',{}).get('fc_region',pivot)
        for child in node.get('children',[]):
            visit(child, world, pivot)
        if 'mesh' not in node:
            return
        for primitive in data['meshes'][node['mesh']]['primitives']:
            assert primitive.get('mode', 4) == 4
            attr = primitive['attributes']
            points = accessor(attr['POSITION']) @ world[:3,:3].T + world[:3,3]
            norm = unit(accessor(attr['NORMAL']) @ np.linalg.inv(world[:3,:3]))
            idx = accessor(primitive['indices']).reshape(-1,3)
            name = data['materials'][primitive['material']]['name']
            key = (pivot, node['extras']['region'], name)
            assert key not in groups
            assert np.linalg.det(world[:3,:3]) > 0
            if transforms is not None:
                transforms[key] = (world[:3,:3], primitive)
            groups[key] = (points[idx],norm[idx])
    for root in data['scenes'][data['scene']]['nodes']:
        visit(root, np.eye(4), None)
    return groups


def associate(pos, exp_pos):
    centres = pos.mean(axis=1)
    tree = KDTree(len(centres))
    for i, centre in enumerate(centres):
        tree.insert(centre,i)
    tree.balance()
    # Use position only for correspondence. No normal is consulted to match corners.
    ce = exp_pos.mean(axis=1)
    matches = [tree.find_range(c, POSITION_WINDOW) for c in ce]
    pairs = [(i, r[1]) for i, hits in enumerate(matches) for r in hits]
    if not pairs:
        raise ValueError('Unresolved entire material/pivot group')
    indices = np.array(pairs)
    good = []
    for start in range(0, len(pairs), 20000):
        ei, ni = indices[start:start+20000].T
        shortest = np.full(len(ni), np.inf)
        order = np.full(len(ni), -1)
        for pi, perm in enumerate(PERMS):
            distance = np.linalg.norm(exp_pos[ei] - pos[ni][:,perm,:], axis=2).max(axis=1)
            better = distance < shortest
            shortest[better] = distance[better]
            order[better] = pi
        within = shortest <= POSITION_WINDOW
        good.extend(zip(ei[within], ni[within], order[within], shortest[within]))
    # Require a bijective geometric match. Distinct overlapping native surfaces
    # are never resolved by choosing whichever normal gives the best answer.
    valid = np.array(good, dtype=np.float64).reshape(-1,4)
    ei, ni, perm = valid[:,:3].T.astype(np.int64)
    edegree = np.bincount(ei, minlength=len(exp_pos))
    ndegree = np.bincount(ni, minlength=len(pos))
    unique = (edegree[ei] == 1) & (ndegree[ni] == 1)
    ei, ni, perm = ei[unique], ni[unique], perm[unique]
    return ei, ni, perm, edegree, ndegree, valid[unique,3]


def compare(source, exported, names):
    pos, normal, split, objects = (np.concatenate(arrays) for arrays in zip(*source))
    exp_pos, exp_norm = exported
    ei, ni, perm, edegree, ndegree, position_error = associate(pos, exp_pos)
    n = normal[ni[:,None], PERMS[perm]]
    e = exp_norm[ei]
    err = np.linalg.norm(e - n, axis=2)
    fails = err > NORMAL_LIMIT
    sharp = split[ni[:,None], PERMS[perm]]
    result = dict(native_triangles=len(pos), glb_triangles=len(exp_pos),
        matched_triangles=len(ni), native_without_triangle_match=int(sum(ndegree==0)),
        glb_without_triangle_match=int(sum(edegree==0)),
        ambiguous_glb_triangles=int(sum(edegree!=0)-len(ei)), compared_corners=int(err.size),
        failed_corners=int(fails.sum()), failed_triangles=int(fails.any(axis=1).sum()),
        source_split_corners=int(sharp.sum()), failures_at_split_vertices=int((sharp & fails).sum()),
        failures_at_single_normal_vertices=int((~sharp & fails).sum()))
    if err.size:
        t, c = np.unravel_index(err.argmax(),err.shape)
        result.update(max_position_error=float(position_error.max()), max_normal_l2=float(err.max()),
            max_angle_degrees=float(np.degrees(2*np.arcsin(np.clip(err.max()/2,0,1)))),
            worst_native_object=names[objects[ni[t]]],worst_glb_triangle=int(ei[t]),
            worst_glb_corner=int(c),worst_position_gltf=exp_pos[ei[t],c].tolist(),
            worst_native_normal=n[t,c].tolist(),worst_export_normal=e[t,c].tolist(),
            worst_on_split_vertex=bool(sharp[t,c]))
    return result


if __name__ == "__main__":
    native = Path(bpy.data.filepath)
    args = sys.argv[sys.argv.index('--')+1:]
    glb, output = map(Path,args[:2])
    expected_glb_sha = args[2] if len(args) == 3 else GLB_SHA
    def sha(path):
        with path.open('rb') as file:
            return hashlib.file_digest(file,'sha256').hexdigest()
    native_hash = sha(native)
    assert native_hash in NATIVE_HASHES and sha(glb)==expected_glb_sha
    src, names = mesh_groups()
    dest = gltf_groups(glb)
    assert set(src)==set(dest), (set(src)-set(dest), set(dest)-set(src))
    rows = []
    for group in sorted(src):
        result = compare(src.pop(group), dest.pop(group), names)
        rows.append(dict(pivot=group[0],region=group[1],material=group[2],**result))
    totals = {key:sum(r[key] for r in rows) for key in rows[0] if key in [
        'native_triangles','glb_triangles','matched_triangles','native_without_triangle_match',
        'glb_without_triangle_match','ambiguous_glb_triangles','compared_corners','failed_corners',
        'failed_triangles','source_split_corners','failures_at_split_vertices','failures_at_single_normal_vertices']}
    worst = max(rows,key=lambda row:row.get('max_normal_l2',0))
    verdict = ('FAIL' if totals['failed_corners'] else
               'INCOMPLETE' if totals['matched_triangles']!=max(totals['glb_triangles'],totals['native_triangles']) else 'PASS')
    report = dict(verdict=verdict, blender=bpy.app.version_string,native_sha256=native_hash,
                  glb_sha256=expected_glb_sha, evaluated_objects=len(names), material_pivot_groups=len(rows),
                  world_frame='rest, frame 0, glTF Y-up', normal_l2_limit=NORMAL_LIMIT,
                  position_window_world_units=POSITION_WINDOW, totals=totals,worst=worst,groups=rows)
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(verdict,totals,worst,flush=True)
