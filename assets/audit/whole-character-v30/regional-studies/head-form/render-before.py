from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
OUT=Path('/tmp/v30-head-form/attempt01');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/whole-character-v29/attempt-fit01/murderbird-whole-character-v29.blend');bpy.ops.wm.open_mainfile(filepath=str(base));r={'baseSHA256':sha(base),'executedRendererSHA256':sha(Path(__file__)),'views':[]}
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('V30 temporary head study');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam
for label,pos,target,scale,jaw in [('whole',(-6,-3.5,2.75),(0,-.08,1.02),2.5,0),('head',(-6,-2.4,2.15),(0,-.50,1.77),.95,0),('side',(-6,-.50,1.77),(0,-.50,1.77),.95,0),('jaw-open',(-6,-2.4,2.15),(0,-.50,1.77),.95,.32),('front',(0,-6,1.9),(0,-.50,1.77),.95,0)]:
 bpy.data.objects['jaw'].rotation_euler.x=jaw;bpy.context.view_layer.update();cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;scene.render.filepath=str(OUT/('before-'+label+'.png'));bpy.ops.render.render(write_still=True);r['views'].append({'name':label,'path':scene.render.filepath,'sha256':sha(Path(scene.render.filepath)),'jawNativeX':jaw,'camera':{'position':pos,'target':target,'orthoScale':scale}});(OUT/'before-render-receipt.json').write_text(json.dumps(r,indent=2)+'\n')
