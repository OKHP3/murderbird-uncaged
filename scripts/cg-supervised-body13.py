"""BODY13: mid/lower breast planforms only. Deterministic from receiving06.
Preserves BODY12 upper panels exactly; native sources resolved in architect ROOT.
"""
import argparse,hashlib,json,math,sys,importlib.util
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
REF_SHA='645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114'
CANDIDATE_SHA='538c51bcdbf5bfce95a0932fdbbb0f5868b446f4985346d15e6cacd32430e633'
RECEIVING_SHA='72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4'
BODY12_SHA='31635008853aa813bedec4a71623c5cc71faeeafe50967f244489fae865642d9'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(root):
 spec=importlib.util.spec_from_file_location('body12',Path(root)/'scripts/cg-supervised-body12.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def apply(scene,root_path=None,era='builder'):
 root=Path(root_path or ROOT);m=module(root)
 if any(o.get('cgSupervisedBody13') for o in scene.objects):raise RuntimeError('Reload receiving06; BODY13 already present')
 if not any(o.get('cgSupervisedBody12') for o in scene.objects):m.apply(scene,root,era)
 retained={};removed=[]
 for o in list(scene.objects):
  if not o.get('cgSupervisedBody12'):continue
  bounds=json.loads(o['body12GuideParamBounds'])
  if bounds[2]<.40:retained[o.name]=m.digest(o)
  else:removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
 guide=next(o for o in scene.objects if o.get('cgSupervisedBody11'));deps=bpy.context.evaluated_depsgraph_get();ev=guide.evaluated_get(deps);md=ev.to_mesh();md.calc_loop_triangles();layer=md.uv_layers.active
 tuv=[];world=[];points=[]
 for t in md.loop_triangles:
  if md.polygons[t.polygon_index].material_index:continue
  uv=[Vector((*layer.data[i].uv,0)) for i in t.loops];tuv.append(uv);world.append([guide.matrix_world@md.vertices[i].co for i in t.vertices]);points.extend(uv)
 tree=BVHTree.FromPolygons(points,[(3*i,3*i+1,3*i+2) for i in range(len(tuv))],all_triangles=True);hitmax=0
 def surface(u,v):
  nonlocal hitmax
  q=Vector((u,v,0));h,n,idx,d=tree.find_nearest(q);hitmax=max(hitmax,d);assert d<2e-6,(u,v,d)
  a,b,c=tuv[idx];p0,p1,p2=world[idx];ab=b-a;ac=c-a;aq=h-a;den=ab.x*ac.y-ab.y*ac.x;w1=(aq.x*ac.y-aq.y*ac.x)/den;w2=(ab.x*aq.y-ab.y*aq.x)/den
  return p0*(1-w1-w2)+p1*w1+p2*w2
 def normal(u,v):
  du=surface(u+.00005,v)-surface(u-.00005,v);dv=surface(u,min(.99995,v+.00005))-surface(u,max(.00005,v-.00005));n=du.cross(dv).normalized();return -n if n.y>0 else n
 mats={}
 for o in scene.objects:
  if o.type=='MESH' and o.get('cgSupervisedBody05'):
   for i,f in enumerate(json.loads(o.get('cgSurfaceFamilies','[]'))):
    if i<len(o.data.materials) and o.data.materials[i]:mats.setdefault(f,o.data.materials[i])
 coll=bpy.data.collections.new('BODY13 irregular longitudinal formed breast');scene.collection.children.link(coll);records=[]
 # These independent schedules follow the long staggered blunt breast faces in
 # candidate03, with oblique terminations and seam migration across the keel.
 # Depth and exact divisions remain inferred, never extracted-source geometry.
 schedules=[(.025,.148,[.408,.578,.802,1]),(.127,.254,[.420,.657,.862,1]),(.233,.357,[.408,.602,.833,1]),(.336,.463,[.411,.715,.906,1]),(.442,.570,[.403,.620,.870,1]),(.549,.676,[.408,.760,1]),(.655,.785,[.417,.665,.882,1]),(.764,.884,[.425,.598,.809,1]),(.863,.975,[.408,.718,.936,1])]
 for col,(left,right,ends) in enumerate(schedules):
  for row,(a,b) in enumerate(zip(ends,ends[1:])):
   begin=max(.395,a-.029);end=min(.9999,b+.008);nu,nv=9,29;verts=[];uvs=[];params=[];sign=1 if (col+row)%2 else -1
   for j in range(nv):
    v=j/(nv-1)
    for i in range(nu):
     u=i/(nu-1)
     # Linear diagonal end and tiny straight corner chamfers, no scallop.
     diagonal=sign*.018*(2*u-1)*v**5
     chamfer=.008*max(0,(abs(u-.5)-.35)/.15)*v**7
     gv=max(.0001,min(.9999,begin+(end-begin)*v+diagonal-chamfer))
     # Migrating vertical seams; center piece straddles the old central zipper.
     sway=.011*sign*v+.007*math.sin(math.pi*v)*(1 if col<4 else -1)
     taper=.045*v**7
     gu=max(.02505,min(.97495,left+(right-left)*(taper+(1-2*taper)*u)+sway))
     base=surface(gu,gv);n=normal(gu,gv);relief=-.006+.00015*math.sin(math.pi*u)+.0056*v**3;pos=base+n*relief
     pos.x=max(-.232,min(.232,pos.x));pos.y=max(-.419570,pos.y)
     verts.append(tuple(pos));uvs.append((u,v));params.append((gu,gv))
   faces=[(j*nu+i,j*nu+i+1,(j+1)*nu+i+1,(j+1)*nu+i) for j in range(nv-1) for i in range(nu-1)]
   d=bpy.data.meshes.new(f'body13 formed plate {col}-{row}');d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(f'CGB13 narrow formed panel {col}-{row}',d);coll.objects.link(o)
   for f in ('breast-armor','black-iron'):d.materials.append(mats[f])
   uv=d.uv_layers.new(name='body13-local-normalized')
   for poly in d.polygons:
    poly.use_smooth=True
    for li in poly.loop_indices:uv.data[li].uv=uvs[d.loops[li].vertex_index]
   bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
   if sum((f.normal for f in bm.faces),Vector()).y>0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
   bm.to_mesh(d);bm.free();sol=o.modifiers.new('inward formed metal stock','SOLIDIFY');sol.thickness=.0013;sol.offset=-1;sol.material_offset=1;sol.material_offset_rim=1
   for k,val in dict(cgSupervisedBody13=True,cg1cRegion='body',cg2bRegion='body',surfaceRole='breast-armor',cgSurfaceFamilies=json.dumps(['breast-armor','black-iron']),exteriorEras='maker,mechanic,builder',sourceImageSHA256=REF_SHA,cgConstructionStatus='Inferred mid/lower formed planforms; unaccepted',body13GuideSamples=json.dumps(params),body13GuideParamBounds=json.dumps([left,right,begin,end]),body13Grid=json.dumps([nu,nv])).items():o[k]=val
   records.append(dict(object=o.name,track=col,segment=row,paramBounds=[left,right,begin,end],end='straight diagonal blunt chamfer',faceRelief=.00015,grid=[nu,nv]))
 ev.to_mesh_clear();guide.hide_render=True;guide.hide_set(True);bpy.context.view_layer.update()
 assert all(m.digest(scene.objects[n])==h for n,h in retained.items())
 return dict(module='cg-supervised-body13',newPanels=len(records),upperBody12RetainedDigests=retained,removedBody12MidLowerPanels=removed,sourcePartitions=records,actualGuideUVHitMaxDistance=hitmax,hiddenLegacyManifest=m.HIDE_MANIFEST,hiddenGuide=guide.name,limits=['Planform schedules/side-depth inferred from lockedSept22 and candidate03','No surface-polish pass, added backing or supports','July body excluded','Owner acceptance pending'])

def diagnostic():
 p=argparse.ArgumentParser();p.add_argument('--input-root',default=str(ROOT));p.add_argument('--resolution',type=int,default=640);p.add_argument('--samples',type=int,default=4);args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=Path(args.input_root);m=module(root);out=Path(__file__).resolve().parents[1]/'assets/audit/cg-supervised-body13/attempt01';out.mkdir(parents=True,exist_ok=True)
 rec=root/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend';old=root/'assets/audit/cg-supervised-body12/attempt02/murderbird-body12.blend';assert sha(rec)==RECEIVING_SHA and sha(old)==BODY12_SHA
 assert sha(root/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg')==REF_SHA;assert sha(root/'assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png')==CANDIDATE_SHA
 bpy.ops.wm.open_mainfile(filepath=str(rec));s=bpy.context.scene;frozen={o.name:m.digest(o) for o in s.objects if o.type in ('MESH','EMPTY')};vis={o.name:[o.hide_render,o.hide_viewport,o.hide_get()] for o in s.objects};graphs=m.material_digest();packed=m.packed_image_digest()
 bpy.ops.wm.open_mainfile(filepath=str(old));s=bpy.context.scene;result=apply(s,root);native=out/'murderbird-body13.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native));nativehash=sha(native)
 bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene
 def verify():
  changed=[n for n,h in frozen.items() if m.digest(s.objects[n])!=h];assert not changed,changed
  assert graphs==m.material_digest() and packed==m.packed_image_digest()
  vc=[n for n,v in vis.items() if n not in m.HIDE_MANIFEST and [s.objects[n].hide_render,s.objects[n].hide_viewport,s.objects[n].hide_get()]!=v];assert not vc,vc
  assert all(s.objects[n].hide_render and s.objects[n].hide_get() for n in m.HIDE_MANIFEST)
  assert all(m.digest(s.objects[n])==h for n,h in result['upperBody12RetainedDigests'].items())
  bounds=[];uvchecks=[];deps=bpy.context.evaluated_depsgraph_get()
  for o in s.objects:
   if not (o.get('cgSupervisedBody13') or o.get('cgSupervisedBody12')):continue
   ev=o.evaluated_get(deps);md=ev.to_mesh();bounds.extend([o.matrix_world@v.co for v in md.vertices]);vs=[c for l in md.uv_layers for u in l.data for c in u.uv];assert all(math.isfinite(c) and -1e-6<=c<=1.000001 for c in vs);uvchecks.append(dict(object=o.name,min=min(vs),max=max(vs),evaluated=True));ev.to_mesh_clear()
  bb=dict(min=[min(v[i] for v in bounds) for i in range(3)],max=[max(v[i] for v in bounds) for i in range(3)]);assert bb['min'][0]>=-.23201 and bb['max'][0]<=.23201 and bb['min'][1]>=-.41958,bb
  return dict(originalMeshesAndAnchorsChecked=len(frozen),payloadChanged=changed,graphs=len(graphs),packedMaps=len(packed),upperBody12PanelsPreserved=len(result['upperBody12RetainedDigests']),exact149LegacyHides=True,exactVisibilityOutside149=True,evaluatedBounds=bb,evaluatedUV=uvchecks)
 result['earlySavedReopenedChecks']=verify();(out/'early-native-receipt.json').write_text(json.dumps(result,indent=2));print('BODY13_EARLY_SAVE_REOPEN_PASS',flush=True)
 prior=json.loads((root/'assets/audit/cg-supervised-body12/attempt02/receipt.json').read_text());cameras={};frames=[]
 def render(name,key):
  q=prior['cameras'][key];cam=s.camera;cam.location=q['location'];cam.rotation_euler=q['rotation_euler'];cam.data.type='ORTHO';cam.data.ortho_scale=q['scale'];cam.data.shift_x,cam.data.shift_y=q['shift']
  for l in q['lights']:
   o=s.objects[l['name']];o.location=l['location'];o.rotation_euler=l['rotation'];o.data.energy=l['power'];o.data.color=l['color'];o.data.size=l['size']
  s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=args.samples;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.resolution_x=args.resolution;s.render.resolution_y=round(args.resolution*q['resolution'][1]/q['resolution'][0]);s.render.image_settings.file_format='PNG'
  s.view_layers[0].material_override=bpy.data.materials.get('Body11 diagnostic clay') if q['clay'] else None
  if q['clay'] and s.view_layers[0].material_override is None:
   c=bpy.data.materials.new('Body11 diagnostic clay');c.use_nodes=True;c.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.23,.23,.23,1);c.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.64;s.view_layers[0].material_override=c
  bpy.context.view_layer.update()
  qq=dict(q);qq['resolution']=[s.render.resolution_x,s.render.resolution_y];cameras[name]=qq
  if 'whole' in key:
   from bpy_extras.object_utils import world_to_camera_view
   coords=[world_to_camera_view(s,cam,o.matrix_world@Vector(c)) for o in s.objects if o.type=='MESH' and not o.hide_render and o.get('cg1cRegion') for c in o.bound_box]
   if coords:frames.append(dict(image=name,min=[min(v[i] for v in coords) for i in (0,1)],max=[max(v[i] for v in coords) for i in (0,1)]))
  s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 # Actual three-way whole pair first, before expensive view expansion.
 for path,stage in [(rec,'receiving06'),(old,'frozen12'),(native,'final13')]:
  bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
  render(stage+'-whole35-pbr','after-whole-pbr');render(stage+'-whole35-clay','after-whole-clay')
 print('BODY13_FIRST_THREE_WAY_PAIR_READY',out,flush=True)
 for path,stage in [(rec,'receiving06'),(old,'frozen12'),(native,'final13')]:
  bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
  for suffix,key in [('whole64-pbr','after-whole64-pbr'),('whole64-clay','after-whole64-clay'),('front-whole-pbr','after-front-whole-pbr'),('front-whole-clay','after-front-whole-clay'),('profile-whole-pbr','after-profile-whole-pbr'),('profile-whole-clay','after-profile-whole-clay'),('whole-grazing-pbr','after-whole-grazing-pbr'),('whole-grazing-clay','after-whole-grazing-clay'),('front-pbr','after-front-pbr'),('front-clay','after-front-clay'),('body-grazing-clay','after-body-grazing-clay'),('side-clay','after-side-clay')]:render(stage+'-'+suffix,key)
 bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene
 for i in range(8):
  cam=s.camera;a=math.radians(i*45);target=Vector((0,-.04,1));cam.location=target+Vector((6*math.sin(a),-6*math.cos(a),1.02));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.20;cam.data.shift_x=cam.data.shift_y=0;s.render.resolution_x=640;s.render.resolution_y=427;s.render.engine='CYCLES';s.cycles.samples=args.samples;s.view_layers[0].material_override=None;s.render.image_settings.file_format='PNG';name=f'final13-turn-{i*45:03d}';s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);cameras[name]=dict(location=list(cam.location),rotation_euler=list(cam.rotation_euler),scale=3.20,resolution=[640,427])
 bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;result['finalSavedReopenedChecks']=verify();assert sha(native)==nativehash
 result.update(nativeSHA256=nativehash,receiving06SHA256=sha(rec),frozen12SHA256=sha(old),sourceReferenceSHA256=REF_SHA,candidate03SHA256=CANDIDATE_SHA,originalPayloadDigests=frozen,receivingMaterialGraphDigests=graphs,packedImageDigests=packed,cameras=cameras,wholeFrameBounds=frames,images={f.name:sha(f) for f in out.glob('*.png')},status='Unaccepted CG proposal; whole-source likeness gate pending independent review')
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('BODY13_COMPLETE',out,flush=True)
def audit_native():
 root=ROOT;m=module(root);out=Path(__file__).resolve().parents[1]/'assets/audit/cg-supervised-body13/attempt01';native=out/'murderbird-body13.blend';receipt=json.loads((out/'receipt.json').read_text())
 def image_metadata():
  return {i.name:dict(items=dict(i.items()),size=list(i.size),channels=i.channels,alphaMode=i.alpha_mode,colorSpace=i.colorspace_settings.name,fileFormat=i.file_format,source=i.source,filepath=i.filepath,packedSHA256=sha_bytes(bytes(i.packed_file.data))) for i in bpy.data.images if i.packed_file}
 def sha_bytes(x):return hashlib.sha256(x).hexdigest()
 bpy.ops.wm.open_mainfile(filepath=str(root/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'));source_metadata=image_metadata()
 bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;metadata=image_metadata();assert metadata==source_metadata
 assert sha(native)==receipt['nativeSHA256'];panels=[o for o in s.objects if o.get('cgSupervisedBody13') or o.get('cgSupervisedBody12')];deps=bpy.context.evaluated_depsgraph_get();trees={}
 for o in panels:
  ev=o.evaluated_get(deps);md=ev.to_mesh();trees[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in md.vertices],[tuple(p.vertices) for p in md.polygons]);ev.to_mesh_clear()
 records=[]
 for o in panels:
  grid=json.loads(o.get('body13Grid') or o.get('body12Grid'));nu,nv=grid;rc=rt=tc=tt=ic=it=0;ra=rca=ta=tca=0.;long_root=0;root_hits={}
  for p in o.data.polygons:
   co=sum((o.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices);v=sum(i//nu/(nv-1) for i in p.vertices)/len(p.vertices);n=p.normal.normalized();n=-n if n.y>0 else n;origin=co+n*.035;hits=[]
   for name,t in trees.items():
    if name==o.name:continue
    h,hn,idx,d=t.ray_cast(origin,-n,.075)
    if h is not None and .035-d>.0002:hits.append(name)
   covered=bool(hits)
   if v<=.25:
    rt+=1;rc+=covered;ra+=p.area;rca+=p.area*covered
    for name in hits:root_hits[name]=root_hits.get(name,0)+1
    # Same track preceding segment is longitudinal overlap for BODY13.
    if o.get('cgSupervisedBody13'):
     col,row=map(int,o.name.rsplit(' ',1)[-1].split('-'));long_root+=any((name.startswith(f'CGB13 narrow formed panel {col}-') and int(name.rsplit('-',1)[-1])<row) or (row==0 and name.startswith('CGB12')) for name in hits)
   elif v>=.82:tt+=1;tc+=covered;ta+=p.area;tca+=p.area*covered
   else:it+=1;ic+=covered
  records.append(dict(object=o.name,newBody13=bool(o.get('cgSupervisedBody13')),rootSamples=rt,rootCovered=rc,rootCoveredArea=rca,rootArea=ra,longitudinalRootSamples=long_root,rootOccluders=root_hits,freeEndSamples=tt,freeEndBuried=tc,freeEndBuriedArea=tca,freeEndArea=ta,interiorSamples=it,interiorCovered=ic))
 final_payload={o.name:m.digest(o) for o in s.objects if o.get('cgSupervisedBody13') or o.get('cgSupervisedBody12') or o.get('cgSupervisedBody11')}
 bpy.ops.wm.open_mainfile(filepath=str(root/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'));s=bpy.context.scene;api=apply(s,root);newpayload={o.name:m.digest(o) for o in s.objects if o.get('cgSupervisedBody13') or o.get('cgSupervisedBody12') or o.get('cgSupervisedBody11')};assert newpayload==final_payload
 mismatch=[f for f,h in receipt['images'].items() if sha(out/f)!=h];assert not mismatch
 summary=dict(nativeSHA256=sha(native),nativeFrozenDuringAudit=True,packedImageMetadataExactFromReceiving06=True,packedImageMetadata=metadata,packedMapCount=len(metadata),standaloneFrom06APIExactlyMatchesNative=True,standalonePayloadCount=len(newpayload),imageHashMismatches=mismatch,overlapMethod='Actual quad-center local-normal BVH rays against all evaluated adjacent plates; root v<=.25 and end v>=.82; area-weighted sampled coverage. Adjacent seam burial explicitly counted. No visible-pixel area guarantee.',overlapPanels=records,newPanelsWithLongitudinalRootOverlap=sum(x['longitudinalRootSamples']>0 for x in records if x['newBody13']),newPanelCount=sum(x['newBody13'] for x in records),allPanelsWithRootOverlap=sum(x['rootCovered']>0 for x in records),freeEndsWithSomeAdjacentBurial=sum(x['freeEndBuried']>0 for x in records),limits=['First segments classify coverage by retained upper BODY12 as longitudinal; track migration makes upstream track identity nonunique','Sparse area probes do not establish artifact-free animation','Source placement/depth inferred; owner artistic acceptance pending'])
 (out/'extra-preservation-and-overlap.json').write_text(json.dumps(summary,indent=2)+'\n');print('BODY13_EXTRA_AUDIT_PASS',summary['newPanelsWithLongitudinalRootOverlap'],summary['newPanelCount'],summary['freeEndsWithSomeAdjacentBurial'],flush=True)
def audit_frames():
 from bpy_extras.object_utils import world_to_camera_view
 root=ROOT;out=Path(__file__).resolve().parents[1]/'assets/audit/cg-supervised-body13/attempt01';r=json.loads((out/'receipt.json').read_text());records=[]
 for stage,path in [('receiving06',root/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'),('frozen12',root/'assets/audit/cg-supervised-body12/attempt02/murderbird-body12.blend'),('final13',out/'murderbird-body13.blend')]:
  bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;cam=s.camera
  for name,q in r['cameras'].items():
   if not name.startswith(stage) or not ('whole' in name or 'turn' in name):continue
   cam.location=q['location'];cam.rotation_euler=q['rotation_euler'];cam.data.type='ORTHO';cam.data.ortho_scale=q['scale'];cam.data.shift_x,cam.data.shift_y=q.get('shift',[0,0]);s.render.resolution_x,s.render.resolution_y=q['resolution'];bpy.context.view_layer.update();coords=[];objects=0
   for o in s.objects:
    if o.type!='MESH' or o.hide_render or not o.get('cg1cRegion'):continue
    objects+=1;coords.extend([world_to_camera_view(s,cam,o.matrix_world@Vector(c)) for c in o.bound_box])
   mi=[min(v[i] for v in coords) for i in (0,1)];ma=[max(v[i] for v in coords) for i in (0,1)];records.append(dict(image=name,objects=objects,min=mi,max=ma,allCharacterConservativeBoundsInFrame=min(mi)>=0 and max(ma)<=1))
 result=dict(method='Readonly native projection after explicit depsgraph transform update; conservative visible character object boxes including head and feet',frames=records,allPass=all(x['allCharacterConservativeBoundsInFrame'] for x in records));(out/'whole-frame-audit.json').write_text(json.dumps(result,indent=2)+'\n');print('BODY13_FRAME_AUDIT',len(records),result['allPass'],flush=True)
if __name__=='__main__':
 if '--audit-only' in sys.argv:audit_native()
 elif '--frame-audit' in sys.argv:audit_frames()
 else:diagnostic()
