"""Source-guided forward toe/claw successor. Inert API; explicit receiving root.

Only new meshes and exact declared retirement hides. Original payloads, graph,
images, stance and rig are preserved. All hidden depths are visual proposals.
"""
import argparse,datetime,hashlib,importlib.util,json,math,sys
from pathlib import Path
from types import SimpleNamespace
import bpy,bmesh
sys.dont_write_bytecode=True
from mathutils import Vector

TAG='cgRecursiveFeet02'
DEFAULT_DESIGN=1
REF_SHA='645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114'
MANIFEST='assets/audit/cg-recursive-three-loop01/loop02-preparation/receiving-manifest-loop02.json'
MANIFEST_SHA='47ed3ee74f0a06a9c470a427f8151dd032b0b48e1c68083f50d092cd1ec3308f'
BRIEF='assets/audit/cg-recursive-three-loop01/loop02-preparation/cg-recursive-feet02-approach.json'
BRIEF_SHA='a3cbc933bd6377ede7b2898b53f2d3d9a6af3c024fcba26cdfb608e6b321328f'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(root,n):
 p=Path(root)/'scripts'/n;s=importlib.util.spec_from_file_location('feet02_'+p.stem.replace('-','_'),p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def preflight(scene,root,era):
 root=Path(root).resolve();p=root/BRIEF
 if sha(p)!=BRIEF_SHA:raise RuntimeError('Approved foot approach changed')
 d=json.loads(p.read_text());names=d['proposed_later_retirement_whitelist']['names']
 if len(names)!=102 or len(set(names))!=102:raise RuntimeError('102 exact retirements required')
 expected={n:v for group in d['exact_era_material_bindings'][era].values() for n,v in group.items()};records=[]
 for n in names:
  o=scene.objects.get(n)
  if not o or o.type!='MESH' or o.hide_render:raise RuntimeError('Actual retained retirement receiver absent/hidden: '+n)
  mats=[m.name if m else None for m in o.data.materials]
  if mats!=expected[n]:raise RuntimeError('Actual era binding differs: '+n)
  records.append({'name':n,'before':[o.hide_render,o.hide_viewport,o.hide_get()],'materials':mats,'vertices':len(o.data.vertices),'uv_layers':[u.name for u in o.data.uv_layers]})
 anchors=[]
 for a in d['exact_anchors_and_stance']:
  o=scene.objects.get(a['name'])
  if not o or [[float(c) for c in r] for r in o.matrix_world]!=a['matrix_world']:raise RuntimeError('Named anchor matrix changed: '+a['name'])
  vs=[o.matrix_world@v.co for v in o.data.vertices];c=sum(vs,Vector())/len(vs)
  if max(abs(c[i]-a['center'][i]) for i in range(3))>1e-7:raise RuntimeError('Named anchor center changed: '+a['name'])
  anchors.append({'name':o.name,'center':list(c),'matrix_world':[list(r) for r in o.matrix_world]})
 return d,names,records,anchors

def apply(scene,root_path,era='builder',design=None):
 """Default retained design; no IO beyond pinned brief read; no saving/rendering."""
 if root_path is None:raise ValueError('Explicit receiving root required')
 if era not in ('builder','maker','mechanic'):raise ValueError(era)
 design=DEFAULT_DESIGN if design is None else design
 if design!=1:raise ValueError('Only preserved design01 exists')
 if any(o.get(TAG) for o in scene.objects):raise RuntimeError('Reload exact retained native before apply')
 brief,names,receivers,anchors=preflight(scene,root_path,era);made=[];toe_records=[];hides={}
 coll=bpy.data.collections.new('CG recursive FEET02 forward articulation');scene.collection.children.link(coll)
 def points(o):return [o.matrix_world@v.co for v in o.data.vertices]
 def sections(o,n):
  vs=points(o)
  if len(vs)%n:raise RuntimeError('Receiving section topology differs: '+o.name)
  return [sum(vs[i:i+n],Vector())/n for i in range(0,len(vs),n)]
 def mesh(n,vs,fs,uv,src,role,stock=0):
  d=bpy.data.meshes.new('CGRF02 '+n);d.from_pydata([tuple(v) for v in vs],[],fs);d.update();o=bpy.data.objects.new(d.name,d);coll.objects.link(o)
  d.materials.append(src.data.materials[0]);layer=d.uv_layers.new(name='recursive-feet02-across-along')
  for f in d.polygons:
   f.use_smooth=True
   for li in f.loop_indices:layer.data[li].uv=uv[d.loops[li].vertex_index]
  bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(d);bm.free()
  if stock:
   sol=o.modifiers.new('inward formed metal stock','SOLIDIFY');sol.thickness=stock;sol.offset=-1
  b=o.modifiers.new('small formed edge roll','BEVEL');b.width=.00055;b.segments=2
  o[TAG]=True;o['cg1cRegion']='foot';o['cg2bRegion']='foot';o['surfaceRole']=role;o['cgSurfaceFamilies']=json.dumps([role]);o['exteriorEras']='maker,mechanic,builder';o['era']=era;o['cgConstructionStatus']='Source-informed articulated exterior; hidden depth inferred; no engineering/owner acceptance';o['cgFeet02Receiver']=src.name
  made.append(o.name);return o
 for side in ('left','right'):
  for digit in (1,2,3):
   label=side+' forward toe '+str(digit);a,b=sections(scene.objects['CG1c '+label+' dark tendon chassis'],12);direction=Vector((b.x-a.x,b.y-a.y,0)).normalized();across=Vector((-direction.y,direction.x,0));cover=scene.objects['CGF14 '+label+' dorsal formed cover 0'];bearing=scene.objects['CGF14 '+label+' formed talon seat'];inner=scene.objects['CGF03 '+label+' recessed tendon body']
   def station(t):
    p=a.lerp(b,t);p.z+=.019+.016*math.sin(math.pi*t)
    return p,.0354*(1-.15*t),.0350*(1-.17*t)
   # Three domed open U sections, unequal longitudinal bulges and pinched necks.
   ranges=[(0,.290),(.335,.635),(.680,1.0)]
   for k,(lo,hi) in enumerate(ranges):
    vs=[];uv=[];nu,nv=15,13
    for j in range(nv):
     v=j/(nv-1);t=lo+(hi-lo)*v;p,w,h=station(t);neck=.87+.13*math.sin(math.pi*v)**.35
     for i in range(nu):
      u=i/(nu-1)*2-1
      # Turned shoulders descend below center; curved crown remains convex.
      theta=(u+1)*math.pi*.5;q=p+across*(w*neck*(-math.cos(theta)))+Vector((0,0,h*(math.sin(theta)-.14*abs(u)**6)))
      q.z+=.0045*math.sin(math.pi*v)*math.sin(theta);vs.append(q);uv.append((i/(nu-1),v))
    fs=[(j*nu+i,j*nu+i+1,(j+1)*nu+i+1,(j+1)*nu+i) for j in range(nv-1) for i in range(nu-1)];mesh(label+' convex articulated lobe '+str(k),vs,fs,uv,cover,'forged-steel',.0015)
   # Short side-return neck collars remain open; no decorative ring pile.
   for k,t in enumerate((.305,.650)):
    vs=[];uv=[];nu=15
    for j,dt in enumerate((-.002,.002,.005)):
     p,w,h=station(t+dt)
     for i in range(nu):
      u=i/(nu-1)*2-1;theta=(u+1)*math.pi*.5;q=p+across*(w*.91*(-math.cos(theta)))+Vector((0,0,h*.94*(math.sin(theta)-.14*abs(u)**6)));vs.append(q);uv.append((i/(nu-1),j/2))
    mesh(label+' recessed joint shoulder '+str(k),vs,[(j*nu+i,j*nu+i+1,(j+1)*nu+i+1,(j+1)*nu+i) for j in range(2) for i in range(nu-1)],uv,bearing,'machined-steel',.0010)
   # A narrow formed socket follows the unchanged distal chassis root.
   vs=[];uv=[];nu=15
   for j,t in enumerate((.93,.97,1.006)):
    p,w,h=station(t)
    for i in range(nu):
     theta=i/(nu-1)*math.pi;q=p+across*(-math.cos(theta)*w*.92)+Vector((0,0,h*.88*math.sin(theta)));vs.append(q);uv.append((i/(nu-1),j/2))
   mesh(label+' narrow talon socket',vs,[(j*nu+i,j*nu+i+1,(j+1)*nu+i+1,(j+1)*nu+i) for j in range(2) for i in range(nu-1)],uv,bearing,'machined-steel',.0012)
   old=scene.objects['CGF03 '+label+' substantial descending talon'];oldvs=points(old);centers=sections(old,32);vs=[];uv=[];nr=32;ns=len(centers)
   for j,p in enumerate(centers):
    t=j/(ns-1);tangent=(centers[min(ns-1,j+1)]-centers[max(0,j-1)]).normalized();up=tangent.cross(across).normalized();ring=oldvs[j*nr:(j+1)*nr];wx=max(abs((q-p).dot(across)) for q in ring);hz=max(abs((q-p).dot(up)) for q in ring)
    for i in range(nr):
     ang=math.tau*i/nr
     if j>=ns-2:q=oldvs[j*nr+i].copy()
     else:
      ca,sa=math.cos(ang),math.sin(ang);ridge=.0022*(1-t)**.6*max(0,sa)**10;q=p+across*(wx*.77*ca)+up*(hz*.87*sa+ridge);q.z=max(min(q0.z for q0 in ring),q.z)
     vs.append(q);uv.append((i/nr,t))
   fs=[(j*nr+i,j*nr+(i+1)%nr,(j+1)*nr+(i+1)%nr,(j+1)*nr+i) for j in range(ns-1) for i in range(nr)];fs.extend([tuple(reversed(range(nr))),tuple(range((ns-1)*nr,ns*nr))]);obj=mesh(label+' narrower ridged descending hook',vs,fs,uv,old,'forged-steel')
   # Last two contact/tip rings remain exact receiving coordinates; do not bevel them.
   obj.modifiers.clear()
   toe_records.append({'label':label,'chassis_root':list(a),'chassis_distal':list(b),'current_claw_root':list(centers[0]),'current_claw_tip':list(centers[-1]),'tip_last_two_rings_byte_coordinates_preserved':True,'ranges':ranges,'cross_width_factor':.77,'new_claw':obj.name})
 for n in names:
  o=scene.objects[n];before=[o.hide_render,o.hide_viewport,o.hide_get()];o.hide_render=True;o.hide_set(True);hides[n]={'before':before,'after':[True,before[1],True],'hide_set':True}
 bpy.context.view_layer.update()
 return {'module':'cg-recursive-feet02','era':era,'design':design,'newMeshes':made,'hideOverrides':hides,'receiving_preflight':receivers,'protected_named_anchors':anchors,'toe_receipts':toe_records,'source_image_sha256':REF_SHA,'source_plan_sha256':BRIEF_SHA,'status':'Partial forward-feet construction; inferred depth; source likeness/owner acceptance not claimed','limits':['Rear toes/talons retained including known bulk','Ankle/instep/head/breast/shoulder untouched','No engineered-joint or motion claim']}

def review_only(root,own,era,design):
 out=own/'assets/audit/cg-recursive-feet02'/('design%02d'%design)/era
 r=json.loads((out/'receipt.json').read_text());native=own/r['native_path']
 if sha(native)!=r['native_sha256']:raise RuntimeError('Saved reviewed candidate changed')
 bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;delivery=load(root,'cg-recursive-delivery01.py');q=json.loads((root/'assets/audit/cg-supervised01/attempt09'/era/'receipt.json').read_text())
 for name,base in [('feet-far-profile','neutral-090'),('feet-rear','neutral-180')]:
  z=dict(q['cameras'][base]);target=Vector((0,-.03,.14));z['location']=list(Vector(z['location'])-Vector((0,-.04,.97))+target);z['rotation_euler']=list((target-Vector(z['location'])).to_track_quat('-Z','Y').to_euler());z['ortho_scale']=.92;z['shift']=[0,0];z['resolution']=[640,640];q['cameras'][name]=z
 ex=out/'continuity';ex.mkdir(exist_ok=False)
 views=delivery.render_views(s,q,['side-profile','neutral-180','neutral-090','neutral-270','feet-detail-clay','canon-workshop','feet-far-profile','feet-rear'],ex,SimpleNamespace(resolution=640,samples=4))
 (ex/'receipt.json').write_text(json.dumps({'native_sha256':r['native_sha256'],'unchanged_after_review':sha(native)==r['native_sha256'],'cameras':views,'render_only_no_native_save':True},indent=2)+'\n');print('FEET02_CONTINUITY_COMPLETE',str(ex),flush=True)

def run():
 p=argparse.ArgumentParser();p.add_argument('--input-root',required=True);p.add_argument('--era',choices=['builder','maker','mechanic'],default='builder');p.add_argument('--design',type=int,default=DEFAULT_DESIGN);p.add_argument('--expand',action='store_true');p.add_argument('--custody-only',action='store_true');p.add_argument('--review-only',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=Path(a.input_root).resolve();own=Path(__file__).resolve().parents[1];
 if a.review_only:return review_only(root,own,a.era,a.design)
 out=own/'assets/audit/cg-recursive-feet02'/('design%02d'%a.design)/a.era;asset=own/'assets/models/cg-recursive-feet02'/('design%02d'%a.design);out.mkdir(parents=True,exist_ok=True);asset.mkdir(parents=True,exist_ok=True)
 if sha(root/MANIFEST)!=MANIFEST_SHA:raise RuntimeError('Approved retained manifest changed')
 manifest=json.loads((root/MANIFEST).read_text());pin=manifest['natives'][a.era];inp=root/pin['path'];assert sha(inp)==pin['sha256'];assert sha(root/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg')==REF_SHA
 native=asset/('murderbird-recursive-feet-'+a.era+'.blend')
 if native.exists():raise RuntimeError('Native output collision')
 bpy.ops.wm.open_mainfile(filepath=str(inp));s=bpy.context.scene;delivery=load(root,'cg-recursive-delivery01.py');strong=load(root,'cg-supervised-head17.py');payload=load(root,'cg-supervised-body12.py');pres=load(root,'cg-supervised-preservation.py');before=delivery.snapshot(s,strong,payload);q=json.loads((root/'assets/audit/cg-supervised01/attempt09'/a.era/'receipt.json').read_text());args=SimpleNamespace(resolution=640,samples=4)
 # Foot-visible diagnostic front/profile use held neutral09 area rig and exact09
 # whole front/side orientations with documented foot-only framing.
 def detail(key,whole,target):
  z=dict(q['cameras'][whole]);z['location']=(Vector(z['location'])-Vector((0,-.04,.97))+Vector(target));z['rotation_euler']=list((Vector(target)-Vector(z['location'])).to_track_quat('-Z','Y').to_euler());z['ortho_scale']=.92;z['shift']=[0,0];z['resolution']=[640,640];q['cameras'][key]=z
 detail('feet-front','neutral-000',(0,-.03,.14));detail('feet-profile','side-profile',(0,-.03,.14))
 receipt={'input_path':pin['path'],'input_sha256':pin['sha256'],'input_manifest_sha256':MANIFEST_SHA,'source_path':'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg','source_sha256':REF_SHA,'script_sha256':sha(Path(__file__)),'shared_main':'251f2f0243181e97140179c2aff6eb057e165438','loop01_remote':'07c52bb0a1c57d38b37c3c09d8a104ff2634ec41','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cameras':{},'status':'Unaccepted partial feet study'}
 def write(): (out/'receipt.json').write_text(json.dumps(receipt,indent=2,default=list)+'\n')
 if not a.custody_only:
  bo=out/'before';bo.mkdir();receipt['cameras']['before']=delivery.render_views(s,q,['canon-neutral','canon-neutral-clay','feet-detail','feet-front','feet-profile'],bo,args);write()
 result=apply(s,root,a.era,a.design);receipt['application']=result;declared={n:{'hide_set':True} for n in result['hideOverrides']};receipt['pre_save_custody']=delivery.verify(s,before,strong,payload,declared)
 pres.retain_packed_image_ids(s);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False);receipt['native_path']=str(native.relative_to(own));receipt['native_sha256']=sha(native);bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;receipt['save_reopen_custody']=delivery.verify(s,before,strong,payload,declared);write();print('FEET02_NATIVE_CUSTODY_PASS',str(native),flush=True)
 if not a.custody_only:
  ao=out/'after';ao.mkdir();receipt['cameras']['after']=delivery.render_views(s,q,['canon-neutral','canon-neutral-clay','feet-detail','feet-front','feet-profile'],ao,args);write();print('FEET02_FIRST_WHOLE_COMPLETE',str(out),flush=True)
 if a.expand and not a.custody_only:
  ex=out/'continuity';ex.mkdir();receipt['cameras']['continuity']=delivery.render_views(s,q,['side-profile','neutral-180','neutral-090','neutral-270','feet-detail-clay','canon-workshop'],ex,args);write()
 # Evaluated audit confined to new visible surfaces; no whole-scene proxy gate.
 finite=[];deps=bpy.context.evaluated_depsgraph_get()
 for n in result['newMeshes']:
  o=s.objects[n];ev=o.evaluated_get(deps);m=ev.to_mesh();ok=all(math.isfinite(v) for q in m.vertices for v in q.co) and all(math.isfinite(v) for l in m.uv_layers for q in l.data for v in q.uv);finite.append({'name':n,'finite':ok,'material_slots':[m.name if m else None for m in o.data.materials]});ev.to_mesh_clear();assert ok
 receipt['evaluated_new_surfaces']=finite;receipt['final_receiving_custody']=delivery.verify(s,before,strong,payload,declared);receipt['input_hash_preserved']=sha(inp)==pin['sha256'];assert receipt['input_hash_preserved'];receipt['complete_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write();print('FEET02_COMPLETE',str(out),flush=True)
if __name__=='__main__':run()
