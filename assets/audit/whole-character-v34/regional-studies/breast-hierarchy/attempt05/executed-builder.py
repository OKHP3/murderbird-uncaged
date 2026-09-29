from pathlib import Path
import bpy,runpy,json,hashlib,shutil,math
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
BASE=ROOT/'assets/models/whole-character-v34/attempt-upper01/murderbird-whole-character-v34.blend'
SHA='eaffa2b19d3ebb5b419797cedbf0ba49971863ef41e942f1cc14eb3ecfab17ba'
A=ROOT/'assets/audit/whole-character-v34/regional-studies/breast-hierarchy/attempt05';assert not A.exists();A.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(BASE)==SHA
shutil.copyfile(__file__,A/'executed-builder.py')
shutil.copyfile(ROOT/'scripts/regions/whole-character-v34-breast-hierarchy.py',A/'executed-breast-hierarchy.py')
h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'))
bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']();mats={m.name:h['material_signature'](m) for m in bpy.data.materials}
m=runpy.run_path(str(A/'executed-breast-hierarchy.py'));m['apply'].__globals__['ROOT']=ROOT;result=m['apply']();after=h['scene_snapshot']();assert before['empties']==after['empties'];assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
native=A/'murderbird-breast-hierarchy.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
receipt={'status':'Coarse mass proposal; no artistic/full-motion acceptance','baseNativeSHA256':SHA,'nativeSHA256':sha(native),'sourceSHA256':sha(A/'executed-breast-hierarchy.py'),'builderSHA256':sha(A/'executed-builder.py'),'result':result,'saveReopenExact':True,'materialsExact':True,'views':[]}
(A/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
d=bpy.data.cameras.new('temporary V34 camera');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam
views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('side',(-7,0,1.35),(0,-.08,1.02),2.5),('breast',(-6,-3.5,2.0),(0,-.20,1.00),1.10),('breast-front',(0,-7,1.0),(0,-.20,1.00),1.10)]
for name,pos,target,scale in views:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;scene.render.filepath=str(A/f'after-{name}.png');bpy.ops.render.render(write_still=True);receipt['views'].append({'path':f'after-{name}.png','sha256':sha(Path(scene.render.filepath)),'camera':{'position':pos,'target':target,'orthoScale':scale}});(A/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert sha(BASE)==SHA
print(json.dumps({'nativeSHA256':receipt['nativeSHA256'],'sourceSHA256':receipt['sourceSHA256'],'changedMeshes':len(result['changedMeshes']),'views':len(receipt['views'])}))
