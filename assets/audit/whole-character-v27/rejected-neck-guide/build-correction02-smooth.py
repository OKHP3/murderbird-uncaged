from pathlib import Path
import bpy,runpy,json,hashlib,shutil,math,bmesh
from mathutils import Vector,Matrix
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v27-neck-guide/correction02-smooth');OUT.mkdir(exist_ok=False);BASE=ROOT/'assets/models/whole-character-v26/attempt-form01/murderbird-whole-character-v26.blend';SRC=ROOT/'scripts/regions/whole-character-v27-neck-guide.py';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(BASE)=='f897b3310af0c9d8b5e079484bcd9b8863e35c12e6b2be26601ad56700b65564'
for p,n in [(SRC,'executed-region.py'),(Path(__file__),'executed-builder.py'),(ROOT/'scripts/build-uncaged-alignment-v7.py','snapshot.py'),(ROOT/'assets/audit/whole-character-v25/rejected-neck-source-screen/baseline.py','pose-screen.py')]:shutil.copyfile(p,OUT/n)
h=runpy.run_path(str(OUT/'snapshot.py'));bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']();mats={m.name:h['material_signature'](m) for m in bpy.data.materials};mod=runpy.run_path(str(OUT/'executed-region.py'));result=mod['apply']();after=h['scene_snapshot']();owned=set(result['reparentedGuards']);deltas=[]
for n,s in before['empties'].items():
 if after['empties'][n]!=s:deltas.append(n)
protected=[n for n,s in before['meshes'].items() if n not in owned and after['meshes'][n]!=s];assert not protected,protected;assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
solids=[];dg=bpy.context.evaluated_depsgraph_get()
for n in result['addedMeshes']:
 o=bpy.data.objects[n];ev=o.evaluated_get(dg);m=ev.to_mesh();bm=bmesh.new();bm.from_mesh(m);solids.append({'name':n,'finite':all(math.isfinite(c) for v in m.vertices for c in v.co),'closed':all(e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True)});bm.free();ev.to_mesh_clear()
native=OUT/'murderbird-v27-neck-guide.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
tools=runpy.run_path(str(OUT/'pose-screen.py'),run_name='tooling');tools['configure'].__globals__['BASE']=native;tools['configure']();scene=bpy.context.scene
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('V27 guide review camera');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam
receipt={'baseSha256':sha(BASE),'sourceSha256':sha(SRC),'nativeSha256':sha(native),'result':result,'originalNodeSnapshotDeltas':deltas,'outsideExact':True,'materialsExact':True,'solids':solids,'saveReopenExact':True,'views':[]}
for state in tools['STATES']:
 tools['pose'](state);mod['proof_update']()
 if state[0] in ('rest','maker-neck-jaw','contact-neck'):
  for label,pos,target,scale in [('neck',(-6,-3.5,2.45),(0,-.27,1.48),1.4),('front',(0,-6,1.48),(0,-.25,1.48),1.25)]:
   d.ortho_scale=scale;cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/f'{state[0]}-{label}.png');bpy.ops.render.render(write_still=True);receipt['views'].append({'path':scene.render.filepath,'sha256':sha(Path(scene.render.filepath))})
 if state[0]=='rest':
  d.ortho_scale=2.35;cam.location=(-6,-3.5,2.45);cam.rotation_euler=(Vector((0,-.1,1.05))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/'whole-reference-angle.png');bpy.ops.render.render(write_still=True)
 (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('COARSE_RENDERED',str(OUT),flush=True)
