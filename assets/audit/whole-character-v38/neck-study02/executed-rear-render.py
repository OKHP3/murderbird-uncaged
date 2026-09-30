"""Read-only matched rear supplement; never changes native model."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
base,candidate,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not (out/'rear-media.json').exists();rows=[]
for prefix,path in [('baseline',base),('candidate',candidate)]:
 digest=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene
 for o in bpy.data.objects:
  if o.type=='MESH':o.hide_render=o.get('authoringGuide') is True or 'builder' not in str(o.get('exteriorEras','maker,mechanic,builder')).split(',')
  elif o.type=='CURVE':o.hide_render=True
 scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
 scene.render.resolution_x=scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';data=bpy.data.cameras.new('Matched rear supplement');data.type='ORTHO';cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam
 for label,pos,target,scale in [('full-bird-rear',(0,7,2.2),(0,-.08,1.03),2.4),('neck-rear',(0,7,1.6),(0,-.32,1.48),.8)]:
  image=out/f'{prefix}-{label}.png';assert not image.exists();cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale;scene.render.filepath=str(image);bpy.ops.render.render(write_still=True)
  rows.append({'path':str(image),'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'nativeSha256':digest,'camera':{'position':pos,'target':target,'orthoScale':scale},'size':[1200,1200]})
 assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
(out/'rear-media.json').write_text(json.dumps({'status':'matched neutral rear native supplement; no runtime acceptance','scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'views':rows},indent=2)+'\n')
