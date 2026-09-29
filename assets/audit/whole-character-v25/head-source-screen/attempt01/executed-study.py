from pathlib import Path
import bpy,json,hashlib,runpy,shutil,math
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v25-head-mass/attempt01');OUT.mkdir(exist_ok=False)
BASE=ROOT/'assets/models/whole-character-v24/attempt-form02/murderbird-whole-character-v24.blend';SRC=ROOT/'scripts/regions/whole-character-v25-head-mass.py';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(BASE)=='acb91013e0ca7cf98475e0d2ba6fb36d9c081c29c91b27e104bf7367d57f306d'
bpy.ops.wm.open_mainfile(filepath=str(BASE));bpy.context.view_layer.update();h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'));before=h['scene_snapshot']();mats={m.name:h['material_signature'](m) for m in bpy.data.materials};shutil.copyfile(SRC,OUT/'executed-head-mass.py');shutil.copyfile(__file__,OUT/'executed-study.py')
lib=runpy.run_path(str(OUT/'executed-head-mass.py'));result=lib['apply']();after=h['scene_snapshot']();assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
# Evaluated uniform-map witnesses against an independently reopened source.
expected={};dg=bpy.context.evaluated_depsgraph_get();changed=result['changedMeshes'];pivot=Vector(result['transformContract']['pivotNativeWorld'])
for n in changed:
 o=bpy.data.objects[n];ev=o.evaluated_get(dg);m=ev.to_mesh();expected[n]=[ev.matrix_world@v.co for v in m.vertices];ev.to_mesh_clear()
bpy.context.preferences.filepaths.save_version=0;native=OUT/'head-mass.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(BASE));errors=[];counts=[];independentbounds=[]
dg=bpy.context.evaluated_depsgraph_get()
for n in changed:
 o=bpy.data.objects[n];ev=o.evaluated_get(dg);m=ev.to_mesh();p=[pivot+1.30*(ev.matrix_world@v.co-pivot) for v in m.vertices];ev.to_mesh_clear();assert len(p)==len(expected[n]),n;err=max((a-b).length for a,b in zip(p,expected[n]));assert err<2e-6,(n,err);errors.append(err);independentbounds.append({'name':n,'expected':lib['bounds'](p),'actual':lib['bounds'](expected[n]),'maximumEvaluatedWorldErrorM':err})
bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after;assert sha(BASE)=='acb91013e0ca7cf98475e0d2ba6fb36d9c081c29c91b27e104bf7367d57f306d'
receipt={'baseSHA256':sha(BASE),'sourceSHA256':sha(SRC),'nativeSHA256':sha(native),'rendererSHA256':sha(Path(__file__)),'result':result,'independentEvaluatedMapWitnesses':independentbounds,'maximumEvaluatedUniformMapErrorM':max(errors),'saveReopenExact':True,'materialSignaturesExact':True,'views':[]};(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
d=bpy.data.cameras.new('V25 temporary mass camera');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam
views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5,0),('front',(0,-7,1.65),(0,-.08,1.02),2.5,0),('side',(-7,0,1.35),(0,-.08,1.02),2.5,0),('jaw-open',(-6,-3.5,2.6),(0,-.40,1.78),1.10,.32)]
for label,pos,target,scale,jaw in views:
 bpy.data.objects['jaw'].rotation_euler.x=jaw;bpy.context.view_layer.update();cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;scene.render.filepath=str(OUT/f'after-{label}.png');bpy.ops.render.render(write_still=True);receipt['views'].append({'name':label,'path':scene.render.filepath,'sha256':sha(Path(scene.render.filepath)),'jawPitchNativeX':jaw,'camera':{'position':pos,'target':target,'orthoScale':scale}});(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ('sourceSHA256','nativeSHA256','saveReopenExact','maximumEvaluatedUniformMapErrorM')}))
