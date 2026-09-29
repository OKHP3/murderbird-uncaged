from pathlib import Path
import bpy,bmesh,json,hashlib,runpy,shutil,math
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v30-support-proportion/attempt01');OUT.mkdir(exist_ok=False);BASE=ROOT/'assets/models/whole-character-v29/attempt-fit01/murderbird-whole-character-v29.blend';SRC=ROOT/'scripts/regions/whole-character-v30-support-proportion.py';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(BASE)=='04040543c39e98dd3d20da3d51a5ba40fd87151315ef074d328276eed97c63e7'
bpy.ops.wm.open_mainfile(filepath=str(BASE));bpy.context.view_layer.update();helper=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'));before=helper['scene_snapshot']();materials={m.name:helper['material_signature'](m) for m in bpy.data.materials};shutil.copyfile(SRC,OUT/'executed-support-proportion.py');shutil.copyfile(__file__,OUT/'executed-study.py');result=runpy.run_path(str(OUT/'executed-support-proportion.py'))['apply']();after=helper['scene_snapshot']();assert materials=={m.name:helper['material_signature'](m) for m in bpy.data.materials}
finite=[];dg=bpy.context.evaluated_depsgraph_get()
for n in result['geometryChangedMeshes']:
 o=bpy.data.objects[n];ev=o.evaluated_get(dg);m=ev.to_mesh();points=[ev.matrix_world@v.co for v in m.vertices];assert all(math.isfinite(c) for p in points for c in p),n;bm=bmesh.new();bm.from_mesh(m);finite.append({'name':n,'vertices':len(m.vertices),'finite':True,'closed':all(e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True)});bm.free();ev.to_mesh_clear()
bpy.context.preferences.filepaths.save_version=0;native=OUT/'support-proportion.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert after==helper['scene_snapshot']();assert sha(BASE)=='04040543c39e98dd3d20da3d51a5ba40fd87151315ef074d328276eed97c63e7'
r={'baseSHA256':sha(BASE),'sourceSHA256':sha(SRC),'nativeSHA256':sha(native),'executedStudySHA256':sha(Path(__file__)),'result':result,'finiteMemberEvidence':finite,'materialsExact':True,'saveReopenExact':True,'views':[]};(OUT/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
# Same orthographic cameras/light for before and after, no recenter/crop trick.
views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('front',(0,-7,1.65),(0,-.08,1.02),2.5),('side',(-7,0,1.35),(0,-.08,1.02),2.5)]
for state,path in [('after',native),('before',BASE)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene
 for o in bpy.data.objects:
  if o.animation_data:o.animation_data_clear()
  if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
  elif o.type=='CURVE':o.hide_render=True
 scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('V30 neutral support study');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam
 for label,pos,target,scale in views:
  cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;scene.render.filepath=str(OUT/(state+'-'+label+'.png'));bpy.ops.render.render(write_still=True);r['views'].append({'name':state+'-'+label,'sha256':sha(Path(scene.render.filepath)),'camera':{'position':pos,'target':target,'orthoScale':scale}})
assert sha(native)==r['nativeSHA256'];(OUT/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'sourceSHA256':r['sourceSHA256'],'nativeSHA256':r['nativeSHA256'],'changedNodes':result['changedNodes'],'memberContracts':result['memberEndpoints'],'finiteMembers':len(finite)}))
