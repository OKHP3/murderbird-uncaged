from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v25-head-priority');NATIVE=ROOT/'assets/models/whole-character-v25/attempt-form01/murderbird-whole-character-v25.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();expected='b1b9cc889940b32e25e3a0b30a4fd5b98a7025ad0af5076873f35fda908911f6';assert sha(NATIVE)==expected;bpy.ops.wm.open_mainfile(filepath=str(NATIVE));scene=bpy.context.scene
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';data=bpy.data.cameras.new('V25 read-only head priority');data.type='ORTHO';data.ortho_scale=.95;cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam;receipt={'native':str(NATIVE),'nativeSHA256':expected,'rendererSHA256':sha(Path(__file__)),'status':'Read-only neutral head comparison illustrations; perspective differs from references','views':[]}
for label,pos,jaw in [('rest',(-6,-2.4,2.15),0),('jaw-open',(-6,-2.4,2.15),.32),('side',(-6,-.40,1.78),0)]:
 bpy.data.objects['jaw'].rotation_euler.x=jaw;bpy.context.view_layer.update();cam.location=pos;target=(0,-.445,1.75);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/(label+'.png'));bpy.ops.render.render(write_still=True);receipt['views'].append({'name':label,'path':scene.render.filepath,'sha256':sha(Path(scene.render.filepath)),'camera':{'position':pos,'target':target,'orthoScale':.95},'jawNativeX':jaw})
assert sha(NATIVE)==expected;receipt['nativeUnchanged']=True;(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
