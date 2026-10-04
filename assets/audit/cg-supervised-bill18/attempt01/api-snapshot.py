"""BILL18 source-informed formed bill plates; exact receiving originals preserved."""
import bpy, json, math, hashlib, sys, importlib.util, datetime
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
HEAD17=Path('/Users/okh/.codex/worktrees/cg-supervised-layered-crown17/murderbird-uncaged')
INPUT=HEAD17/'assets/audit/cg-supervised-head17/attempt02/layered-head17.blend'
EXPECTED='f95a7372f1af386ced4c7babda0ed250a99bb3760d6f78659804916ec9a12a2a'
BASE06=BASE/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'
EXPECTED06='72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4'
HIDE=('CGH04 nine section convex hooked upper bill','CGH06 formed bill saddle side panel L','CGH06 formed bill saddle side panel R')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
 sp=importlib.util.spec_from_file_location('b18_'+p.stem,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def apply(scene,root=None,era='builder'):
 if era not in ('maker','mechanic','builder'):raise ValueError(era)
 if any(o.get('cgSupervisedBill18') for o in scene.objects):raise RuntimeError('Reload preserved receiving scene')
 for n in HIDE:
  if n not in scene.objects or scene.objects[n].hide_render:raise RuntimeError('Expected visible receiving bill '+n)
 frame=scene.objects['CG2b head frame'].matrix_world.copy();made=[]
 # Same-era graph identities are reused; no material node or image edits.
 def family(f):
  candidates=[m for m in bpy.data.materials if m.get('cgMetal05Family')==f and m.get('cgMetal05Era')==era]
  if not candidates:raise RuntimeError('No same-era graph '+f)
  return candidates[0]
 mats=[family(f) for f in ('machined-steel','black-iron','worn-bronze')]
 def p(px,py,d):return (d,(788-px)*.0012+.005,(188-py)*.0012+.020)
 def mesh(label,vs,fs,controls):
  name='CGH18 '+label;d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.matrix_world=frame
  o['cgSupervisedBill18']=True;o['cg1cRegion']='head';o['cg2bRegion']='head';o['surfaceRole']='machined-steel';o['cgSurfaceFamilies']='["machined-steel","black-iron","worn-bronze"]';o['constructionStatus']='Two source-informed formed bill plates and compact inward root returns; depth/count proposal; open gape retained';o['cageControls']=json.dumps(controls)
  for m in mats:d.materials.append(m)
  uv=d.uv_layers.new(name='bill18-normalized-local');lo=[min(v.co[a] for v in d.vertices) for a in (1,2)];hi=[max(v.co[a] for v in d.vertices) for a in (1,2)]
  for f in d.polygons:
   f.use_smooth=True
   for li in f.loop_indices:
    q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=((q.y-lo[0])/max(hi[0]-lo[0],1e-6),(q.z-lo[1])/max(hi[1]-lo[1],1e-6))
  so=o.modifiers.new('thin inward formed plate wall','SOLIDIFY');so.thickness=.0018;so.offset=-1;so.material_offset=1;so.material_offset_rim=1
  b=o.modifiers.new('small formed metal edge','BEVEL');b.width=.00035;b.segments=2
  made.append(o);return o
 bill=[(220,907,10,.091),(237,916,27,.108),(266,921,40,.101),(298,919,49,.085),(332,918,51,.065),(366,927,37,.047),(397,925,27,.032),(430,910,16,.015),(460,885,.8,.0012)]
 # Open posterior shell seam has genuine inward lips. All original deep-hook
 # outer control sections and tip retained; the cuff overlaps internally.
 def shell(label,rr,inset=0):
  vs=[];n=33
  for py,px,r,w in rr:
   for k in range(n):
    a=-math.pi+.085+(math.tau-.17)*k/(n-1);fold=.0028*max(0,1-min(k,n-1-k)/1.5)
    vs.append(p(px+(r-inset/.0012)*math.cos(a),py,(w-inset-fold)*math.sin(a)))
  fs=[(j*n+k,j*n+k+1,(j+1)*n+k+1,(j+1)*n+k) for j in range(len(rr)-1) for k in range(n-1)]
  return mesh(label,vs,fs,rr)
 cuff=[(175,887,16,.102),(195,899,18,.099),bill[0],bill[1],bill[2],(277,920.3,43.1,.0961)]
 shell('formed dorsal bill root cuff',cuff,.0013)
 shell('formed distal hooked bill plate',bill[2:])
 # Compact shallow side returns reach under the protected cheek-root boundary.
 # No fill across the gape, aperture depth is unknown.
 for side,label in [(-1,'L'),(1,'R')]:
  rr=[(869,187,.128),(883,205,.125),(896,227,.112),(909,249,.103),(915,271,.095)]
  vs=[]
  for j,(px,py,dep) in enumerate(rr):
   for u in [0,.13,.55,.90,1]:
    vs.append(p(px-13*u,py+8*u,side*(dep+.003*math.sin(math.pi*u)-.009*u*u)))
  fs=[(j*5+k,j*5+k+1,(j+1)*5+k+1,(j+1)*5+k) for j in range(len(rr)-1) for k in range(4)]
  if side<0:fs=[tuple(reversed(f)) for f in fs]
  mesh('compact posterior bill root return '+label,vs,fs,rr)
 for n in HIDE:scene.objects[n].hide_render=True;scene.objects[n].hide_set(True)
 bpy.context.view_layer.update()
 return {'era':era,'new_objects':[o.name for o in made],'hidden_originals':list(HIDE),'material_graphs':[m.name for m in mats],'original_bill_controls':bill,'tip_local':p(885,460,.0012),'construction':'Two broad thin curved plates with inward folded free edges plus compact root returns; not seam-only decoration','proposal_only':True,'artistic_acceptance':False}

def run():
 out=ROOT/'assets/audit/cg-supervised-bill18/attempt01';out.mkdir(parents=True,exist_ok=True)
 assert sha(INPUT)==EXPECTED;assert sha(BASE06)==EXPECTED06
 h=load(HEAD17/'scripts/cg-supervised-head17.py');pres=load(BASE/'scripts/cg-supervised-preservation.py')
 bpy.ops.wm.open_mainfile(filepath=str(INPUT));scene=bpy.context.scene;before=h.snap();maps=pres.packed_image_snapshot();pres.retain_packed_image_ids(scene)
 report=apply(scene,ROOT,'builder');report.update(input_path=str(INPUT),input_sha256=EXPECTED,baseline06_sha256=EXPECTED06,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cameras={})
 native=out/'formed-bill18.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;after=h.snap()
 report['early_preservation']={'receiving_objects':len(before['objects']),'materials':len(before['materials']),'file_images':sum(v['source']=='FILE' for v in before['images'].values()),'packed':pres.verify_receiving_images(maps),'payload_changes':[n for n,v in before['objects'].items() if after['objects'].get(n)!=v],'graph_changes':[n for n,v in before['materials'].items() if after['materials'].get(n)!=v],'file_image_changes':[n for n,v in before['images'].items() if v['source']=='FILE' and after['images'].get(n)!=v],'visibility_changes':[n for n,v in before['visibility'].items() if after['visibility'].get(n)!=v]}
 assert not any(report['early_preservation'][k] for k in ('payload_changes','graph_changes','file_image_changes'));assert set(report['early_preservation']['visibility_changes'])==set(HIDE)
 report['mesh_checks']=[]
 for n in report['new_objects']:
  o=scene.objects[n];uv=[v for d in o.data.uv_layers.active.data for v in d.uv];report['mesh_checks'].append({'name':n,'vertices':len(o.data.vertices),'finite':all(math.isfinite(v) for q in o.data.vertices for v in q.co) and all(math.isfinite(v) for v in uv),'uv_range':[min(uv),max(uv)]})
 def write():
  report['image_hashes']={p.name:sha(p) for p in out.glob('*.png')};(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
 write();print('BILL18_NATIVE_REOPEN_PRESERVED',report['early_preservation'],flush=True)
 ref=json.loads((HEAD17/'assets/audit/cg-supervised-head17/attempt02/receipt.json').read_text());camera=scene.camera
 scene.render.engine='CYCLES';scene.cycles.samples=4;scene.cycles.use_denoising=True;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 clay=bpy.data.materials.new('CGH18 diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.75
 def render(view,mode):
  key='after-'+mode+'-'+view;rc=ref['cameras'][key];camera.matrix_world=Matrix(rc['matrix']);camera.data.ortho_scale=rc['scale'];camera.data.shift_x,camera.data.shift_y=rc['shift'];scene.render.resolution_x,scene.render.resolution_y=rc['resolution'];scene.view_layers[0].material_override=clay if mode=='clay' else None;scene.render.filepath=str(out/(key+'.png'));bpy.context.view_layer.update();bpy.ops.render.render(write_still=True);report['cameras'][key]=rc;write();print('BILL18_RENDERED',key,flush=True)
 for view in ['source-full-bird','head-profile']:
  for mode in ['clay','pbr']:render(view,mode)
 print('BILL18_FIRST_FOUR_COMPLETE',flush=True)
 if '--first' in sys.argv:return
 for view in ['head-grazing','head-far-profile','head-front']:
  for mode in ['clay','pbr']:render(view,mode)
 scene.view_layers[0].material_override=None
 rc=ref['cameras']['after-pbr-source-full-bird'];camera.matrix_world=Matrix(rc['matrix']);camera.data.ortho_scale=rc['scale'];camera.data.shift_x,camera.data.shift_y=rc['shift'];scene.render.resolution_x,scene.render.resolution_y=rc['resolution'];bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False)
 report['native_sha256']=sha(native);report['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write();print('BILL18_COMPLETE',flush=True)
if __name__=='__main__':run()
