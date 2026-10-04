"""BODY15 oblique mid/lower breast planforms; deterministic receiving06→13 API.
Only lower 26 panels change; original receiving payloads and upper25 stay exact.
"""
import argparse,hashlib,importlib.util,json,math,sys,time
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
RECEIVING_SHA='72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4'
REF_SHA='645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114'
CANDIDATE_SHA='538c51bcdbf5bfce95a0932fdbbb0f5868b446f4985346d15e6cacd32430e633'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(root,name):
 spec=importlib.util.spec_from_file_location(name,Path(root)/'scripts'/('cg-supervised-'+name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def apply(scene,root_path=None,era='builder',design=1):
 root=Path(root_path or ROOT);m13=module(root,'body13');m12=module(root,'body12')
 if any(o.get('cgSupervisedBody15') for o in scene.objects):raise RuntimeError('Reload receiving06 for BODY15')
 if not any(o.get('cgSupervisedBody13') for o in scene.objects):m13.apply(scene,root,era)
 upper={o.name:m12.digest(o) for o in scene.objects if o.get('cgSupervisedBody12')};guide=next(o for o in scene.objects if o.get('cgSupervisedBody11'));deps=bpy.context.evaluated_depsgraph_get();ev=guide.evaluated_get(deps);md=ev.to_mesh();md.calc_loop_triangles();layer=md.uv_layers.active;tuv=[];world=[];points=[]
 for t in md.loop_triangles:
  if md.polygons[t.polygon_index].material_index:continue
  uv=[Vector((*layer.data[i].uv,0)) for i in t.loops];tuv.append(uv);world.append([guide.matrix_world@md.vertices[i].co for i in t.vertices]);points.extend(uv)
 tree=BVHTree.FromPolygons(points,[(3*i,3*i+1,3*i+2) for i in range(len(tuv))],all_triangles=True);hitmax=0
 def surface(u,v):
  nonlocal hitmax
  h,n,idx,d=tree.find_nearest(Vector((u,v,0)));hitmax=max(hitmax,d);assert d<2e-6,(u,v,d)
  a,b,c=tuv[idx];p0,p1,p2=world[idx];ab=b-a;ac=c-a;aq=h-a;den=ab.x*ac.y-ab.y*ac.x;w1=(aq.x*ac.y-aq.y*ac.x)/den;w2=(ab.x*aq.y-ab.y*aq.x)/den;return p0*(1-w1-w2)+p1*w1+p2*w2
 def normal(u,v):
  du=surface(min(.9999,u+.00005),v)-surface(max(.0001,u-.00005),v);dv=surface(u,min(.99995,v+.00005))-surface(u,max(.00005,v-.00005));n=du.cross(dv).normalized();return -n if n.y>0 else n
 records=[]
 for o in list(scene.objects):
  if not o.get('cgSupervisedBody13'):continue
  samples=json.loads(o['body13GuideSamples']);nu,nv=json.loads(o['body13Grid']);col,row=map(int,o.name.rsplit(' ',1)[-1].split('-'));params=[]
  for idx,(gu,gv) in enumerate(samples):
   u=(idx%nu)/(nu-1);v=(idx//nu)/(nv-1);t=max(0,min(1,(gv-.375)/.625));ramp=math.sin(math.pi*t)
   # Coherent oblique migration around keel; transverse nonlinear warp varies
   # track widths without shrink or texture/hardware changes. Side rails fixed.
   strength=.155 if design==1 else .22
   q=(gu-.025)/.950
   newu=gu+strength*ramp*math.sin(math.pi*q)+.025*ramp*math.sin(5*math.pi*q)
   newv=gv+.10*(gu-.5)*ramp
   newu=max(.02505,min(.97495,newu));newv=max(.0001,min(.9999,newv));base=surface(newu,newv);n=normal(newu,newv)
   relief=-.006+.00015*math.sin(math.pi*u)+.0056*v**3;pos=base+n*relief;pos.x=max(-.2307,min(.2307,pos.x));pos.y=max(-.419570,pos.y);o.data.vertices[idx].co=pos;params.append((newu,newv))
  o.data.update();o.name=f'CGB15 oblique formed panel {col}-{row}';o.data.name=f'body15 oblique formed plate {col}-{row}';del o['cgSupervisedBody13'];o['cgSupervisedBody15']=True;o['body15Grid']=o['body13Grid'];o['body15GuideSamples']=json.dumps(params);o['cgConstructionStatus']='Inferred oblique mid/lower keel sweep; unaccepted';o['cgBodyUVConvention']='Normalized corner UVs across plate/down root→free end; stock inward only';records.append(dict(object=o.name,track=col,segment=row,guideBounds=[min(p[0] for p in params),max(p[0] for p in params),min(p[1] for p in params),max(p[1] for p in params)],grid=[nu,nv],sweep=strength,widthWarp=.025,verticalShear=.10))
 ev.to_mesh_clear();bpy.context.view_layer.update();assert len(records)==26 and len(upper)==25;assert all(m12.digest(scene.objects[n])==h for n,h in upper.items())
 return dict(module='cg-supervised-body15',design=design,newPanels=26,upper25Digests=upper,sourcePartitions=records,actualGuideUVHitMaxDistance=hitmax,hiddenLegacyManifest=m12.HIDE_MANIFEST,hiddenGuide=guide.name,limits=['Warp/depth inferred from pinned composite+Candidate03; July body excluded','Fixed envelope/corridor; no hardware/material/pose edit','Owner artistic acceptance not established'])

def run():
 p=argparse.ArgumentParser();p.add_argument('--input-root',default=str(ROOT));p.add_argument('--design',type=int,default=1);p.add_argument('--phase',choices=['early','expand','audit','frames'],default='early');p.add_argument('--resolution',type=int,default=640);p.add_argument('--samples',type=int,default=4);args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=Path(args.input_root);out=Path(__file__).resolve().parents[1]/'assets/audit/cg-supervised-body15'/f'attempt{args.design:02d}';out.mkdir(parents=True,exist_ok=True);native=out/'murderbird-body15.blend';m=module(root,'body12');pres=module(root,'preservation');rec=root/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend';before=root/'assets/audit/cg-supervised-body13/attempt01/murderbird-body13.blend';assert sha(rec)==RECEIVING_SHA;assert sha(root/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg')==REF_SHA;assert sha(root/'assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png')==CANDIDATE_SHA
 start=time.time();receipt_path=out/'receipt.json'
 if args.phase=='early':
  bpy.ops.wm.open_mainfile(filepath=str(rec));s=bpy.context.scene;frozen={o.name:m.digest(o) for o in s.objects if o.type in ('MESH','EMPTY')};vis={o.name:[o.hide_render,o.hide_viewport,o.hide_get()] for o in s.objects};graphs=m.material_digest();packed=pres.packed_image_snapshot();result=apply(s,root,design=args.design);pres.retain_packed_image_ids(s);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native));result.update(originalPayloadDigests=frozen,originalVisibility=vis,receivingMaterialGraphDigests=graphs,packedImageSnapshot=packed,nativeSHA256=sha(native),receiving06SHA256=sha(rec),before13SHA256=sha(before),sourceReferenceSHA256=REF_SHA,candidate03SHA256=CANDIDATE_SHA,cameras={},images={})
 else:result=json.loads(receipt_path.read_text())
 bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene
 def verify():
  changed=[n for n,h in result['originalPayloadDigests'].items() if n not in s.objects or m.digest(s.objects[n])!=h];assert not changed,changed;assert m.material_digest()==result['receivingMaterialGraphDigests'];assert pres.packed_image_snapshot()==result['packedImageSnapshot'];assert all(m.digest(s.objects[n])==h for n,h in result['upper25Digests'].items());hides=result['hiddenLegacyManifest'];vc=[n for n,v in result['originalVisibility'].items() if n not in hides and [s.objects[n].hide_render,s.objects[n].hide_viewport,s.objects[n].hide_get()]!=v];assert not vc,vc;assert all(s.objects[n].hide_render and s.objects[n].hide_get() for n in hides)
  bounds=[];uvchecks=[];deps=bpy.context.evaluated_depsgraph_get()
  for o in s.objects:
   if not(o.get('cgSupervisedBody12') or o.get('cgSupervisedBody15')):continue
   ev=o.evaluated_get(deps);md=ev.to_mesh();bounds.extend([o.matrix_world@v.co for v in md.vertices]);vs=[c for l in md.uv_layers for u in l.data for c in u.uv];assert all(math.isfinite(c) and -1e-6<=c<=1.000001 for c in vs);uvchecks.append(dict(object=o.name,min=min(vs),max=max(vs),evaluated=True));ev.to_mesh_clear()
  bb=dict(min=[min(v[i] for v in bounds) for i in range(3)],max=[max(v[i] for v in bounds) for i in range(3)]);assert bb['min'][0]>=-.23201 and bb['max'][0]<=.23201 and bb['min'][1]>=-.41958,bb
  return dict(originalMeshesAndAnchorsChecked=len(result['originalPayloadDigests']),payloadChanged=changed,graphs=len(result['receivingMaterialGraphDigests']),packedMaps=len(result['packedImageSnapshot']),packedBytesAndMetadataExact=True,upperPanelsPreserved=25,exact149LegacyHides=len(hides)==149,exactVisibilityOutside149=True,evaluatedBounds=bb,evaluatedUV=uvchecks,nativeFrozen=sha(native)==result['nativeSHA256'])
 result['savedReopenedChecks']=verify();receipt_path.write_text(json.dumps(result,indent=2));print('BODY15_EARLY_SAVE_REOPEN_PASS',flush=True)
 prior=json.loads((root/'assets/audit/cg-supervised-body13/attempt01/receipt.json').read_text())
 def render(name,key):
  nonlocal s
  q=prior['cameras'][key];cam=s.camera;cam.location=q['location'];cam.rotation_euler=q['rotation_euler'];cam.data.type='ORTHO';cam.data.ortho_scale=q['scale'];cam.data.shift_x,cam.data.shift_y=q.get('shift',[0,0])
  for l in q['lights']:
   o=s.objects[l['name']];o.location=l['location'];o.rotation_euler=l['rotation'];o.data.energy=l['power'];o.data.color=l['color'];o.data.size=l['size']
  s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=args.samples;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_percentage=100;s.render.resolution_x=args.resolution;s.render.resolution_y=round(args.resolution*q['resolution'][1]/q['resolution'][0]);s.render.image_settings.file_format='PNG';s.view_layers[0].material_override=bpy.data.materials.get('Body11 diagnostic clay') if q['clay'] else None
  if q['clay'] and s.view_layers[0].material_override is None:
   c=bpy.data.materials.new('Body11 diagnostic clay');c.use_nodes=True;c.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.23,.23,.23,1);c.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.64;s.view_layers[0].material_override=c
  bpy.context.view_layer.update();qq=dict(q);qq['resolution']=[s.render.resolution_x,s.render.resolution_y];result['cameras'][name]=qq;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);print('BODY15_RENDER',name,flush=True)
 if args.phase=='early':
  for suffix,key in [('whole35-pbr','final13-whole35-pbr'),('whole35-clay','final13-whole35-clay'),('whole64-pbr','final13-whole64-pbr'),('whole64-clay','final13-whole64-clay'),('front-clay','final13-front-clay'),('body-grazing-clay','final13-body-grazing-clay')]:render('final15-'+suffix,key)
 elif args.phase=='expand':
  for suffix in ['front-pbr','front-whole-pbr','front-whole-clay','profile-whole-pbr','profile-whole-clay','whole-grazing-pbr','whole-grazing-clay','side-clay']:render('final15-'+suffix,'final13-'+suffix)
  # Fixed eight-angle turntable shares prior same-camera records exactly.
  for i in range(8):
   q=prior['cameras'][f'final13-turn-{i*45:03d}'];cam=s.camera;cam.location=q['location'];cam.rotation_euler=q['rotation_euler'];cam.data.type='ORTHO';cam.data.ortho_scale=q['scale'];cam.data.shift_x=cam.data.shift_y=0;s.view_layers[0].material_override=None;s.render.resolution_x,s.render.resolution_y=q['resolution'];s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=args.samples;s.render.threads_mode='FIXED';s.render.threads=2;s.render.image_settings.file_format='PNG';name=f'final15-turn-{i*45:03d}';s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);result['cameras'][name]=q
 elif args.phase=='audit':
  def full_metadata():
   return {i.name:dict(items=dict(i.items()),size=list(i.size),channels=i.channels,alphaMode=i.alpha_mode,colorSpace=i.colorspace_settings.name,fileFormat=i.file_format,source=i.source,filepath=i.filepath,filepathRaw=i.filepath_raw,fakeUser=i.use_fake_user,packedSHA256=hashlib.sha256(bytes(i.packed_file.data)).hexdigest()) for i in bpy.data.images if i.packed_file}
  final_metadata=full_metadata()
  panels=[o for o in s.objects if o.get('cgSupervisedBody12') or o.get('cgSupervisedBody15')];deps=bpy.context.evaluated_depsgraph_get();trees={}
  for o in panels:
   ev=o.evaluated_get(deps);md=ev.to_mesh();trees[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in md.vertices],[tuple(p.vertices) for p in md.polygons]);ev.to_mesh_clear()
  records=[]
  for o in panels:
   if not o.get('cgSupervisedBody15'):continue
   nu,nv=json.loads(o['body15Grid']);rt=rc=tt=tc=it=ic=0;long=0;occluders={}
   # Bounded every-second quad probes explicitly subsampled; no zero-burial claim.
   for p in list(o.data.polygons)[::2]:
    co=sum((o.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices);v=sum(i//nu/(nv-1) for i in p.vertices)/len(p.vertices);n=p.normal.normalized();n=-n if n.y>0 else n;origin=co+n*.035;hits=[]
    for name,t in trees.items():
     if name==o.name:continue
     h,hn,idx,d=t.ray_cast(origin,-n,.075)
     if h is not None and .035-d>.0002:hits.append(name)
    covered=bool(hits)
    if v<=.25:
     rt+=1;rc+=covered;col,row=map(int,o.name.rsplit(' ',1)[-1].split('-'));long+=any((name.startswith(f'CGB15 oblique formed panel {col}-') and int(name.rsplit('-',1)[-1])<row) or(row==0 and name.startswith('CGB12')) for name in hits)
     for name in hits:occluders[name]=occluders.get(name,0)+1
    elif v>=.82:tt+=1;tc+=covered
    else:it+=1;ic+=covered
   records.append(dict(object=o.name,rootSamples=rt,rootCovered=rc,longitudinalRootSamples=long,rootOccluders=occluders,freeEndSamples=tt,freeEndBuried=tc,interiorSamples=it,interiorCovered=ic))
  result['overlap']=dict(method='Every second actual quad-center local-normal BVH ray against all51 evaluated adjacent plates; root v<=.25 end v>=.82; static SUBSAMPLED evidence, not visible-pixel guarantee',panels=records,panelsWithSomeRootCoverage=sum(x['rootCovered']>0 for x in records),panelsWithSomeFreeEndBurial=sum(x['freeEndBuried']>0 for x in records))
  saved={o.name:m.digest(o) for o in s.objects if o.get('cgSupervisedBody12') or o.get('cgSupervisedBody15') or o.get('cgSupervisedBody11')};bpy.ops.wm.open_mainfile(filepath=str(before));s=bpy.context.scene;before_upper={o.name:m.digest(o) for o in s.objects if o.get('cgSupervisedBody12')};assert before_upper==result['upper25Digests'];assert sha(before)=='88903f33a1af045df87e7482d7ff5dd5eaa48cc1ee858c84ea697f0f7efd4566';result['upper25ExactlyMatchesFrozen13']=True
  bpy.ops.wm.open_mainfile(filepath=str(rec));s=bpy.context.scene;source_metadata=full_metadata();assert source_metadata==final_metadata;result['packedFullMetadataExactFromReceiving06']=True;result['packedFullMetadata']=final_metadata;api=apply(s,root,design=args.design);replay={o.name:m.digest(o) for o in s.objects if o.get('cgSupervisedBody12') or o.get('cgSupervisedBody15') or o.get('cgSupervisedBody11')};assert replay==saved;result['standaloneAPIExactNative']=True
 if args.phase=='frames':
  from bpy_extras.object_utils import world_to_camera_view
  records=[]
  for name,q in result['cameras'].items():
   if not ('whole' in name or 'turn' in name):continue
   cam=s.camera;cam.location=q['location'];cam.rotation_euler=q['rotation_euler'];cam.data.type='ORTHO';cam.data.ortho_scale=q['scale'];cam.data.shift_x,cam.data.shift_y=q.get('shift',[0,0]);s.render.resolution_x,s.render.resolution_y=q['resolution'];bpy.context.view_layer.update();coords=[]
   for o in s.objects:
    if o.type=='MESH' and not o.hide_render and o.get('cg1cRegion'):coords.extend([world_to_camera_view(s,cam,o.matrix_world@Vector(c)) for c in o.bound_box])
   mi=[min(v[i] for v in coords) for i in (0,1)];ma=[max(v[i] for v in coords) for i in (0,1)];records.append(dict(image=name,min=mi,max=ma,allCharacterConservativeBoundsInFrame=min(mi)>=0 and max(ma)<=1))
  result['wholeFrameAudit']=dict(method='Readonly frozen native projection; updated depsgraph; all visible character conservative boxes including head+feet',frames=records,allPass=all(x['allCharacterConservativeBoundsInFrame'] for x in records));assert result['wholeFrameAudit']['allPass']
 result['images']={f.name:sha(f) for f in out.glob('*.png')};result['runSeconds']=result.get('runSeconds',0)+time.time()-start;assert sha(native)==result['nativeSHA256'];receipt_path.write_text(json.dumps(result,indent=2)+'\n');print('BODY15_PHASE_COMPLETE',args.phase,out,flush=True)
if __name__=='__main__':run()
