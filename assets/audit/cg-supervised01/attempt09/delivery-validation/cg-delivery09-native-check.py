import bpy,numpy as np,sys,json,math,hashlib,importlib.util,datetime
from pathlib import Path
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');era=sys.argv[-1];preflight='--preflight' in sys.argv;early='--early' in sys.argv
def load(n):
 s=importlib.util.spec_from_file_location(n.replace('-','_'),R/'scripts'/n);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
payload=load('cg-supervised-body12.py');head=load('cg-supervised-head17.py')
def val(x):
 if isinstance(x,(str,int,float,bool,type(None))):return x
 if hasattr(x,'name'):return {'id_name':x.name}
 if hasattr(x,'to_dict'):return {k:val(v) for k,v in x.to_dict().items()}
 try:return [val(v) for v in x]
 except:return str(x)
def images():
 return {i.name:{'source':i.source,'filepath':i.filepath,'filepath_raw':i.filepath_raw,'size':list(i.size),'channels':i.channels,'file_format':i.file_format,'colorspace':i.colorspace_settings.name,'alpha_mode':i.alpha_mode,'fake_user':i.use_fake_user,'props':{k:val(v) for k,v in i.items()},'packed_sha256':hashlib.sha256(bytes(i.packed_file.data)).hexdigest() if i.packed_file else None} for i in bpy.data.images if i.source=='FILE'}
def snapshot():
 s=bpy.context.scene;return {'payload':{o.name:payload.digest(o) for o in s.objects if o.type in ('MESH','EMPTY')},'strong_payload':{o.name:head.digest(o) for o in s.objects if o.type in ('MESH','EMPTY')},'graphs':payload.material_digest(),'images':images(),'authoring_guides':{o.name:bool(o.get('authoringGuide')) for o in s.objects if o.type in ('MESH','EMPTY')},'visibility':{o.name:[o.hide_render,o.hide_viewport,o.hide_get()] for o in s.objects if o.type in ('MESH','EMPTY')}}
base=R/f'assets/models/cg-supervised01/attempt06/murderbird-supervised-{era}.blend';native=Path(f'/tmp/cg-delivery09-early-{era}.blend') if early else R/f'assets/models/cg-supervised01/attempt09/murderbird-supervised-{era}.blend';receipt={'module_changes':{}} if preflight or early else json.loads((R/f'assets/audit/cg-supervised01/attempt09/{era}/receipt.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(base));before=snapshot();print('DELIVERY09_BASE_SNAPSHOT',era,flush=True)
if preflight:
 selection=json.loads((R/'assets/audit/cg-supervised01/attempt09/selected-modules.json').read_text());assert selection['root_regional_adjudication_complete']
 for item in selection['review_inputs']:assert hashlib.sha256((R/item['path']).read_bytes()).hexdigest()==item['sha256']
 for name in selection['selected_module_names']:receipt['module_changes'][name]=load(name).apply(bpy.context.scene,R,era)
else:bpy.ops.wm.open_mainfile(filepath=str(native))
after=snapshot();s=bpy.context.scene
changes={k:[n for n,v in before[k].items() if after[k].get(n)!=v] for k in ('payload','strong_payload','graphs','images')};assert not any(changes.values()),changes
assert len(before['payload'])==7424 and len(before['graphs'])==56 and len(before['images'])==160
expected={}
for module,r in receipt['module_changes'].items():
 if not isinstance(r,dict):continue
 names=r.get('hidden_originals',r.get('hiddenOriginals',r.get('hiddenLegacyManifest',[])))
 for n in names:
  if n not in before['visibility']:continue
  q=list(before['visibility'][n]);q[0]=True
  if 'feet' not in module:q[2]=True
  expected[n]=q
if early:expected=json.loads(Path(f'/tmp/cg-delivery09-preflight-{era}.json').read_text())['declared_visibility']
if not preflight and not early:
 n='Finish02 review contact ground.003';assert before['authoring_guides'][n] is True;assert after['authoring_guides'][n] is True;q=list(before['visibility'][n]);q[0]=True;expected[n]=q
actual={n:v for n,v in after['visibility'].items() if n in before['visibility'] and v!=before['visibility'][n]}
expected={n:v for n,v in expected.items() if v!=before['visibility'][n]};assert actual==expected,{'missing':list(set(expected)-set(actual)),'unexpected':list(set(actual)-set(expected)),'values':[n for n in actual if n in expected and actual[n]!=expected[n]]}
new=[o for o in s.objects if o.type=='MESH' and o.name not in before['payload'] and not o.get('authoringGuide')];records={};deps=bpy.context.evaluated_depsgraph_get()
for o in new:
 e=o.evaluated_get(deps);m=e.to_mesh();m.calc_loop_triangles();a=np.empty(len(m.vertices)*3,np.float32);m.vertices.foreach_get('co',a);assert np.isfinite(a).all(),o.name;h=hashlib.sha256(a.tobytes());uvrec=[]
 for uv in m.uv_layers:
  b=np.empty(len(uv.data)*2,np.float32);uv.data.foreach_get('uv',b);assert np.isfinite(b).all(),o.name;h.update(uv.name.encode());h.update(b.tobytes());normalized='normalized' in uv.name.lower() or any(o.get(k) for k in ('cgSupervisedHead17','cgSupervisedBill18','cgSupervisedOptic13','cgSupervisedBody11','cgSupervisedBody12','cgSupervisedBody15','cgSupervisedFeet14'))
  if normalized:
   rawuv=o.data.uv_layers.get(uv.name);c=np.empty(len(rawuv.data)*2,np.float32);rawuv.data.foreach_get('uv',c);assert np.isfinite(c).all() and c.min()>=-1e-6 and c.max()<=1.000001,(o.name,uv.name,'controlUV',c.min(),c.max());assert b.min()>=-1e-4 and b.max()<=1.0001,(o.name,uv.name,'evaluatedUV',b.min(),b.max())
  uvrec.append({'name':uv.name,'min':float(b.min()),'max':float(b.max()),'sha256':hashlib.sha256(b.tobytes()).hexdigest(),'normalized_bound_checked':normalized,'evaluated_tolerance':1e-4 if normalized else None,'control_tolerance':1e-6 if normalized else None,'control_min':float(c.min()) if normalized else None,'control_max':float(c.max()) if normalized else None,'evaluated_overshoot':bool(normalized and (b.min()<0 or b.max()>1)),'modifier_types':[q.type for q in o.modifiers]})
 h.update(repr([tuple(p.vertices) for p in m.polygons]).encode());h.update(repr(tuple(tuple(x) for x in o.matrix_world)).encode());slots=[x.name if x else None for x in m.materials];assert all(p.material_index<len(slots) and slots[p.material_index] for p in m.polygons),o.name
 if o.get('cgSupervisedBill18'):
  control=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',control);np.savez('/tmp/cg-delivery09-bill-'+era+'-'+str(sum(k.startswith('CGH18') for k in records))+'.npz',positions=a.reshape((-1,3)),control=control.reshape((-1,3)),matrix=np.array(o.matrix_world),uv=b,faces=np.array([tuple(t.vertices) for t in m.loop_triangles]),name=np.array(o.name))
 records[o.name]={'topology_sha256':hashlib.sha256(repr([tuple(p.vertices) for p in m.polygons]).encode()).hexdigest(),'position_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'matrix_world':[list(row) for row in o.matrix_world],'vertices':len(m.vertices),'polygons':len(m.polygons),'geometry_uv_transform_digest':h.hexdigest(),'determinant':o.matrix_world.to_3x3().determinant(),'slots':slots,'face_slots':sorted(set(p.material_index for p in m.polygons)),'uv':uvrec,'finite':True};e.to_mesh_clear()
 if o.get('cgSupervisedBill18') and any(q['evaluated_overshoot'] and q['max']>1.000001 for q in uvrec):
  bevel=[q for q in o.modifiers if q.type=='BEVEL'];assert bevel;flags=[q.show_viewport for q in bevel]
  try:
   for q in bevel:q.show_viewport=False
   bpy.context.view_layer.update();ee=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mm=ee.to_mesh();pre=[float(c) for layer in mm.uv_layers for x in layer.data for c in x.uv];ee.to_mesh_clear();assert min(pre)>=-1e-6 and max(pre)<=1.000001;records[o.name]['bevel_only_overshoot_confirmed']={'bevel_disabled_uv_min':min(pre),'bevel_disabled_uv_max':max(pre),'all_finite':all(math.isfinite(c) for c in pre)}
  finally:
   for q,flag in zip(bevel,flags):q.show_viewport=flag
   bpy.context.view_layer.update()
result={'era':era,'status':'PASS','base_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'native_sha256':None if preflight else hashlib.sha256(native.read_bytes()).hexdigest(),'original_payloads':len(before['payload']),'original_graphs':len(before['graphs']),'original_file_images':len(before['images']),'preservation_changes':changes,'declared_visibility_exact':True,'approved_stage_guide_retirement':None if preflight or early else 'Finish02 review contact ground.003 hide_render only; originalauthoringGuide true, unchanged payload/matrix/other flags; rootexplicitadjudication','declared_visibility':expected,'new_evaluated_meshes':records,'method':'Reopen immutable06 and final09; project digest plus independent stronger payload and full FILE metadata checks; evaluated regional mesh scan. No saves/render.','limits':['No engineering, continuous clearance, browser or artistic acceptance.','Root authorized evaluated normalized UV tolerance1e-4 at10:56Z; native control bound1e-6. Exact ranges retained; BILL18 evaluated bevel may cause numerical interpolation overshoot. No clamping or payload changes.']}
Path(f'/tmp/cg-delivery09-{'preflight' if preflight else 'early' if early else 'native'}-{era}.json').write_text(json.dumps(result,indent=2));print('DELIVERY09_PREFLIGHT_PASS' if preflight else 'DELIVERY09_EARLY_PASS' if early else 'DELIVERY09_NATIVE_PASS',era,len(records),flush=True)
