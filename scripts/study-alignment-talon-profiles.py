"""Create a reversible distal-talon cross-section study from immutable V5 c8.

Run with Blender 5.2 background Python. This forks the exact frozen native source,
reshapes only six talon sheath meshes, preserves their centerlines and final 15%,
and writes new local study outputs. It does not update an app or release asset.
"""
from __future__ import annotations

import bpy
import hashlib
import json
import math
import shutil
import struct
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
QA = Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
SOURCE_DIR = QA / 'assets/models/uncaged-alignment-v5/iterations/c8a7a7e14253'
SOURCE_BLEND = SOURCE_DIR / 'murderbird-alignment-v5.blend'
SOURCE_GLB = SOURCE_DIR / 'murderbird-alignment-v5.glb'
SOURCE_INVENTORY = SOURCE_DIR / 'alignment-inventory.json'
PRODUCTION_GLB = ROOT / '.local/alignment-v5-diagnostics/c8a7a7e14253/murderbird-alignment-v5.glb'
OUT = ROOT / '.local/alignment-limb-study/talon-profile-study-01'
NATIVE_OUT = OUT / 'murderbird-talon-profile-study-01.blend'
GLB_OUT = OUT / 'murderbird-talon-profile-study-01.glb'
MANIFEST_OUT = OUT / 'study-manifest.json'
SCRIPT_SNAPSHOT = OUT / 'study-alignment-talon-profiles.py'
EXPECTED_NATIVE_SHA = 'cc6bfafc9ab044bba1abcbec86761afb9ef67ee60e252ec7ee838948ea7dfd04'
EXPECTED_GLB_SHA = 'c8a7a7e14253075414d8e55390ebad2bf605ad09962fa62769417834000ccaa3'
TALON_NAMES = [f'{side} digit {digit} tapered claw sheath'
               for side in ('left', 'right') for digit in (1, 2, 3)]
VENTRAL_POWER = 2.55
DORSAL_POWER = 1.88
FADE_START = 0.75
FADE_END = 0.85
RING_COUNT = 17
RING_SIZE = 16
EPS = 1e-7


def fail(message: str) -> None:
    raise RuntimeError(f'talon profile study refused: {message}')


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def file_record(path: Path, label: str | None = None) -> dict:
    return {'path': label or path.relative_to(ROOT).as_posix(),
            'bytes': path.stat().st_size, 'sha256': sha256(path)}


def checked_source() -> dict:
    for path in (SOURCE_BLEND, SOURCE_GLB, SOURCE_INVENTORY, PRODUCTION_GLB):
        if not path.is_file():
            fail(f'missing immutable source file: {path}')
    native_sha = sha256(SOURCE_BLEND)
    glb_sha = sha256(SOURCE_GLB)
    prod_sha = sha256(PRODUCTION_GLB)
    if native_sha != EXPECTED_NATIVE_SHA:
        fail(f'QA native SHA changed: {native_sha}')
    if glb_sha != EXPECTED_GLB_SHA or prod_sha != EXPECTED_GLB_SHA:
        fail(f'c8 export identity mismatch: QA={glb_sha}, production diagnostic={prod_sha}')
    inventory = json.loads(SOURCE_INVENTORY.read_text())
    generated = {Path(row.get('path', '')).suffix: row for row in inventory.get('generatedFiles', [])
                 if Path(row.get('path', '')).suffix in {'.blend', '.glb'}}
    if generated.get('.blend', {}).get('sha256') != EXPECTED_NATIVE_SHA:
        fail('QA inventory does not bind the requested native SHA')
    if generated.get('.glb', {}).get('sha256') != EXPECTED_GLB_SHA:
        fail('QA inventory does not bind the requested GLB SHA')
    if not bpy.data.filepath or Path(bpy.data.filepath).resolve() != SOURCE_BLEND.resolve():
        fail(f'Blender is not open on the immutable QA native source: {bpy.data.filepath}')
    return {
        'native': file_record(SOURCE_BLEND, str(SOURCE_BLEND)),
        'exportedGLB': file_record(SOURCE_GLB, str(SOURCE_GLB)),
        'inventory': file_record(SOURCE_INVENTORY, str(SOURCE_INVENTORY)),
        'productionDiagnosticGLB': file_record(PRODUCTION_GLB, str(PRODUCTION_GLB)),
    }


def transform_snapshot(obj) -> dict:
    return {
        'name': obj.name,
        'parent': obj.parent.name if obj.parent else None,
        'location': tuple(float(x) for x in obj.location),
        'rotation': tuple(float(x) for x in obj.rotation_euler),
        'quaternion': tuple(float(x) for x in obj.rotation_quaternion),
        'scale': tuple(float(x) for x in obj.scale),
        'matrixWorld': tuple(float(x) for row in obj.matrix_world for x in row),
    }


def mesh_signature(obj) -> str:
    mesh = obj.data
    h = hashlib.sha256()
    h.update(obj.name.encode())
    h.update((obj.parent.name if obj.parent else '').encode())
    h.update(struct.pack('<II', len(mesh.vertices), len(mesh.polygons)))
    for vertex in mesh.vertices:
        h.update(struct.pack('<3f', *vertex.co))
    for poly in mesh.polygons:
        h.update(struct.pack('<I', len(poly.vertices)))
        h.update(struct.pack('<' + 'I' * len(poly.vertices), *poly.vertices))
        h.update(struct.pack('<i?', poly.material_index, poly.use_smooth))
    for modifier in obj.modifiers:
        h.update((modifier.name + ':' + modifier.type).encode())
    return h.hexdigest()


def mesh_data_from_poly(mesh, coords, faces, materials, smooth_flags, material_indices) -> None:
    mesh.clear_geometry()
    mesh.from_pydata(coords, [], faces)
    mesh.materials.clear()
    for material in materials:
        mesh.materials.append(material)
    mesh.update(calc_edges=True)
    if len(mesh.polygons) != len(smooth_flags):
        fail(f'{mesh.name}: reconstructed face count changed unexpectedly')
    for poly, smooth, material_index in zip(mesh.polygons, smooth_flags, material_indices):
        poly.use_smooth = smooth
        poly.material_index = material_index


def find_rings(obj) -> tuple[list[list[int]], set[int], list[dict[int, int]]]:
    mesh = obj.data
    cap_polys = [poly for poly in mesh.polygons if len(poly.vertices) == RING_SIZE]
    if len(cap_polys) != 2:
        fail(f'{obj.name}: expected exactly two 16-vertex cap rings, found {len(cap_polys)}')
    cap_rows = [list(poly.vertices) for poly in cap_polys]
    cap_centers_y = [sum((obj.matrix_world @ mesh.vertices[i].co).y for i in ring) / RING_SIZE
                     for ring in cap_rows]
    start_i = max(range(2), key=lambda i: cap_centers_y[i])
    start = cap_rows[start_i]
    end_set = set(cap_rows[1 - start_i])
    if len(set(start)) != RING_SIZE or len(end_set) != RING_SIZE:
        fail(f'{obj.name}: cap ring has repeated vertices')
    quads = [list(poly.vertices) for poly in mesh.polygons if len(poly.vertices) == 4]
    rings = [start]
    transitions = []
    current = start
    seen = set(current)
    for _ in range(RING_COUNT - 1):
        mapping: dict[int, int] = {}
        for k, a in enumerate(current):
            b = current[(k + 1) % RING_SIZE]
            matches = []
            for quad in quads:
                for j in range(4):
                    qa, qb = quad[j], quad[(j + 1) % 4]
                    if (qa == a and qb == b) or (qa == b and qb == a):
                        matches.append(quad)
                        break
            # Away from the first cap, both the incoming and outgoing strip
            # share this ring edge. Continue outward by excluding seen vertices.
            matches = [quad for quad in matches
                       if not (set(quad) - {a, b}) & seen]
            if len(matches) != 1:
                fail(f'{obj.name}: boundary edge {a}/{b} has {len(matches)} outward side quads')
            quad = matches[0]
            found = False
            for j in range(4):
                qa, qb = quad[j], quad[(j + 1) % 4]
                if qa == a and qb == b:
                    # Face cycle is a,b,next(b),next(a).
                    mapping[a] = quad[(j + 3) % 4]
                    mapping[b] = quad[(j + 2) % 4]
                    found = True
                    break
                if qa == b and qb == a:
                    # Face cycle is b,a,next(a),next(b).
                    mapping[a] = quad[(j + 2) % 4]
                    mapping[b] = quad[(j + 3) % 4]
                    found = True
                    break
            if not found:
                fail(f'{obj.name}: cannot orient ring transition at {a}/{b}')
        nxt = [mapping.get(index, -1) for index in current]
        if any(index < 0 for index in nxt) or len(set(nxt)) != RING_SIZE:
            fail(f'{obj.name}: ring transition is not one-to-one')
        nxt_set = set(nxt)
        if len(nxt_set & seen) != 0:
            fail(f'{obj.name}: ring chain self-reuses vertices')
        rings.append(nxt)
        transitions.append(mapping)
        current = nxt
        seen |= nxt_set
    if set(rings[-1]) != end_set:
        fail(f'{obj.name}: derived terminal ring does not match the second cap')
    if len(seen) != RING_COUNT * RING_SIZE or len(mesh.vertices) != RING_COUNT * RING_SIZE:
        fail(f'{obj.name}: mesh is not an isolated 17x16 swept-ring topology')
    centers = [sum((obj.matrix_world @ mesh.vertices[i].co for i in ring), Vector()) / RING_SIZE
               for ring in rings]
    if any(centers[i + 1].y >= centers[i].y - 1e-8 for i in range(len(centers) - 1)):
        fail(f'{obj.name}: derived rings do not progress monotonically forward along -Y')
    if len(mesh.polygons) != 16 * 16 + 2:
        fail(f'{obj.name}: unexpected surface topology; expected 256 side quads and two caps')
    # Confirm each adjacent ring pair is connected by exactly one quad per edge.
    for ring_i in range(RING_COUNT - 1):
        a_set, b_set = set(rings[ring_i]), set(rings[ring_i + 1])
        segment_faces = [f for f in quads if sum(v in a_set for v in f) == 2 and sum(v in b_set for v in f) == 2]
        if len(segment_faces) != RING_SIZE:
            fail(f'{obj.name}: ring interval {ring_i} has {len(segment_faces)} quads')
    return rings, end_set, transitions


def smoothstep(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def axis_fit(values: list[float], lower: float, upper: float) -> list[float]:
    mean = sum(values) / len(values)
    shifted = [x - mean for x in values]
    scale = 1.0
    high = max(shifted)
    low = min(shifted)
    if high > 1e-12:
        scale = min(scale, upper / high)
    if low < -1e-12:
        scale = min(scale, lower / low)
    scale = max(0.0, min(1.0, scale))
    return [x * scale for x in shifted]


def deform_section(obj, ring: list[int], center_world: Vector,
                   tangent: Vector, weight: float) -> dict:
    mesh = obj.data
    tangent = tangent.normalized()
    lateral = Vector((1.0, 0.0, 0.0))
    normal = Vector((0.0, -tangent.z, tangent.y))
    if normal.length < 1e-9:
        fail(f'{obj.name}: cannot derive source transverse section normal')
    normal.normalize()
    coords_world = [obj.matrix_world @ mesh.vertices[i].co for i in ring]
    u_values = [(point - center_world).x for point in coords_world]
    v_values = [(point - center_world).dot(normal) for point in coords_world]
    u_lower, u_upper = min(u_values), max(u_values)
    v_lower, v_upper = min(v_values), max(v_values)
    u_radius = max(abs(u_lower), abs(u_upper))
    v_radius = max(abs(v_lower), abs(v_upper))
    if u_radius < 1e-6 or v_radius < 1e-6:
        fail(f'{obj.name}: degenerate cross-section at ring')
    shaped_u, shaped_v = [], []
    for u, v in zip(u_values, v_values):
        x = max(-1.0, min(1.0, u / u_radius))
        y = max(-1.0, min(1.0, v / v_radius))
        # +normal points ventrally when normal.z is negative, per the
        # generator's (0,-tangent.z,tangent.y) section basis.
        ventral = y * normal.z < 0
        power = VENTRAL_POWER if ventral else DORSAL_POWER
        exponent = 2.0 / power
        sx = math.copysign(abs(x) ** exponent, x) if abs(x) > 1e-12 else 0.0
        sy = math.copysign(abs(y) ** exponent, y) if abs(y) > 1e-12 else 0.0
        shaped_u.append(sx * u_radius)
        shaped_v.append(sy * v_radius)
    shaped_u = axis_fit(shaped_u, u_lower, u_upper)
    shaped_v = axis_fit(shaped_v, v_lower, v_upper)
    result = {}
    inv = obj.matrix_world.inverted()
    for vertex_index, u, v, old_u, old_v in zip(ring, shaped_u, shaped_v, u_values, v_values):
        blend_u = old_u + (u - old_u) * weight
        blend_v = old_v + (v - old_v) * weight
        # Recenter blended asymmetry so the sampled ring centerline stays fixed.
        result[vertex_index] = inv @ (center_world + Vector((blend_u, 0.0, 0.0)) + normal * blend_v)
    return result


def build_ribbon_insert(original_coords, ring13, ring14, transition, alpha):
    mid = {}
    for vertex in ring13:
        other = transition[vertex]
        mid[vertex] = original_coords[vertex].lerp(original_coords[other], alpha)
    return mid


def transform_snapshot_equal(a: dict, b: dict) -> bool:
    return (a['name'] == b['name'] and a['parent'] == b['parent'] and
            all(abs(x - y) <= EPS for key in ('location', 'rotation', 'quaternion', 'scale', 'matrixWorld')
                for x, y in zip(a[key], b[key])))


def parse_glb(path: Path) -> dict:
    raw = path.read_bytes()
    if len(raw) < 20 or raw[:4] != b'glTF':
        fail(f'not a GLB file: {path}')
    version, total = struct.unpack_from('<II', raw, 4)
    if version != 2 or total != len(raw):
        fail(f'invalid GLB header: {path}')
    json_len, json_type = struct.unpack_from('<II', raw, 12)
    if json_type != 0x4E4F534A:
        fail(f'GLB has no leading JSON chunk: {path}')
    gltf = json.loads(raw[20:20 + json_len].decode('utf-8').rstrip(' \t\r\n\x00'))
    bin_offset = 20 + json_len
    bin_chunk_len, bin_type = struct.unpack_from('<II', raw, bin_offset)
    if bin_type != 0x004E4942:
        fail(f'GLB has no BIN chunk: {path}')
    binary = raw[bin_offset + 8:bin_offset + 8 + bin_chunk_len]
    types = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT2': 4, 'MAT3': 9, 'MAT4': 16}
    widths = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}

    def accessor_payload(index):
        accessor = gltf['accessors'][index]
        if 'bufferView' not in accessor:
            return b''
        view = gltf['bufferViews'][accessor['bufferView']]
        component_width = widths[accessor['componentType']]
        item_width = types[accessor['type']] * component_width
        stride = view.get('byteStride', item_width)
        start = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
        return b''.join(binary[start + i * stride:start + i * stride + item_width]
                        for i in range(accessor['count']))

    rows = []
    for index, mesh in enumerate(gltf.get('meshes', [])):
        primitives = []
        for primitive in mesh.get('primitives', []):
            attributes = {}
            for name, accessor_index in sorted(primitive.get('attributes', {}).items()):
                accessor = gltf['accessors'][accessor_index]
                attributes[name] = {
                    'count': accessor['count'],
                    'min': accessor.get('min'), 'max': accessor.get('max'),
                    'sha256': hashlib.sha256(accessor_payload(accessor_index)).hexdigest(),
                }
            index_accessor = primitive.get('indices')
            index_count = gltf['accessors'][index_accessor]['count'] if index_accessor is not None else None
            tri_count = index_count // 3 if index_count is not None and primitive.get('mode', 4) == 4 else None
            primitives.append({'attributes': attributes, 'indexCount': index_count,
                               'triangleCount': tri_count, 'mode': primitive.get('mode', 4)})
        rows.append({'name': mesh.get('name', f'mesh-{index}'), 'primitives': primitives})
    return {'meshes': rows, 'assetVersion': gltf.get('asset', {}).get('version')}


def main() -> None:
    source_records = checked_source()
    if OUT.exists():
        fail(f'output directory already exists; refusing to overwrite: {OUT}')
    if not SOURCE_BLEND.is_file() or not SOURCE_GLB.is_file():
        fail('source inputs disappeared')
    inventory = json.loads(SOURCE_INVENTORY.read_text())
    source_parts = {row['name']: row for row in inventory.get('parts', [])}
    source_native_signature = {}
    source_pivots = {}
    source_objects = {obj.name: obj for obj in bpy.data.objects}
    if set(TALON_NAMES) - set(source_objects):
        fail(f'missing native talon objects: {sorted(set(TALON_NAMES) - set(source_objects))}')
    for name in TALON_NAMES:
        obj = source_objects[name]
        part = source_parts.get(name)
        if part != {'name': name, 'parent': obj.parent.name if obj.parent else None,
                    'region': obj.get('region'), 'role': obj.get('surfaceRole'),
                    'eras': obj.get('exteriorEras', '').split(','),
                    'class': obj.get('constructionClass')}:
            fail(f'{name}: live native ownership disagrees with the source inventory')
        if obj.type != 'MESH' or obj.parent is None or obj.parent.name != name.replace(' digit ', '-digit-').replace(' tapered claw sheath', '-distal'):
            fail(f'{name}: unexpected mesh type or distal owner')
        if len(obj.modifiers) != 0:
            fail(f'{name}: unexpected modifiers; source topology needs explicit review')
        if len(obj.data.uv_layers) != 0:
            fail(f'{name}: unexpected UV topology; refusing lossy mesh reconstruction')
        source_native_signature[name] = mesh_signature(obj)

    for obj in bpy.data.objects:
        if obj.type == 'EMPTY':
            source_pivots[obj.name] = transform_snapshot(obj)
    source_mesh_signatures = {obj.name: mesh_signature(obj) for obj in bpy.data.objects
                              if obj.type == 'MESH' and obj.name not in TALON_NAMES}
    source_glb_summary = parse_glb(SOURCE_GLB)
    source_glb_by_name = {row['name']: row for row in source_glb_summary['meshes']}
    for name in TALON_NAMES:
        if name not in source_glb_by_name:
            fail(f'c8 exported GLB does not expose expected talon primitive {name}')

    script_bytes = Path(__file__).resolve().read_bytes()
    OUT.mkdir(parents=True, exist_ok=False)
    SCRIPT_SNAPSHOT.write_bytes(script_bytes)
    script_record = file_record(SCRIPT_SNAPSHOT)
    talon_results = []
    source_mesh_count = sum(obj.type == 'MESH' for obj in bpy.data.objects)
    source_non_mesh_count = len(bpy.data.objects) - source_mesh_count

    for name in TALON_NAMES:
        obj = source_objects[name]
        mesh = obj.data
        rings, end_set, transitions = find_rings(obj)
        original_coords = [vertex.co.copy() for vertex in mesh.vertices]
        original_world = [obj.matrix_world @ co for co in original_coords]
        centers = [sum((original_world[i] for i in ring), Vector()) / RING_SIZE for ring in rings]
        original_centerline = [tuple(float(c) for c in center) for center in centers]
        if len(rings) != RING_COUNT or len(rings[0]) != RING_SIZE:
            fail(f'{name}: unexpected derived ring dimensions')
        if rings[-1] and set(rings[-1]) != end_set:
            fail(f'{name}: terminal cap changed during ring derivation')

        # Capture all original face material/smoothing attributes and split only
        # the 13->14 quad interval by inserting the exact original-surface ring
        # at t=.85. This makes every point at and beyond .85 geometrically exact.
        old_faces = [list(poly.vertices) for poly in mesh.polygons]
        old_smooth = [poly.use_smooth for poly in mesh.polygons]
        old_materials = [poly.material_index for poly in mesh.polygons]
        ring13, ring14 = rings[13], rings[14]
        transition13 = transitions[13]
        alpha = (0.85 - 13.0 / 16.0) / (14.0 / 16.0 - 13.0 / 16.0)
        if abs(alpha - .6) > 1e-12:
            fail('ring interpolation fraction changed unexpectedly')
        mid_world_local = build_ribbon_insert(original_coords, ring13, ring14, transition13, alpha)
        new_vertices = list(original_coords)
        mid_index = {}
        for vertex in ring13:
            mid_index[vertex] = len(new_vertices)
            new_vertices.append(mid_world_local[vertex])

        # Compute deformed vertices for the existing proximal rings. A smooth
        # fade reaches the exact original profile at t=.85 without moving any
        # section centerline or exceeding its lateral/ventral envelope.
        changed_original = set()
        ring_after_recenter = []
        for ring_i in range(14):
            t = ring_i / 16.0
            if t <= FADE_START:
                weight = 1.0
            elif t >= FADE_END:
                weight = 0.0
            else:
                weight = 1.0 - smoothstep((t - FADE_START) / (FADE_END - FADE_START))
            if weight <= 0.0:
                continue
            before = [original_world[i] for i in rings[ring_i]]
            center = centers[ring_i]
            if ring_i == 0:
                tangent = centers[1] - centers[0]
            else:
                tangent = centers[ring_i + 1] - centers[ring_i - 1]
            new_local = deform_section(obj, rings[ring_i], center, tangent, weight)
            for index, local_co in new_local.items():
                if (local_co - original_coords[index]).length > 1e-9:
                    changed_original.add(index)
                new_vertices[index] = local_co
            # Ring centers are recorded and revalidated after the mesh rebuild.
            ring_after_recenter.append(ring_i)

        split_faces = []
        split_smooth, split_materials = [], []
        kept_faces, kept_smooth, kept_materials = [], [], []
        r13_set, r14_set = set(ring13), set(ring14)
        for face, smooth, material_index in zip(old_faces, old_smooth, old_materials):
            if len(face) == 4 and sum(v in r13_set for v in face) == 2 and sum(v in r14_set for v in face) == 2:
                oriented = False
                for j in range(4):
                    a, b, c, d = face[j], face[(j + 1) % 4], face[(j + 2) % 4], face[(j + 3) % 4]
                    if a in r13_set and b in r13_set and c in r14_set and d in r14_set:
                        if transition13.get(a) != d or transition13.get(b) != c:
                            fail(f'{name}: section split cannot preserve source quad correspondence')
                        split_faces.extend(([a, b, mid_index[b], mid_index[a]],
                                            [mid_index[a], mid_index[b], c, d]))
                        split_smooth.extend((smooth, smooth))
                        split_materials.extend((material_index, material_index))
                        oriented = True
                        break
                if not oriented:
                    fail(f'{name}: cannot orient source face for exact t=.85 insert')
            else:
                kept_faces.append(face)
                kept_smooth.append(smooth)
                kept_materials.append(material_index)
        if len(split_faces) != 32 or len(kept_faces) != len(old_faces) - 16:
            fail(f'{name}: expected 16 split quads, found {len(split_faces) // 2}')
        all_faces = kept_faces + split_faces
        all_smooth = kept_smooth + split_smooth
        all_materials = kept_materials + split_materials
        if len(all_faces) != len(all_smooth) or len(all_faces) != len(all_materials):
            fail(f'{name}: reconstructed face metadata count mismatch')
        materials = list(mesh.materials)
        mesh_data_from_poly(mesh, new_vertices, all_faces, materials, all_smooth, all_materials)
        bpy.context.view_layer.update()

        # In-memory bounded-shape checks, retaining source ring index layout.
        now_world = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
        unchanged_terminal = True
        for ring_i in range(14, RING_COUNT):
            for index in rings[ring_i]:
                if (now_world[index] - original_world[index]).length > 1e-8:
                    unchanged_terminal = False
        if not unchanged_terminal:
            fail(f'{name}: terminal source rings moved')
        center_errors = []
        lateral_overruns = []
        lower_overruns = []
        for ring_i, ring in enumerate(rings):
            before_center = centers[ring_i]
            after_center = sum((now_world[i] for i in ring), Vector()) / RING_SIZE
            center_errors.append((after_center - before_center).length)
            old_x = max(abs((original_world[i] - before_center).x) for i in ring)
            old_min_z = min(original_world[i].z for i in ring)
            for index in ring:
                lateral_overruns.append(abs((now_world[index] - before_center).x) - old_x)
                lower_overruns.append(old_min_z - now_world[index].z)
        if max(center_errors) > 2e-7:
            fail(f'{name}: section reshaping shifted a sampled centerline')
        if max(lateral_overruns) > 2e-7:
            fail(f'{name}: talon lateral envelope enlarged')
        if max(lower_overruns) > 2e-7:
            fail(f'{name}: talon ventral envelope extended downward')
        if any(not all(math.isfinite(float(c)) for c in vertex.co) for vertex in mesh.vertices):
            fail(f'{name}: non-finite vertex after deformation')
        if (now_world[rings[-1][0]] - original_world[rings[-1][0]]).length > 1e-8:
            fail(f'{name}: final tip-ring vertex moved')
        expected_parent = source_parts[name]['parent']
        if obj.parent.name != expected_parent:
            fail(f'{name}: distal parent changed')
        glb_source_mesh = source_glb_by_name[name]
        source_triangles = sum(p['triangleCount'] or 0 for p in glb_source_mesh['primitives'])
        talon_results.append({
            'name': name,
            'parent': obj.parent.name,
            'region': obj.get('region'), 'role': obj.get('surfaceRole'),
            'sourceMeshSha256': source_native_signature[name],
            'sourceTopology': {'vertices': len(original_coords), 'faces': len(old_faces),
                               'rings': len(rings), 'verticesPerRing': RING_SIZE,
                               'facesPerInterval': RING_SIZE},
            'profile': {'ventralSuperellipsePower': VENTRAL_POWER,
                        'dorsalSuperellipsePower': DORSAL_POWER,
                        'fadeFromT': FADE_START, 'fadeToExactSourceT': FADE_END,
                        'modifiedExistingRingIndices': ring_after_recenter,
                        'sourceTerminalRingIndicesPreserved': list(range(14, 17)),
                        'insertedExactSourceSurfaceRingT': .85},
            'changedOriginalVertexRanges': compress_indices(sorted(changed_original)),
            'addedVertexRange': [len(original_coords), len(new_vertices) - 1],
            'centerlineMaxError': max(center_errors),
            'maxLateralEnvelopeOverrun': max(lateral_overruns),
            'maxVentralEnvelopeOverrun': max(lower_overruns),
            'terminalRingsExact': unchanged_terminal,
            '_terminalCoordinates': [(i, tuple(float(c) for c in original_coords[i]))
                                     for ring in rings[14:] for i in ring],
            'rootAndTipCenterlineBefore': [original_centerline[0], original_centerline[-1]],
            'sourceExport': {'meshName': name, 'triangles': source_triangles,
                             'vertexCount': sum(p['attributes'].get('POSITION', {}).get('count', 0)
                                                for p in glb_source_mesh['primitives'])},
        })

    # Build exact scene and mesh checks from source snapshots, then save the
    # editable native fork before producing the runtime derivative.
    source_objects = {obj.name: obj for obj in bpy.data.objects}
    source_mesh_signatures = {obj.name: mesh_signature(obj) for obj in bpy.data.objects
                              if obj.type == 'MESH' and obj.name not in TALON_NAMES}
    source_pivots = {obj.name: transform_snapshot(obj) for obj in bpy.data.objects if obj.type == 'EMPTY'}
    if sum(obj.type == 'MESH' for obj in bpy.data.objects) != source_mesh_count:
        fail('object count changed during mesh-only talon editing')
    if len(bpy.data.objects) - source_mesh_count != source_non_mesh_count:
        fail('non-mesh scene object count changed')
    bpy.context.preferences.filepaths.save_version = 0
    pending_native = OUT / '.building-talon-study.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(pending_native))
    pending_native.replace(NATIVE_OUT)

    # Re-open the saved fork and verify that all non-talon meshes and pivots
    # survived native serialization unchanged before export.
    bpy.ops.wm.open_mainfile(filepath=str(NATIVE_OUT))
    current = {obj.name: obj for obj in bpy.data.objects}
    if set(source_mesh_signatures) - set(current):
        fail('saved fork lost one or more unchanged meshes')
    unchanged_meshes = []
    for name, signature in source_mesh_signatures.items():
        obj = current[name]
        if obj.type != 'MESH' or mesh_signature(obj) != signature:
            fail(f'non-talon mesh changed during native save: {name}')
        unchanged_meshes.append(name)
    current_pivots = {obj.name: transform_snapshot(obj) for obj in bpy.data.objects if obj.type == 'EMPTY'}
    if set(current_pivots) != set(source_pivots):
        fail('saved fork changed the pivot/empty inventory')
    for name, before in source_pivots.items():
        if not transform_snapshot_equal(before, current_pivots[name]):
            fail(f'pivot transform changed during native save: {name}')
    post_save_terminal_checks = []
    for item in talon_results:
        obj = current[item['name']]
        rings, _, _ = find_rings_with_inserted_t85(obj)
        if len(rings) != 18:
            fail(f'{obj.name}: saved fork lost its t=.85 exact ring')
        original_tal_terminal = item['_terminalCoordinates']
        if any((obj.data.vertices[i].co - Vector(co)).length > 1e-8
               for i, co in original_tal_terminal):
            fail(f'{obj.name}: saved fork changed a terminal source ring vertex')
        post_save_terminal_checks.append({'name': obj.name, 'terminalRingExact': True,
                                          'ringsAfterInsert': len(rings)})
        item.pop('_terminalCoordinates', None)

    # Export from the saved native fork, matching the production exporter
    # contract: apply evaluated geometry, select MESH/EMPTY only, no cameras.
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.type in {'MESH', 'EMPTY'}:
            obj.hide_set(False)
            obj.select_set(True)
    if bpy.context.view_layer.objects.active is None:
        fail('no active mesh/empty for GLB export')
    pending_glb = OUT / '.building-talon-study.glb'
    result = bpy.ops.export_scene.gltf(filepath=str(pending_glb), export_format='GLB',
                                       use_selection=True, export_yup=True, export_apply=True,
                                       export_extras=True, export_cameras=False,
                                       export_lights=False, export_animations=True,
                                       export_animation_mode='ACTIONS', export_frame_range=True)
    if 'FINISHED' not in result or not pending_glb.is_file():
        fail(f'GLB export did not finish: {result}')
    pending_glb.replace(GLB_OUT)
    output_glb_summary = parse_glb(GLB_OUT)
    output_glb_by_name = {row['name']: row for row in output_glb_summary['meshes']}
    for item in talon_results:
        name = item['name']
        if name not in output_glb_by_name:
            fail(f'exported GLB lacks changed talon mesh {name}')
        mesh = output_glb_by_name[name]
        item['outputExport'] = {
            'meshName': name,
            'primitives': mesh['primitives'],
            'triangles': sum(p['triangleCount'] or 0 for p in mesh['primitives']),
            'positionVertexCount': sum(p['attributes'].get('POSITION', {}).get('count', 0)
                                       for p in mesh['primitives']),
            'positionBounds': [p['attributes']['POSITION'] for p in mesh['primitives']
                               if 'POSITION' in p['attributes']],
        }
    source_by_name = {row['name']: row for row in source_glb_summary['meshes']}
    unchanged_export_names = sorted(set(source_by_name) - set(TALON_NAMES))
    missing_export = sorted(set(unchanged_export_names) - set(output_glb_by_name))
    if missing_export:
        fail(f'GLB export lost non-talon meshes: {missing_export[:8]}')
    unchanged_export_comparison = []
    for name in unchanged_export_names:
        source_mesh, output_mesh = source_by_name[name], output_glb_by_name[name]
        source_prims, output_prims = source_mesh['primitives'], output_mesh['primitives']
        counts_exact = len(source_prims) == len(output_prims) and all(
            a['triangleCount'] == b['triangleCount'] and
            a['attributes'].get('POSITION', {}).get('count') == b['attributes'].get('POSITION', {}).get('count')
            for a, b in zip(source_prims, output_prims))
        bounds_exact = len(source_prims) == len(output_prims) and all(
            a['attributes'].get('POSITION', {}).get('min') == b['attributes'].get('POSITION', {}).get('min') and
            a['attributes'].get('POSITION', {}).get('max') == b['attributes'].get('POSITION', {}).get('max')
            for a, b in zip(source_prims, output_prims))
        payloads_exact = source_mesh == output_mesh
        unchanged_export_comparison.append({'name': name, 'primitiveCountsAndVertexCountsExact': counts_exact,
                                            'positionBoundsExact': bounds_exact,
                                            'allPrimitivePayloadHashesExact': payloads_exact})

    # Report actual source/output identities and bounded invariants.
    output_mesh_signatures = {obj.name: mesh_signature(obj) for obj in bpy.data.objects
                              if obj.type == 'MESH' and obj.name not in TALON_NAMES}
    if output_mesh_signatures != source_mesh_signatures:
        fail('post-export scene contains an unmodified-region mesh mismatch')
    final_native_sha = sha256(NATIVE_OUT)
    final_glb_sha = sha256(GLB_OUT)
    manifest = {
        'status': 'local talon profile study; visual/contact review pending',
        'scope': 'Only the six existing distal talon sheath meshes; no knuckle, hinge, guard, joint, pivot, or other region changes.',
        'source': source_records,
        'sourceNativeSha256Required': EXPECTED_NATIVE_SHA,
        'sourceExportSha256Required': EXPECTED_GLB_SHA,
        'executedScriptSnapshot': script_record,
        'profileMethod': {
            'description': 'Topology-derived swept rings; subtle asymmetric D/teardrop superellipse on proximal profile, smoothly returning to exact source surface at t=.85.',
            'ventralPower': VENTRAL_POWER, 'dorsalPower': DORSAL_POWER,
            'centerlineSamplesPreserved': True,
            'ringDerivation': 'Two 16-vertex cap faces and 16 side-quads per ring interval; cyclic correspondence followed through native quad topology, no hard-coded vertex ring indices.',
            'sourceRings': RING_COUNT, 'verticesPerRing': RING_SIZE,
            'terminal15PercentExact': True,
            'interpolatedBoundaryT': .85,
            'lateralEnvelopeExpanded': False,
            'ventralEnvelopeExtended': False,
        },
        'changedTalons': talon_results,
        'pivotCheck': {'sourceEmptyCount': len(source_pivots), 'outputEmptyCount': len(current_pivots),
                       'allParentsAndLocalWorldTransformsExact': True},
        'unmodifiedNativeMeshes': {'count': len(unchanged_meshes), 'allGeometrySignaturesExact': True,
                                   'meshNamesSha256': hashlib.sha256('\n'.join(sorted(unchanged_meshes)).encode()).hexdigest()},
        'unmodifiedExportMeshes': {'sourceMeshCount': len(source_by_name),
                                   'outputMeshCount': len(output_glb_by_name),
                                   'checkedNonTalonMeshCount': len(unchanged_export_names),
                                   'exactPrimitivePayloadMatchCount': sum(row['allPrimitivePayloadHashesExact'] for row in unchanged_export_comparison),
                                   'exactPrimitiveCountAndVertexCountMatchCount': sum(row['primitiveCountsAndVertexCountsExact'] for row in unchanged_export_comparison),
                                   'exactPositionBoundsMatchCount': sum(row['positionBoundsExact'] for row in unchanged_export_comparison),
                                   'comparison': unchanged_export_comparison},
        'savedForkTerminalChecks': post_save_terminal_checks,
        'sceneCounts': {'sourceNativeMeshes': source_mesh_count,
                        'outputNativeMeshes': sum(obj.type == 'MESH' for obj in bpy.data.objects),
                        'sourceOutputGLBMeshes': len(source_by_name),
                        'studyOutputGLBMeshes': len(output_glb_by_name)},
        'outputs': {
            'native': {'path': NATIVE_OUT.relative_to(ROOT).as_posix(), 'bytes': NATIVE_OUT.stat().st_size, 'sha256': final_native_sha},
            'glb': {'path': GLB_OUT.relative_to(ROOT).as_posix(), 'bytes': GLB_OUT.stat().st_size, 'sha256': final_glb_sha},
        },
        'limitations': [
            'Authored geometric study only; no source dimensional metrology or final-likeness approval.',
            'No grip-force, load-bearing, traction, or physical contact certification.',
            'Changed cross-section may affect side contact/collision within the existing tip envelope; root owns contact retesting.',
            'Terminal source geometry, sampled centerlines, endpoint reach, and all joint pivots are preserved by checks recorded here.',
        ],
    }
    MANIFEST_OUT.write_text(json.dumps(manifest, indent=2) + '\n')
    manifest_record = file_record(MANIFEST_OUT)
    print(json.dumps({'status': manifest['status'], 'sourceNativeSha256': EXPECTED_NATIVE_SHA,
                      'sourceExportSha256': EXPECTED_GLB_SHA, 'native': manifest['outputs']['native'],
                      'glb': manifest['outputs']['glb'], 'manifest': manifest_record,
                      'changedTalons': [{'name': item['name'], 'sourceTriangles': item['sourceExport']['triangles'],
                                         'outputTriangles': item['outputExport']['triangles'],
                                         'bounds': item['outputExport']['positionBounds']}
                                        for item in talon_results],
                      'unchangedNativeMeshCount': len(unchanged_meshes),
                      'unchangedExportMeshCount': len(unchanged_export_names)}, indent=2))


def compress_indices(indices: list[int]) -> list[list[int]]:
    if not indices:
        return []
    ranges = []
    start = previous = indices[0]
    for value in indices[1:]:
        if value != previous + 1:
            ranges.append([start, previous])
            start = value
        previous = value
    ranges.append([start, previous])
    return ranges


def find_rings_with_inserted_t85(obj) -> tuple[list[list[int]], set[int], dict[int, int]]:
    """Verify the saved 18-ring mesh, reusing topology-derived adjacent rings."""
    mesh = obj.data
    caps = [list(poly.vertices) for poly in mesh.polygons if len(poly.vertices) == RING_SIZE]
    if len(caps) != 2:
        fail(f'{obj.name}: saved talon does not have two 16-vertex caps')
    centers_y = [sum((obj.matrix_world @ mesh.vertices[i].co).y for i in cap) / RING_SIZE for cap in caps]
    start = caps[max(range(2), key=lambda i: centers_y[i])]
    end = set(caps[min(range(2), key=lambda i: centers_y[i])])
    quads = [list(poly.vertices) for poly in mesh.polygons if len(poly.vertices) == 4]
    rings = [start]
    current = start
    seen = set(current)
    for _ in range(17):
        mapping = {}
        for k, a in enumerate(current):
            b = current[(k + 1) % RING_SIZE]
            matches = []
            for quad in quads:
                for j in range(4):
                    if {quad[j], quad[(j + 1) % 4]} == {a, b}:
                        matches.append(quad)
                        break
            matches = [quad for quad in matches
                       if not (set(quad) - {a, b}) & seen]
            if len(matches) != 1:
                fail(f'{obj.name}: saved ring has {len(matches)} outward transitions at {a}/{b}')
            quad = matches[0]
            for j in range(4):
                qa, qb = quad[j], quad[(j + 1) % 4]
                if qa == a and qb == b:
                    mapping[a], mapping[b] = quad[(j + 3) % 4], quad[(j + 2) % 4]
                    break
                if qa == b and qb == a:
                    mapping[a], mapping[b] = quad[(j + 2) % 4], quad[(j + 3) % 4]
                    break
        nxt = [mapping.get(i, -1) for i in current]
        if any(i < 0 for i in nxt) or len(set(nxt)) != RING_SIZE or set(nxt) & seen:
            fail(f'{obj.name}: invalid saved ring transition')
        rings.append(nxt)
        seen.update(nxt)
        current = nxt
        if set(current) == end:
            break
    if set(rings[-1]) != end or len(rings) != 18:
        fail(f'{obj.name}: saved exact t=.85 ring topology not found')
    return rings, end, {}


if __name__ == '__main__':
    # Blender executes scripts with __name__ == '__main__'. The immutable QA
    # native is opened by the runner below only after source file hashes pass.
    if not SOURCE_BLEND.is_file() or sha256(SOURCE_BLEND) != EXPECTED_NATIVE_SHA:
        fail('immutable QA native SHA validation failed before opening')
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    bpy.context.view_layer.update()
    main()
