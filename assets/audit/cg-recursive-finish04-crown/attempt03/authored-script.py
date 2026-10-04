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
DESIGN = 'uv-method02-visual01'
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


def _maps(mesh, era):
    """UV-only hypothesis: all aliases receive identical authored response.

    Actual triangle union establishes coverage, not unique physical ownership.
    No local-3D interpolation, physical edge attribution or old threshold repair.
    """
    import numpy as np
    mesh.calc_loop_triangles()
    uv = mesh.uv_layers[UV_NAME].data
    covered = np.zeros((SIZE, SIZE), dtype=bool)
    multiplicity = np.zeros((SIZE, SIZE), dtype=np.uint16)
    degenerate = 0
    for tri in mesh.loop_triangles:
        q = np.array([uv[i].uv[:] for i in tri.loops], dtype=float)
        e = np.column_stack((q[1] - q[0], q[2] - q[0]))
        if abs(float(np.linalg.det(e))) < 1e-12:
            degenerate += 1
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
        covered[y, x] = True
        multiplicity[y, x] += 1
    if covered.sum() < SIZE * SIZE * .02:
        raise RuntimeError('Unexpectedly small actual crown chart union')
    u, v = np.meshgrid((np.arange(SIZE) + .5) / SIZE, (np.arange(SIZE) + .5) / SIZE)
    phase = 2 * np.pi * (2.25 * u + .18 * v * v + .13)
    band = .5 + .5 * np.sin(phase)
    regional = np.clip(.58 + .28 * np.sin(np.pi * u) - .26 * v + .12 * np.sin(2 * np.pi * (.62 * u + .28 * v)), 0, 1)
    params = {
      'maker': ((.36, .33, .26), (.245, .285, .30), .48, .035, 3.5),
      'mechanic': ((.32, .285, .205), (.225, .26, .265), .61, .045, 5.5),
      'builder': ((.345, .30, .225), (.255, .285, .29), .56, .045, 4.5),
    }
    brass, slate, rough_base, rough_amplitude, angle = params[era]
    base = np.array(brass) * (1 - regional[..., None]) + np.array(slate) * regional[..., None]
    base += (band[..., None] - .5) * np.array((.055, .043, .025))
    rough = np.clip(rough_base + rough_amplitude * np.sin(phase), .45, .68)
    orm = np.stack((np.ones_like(rough), rough, np.full_like(rough, .92)), axis=-1)
    # Derivative of one coarse swept UV height field, encoded directly in
    # tangent-normal coordinates. No physical edge or 3D-tangent claims.
    dhdu = 2.25 * np.cos(phase)
    dhdv = .36 * v * np.cos(phase)
    scale = math.tan(math.radians(angle)) / math.sqrt(2.25 ** 2 + .36 ** 2)
    normal = np.stack((-scale * dhdu, -scale * dhdv, np.ones_like(u)), axis=-1)
    normal /= np.linalg.norm(normal, axis=-1)[..., None]
    normal = normal * .5 + .5
    # UV field is defined across full image, including island gutters; actual
    # coverage is receipt evidence, never an invented physical edge mask.
    receipt = {'method':'UV-only shared-alias field', 'covered_texels':int(covered.sum()), 'multiply_covered_texels':int((multiplicity > 1).sum()), 'maximum_triangle_aliases':int(multiplicity.max()), 'degenerate_uv_triangles':degenerate, 'cage_triangles':len(mesh.loop_triangles), 'chart_uv':UV_NAME, 'normal_max_design_degrees':angle, 'roughness_min':float(rough[covered].min()), 'roughness_max':float(rough[covered].max()), 'physical_edge_wear':False, 'unique_3D_mapping':False, 'limits':'All aliases share UV-function color/roughness/normal response. No independent side wear or actual plate topology claim.'}
    return {'basecolor':base,'orm':orm,'normal':normal},receipt


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
    _pinned_json(PREP_ROOT / 'uv-domain-method02.json', 'a2a9294406db3fdbb6df1ec6994abd9a46283dab599211a34dfad94d355d7cfc')
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
        actual_material = evaluated_mesh.materials[2]
        predicates = {'faces_1912': len(evaluated_mesh.polygons) == 1912, 'all_faces_slot2': all(f.material_index == 2 for f in evaluated_mesh.polygons), 'material_original_identity': actual_material.original == material.original, 'DATA_link': successor.material_slots[2].link == 'DATA'}
        image_proof = {}
        for record in records:
            role = record['role']
            node = actual_material.node_tree.nodes.get('CGRS04 ' + role)
            actual_image = node.image if node is not None else None
            identity = actual_image is not None and actual_image.original == images[role].original
            packed_hash = _sha(actual_image.packed_file.data) if actual_image is not None and actual_image.packed_file else None
            predicates[role + '_original_identity'] = identity
            predicates[role + '_packed_hash'] = packed_hash == record['sha256']
            image_proof[role] = {'original_identity': identity, 'actual_packed_sha256': packed_hash, 'expected_packed_sha256': record['sha256'], 'image': actual_image.name if actual_image else None}
        for name, passed in predicates.items():
            print('CGRS04_EVALUATED_PREDICATE', era, name, passed, flush=True)
        if not all(predicates.values()):
            raise RuntimeError('Evaluated DATA binding predicate failure: ' + json.dumps(predicates))
        proof = {'faces': len(evaluated_mesh.polygons), 'slot': 2, 'material': actual_material.name, 'link': successor.material_slots[2].link, 'uv': successor.data.uv_layers.active.name, 'maps': records, 'predicates': predicates, 'evaluated_images': image_proof}
    finally:
        evaluated.to_mesh_clear()
    return {'module': 'cg-recursive-finish04-crown-uv02', 'design': DESIGN, 'era': era, 'newMeshes': [successor.name], 'hideOverrides': [{'name': SOURCE, 'hide_render': True, 'hide_set': True, 'hide_viewport': source.hide_viewport}], 'materials': [material.name], 'newMaps': records, 'chart': chart_receipt, 'evaluatedBinding': proof, 'sourceNativeExpectedSha256': entry['native_sha256'], 'limits': ['Appearance experiment; no geometry or cavity repair', 'Whole neutral/workshop gain untested until actual dispatch', 'Owner likeness acceptance remains pending']}
