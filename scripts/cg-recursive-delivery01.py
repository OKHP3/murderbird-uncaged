"""Explicit successor authoring runner: immutable saved09 -> new versioned checkpoint.

Run inside Blender. Inputs are hash pinned; native custody is checked before and
following a save/reopen. Review scenes/clay overrides never enter the native.
Final packets/export require an explicit whole-candidate approval in selection.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import math
import re
import struct
import sys
import traceback
from pathlib import Path

import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ERAS = ('builder', 'maker', 'mechanic')
MANIFEST = 'assets/audit/cg-supervised01/attempt09/frozen-manifest.json'
MANIFEST_SHA = '378a01fb9430ade08c9de4c5bcc2026f9130bda95d8d57d237390bf12e748c36'
COMPLETE_MARKER = 'CG_RECURSIVE_DELIVERY01_COMPLETE'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, default=str) + '\n')


def load(path, expected):
    path = Path(path).resolve()
    if sha(path) != expected:
        raise RuntimeError('Pinned Python input changed: ' + str(path))
    spec = importlib.util.spec_from_file_location('delivery_' + path.stem.replace('-', '_'), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resolve(root, path):
    return (root / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()


def value(x):
    if isinstance(x, (str, int, float, bool, type(None))):
        return x
    if hasattr(x, 'name'):
        return {'id_name': x.name}
    if hasattr(x, 'to_dict'):
        return {k: value(v) for k, v in x.to_dict().items()}
    try:
        return [value(v) for v in x]
    except TypeError:
        return str(x)


def image_snapshot():
    return {i.name: {'source': i.source, 'filepath': i.filepath,
        'filepath_raw': i.filepath_raw, 'size': list(i.size), 'channels': i.channels,
        'file_format': i.file_format, 'colorspace': i.colorspace_settings.name,
        'alpha_mode': i.alpha_mode, 'fake_user': i.use_fake_user,
        'props': {k: value(v) for k, v in sorted(i.items())},
        'packed_sha256': hashlib.sha256(bytes(i.packed_file.data)).hexdigest() if i.packed_file else None}
        for i in bpy.data.images if i.source == 'FILE' or i.packed_file}


def snapshot(scene, strong, payload):
    objects = [o for o in scene.objects if o.type in ('MESH', 'EMPTY')]
    return {'payload': {o.name: payload.digest(o) for o in objects},
            'strong_payload': {o.name: strong.digest(o) for o in objects},
            'materials': strong.snap()['materials'], 'images': image_snapshot(),
            'visibility': {o.name: [o.hide_render, o.hide_viewport, o.hide_get()] for o in objects},
            'mesh_names': sorted(o.name for o in objects if o.type == 'MESH'),
            'empty_names': sorted(o.name for o in objects if o.type == 'EMPTY')}


def verify(scene, before, strong, payload, declared):
    after = snapshot(scene, strong, payload)
    changed = {key: [n for n, d in before[key].items() if after[key].get(n) != d]
               for key in ('payload', 'strong_payload', 'materials', 'images')}
    if any(changed.values()):
        raise RuntimeError('Receiving custody changed: ' + repr({k: v[:12] for k, v in changed.items()}))
    visibility = {n: {'before': v, 'after': after['visibility'].get(n)}
                  for n, v in before['visibility'].items() if after['visibility'].get(n) != v}
    for n, change in visibility.items():
        if n not in declared:
            raise RuntimeError('Undeclared receiving visibility change: ' + n)
        old, new = change['before'], change['after']
        # Only retirement hides are authorized. Global viewport flag stays exact;
        # an optional per-view-layer hide is allowed when specifically declared.
        expected = declared[n]
        want = [True, old[1], True if expected.get('hide_set', False) else old[2]]
        if new != want:
            raise RuntimeError('Declared render hide differs: ' + repr((n, old, new, want)))
    missing_hides = [n for n in declared if not scene.objects[n].hide_render]
    if missing_hides:
        raise RuntimeError('Declared superseded object still renders: ' + repr(missing_hides))
    return {'status': 'PASS', 'receiving_mesh_empty_payloads': len(before['payload']),
            'original_material_graphs': len(before['materials']),
            'original_file_images': sum(i['source'] == 'FILE' for i in before['images'].values()),
            'original_packed_images': sum(i['packed_sha256'] is not None for i in before['images'].values()),
            'receiving_changes': changed, 'declared_visibility_changes': visibility,
            'added_mesh_count': len(set(after['mesh_names']) - set(before['mesh_names'])),
            'added_empty_count': len(set(after['empty_names']) - set(before['empty_names']))}


def evaluated_check(scene, receiving_names):
    """Finite evaluated coordinates/UV/normals and actual face assignments.

    Pre-existing zero-area triangles are counted, not an engineering rejection.
    UV coordinates may tile: finite does not mean all inherited UVs are 0..1.
    """
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    records = []
    for obj in scene.objects:
        if obj.type != 'MESH' or obj.hide_render or obj.get('authoringGuide'):
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
        try:
            mesh.calc_loop_triangles()
            positions = np.empty(len(mesh.vertices) * 3, np.float32)
            mesh.vertices.foreach_get('co', positions)
            if not np.isfinite(positions).all() or not all(math.isfinite(c) for row in obj.matrix_world for c in row):
                raise RuntimeError('Non-finite evaluated positions/transform: ' + obj.name)
            uv_names = []
            for uv in mesh.uv_layers:
                points = np.empty(len(uv.data) * 2, np.float32)
                uv.data.foreach_get('uv', points)
                if not np.isfinite(points).all():
                    raise RuntimeError('Non-finite UV: ' + obj.name + ':' + uv.name)
                uv_names.append(uv.name)
            normals = [tuple(n.vector) for n in mesh.corner_normals]
            if not all(math.isfinite(c) for n in normals for c in n):
                raise RuntimeError('Non-finite corner normal: ' + obj.name)
            bad_slots = sorted({p.material_index for p in mesh.polygons
                                if p.material_index >= len(mesh.materials) or mesh.materials[p.material_index] is None})
            if bad_slots:
                raise RuntimeError('Missing evaluated face material: ' + repr((obj.name, bad_slots)))
            zero_triangles = sum(t.area == 0 for t in mesh.loop_triangles)
            record = {'name': obj.name, 'added': obj.name not in receiving_names,
                      'vertices': len(mesh.vertices), 'triangles': len(mesh.loop_triangles),
                      'uv_layers': uv_names, 'face_slots': sorted({p.material_index for p in mesh.polygons}),
                      'material_slots': [m.name if m else None for m in mesh.materials],
                      'finite_positions_uv_normals': True, 'zero_area_triangles': zero_triangles}
            records.append(record)
        finally:
            evaluated.to_mesh_clear()
    return {'status': 'PASS', 'checked_visible_meshes': len(records),
            'added_visible_meshes': sum(r['added'] for r in records),
            'evaluated_triangles': sum(r['triangles'] for r in records),
            'zero_area_triangles': sum(r['zero_area_triangles'] for r in records),
            'records': records, 'limits': ['No manifold, engineering, appearance or browser validation.']}


def view_keys(argument, cameras):
    aliases = {'whole-pbr': 'canon-neutral', 'whole-clay': 'canon-neutral-clay',
               'head': 'head-neck', 'body': 'body-detail', 'profile': 'side-profile', 'rear': 'neutral-180'}
    if argument == 'none':
        return []
    if argument == 'final':
        return ['canon-neutral', 'canon-workshop', 'head-neck', 'body-detail', 'feet-detail', 'side-profile'] + [
            f'{lighting}-{angle:03d}' for lighting in ('neutral', 'workshop') for angle in range(0, 360, 45)] + ['hero']
    result = [aliases.get(item.strip(), item.strip()) for item in argument.split(',')]
    if len(set(result)) != len(result):
        raise ValueError('Duplicate view names')
    missing = [key for key in result if key.removesuffix('-clay') not in cameras]
    if missing:
        raise ValueError('Unknown saved09 view: ' + repr(missing))
    return result


def render_views(receiving_scene, source_receipt, keys, out, args):
    """Use a separate scene and exact saved09 serialized area rig/cameras."""
    if not keys:
        return {}
    scene = bpy.data.scenes.new('Recursive disposable saved09 review rig')
    added_objects, added_lights = [], []
    world = bpy.data.worlds.new('Recursive disposable saved09 world')
    world.use_nodes = True
    scene.world = world
    clay = None
    prior_scene = bpy.context.window.scene
    try:
        for obj in receiving_scene.objects:
            if obj.type == 'MESH' and not obj.hide_render and not obj.get('authoringGuide'):
                scene.collection.objects.link(obj)
        # Saved09 stage ground is preserved as a receiving guide. A temporary
        # object copy restores it only in the review scene, never in the asset.
        grounds = [o for o in receiving_scene.objects if o.type == 'MESH'
                   and o.get('authoringGuide') and o.name.startswith('Finish02 review contact ground')]
        if grounds:
            ground = sorted(grounds, key=lambda o: o.name)[-1].copy()
            ground.name = 'Recursive disposable original09 stage copy'
            scene.collection.objects.link(ground); ground.hide_render = False; ground.hide_viewport = False
            added_objects.append(ground)
        bpy.context.window.scene = scene
        camera_data = bpy.data.cameras.new('Recursive disposable exact09 camera')
        camera = bpy.data.objects.new(camera_data.name, camera_data)
        scene.collection.objects.link(camera); scene.camera = camera; added_objects.append(camera)
        settings = source_receipt['render_settings']
        scene.render.engine = settings['engine']; scene.cycles.device = settings['device']
        scene.cycles.samples = args.samples; scene.cycles.use_denoising = settings['denoising']
        scene.render.threads_mode = 'FIXED'; scene.render.threads = 2
        scene.view_settings.view_transform = settings['view_transform']; scene.view_settings.look = settings['look']
        scene.view_settings.exposure = settings['exposure']; scene.view_settings.gamma = settings['gamma']
        scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_mode = 'RGBA'
        scene.render.resolution_percentage = 100; scene.render.film_transparent = False
        background = world.node_tree.nodes['Background']
        clay = bpy.data.materials.new('Recursive disposable clay override')
        clay.use_nodes = True
        shader = clay.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Base Color'].default_value = (.35, .35, .35, 1)
        shader.inputs['Roughness'].default_value = .70
        shader.inputs['Metallic'].default_value = 0
        records = {}
        for key in keys:
            path = out / (key + '.png')
            if path.exists():
                raise RuntimeError('Render output collision: ' + str(path))
            spec = source_receipt['cameras'][key.removesuffix('-clay')]
            for obj in list(added_lights):
                data = obj.data; bpy.data.objects.remove(obj, do_unlink=True); bpy.data.lights.remove(data)
            added_lights.clear()
            background.inputs[0].default_value = spec['world_color']
            background.inputs[1].default_value = spec['world_strength']
            for index, area in enumerate(spec['areas']):
                data = bpy.data.lights.new('Recursive saved09 area ' + str(index), 'AREA')
                data.energy = area['power']; data.color = area['color']; data.size = area['size']
                obj = bpy.data.objects.new(data.name, data); scene.collection.objects.link(obj)
                obj.location = area['location']; obj.rotation_euler = area['rotation_euler']; added_lights.append(obj)
            camera.location = spec['location']; camera.rotation_euler = spec['rotation_euler']
            camera_data.type = spec['projection']; camera_data.ortho_scale = spec['ortho_scale']
            camera_data.lens = spec['lens_mm']; camera_data.shift_x, camera_data.shift_y = spec['shift']
            w, h = spec['resolution']
            if args.resolution:
                factor = args.resolution / max(w, h); w, h = round(w * factor), round(h * factor)
            scene.render.resolution_x, scene.render.resolution_y = w, h
            scene.view_layers[0].material_override = clay if key.endswith('-clay') else None
            scene.render.filepath = str(path)
            bpy.context.view_layer.update()
            bounds = None
            full = key.startswith(('canon-', 'neutral-', 'workshop-')) or key in ('side-profile', 'hero')
            if full:
                points = [world_to_camera_view(scene, camera, obj.matrix_world @ Vector(v))
                          for obj in scene.objects if obj.type == 'MESH' and not obj.get('authoringGuide')
                          for v in obj.bound_box]
                bounds = [min(p.x for p in points), min(p.y for p in points), max(p.x for p in points), max(p.y for p in points)]
                # Same camera is the contract. Never auto-fit a changed candidate.
                if min(bounds[:2]) < -1e-5 or max(bounds[2:]) > 1.00001:
                    raise RuntimeError('Candidate cropped by immutable saved09 view: ' + repr((key, bounds)))
            bpy.ops.render.render(write_still=True)
            if not path.exists() or path.stat().st_size < 100:
                raise RuntimeError('Render did not produce PNG: ' + str(path))
            records[key] = {'saved09_view': key.removesuffix('-clay'), 'camera_light_spec': spec,
                'resolution': [w, h], 'samples': args.samples, 'material_override': 'temporary clay' if key.endswith('-clay') else None,
                'full_character_bounds': bounds, 'sha256': sha(path)}
            print('CG_RECURSIVE_DELIVERY01_VIEW_COMPLETE', key, str(path), flush=True)
        return records
    finally:
        bpy.context.window.scene = prior_scene
        for obj in added_lights:
            data = obj.data; bpy.data.objects.remove(obj, do_unlink=True); bpy.data.lights.remove(data)
        for obj in added_objects:
            if obj.type == 'CAMERA':
                data = obj.data; bpy.data.objects.remove(obj, do_unlink=True); bpy.data.cameras.remove(data)
            else:
                bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.scenes.remove(scene)
        bpy.data.worlds.remove(world)
        if clay:
            bpy.data.materials.remove(clay)


def inspect_static_glb(path):
    raw = Path(path).read_bytes()
    size, chunk_type = struct.unpack_from('<II', raw, 12)
    if chunk_type != 0x4e4f534a:
        raise RuntimeError('Missing GLB JSON')
    doc = json.loads(raw[20:20 + size])
    if doc.get('animations') or doc.get('skins') or any('skin' in n for n in doc.get('nodes', [])):
        raise RuntimeError('Static review export contains animation or skin')
    if any('uri' in item for group in ('buffers', 'images') for item in doc.get(group, [])):
        raise RuntimeError('Review GLB contains external URI')
    return {'status': 'PASS', 'animation_count': 0, 'skin_count': 0, 'external_uri_count': 0,
            'embedded_images': len(doc.get('images', [])), 'mesh_count': len(doc.get('meshes', []))}


def run(args):
    root = Path(args.source_root).resolve()
    manifest_path = root / MANIFEST
    if sha(manifest_path) != MANIFEST_SHA:
        raise RuntimeError('Frozen09 manifest changed')
    manifest = json.loads(manifest_path.read_text())
    pins = {f['path']: f for f in manifest['files']}
    helper_names = ('cg-supervised-preservation.py', 'cg-supervised-head17.py', 'cg-supervised-body12.py', 'cg-supervised-export.py')
    helpers = {name: load(root / 'scripts' / name, pins['scripts/' + name]['sha256']) for name in helper_names}
    selection = json.loads(Path(args.selection).read_text()) if args.selection else {'modules': []}
    if args.mode == 'candidate' and not (args.selection and selection.get('root_adjudication_complete')):
        raise RuntimeError('Candidate requires explicit root-adjudicated module selection')
    if args.mode == 'baseline' and selection.get('modules'):
        raise RuntimeError('Baseline cannot apply modules')
    if (args.export or args.views == 'final') and not selection.get('visible_whole_candidate_approved'):
        raise RuntimeError('Final packet/export requires root approval of the visible whole candidate')
    module_pins = []
    for item in selection.get('modules', []):
        if not isinstance(item.get('declared_superseded_render_hides', []), list):
            raise ValueError('Each module must list declared_superseded_render_hides')
        path = resolve(root, item['path'])
        if sha(path) != item['sha256']:
            raise RuntimeError('Selected module hash changed: ' + str(path))
        module_pins.append((item, path))
    parent = Path(args.output_root).resolve()
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,79}', args.checkpoint_id):
        raise ValueError('Checkpoint id must be lowercase kebab-case')
    checkpoint = parent / args.checkpoint_id
    if 'public' in checkpoint.parts or '.local' in checkpoint.parts:
        raise ValueError('Runtime/public or private archive output is prohibited')
    # Reject writes within every frozen asset/audit directory, even through symlinks.
    for frozen in ('assets/models/cg-supervised01', 'assets/audit/cg-supervised01'):
        protected = (root / frozen).resolve()
        if checkpoint == protected or protected in checkpoint.parents:
            raise ValueError('Frozen/historical output tree is prohibited')
    marker = checkpoint / 'checkpoint-state.json'
    signature = {'source_root': str(root), 'mode': args.mode, 'selection_sha256': sha(args.selection) if args.selection else None,
                 'checkpoint_id': args.checkpoint_id, 'runner_sha256': sha(__file__)}
    if checkpoint.exists():
        if not args.continue_unfinalized or not marker.exists():
            raise RuntimeError('Checkpoint output collision; choose a new id')
        state = json.loads(marker.read_text())
        if state.get('status') != 'unfinalized' or state.get('signature') != signature:
            raise RuntimeError('Continuation requires the exact same new unfinalized checkpoint')
    else:
        checkpoint.mkdir(parents=True, exist_ok=False)
        write(marker, {'status': 'unfinalized', 'signature': signature})
    for era in ERAS if args.era == 'all' else (args.era,):
        out = checkpoint / era
        if out.exists():
            raise RuntimeError('Era output collision; choose a new checkpoint id: ' + str(out))
        out.mkdir()
        relative_native = f'assets/models/cg-supervised01/attempt09/murderbird-supervised-{era}.blend'
        source = root / relative_native
        relative_receipt = f'assets/audit/cg-supervised01/attempt09/{era}/receipt.json'
        camera_receipt_path = root / relative_receipt
        for rel in (relative_native, relative_receipt):
            if sha(root / rel) != pins[rel]['sha256']:
                raise RuntimeError('Frozen09 source changed: ' + rel)
        cameras = json.loads(camera_receipt_path.read_text())
        keys = view_keys(args.views, cameras['cameras'])
        report = {'status': 'IN_PROGRESS', 'scope': 'Development successor from exact saved09; no runtime/publish/engineering/acceptance claim',
            'era': era, 'mode': args.mode, 'checkpoint': str(checkpoint),
            'source_native': str(source), 'source_native_sha256': sha(source),
            'frozen_manifest': str(manifest_path), 'frozen_manifest_sha256': MANIFEST_SHA,
            'saved09_camera_receipt': str(camera_receipt_path), 'camera_receipt_sha256': sha(camera_receipt_path),
            'runner_sha256': sha(__file__), 'helper_pins': {n: pins['scripts/' + n]['sha256'] for n in helper_names},
            'selection': selection, 'selection_sha256': signature['selection_sha256'], 'module_results': {},
            'browser_light_difference': 'Native exact09 area rig and browser environment are distinct; no pixel equivalence claimed.',
            'checks_not_run': ['Owner artistic acceptance', 'CI', 'deployment', 'production runtime replacement'],
            'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
        write(out / 'receipt.json', report)
        bpy.ops.wm.open_mainfile(filepath=str(source)); scene = bpy.context.scene
        strong, payload = helpers['cg-supervised-head17.py'], helpers['cg-supervised-body12.py']
        before = snapshot(scene, strong, payload)
        report['actual_receiving_counts'] = {'mesh_empty': len(before['payload']), 'meshes': len(before['mesh_names']),
            'empties': len(before['empty_names']), 'materials': len(before['materials']),
            'packed_images': sum(i['packed_sha256'] is not None for i in before['images'].values()),
            'file_images': sum(i['source'] == 'FILE' for i in before['images'].values())}
        if (report['actual_receiving_counts']['mesh_empty'], report['actual_receiving_counts']['materials'], report['actual_receiving_counts']['packed_images']) != (7608, 62, 161):
            raise RuntimeError('Saved09 receiving counts differ from the expected frozen inventory: ' + repr(report['actual_receiving_counts']))
        write(out / 'receiving-snapshot.json', before)
        declared = {}
        for item, path in module_pins:
            for entry in item.get('declared_superseded_render_hides', []):
                entry = {'name': entry, 'hide_set': False} if isinstance(entry, str) else entry
                if entry['name'] not in before['visibility']:
                    raise RuntimeError('Declared receiving hide name does not exist: ' + entry['name'])
                if entry['name'] in declared and declared[entry['name']] != entry:
                    raise RuntimeError('Conflicting declared visibility retirement: ' + entry['name'])
                declared[entry['name']] = entry
            module = load(path, item['sha256'])
            report['module_results'][str(path)] = module.apply(scene, resolve(root, item.get('root_path', str(root))), era)
        report['before_save_custody'] = verify(scene, before, strong, payload, declared)
        # Retain otherwise orphaned packed FILE ids without changing original
        # material graphs, pixels, image fake-user flags or receiving payloads.
        helpers['cg-supervised-preservation.py'].retain_packed_image_ids(scene)
        native = out / f'murderbird-recursive-{era}.blend'
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=str(native), relative_remap=False)
        bpy.ops.wm.open_mainfile(filepath=str(native)); scene = bpy.context.scene
        report['save_reopen_custody'] = verify(scene, before, strong, payload, declared)
        report['native_sha256'] = sha(native)
        report['native_path'] = str(native)
        report['added_mesh_count'] = report['save_reopen_custody']['added_mesh_count']
        report['evaluated_geometry'] = evaluated_check(scene, set(before['payload']))
        write(out / 'receipt.json', report)
        print('CG_RECURSIVE_DELIVERY01_CUSTODY_PASS', era, report['actual_receiving_counts'], flush=True)
        report['renders'] = render_views(scene, cameras, keys, out, args)
        report['after_render_custody'] = verify(scene, before, strong, payload, declared)
        if args.export:
            glb = out / f'murderbird-recursive-{era}.glb'
            report['browser_export'] = helpers['cg-supervised-export.py'].export(scene, glb, batched=True)
            report['static_export_check'] = inspect_static_glb(glb)
            report['after_export_custody'] = verify(scene, before, strong, payload, declared)
        else:
            report['checks_not_run'].append('GLB export and browser verification')
        if sha(source) != report['source_native_sha256'] or sha(native) != report['native_sha256']:
            raise RuntimeError('Receiving or newly saved native changed after custody verification')
        report['status'] = 'PASS'
        report['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        write(out / 'receipt.json', report)
        print(COMPLETE_MARKER, era, str(out / 'receipt.json'), flush=True)
    write(marker, {'status': 'complete', 'signature': signature, 'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', required=True)
    parser.add_argument('--output-root', required=True)
    parser.add_argument('--checkpoint-id', required=True)
    parser.add_argument('--era', choices=(*ERAS, 'all'), default='builder')
    parser.add_argument('--mode', choices=('baseline', 'candidate'), default='baseline')
    parser.add_argument('--selection')
    parser.add_argument('--views', default='whole-clay,whole-pbr')
    parser.add_argument('--samples', type=int, default=4)
    parser.add_argument('--resolution', type=int, default=640, help='Longest edge; 0 retains saved09 pixel dimensions')
    parser.add_argument('--export', action='store_true')
    parser.add_argument('--continue-unfinalized', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    if args.samples < 1 or args.resolution < 0:
        raise ValueError('Samples must be positive; resolution cannot be negative')
    run(args)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        print('CG_RECURSIVE_DELIVERY01_FAILED', flush=True)
        # Blender sometimes exits zero on Python failure; explicit process exit
        # plus the missing completion marker lets shell integration reject it.
        sys.exit(1)
