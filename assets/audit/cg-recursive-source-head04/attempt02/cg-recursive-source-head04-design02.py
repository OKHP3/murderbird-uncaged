"""HEAD04 design02: closed volume cages from observed contour controls.
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
 # Region-only copy of the compatible inherited era graph. Existing nodes,
 # maps and data remain byte-exact; links are changed only in the new copy.
 dark=armor.copy();dark.name='CGRV04D2 rough formed crown / '+era
 bs=next(n for n in dark.node_tree.nodes if n.type=='BSDF_PRINCIPLED');nt=dark.node_tree
 mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.30,.48,.44,1)
 source=next((l.from_socket for l in nt.links if l.to_socket==bs.inputs['Base Color']),None)
 if source:nt.links.new(source,mix.inputs[1])
 else:mix.inputs[1].default_value=bs.inputs['Base Color'].default_value
 nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
 rough=nt.nodes.new('ShaderNodeMath');rough.operation='MAXIMUM';rough.inputs[1].default_value=.55
 source=next((l.from_socket for l in nt.links if l.to_socket==bs.inputs['Roughness']),None)
 if source:nt.links.new(source,rough.inputs[0])
 else:rough.inputs[0].default_value=bs.inputs['Roughness'].default_value
 nt.links.new(rough.outputs[0],bs.inputs['Roughness'])
 dark['cgRecursiveSourceHead04']=True;dark['era']=era;dark['scope']='regional head formed metal only; inherited graph copy'
 mats={'armor':dark,'iron':iron,'bronze':bronze};made=[];proof=[]
 controls={c['id']:Vector(c['world_control_prior']) for c in plan['control_edge_correspondences']}
 def mesh(label,vs,fs,role='armor',subd=1):
  name='CGRV04D2 '+label;data=bpy.data.meshes.new(name);data.from_pydata([fi@Vector(v) for v in vs],[],fs);data.update();obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.parent=frame;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=Matrix.Identity(4)
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
 # Connected closed cranial support: source dorsal station heights, compact
 # posterior return. Entire visible exterior is covered by local short plates.
 support_rows=[(-.34,1.705,.009,.010),(-.32,1.698,.073,.065),(-.27,1.710,.127,.090),(-.19,1.733,.151,.090),(-.10,1.729,.149,.090),(-.02,1.718,.136,.088),(.07,1.697,.112,.086),(.13,1.633,.075,.074),(.165,1.544,.009,.011)]
 support=volume_y('connected covered cranial support',support_rows,'iron')
 def profile(y):
  y=max(support_rows[0][0],min(support_rows[-1][0],y))
  for a,b in zip(support_rows,support_rows[1:]):
   if a[0]<=y<=b[0]:
    t=(y-a[0])/(b[0]-a[0]);return tuple(a[i]*(1-t)+b[i]*t for i in (1,2,3))
  return support_rows[-1][1:]
 # Twenty source-sector plate volumes, each a short curved filled footprint
 # with a closed under-skin. No full-width roof sectors or C-to-P2 blades.
 plate_count=0
 for side,sgn in [('L',-1),('R',1)]:
  for j,cy in enumerate([-.278,-.204,-.130,-.056,.018,.092]):
   for zone,(amin,amax) in enumerate([(0,54),(46,94)]):
    if zone==1 and j in (0,1):continue # reserved complete fixed optical aperture
    vs=[];nu,nv=5,5
    for layer in (0,1):
     for u in range(nu):
      t=u/(nu-1);y=cy+(t-.5)*.104+(zone-.5)*.014;zc,rx,rz=profile(y)
      for v in range(nv):
       w=v/(nv-1);ang=math.radians(amin+(amax-amin)*w);taper=.82+.18*math.sin(math.pi*t)
       x=sgn*(rx+.006-layer*.004)*math.sin(ang)*taper
       z=zc+(rz+.009-layer*.004)*math.cos(ang)+.008*math.sin(math.pi*t)*math.sin(math.pi*w)
       # Locally swept rear termination, at most .018world beyond its course.
       yy=y+.016*(w-.5)*math.sin(math.pi*t)
       vs.append(Vector((x,yy,z)))
    M=nu*nv;fs=[]
    for u in range(nu-1):
     for v in range(nv-1):
      a=u*nv+v;f=(a,a+1,a+nv+1,a+nv);fs.extend([f,tuple(M+i for i in reversed(f))])
    border=list(range(nv))+[u*nv+nv-1 for u in range(1,nu)]+list(range((nu-1)*nv+nv-2,(nu-1)*nv-1,-1))+[u*nv for u in range(nu-2,0,-1)]
    for a,b in zip(border,border[1:]+border[:1]):fs.append((a,M+a,M+b,b))
    mesh('short staggered curved crown plate '+side+str(j)+'-'+str(zone),vs,fs);plate_count+=1
 # Narrow upper ledge follows the observed dorsal source contour; it seats
 # on the crown, and does not enlarge a forehead roof or wrap the optic.
 top=[controls[f'C{i}'] for i in range(5)]
 for side,sgn in [('L',-1),('R',1)]:
  sections=[]
  for i,q0 in enumerate(top):
   q=q0.copy();q.x=sgn*[.097,.132,.156,.123,.076][i];q.z+=.003
   sections.append((q,Vector((.0018,0,0)),Vector((0,0,.0025))))
  rings('narrow seated bronze ledge '+side,sections,'bronze',12)
 receipt=json.loads((base/f'assets/audit/cg-supervised01/attempt09/{era}/receipt.json').read_text());cam=receipt['cameras']['canon-neutral'];from mathutils import Euler
 cm=Matrix.Translation(Vector(cam['location']))@Euler(cam['rotation_euler'],'XYZ').to_matrix().to_4x4();ci=cm.inverted()
 def project(v):
  q=ci@v;w,h=cam['resolution'];s=cam['ortho_scale'];return Vector(((q.x/s+.5-cam['shift'][0])*w,(.5-q.y/(s*h/w)+cam['shift'][1]*w/h)*h))
 distal=scene.objects['CGH18 formed distal hooked bill plate'];ev=distal.evaluated_get(bpy.context.evaluated_depsgraph_get());tip=max((ev.matrix_world@v.co for v in ev.data.vertices),key=lambda v:project(v).y)
 # Slim polygonal cross sections produce broad formed metal planes with
 # rounded edges, avoiding the elliptical smooth bulb of design01.
 outer=[controls[n].copy() for n in ['B0','B1','B2','B3','B4']]+[tip.copy()]
 inner=[Vector((0,-.302,1.653)),Vector((0,-.386,1.625)),Vector((0,-.403,1.554)),Vector((0,-.411,1.484)),Vector((0,-.408,1.417)),tip.copy()]
 widths=[.058,.076,.063,.044,.026,.0025]
 sections=[]
 for i,(a,b) in enumerate(zip(outer,inner)):
  c=(a+b)/2;c.x=0;ax=(a-b)/2;ax.x=0
  if ax.length<.003:ax=Vector((0,.002,.002))
  sections.append((c,widths[i],ax))
 # Add intermediate rings to retain a compound curved profile while giving
 # side walls broad planar facets. Mesh edges receive only a small bevel.
 dens=[]
 for a,b in zip(sections,sections[1:]):
  dens.append(a);dens.append((a[0].lerp(b[0],.5),(a[1]+b[1])/2,a[2].lerp(b[2],.5)))
 dens.append(sections[-1]);vs=[]
 octagon=[(-.80,-1),(.80,-1),(1,-.72),(1,.72),(.80,1),(-.80,1),(-1,.72),(-1,-.72)]
 for c,width,ax in dens:
  for x,z in octagon:vs.append(c+Vector((x*width,0,0))+ax*z)
 N=8;fs=[(j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k) for j in range(len(dens)-1) for k in range(N)];fs += [tuple(reversed(tuple(range(N)))),tuple((len(dens)-1)*N+k for k in range(N))]
 upper=mesh('slim compound hooked bill with formed side planes',vs,fs,'armor',0)
 for f in upper.data.polygons:f.use_smooth=False
 be=upper.modifiers.new('rounded metal formed edges','BEVEL');be.width=.0022;be.segments=3
 wn=upper.modifiers.new('formed side plane normals','WEIGHTED_NORMAL');wn.keep_sharp=True
 # Separate lower jaw joins the pocket sill. It remains above existing throat
 # skin and terminates before the preserved deep upper hook.
 a=Vector((0,-.155,1.557));b=Vector((0,-.343,1.522));c=Vector((0,-.416,1.494));sections=[]
 for q,width,height in [(a,.128,.016),(a.lerp(b,.35),.122,.020),(a.lerp(b,.75),.103,.016),(b,.074,.011),(c,.019,.003),(c+Vector((0,-.009,.002)),.002,.0018)]:sections.append((q,Vector((width,0,0)),Vector((0,0,height))))
 jaw=rings('connected separate lower jaw with visible gape',sections)
 # Bounded cup recess: rolled opening, inset walls, dark floor, outer closed
 # back. Lower lip overlaps the jaw root; no floating separate sill volume.
 for side,sgn in [('L',-1),('R',1)]:
  outline=[(-.095,1.609),(-.236,1.617),(-.319,1.586),(-.370,1.535),(-.263,1.541),(-.131,1.566)]
  yc=sum(v[0] for v in outline)/6;zc=sum(v[1] for v in outline)/6;vs=[]
  for depth,inset in [(.160,1),(.159,.94),(.114,.79),(.105,1)]:
   for y,z in outline:vs.append(Vector((sgn*depth,yc+(y-yc)*inset,zc+(z-zc)*inset)))
  N=6;fs=[]
  for k in range(N):
   kk=(k+1)%N;fs += [(k,kk,N+kk,N+k),(N+k,N+kk,2*N+kk,2*N+k),(k,3*N+k,3*N+kk,kk)]
  fs += [tuple(2*N+k for k in range(N)),tuple(reversed(tuple(3*N+k for k in range(N))))]
  pocket=mesh('bounded rolled cheek pocket attached to jaw '+side,vs,fs,'armor',1)
  # Only added faces get regional assignments. Dark inherited floor is recessed.
  pocket.data.polygons[-2].material_index=1
  for i in range(1,3*N,3):pocket.data.polygons[i].material_index=1
 # All retirement is explicit; untouched global viewport flags persist.
 overrides={}
 for n in retire:
  o=scene.objects[n];overrides[n]={'hide_render_before':o.hide_render,'hide_set_before':o.hide_get(),'hide_viewport_unchanged':o.hide_viewport};o.hide_render=True;o.hide_set(True)
 bpy.context.view_layer.update()
 return {'added':[o.name for o in made],'hideOverrides':retire,'visibilityOverrides':overrides,'protectedNames':plan['protected_exact_objects'],'closedCageProof':proof,'actualReceivingHookTipWorld':list(tip),'actualReceivingHookTipPixel':list(project(tip)),'shortCrownPlateCount':plate_count,'controlWorldPriors':{n:list(q) for n,q in controls.items()},'limits':['Source camera/depth estimated; actual whole likeness unreviewed. Closed-cage diagnostics establish topology only.']}

def run():
 args=argparse.ArgumentParser();args.add_argument('--root',type=Path,required=True);args.add_argument('--era',default='builder');opt=args.parse_args(sys.argv[sys.argv.index('--')+1:]);base=opt.root.resolve();era=opt.era
 assert era=='builder','Design02 is Builder only pending root gate'
 assert sha(base/MANIFEST)==MANIFEST_SHA;receiver=json.loads((base/MANIFEST).read_text())['natives'][era];native=base/receiver['path'];assert sha(native)==receiver['sha256']
 out=ROOT/f'assets/audit/cg-recursive-source-head04/attempt02/{era}';out.mkdir(parents=True,exist_ok=False);models=ROOT/'assets/models/cg-recursive-source-head04/attempt02';models.mkdir(parents=True,exist_ok=False)
 delivery=load(base/'scripts/cg-recursive-delivery02.py');strong=load(base/'scripts/cg-supervised-head17.py');payload=load(base/'scripts/cg-supervised-body12.py');pres=load(base/'scripts/cg-supervised-preservation.py')
 bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene
 def rig():return {'objects':{o.name:{'matrix':[list(r) for r in o.matrix_world],'objectRNA':strong.rna(o),'dataRNA':strong.rna(o.data)} for o in scene.objects if o.type in ('CAMERA','LIGHT')},'world':{'name':scene.world.name,'nodes':[(n.name,n.type,[(i.name,delivery.value(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in scene.world.node_tree.nodes]},'render':{k:getattr(scene.render,k) for k in ['engine','resolution_x','resolution_y','resolution_percentage','filepath','film_transparent']},'view':{k:getattr(scene.view_settings,k) for k in ['view_transform','look','exposure','gamma']},'override':scene.view_layers[0].material_override.name if scene.view_layers[0].material_override else None}
 original_rig=rig();before=delivery.snapshot(scene,strong,payload);assert len(before['payload'])==7644 and len(before['materials'])==62
 report={'status':'IN_PROGRESS','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input':str(native),'input_sha256':sha(native),'receiving_manifest_sha256':MANIFEST_SHA,'plan_sha256':PLAN_SHA,'authoring_sha256':sha(__file__),'era':era,'receiving_counts':receiver['custody_counts'],'scope':'HEAD04 Design02 only; no artistic acceptance or exports/runtime/publication'}
 def write():(out/'receipt.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
 write();(out/'receiving-snapshot.json').write_text(json.dumps(before,indent=2)+'\n');camera=json.loads((base/f'assets/audit/cg-supervised01/attempt09/{era}/receipt.json').read_text());rargs=argparse.Namespace(samples=4,resolution=640);baseline=out/'before';baseline.mkdir();report['before_renders']=delivery.render_views(scene,camera,['canon-neutral','canon-neutral-clay'],baseline,rargs);assert rig()==original_rig;write()
 report['changes']=apply(scene,base,era);declared={n:{'name':n,'hide_set':True} for n in report['changes']['hideOverrides']};report['before_save_custody']=delivery.verify(scene,before,strong,payload,declared);pres.retain_packed_image_ids(scene);assert rig()==original_rig
 output=models/f'murderbird-source-head04-design02-{era}.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(output),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(output));scene=bpy.context.scene;report['save_reopen_custody']=delivery.verify(scene,before,strong,payload,declared);report['native']=str(output);report['native_sha256']=sha(output);report['original_rig_restored_before_save']=True;assert rig()==original_rig;write()
 candidate=out/'candidate';candidate.mkdir();report['candidate_renders']=delivery.render_views(scene,camera,['canon-neutral','canon-neutral-clay','head-neck'],candidate,rargs);assert rig()==original_rig;write()
 # Opposing head: held head camera mirrored about X, same lens/framing/lights.
 from mathutils import Euler
 opposite=json.loads(json.dumps(camera));spec=opposite['cameras']['head-neck'];rot=Euler(spec['rotation_euler'],'XYZ').to_matrix();direction=rot@Vector((0,0,-1));pos=Vector(spec['location']);target=pos+direction*6;pos.x=-pos.x;target.x=-target.x;spec['location']=list(pos);spec['rotation_euler']=list((target-pos).to_track_quat('-Z','Y').to_euler());opposite['cameras']['head-neck-opposite']=spec
 report['opposite_renders']=delivery.render_views(scene,opposite,['head-neck-opposite'],candidate,rargs);report['after_render_custody']=delivery.verify(scene,before,strong,payload,declared);assert rig()==original_rig;assert sha(native)==receiver['sha256'] and sha(output)==report['native_sha256'];report['status']='MECHANICAL_PASS_PAUSED_FOR_ROOT_DESIGN02_GATE';report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write();print('HEAD04_DESIGN02_COMPLETE',str(out),flush=True)
if __name__=='__main__':
 try:run()
 except Exception:
  import traceback;traceback.print_exc();sys.exit(1)
