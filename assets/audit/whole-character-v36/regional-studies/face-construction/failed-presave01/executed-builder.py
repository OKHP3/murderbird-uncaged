from pathlib import Path
import bpy,runpy,json,hashlib,shutil
from mathutils import Vector
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');A=R/'assets/audit/whole-character-v36/regional-studies/face-construction/attempt01';M=R/'assets/models/whole-character-v36/regional-studies/face-construction/attempt01';assert not A.exists() and not M.exists();A.mkdir(parents=True);M.mkdir(parents=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base=R/'assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend';S='d2c704ccf89f3f0e7dbeb3613dcdbdd964c4ba69991783783830803eecf59cb0';assert sha(base)==S
shutil.copyfile(__file__,A/'executed-builder.py');src=R/'scripts/regions/whole-character-v36-face-construction.py';shutil.copyfile(src,A/'executed-face-construction.py');hp=R/'scripts/build-uncaged-alignment-v7.py';shutil.copyfile(hp,A/'executed-snapshot-helper.py');h=runpy.run_path(str(hp));helper=R/'scripts/regions/whole-character-v31-head-reconstruction.py';shutil.copyfile(helper,A/'executed-geometry-helper.py');bpy.ops.wm.open_mainfile(filepath=str(base));before=h['scene_snapshot']();mats={m.name:h['material_signature'](m) for m in bpy.data.materials};bpy.context.view_layer.update();module=runpy.run_path(str(A/'executed-face-construction.py'));result=module['apply']();after=h['scene_snapshot']();assert before['empties']==after['empties'];assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials};native=M/'murderbird-face-construction.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
rec={'status':'Coarse visible study; no fit/artistic acceptance','baseSHA256':S,'native':{'path':str(native.relative_to(R)),'sha256':sha(native)},'sourceSHA256':sha(A/'executed-face-construction.py'),'result':result,'saveReopenExact':True,'nodesExact':True,'materialsExact':True,'views':[]};(A/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n')
# Actual V35 camera records for matched head views, plus its whole cameras.
caminput=R/'assets/audit/whole-character-v35/attempt-form01/head-neck-screen/head/executed-v31-camera-input.json';shutil.copyfile(caminput,A/'executed-camera-input.json');inputs=json.loads(caminput.read_text())['views'];views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5,0),('front',(0,-7,1.35),(0,-.08,1.02),2.5,0),('side',(-7,0,1.35),(0,-.08,1.02),2.5,0)]
for v in inputs:
 if v['name'] in ('closed-head','closed-side','closed-front','open-head'):
  c=v['camera'];views.append((v['name'],c['position'],c['target'],c['orthoScale'],v['jawNativeX']))
def setup():
 scene=bpy.context.scene
 for o in bpy.data.objects:
  if o.animation_data:o.animation_data_clear()
  if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
  elif o.type=='CURVE':o.hide_render=True
 scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('V36 matched neutral camera');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam;return scene,cam,d
for stage,path in [('before',base),('after',native)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));scene,cam,d=setup();rest=bpy.data.objects['jaw'].matrix_basis.copy()
 for name,pos,target,scale,jaw in views:
  bpy.data.objects['jaw'].matrix_basis=rest;bpy.data.objects['jaw'].rotation_euler.x+=jaw;bpy.context.view_layer.update();cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;scene.render.filepath=str(A/f'{stage}-{name}.png');bpy.ops.render.render(write_still=True);rec['views'].append({'path':f'{stage}-{name}.png','sha256':sha(Path(scene.render.filepath)),'camera':{'position':pos,'target':target,'orthoScale':scale},'jawNativeX':jaw});(A/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n')
assert sha(base)==S;assert sha(native)==rec['native']['sha256'];print('READY',rec['native']['sha256'],rec['sourceSHA256'])
