"""Seven family/three era material swatches, no character geometry exported."""
import bpy,json,importlib.util,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];INP=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');OUT=Path(__file__).resolve().parent/'era-swatch';OUT.mkdir(exist_ok=True)
def mod(n):
 sp=importlib.util.spec_from_file_location(n,ROOT/'scripts'/('cg-supervised-'+n+'.py'));m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
for era in ('maker','mechanic','builder'):
 bpy.ops.wm.open_mainfile(filepath=str(INP/'assets/audit/cg-supervised-body05/attempt02/murderbird-body05.blend'));s=bpy.context.scene
 # This smoke checks incoming finish04 graphs and per-era overlays; never alters optics.
 mod('finish04').apply(s,OUT/(era+'-baseline'),era,INP)
 receipt=mod('metal05').apply(s,OUT,era,INP)
 bpy.ops.object.select_all(action='DESELECT');sw=[];families=list(mod('metal05').PALETTES)
 for i,fam in enumerate(families):
  m=next(m for m in bpy.data.materials if m.get('cgMetal05Family')==fam and not m.get('cgMetal05LocalBoundary'))
  bpy.ops.mesh.primitive_plane_add(size=1,location=(i*1.2,0,0));o=bpy.context.object;o.name='Metal05 material swatch '+fam;o.data.materials.append(m);sw.append(o)
 bpy.ops.object.select_all(action='DESELECT')
 for o in sw:o.select_set(True)
 bpy.context.view_layer.objects.active=sw[0]
 path=OUT/(era+'-seven-family.glb');bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=False,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_animations=False,export_extras=True)
 # Display swatches only, with the same two light rig values as character tests.
 for o in s.objects:o.hide_render=o not in sw
 from mathutils import Vector
 cfg=mod('lighting02').profiles()['neutral'];world=bpy.data.worlds.new('Swatch neutral');world.use_nodes=True;s.world=world;world.node_tree.nodes['Background'].inputs[0].default_value=(*cfg['world_color'],1);world.node_tree.nodes['Background'].inputs[1].default_value=cfg['world_strength']
 for i,a in enumerate(cfg['areas']):
  d=bpy.data.lights.new('Swatch area '+str(i),'AREA');o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=Vector(a['position'])+Vector((3.6,0,3));o.rotation_euler=(Vector((3.6,0,0))-o.location).to_track_quat('-Z','Y').to_euler();d.energy=a['power']*2;d.color=a['color'];d.size=a['size']
 d=bpy.data.cameras.new('Swatch camera');cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);s.camera=cam;cam.location=(3.6,-.01,8);cam.rotation_euler=(Vector((3.6,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=9.0
 s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=240;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=True;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.render.filepath=str(OUT/(era+'-seven-family.png'));bpy.ops.render.render(write_still=True)
 print('METAL05_SWATCH',era,path,flush=True)
