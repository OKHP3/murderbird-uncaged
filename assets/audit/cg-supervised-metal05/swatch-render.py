"""Render already exported seven-plane swatches; no third character attempt."""
from pathlib import Path
import bpy,importlib.util
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
for era in ('maker','mechanic','builder'):
 bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;bpy.ops.import_scene.gltf(filepath=str(ROOT/'era-swatch'/(era+'-seven-family.glb')))
 sp=importlib.util.spec_from_file_location('rig',ROOT.parents[2]/'scripts/cg-supervised-lighting02.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);cfg=m.profiles()['neutral']
 world=bpy.data.worlds.new('Swatch neutral');world.use_nodes=True;s.world=world;world.node_tree.nodes['Background'].inputs[0].default_value=(*cfg['world_color'],1);world.node_tree.nodes['Background'].inputs[1].default_value=cfg['world_strength']
 for i,a in enumerate(cfg['areas']):
  d=bpy.data.lights.new('Swatch area '+str(i),'AREA');o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=Vector(a['position'])+Vector((3.6,0,3));o.rotation_euler=(Vector((3.6,0,0))-o.location).to_track_quat('-Z','Y').to_euler();d.energy=a['power']*2;d.color=a['color'];d.size=a['size']
 d=bpy.data.cameras.new('Swatch camera');cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);s.camera=cam;cam.location=(3.6,-.01,8);cam.rotation_euler=(Vector((3.6,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=9.0
 s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=240;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=True;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.render.filepath=str(ROOT/'era-swatch'/(era+'-seven-family.png'));bpy.ops.render.render(write_still=True)
 print('SWATCH_RENDER',era,flush=True)
