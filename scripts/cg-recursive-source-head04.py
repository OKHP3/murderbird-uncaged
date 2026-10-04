"""HEAD04 design01: closed volume cages from observed contour controls.
Import is inert. All receiving payloads survive unchanged apart from55 named hides.
"""
import bpy,math,json,hashlib,importlib.util,datetime,sys,argparse
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
PLAN='assets/audit/cg-recursive-three-loop01/loop02/source-head04-preparation/plan.json'
PLAN_SHA='d3b78febc62326f2310cb1d5cb5f1f04cd13b2889ee7fece84acf5db1ce3cbdf'
MANIFEST='assets/audit/cg-recursive-three-loop01/loop02-preparation/receiving-manifest-loop02.json'
MANIFEST_SHA='47ed3ee74f0a06a9c470a427f8151dd032b0b48e1c68083f50d092cd1ec3308f'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
 s=importlib.util.spec_from_file_location('head04_'+p.stem.replace('-','_'),p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def apply(scene,root_path,era='builder'):
 base=Path(root_path);assert sha(base/PLAN)==PLAN_SHA
 plan=json.loads((base/PLAN).read_text());retire=plan['proposed_exact_visible_retirements'];assert len(retire)==55
 assert not any(o.get('cgRecursiveSourceHead04') for o in scene.objects)
 for n in retire:assert n in scene.objects and not scene.objects[n].hide_render,n
 for n in plan['protected_exact_objects']:assert n in scene.objects,n
 frame=scene.objects['CG2b head frame'];fm=frame.matrix_world.copy();fi=fm.inverted()
 old=scene.objects['CGH17 frontal crown root'];armor,iron,bronze=old.data.materials[:3]
 assert all(m.get('cgMetal05Era')==era for m in [armor,iron,bronze])
 # Separately named regional dark metal; inherited graphs/images never rebound.
 dark=bpy.data.materials.new('CGRV04 formed dark crown / '+era);dark.use_nodes=True
 bs=dark.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.042,.068,.067,1);bs.inputs['Metallic'].default_value=.78;bs.inputs['Roughness'].default_value=.39
 dark['cgRecursiveSourceHead04']=True;dark['era']=era;dark['scope']='regional head formed metal only'
 mats={'armor':dark,'iron':iron,'bronze':bronze};made=[];proof=[]
 controls={c['id']:Vector(c['world_control_prior']) for c in plan['control_edge_correspondences']}
 def mesh(label,vs,fs,role='armor',subd=1):
  name='CGRV04 '+label;data=bpy.data.meshes.new(name);data.from_pydata([fi@Vector(v) for v in vs],[],fs);data.update();obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.parent=frame;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=Matrix.Identity(4)
  for m in (mats[role],iron,bronze):data.materials.append(m)
  uv=data.uv_layers.new(name='head04-local-normalized')
  ys=[v.co.y for v in data.vertices];zs=[v.co.z for v in data.vertices];lo=(min(ys),min(zs));hi=(max(ys),max(zs))
  for poly in data.polygons:
   poly.use_smooth=True
   for li in poly.loop_indices:
    v=data.vertices[data.loops[li].vertex_index].co;uv.data[li].uv=((v.y-lo[0])/max(hi[0]-lo[0],1e-7),(v.z-lo[1])/max(hi[1]-lo[1],1e-7))
  if subd:
   s=obj.modifiers.new('closed cage curvature','SUBSURF');s.levels=subd;s.render_levels=subd
  for k,v in {'cgRecursiveSourceHead04':True,'cg1cRegion':'head','cg2bRegion':'head','surfaceRole':role,'cgSurfaceFamilies':json.dumps([role,'black-iron','worn-bronze']),'constructionStatus':'Closed volume cage from observed source control priors; likeness pending','sourcePlanSHA':PLAN_SHA,'exteriorEras':'maker,mechanic,builder'}.items():obj[k]=v
  made.append(obj)
  edge_counts={}
  for face in fs:
   for a,b in zip(face,face[1:]+face[:1]):k=tuple(sorted((a,b)));edge_counts[k]=edge_counts.get(k,0)+1
  proof.append({'name':name,'vertices':len(vs),'faces':len(fs),'closed_base_cage':all(n==2 for n in edge_counts.values()),'world_bounds':[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]],'role':role})
  return obj
 def rings(label,sections,role='armor',N=16,subd=1):
  vs=[]
  for center,axis1,axis2 in sections:
   for k in range(N):a=math.tau*k/N;vs.append(Vector(center)+Vector(axis1)*math.cos(a)+Vector(axis2)*math.sin(a))
  fs=[(j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k) for j in range(len(sections)-1) for k in range(N)]
  fs += [tuple(reversed(tuple(range(N)))),tuple((len(sections)-1)*N+k for k in range(N))]
  return mesh(label,vs,fs,role,subd)
 def volume_y(label,rows,role='armor'):
  return rings(label,[(Vector((0,y,z)),Vector((rx,0,0)),Vector((0,0,rz))) for y,z,rx,rz in rows],role)
 # A single closed covered support. It is behind the original optical seats,
 # with actual fitted circular tunnels and a separately bounded cheek recess.
 support=volume_y('connected covered cranial support',[(.177,1.448,.008,.012),(.16,1.48,.055,.042),(.10,1.58,.102,.082),(.02,1.645,.119,.097),(-.08,1.70,.132,.091),(-.19,1.712,.138,.089),(-.275,1.718,.125,.074),(-.327,1.710,.075,.035),(-.34,1.710,.007,.008)],'iron')
 # Closed crown plates: short full-width curved lenticular sectors.
 top=[controls[f'C{i}'] for i in range(5)]
 for i in range(4):
  a,b=top[i],top[i+1];rows=[]
  for t,scale_r in [(0,.08),(.09,.68),(.24,1),(.52,1),(.82,.72),(1,.07)]:
   q=a.lerp(b,t);y=q.y+.012;z=q.z-.010+.008*math.sin(math.pi*t);rx=[.135,.185,.192,.133][i]*scale_r;rz=.015*scale_r
   rows.append((y,z,rx,rz))
  volume_y('overlapping closed crown sector '+str(i),rows)
 # Posterior source-enclosure lobes are compact curved solid cages joined over
 # the support, not open-ended ribbon planes. Pair across existing head frame.
 for side,sgn in [('L',-1),('R',1)]:
  for i,(start,end) in enumerate([('C0','P0'),('C1','P1'),('C2','P2')]):
   a=controls[start].copy();b=controls[end].copy();sections=[]
   for t,r in [(0,.08),(.10,.65),(.30,1),(.58,.96),(.83,.50),(1,.045)]:
    q=a.lerp(b,t);q.x=sgn*(.13+.067*math.sin(math.pi*t));q.y+=.020*math.sin(math.pi*t)
    tangent=(b-a);tangent.x=0;tangent.normalize();perp=Vector((0,-tangent.z,tangent.y))
    sections.append((q,Vector((.010*r,0,0)),perp*(.027*r)))
   rings('closed swept enclosure lobe '+side+str(i),sections)
 # Narrow bronze accent is a formed closed ridge with two source edge bounds.
 for side,sgn in [('L',-1),('R',1)]:
  sections=[]
  for i,q0 in enumerate(top):
   q=q0.copy();q.x=sgn*[.13,.181,.191,.140,.077][i];q.z+=.004
   r=.45 if i in (0,4) else 1
   sections.append((q,Vector((.0022*r,0,0)),Vector((0,0,.004*r))))
  rings('narrow supraoptic formed bronze ledge '+side,sections,'bronze',12)
 # Compound hooked upper bill: paired transverse rings from outer/inner rails.
 # Distal endpoint derives from actual receiving evaluated silhouette vertex.
 receipt=json.loads((base/f'assets/audit/cg-supervised01/attempt09/{era}/receipt.json').read_text());cam=receipt['cameras']['canon-neutral'];from mathutils import Euler
 cm=Matrix.Translation(Vector(cam['location']))@Euler(cam['rotation_euler'],'XYZ').to_matrix().to_4x4();ci=cm.inverted()
 def project(v):
  q=ci@v;w,h=cam['resolution'];s=cam['ortho_scale'];return Vector(((q.x/s+.5-cam['shift'][0])*w,(.5-q.y/(s*h/w)+cam['shift'][1]*w/h)*h))
 distal=scene.objects['CGH18 formed distal hooked bill plate'];ev=distal.evaluated_get(bpy.context.evaluated_depsgraph_get());tip=max((ev.matrix_world@v.co for v in ev.data.vertices),key=lambda v:project(v).y)
 outer=[controls[n] for n in ['B0','B1','B2','B3','B4']]+[tip];inner=[controls['BR'],Vector((-.05,-.367,1.606)),controls['BI'],Vector((-.02,-.410,1.477)),Vector((-.01,-.405,1.416)),tip]
 sections=[]
 for i,(a,b) in enumerate(zip(outer,inner)):
  center=(a+b)/2;center.x=0;perp=(a-b)/2;perp.x=0
  sections.append((center,Vector(([.085,.099,.083,.060,.035,.003][i],0,0)),perp if perp.length>.002 else Vector((0,.002,.002))))
 upper=rings('compound formed upper bill and deep hook',sections,'armor',20)
 # Closed lower jaw follows the observed cheek sill and stops before hook tip.
 a,b,c=controls['K1'],controls['K2'],controls['K3'];sections=[]
 for q,width,height in [(a,.117,.018),(a.lerp(b,.28),.115,.022),(a.lerp(b,.66),.096,.017),(b,.067,.012),(c,.016,.004),(c+Vector((0,-.010,.003)),.003,.002)]:
  q=q.copy();q.x=0;sections.append((q,Vector((width,0,0)),Vector((0,0,height))))
 rings('separate closed lower jaw with gape',sections)
 # Fitted recess lip: three short closed sill volumes rather than a sweeping
 # void frame. Original optic seat provides the thin upper surround.
 for side,sgn in [('L',-1),('R',1)]:
  rows=[controls[n].copy() for n in ['K0','K1','KI']];sections=[]
  for i,q in enumerate(rows):
   q.x=sgn*.151;q.z+=.012
   sections.append((q,Vector((.009,0,0)),Vector((0,0,.017 if i==1 else .006))))
  rings('rolled recessed cheek sill '+side,sections)
 # All retirement is explicit; untouched global viewport flags persist.
 overrides={}
 for n in retire:
  o=scene.objects[n];overrides[n]={'hide_render_before':o.hide_render,'hide_set_before':o.hide_get(),'hide_viewport_unchanged':o.hide_viewport};o.hide_render=True;o.hide_set(True)
 bpy.context.view_layer.update()
 return {'added':[o.name for o in made],'hideOverrides':retire,'visibilityOverrides':overrides,'protectedNames':plan['protected_exact_objects'],'closedCageProof':proof,'actualReceivingHookTipWorld':list(tip),'actualReceivingHookTipPixel':list(project(tip)),'controlWorldPriors':{n:list(q) for n,q in controls.items()},'limits':['Source camera/depth estimated; actual whole likeness unreviewed. Closed-cage diagnostics establish topology only.']}

def run():
 args=argparse.ArgumentParser();args.add_argument('--root',type=Path,required=True);args.add_argument('--era',default='builder');opt=args.parse_args(sys.argv[sys.argv.index('--')+1:]);base=opt.root.resolve();era=opt.era
 assert era=='builder','Design01 is Builder only pending root gate'
 assert sha(base/MANIFEST)==MANIFEST_SHA;receiver=json.loads((base/MANIFEST).read_text())['natives'][era];native=base/receiver['path'];assert sha(native)==receiver['sha256']
 out=ROOT/f'assets/audit/cg-recursive-source-head04/attempt01/{era}';out.mkdir(parents=True,exist_ok=False);models=ROOT/'assets/models/cg-recursive-source-head04/attempt01';models.mkdir(parents=True,exist_ok=False)
 delivery=load(base/'scripts/cg-recursive-delivery02.py');strong=load(base/'scripts/cg-supervised-head17.py');payload=load(base/'scripts/cg-supervised-body12.py');pres=load(base/'scripts/cg-supervised-preservation.py')
 bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene
 def rig():return {'objects':{o.name:{'matrix':[list(r) for r in o.matrix_world],'objectRNA':strong.rna(o),'dataRNA':strong.rna(o.data)} for o in scene.objects if o.type in ('CAMERA','LIGHT')},'world':{'name':scene.world.name,'nodes':[(n.name,n.type,[(i.name,delivery.value(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in scene.world.node_tree.nodes]},'render':{k:getattr(scene.render,k) for k in ['engine','resolution_x','resolution_y','resolution_percentage','filepath','film_transparent']},'view':{k:getattr(scene.view_settings,k) for k in ['view_transform','look','exposure','gamma']},'override':scene.view_layers[0].material_override.name if scene.view_layers[0].material_override else None}
 original_rig=rig();before=delivery.snapshot(scene,strong,payload);assert len(before['payload'])==7644 and len(before['materials'])==62
 report={'status':'IN_PROGRESS','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input':str(native),'input_sha256':sha(native),'receiving_manifest_sha256':MANIFEST_SHA,'plan_sha256':PLAN_SHA,'authoring_sha256':sha(__file__),'era':era,'receiving_counts':receiver['custody_counts'],'scope':'HEAD04 Design01 only; no artistic acceptance or exports/runtime/publication'}
 def write():(out/'receipt.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
 write();(out/'receiving-snapshot.json').write_text(json.dumps(before,indent=2)+'\n');camera=json.loads((base/f'assets/audit/cg-supervised01/attempt09/{era}/receipt.json').read_text());rargs=argparse.Namespace(samples=4,resolution=640);baseline=out/'before';baseline.mkdir();report['before_renders']=delivery.render_views(scene,camera,['canon-neutral','canon-neutral-clay'],baseline,rargs);assert rig()==original_rig;write()
 report['changes']=apply(scene,base,era);declared={n:{'name':n,'hide_set':True} for n in report['changes']['hideOverrides']};report['before_save_custody']=delivery.verify(scene,before,strong,payload,declared);pres.retain_packed_image_ids(scene);assert rig()==original_rig
 output=models/f'murderbird-source-head04-{era}.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(output),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(output));scene=bpy.context.scene;report['save_reopen_custody']=delivery.verify(scene,before,strong,payload,declared);report['native']=str(output);report['native_sha256']=sha(output);report['original_rig_restored_before_save']=True;assert rig()==original_rig;write()
 candidate=out/'candidate';candidate.mkdir();report['candidate_renders']=delivery.render_views(scene,camera,['canon-neutral','canon-neutral-clay','head-neck'],candidate,rargs);assert rig()==original_rig;write()
 # Opposing head: held head camera mirrored about X, same lens/framing/lights.
 from mathutils import Euler
 opposite=json.loads(json.dumps(camera));spec=opposite['cameras']['head-neck'];rot=Euler(spec['rotation_euler'],'XYZ').to_matrix();direction=rot@Vector((0,0,-1));pos=Vector(spec['location']);target=pos+direction*6;pos.x=-pos.x;target.x=-target.x;spec['location']=list(pos);spec['rotation_euler']=list((target-pos).to_track_quat('-Z','Y').to_euler());opposite['cameras']['head-neck-opposite']=spec
 report['opposite_renders']=delivery.render_views(scene,opposite,['head-neck-opposite'],candidate,rargs);report['after_render_custody']=delivery.verify(scene,before,strong,payload,declared);assert rig()==original_rig;assert sha(native)==receiver['sha256'] and sha(output)==report['native_sha256'];report['status']='MECHANICAL_PASS_PAUSED_FOR_ROOT_DESIGN01_GATE';report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write();print('HEAD04_DESIGN01_COMPLETE',str(out),flush=True)
if __name__=='__main__':
 try:run()
 except Exception:
  import traceback;traceback.print_exc();sys.exit(1)
