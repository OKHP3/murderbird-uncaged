from pathlib import Path
import bpy,runpy,json,hashlib,shutil
from mathutils import Vector
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');A=R/'assets/audit/whole-character-v35/regional-studies/torso-integration/attempt05';M=R/'assets/models/whole-character-v35/regional-studies/torso-integration/attempt05';assert not A.exists() and not M.exists();A.mkdir(parents=True);M.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=R/'assets/models/whole-character-v34/attempt-form01/murderbird-whole-character-v34.blend';bound='3f4c12983feea5e4d45f5609d749c1dfa78ecdafc34936d3e702ffa403fed716';assert sha(base)==bound
shutil.copyfile(__file__,A/'executed-builder.py');src=R/'scripts/regions/whole-character-v35-torso-integration.py';shutil.copyfile(src,A/'executed-torso-integration.py')
h=runpy.run_path(str(R/'scripts/build-uncaged-alignment-v7.py'));bpy.ops.wm.open_mainfile(filepath=str(base));before=h['scene_snapshot']();mats={m.name:h['material_signature'](m) for m in bpy.data.materials};module=runpy.run_path(str(A/'executed-torso-integration.py'));module['apply'].__globals__['ROOT']=R;result=module['apply']();after=h['scene_snapshot']();assert before['empties']==after['empties'];assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
native=M/'murderbird-torso-integration.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
rec={'status':'First coarse shape study; no likeness or motion acceptance','baseSHA256':bound,'native':{'path':str(native.relative_to(R)),'sha256':sha(native)},'sourceSHA256':sha(A/'executed-torso-integration.py'),'result':result,'saveReopenExact':True,'nodesExact':True,'materialsExact':True,'views':[]};(A/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n')
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('temporary V35 neutral camera');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam
for name,pos,target,scale in [('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('front',(0,-7,1.35),(0,-.08,1.02),2.5),('side',(-7,0,1.35),(0,-.08,1.02),2.5),('torso',(-6,-3.5,2.0),(0,-.10,1.00),1.15)]:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;scene.render.filepath=str(A/f'after-{name}.png');bpy.ops.render.render(write_still=True);rec['views'].append({'path':f'after-{name}.png','sha256':sha(Path(scene.render.filepath)),'camera':{'position':pos,'target':target,'orthoScale':scale}});(A/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n')
assert sha(base)==bound;print('READY',rec['native']['sha256'],rec['sourceSHA256'])
