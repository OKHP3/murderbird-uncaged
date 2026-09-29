from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
A=ROOT/'assets/audit/whole-character-v34/regional-studies/breast-hierarchy/attempt04'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
native=A/'murderbird-breast-hierarchy.blend';assert sha(native)=='d612fe357137bf02b26b36678e64eab51b078815ddb514222d74d56a91aa40f8'
bpy.ops.wm.open_mainfile(filepath=str(native))
bpy.data.objects['breastplate'].rotation_euler.x+=1.1
bpy.context.view_layer.update()
receipt={'nativeSHA256':sha(native),'executedSourceSHA256':sha(Path(__file__)),'breastLocalXDeltaRadians':1.1,'readOnlyNative':True,'views':[]}
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
d=bpy.data.cameras.new('temporary V34 camera');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam
views=[('open-reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('open-breast',(-6,-3.5,2.0),(0,-.20,1.00),1.10)]
for name,pos,target,scale in views:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;scene.render.filepath=str(A/f'after-{name}.png');bpy.ops.render.render(write_still=True);receipt['views'].append({'path':f'after-{name}.png','sha256':sha(Path(scene.render.filepath)),'camera':{'position':pos,'target':target,'orthoScale':scale}});(A/'open-render-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')

assert sha(native)=='d612fe357137bf02b26b36678e64eab51b078815ddb514222d74d56a91aa40f8'
