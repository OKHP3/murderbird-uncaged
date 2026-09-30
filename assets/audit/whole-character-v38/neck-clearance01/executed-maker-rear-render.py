"""Read-only matched Maker rear witness, exact original screen pose functions."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
base,candidate,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not (out/'maker-rear-media.json').exists();source=Path(__file__).resolve().parents[4]/'scripts/validate-neck-guard-envelope.py';media=[]
for prefix,native in [('baseline',base),('candidate',candidate)]:
 digest=hashlib.sha256(native.read_bytes()).hexdigest();sys.argv=['render','--','--model',str(native.resolve()),'--sha',digest,'--output',str((out/'maker-pose-support'/prefix).resolve())]
 namespace={'__file__':str(source),'__name__':'actual_pose_functions'};exec(source.read_text().split("result={'nativeSHA256'")[0],namespace);namespace['pose'](namespace['STATES'][1])
 scene=bpy.context.scene
 for o in bpy.data.objects:
  if o.type=='MESH':o.hide_render=o.get('authoringGuide') is True or 'builder' not in str(o.get('exteriorEras','maker,mechanic,builder')).split(',')
  elif o.type=='CURVE':o.hide_render=True
 scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 data=bpy.data.cameras.new('Matched Maker rear witness');data.type='ORTHO';data.ortho_scale=.65;cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam;position=(-5,7,2.3);target=(0,-.28,1.40);cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();image=out/f'{prefix}-maker-rear-witness.png';assert not image.exists();scene.render.filepath=str(image);bpy.ops.render.render(write_still=True)
 media.append({'path':str(image),'nativeSha256':digest,'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'camera':{'position':position,'target':target,'orthoScale':.65},'pose':namespace['STATES'][1],'size':[1200,1200]});assert hashlib.sha256(native.read_bytes()).hexdigest()==digest
(out/'maker-rear-media.json').write_text(json.dumps({'status':'matched actual authored Maker pose witness; no browser or physical motion certificate','screenPoseSourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'rendererSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'views':media},indent=2)+'\n')
