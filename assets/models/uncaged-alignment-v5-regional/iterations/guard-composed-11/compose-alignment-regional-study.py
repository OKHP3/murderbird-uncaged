"""Compose selected regional study meshes and produce a batched GLB derivative.

The native composition is saved before any mesh conversion or object joining.
The export-only batching is adapted from the V5 generator's owner/era/region/
surface-role grouping. The resulting geometry remains a proposal, not metrology.
"""

import argparse
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Matrix, Quaternion, Vector
from mathutils.kdtree import KDTree


ROOT = Path(__file__).resolve().parents[1]
BASE_DIR = ROOT / '.local/alignment-composed-study/inputs/v5-sixth-1e7febcc03d9'
GUARD_DIR = ROOT / '.local/alignment-limb-study/v5-fourth-limb-profile-study-05'
C8_DIR = Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/uncaged-alignment-v5/iterations/c8a7a7e14253')
QA_ROOT = Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
EXPECTED_BASE_BLEND_SHA = 'fd5c8a21e8e7808fa94c9baa3499574bac3d0c1ed5a44573637286c359cea0e4'
EXPECTED_BASE_GLB_SHA = '1e7febcc03d9f8d1a644580c8422b124403cf4e5768aa01df747e3d9b6af9f1e'
EXPECTED_C8_BLEND_SHA = 'cc6bfafc9ab044bba1abcbec86761afb9ef67ee60e252ec7ee838948ea7dfd04'
EXPECTED_C8_GLB_SHA = 'c8a7a7e14253075414d8e55390ebad2bf605ad09962fa62769417834000ccaa3'
EXPECTED_C8_INVENTORY_SHA = '5fda3638038b0a5d4c040544a2b419962cd33c55c9a3f0edc416aef4c18b7ee0'
ALL_ERAS = 'maker,mechanic,builder'
WORLD_VERTEX_TOLERANCE = 1e-5
PIVOT_MATRIX_TOLERANCE = 1e-8


def options():
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / '.local/alignment-composed-study/guard-only-06')
    parser.add_argument('--base-blend', type=Path, default=BASE_DIR / 'murderbird-alignment-v5.blend')
    parser.add_argument('--base-glb', type=Path, default=BASE_DIR / 'murderbird-alignment-v5.glb')
    parser.add_argument('--base-manifest', type=Path, default=BASE_DIR / 'alignment-inventory.json')
    parser.add_argument('--guard-blend', type=Path, default=GUARD_DIR / 'murderbird-limb-profile-study.blend')
    parser.add_argument('--guard-glb', type=Path, default=GUARD_DIR / 'murderbird-limb-profile-study.glb')
    parser.add_argument('--guard-manifest', type=Path, default=GUARD_DIR / 'manifest.json')
    parser.add_argument('--c8-blend', type=Path, default=C8_DIR / 'murderbird-alignment-v5.blend')
    parser.add_argument('--c8-glb', type=Path, default=C8_DIR / 'murderbird-alignment-v5.glb')
    parser.add_argument('--c8-manifest', type=Path, default=C8_DIR / 'alignment-inventory.json')
    parser.add_argument('--talon-blend', type=Path, default=None,
                        help='Reserved for a later reviewed six-talon native source; not yet composed.')
    return parser.parse_args(args)


OPT = options()
BASE_BLEND = OPT.base_blend.expanduser().resolve()
BASE_GLB = OPT.base_glb.expanduser().resolve()
BASE_MANIFEST = OPT.base_manifest.expanduser().resolve()
GUARD_BLEND = OPT.guard_blend.expanduser().resolve()
GUARD_GLB = OPT.guard_glb.expanduser().resolve()
GUARD_MANIFEST = OPT.guard_manifest.expanduser().resolve()
C8_BLEND = OPT.c8_blend.expanduser().resolve()
C8_GLB = OPT.c8_glb.expanduser().resolve()
C8_MANIFEST = OPT.c8_manifest.expanduser().resolve()
OUT_DIR = OPT.out.expanduser().resolve()
OUT_BLEND = OUT_DIR / 'murderbird-v5-sixth-guard-study.blend'
OUT_GLB = OUT_DIR / 'murderbird-v5-sixth-guard-study.glb'
OUT_MANIFEST = OUT_DIR / 'manifest.json'
OUT_SCRIPT = OUT_DIR / 'compose-alignment-regional-study.py'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def record(path):
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha256(path)}


def copy_verified(source, destination, expected_sha=None):
    require(source.is_file(), f'Missing source file: {source}')
    source_sha = sha256(source)
    if expected_sha is not None:
        require(source_sha == expected_sha, f'Source SHA mismatch: {source}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    require(not destination.exists(), f'Refusing to replace snapshot: {destination}')
    shutil.copy2(source, destination)
    require(sha256(destination) == source_sha, f'Snapshot copy SHA mismatch: {destination}')
    return record(destination)


def json_file(path):
    return json.loads(path.read_text())


def matrix_json(matrix):
    return [[round(float(matrix[r][c]), 12) for c in range(4)] for r in range(4)]


def matrix_error(a, b):
    return max(abs(float(a[r][c]) - float(b[r][c]))
               for r in range(4) for c in range(4))


def mesh_digest(obj):
    payload = (
        tuple(tuple(round(float(c), 9) for c in v.co) for v in obj.data.vertices),
        tuple(tuple(poly.vertices) for poly in obj.data.polygons),
    )
    return hashlib.sha256(repr(payload).encode()).hexdigest()


LIMB_OWNERS = {f'{side}-{part}' for side in ('left', 'right')
               for part in ('thigh', 'shin', 'foot', 'toes')}
LIMB_OWNERS |= {f'{side}-digit-{digit}-{joint}' for side in ('left', 'right')
                for digit in (1, 2, 3) for joint in ('proximal', 'distal')}


def limb_snapshot(path, replaced_names):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    empties = {o.name: {'parent': o.parent.name if o.parent else None,
                        'matrixWorld': matrix_json(o.matrix_world)}
               for o in bpy.data.objects if o.type == 'EMPTY' and o.name in LIMB_OWNERS}
    meshes = {}
    targets = {}
    for obj in bpy.data.objects:
        if obj.type != 'MESH' or not obj.parent or obj.parent.name not in LIMB_OWNERS:
            continue
        info = {'parent': obj.parent.name, 'digest': mesh_digest(obj),
                'region': obj.get('region'), 'surfaceRole': obj.get('surfaceRole'),
                'materials': [m.name if m else None for m in obj.data.materials],
                'matrixWorld': matrix_json(obj.matrix_world)}
        if obj.name in replaced_names:
            targets[obj.name] = info
        else:
            meshes[obj.name] = info
    return {'empties': empties, 'unreplacedMeshes': meshes, 'replacementMeshes': targets}


def whole_scene_snapshot():
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    empties = {o.name: matrix_json(o.matrix_world) for o in bpy.data.objects if o.type == 'EMPTY'}
    meshes = {}
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        meshes[obj.name] = {
            'parent': obj.parent.name if obj.parent else None,
            'matrixWorld': matrix_json(obj.matrix_world),
            'digest': mesh_digest(obj),
            'props': {key: str(obj.get(key)) for key in
                      ('exteriorEras', 'region', 'surfaceRole', 'constructionClass') if key in obj},
            'materials': [mat.name if mat else None for mat in obj.data.materials],
        }
    materials = sorted(mat.name for mat in bpy.data.materials)
    return {'empties': empties, 'meshes': meshes, 'materials': materials}


def compare_limb_snapshots(source_c8, target_base, replaced_names):
    for field in ('empties', 'unreplacedMeshes', 'replacementMeshes'):
        left, right = source_c8[field], target_base[field]
        require(set(left) == set(right), f'c8/base6 limb {field} names differ')
        for name in left:
            require(left[name] == right[name], f'c8/base6 limb mismatch in {field}: {name}')
    require(len(source_c8['empties']) == len(LIMB_OWNERS), 'Incomplete limb/digit pivot coverage')
    require(set(source_c8['replacementMeshes']) == set(replaced_names),
            'c8 source does not contain the exact 26 replacement surfaces')
    require(len(source_c8['unreplacedMeshes']) == 148,
            'Unexpected count of retained original limb-owned meshes')
    return {'limbDigitPivotCount': len(source_c8['empties']),
            'pivotWorldMatrixMaxDelta': 0.0,
            'untouchedLimbMeshCount': len(source_c8['unreplacedMeshes']),
            'untouchedLimbMeshComparisons': 'names, direct owner, region, role, materials, local mesh vertices/faces and world matrix exactly match c8 at 9-decimal coordinate serialization',
            'replacementSurfaceCount': len(source_c8['replacementMeshes']),
            'replacementSurfaceComparisons': 'all 26 names, owners, mesh vertices/faces, tags, materials and world matrices match c8'}


def evaluated_mesh_data(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    return evaluated, mesh


def triangle_count(mesh):
    return sum(max(0, len(poly.vertices) - 2) for poly in mesh.polygons)


def material_face_counts(obj, mesh):
    names = []
    for mat in mesh.materials:
        names.append(mat.name if mat else '__none__')
    counts = {}
    for poly in mesh.polygons:
        idx = poly.material_index
        name = names[idx] if idx < len(names) else '__none__'
        counts[name] = counts.get(name, 0) + 1
    return dict(sorted(counts.items()))


def material_triangle_counts(obj, mesh):
    names = [mat.name if mat else '__none__' for mat in mesh.materials]
    counts = {}
    for poly in mesh.polygons:
        idx = poly.material_index
        name = names[idx] if idx < len(names) else '__none__'
        counts[name] = counts.get(name, 0) + max(0, len(poly.vertices) - 2)
    return dict(sorted(counts.items()))


def mesh_metrics(objects):
    vertices = []
    minv = [math.inf, math.inf, math.inf]
    maxv = [-math.inf, -math.inf, -math.inf]
    triangles = polygons = 0
    materials = {}
    material_triangles = {}
    for obj in objects:
        mesh = obj.data
        world = obj.matrix_world
        for vert in mesh.vertices:
            p = world @ vert.co
            xyz = tuple(float(c) for c in p)
            vertices.append(xyz)
            for i in range(3):
                minv[i] = min(minv[i], xyz[i])
                maxv[i] = max(maxv[i], xyz[i])
        triangles += triangle_count(mesh)
        polygons += len(mesh.polygons)
        for name, count in material_face_counts(obj, mesh).items():
            materials[name] = materials.get(name, 0) + count
        for name, count in material_triangle_counts(obj, mesh).items():
            material_triangles[name] = material_triangles.get(name, 0) + count
    return {'vertexCount': len(vertices), 'polygonCount': polygons,
            'triangleCount': triangles, 'worldBounds': {'min': minv, 'max': maxv},
            'materialFaceCounts': dict(sorted(materials.items())),
            'materialTriangleCounts': dict(sorted(material_triangles.items())),
            'worldVertices': vertices}


def mesh_metrics_from_data(mesh, world):
    vertices = []
    minv = [math.inf, math.inf, math.inf]
    maxv = [-math.inf, -math.inf, -math.inf]
    for vert in mesh.vertices:
        xyz = tuple(float(c) for c in world @ vert.co)
        vertices.append(xyz)
        for i in range(3):
            minv[i] = min(minv[i], xyz[i])
            maxv[i] = max(maxv[i], xyz[i])
    names = [mat.name if mat else '__none__' for mat in mesh.materials]
    face_counts = {}
    triangle_counts = {}
    for poly in mesh.polygons:
        name = names[poly.material_index] if poly.material_index < len(names) else '__none__'
        face_counts[name] = face_counts.get(name, 0) + 1
        triangle_counts[name] = triangle_counts.get(name, 0) + max(0, len(poly.vertices) - 2)
    return {'vertexCount': len(vertices), 'polygonCount': len(mesh.polygons),
            'triangleCount': triangle_count(mesh), 'worldBounds': {'min': minv, 'max': maxv},
            'materialFaceCounts': dict(sorted(face_counts.items())),
            'materialTriangleCounts': dict(sorted(triangle_counts.items())),
            'worldVertices': vertices}


def bounds_error(a, b):
    return max(abs(a['min'][i] - b['min'][i]) for i in range(3)) + max(
        abs(a['max'][i] - b['max'][i]) for i in range(3))


def cloud_error(points_a, points_b, allow_different_counts=False):
    if not allow_different_counts:
        require(len(points_a) == len(points_b), 'Batched vertex count changed')
    if not points_a:
        return 0.0
    tree_b = KDTree(len(points_b))
    for idx, point in enumerate(points_b):
        tree_b.insert(Vector(point), idx)
    tree_b.balance()
    max_ab = max(tree_b.find(Vector(point))[2] for point in points_a)
    tree_a = KDTree(len(points_a))
    for idx, point in enumerate(points_a):
        tree_a.insert(Vector(point), idx)
    tree_a.balance()
    max_ba = max(tree_a.find(Vector(point))[2] for point in points_b)
    return max(max_ab, max_ba)


def batch_key(parent_name, eras, region, role):
    return json.dumps([parent_name, eras, region, role], separators=(',', ':'))


def read_glb_json(path):
    import struct
    data = path.read_bytes()
    require(data[:4] == b'glTF', 'Exported model is not a GLB')
    length, kind = struct.unpack_from('<I4s', data, 12)
    require(kind == b'JSON', 'GLB first chunk is not JSON')
    return json.loads(data[20:20 + length].decode('utf-8').rstrip(' \0'))


def read_glb_document(path):
    import struct
    data = path.read_bytes()
    require(data[:4] == b'glTF', 'Exported model is not a GLB')
    json_length, json_kind = struct.unpack_from('<I4s', data, 12)
    require(json_kind == b'JSON', 'GLB first chunk is not JSON')
    doc = json.loads(data[20:20 + json_length].decode('utf-8').rstrip(' \0'))
    bin_header = 20 + json_length
    bin_length, bin_kind = struct.unpack_from('<I4s', data, bin_header)
    require(bin_kind == b'BIN\0', 'GLB second chunk is not binary')
    return doc, data[bin_header + 8:bin_header + 8 + bin_length]


def gltf_node_world_matrices(doc):
    parents = {}
    for parent_index, node in enumerate(doc.get('nodes', [])):
        for child_index in node.get('children', []):
            require(child_index not in parents, 'GLTF node has multiple parents')
            parents[child_index] = parent_index
    cache = {}

    def local_matrix(node):
        if 'matrix' in node:
            values = node['matrix']
            return Matrix([[values[col * 4 + row] for col in range(4)] for row in range(4)])
        translation = Vector(node.get('translation', (0, 0, 0)))
        rotation = node.get('rotation', (0, 0, 0, 1))
        quat = Quaternion((rotation[3], rotation[0], rotation[1], rotation[2]))
        scale = node.get('scale', (1, 1, 1))
        return Matrix.Translation(translation) @ quat.to_matrix().to_4x4() @ Matrix.Diagonal(Vector((scale[0], scale[1], scale[2], 1)))

    def world(index):
        if index not in cache:
            local = local_matrix(doc['nodes'][index])
            cache[index] = world(parents[index]) @ local if index in parents else local
        return cache[index]

    return cache, world


def glb_mesh_world_metrics(path, node_index, matrices, world_for_node):
    import struct
    doc, binary = read_glb_document(path)
    node = doc['nodes'][node_index]
    mesh = doc['meshes'][node['mesh']]
    world = world_for_node(node_index)
    points = []
    triangles = 0
    materials = {}
    for primitive in mesh.get('primitives', []):
        accessor_index = primitive['attributes']['POSITION']
        accessor = doc['accessors'][accessor_index]
        require(accessor['componentType'] == 5126 and accessor['type'] == 'VEC3',
                f'Unsupported GLB POSITION accessor: {node.get("name")}')
        view = doc['bufferViews'][accessor['bufferView']]
        offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
        stride = view.get('byteStride', 12)
        for i in range(accessor['count']):
            p = struct.unpack_from('<3f', binary, offset + i * stride)
            points.append(tuple(float(c) for c in world @ Vector(p)))
        index_count = doc['accessors'][primitive['indices']]['count'] if 'indices' in primitive else accessor['count']
        triangles += index_count // 3
        mat_name = doc['materials'][primitive['material']].get('name', '__unnamed__') if 'material' in primitive else '__none__'
        materials[mat_name] = materials.get(mat_name, 0) + index_count // 3
    return {'worldVertices': points, 'triangleCount': triangles,
            'materialTriangleCounts': dict(sorted(materials.items()))}


def blender_to_gltf_points(points):
    return [(x, z, -y) for x, y, z in points]


def make_mesh_signatures(path, guard_manifest, base_manifest, c8_manifest):
    require(sha256(BASE_BLEND) == EXPECTED_BASE_BLEND_SHA, 'Frozen V5 sixth native SHA mismatch')
    require(sha256(BASE_GLB) == EXPECTED_BASE_GLB_SHA, 'Frozen V5 sixth GLB SHA mismatch')
    require(sha256(C8_BLEND) == EXPECTED_C8_BLEND_SHA, 'Frozen c8 native SHA mismatch')
    require(sha256(C8_GLB) == EXPECTED_C8_GLB_SHA, 'Frozen c8 GLB SHA mismatch')
    require(sha256(C8_MANIFEST) == EXPECTED_C8_INVENTORY_SHA, 'Frozen c8 inventory SHA mismatch')
    guard_output_blend = guard_manifest['outputs']['blend']
    guard_output_glb = guard_manifest['outputs']['glb']
    require(sha256(GUARD_BLEND) == guard_output_blend['sha256'], 'Guard-study05 native SHA differs from its manifest')
    require(sha256(GUARD_GLB) == guard_output_glb['sha256'], 'Guard-study05 GLB SHA differs from its manifest')
    for manifest, expected_glb, expected_blend in (
        (base_manifest, EXPECTED_BASE_GLB_SHA, EXPECTED_BASE_BLEND_SHA),
        (c8_manifest, EXPECTED_C8_GLB_SHA, EXPECTED_C8_BLEND_SHA),
    ):
        generated = {item['path'].rsplit('/', 1)[-1]: item for item in manifest['generatedFiles']}
        require(generated['murderbird-alignment-v5.blend']['sha256'] == expected_blend,
                'Inventory does not bind the expected native input')
        require(generated['murderbird-alignment-v5.glb']['sha256'] == expected_glb,
                'Inventory does not bind the expected GLB input')


require(OPT.talon_blend is None,
        '--talon-blend composition is not enabled until its exact manifest and replacement contract are verified')
require(not OUT_DIR.exists(), f'Refusing to replace existing output folder: {OUT_DIR}')
for source in (BASE_BLEND, BASE_GLB, BASE_MANIFEST, GUARD_BLEND, GUARD_GLB,
               GUARD_MANIFEST, C8_BLEND, C8_GLB, C8_MANIFEST):
    require(source.is_file(), f'Missing composition input: {source}')

base_manifest = json_file(BASE_MANIFEST)
guard_manifest = json_file(GUARD_MANIFEST)
c8_manifest = json_file(C8_MANIFEST)
make_mesh_signatures(OUT_DIR, guard_manifest, base_manifest, c8_manifest)
replaced_names = set(guard_manifest['replacedObjects'])
guard_records = guard_manifest['newObjects']
require(len(replaced_names) == 26 and len(guard_records) == 10,
        'Guard-study05 manifest has unexpected replacement/addition counts')
guard_names = [item['name'] for item in guard_records]
require(len(set(guard_names)) == 10, 'Guard object names are not unique')

# The intended output base claims no limb revision; prove it against c8 before
# copying or modifying the frozen V5 sixth source.
c8_limb = limb_snapshot(C8_BLEND, replaced_names)
base_limb = limb_snapshot(BASE_BLEND, replaced_names)
compatibility = compare_limb_snapshots(c8_limb, base_limb, replaced_names)

# Capture evaluated study geometry while its authored scene is active so the
# modifier stack is fully represented. These records remain the comparison
# oracle after reopening base6 for composition.
bpy.ops.wm.open_mainfile(filepath=str(GUARD_BLEND))
bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()
guard_source_world = {}
source_guard_metrics = {}
source_guard_modifier_records = {}
depsgraph = bpy.context.evaluated_depsgraph_get()
for item in guard_records:
    name = item['name']
    obj = bpy.data.objects.get(name)
    require(obj is not None and obj.type == 'MESH', f'Guard study object missing: {name}')
    guard_source_world[name] = obj.matrix_world.copy()
    evaluated, mesh = evaluated_mesh_data(obj, depsgraph)
    source_guard_metrics[name] = mesh_metrics_from_data(mesh, obj.matrix_world)
    evaluated.to_mesh_clear()
    source_guard_modifier_records[name] = [{'name': mod.name, 'type': mod.type,
                                             'showViewport': mod.show_viewport,
                                             'showRender': mod.show_render}
                                            for mod in obj.modifiers]
    require(source_guard_metrics[name]['triangleCount'] == item['evaluatedTriangles'],
            f'Guard-study05 evaluated triangle count does not match its manifest: {name}')

# Bind every input/script into the new isolated output before composition.
OUT_DIR.mkdir(parents=True, exist_ok=False)
shutil.copy2(Path(__file__).resolve(), OUT_SCRIPT)
snapshot_records = {}
for label, sources in {
    'base-v5-sixth': [(BASE_BLEND, 'murderbird-alignment-v5.blend', EXPECTED_BASE_BLEND_SHA),
                      (BASE_GLB, 'murderbird-alignment-v5.glb', EXPECTED_BASE_GLB_SHA),
                      (BASE_MANIFEST, 'alignment-inventory.json', sha256(BASE_MANIFEST))],
    'guard-study05': [(GUARD_BLEND, 'murderbird-limb-profile-study.blend', guard_manifest['outputs']['blend']['sha256']),
                      (GUARD_GLB, 'murderbird-limb-profile-study.glb', guard_manifest['outputs']['glb']['sha256']),
                      (GUARD_MANIFEST, 'manifest.json', sha256(GUARD_MANIFEST))],
    'c8-limb-compatibility-source': [(C8_BLEND, 'murderbird-alignment-v5.blend', EXPECTED_C8_BLEND_SHA),
                                    (C8_GLB, 'murderbird-alignment-v5.glb', EXPECTED_C8_GLB_SHA),
                                    (C8_MANIFEST, 'alignment-inventory.json', EXPECTED_C8_INVENTORY_SHA)],
}.items():
    for source, name, expected in sources:
        rel = Path('input-snapshots') / label / name
        snapshot_records[str(rel)] = copy_verified(source, OUT_DIR / rel, expected)

source_names = [item['path'].split('/')[-1] for item in base_manifest['generatedFiles']
                if '/generation-source/' in item['path'] and item['path'].endswith('.py')]
require(source_names, 'V5 sixth inventory has no generation-source snapshots')
base_generation_sources = {}
for name in source_names:
    item = next(i for i in base_manifest['generatedFiles'] if i['path'].endswith('/' + name))
    source = QA_ROOT / item['path']
    expected = item['sha256']
    target = OUT_DIR / 'input-snapshots' / 'v5-sixth-generation-source' / name
    base_generation_sources[name] = copy_verified(source, target, expected)
guard_script_source = GUARD_DIR / guard_manifest['generatorScriptSnapshot']['path'].split('/')[-1]
guard_script_record = copy_verified(guard_script_source,
                                    OUT_DIR / 'input-snapshots/guard-study05-generator.py',
                                    guard_manifest['generatorScriptSnapshot']['sha256'])

# Reopen the exact frozen V5 sixth source for composition and retain a complete
# snapshot of every untouched mesh and rig empty for post-compose assertions.
bpy.ops.wm.open_mainfile(filepath=str(BASE_BLEND))
source_scene = whole_scene_snapshot()
require(len(source_scene['empties']) == 51, 'Unexpected V5 sixth empty/pivot count')
base_targets = {name: bpy.data.objects.get(name) for name in replaced_names}
require(all(obj is not None and obj.type == 'MESH' for obj in base_targets.values()),
        'Frozen V5 sixth does not contain every exact guard-study replacement surface')
for name, obj in base_targets.items():
    require(obj.parent and obj.parent.name in LIMB_OWNERS,
            f'Replacement surface has an unexpected owner: {name}')
removed_records = [{'name': name, 'owner': base_targets[name].parent.name,
                    'meshDigest': mesh_digest(base_targets[name])}
                   for name in sorted(replaced_names)]
for name in sorted(replaced_names):
    bpy.data.objects.remove(base_targets[name], do_unlink=True)

# Load only the ten authored guard objects. This preserves their editable
# Solidify/Bevel/WeightedNormal stacks; only their parent pivots are remapped.
# Blender also resolves source parent datablocks, but these are unlinked and
# removed after each guard is attached to the compatible V5 sixth owner.
with bpy.data.libraries.load(str(GUARD_BLEND), link=False) as (data_from, data_to):
    require(set(guard_names).issubset(set(data_from.objects)),
            'Guard-study05 is missing an expected source object')
    # Blender replaces entries in its destination list with loaded datablocks;
    # give it a copy so the manifest's canonical string-name list stays intact.
    data_to.objects = list(guard_names)
loaded_objects = {obj.name: obj for obj in data_to.objects if obj is not None}
require(len(loaded_objects) == 10, 'Could not append all 10 guard source objects')
plate_material = bpy.data.materials.get('Neutral / plate')
require(plate_material is not None, 'V5 sixth base lacks Neutral / plate material')
added_guard_objects = []
guard_control_records = []
for item in guard_records:
    name = item['name']
    owner = bpy.data.objects.get(item['owner'])
    require(owner is not None and owner.type == 'EMPTY', f'Guard owner pivot missing: {item["owner"]}')
    obj = loaded_objects[name]
    require(obj.type == 'MESH', f'Guard source is not a mesh object: {name}')
    source_world = guard_source_world[name]
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = owner
    obj.matrix_world = source_world
    # Keep the established neutral plate role while preserving modifier offsets.
    obj.data.materials.clear()
    obj.data.materials.append(plate_material)
    obj['region'] = item['region']
    obj['surfaceRole'] = 'plate'
    obj['exteriorEras'] = ALL_ERAS
    obj['geometryStatus'] = 'editable regional profile proposal'
    require(obj.parent.name == item['owner'], f'Guard owner changed: {name}')
    require(matrix_error(obj.matrix_world, source_world) <= PIVOT_MATRIX_TOLERANCE,
            f'Source guard world transform changed during owner remap: {name}')
    bpy.context.view_layer.update()
    require(all(math.isfinite(float(c)) for vert in obj.data.vertices for c in vert.co),
            f'Non-finite guard geometry: {name}')
    added_guard_objects.append(obj)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated, evaluated_mesh = evaluated_mesh_data(obj, depsgraph)
    composed_metrics = mesh_metrics_from_data(evaluated_mesh, obj.matrix_world)
    evaluated.to_mesh_clear()
    error = cloud_error(source_guard_metrics[name]['worldVertices'],
                        composed_metrics['worldVertices'], allow_different_counts=True)
    require(error <= WORLD_VERTEX_TOLERANCE,
            f'Composed evaluated guard differs from study05 source: {name}, {error}m')
    require(composed_metrics['triangleCount'] == item['evaluatedTriangles'],
            f'Evaluated triangle count differs from guard-study05 manifest: {name}')
    guard_control_records.append({'name': name, 'owner': item['owner'],
                                  'region': item['region'], 'surfaceRole': 'plate',
                                  'eras': ALL_ERAS, 'meshDigest': mesh_digest(obj),
                                  'vertices': len(obj.data.vertices),
                                  'controlTriangles': triangle_count(obj.data),
                                  'evaluatedTriangles': composed_metrics['triangleCount'],
                                  'sourceEvaluatedTriangles': item['evaluatedTriangles'],
                                  'sourceToCompositionMaxWorldVertexErrorMetres': error,
                                  'materials': [m.name for m in obj.data.materials],
                                  'sourceModifiers': source_guard_modifier_records[name],
                                  'modifiers': [{'name': mod.name, 'type': mod.type}
                                                for mod in obj.modifiers]})

# Remove only the unlinked parent datablocks imported as dependencies with the
# source objects. The composed guards now point at base6 owners.
for imported in list(bpy.data.objects):
    if imported.type == 'EMPTY' and imported.name not in bpy.context.scene.objects and imported.users == 0:
        bpy.data.objects.remove(imported)

composed_scene = whole_scene_snapshot()
require(set(composed_scene['empties']) == set(source_scene['empties']),
        'Rig empty set changed during composition')
composition_pivot_errors = {name: matrix_error(source_scene['empties'][name],
                                               composed_scene['empties'][name])
                            for name in source_scene['empties']}
require(max(composition_pivot_errors.values(), default=0.0) <= PIVOT_MATRIX_TOLERANCE,
        'An empty/pivot moved during composition')
for name, before in source_scene['meshes'].items():
    if name in replaced_names:
        continue
    after = composed_scene['meshes'].get(name)
    require(after == before, f'Untouched base mesh changed: {name}')
require(set(composed_scene['meshes']) ==
        (set(source_scene['meshes']) - replaced_names) | set(guard_names),
        'Unexpected mesh set after guard-only composition: extra=' +
        repr(list(set(composed_scene['meshes']) - ((set(source_scene['meshes']) - replaced_names) | set(guard_names)))) +
        ', missing=' +
        repr(list(((set(source_scene['meshes']) - replaced_names) | set(guard_names)) - set(composed_scene['meshes']))))

# Save the fully editable composition before applying any modifiers or joins.
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND), check_existing=False)
require(OUT_BLEND.is_file(), 'Editable composed native fork was not saved')

# Prepare a throwaway in-memory export copy using the existing V5 normalization:
# convert modifiers, remove only recorded zero-area faces, recalc normals, and
# remove color attributes. Native output above remains unbatched/editable.
depsgraph = bpy.context.evaluated_depsgraph_get()
normalization = []
for obj in list(bpy.context.scene.objects):
    if obj.type != 'MESH':
        continue
    before_triangles = triangle_count(obj.data)
    bpy.ops.object.select_all(action='DESELECT')
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target='MESH')
    obj = bpy.context.object
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bad_faces = [face for face in bm.faces if face.calc_area() < 1e-12]
    bad_triangle_count = sum(max(0, len(face.verts) - 2) for face in bad_faces)
    if bad_faces:
        bmesh.ops.delete(bm, geom=bad_faces, context='FACES_ONLY')
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    for attribute in list(obj.data.color_attributes):
        obj.data.color_attributes.remove(attribute)
    normalization.append({'name': obj.name, 'removedZeroAreaFaces': len(bad_faces),
                          'removedFaceTriangles': bad_triangle_count,
                          'trianglesBeforeConversion': before_triangles,
                          'trianglesAfterNormalization': triangle_count(obj.data)})

pre_batch_pivots = {o.name: matrix_json(o.matrix_world) for o in bpy.data.objects if o.type == 'EMPTY'}
groups = {}
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    parent = obj.parent
    eras = obj.get('exteriorEras', ALL_ERAS)
    region = obj.get('region', 'back')
    role = obj.get('surfaceRole', 'frame')
    require(parent is not None, f'Unowned mesh cannot be batched: {obj.name}')
    key = (parent.name, eras, region, role)
    groups.setdefault(key, []).append(obj)

batch_expectations = {}
for key, objects in groups.items():
    objects.sort(key=lambda obj: obj.name)
    metrics = mesh_metrics(objects)
    batch_expectations[key] = metrics
batch_records = []
joined_objects = []
for key in sorted(groups):
    parent_name, eras, region, role = key
    objects = groups[key]
    names = [obj.name for obj in objects]
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    joined = bpy.context.object
    joined.name = f'{parent_name}-{region}-{role}'
    joined['exteriorEras'] = eras
    joined['region'] = region
    joined['surfaceRole'] = role
    joined['batchKey'] = batch_key(*key)
    joined['exportOwner'] = parent_name
    joined['batchSourceObjectsJson'] = json.dumps(names, separators=(',', ':'))
    joined['batchSourceObjectCount'] = len(names)
    joined_objects.append(joined)

    expected = batch_expectations[key]
    actual = mesh_metrics([joined])
    error = cloud_error(expected['worldVertices'], actual['worldVertices'])
    require(error <= WORLD_VERTEX_TOLERANCE,
            f'Batched world-vertex error {error} exceeds tolerance for {key}')
    require(expected['vertexCount'] == actual['vertexCount'], f'Batched vertex count changed for {key}')
    require(expected['polygonCount'] == actual['polygonCount'], f'Batched polygon count changed for {key}')
    require(expected['triangleCount'] == actual['triangleCount'], f'Batched triangle count changed for {key}')
    require(expected['materialFaceCounts'] == actual['materialFaceCounts'],
            f'Batched material face assignments changed for {key}')
    require(expected['materialTriangleCounts'] == actual['materialTriangleCounts'],
            f'Batched material triangle assignments changed for {key}')
    require(bounds_error(expected['worldBounds'], actual['worldBounds']) <= WORLD_VERTEX_TOLERANCE,
            f'Batched world bounds changed for {key}')
    require(joined.parent and joined.parent.name == parent_name, f'Batch owner changed for {key}')
    batch_records.append({'key': list(key), 'objectName': joined.name,
                          'sourceObjects': names, 'sourceObjectCount': len(names),
                          'vertices': actual['vertexCount'], 'polygons': actual['polygonCount'],
                          'triangles': actual['triangleCount'],
                          'worldBounds': actual['worldBounds'],
                          'materialFaceCounts': actual['materialFaceCounts'],
                          'materialTriangleCounts': actual['materialTriangleCounts'],
                          'maxSymmetricWorldVertexErrorMetres': error,
                          'owner': parent_name, 'eras': eras, 'region': region,
                          'surfaceRole': role})

post_batch_pivots = {o.name: matrix_json(o.matrix_world) for o in bpy.data.objects if o.type == 'EMPTY'}
require(set(post_batch_pivots) == set(pre_batch_pivots), 'Batch export changed the empty/pivot set')
pivot_batch_errors = {name: matrix_error(pre_batch_pivots[name], post_batch_pivots[name])
                      for name in pre_batch_pivots}
require(max(pivot_batch_errors.values(), default=0.0) <= PIVOT_MATRIX_TOLERANCE,
        'Batch export changed an empty/pivot transform')

bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.context.scene.objects:
    if obj.type in {'MESH', 'EMPTY'}:
        obj.select_set(True)
bpy.context.view_layer.objects.active = joined_objects[0] if joined_objects else None
bpy.ops.export_scene.gltf(
    filepath=str(OUT_GLB), export_format='GLB', use_selection=True,
    export_yup=True, export_apply=True, export_extras=True,
    export_cameras=False, export_lights=False, export_animations=True,
    export_animation_mode='ACTIONS', export_frame_range=True)
require(OUT_GLB.is_file() and OUT_GLB.stat().st_size > 100_000,
        'Batched GLB export missing or implausibly small')

# Verify encoded node ownership/tags/materials, then import the served derivative
# into a clean scene and compare its world geometry to the pre-export batches.
glb_doc = read_glb_json(OUT_GLB)
glb_full_doc, _glb_binary = read_glb_document(OUT_GLB)
glb_matrices, glb_world_for_node = gltf_node_world_matrices(glb_full_doc)
glb_nodes = {node.get('name'): node for node in glb_doc.get('nodes', []) if node.get('name')}
glb_node_indices = {node.get('name'): index for index, node in enumerate(glb_doc.get('nodes', []))
                    if node.get('name')}
glb_parent = {}
for node in glb_doc.get('nodes', []):
    for child in node.get('children', []):
        glb_parent[child] = node.get('name')
glb_export_records = []
glb_geometry_checks = []
for batch in batch_records:
    node = glb_nodes.get(batch['objectName'])
    require(node is not None and 'mesh' in node, f'GLB batch node missing: {batch["objectName"]}')
    require(glb_parent.get(glb_doc['nodes'].index(node)) == batch['owner'],
            f'GLB batch direct owner differs: {batch["objectName"]}')
    extras = node.get('extras', {})
    expected_extras = {'region': batch['region'], 'surfaceRole': batch['surfaceRole'],
                       'exteriorEras': batch['eras'], 'batchKey': batch_key(*batch['key']),
                       'exportOwner': batch['owner']}
    for field in ('region', 'surfaceRole', 'exteriorEras', 'batchKey', 'exportOwner'):
        require(extras.get(field) == expected_extras[field],
                f'GLB extra {field} was not preserved on {batch["objectName"]}')
    mesh = glb_doc['meshes'][node['mesh']]
    exported_triangles = 0
    material_names = set()
    for primitive in mesh.get('primitives', []):
        accessor = glb_doc['accessors'][primitive['attributes']['POSITION']]
        if 'indices' in primitive:
            index_count = glb_doc['accessors'][primitive['indices']]['count']
            require(index_count % 3 == 0, f'GLB primitive is not triangles: {batch["objectName"]}')
            exported_triangles += index_count // 3
        else:
            exported_triangles += max(0, accessor['count'] - 2)
        if 'material' in primitive:
            material_names.add(glb_doc['materials'][primitive['material']].get('name', '__unnamed__'))
    require(exported_triangles == batch['triangles'],
            f'GLB triangle count differs from joined geometry: {batch["objectName"]}')
    require(material_names == set(batch['materialFaceCounts']),
            f'GLB material set differs from joined geometry: {batch["objectName"]}')
    direct_metrics = glb_mesh_world_metrics(OUT_GLB, glb_node_indices[batch['objectName']],
                                            glb_matrices, glb_world_for_node)
    expected_gltf_points = blender_to_gltf_points(batch_expectations[tuple(batch['key'])]['worldVertices'])
    direct_error = cloud_error(expected_gltf_points, direct_metrics['worldVertices'],
                               allow_different_counts=True)
    require(direct_error <= WORLD_VERTEX_TOLERANCE,
            f'Direct GLB world-vertex error {direct_error} exceeds tolerance for {batch["objectName"]}')
    require(direct_metrics['triangleCount'] == batch['triangles'],
            f'Direct GLB triangle count changed for {batch["objectName"]}')
    require(direct_metrics['materialTriangleCounts'] == batch['materialTriangleCounts'],
            f'Direct GLB material triangles changed for {batch["objectName"]}')
    glb_geometry_checks.append({'objectName': batch['objectName'],
                                'triangleCount': direct_metrics['triangleCount'],
                                'materialTriangleCounts': direct_metrics['materialTriangleCounts'],
                                'exportedVertexCount': len(direct_metrics['worldVertices']),
                                'maxBidirectionalWorldVertexErrorMetres': direct_error})
    glb_export_records.append({'objectName': batch['objectName'],
                               'triangleCount': exported_triangles,
                               'materials': sorted(material_names),
                               'parentNode': glb_parent.get(glb_doc['nodes'].index(node)),
                               'extras': extras})

require(not any(node.get('camera') is not None or node.get('extensions', {}).get('KHR_lights_punctual')
                for node in glb_doc.get('nodes', [])), 'Camera/light node unexpectedly exported')
glb_material_names = sorted(mat.get('name', '__unnamed__') for mat in glb_doc.get('materials', []))
required_materials = sorted({name for batch in batch_records for name in batch['materialFaceCounts']
                             if name != '__none__'})
require(set(required_materials).issubset(set(glb_material_names)), 'GLB lost a used source material')

batch_expected_for_import = {
    batch['objectName']: (batch, batch_expectations[tuple(batch['key'])])
    for batch in batch_records
}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(OUT_GLB))
bpy.context.view_layer.update()
imported_objects = {obj.name: obj for obj in bpy.context.scene.objects if obj.type == 'MESH'}
glb_import_checks = []
for name, (batch, expected) in batch_expected_for_import.items():
    obj = imported_objects.get(name)
    require(obj is not None, f'Imported GLB batch missing: {name}')
    require(obj.parent is not None and obj.parent.name == batch['owner'],
            f'Imported GLB owner changed: {name}')
    metrics = mesh_metrics([obj])
    require(all(math.isfinite(c) for point in metrics['worldVertices'] for c in point),
            f'Imported GLB has non-finite positions: {name}')
    error = cloud_error(expected['worldVertices'], metrics['worldVertices'],
                        allow_different_counts=True)
    # Blender's own glTF importer is retained as a diagnostic, not a gate. Its
    # axis-root and animation-action evaluation can create small scene-matrix
    # differences that are absent in the direct GLB-space comparison above.
    require(metrics['triangleCount'] == batch['triangles'], f'Imported GLB triangle count changed: {name}')
    require(metrics['materialTriangleCounts'] == expected['materialTriangleCounts'],
            f'Imported GLB material face assignment changed: {name}')
    imported_bounds_error = bounds_error(metrics['worldBounds'], expected['worldBounds'])
    glb_import_checks.append({'objectName': name, 'owner': obj.parent.name,
                              'triangleCount': metrics['triangleCount'],
                              'materialTriangleCounts': metrics['materialTriangleCounts'],
                              'importedVertexCount': metrics['vertexCount'],
                              'maxBidirectionalWorldVertexErrorMetres': error,
                              'vertexErrorWithinTolerance': error <= WORLD_VERTEX_TOLERANCE,
                              'maxWorldBoundsDeltaMetres': imported_bounds_error,
                              'boundsWithinTolerance': imported_bounds_error <= WORLD_VERTEX_TOLERANCE,
                              'worldBounds': metrics['worldBounds']})

all_newguard_triangles = sum(item['controlTriangles'] for item in guard_control_records)
all_export_triangles = sum(item['triangles'] for item in batch_records)
manifest = {
    'schema': 'alignment-composed-regional-study/v1',
    'status': 'guard-only V5 sixth composition; regional study, not active application reference',
    'scope': 'V5 sixth frozen base with only the ten guard-study05 limb meshes replacing the exact 26 named prior sleeve/ankle surfaces. Talons are not included.',
    'batchingRecipe': 'V5 generator grouping by (parent owner, exteriorEras, region, surfaceRole); materials remain as multiple slots/primitives inside each owner batch.',
    'inputIdentity': {
        'base': {'blend': record(BASE_BLEND), 'glb': record(BASE_GLB), 'manifest': record(BASE_MANIFEST)},
        'guardStudy05': {'blend': record(GUARD_BLEND), 'glb': record(GUARD_GLB), 'manifest': record(GUARD_MANIFEST)},
        'c8LimbCompatibilitySource': {'blend': record(C8_BLEND), 'glb': record(C8_GLB), 'manifest': record(C8_MANIFEST)},
        'snapshots': snapshot_records,
        'baseGenerationSources': base_generation_sources,
        'guardStudyGeneratorScriptSnapshot': guard_script_record,
    },
    'generatorScript': record(Path(__file__).resolve()),
    'generatorScriptSnapshot': record(OUT_SCRIPT),
    'limbSourceCompatibility': compatibility,
    'composition': {
        'replacedObjects': removed_records,
        'addedGuards': guard_control_records,
        'guardObjectCount': len(guard_control_records),
        'newGuardControlTriangleCount': all_newguard_triangles,
        'nativeEmptyCount': len(composed_scene['empties']),
        'nativePivotMatrixMaxDelta': max(composition_pivot_errors.values(), default=0.0),
        'untouchedBaseMeshCount': len(source_scene['meshes']) - len(replaced_names),
        'materialNames': composed_scene['materials'],
    },
    'nativeOutput': record(OUT_BLEND),
    'export': {
        'glb': record(OUT_GLB),
        'modifierGeometryApplied': True,
        'camerasAndLightsExported': False,
        'usedMaterialNames': required_materials,
        'batchGroupCount': len(batch_records),
        'batchedTriangleCount': all_export_triangles,
        'worldVertexToleranceMetres': WORLD_VERTEX_TOLERANCE,
        'normalization': normalization,
        'pivotMatrixMaxDeltaDuringBatch': max(pivot_batch_errors.values(), default=0.0),
        'batches': batch_records,
        'glbBatchVerification': glb_export_records,
        'directGlbGeometryVerification': glb_geometry_checks,
        'glbImportedGeometryVerification': glb_import_checks,
    },
    'limits': [
        'Guard-only composition; six talons are intentionally not included pending a separately reviewed source.',
        'Batching is an export derivative. The saved native fork retains independent objects and editable modifiers.',
        'Geometry checks use bounded world-space vertex-cloud distance, bounds, face/material counts and triangles; they are not a mechanical or silhouette acceptance.',
        'No app reference, active model, runtime, or QA worktree was changed.',
    ],
}
OUT_MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'native': str(OUT_BLEND), 'glb': str(OUT_GLB),
                  'manifest': str(OUT_MANIFEST), 'baseSha256': sha256(BASE_BLEND),
                  'guardSourceSha256': sha256(GUARD_BLEND),
                  'glbSha256': sha256(OUT_GLB), 'guardCount': len(guard_control_records),
                  'replacedCount': len(removed_records), 'batchGroups': len(batch_records),
                  'batchTriangles': all_export_triangles,
                  'nativePivotMaxDelta': max(composition_pivot_errors.values(), default=0.0),
                  'batchPivotMaxDelta': max(pivot_batch_errors.values(), default=0.0),
                  'maxGeometryError': max((b['maxSymmetricWorldVertexErrorMetres'] for b in batch_records), default=0.0)}, indent=2))
