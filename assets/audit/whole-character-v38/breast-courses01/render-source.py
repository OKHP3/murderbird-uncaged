from pathlib import Path
import bpy,hashlib
from mathutils import Vector
R=Path("/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged");A=R/"assets/audit/whole-character-v38/breast-courses01";SN=R/"assets/models/whole-character-v38/jaw-stock01/murderbird-v38-jaw-stock01.blend"
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
images=[]
for prefix,model in [('source',SN)]:
 bpy.ops.wm.open_mainfile(filepath=str(model));scene=bpy.context.scene
 for o in bpy.data.objects:
  if o.type=='MESH':o.hide_render=o.get('silhouetteStudyHistoricalHidden')is True or o.get('authoringGuide')is True or 'builder'not in str(o.get('exteriorEras','maker,mechanic,builder')).split(',')
  elif o.type=='CURVE':o.hide_render=True
 scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';data=bpy.data.cameras.new('temporary matched headgape camera');data.type='ORTHO';cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam
 for name,pos,target,scale in [('breast-three-quarter',(-6,-3.5,1.70),(0,-.20,.995),.80),('full-bird-profile',(-6,0,2.0),(0,-.08,1.03),2.4)]:
  cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale;path=A/(prefix+'-'+name+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);images.append({'path':str(path.relative_to(R)),'sha256':sha(path)});print('MEDIA',path,flush=True)
