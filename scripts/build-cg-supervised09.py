"""Integrate source-aligned CG modules and freeze reproducible visual evidence.

Development-only authoring. Historical binaries and production runtime stay intact.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--mode', choices=['baseline', 'candidate'], default='candidate')
parser.add_argument('--readable-lighting', action='store_true')
parser.add_argument('--stage', action='store_true')
parser.add_argument('--era', choices=['builder', 'maker', 'mechanic'], default='builder')
parser.add_argument('--attempt', default='attempt09')
parser.add_argument('--final', action='store_true')
parser.add_argument('--export', action='store_true')
parser.add_argument('--resolution', type=int, default=1000)
parser.add_argument('--samples', type=int, default=32)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
AUDIT = ROOT / 'assets/audit/cg-supervised01'
ASSET = ROOT / 'assets/models/cg-supervised01' / (args.attempt if args.mode == 'candidate' else args.attempt + '-' + args.mode)
OUT = AUDIT / (args.attempt if args.mode == 'candidate' else args.attempt + '-' + args.mode) / args.era
OUT.mkdir(parents=True, exist_ok=True)
ASSET.mkdir(parents=True, exist_ok=True)
INPUT = ROOT / 'assets/models/cg-supervised01/attempt06' / f'murderbird-supervised-{args.era}.blend'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
input_sha = sha(INPUT)
EXPECTED={'builder':'72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4','maker':'bda040ce03f1f628850da1744f6ca3359bd6a8f0e496a910347becb5216c622a','mechanic':'9b6006f035896490dab43301ddfde96aee26ec0dcbeca18848d3e43189794acb'}
if input_sha != EXPECTED[args.era]:
    raise RuntimeError('Frozen completed06 era receiving native changed')
if INPUT.stat().st_size < 1000:
    raise RuntimeError('Native input is an unhydrated LFS pointer')
bpy.ops.wm.open_mainfile(filepath=str(INPUT))
scene = bpy.context.scene

def module(name):
    path = ROOT / 'scripts' / name
    spec = importlib.util.spec_from_file_location(path.stem.replace('-', '_'), path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def mesh_digest(obj):
    h = hashlib.sha256()
    h.update(np.asarray(obj.matrix_world, dtype='<f8').tobytes())
    h.update(str(obj.parent.name if obj.parent else None).encode())
    if obj.type == 'MESH':
        for item in obj.data.vertices:
            h.update(np.asarray(item.co[:], dtype='<f4').tobytes())
        for item in obj.data.polygons:
            h.update(np.asarray(item.vertices[:], dtype='<i4').tobytes())
            h.update(int(item.material_index).to_bytes(4, 'little'))
        for layer in obj.data.uv_layers:
            h.update(layer.name.encode())
            for item in layer.data:
                h.update(np.asarray(item.uv[:], dtype='<f4').tobytes())
        h.update(len(obj.data.materials).to_bytes(4, 'little'))
    return h.hexdigest()

preservation = module('cg-supervised-preservation.py')
payload_audit = module('cg-supervised-body12.py')
receiving = {o.name: payload_audit.digest(o) for o in scene.objects if o.type in ('MESH', 'EMPTY')}
receiving_images = preservation.packed_image_snapshot()
receiving_materials = payload_audit.material_digest()
receiving_visibility = {o.name: [o.hide_render, o.hide_viewport, o.hide_get()] for o in scene.objects if o.type in ('MESH', 'EMPTY')}
receipt = {'mode': args.mode, 'era': args.era, 'attempt': args.attempt,
           'input_path': str(INPUT.relative_to(ROOT)), 'input_sha256': input_sha,
           'shared_goal_revision': '251f2f0243181e97140179c2aff6eb057e165438',
           'module_changes': {}, 'artistic_acceptance': 'not claimed',
           'construction_cycle': 9,
           'era_display_name': {'builder': 'Advanced', 'maker': 'Maker', 'mechanic': 'Mechanic'}[args.era],
           'reference_registration': 'estimated, not calibrated',
           'builder_script_sha256': sha(Path(__file__))}
if args.mode == 'candidate':
    # Regional modules are selected only after independent frozen review.
    selection_path = AUDIT / args.attempt / 'selected-modules.json'
    selection = json.loads(selection_path.read_text())
    if not selection.get('root_regional_adjudication_complete'):
        raise RuntimeError('Regional root adjudication is required before integration')
    selected = selection['selected_module_names']
    for item in selection['review_inputs']:
        if sha(ROOT / item['path']) != item['sha256']:
            raise RuntimeError('Pinned regional review input changed: ' + item['path'])
    for name in selected:
        receipt['module_changes'][name] = module(name).apply(scene, ROOT, args.era)
        receipt['module_changes'][name + '-sha256'] = sha(ROOT / 'scripts' / name)
receipt['era_optic_graphs'] = 'Inherited exact completed06 era graphs, replaced optical interior uses same era directly; no shared graph or texture outputs overwritten'

# Material graphs and declared superseded visibility may change; every receiving
# mesh/anchor payload, slot count and polygon material index must remain intact.
changed = [name for name, digest in receiving.items()
           if not scene.objects.get(name) or payload_audit.digest(scene.objects[name]) != digest]
if changed:
    raise RuntimeError('Receiving geometry/UV/indices/transform preservation failed: ' + repr(changed[:10]))
receipt['receiving_preservation'] = {'mesh_and_anchor_count': len(receiving), 'changed': changed}

# Fail cheaply on historical image or material loss before rendering a packet.
if args.mode == 'candidate':
    native = ASSET / f'murderbird-supervised-{args.era}.blend'
    preservation.retain_packed_image_ids(scene)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(native), relative_remap=False)
    bpy.ops.wm.open_mainfile(filepath=str(native))
    scene = bpy.context.scene
    receipt['early_packed_history_save_readback'] = preservation.verify_receiving_images(receiving_images)
    after_materials = payload_audit.material_digest()
    material_changes = [n for n,d in receiving_materials.items() if after_materials.get(n) != d]
    if material_changes: raise RuntimeError('Early receiving material graphs changed: ' + repr(material_changes))
    payload_changes = [n for n,d in receiving.items() if not scene.objects.get(n) or payload_audit.digest(scene.objects[n]) != d]
    if payload_changes: raise RuntimeError('Early receiving native payload changed: ' + repr(payload_changes[:10]))
    receipt['early_receiving_save_readback'] = {'mesh_empty_payloads':len(receiving),'changed':payload_changes,'original_material_graphs':len(receiving_materials)}


for obj in list(scene.objects):
    if obj.type in ('LIGHT', 'CAMERA'):
        bpy.data.objects.remove(obj, do_unlink=True)
    elif obj.get('authoringGuide'):
        obj.hide_render = True
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = args.samples
scene.cycles.use_denoising = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.film_transparent = False
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = 0
scene.view_settings.gamma = 1
receipt['render_settings'] = {'engine': scene.render.engine, 'device': scene.cycles.device,
    'samples': scene.cycles.samples, 'denoising': scene.cycles.use_denoising,
    'view_transform': scene.view_settings.view_transform, 'look': scene.view_settings.look,
    'exposure': scene.view_settings.exposure, 'gamma': scene.view_settings.gamma,
    'resolution_percentage': 100}
scene.world = bpy.data.worlds.new('Supervised matched comparison world')
scene.world.use_nodes = True
background = scene.world.node_tree.nodes['Background']
lighting = module('cg-supervised-lighting02.py' if args.readable_lighting else 'cinematic-cg-2b-lighting.py')
if args.stage:
    if not hasattr(lighting, 'stage'):
        raise RuntimeError('Requested lighting module has no stage()')
    visible_meshes = [o for o in scene.objects if o.type == 'MESH' and not o.hide_render and not o.get('authoringGuide')]
    floor_z = min((o.matrix_world @ Vector(corner)).z for o in visible_meshes for corner in o.bound_box)
    lighting.stage(scene, floor_z)
    receipt['stage'] = {'contact_plane_z': floor_z - .0005, 'export_excluded': True}
profiles = lighting.profiles()
lights = []
for index in range(3):
    data = bpy.data.lights.new('Supervised area ' + str(index), 'AREA')
    obj = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(obj)
    lights.append(obj)
camera_data = bpy.data.cameras.new('Supervised frozen comparison camera')
camera = bpy.data.objects.new(camera_data.name, camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
prior = json.loads((ROOT / 'assets/audit/cinematic-cg-milestone02b/construction01/receipt.json').read_text())
receipt['cameras'] = {}

def render(name, location, target=None, scale=2.1, profile='neutral', rotation=None,
           shift=(0, 0), projection='ORTHO', lens=65, resolution=None):
    rig = profiles[profile]
    background.inputs[0].default_value = (*rig['world_color'][:3], 1)
    background.inputs[1].default_value = rig['world_strength']
    for obj, spec in zip(lights, rig['areas']):
        obj.location = spec['position']
        obj.rotation_euler = (Vector(spec['target']) - obj.location).to_track_quat('-Z', 'Y').to_euler()
        obj.data.energy = spec['power']
        obj.data.color = spec['color']
        obj.data.size = spec['size']
    camera.location = location
    camera.rotation_euler = rotation if rotation else (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera_data.type = projection
    camera_data.ortho_scale = scale
    camera_data.lens = lens
    camera_data.shift_x, camera_data.shift_y = shift
    w, h = resolution or (args.resolution, round(args.resolution * 853 / 1280))
    scene.render.resolution_x, scene.render.resolution_y = w, h
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(OUT / (name + '.png'))
    bpy.context.view_layer.update()
    full_view = name.startswith(('canon-', 'neutral-', 'workshop-')) or name in ('side-profile', 'hero')
    if full_view:
        points = [world_to_camera_view(scene, camera, o.matrix_world @ Vector(corner))
                  for o in scene.objects if o.type == 'MESH' and not o.hide_render and not o.get('authoringGuide')
                  for corner in o.bound_box]
        bounds = [min(p.x for p in points), min(p.y for p in points),
                  max(p.x for p in points), max(p.y for p in points)]
        if bounds[0] < 0 or bounds[1] < 0 or bounds[2] > 1 or bounds[3] > 1:
            raise RuntimeError('Full character cropped in ' + name + ': ' + repr(bounds))
    else:
        bounds = None
    bpy.ops.render.render(write_still=True)
    receipt['cameras'][name] = {'location': list(camera.location), 'rotation_euler': list(camera.rotation_euler),
        'ortho_scale': scale, 'shift': list(shift), 'projection': projection, 'lens_mm': lens,
        'resolution': [w, h], 'lighting': profile,
        'world_color': list(background.inputs[0].default_value),
        'world_strength': background.inputs[1].default_value,
        'areas': [{'location': list(o.location), 'rotation_euler': list(o.rotation_euler),
            'power': o.data.energy, 'color': list(o.data.color), 'size': o.data.size} for o in lights],
        'render_settings': dict(receipt['render_settings']), 'full_character_bounds': bounds}

canon = module('cg-supervised-camera04.py').camera(ROOT)
for profile in ('neutral', 'workshop'):
    render('canon-' + profile, canon['location'], rotation=canon['rotation_euler'],
           scale=canon['ortho_scale'], shift=canon['shift'], projection=canon['projection'], lens=canon['lens_mm'], profile=profile)
render('head-neck', (-6, -2.14, 2.04), (0, -.10, 1.55), scale=1.10, resolution=(args.resolution, args.resolution))
render('side-profile', (-6, 0, .97), (0, 0, .97), scale=3.20)
if args.final:
    render('body-detail', (-6, -2.4, 1.50), (0, -.04, 1.13), scale=1.28, resolution=(args.resolution, args.resolution))
    render('feet-detail', (-2.8, -3.6, 1.02), (0, -.03, .14), scale=.92, resolution=(args.resolution, args.resolution))
    for profile in ('neutral', 'workshop'):
        for i in range(8):
            angle = math.radians(i * 45)
            center = Vector((0, -.04, .97))
            position = center + Vector((6 * math.sin(angle), -6 * math.cos(angle), 1.02))
            render(f'{profile}-{i * 45:03d}', position, center, scale=3.20, profile=profile)
    render('hero', (-3, -3.9, 1.32), (0, -.04, .99), profile='cinematic', projection='PERSP',
           resolution=(int(args.resolution * .75), args.resolution))
if args.mode == 'candidate':
    for image in bpy.data.images:
        if image.source == 'FILE' and not image.packed_file:
            image.pack()
    bpy.context.preferences.filepaths.save_version = 0
    native = ASSET / f'murderbird-supervised-{args.era}.blend'
    preservation.retain_packed_image_ids(scene)
    bpy.ops.wm.save_as_mainfile(filepath=str(native), relative_remap=False)
    receipt['native_sha256'] = sha(native)
    bpy.ops.wm.open_mainfile(filepath=str(native))
    scene = bpy.context.scene
    receipt['packed_history_save_readback'] = preservation.verify_receiving_images(receiving_images)
    after_materials = payload_audit.material_digest()
    material_changes = [n for n,d in receiving_materials.items() if after_materials.get(n) != d]
    if material_changes: raise RuntimeError('Receiving material graphs changed: ' + repr(material_changes))
    payload_changes = [n for n,d in receiving.items() if not scene.objects.get(n) or payload_audit.digest(scene.objects[n]) != d]
    if payload_changes: raise RuntimeError('Receiving native payload changed: ' + repr(payload_changes[:10]))
    receipt['receiving_material_graph_preservation'] = {'graphs':len(receiving_materials),'changed':material_changes}
    receipt['receiving_save_readback'] = {'mesh_empty_payloads':len(receiving),'changed':payload_changes}
    receipt['receiving_visibility_changes'] = {n: {'before':v, 'after':[scene.objects[n].hide_render, scene.objects[n].hide_viewport, scene.objects[n].hide_get()]} for n,v in receiving_visibility.items() if [scene.objects[n].hide_render,scene.objects[n].hide_viewport,scene.objects[n].hide_get()] != v}
    if args.export:
        try:
            receipt['browser_export'] = module('cg-supervised-export.py').export(scene, ASSET / f'murderbird-supervised-{args.era}.glb')
        except Exception as exc:
            receipt['browser_export_failure'] = str(exc)
            (OUT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
            raise
if sha(INPUT) != input_sha:
    raise RuntimeError('Historical input binary changed')
receipt['input_preserved'] = True
receipt['created_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
receipt['image_hashes'] = {p.name: sha(p) for p in OUT.glob('*.png')}
(OUT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('SUPERVISED09_COMPLETE', OUT)
