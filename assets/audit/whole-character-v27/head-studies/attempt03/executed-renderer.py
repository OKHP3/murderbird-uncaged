from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
OUT=Path('/tmp/v27-cranial-wrap/attempt03');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();native=OUT/'cranial-wrap.blend';r=json.loads((OUT/'receipt.json').read_text());assert sha(native)==r['nativeSHA256'];checks=json.loads((OUT/'cover-screen.json').read_text());assert all(p['strictPairCount']==0 for p in checks['poses']);bpy.ops.wm.open_mainfile(filepath=str(native));bpy.context.view_layer.update()
r['rendererSHA256']=sha(Path(__file__));r['views']=[]
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('V27 temporary cranial study');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam
cover=bpy.data.objects['cranial-cover'];cover_rest=cover.location.copy()
for label,pos,target,scale,jaw in [('whole',(-6,-3.5,2.75),(0,-.08,1.02),2.5,0),('head',(-6,-2.4,2.15),(0,-.445,1.75),.95,0),('side',(-6,-.40,1.78),(0,-.445,1.75),.95,0),('jaw-open',(-6,-2.4,2.15),(0,-.445,1.75),.95,.32),('front',(0,-6,1.9),(0,-.445,1.75),.95,0),('cranial-open',(-6,-2.4,2.15),(0,-.445,1.75),.95,0)]:
 cover.location=cover_rest;cover.location.z+=.08 if label=='cranial-open' else 0
 bpy.data.objects['jaw'].rotation_euler.x=jaw;bpy.context.view_layer.update();cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;scene.render.filepath=str(OUT/(label+'.png'));bpy.ops.render.render(write_still=True);r['views'].append({'name':label,'path':scene.render.filepath,'sha256':sha(Path(scene.render.filepath)),'jawNativeX':jaw,'camera':{'position':pos,'target':target,'orthoScale':scale}});(OUT/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')

assert sha(native)==r['nativeSHA256'];print('Native unchanged; rendered after scoped zero cover/receiver pair screen.')
