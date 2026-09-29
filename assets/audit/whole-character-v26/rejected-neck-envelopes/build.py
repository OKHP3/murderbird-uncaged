from pathlib import Path
import bpy,bmesh,runpy,json,hashlib,shutil,math
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v26-neck-envelopes/coarse01');OUT.mkdir(exist_ok=False)
BASE=ROOT/'assets/models/whole-character-v25/attempt-form01/murderbird-whole-character-v25.blend';SRC=ROOT/'scripts/regions/whole-character-v26-neck-envelopes.py';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(BASE)=='b1b9cc889940b32e25e3a0b30a4fd5b98a7025ad0af5076873f35fda908911f6'
for p,n in [(SRC,'executed-region.py'),(Path(__file__),'executed-builder.py'),(ROOT/'scripts/build-uncaged-alignment-v7.py','executed-snapshot-helper.py'),(ROOT/'assets/audit/whole-character-v25/rejected-neck-source-screen/baseline.py','executed-pose-screen.py')]:shutil.copyfile(p,OUT/n)
h=runpy.run_path(str(OUT/'executed-snapshot-helper.py'));tools=runpy.run_path(str(OUT/'executed-pose-screen.py'),run_name='tooling');g=tools['configure'].__globals__;g['BASE']=BASE
bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']();mats={m.name:h['material_signature'](m) for m in bpy.data.materials}
module=runpy.run_path(str(OUT/'executed-region.py'));result=module['apply']();after=h['scene_snapshot']();changed=set(result['changedMeshes']);assert before['empties']==after['empties'];assert before['curves']==after['curves'];assert all(before['meshes'][n]==after['meshes'][n] for n in before['meshes'] if n not in changed);assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
solids=[];dg=bpy.context.evaluated_depsgraph_get()
for n in result['changedMeshes']:
 o=bpy.data.objects[n];ev=o.evaluated_get(dg);m=ev.to_mesh();bm=bmesh.new();bm.from_mesh(m);r={'name':n,'finite':all(math.isfinite(c) for v in m.vertices for c in v.co),'closed':all(e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True),'rigidOwner':o.parent.name,'ownerScale':list(o.parent.matrix_world.to_scale())};solids.append(r);bm.free();ev.to_mesh_clear()
assert all(r['finite'] and r['closed'] and r['signedVolumeM3']>0 for r in solids),[r for r in solids if not(r['finite'] and r['closed'] and r['signedVolumeM3']>0)]
bpy.context.preferences.filepaths.save_version=0;native=OUT/'murderbird-v26-neck-envelopes.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
g['BASE']=native;tools['configure']();scene=bpy.context.scene
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('V26 envelope review camera');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam
receipt={'baseSha256':sha(BASE),'sourceSha256':sha(SRC),'nativeSha256':sha(native),'result':result,'solids':solids,'saveReopenExact':True,'materialsExact':True,'outsideExact':True,'poses':[],'views':[]}
for state in tools['STATES']:
 tools['pose'](state)
 if state[0] in ('rest','maker-neck-jaw','contact-neck'):
  d.ortho_scale=1.40;cam.location=(-6,-3.5,2.45);cam.rotation_euler=(Vector((0,-.27,1.48))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/f'{state[0]}.png');bpy.ops.render.render(write_still=True);receipt['views'].append({'pose':state[0],'path':scene.render.filepath,'sha256':sha(Path(scene.render.filepath))})
 if state[0]=='rest':
  for label,pos in [('front',(0,-6,1.05)),('side',(-6,0,1.05)),('reference-angle',(-6,-3.5,2.45))]:
   d.ortho_scale=2.35;cam.location=pos;cam.rotation_euler=(Vector((0,-.10,1.05))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/f'whole-{label}.png');bpy.ops.render.render(write_still=True);receipt['views'].append({'pose':state[0],'path':scene.render.filepath,'sha256':sha(Path(scene.render.filepath))})
 (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('COARSE_RENDERED',str(OUT),flush=True)
# Read-only paired diagnostics after the early rendered candidate is complete.
def categorized(r):
 for p in r['pairs']:
  names=(p['a'],p['b']);owners=p['owners'];p['category']='owned-neck-or-breast' if all(n in changed for n in names) else 'protected-head-neighbor' if any(o in ['head','jaw','upper-bill','cranial-cover','builder-optics'] for o in owners) else 'protected-body-neighbor'
 r['categories']={c:sum(p['category']==c for p in r['pairs']) for c in ['owned-neck-or-breast','protected-head-neighbor','protected-body-neighbor']};return r
states=tools['STATES']+[('grid-p%.3f-y%.3f'%(q,y),q,y,0,0) for q in (-.14,.1625,.325,.4875,.65) for y in (-.45,-.225,0,.225,.45)]
for label,path in [('candidate',native),('baseline',BASE)]:
 g['BASE']=path;tools['configure']();rows=[categorized(tools['screen'](state)) for state in states];(OUT/f'{label}-strict-screen.json').write_text(json.dumps({'method':'Evaluated loop triangles with mutual plane straddle epsilon 1e-7; finite sampled poses, not continuous or physical proof.','poses':rows},indent=2)+'\n');print(label,[(r['pose'],r['categories']) for r in rows],flush=True)
receipt['poses']=json.loads((OUT/'candidate-strict-screen.json').read_text())['poses'];receipt['baselinePoses']=json.loads((OUT/'baseline-strict-screen.json').read_text())['poses'];(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
