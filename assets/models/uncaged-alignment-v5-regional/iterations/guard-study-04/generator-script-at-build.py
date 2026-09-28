"""Build an isolated, editable limb-profile study from frozen V5 source.

This is a regional visible-shape study, not dimensional reconstruction or a
validated mechanical design. The script preserves every existing rig empty and
only replaces the authored thigh/shin sleeves and ankle sheath/lap-rib meshes.
"""

import hashlib
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import struct
import sys

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
ITERATION = 'c8a7a7e14253'


def parse_options():
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    frozen_dir = Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged') / 'assets/models/uncaged-alignment-v5/iterations' / ITERATION
    parser.add_argument('--out', type=Path, default=ROOT / '.local/alignment-limb-study/v5-fourth-limb-profile-study-04')
    parser.add_argument('--source-blend', type=Path, default=frozen_dir / 'murderbird-alignment-v5.blend')
    parser.add_argument('--source-manifest', type=Path, default=frozen_dir / 'alignment-inventory.json')
    parser.add_argument('--source-glb', type=Path, default=frozen_dir / 'murderbird-alignment-v5.glb')
    return parser.parse_args(args)


OPTIONS = parse_options()
SOURCE_BLEND = OPTIONS.source_blend.expanduser().resolve()
SOURCE_MANIFEST = OPTIONS.source_manifest.expanduser().resolve()
SOURCE_GLB = OPTIONS.source_glb.expanduser().resolve()
OUT_DIR = OPTIONS.out.expanduser().resolve()
OUT_BLEND = OUT_DIR / 'murderbird-limb-profile-study.blend'
OUT_GLB = OUT_DIR / 'murderbird-limb-profile-study.glb'
OUT_MANIFEST = OUT_DIR / 'manifest.json'
OUT_SCRIPT = OUT_DIR / 'generator-script-at-build.py'
EXPECTED_BLEND_SHA = 'cc6bfafc9ab044bba1abcbec86761afb9ef67ee60e252ec7ee838948ea7dfd04'
EXPECTED_GLB_SHA = 'c8a7a7e14253075414d8e55390ebad2bf605ad09962fa62769417834000ccaa3'
EXPECTED_BLEND_BYTES = 1827441
EXPECTED_GLB_BYTES = 3844888


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def file_record(path):
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha256(path)}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def vector_json(v):
    return [round(float(x), 12) for x in v]


def matrix_json(matrix):
    return [[round(float(matrix[r][c]), 12) for c in range(4)] for r in range(4)]


def matrix_error(a, b):
    return max(abs(float(a[r][c]) - float(b[r][c]))
               for r in range(4) for c in range(4))


def bind_to_owner(obj, owner):
    # Geometry is authored in world coordinates at the source neutral pose.
    # Parent inverse keeps that neutral placement and makes the shell follow
    # the existing rigid owner when its preserved hierarchy articulates.
    obj.parent = owner
    obj.matrix_parent_inverse = owner.matrix_world.inverted()
    obj.matrix_basis.identity()


def add_mesh(name, vertices_world, faces, owner, region):
    mesh = bpy.data.meshes.new(name + ' editable control mesh')
    mesh.from_pydata([tuple(v) for v in vertices_world], [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bind_to_owner(obj, owner)
    obj['region'] = region
    obj['surfaceRole'] = 'plate'
    obj['geometryStatus'] = 'editable regional profile proposal'
    mat = bpy.data.materials.get('Neutral / plate')
    require(mat is not None, 'Neutral / plate material missing')
    obj.data.materials.append(mat)
    for poly in mesh.polygons:
        poly.use_smooth = True
    solid = obj.modifiers.new('Shallow returned profile wall', 'SOLIDIFY')
    solid.thickness = 0.005
    solid.offset = -0.7
    bevel = obj.modifiers.new('Soft profile edge', 'BEVEL')
    bevel.width = 0.0014
    bevel.segments = 2
    obj.modifiers.new('Weighted profile normals', 'WEIGHTED_NORMAL')
    return obj


def create_link_guard(label, owner, a, b, side, region, interval, name_suffix):
    axis = (b - a).normalized()
    front = Vector((0, -1, 0))
    front = (front - axis * front.dot(axis)).normalized()
    across = axis.cross(front).normalized()
    if across.x * side < 0:
        across.negate()

    start, end = interval
    rows, columns = 13, 19
    vertices, faces = [], []
    for j in range(rows):
        u = j / (rows - 1)
        t = start + (end - start) * u
        center = a.lerp(b, t)
        # Width is a single smooth link-global taper, so both overlapping
        # panels meet at identical section profiles without a repeated bulb.
        eased = t * t * (3.0 - 2.0 * t)
        breadth = 1.17 - 0.31 * eased
        for k in range(columns):
            theta = -1.32 + 2.64 * k / (columns - 1)
            flank = 1.0 + (0.13 if math.sin(theta) * side > 0 else -0.045)
            w = (0.040 if region == 'thigh' else 0.034) * breadth * flank
            # A small center ridge gives the guard a formed profile while the
            # shallow side skirts leave the paired load rails visible.
            ridge = 0.030 if region == 'thigh' else 0.025
            crown = ridge * math.cos(theta) + 0.0035 * math.exp(-((theta / .20) ** 2))
            p = center + across * (math.sin(theta) * w) + front * crown
            vertices.append(p)
    for j in range(rows - 1):
        for k in range(columns - 1):
            i = j * columns + k
            faces.append((i, i + 1, i + columns + 1, i + columns))
    return add_mesh(f'{label} shaped {region} guard {name_suffix}', vertices, faces,
                    owner, 'leg')


def create_instep(label, owner, ankle, side):
    # Narrow curved dorsal shell follows the source ankle-to-foot direction.
    # A shallow longitudinal trough and returned flanks keep the existing
    # metatarsal rails readable instead of covering them with a broad boot.
    rows, columns = 17, 17
    vertices, faces = [], []
    for j in range(rows):
        u = j / (rows - 1)
        y = ankle.y - 0.018 - 0.128 * u
        z = ankle.z - 0.020 - 0.185 * u + 0.014 * math.sin(math.pi * u)
        width = 0.027 + 0.010 * u
        for k in range(columns):
            theta = -1.25 + 2.5 * k / (columns - 1)
            x = ankle.x + math.sin(theta) * width
            arch = 0.021 * math.cos(theta) * (0.94 - 0.16 * u)
            returned_flank = 0.0045 * math.exp(-(((abs(theta) - .86) / .19) ** 2))
            center_channel = 0.0028 * math.exp(-((theta / .16) ** 2))
            crown = arch + returned_flank - center_channel
            vertices.append(Vector((x, y - crown, z + crown)))
    for j in range(rows - 1):
        for k in range(columns - 1):
            i = j * columns + k
            faces.append((i, i + 1, i + columns + 1, i + columns))
    return add_mesh(f'{label} curved instep guard', vertices, faces, owner, 'foot')


def evaluated_triangles(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        return sum(max(0, len(poly.vertices) - 2) for poly in mesh.polygons)
    finally:
        evaluated.to_mesh_clear()


def evaluated_bounds(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        points = [tuple(float(x) for x in v.co) for v in mesh.vertices]
        return {'min': [min(p[i] for p in points) for i in range(3)],
                'max': [max(p[i] for p in points) for i in range(3)]}
    finally:
        evaluated.to_mesh_clear()


def parse_exported_guard_meshes(path, guard_names):
    data = path.read_bytes()
    require(data[:4] == b'glTF', 'Exported file is not a GLB')
    json_length, chunk_type = struct.unpack_from('<I4s', data, 12)
    require(chunk_type == b'JSON', 'GLB first chunk is not JSON')
    document = json.loads(data[20:20 + json_length].decode('utf-8').rstrip(' \0'))
    records = {}
    for name in guard_names:
        node = next((n for n in document.get('nodes', []) if n.get('name') == name), None)
        require(node is not None and 'mesh' in node, f'Exported node missing: {name}')
        mesh = document['meshes'][node['mesh']]
        triangles, bounds = 0, None
        for primitive in mesh.get('primitives', []):
            position = document['accessors'][primitive['attributes']['POSITION']]
            require('min' in position and 'max' in position, f'POSITION bounds missing: {name}')
            bounds = {'min': position['min'], 'max': position['max']}
            if 'indices' in primitive:
                index_count = document['accessors'][primitive['indices']]['count']
                require(index_count % 3 == 0, f'Non-triangle index count: {name}')
                triangles += index_count // 3
            else:
                triangles += max(0, position['count'] - 2)
        records[name] = {'triangles': triangles, 'accessorBounds': bounds,
                         'primitiveCount': len(mesh.get('primitives', []))}
    return records


require(SOURCE_BLEND.is_file() and SOURCE_MANIFEST.is_file() and SOURCE_GLB.is_file(),
        'Frozen V5 fourth-source files are incomplete')
require(sha256(SOURCE_BLEND) == EXPECTED_BLEND_SHA, 'Frozen input blend SHA mismatch')
require(SOURCE_BLEND.stat().st_size == EXPECTED_BLEND_BYTES, 'Frozen input blend size mismatch')
require(sha256(SOURCE_GLB) == EXPECTED_GLB_SHA, 'Frozen input GLB SHA mismatch')
require(SOURCE_GLB.stat().st_size == EXPECTED_GLB_BYTES, 'Frozen input GLB size mismatch')
require(not any(p.exists() for p in (OUT_BLEND, OUT_GLB, OUT_MANIFEST)),
        'Refusing to replace an existing study output')
require(not OUT_SCRIPT.exists(), 'Refusing to replace existing generator snapshot')
OUT_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(Path(__file__).resolve(), OUT_SCRIPT)

bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
require(bpy.data.objects.get('left-thigh') and bpy.data.objects.get('right-thigh'),
        'Expected bilateral thigh owners missing')
empty_matrices_before = {o.name: o.matrix_world.copy() for o in bpy.data.objects if o.type == 'EMPTY'}
empty_records_before = {name: matrix_json(matrix) for name, matrix in empty_matrices_before.items()}
survivor_hashes_before = {}
for obj in bpy.data.objects:
    name = obj.name.lower()
    replaced_candidate = ('tapered limb sheath' in name or 'articulated ankle sheath' in name
                         or 'ankle sheath lap rib' in name)
    if obj.type == 'MESH' and not replaced_candidate:
        survivor_hashes_before[obj.name] = sha256_bytes = hashlib.sha256(
            repr((tuple(tuple(round(float(v), 9) for v in vert.co) for vert in obj.data.vertices),
                 tuple(tuple(poly.vertices) for poly in obj.data.polygons))).encode()).hexdigest()

replace = []
for obj in list(bpy.data.objects):
    if obj.type != 'MESH':
        continue
    name = obj.name.lower()
    if ('tapered limb sheath' in name or 'articulated ankle sheath' in name
            or 'ankle sheath lap rib' in name):
        replace.append(obj.name)
        bpy.data.objects.remove(obj, do_unlink=True)
require(len(replace) == 26, f'Unexpected sleeve/ankle replacement count: {len(replace)}')

new_objects = []
for label, side in (('left', 1), ('right', -1)):
    thigh = bpy.data.objects[label + '-thigh']
    shin = bpy.data.objects[label + '-shin']
    foot = bpy.data.objects[label + '-foot']
    hip = thigh.matrix_world.translation.copy()
    knee = shin.matrix_world.translation.copy()
    ankle = foot.matrix_world.translation.copy()
    # Two panels overlap once by 0.035 of each link. Each has a separate
    # editable control mesh, giving one leg form per segment, not decorative ribs.
    new_objects.append(create_link_guard(label, thigh, hip, knee, side, 'thigh', (.095, .535), 'proximal'))
    new_objects.append(create_link_guard(label, thigh, hip, knee, side, 'thigh', (.500, .925), 'distal-overlap'))
    new_objects.append(create_link_guard(label, shin, knee, ankle, side, 'shin', (.090, .535), 'proximal'))
    new_objects.append(create_link_guard(label, shin, knee, ankle, side, 'shin', (.500, .915), 'distal-overlap'))
    new_objects.append(create_instep(label, foot, ankle, side))

for name, before in empty_matrices_before.items():
    after = bpy.data.objects[name].matrix_world
    require(matrix_error(before, after) <= 1e-10, f'Pivot moved: {name}')
for obj in bpy.data.objects:
    if obj.name in survivor_hashes_before:
        after_hash = hashlib.sha256(
            repr((tuple(tuple(round(float(v), 9) for v in vert.co) for vert in obj.data.vertices),
                 tuple(tuple(poly.vertices) for poly in obj.data.polygons))).encode()).hexdigest()
        require(after_hash == survivor_hashes_before[obj.name], f'Unrelated mesh changed: {obj.name}')

# Validate all authored control vertices and evaluated geometry before saving.
for obj in new_objects:
    require(all(math.isfinite(float(c)) for v in obj.data.vertices for c in v.co),
            f'Non-finite control vertex in {obj.name}')
depsgraph = bpy.context.evaluated_depsgraph_get()
for obj in new_objects:
    tri_count = evaluated_triangles(obj, depsgraph)
    require(tri_count > 0, f'Empty evaluated geometry in {obj.name}')

# Persist the fully editable native fork before producing the interchange file.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND), check_existing=False)
require(OUT_BLEND.is_file(), 'Native fork was not saved')

# Export visible rigid geometry and the preserved empty hierarchy only.
# Apply modifiers to the GLB derivative; the native fork saved above remains
# editable with its Solidify, Bevel and Weighted Normal modifiers.
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type in {'MESH', 'EMPTY'}:
        obj.select_set(True)
try:
    bpy.ops.export_scene.gltf(filepath=str(OUT_GLB), export_format='GLB',
                              use_selection=True, export_yup=True,
                              export_apply=True, export_extras=True,
                              export_animations=True, export_cameras=False,
                              export_lights=False)
except TypeError:
    bpy.ops.export_scene.gltf(filepath=str(OUT_GLB), export_format='GLB',
                              use_selection=True, export_yup=True,
                              export_apply=True, export_extras=True,
                              export_cameras=False, export_lights=False)
require(OUT_GLB.is_file() and OUT_GLB.stat().st_size > 100_000,
        'GLB export missing or implausibly small')

depsgraph = bpy.context.evaluated_depsgraph_get()
piece_records = []
for obj in new_objects:
    piece_records.append({
        'name': obj.name,
        'owner': obj.parent.name if obj.parent else None,
        'region': obj.get('region'),
        'vertices': len(obj.data.vertices),
        'controlTriangles': sum(max(0, len(poly.vertices) - 2) for poly in obj.data.polygons),
        'evaluatedTriangles': evaluated_triangles(obj, depsgraph),
        'evaluatedLocalBounds': evaluated_bounds(obj, depsgraph),
        'finiteGeometry': True,
    })
exported_guards = parse_exported_guard_meshes(OUT_GLB, [obj.name for obj in new_objects])
for record in piece_records:
    exported = exported_guards[record['name']]
    require(exported['triangles'] == record['evaluatedTriangles'],
            f"Modifier export triangle mismatch for {record['name']}: "
            f"native={record['evaluatedTriangles']} glb={exported['triangles']}")
    native_bounds = record['evaluatedLocalBounds']
    # Blender's z-up local xyz becomes glTF's y-up xyz as (x, z, -y).
    expected_min = [native_bounds['min'][0], native_bounds['min'][2], -native_bounds['max'][1]]
    expected_max = [native_bounds['max'][0], native_bounds['max'][2], -native_bounds['min'][1]]
    for axis in range(3):
        require(abs(expected_min[axis] - exported['accessorBounds']['min'][axis]) < 1e-5
                and abs(expected_max[axis] - exported['accessorBounds']['max'][axis]) < 1e-5,
                f"Modifier export bounds mismatch for {record['name']}")
    record['exportedTriangles'] = exported['triangles']
    record['exportedAccessorBounds'] = exported['accessorBounds']
empty_records_after = {o.name: matrix_json(o.matrix_world) for o in bpy.data.objects if o.type == 'EMPTY'}
pivot_checks = []
for name, before in empty_records_before.items():
    after = empty_records_after.get(name)
    require(after is not None, f'Pivot removed: {name}')
    err = matrix_error(empty_matrices_before[name], bpy.data.objects[name].matrix_world)
    pivot_checks.append({'name': name, 'before': before, 'after': after, 'maxAbsMatrixDelta': err})

manifest = {
    'schema': 'alignment-limb-profile-study/v1',
    'status': 'isolated regional geometry study; not active V6 and not mechanically validated',
    'scope': 'Visible leg-guard profile study based on illustration-supported silhouette cues only; hidden mechanisms, dimensional metrology, load capacity, balance, and force/grip remain unknown.',
    'export': {'modifierGeometryAppliedToGlb': True, 'nativeBlendRetainsEditableModifiers': True,
               'selectedTypes': ['MESH', 'EMPTY'], 'camerasAndLights': False,
               'geometryCheck': 'Each new guard GLB triangle count and POSITION accessor bounds are compared with its Blender dependency-graph evaluated mesh after the documented Blender z-up to glTF y-up basis conversion (x,z,-y).'},
    'input': {
        'sourceIteration': ITERATION,
        'blend': file_record(SOURCE_BLEND),
        'glb': file_record(SOURCE_GLB),
        'inventoryManifest': file_record(SOURCE_MANIFEST),
    },
    'generatorScript': file_record(Path(__file__).resolve()),
    'generatorScriptSnapshot': file_record(OUT_SCRIPT),
    'outputs': {'blend': file_record(OUT_BLEND), 'glb': file_record(OUT_GLB)},
    'replacedObjects': sorted(replace),
    'newObjects': piece_records,
    'pieceCount': len(piece_records),
    'controlTriangleCount': sum(p['controlTriangles'] for p in piece_records),
    'evaluatedTriangleCount': sum(p['evaluatedTriangles'] for p in piece_records),
    'exportedGuardTriangleCount': sum(p['exportedTriangles'] for p in piece_records),
    'pivotMatrixComparison': {'emptyCount': len(pivot_checks), 'maxAbsMatrixDelta': max((p['maxAbsMatrixDelta'] for p in pivot_checks), default=0), 'checks': pivot_checks},
    'preservedExternalMeshCount': len(survivor_hashes_before),
}
OUT_MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'savedBlend': str(OUT_BLEND), 'savedGlb': str(OUT_GLB),
                  'manifest': str(OUT_MANIFEST), 'pieces': len(piece_records),
                  'triangles': manifest['evaluatedTriangleCount'],
                  'pivotCount': len(pivot_checks),
                  'maxPivotDelta': manifest['pivotMatrixComparison']['maxAbsMatrixDelta']}, indent=2))
