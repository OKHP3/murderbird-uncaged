"""Disposable matched native review using retained04 serialized cameras/lights.

No auto-fit, source save, material override or reference substitution. Reduced
samples/resolution are diagnostic settings and are identical for each pair.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args):
    native = Path(args.native).resolve()
    original_hash = sha(native)
    out = Path(args.out).resolve()
    # Every render batch is retained evidence. A later invocation must use a
    # fresh purpose-specific directory, including for a different view list.
    out.mkdir(parents=True, exist_ok=False)
    receiving = ROOT / 'assets/audit/cg-recursive-three-loop01/loop03/delivery/retained04' / args.era
    source_receipt = json.loads((receiving / 'receipt.json').read_text(encoding='utf-8'))
    bpy.ops.wm.open_mainfile(filepath=str(native), load_ui=False, use_scripts=False)
    asset_scene = bpy.context.scene
    scene = bpy.data.scenes.new('Disposable connected head matched review')
    world = bpy.data.worlds.new('Disposable connected head review world')
    world.use_nodes = True
    scene.world = world
    for obj in asset_scene.objects:
        if obj.type == 'MESH' and not obj.hide_render and not obj.get('authoringGuide'):
            scene.collection.objects.link(obj)
    # The already-preserved stage is a review prop, not new character geometry.
    grounds = [obj for obj in asset_scene.objects if obj.type == 'MESH'
               and obj.get('authoringGuide') and obj.name.startswith('Finish02 review contact ground')]
    if grounds:
        ground = sorted(grounds, key=lambda obj: obj.name)[-1].copy()
        scene.collection.objects.link(ground)
        ground.hide_render = False; ground.hide_viewport = False; ground.hide_set(False)
    bpy.context.window.scene = scene
    camera_data = bpy.data.cameras.new('Disposable fixed retained camera')
    camera = bpy.data.objects.new(camera_data.name, camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True
    scene.render.threads_mode = 'FIXED'; scene.render.threads = 4
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    lights = []
    records = []
    for key in args.views.split(','):
        path = out / (key + '.png')
        if path.exists():
            raise FileExistsError('Retained image collision: ' + str(path))
        head = key.startswith('head-')
        lighting = 'neutral' if key.endswith('neutral') else 'workshop'
        spec = source_receipt['renders']['head-neck' if head else 'canon-' + lighting]['camera_light_spec']
        light_spec = source_receipt['renders']['canon-' + lighting]['camera_light_spec']
        for obj in lights:
            data = obj.data; bpy.data.objects.remove(obj, do_unlink=True); bpy.data.lights.remove(data)
        lights.clear()
        background = world.node_tree.nodes['Background']
        background.inputs[0].default_value = light_spec['world_color']
        background.inputs[1].default_value = light_spec['world_strength']
        for index, area in enumerate(light_spec['areas']):
            data = bpy.data.lights.new('Disposable review area ' + str(index), 'AREA')
            data.energy = area['power']; data.color = area['color']; data.size = area['size']
            obj = bpy.data.objects.new(data.name, data); scene.collection.objects.link(obj)
            obj.location = area['location']; obj.rotation_euler = area['rotation_euler']; lights.append(obj)
        settings = spec['render_settings']
        scene.view_settings.view_transform = settings['view_transform']
        scene.view_settings.look = settings['look']
        scene.view_settings.exposure = settings['exposure']
        scene.view_settings.gamma = settings['gamma']
        camera.location = spec['location']; camera.rotation_euler = spec['rotation_euler']
        camera_data.type = spec['projection']; camera_data.ortho_scale = spec['ortho_scale']
        camera_data.lens = spec['lens_mm']; camera_data.shift_x, camera_data.shift_y = spec['shift']
        width, height = spec['resolution']
        factor = args.resolution / max(width, height)
        scene.render.resolution_x = round(width * factor); scene.render.resolution_y = round(height * factor)
        scene.render.filepath = str(path)
        bpy.context.view_layer.update()
        bpy.ops.render.render(write_still=True)
        records.append({'view': key, 'native_sha256': original_hash, 'image': str(path), 'sha256': sha(path),
                        'camera': spec, 'lighting': light_spec, 'samples': args.samples,
                        'resolution': [scene.render.resolution_x, scene.render.resolution_y]})
        (out / 'render-receipt.json').write_text(json.dumps(records, indent=2) + '\n')
        print('CONNECTED_HEAD_RENDERED', key, flush=True)
    assert sha(native) == original_hash, 'Review modified native file'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--native', required=True)
    parser.add_argument('--era', required=True, choices=('maker', 'mechanic', 'builder'))
    parser.add_argument('--out', required=True)
    parser.add_argument('--views', default='canon-neutral,head-neutral,canon-workshop,head-workshop')
    parser.add_argument('--samples', type=int, default=4)
    parser.add_argument('--resolution', type=int, default=800)
    run(parser.parse_args(sys.argv[sys.argv.index('--') + 1:]))
