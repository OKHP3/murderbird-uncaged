from pathlib import Path
import bpy,sys,json,shutil
from mathutils import Vector
root=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');out=root/'assets/audit/whole-character-v34/attempt-shoulder03/diagnostic-colors';out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'executed-colors.py')
bpy.ops.wm.open_mainfile(filepath=str(root/'assets/models/whole-character-v34/attempt-shoulder03/murderbird-whole-character-v34.blend'))
colors={};palette={'body':(.9,.2,.15,1),'breastplate':(.2,.7,.2,1),'left-mantle':(.15,.45,.95,1),'right-mantle':(.15,.45,.95,1),'left-wing-shield':(.6,.2,.9,1),'right-wing-shield':(.6,.2,.9,1)}
for o in bpy.data.objects:
 if o.type=='MESH':
  key=o.parent.name if o.parent else 'none';o.color=palette.get(key,(.65,.65,.65,1));o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',');colors[o.name]=list(o.color)
 elif o.type=='CURVE':o.hide_render=True
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='OBJECT';s.display.shading.light='STUDIO';s.display.shading.show_shadows=False;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.world.color=(.12,.13,.14);s.render.resolution_x=s.render.resolution_y=900;s.render.resolution_percentage=100
cam=bpy.data.objects.new('diagnostic camera',bpy.data.cameras.new('diagnostic camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=1.25;cam.location=(0,-7,1.45);cam.rotation_euler=(Vector((0,-.03,1.20))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(out/'owners-front.png');bpy.ops.render.render(write_still=True)
(out/'colors.json').write_text(json.dumps({'purpose':'Diagnostic owner colors only; native unchanged, not materials or artwork','ownerPalette':palette,'objects':colors},indent=2)+'\n')
