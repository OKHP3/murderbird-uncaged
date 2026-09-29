from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector,Quaternion
OUT=Path('/tmp/v29-breast-hinge/attempt02');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();native=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/whole-character-v28/attempt-form02/murderbird-whole-character-v28.blend');assert sha(native)=='838a86b16766ddd4491c9f1cbe6a7aa0039c2b9e8514a04eb710d1e9b2f9bd9d';r={'nativeSHA256':sha(native),'status':'Read-only exact V28 before views at identical study cameras','views':[]};bpy.ops.wm.open_mainfile(filepath=str(native));bpy.context.view_layer.update();r['rendererSHA256']=sha(Path(__file__));r['views']=[]
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('V29 temporary hinge study');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam

rest=bpy.data.objects['breastplate'].rotation_euler.copy()
for label,pos,target,scale,opening in [('whole',(-6,-3.5,2.75),(0,-.08,1.02),2.5,0),('closed',(-6,-3.5,1.25),(0,-.145,.850),.55,0),('open',(-6,-3.5,1.25),(0,-.145,.850),.75,1.1),('open-side',(-6,-.145,.85),(0,-.145,.850),.75,1.1)]:
 bpy.data.objects['breastplate'].rotation_euler=rest;bpy.data.objects['breastplate'].rotation_euler.x+=opening;bpy.context.view_layer.update();cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;scene.render.filepath=str(OUT/('before-'+label+'.png'));bpy.ops.render.render(write_still=True);r['views'].append({'name':label,'path':scene.render.filepath,'sha256':sha(Path(scene.render.filepath)),'camera':{'position':pos,'target':target,'orthoScale':scale},'breastLocalXDelta':opening});(OUT/'before-render-receipt.json').write_text(json.dumps(r,indent=2)+'\n')
assert sha(native)==r['nativeSHA256'];print('Rendered unchanged-native breast study.')
