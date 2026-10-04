"""CHEEK19 final broad cheek/root construction trial; exact receiving originals preserved."""
import bpy, json, math, hashlib, sys, importlib.util, datetime
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
HEAD17=Path('/Users/okh/.codex/worktrees/cg-supervised-layered-crown17/murderbird-uncaged')
INPUT=BASE/'assets/audit/cg-supervised-bill18/attempt02/formed-bill18.blend'
EXPECTED='abc993f59b327db2916960c06e15307963f3a820fc18c39bce1b6a05cc83bf15'
BASE06=BASE/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'
EXPECTED06='72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4'
HIDE=()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
 sp=importlib.util.spec_from_file_location('b18_'+p.stem,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def apply(scene,root=None,era='builder'):
 if era=='advanced':era='builder'
 if era not in ('maker','mechanic','builder'):raise ValueError(era)
 if any(o.get('cgSupervisedCheek19') for o in scene.objects):raise RuntimeError('Reload immutable receiving scene')
 frame=scene.objects['CG2b head frame'].matrix_world.copy();made=[]
 def family(f):
  candidates=[m for m in bpy.data.materials if m.get('cgMetal05Family')==f and m.get('cgMetal05Era')==era]
  if not candidates:raise RuntimeError('No same-era graph '+f)
  return candidates[0]
 mats=[family(f) for f in ('head-armor','black-iron','worn-bronze','machined-steel')]
 def p(px,py,d):return (d,(788-px)*.0012+.005,(188-py)*.0012+.020)
 def mesh(label,vs,fs,controls,role):
  name='CGH19 '+label;d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.matrix_world=frame
  o['cgSupervisedCheek19']=True;o['cg1cRegion']='head';o['cg2bRegion']='head';o['surfaceRole']=role;o['cgSurfaceFamilies']='["head-armor","black-iron","worn-bronze","machined-steel"]';o['constructionStatus']='Broad curved cheek sweep and recessed concave root sheet; source-informed visible construction, unseen depth proposal';o['cageControls']=json.dumps(controls)
  for m in mats:d.materials.append(m)
  uv=d.uv_layers.new(name='cheek19-normalized-local');lo=[min(v.co[a] for v in d.vertices) for a in (1,2)];hi=[max(v.co[a] for v in d.vertices) for a in (1,2)]
  for f in d.polygons:
   f.use_smooth=True;f.material_index=0 if role=='head-armor' else 1
   for li in f.loop_indices:
    q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=((q.y-lo[0])/max(hi[0]-lo[0],1e-6),(q.z-lo[1])/max(hi[1]-lo[1],1e-6))
  sm=o.modifiers.new('smooth formed cheek cage','SUBSURF');sm.levels=sm.render_levels=2
  so=o.modifiers.new('thin inward formed cheek shell','SOLIDIFY');so.thickness=.002;so.offset=-1;so.material_offset=1;so.material_offset_rim=1
  b=o.modifiers.new('formed edge bevel','BEVEL');b.width=.00035;b.segments=2
  made.append(o);return o
 # Broad outer cheek rail follows the July under-optic sweep, bends inward
 # at both margins and continues into the retained CHEEK19 rear cuff.
 # A curved concave root sheet behind it densifies the empty pocket while
 # retaining a clear anterior mouth aperture. No original mesh is hidden.
 rail=[(664,213,.127,669,243,.127),(686,223,.150,695,260,.151),(715,245,.164,729,279,.151),(750,264,.163,761,293,.143),(786,269,.159,795,296,.131),(820,261,.151,829,291,.124),(850,242,.139,861,277,.113),(877,232,.116,899,276,.097),(899,244,.102,916,292,.084)]
 wall=[(687,249,.124,704,278,.123),(715,266,.127,738,305,.119),(749,282,.122,769,331,.107),(784,289,.114,799,349,.088),(814,279,.106,823,347,.070),(842,271,.091,843,329,.052),(868,269,.078,860,307,.042)]
 for side,label in [(-1,'L'),(1,'R')]:
  for kind,rr,role in [('broad suboptic cheek sweep',rail,'head-armor'),('recessed rearward cheek root wall',wall,'black-iron')]:
   vs=[];cols=9
   for j,(tx,ty,td,bx,by,bd) in enumerate(rr):
    for k in range(cols):
     u=k/(cols-1);dep=td+(bd-td)*u
     if role=='head-armor':dep+=.007*math.sin(math.pi*u)-.006*max(0,1-min(u,1-u)/.15)**2
     else:dep-=.022*math.sin(math.pi*u)
     vs.append(p(tx+(bx-tx)*u,ty+(by-ty)*u,side*dep))
   fs=[(j*cols+k,j*cols+k+1,(j+1)*cols+k+1,(j+1)*cols+k) for j in range(len(rr)-1) for k in range(cols-1)]
   if side<0:fs=[tuple(reversed(f)) for f in fs]
   mesh(kind+' '+label,vs,fs,rr,role)
 bpy.context.view_layer.update()
 return {'era':era,'new_objects':[o.name for o in made],'hidden_originals':[],'material_graphs':[m.name for m in mats],'construction':'Broad thin shell cheek sweep with curved folded margins; recessed concave root sheet; actual anterior jaw aperture remains open','proposal_only':True,'artistic_acceptance':False,'depth_status':'inferred camera-relative depth, no metrology; unseen rear has no source promise'}

def run():
 out=ROOT/'assets/audit/cg-supervised-cheek19/attempt01';out.mkdir(parents=True,exist_ok=True)
 assert sha(INPUT)==EXPECTED;assert sha(BASE06)==EXPECTED06
 h=load(HEAD17/'scripts/cg-supervised-head17.py');pres=load(BASE/'scripts/cg-supervised-preservation.py')
 bpy.ops.wm.open_mainfile(filepath=str(INPUT));scene=bpy.context.scene;before=h.snap();maps=pres.packed_image_snapshot();pres.retain_packed_image_ids(scene)
 report=apply(scene,ROOT,'builder');report.update(input_path=str(INPUT),input_sha256=EXPECTED,baseline06_sha256=EXPECTED06,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cameras={})
 native=out/'formed-cheek19.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;after=h.snap()
 report['early_preservation']={'receiving_objects':len(before['objects']),'materials':len(before['materials']),'file_images':sum(v['source']=='FILE' for v in before['images'].values()),'packed':pres.verify_receiving_images(maps),'payload_changes':[n for n,v in before['objects'].items() if after['objects'].get(n)!=v],'graph_changes':[n for n,v in before['materials'].items() if after['materials'].get(n)!=v],'file_image_changes':[n for n,v in before['images'].items() if v['source']=='FILE' and after['images'].get(n)!=v],'visibility_changes':[n for n,v in before['visibility'].items() if after['visibility'].get(n)!=v]}
 assert not any(report['early_preservation'][k] for k in ('payload_changes','graph_changes','file_image_changes'));assert set(report['early_preservation']['visibility_changes'])==set(HIDE)
 report['mesh_checks']=[]
 for n in report['new_objects']:
  o=scene.objects[n];uv=[v for d in o.data.uv_layers.active.data for v in d.uv];report['mesh_checks'].append({'name':n,'vertices':len(o.data.vertices),'finite':all(math.isfinite(v) for q in o.data.vertices for v in q.co) and all(math.isfinite(v) for v in uv),'uv_range':[min(uv),max(uv)]})
 def write():
  report['image_hashes']={p.name:sha(p) for p in out.glob('*.png')};(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
 write();print('CHEEK19_NATIVE_REOPEN_PRESERVED',report['early_preservation'],flush=True)
 if '--native-only' in sys.argv:return
 ref=json.loads((BASE/'assets/audit/cg-supervised-bill18/attempt02/receipt.json').read_text());camera=scene.camera
 scene.render.engine='CYCLES';scene.cycles.samples=4;scene.cycles.use_denoising=True;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 clay=bpy.data.materials.new('CGH19 diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.75
 def render(view,mode):
  key='after-'+mode+'-'+view;rc=ref['cameras'][key];camera.matrix_world=Matrix(rc['matrix']);camera.data.ortho_scale=rc['scale'];camera.data.shift_x,camera.data.shift_y=rc['shift'];scene.render.resolution_x,scene.render.resolution_y=rc['resolution'];scene.view_layers[0].material_override=clay if mode=='clay' else None;scene.render.filepath=str(out/(key+'.png'));bpy.context.view_layer.update();bpy.ops.render.render(write_still=True);report['cameras'][key]=rc;write();print('CHEEK19_RENDERED',key,flush=True)
 for view in ['source-full-bird','head-profile']:
  for mode in ['pbr','clay']:render(view,mode)
 print('CHEEK19_FIRST_FOUR_COMPLETE',flush=True)
 if '--first' in sys.argv:return
 for view in ['head-grazing']:
  for mode in ['pbr','clay']:render(view,mode)
 scene.view_layers[0].material_override=None
 rc=ref['cameras']['after-pbr-source-full-bird'];camera.matrix_world=Matrix(rc['matrix']);camera.data.ortho_scale=rc['scale'];camera.data.shift_x,camera.data.shift_y=rc['shift'];scene.render.resolution_x,scene.render.resolution_y=rc['resolution'];bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False)
 bpy.data.materials.remove(clay);bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False);report['native_sha256']=sha(native);report['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write();print('CHEEK19_COMPLETE',flush=True)
if __name__=='__main__':run()
