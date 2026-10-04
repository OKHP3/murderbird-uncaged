"""Inert FINISH04 crown-only appearance trial. Scene changes occur only in apply.

Surface response is an artistic source-directed experiment, not calibrated
albedo, reconstructed plate geometry, source projection or likeness acceptance.
"""
import hashlib
import json
import math
from pathlib import Path
import struct
import zlib

SOURCE = 'CGH17 frontal crown root'
SUCCESSOR = 'CGRS04 source-scale frontal crown appearance'
UV_NAME = 'head17-normalized-local'
DESIGN = 'design01'
SIZE = 1024
INVENTORY_SHA = 'b4b04546e26e410acdeb43b8490fdc7aae55bebf4bd28847b1b156ad572ecf84'
PLAN_SHA = 'a0b98a3560ee2074b4700c9979367a8a6ab0a807b52b2ddf3b4c978b02030fee'
SOURCE_ROOT = Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
PREP_ROOT = SOURCE_ROOT / 'assets/audit/cg-recursive-three-loop01/loop03-preparation/finish04-corrected'


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _pinned_json(path, expected):
    data = path.read_bytes()
    if _sha(data) != expected:
        raise RuntimeError('Preparation pin changed: ' + str(path))
    return json.loads(data)


def _png(values):
    """Numeric RGB bytes; bpy UV rows run bottom to top, PNG top to bottom."""
    import numpy as np
    rgb = np.rint(np.clip(values, 0, 1) * 255).astype('uint8')
    h, w, _ = rgb.shape
    def chunk(tag, payload):
        return struct.pack('>I', len(payload)) + tag + payload + struct.pack('>I', zlib.crc32(tag + payload) & 0xffffffff)
    rows = b''.join(b'\x00' + row.tobytes() for row in rgb[::-1])
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(rows, 9)) + chunk(b'IEND', b'')


def _atlas(mesh):
    """Actual cage triangles produce local-position and UV tangent charts.

    Work on the successor mesh, leaving the receiving mesh's caches untouched.
    The chart is not assumed rectangular or aligned to image U/V directions.
    """
    import numpy as np
    mesh.calc_loop_triangles()
    uv = mesh.uv_layers[UV_NAME].data
    positions = np.zeros((SIZE, SIZE, 3), dtype=float)
    tangent = np.zeros_like(positions)
    bitangent = np.zeros_like(positions)
    covered = np.zeros((SIZE, SIZE), dtype=bool)
    overlap = 0
    conflicts = 0
    mirror_overlap = 0
    tangent_conflicts = 0
    degenerate_uv = 0
    degenerate_geometry = 0
    for tri in mesh.loop_triangles:
        q = np.array([uv[i].uv[:] for i in tri.loops], dtype=float)
        p = np.array([mesh.vertices[i].co[:] for i in tri.vertices], dtype=float)
        e = np.column_stack((q[1] - q[0], q[2] - q[0]))
        determinant = float(np.linalg.det(e))
        if abs(determinant) < 1e-12:
            degenerate_uv += 1
            continue
        if np.linalg.norm(np.cross(p[1] - p[0], p[2] - p[0])) < 1e-12:
            degenerate_geometry += 1
            continue
        low = np.maximum(0, np.floor(q.min(axis=0) * SIZE - .5).astype(int))
        high = np.minimum(SIZE - 1, np.ceil(q.max(axis=0) * SIZE - .5).astype(int))
        if (high < low).any():
            continue
        xx, yy = np.meshgrid(np.arange(low[0], high[0] + 1), np.arange(low[1], high[1] + 1))
        coords = np.stack(((xx + .5) / SIZE, (yy + .5) / SIZE), axis=-1)
        bary = (coords - q[0]) @ np.linalg.inv(e).T
        inside = (bary[..., 0] >= -1e-8) & (bary[..., 1] >= -1e-8) & (bary.sum(axis=-1) <= 1 + 1e-8)
        x, y = xx[inside], yy[inside]
        local = p[0] + bary[inside, 0, None] * (p[1] - p[0]) + bary[inside, 1, None] * (p[2] - p[0])
        previous = covered[y, x]
        overlap += int(previous.sum())
        old_position = positions[y[previous], x[previous]].copy()
        new_position = local[previous].copy()
        raw_delta = np.linalg.norm(old_position - new_position, axis=1)
        old_position[:, 0] = np.abs(old_position[:, 0])
        new_position[:, 0] = np.abs(new_position[:, 0])
        mirror_equivalent = np.linalg.norm(old_position - new_position, axis=1) <= .001
        mirror_overlap += int(((raw_delta > .001) & mirror_equivalent).sum())
        conflicts += int((~mirror_equivalent).sum())
        dp = np.column_stack((p[1] - p[0], p[2] - p[0])) @ np.linalg.inv(e)
        t = dp[:, 0] / np.linalg.norm(dp[:, 0])
        n = np.cross(p[1] - p[0], p[2] - p[0]); n /= np.linalg.norm(n)
        b = np.cross(n, t)
        if np.dot(b, dp[:, 1]) < 0:
            b = -b
        if previous.any():
            tangent_conflicts += int(((np.abs(tangent[y[previous], x[previous], 1] - t[1]) > .02) | (np.abs(bitangent[y[previous], x[previous], 1] - b[1]) > .02)).sum())
        positions[y, x], tangent[y, x], bitangent[y, x] = local, t, b
        covered[y, x] = True
    if conflicts or tangent_conflicts:
        raise RuntimeError('Ambiguous non-mirror chart/tangent mapping: ' + str({'position': conflicts, 'tangent': tangent_conflicts}))
    if covered.sum() < SIZE * SIZE * .02:
        raise RuntimeError('Unexpectedly small crown UV chart')
    edge_counts = {}
    for face in mesh.polygons:
        for edge in face.edge_keys:
            key = tuple(sorted(edge)); edge_counts[key] = edge_counts.get(key, 0) + 1
    boundary = [key for key, count in edge_counts.items() if count == 1]
    if not boundary:
        raise RuntimeError('No actual open crown boundary; refuse invented edge mask')
    distance = np.full((SIZE, SIZE), float('inf'))
    pc = positions[covered]
    dc = np.full(len(pc), float('inf'))
    for i, j in boundary:
        a, b = np.array(mesh.vertices[i].co[:]), np.array(mesh.vertices[j].co[:])
        v = b - a
        factor = np.clip((pc - a) @ v / np.dot(v, v), 0, 1)
        dc = np.minimum(dc, np.linalg.norm(pc - a - factor[:, None] * v, axis=1))
    distance[covered] = dc
    return positions, tangent, bitangent, covered, distance, {'covered_texels': int(covered.sum()), 'overlap_texels': overlap, 'conflicting_texels': conflicts, 'mirror_equivalent_overlap_texels': mirror_overlap, 'tangent_conflicting_texels': tangent_conflicts, 'boundary_segments': len(boundary), 'cage_triangles': len(mesh.loop_triangles), 'degenerate_uv_triangles': degenerate_uv, 'degenerate_geometry_triangles': degenerate_geometry, 'overlap_handling': 'Same physical point or x-mirror within .001 local units allowed only with projected tangent-y agreement within .02; all other overlap fails before map writing; degenerates skipped and counted. Left/right material response deliberately equivalent under held y/z projection'}


def _maps(mesh, era):
    import numpy as np
    p, t, b, covered, distance, receipt = _atlas(mesh)
    vertices = np.array([v.co[:] for v in mesh.vertices])
    span = np.ptp(vertices, axis=0)
    if min(span) <= 0:
        raise RuntimeError('Degenerate crown local coordinate range')
    # Longitudinal sweep and lateral regionalization use physical cage positions.
    course = (p[..., 1] - vertices[:, 1].min()) / span[1]
    lateral = np.abs(p[..., 0]) / max(abs(vertices[:, 0]).max(), 1e-9)
    sweep = course + .11 * lateral * lateral
    bands = .5 + .5 * np.sin(2 * np.pi * (2.4 * sweep + .12))
    # Broad regional mask, not uniform noise or a global palette multiplier.
    slate_region = np.clip(.65 * (1 - lateral * lateral) + .23 * np.sin(np.pi * course), 0, 1)
    interruption = .3 + .7 * np.clip(.5 + .5 * np.sin(2 * np.pi * (4.2 * course + 1.1 * lateral)), 0, 1)
    edge = np.exp(-np.square(distance / .004)) * interruption
    # Authored sRGB hypotheses: source photographs are not calibrated albedo.
    colors = {
        'maker': ((.36, .33, .26), (.245, .285, .30), (.56, .45, .29), .48, .035, 3.5),
        'mechanic': ((.32, .285, .205), (.225, .26, .265), (.48, .37, .225), .61, .045, 5.5),
        'builder': ((.345, .30, .225), (.255, .285, .29), (.51, .395, .24), .56, .045, 4.5),
    }
    brass, slate, rubbed, face_roughness, rough_band, angle = colors[era]
    base = np.array(brass) * (1 - slate_region[..., None]) + np.array(slate) * slate_region[..., None]
    base += (bands[..., None] - .5) * np.array((.055, .043, .025))
    base = base * (1 - .75 * edge[..., None]) + np.array(rubbed) * .75 * edge[..., None]
    rough = np.clip(face_roughness + rough_band * (bands - .5) * 2, .45, .68)
    rough = rough * (1 - edge) + (.32 if era == 'maker' else .38) * edge
    orm = np.stack((np.ones_like(rough), rough, np.full_like(rough, .92)), axis=-1)
    # Coarse formed-sheet response. Local y direction projected into each chart's
    # own UV tangent basis; no geometric displacement and no fake seam cavity.
    wave = np.sin(2 * np.pi * (2.4 * sweep + .12)) * (1 - .55 * edge)
    amplitude = math.tan(math.radians(angle)) * wave
    nx = amplitude * t[..., 1]
    ny = amplitude * b[..., 1]
    normal = np.stack((nx, ny, np.ones_like(nx)), axis=-1)
    normal /= np.linalg.norm(normal, axis=-1)[..., None]
    normal = normal * .5 + .5
    # Safe 24px gutter dilation around actual islands, without rectangular masks.
    valid = covered.copy()
    for _ in range(24):
        old = valid.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            shifted = np.roll(old, (dy, dx), (0, 1))
            if dy > 0: shifted[:dy] = False
            if dy < 0: shifted[dy:] = False
            if dx > 0: shifted[:, :dx] = False
            if dx < 0: shifted[:, dx:] = False
            take = shifted & ~valid
            for image in (base, orm, normal):
                image[take] = np.roll(image, (dy, dx), (0, 1))[take]
            valid[take] = True
    base[~valid] = brass; orm[~valid] = (1, face_roughness, .92); normal[~valid] = (.5, .5, 1)
    receipt.update(local_bounds=[vertices.min(axis=0).tolist(), vertices.max(axis=0).tolist()], normal_max_design_degrees=angle, roughness_min=float(rough[covered].min()), roughness_max=float(rough[covered].max()), edge_width_local=.004, chart_uv=UV_NAME, physical_course_axis='local y plus lateral curvature')
    return {'basecolor': base, 'orm': orm, 'normal': normal}, receipt


def _image(bpy, out, role, values, era):
    path = out / ('cgrs04-' + era + '-' + DESIGN + '-' + role + '.png')
    payload = _png(values)
    if path.exists() and path.read_bytes() != payload:
        raise RuntimeError('Frozen map bytes differ: ' + str(path))
    if not path.exists():
        path.write_bytes(payload)
    im = bpy.data.images.load(str(path.resolve()), check_existing=False)
    im.name = 'CGRS04 ' + era + ' ' + DESIGN + ' ' + role
    im.colorspace_settings.name = 'sRGB' if role == 'basecolor' else 'Non-Color'
    im.pack()
    if _sha(im.packed_file.data) != _sha(payload):
        raise RuntimeError('Packed map differs from authored bytes')
    return im, {'role': role, 'name': im.name, 'path': str(path), 'sha256': _sha(payload), 'colorspace': im.colorspace_settings.name}


def apply(scene, root_path, era):
    """Explicit dispatch entry point. Never called by import or command line."""
    import bpy
    if era not in ('maker', 'mechanic', 'builder'):
        raise ValueError('Unknown era: ' + str(era))
    _pinned_json(PREP_ROOT / 'plan.json', PLAN_SHA)
    inventory = _pinned_json(PREP_ROOT / 'cg-finish04-entry-inventory.json', INVENTORY_SHA)
    entry = next(e for e in inventory['eras'] if e['era'] == era)
    target = next(o for o in entry['targets'] if o['object'] == SOURCE)
    source = scene.objects.get(SOURCE)
    if source is None or SUCCESSOR in bpy.data.objects:
        raise RuntimeError('Missing source or successor already exists')
    mesh = source.data
    if len(mesh.polygons) != 56 or any(f.material_index != 2 for f in mesh.polygons) or mesh.uv_layers.active.name != UV_NAME:
        raise RuntimeError('Incoming crown cage or UV differs from pinned entry')
    if len(source.material_slots) != len(target['slots']) or source.material_slots[2].material.name != target['slots'][2]['name']:
        raise RuntimeError('Exact current crown material differs from pinned entry')
    if any(slot.link != 'DATA' for slot in source.material_slots):
        raise RuntimeError('Incoming crown slots are not pinned DATA bindings')
    if source.hide_render or source.hide_get() or source.hide_viewport:
        raise RuntimeError('Incoming crown is not current visible crown')
    for slot in target['slots']:
        actual = source.material_slots[slot['index']].material
        for expected in slot['images']:
            node = actual.node_tree.nodes.get(expected['node'])
            if node is None or node.image is None or not node.image.packed_file or _sha(node.image.packed_file.data) != expected['bytes_sha256']:
                raise RuntimeError('Incoming crown original image binding changed')
    # Exact mesh copy has unchanged slots/UV/face assignments except new slot2 graph.
    successor = source.copy(); successor.data = mesh.copy()
    successor.name = SUCCESSOR; successor.data.name = SUCCESSOR + ' exact cage'
    for collection in source.users_collection:
        collection.objects.link(successor)
    for slot in successor.material_slots:
        slot.link = 'DATA'
    material = source.material_slots[2].material.copy()
    material.name = 'CGRS04 ' + era + ' ' + DESIGN + ' formed crown'
    successor.data.materials[2] = material
    maps, chart_receipt = _maps(successor.data, era)
    out = Path(root_path).resolve() / 'assets/models/cg-recursive-finish04-crown' / DESIGN / era
    out.mkdir(parents=True, exist_ok=True)
    images, records = {}, []
    for role, values in maps.items():
        images[role], record = _image(bpy, out, role, values, era); records.append(record)
    # Rebuild only the COPIED graph, using glTF's direct image/Principled paths.
    nt = material.node_tree; nt.nodes.clear()
    output = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    uv = nt.nodes.new('ShaderNodeUVMap'); uv.uv_map = UV_NAME
    textures = {}
    for role, image in images.items():
        tex = nt.nodes.new('ShaderNodeTexImage'); tex.name = 'CGRS04 ' + role; tex.image = image
        tex.extension = 'EXTEND'; tex.interpolation = 'Linear'
        nt.links.new(uv.outputs['UV'], tex.inputs['Vector']); textures[role] = tex
    nt.links.new(textures['basecolor'].outputs['Color'], bsdf.inputs['Base Color'])
    separate = nt.nodes.new('ShaderNodeSeparateColor'); separate.mode = 'RGB'
    nt.links.new(textures['orm'].outputs['Color'], separate.inputs['Color'])
    nt.links.new(separate.outputs['Green'], bsdf.inputs['Roughness'])
    nt.links.new(separate.outputs['Blue'], bsdf.inputs['Metallic'])
    normal = nt.nodes.new('ShaderNodeNormalMap'); normal.space = 'TANGENT'; normal.uv_map = UV_NAME; normal.inputs['Strength'].default_value = 1
    nt.links.new(textures['normal'].outputs['Color'], normal.inputs['Color'])
    nt.links.new(normal.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    successor.hide_render = False; successor.hide_set(False)
    source.hide_render = True; source.hide_set(True)
    bpy.context.view_layer.update()
    evaluated = successor.evaluated_get(bpy.context.evaluated_depsgraph_get())
    evaluated_mesh = evaluated.to_mesh()
    try:
        if len(evaluated_mesh.polygons) != 1912 or any(f.material_index != 2 for f in evaluated_mesh.polygons) or evaluated_mesh.materials[2] != material:
            raise RuntimeError('Evaluated DATA material/crown topology does not match')
        proof = {'faces': len(evaluated_mesh.polygons), 'slot': 2, 'material': evaluated_mesh.materials[2].name, 'link': successor.material_slots[2].link, 'uv': successor.data.uv_layers.active.name, 'maps': records}
    finally:
        evaluated.to_mesh_clear()
    return {'module': 'cg-recursive-finish04-crown', 'design': DESIGN, 'era': era, 'newMeshes': [successor.name], 'hideOverrides': [{'name': SOURCE, 'hide_render': True, 'hide_set': True, 'hide_viewport': source.hide_viewport}], 'materials': [material.name], 'newMaps': records, 'chart': chart_receipt, 'evaluatedBinding': proof, 'sourceNativeExpectedSha256': entry['native_sha256'], 'limits': ['Appearance experiment; no geometry or cavity repair', 'Whole neutral/workshop gain untested until actual dispatch', 'Owner likeness acceptance remains pending']}
