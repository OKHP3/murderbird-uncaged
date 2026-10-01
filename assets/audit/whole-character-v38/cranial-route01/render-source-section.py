import bpy
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;R=P.parents[3];bpy.ops.wm.open_mainfile(filepath=str(R/'assets/models/whole-character-v38/neck-fit01/attempt02/murderbird-v38-neck-fit01-attempt02.blend'));scene=bpy.context.scene
show=['V31 passive cranial load bow -1','V31 passive cranial load bow 1','V31 cranial load bow shaft seat -1','V31 cranial load bow shaft seat 1','V21 head captive shaft','V23 cervical 4 captive pin','V23 cervical 4 distal race -1','V23 cervical 4 distal race 1','V23 cervical 4 load link -1','V23 cervical 4 load link 1']
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render=o.name not in show
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';data=bpy.data.cameras.new('temporary section comparison');data.type='ORTHO';cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam;cam.location=(-3,-2,2.6);cam.rotation_euler=(Vector((0,-.392,1.568))-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=.24;scene.render.filepath=str(P/'source-route-section.png');bpy.ops.render.render(write_still=True)
print('SOURCE_SECTION_READY',flush=True)
