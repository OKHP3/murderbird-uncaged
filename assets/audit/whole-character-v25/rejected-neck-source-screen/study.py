from pathlib import Path
import bpy,bmesh,runpy,json,hashlib,shutil,math
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v25-neck-laps/attempt01');OUT.mkdir(exist_ok=False);SRC=ROOT/'scripts/regions/whole-character-v25-neck-laps.py';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();tools=runpy.run_path('/tmp/v25-neck-laps/baseline.py',run_name='tooling');tools['configure']();h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'));mats={m.name:h['material_signature'](m) for m in bpy.data.materials};shutil.copyfile(SRC,OUT/'executed-neck-laps.py');shutil.copyfile(__file__,OUT/'executed-study.py');shutil.copyfile('/tmp/v25-neck-laps/baseline.py',OUT/'executed-pose-screen.py');module=runpy.run_path(str(OUT/'executed-neck-laps.py'));result=module['apply']();after=h['scene_snapshot']();assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
solids=[];dg=bpy.context.evaluated_depsgraph_get()
for n in result['changedMeshes']:
 o=bpy.data.objects[n];ev=o.evaluated_get(dg);m=ev.to_mesh();assert all(math.isfinite(c) for v in m.vertices for c in v.co);bm=bmesh.new();bm.from_mesh(m);solids.append({'name':n,'closed':all(e.is_manifold for e in bm.edges),'volume':bm.calc_volume(signed=True)});bm.free();ev.to_mesh_clear()
bpy.context.preferences.filepaths.save_version=0;native=OUT/'neck-laps.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('V25 lap camera');d.type='ORTHO';d.ortho_scale=1.40;cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam;cam.location=(-6,-3.5,2.45);cam.rotation_euler=(Vector((0,-.27,1.48))-cam.location).to_track_quat('-Z','Y').to_euler()
receipt={'baseSha256':sha(tools['BASE']),'sourceSha256':sha(SRC),'nativeSha256':sha(native),'result':result,'solids':solids,'saveReopenExact':True,'materialsExact':True,'poses':[],'views':[]}
for state in tools['STATES']:
 r=tools['screen'](state);receipt['poses'].append(r)
 if state[0] in ('rest','maker-neck-jaw','contact-neck'):
  scene.render.filepath=str(OUT/f'{state[0]}.png');bpy.ops.render.render(write_still=True);receipt['views'].append({'pose':state[0],'path':scene.render.filepath,'sha256':sha(Path(scene.render.filepath))})
 (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'sourceSha256':sha(SRC),'poses':[(p['pose'],p['pairCount']) for p in receipt['poses']],'closedPositive':sum(p['closed'] and p['volume']>0 for p in solids)}))
