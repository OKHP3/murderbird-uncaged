"""Authoring-side PBR proof and matched clay silhouettes; no source mutation."""
from pathlib import Path
import bpy,math,json
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/audit/exterior-v1';OUT.mkdir(exist_ok=True,parents=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/models/uncaged-exterior-v1/murderbird-exterior-v1.blend'))
scene=bpy.context.scene;scene.frame_set(1)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=20;scene.cycles.use_denoising=True
scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.35,.35,.35,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
def light(name,pos,power,size,color):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler();return d
key=light('Neutral large key',(-3,-4,5),700,4,(1,1,1));fill=light('Neutral large fill',(3,-1,3),450,3,(1,1,1));rim=light('Neutral rear',(1,3,4),550,3,(1,1,1))
floor=bpy.data.materials.new('Review floor');floor.diffuse_color=(.14,.16,.17,1);floor.use_nodes=True;floor.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.14,.16,.17,1);floor.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.002));bpy.context.object.data.materials.append(floor)
d=bpy.data.cameras.new('Review camera');cam=bpy.data.objects.new('Review camera',d);scene.collection.objects.link(cam);scene.camera=cam;d.type='ORTHO';d.ortho_scale=2.55
def aim(pos,target,scale=2.55):cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale
def era(e):
 for o in scene.objects:
  if o.type=='MESH' and o.get('exteriorEras'):o.hide_render=e not in o['exteriorEras'].split(',');o.hide_set(False)
def render(name):scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
aim((-4.7,-6.5,2.35),(0,-.06,1.05))
for e in ['maker','mechanic','builder']:
 era(e);render(e+'-authoring-neutral')
# Maker/Mechanic illustrations face the other direction. Use the opposite
# three-quarter camera for those source-comparison pairs, without mirroring art.
aim((4.7,-6.5,2.35),(0,-.06,1.05))
for e in ['maker','mechanic']:
 era(e);render(e+'-reference-angle')
# Consistent clay silhouettes isolate form from PBR response.
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studio_light='paint.sl';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.53,.56,.58);scene.display.shading.show_shadows=False;scene.display.shading.show_cavity=True
era('builder')
for name,pos,target,scale in [('front',(0,-6,1.04),(0,0,1.04),2.55),('side',(-6,0,1.04),(0,-.08,1.04),2.55),('three-quarter',(-4.7,-6.5,2.35),(0,-.06,1.05),2.55),('rear',(0,6,1.04),(0,0,1.04),2.55),('head',(-4,-6,2.15),(0,-.3,1.74),1.18)]:
 aim(pos,target,scale);render('exterior-clay-'+name)
print('AUTHORING_PBR_AND_SILHOUETTES_RENDERED')
