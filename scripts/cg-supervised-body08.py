"""REJECTED BODY08: two attempts failed whole-bird hierarchy. Do not integrate.
Selective source-mask hero partition; unaccepted CG inference.
No artwork texture use. Source pixels describe sheet silhouettes only; depth is
explicitly inferred. Useful lower/rear body05 remains. Original data preserved.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector
SOURCE_SHA='72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4'
REF_SHA='645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114'
# Hand-selected source mask controls, full 1280x853 owner-reissued canon pixels.
# Each outline is individually traced; not a repeated parametric leaf family.
WING_MASKS=[
('cap-a',[(681,246),(705,250),(711,265),(700,277),(685,270),(671,257)],.183),
('cap-b',[(660,254),(683,258),(689,274),(677,288),(661,283),(648,269)],.204),
('cap-c',[(636,265),(659,268),(666,286),(650,301),(632,296),(621,282)],.235),
('cap-d',[(613,279),(637,283),(644,302),(628,319),(609,311),(599,297)],.256),
('front-a',[(702,262),(725,270),(734,290),(730,306),(716,300),(700,280)],.212),
('front-b',[(685,282),(711,291),(721,313),(711,331),(695,323),(678,302)],.267),
('middle-a',[(663,294),(690,304),(696,325),(680,345),(661,337),(651,316)],.306),
('middle-b',[(638,308),(664,315),(669,338),(650,360),(632,350),(623,330)],.333),
('rear-a',[(610,319),(636,327),(638,350),(617,376),(601,366),(595,343)],.312),
('front-c',[(700,324),(720,330),(717,352),(700,375),(684,363),(684,343)],.307),
('middle-c',[(673,343),(695,352),(692,377),(670,402),(654,391),(657,364)],.357),
('middle-d',[(648,361),(669,372),(665,398),(639,425),(625,412),(632,383)],.353),
('rear-b',[(605,366),(630,377),(623,403),(596,431),(581,424),(591,392)],.316),
('rear-c',[(585,386),(605,399),(594,426),(571,449),(557,444),(568,412)],.281),
('tip-a',[(665,399),(682,408),(669,433),(637,453),(623,449),(636,422)],.339),
('tip-b',[(635,418),(652,429),(635,447),(604,466),(590,461),(607,438)],.303),
('tip-c',[(604,435),(619,444),(602,462),(577,474),(566,465),(584,449)],.271),
('rim-a',[(590,339),(611,346),(608,369),(585,398),(574,391),(579,365)],.269),
('join-a',[(712,243),(733,247),(750,263),(746,278),(730,272),(715,259)],.159),
('join-b',[(733,258),(750,264),(766,286),(760,301),(747,290),(739,275)],.170),
]
# Source neck and convex breast front. These masks preserve a clear left-side
# mechanism channel at x<817 in the source. Back-facing partner is inferred.
FRONT_MASKS=[
('throat-a',[(818,205),(840,216),(850,241),(846,264),(831,256),(818,230)]),
('throat-b',[(838,214),(855,226),(870,253),(865,272),(851,264),(844,240)]),
('neck-a',[(826,248),(846,256),(860,283),(854,307),(838,298),(830,274)]),
('neck-b',[(848,263),(869,272),(884,299),(879,323),(861,316),(853,290)]),
('neck-c',[(870,270),(890,282),(906,313),(902,331),(885,325),(878,300)]),
('breast-a',[(830,291),(851,305),(860,338),(851,365),(833,354),(830,325)]),
('breast-b',[(855,313),(878,322),(889,357),(881,383),(861,373),(856,346)]),
('breast-c',[(881,323),(903,331),(918,365),(912,390),(892,382),(885,354)]),
('breast-d',[(903,314),(920,329),(935,362),(934,385),(918,378),(914,351)]),
('lower-a',[(829,354),(851,367),(858,397),(849,422),(831,410),(824,382)]),
('lower-b',[(858,374),(881,384),(887,414),(875,441),(855,429),(853,401)]),
('lower-c',[(890,383),(912,391),(910,419),(894,447),(878,441),(883,411)]),
('lower-d',[(915,383),(932,390),(925,420),(905,448),(894,446),(904,416)]),
('keel',[(850,424),(877,441),(885,460),(872,476),(851,465),(838,444)]),
]
# Explicit visual registration: source projected y is monotonic model height.
# These registration controls are inferred, not camera calibration or anatomy.
HEIGHT=[(205,1.56),(250,1.47),(300,1.33),(350,1.20),(400,1.06),(477,.865)]
FRONT_DEPTH=[(1.56,-.234,.112),(1.47,-.194,.098),(1.36,-.205,.112),(1.29,-.274,.149),(1.20,-.367,.210),(1.10,-.400,.227),(.98,-.356,.217),(.865,-.275,.172)]
def interp(rows,x):
 rows=sorted(rows)
 if x<=rows[0][0]:return rows[0][1:]
 if x>=rows[-1][0]:return rows[-1][1:]
 for a,b in zip(rows,rows[1:]):
  if a[0]<=x<=b[0]:
   t=(x-a[0])/(b[0]-a[0]);return [v*(1-t)+w*t for v,w in zip(a[1:],b[1:])]
def apply(scene,root_path=None,era='builder'):
 if any(o.get('cgSupervisedBody08') for o in scene.objects):raise RuntimeError('Reload receiving native')
 original=list(scene.objects);made=[];hidden=[];records=[];mats={};mat_sources={}
 for o in original:
  if o.type!='MESH' or o.hide_render or not o.get('cgSupervisedBody05'):continue
  for i,f in enumerate(json.loads(o.get('cgSurfaceFamilies','[]'))):
   if i<len(o.data.materials) and o.data.materials[i]:
    mats.setdefault(f,o.data.materials[i]);mat_sources.setdefault(f,{'object':o.name,'slot':i,'material':o.data.materials[i].name})
 assert all(k in mats for k in ('wing-armor','breast-armor','black-iron'))
 # Superseded rows are declared. Retain lower shield, lower breast and all
 # rear-neck sheets, channel framing, machinery, original transforms/anchors.
 for o in original:
  if o.type!='MESH' or o.hide_render or not o.get('cgSupervisedBody05'):continue
  n=o.name;hide=False
  if 'shield curved feather' in n:hide=int(n.rsplit(' ',1)[1].split('-')[0]) in (3,4,5,6) and int(n.rsplit('-',1)[-1]) in (2,3,4)
  elif 'small shoulder covert' in n:hide=False
  elif 'cervical curved lamina' in n:hide=int(n.rsplit('-',1)[-1]) in (0,1,2,3)
  elif 'breast curved feather' in n:hide=int(n.rsplit(' ',1)[1].split('-')[0])<=7 and int(n.rsplit('-',1)[-1]) in (1,2,3,4,5)
  if hide:o.hide_render=True;o.hide_set(True);hidden.append(n)
 coll=bpy.data.collections.new('BODY08 source traced hero partitions');scene.collection.children.link(coll)
 def sheet(label,mask,side,region,depth=None):
  cx=sum(p[0] for p in mask)/len(mask);cy=sum(p[1] for p in mask)/len(mask)
  xmin=min(p[0] for p in mask);xmax=max(p[0] for p in mask);ymin=min(p[1] for p in mask);ymax=max(p[1] for p in mask)
  # Quadratic rounded corners preserve individually traced free-end contours.
  border=[]
  for i,b in enumerate(mask):
   a=mask[i-1];c=mask[(i+1)%len(mask)]
   start=Vector(b)*.78+Vector(a)*.22;end=Vector(b)*.78+Vector(c)*.22
   for j in range(4):
    t=j/4;border.append(tuple(start*(1-t)**2+Vector(b)*2*t*(1-t)+end*t*t))
  n=len(border);verts=[];uv=[]
  depth_fit=None
  if region=='wing':
   backing=scene.objects['CG supervised '+('left' if side==-1 else 'right')+' compact shield recess']
   inv=backing.matrix_world.inverted();target_y=.26-(cx-550)/216*.46;target_z=1.400-(cy-240)/234*.455
   origin=Vector((side*1.0,target_y,target_z));direction=Vector((-side,0,0))
   hit,loc,normal,index=backing.ray_cast(inv@origin,(inv.to_3x3()@direction).normalized())
   if hit:
    world=backing.matrix_world@loc;normal=(backing.matrix_world.to_3x3()@normal).normalized()
    depth_fit={'centerDepth':abs(world.x)+.014,'slopeY':max(-1.3,min(1.3,-normal.y/(normal.x*side))),'slopeZ':max(-1.3,min(1.3,-normal.z/(normal.x*side))),'method':'Independent source-mask tangent plane sampled at center of receiving shield recess; depth inferred'}

  def point(px,py,r):
   if region=='wing':
    y=.26-(px-550)/216*.46;z=1.400-(py-240)/234*.455
    # Independent depth plane slopes plus a shallow sheet crown. Per-sheet
    # center depths are explicit in WING_MASKS; no shared enclosing shell.
    xx=depth+.09*(py-cy)/234-.028*(px-cx)/216+.007*(1-r*r)
    if depth_fit:xx=depth_fit['centerDepth']+depth_fit['slopeY']*(y-target_y)+depth_fit['slopeZ']*(z-target_z)+.003*(1-r*r)

    return (side*xx,y,z)
   z=interp(HEIGHT,py)[0];front,rx=interp(FRONT_DEPTH,z)
   angle=(px-879)/62*.91
   return (rx*math.sin(angle),front+rx*(1-math.cos(angle))-.006*(1-r*r),z)
  for r in (.0,.33,.66,1.0):
   for px,py in border:
    xx=cx+(px-cx)*r;yy=cy+(py-cy)*r;verts.append(point(xx,yy,r));uv.append(((xx-xmin)/(xmax-xmin),(yy-ymin)/(ymax-ymin)))
  faces=[]
  for ring in range(3):
   for j in range(n):faces.append((ring*n+j,ring*n+(j+1)%n,(ring+1)*n+(j+1)%n,(ring+1)*n+j))
  mesh=bpy.data.meshes.new(label);mesh.from_pydata(verts,[],faces);mesh.update()
  obj=bpy.data.objects.new('CGB08 '+label,mesh);coll.objects.link(obj)
  family='wing-armor' if region=='wing' else 'breast-armor'
  for f in (family,'black-iron'):mesh.materials.append(mats[f])
  layer=mesh.uv_layers.new(name='body05-local-curved-uv')
  for p in mesh.polygons:
   p.use_smooth=True
   for li in p.loop_indices:layer.data[li].uv=uv[mesh.loops[li].vertex_index]
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
  # Orient the sheet toward its visible region.
  normal=sum((f.normal for f in bm.faces),Vector())
  desired=Vector((side,0,0)) if region=='wing' else Vector((0,-1,0))
  if normal.dot(desired)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  bm.to_mesh(mesh);bm.free()
  sol=obj.modifiers.new('thin inferred sheet stock','SOLIDIFY');sol.thickness=.0018;sol.offset=-1;sol.material_offset=1;sol.material_offset_rim=1
  bevel=obj.modifiers.new('fine rolled edge','BEVEL');bevel.width=.0005;bevel.segments=2
  for k,v in {'cgSupervisedBody05':True,'cgSupervisedBody08':True,'cg1cRegion':region,'cg2bRegion':region,'surfaceRole':family,'cgSurfaceFamilies':json.dumps([family,'black-iron']),'cgBodyUVConvention':'normalized per-mask u,v; root at v=0, tip v=1','exteriorEras':'maker,mechanic,builder','sourceImageSHA256':REF_SHA,'sourcePixelMask':json.dumps(mask),'depthStatus':'Inferred local depth and projected registration; not calibrated','sheetThickness':.0018}.items():obj[k]=v
  record={'object':obj.name,'sourceMaskPixels':mask,'sourceImageSHA256':REF_SHA,'region':region,'depthCenterInferred':depth,'receivingTangentDepthInference':depth_fit,'side':side,'mirroredUnseenSideInferred':side==1 if region=='wing' else False,'generatedControlVertices':verts}
  records.append(record);made.append(obj)
 for side in (-1,1):
  for label,mask,depth in WING_MASKS:sheet(str(side)+' '+label,mask,side,'wing',depth)
 for label,mask in FRONT_MASKS:sheet(label,mask,0,'neck' if 'throat' in label or 'neck' in label else 'body')
 bpy.context.view_layer.update()
 return {'module':'cg-supervised-body08','era':era,'newMeshes':len(made),'retainedHidden':hidden,'sourcePartitions':records,'actualVisibleReceivingMaterialSources':mat_sources,'method':'Individual source traced macro sheet masks with independently inferred depth; lower and unseen body05 retained','limits':['Source registration and every depth are visual inferences','Unseen side mirrored and unaccepted','Original stance remains fixed','No final source likeness or owner acceptance claim']}

def digest(o):
 h=hashlib.sha256();data=[[tuple(r) for r in o.matrix_world],o.parent.name if o.parent else None]
 if o.type=='MESH':data += [[tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],[(u.name,[tuple(v.uv) for v in u.data]) for u in o.data.uv_layers],[m.name if m else None for m in o.data.materials],[p.material_index for p in o.data.polygons]]
 for v in data:h.update(repr(v).encode())
 return h.hexdigest()
def diagnostic():
 p=argparse.ArgumentParser();p.add_argument('--input-root',required=True);p.add_argument('--attempt',default='attempt01');p.add_argument('--resolution',type=int,default=800);p.add_argument('--samples',type=int,default=6);args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 root=Path(__file__).resolve().parents[1];inp=Path(args.input_root);out=root/'assets/audit/cg-supervised-body08'/args.attempt;out.mkdir(parents=True,exist_ok=True)
 source=inp/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend';ref=inp/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
 assert sha(source)==SOURCE_SHA;assert sha(ref)==REF_SHA
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
 frozen={o.name:digest(o) for o in s.objects if o.type in ('MESH','EMPTY')};visibility={o.name:o.hide_render for o in s.objects if o.type=='MESH'}
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=args.samples;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
 prior=json.loads((inp/'assets/audit/cg-supervised01/attempt06/builder/receipt.json').read_text());cam=s.camera;cameras={};initiallights={o.name:(o.location.copy(),o.rotation_euler.copy(),o.data.energy,o.data.color[:],o.data.size) for o in s.objects if o.type=='LIGHT'}
 clay=bpy.data.materials.new('Body05 diagnostic clay');clay.diffuse_color=(.34,.34,.34,1);clay.use_nodes=True;clay.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.64;clay.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.23,.23,.23,1)
 def render(name,view='whole',claypass=False,grazing=False):
  q=json.loads((inp/'assets/audit/cg-supervised-camera04/receipt.json').read_text())['hypotheses']['ortho-35']['camera'];cam.location=q['location'];cam.rotation_euler=q['rotation_euler'];cam.data.type='ORTHO';cam.data.ortho_scale=q['ortho_scale'];cam.data.shift_x,cam.data.shift_y=q['shift']
  s.render.resolution_x=args.resolution;s.render.resolution_y=round(args.resolution*853/1280)
  if view!='whole':
   position={'side':(-6,0,1.2),'front':(0,-6,1.2),'body':(-6,-2.4,1.5)}[view];target=(0,-.045,1.17);cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.00;cam.data.shift_x=cam.data.shift_y=0;s.render.resolution_y=round(args.resolution*853/1280)
  s.view_layers[0].material_override=clay if claypass else None
  for o in s.objects:
   if o.type!='LIGHT':continue
   loc,rot,power,color,size=initiallights[o.name];o.location=loc;o.rotation_euler=rot;o.data.energy=power;o.data.color=color;o.data.size=size
  if grazing:
   lights=[o for o in s.objects if o.type=='LIGHT'];lights[0].location=(-1,-.8,2.5);lights[0].rotation_euler=(Vector((0,0,1.1))-lights[0].location).to_track_quat('-Z','Y').to_euler();lights[0].data.size=.28;lights[0].data.energy=140
   for o in lights[1:]:o.data.energy*=.18
  cameras[name]={'location':list(cam.location),'rotation_euler':list(cam.rotation_euler),'scale':cam.data.ortho_scale,'shift':[cam.data.shift_x,cam.data.shift_y],'resolution':[s.render.resolution_x,s.render.resolution_y],'clay':claypass,'lights':[{'name':o.name,'location':list(o.location),'rotation':list(o.rotation_euler),'power':o.data.energy,'color':list(o.data.color),'size':o.data.size} for o in s.objects if o.type=='LIGHT']}
  s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 render('before-whole-pbr');result=apply(s,inp,'builder');render('after-whole-pbr');render('after-whole-clay',claypass=True)
 for stage in ('before','after'):
  for o in s.objects:
   if o.get('cgSupervisedBody08'):o.hide_render=stage=='before'
   elif o.name in result['retainedHidden']:o.hide_render=stage=='after'
  render(stage+'-whole-clay',claypass=True);render(stage+'-whole-workshop',grazing=True);render(stage+'-body-grazing-clay','body',True,True);render(stage+'-front-clay','front',True);render(stage+'-side-clay','side',True);render(stage+'-body-pbr','body')
 s.view_layers[0].material_override=None
 for i in range(8):
  a=math.radians(i*45);target=Vector((0,-.04,1));cam.location=target+Vector((6*math.sin(a),-6*math.cos(a),1.02));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.15;cam.data.shift_x=cam.data.shift_y=0;s.render.resolution_x=640;s.render.resolution_y=427
  name=f'turn-{i*45:03d}';s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);cameras[name]={'location':list(cam.location),'rotation':list(cam.rotation_euler),'scale':cam.data.ortho_scale,'resolution':[640,427]}
 render('after-whole-pbr')
 s.view_layers[0].material_override=None
 changed=[n for n,d in frozen.items() if digest(s.objects[n])!=d];unexpected=[n for n,v in visibility.items() if s.objects[n].hide_render!=v and n not in result['retainedHidden']];assert not changed and not unexpected,(changed,unexpected)
 bpy.context.preferences.filepaths.save_version=0;native=out/'murderbird-body08.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native));nativehash=sha(native)
 bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;finite=[]
 for o in s.objects:
  if not o.get('cgSupervisedBody08'):continue
  assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
  assert all(math.isfinite(c) and -.00001<=c<=1.00001 for uv in o.data.uv_layers for v in uv.data for c in v.uv)
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());md=ev.to_mesh();assert all(math.isfinite(c) for v in md.vertices for c in v.co);finite.append({'name':o.name,'vertices':len(md.vertices),'evaluatedFinite':True,'normalizedUV':True});ev.to_mesh_clear()
 changedreadback=[n for n,d in frozen.items() if digest(bpy.context.scene.objects[n])!=d];assert not changedreadback
 result.update(finiteEvaluatedGeometryAndUV=finite,sourceSHA256=sha(source),sourceBinaryPreserved=sha(source)==SOURCE_SHA,referenceSHA256=sha(ref),nativeSHA256=nativehash,originalMeshesAndAnchorsChecked=len(frozen),receivingGeometryUVMaterialIndicesTransformsChanged=changed,savedNativePreservationReadback=changedreadback,unexpectedVisibilityChanges=unexpected,cameras=cameras,renderSettings={'engine':'CYCLES','samples':args.samples,'denoise':True,'viewTransform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure},images={f.name:sha(f) for f in out.glob('*.png')},status='Unaccepted CG proposal; likeness not established')
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('BODY08_COMPLETE',out)
if __name__=='__main__':diagnostic()
