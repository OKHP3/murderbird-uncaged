"""Read-only matched neutral views of hash-bound editable models.

Render-only materials and lights never modify the native model. Before/after
must use this same script, camera, ground and lights. No dimensions are inferred
from the artwork and these views do not constitute artistic acceptance.
"""
from pathlib import Path
import argparse, hashlib, json, sys
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--native', required=True)
p.add_argument('--sha', required=True)
p.add_argument('--output', required=True)
p.add_argument('--views', nargs='+', default=['reference-angle'], choices=['reference-angle','front','side','rear','head','shoulder','feet'])
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
native = ROOT / a.native
out = ROOT / a.output
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(native) == a.sha and not out.exists()
out.mkdir(parents=True)
(out / 'executed-neutral-render.py').write_bytes(Path(__file__).read_bytes())
bpy.ops.wm.open_mainfile(filepath=str(native))
scene = bpy.context.scene
for o in list(bpy.data.objects):
    if o.type in {'LIGHT', 'CAMERA'}:
        bpy.data.objects.remove(o, do_unlink=True)
    elif o.type == 'MESH':
        o.hide_render = bool(o.get('authoringGuide')) or 'builder' not in o.get('exteriorEras', 'maker,mechanic,builder').split(',')
    elif o.type == 'CURVE':
        o.hide_render = True
# Shared neutral response: component contrast follows the existing regional
# assignment; no photographic highlights, texture marks or shape changes.
for m in bpy.data.materials:
    m.use_nodes = True
    bsdf = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf:
        rgb = m.diffuse_color[:3]
        value = sum(rgb) / 3
        bsdf.inputs['Base Color'].default_value = (value, value, value, 1)
        bsdf.inputs['Roughness'].default_value = .62
        bsdf.inputs['Metallic'].default_value = 0
        bsdf.inputs['Emission Color'].default_value = (0, 0, 0, 1)
        bsdf.inputs['Emission Strength'].default_value = 0
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.cycles.device = 'CPU'
scene.render.resolution_x = scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.view_settings.view_transform = 'AgX'
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.15, .15, .15, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .4
lights = [('key', (-3, -4, 5), 700, 4), ('fill', (4, -1, 3), 350, 4), ('rim', (0, 4, 4), 500, 3)]
for name, pos, power, size in lights:
    d = bpy.data.lights.new('neutral-' + name, 'AREA')
    d.energy = power
    d.shape = 'DISK'
    d.size = size
    o = bpy.data.objects.new(d.name, d)
    scene.collection.objects.link(o)
    o.location = pos
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
camera_data = bpy.data.cameras.new('matched-neutral-camera')
camera_data.type = 'ORTHO'
camera_data.ortho_scale = 2.5
camera = bpy.data.objects.new(camera_data.name, camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
views = {
    'reference-angle': ((-6,-3.5,2.75),(0,-.08,1.02),2.5),
    'front': ((0,-7,1.65),(0,-.08,1.02),2.5),
    'side': ((-7,0,1.35),(0,-.08,1.02),2.5),
    'rear': ((0,7,1.65),(0,-.08,1.02),2.5),
    'head': ((-6,-3.5,2.75),(0,-.32,1.61),1.1),
    'shoulder': ((-6,-3.5,2.75),(-.22,-.01,1.11),.85),
    'feet': ((-6,-3.5,2.1),(0,-.16,.19),1.1),
}
rendered=[]
for name in a.views:
    pos,target,scale=views[name]
    camera.location=pos
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera_data.ortho_scale=scale
    scene.render.filepath=str(out/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    rendered.append({'name':name,'path':str(Path(scene.render.filepath).relative_to(ROOT)),'sha256':sha(Path(scene.render.filepath)),'camera':{'position':pos,'target':target,'orthoScale':scale}})
assert sha(native)==a.sha
receipt={'native':{'path':a.native,'sha256':a.sha},'views':rendered,'lights':lights,'renderer':'Cycles CPU, 24 samples, denoised, AgX','nativeUnchanged':True,'scope':'Neutral geometry review, temporary gray material response; no ground added, no authored geometry changed, no final surface claim.'}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
