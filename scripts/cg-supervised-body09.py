"""REJECTED body09: two attempts failed the whole-bird / overlap gate.
One-side open-rib shoulder cassette. New 3D Coons cages from four Bezier rails.
Unaccepted local CG construction inference; exact receiving payload preserved.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector
SOURCE_SHA='72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4'
REF_SHA='645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114'
HIDES=['CG supervised left compact shield recess']+[f'CGB05 -1 shield curved feather {r:02d}-{c}' for r in (3,4,5,6) for c in (2,3,4)]
# Per-sheet controls in metres: root and tip center, root width, side bow,
# longitudinal shoulder sweep. Every cage has its own 3D rail controls.
DESIGNS=[
 ('course1-front',(-.322,-.058,1.312),(-.361,-.023,1.229),.101,.005,.009),
 ('course1-rear',(-.320,.036,1.310),(-.356,.072,1.228),.102,.006,.012),
 ('course2-front',(-.351,-.057,1.267),(-.382,-.018,1.173),.112,.006,.010),
 ('course2-rear',(-.350,.047,1.266),(-.375,.091,1.175),.113,.007,.008),
 ('course3-front',(-.373,-.015,1.221),(-.369,.028,1.124),.113,.005,.010),
 ('course3-rear',(-.369,.095,1.220),(-.354,.144,1.128),.113,.007,.011),
 ('course4-front',(-.365,.022,1.178),(-.357,.068,1.077),.113,.005,.012),
 ('course4-rear',(-.350,.130,1.180),(-.337,.184,1.080),.115,.005,.014),
]
def bezier(c,t):
 return sum((Vector(p)*w for p,w in zip(c,((1-t)**3,3*t*(1-t)**2,3*t*t*(1-t),t**3))),Vector())
def digest(o):
 h=hashlib.sha256();data=[[tuple(r) for r in o.matrix_world],o.parent.name if o.parent else None,sorted(o.keys()),[(k,repr(o[k])) for k in sorted(o.keys())],sorted(c.name for c in o.users_collection)]
 if o.type=='MESH':data += [[tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],[(u.name,[tuple(v.uv) for v in u.data]) for u in o.data.uv_layers],[(a.name,a.domain,a.data_type,repr([repr(v) for v in a.data])) for a in o.data.color_attributes],[m.name if m else None for m in o.data.materials],[p.material_index for p in o.data.polygons]]
 for v in data:h.update(repr(v).encode())
 return h.hexdigest()
def apply(scene,root_path=None,era='builder',allow_rejected_diagnostic=False):
 if not allow_rejected_diagnostic:raise RuntimeError('REJECTED body09: use receiving06; explicit diagnostic override required')
 if any(o.get('cgSupervisedBody09') for o in scene.objects):raise RuntimeError('Reload receiving06')
 original=list(scene.objects);mats={};sources={};made=[];records=[]
 for o in original:
  if o.type!='MESH' or o.hide_render or not o.get('cgSupervisedBody05'):continue
  for i,f in enumerate(json.loads(o.get('cgSurfaceFamilies','[]'))):
   if i<len(o.data.materials) and o.data.materials[i]:mats.setdefault(f,o.data.materials[i]);sources.setdefault(f,dict(object=o.name,slot=i,material=o.data.materials[i].name))
 assert all(k in mats for k in ('wing-armor','black-iron'))
 for n in HIDES:
  assert n in scene.objects,n
  scene.objects[n].hide_render=True;scene.objects[n].hide_set(True)
 coll=bpy.data.collections.new('BODY09 open-rib left shoulder cassette');scene.collection.children.link(coll)
 def mesh(name,verts,faces,families,uvs):
  d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new('CGB09 '+name,d);coll.objects.link(o)
  for f in families:d.materials.append(mats[f])
  u=d.uv_layers.new(name='body05-local-curved-uv')
  for p in d.polygons:
   p.use_smooth=True
   for i in p.loop_indices:u.data[i].uv=uvs[d.loops[i].vertex_index]
  bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
  if sum((f.normal for f in bm.faces),Vector()).x>0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  bm.to_mesh(d);bm.free()
  for k,v in dict(cgSupervisedBody05=True,cgSupervisedBody09=True,cg1cRegion='wing',cg2bRegion='wing',surfaceRole=families[0],cgSurfaceFamilies=json.dumps(families),exteriorEras='maker,mechanic,builder',sourceImageSHA256=REF_SHA,cgConstructionStatus='Inferred local 3D rail cassette; unaccepted',cgBodyUVConvention='normalized per-sheet u across / v covered-root to free-tip').items():o[k]=v
  made.append(o);return o
 for label,root,tip,width,bow,sweep in DESIGNS:
  r=Vector(root);t=Vector(tip);rl=r+Vector((.002,-width/2,0));rr=r+Vector((.002,width/2,0));tl=t+Vector((.001,-.003,.003));tr=t+Vector((.001,.003,.003))
  # Root bends gently to shoulder; narrow rounded end rail, outward side
  # crowns, and independent side sweep create compound curvature.
  rails={'coveredRoot':[tuple(rl),tuple(rl+Vector((-.004,width*.30,.004))),tuple(rr+Vector((-.006,-width*.30,.006))),tuple(rr)],
   'freeTip':[tuple(tl),tuple(tl+Vector((-.001,.001,-.005))),tuple(tr+Vector((-.001,-.001,-.005))),tuple(tr)],
   'frontSide':[tuple(rl),tuple(rl.lerp(tl,.32)+Vector((-bow,-sweep,0))),tuple(rl.lerp(tl,.70)+Vector((-bow,-width*.28,0))),tuple(tl)],
   'rearSide':[tuple(rr),tuple(rr.lerp(tr,.32)+Vector((-bow,sweep*.35,0))),tuple(rr.lerp(tr,.70)+Vector((-bow,width*.22,0))),tuple(tr)]}
  vs=[];uv=[];nu=13;nv=25
  for j in range(nv):
   v=j/(nv-1)
   for i in range(nu):
    u=i/(nu-1);a=bezier(rails['coveredRoot'],u)*(1-v)+bezier(rails['freeTip'],u)*v;b=bezier(rails['frontSide'],v)*(1-u)+bezier(rails['rearSide'],v)*u
    bilinear=rl*(1-u)*(1-v)+rr*u*(1-v)+tl*(1-u)*v+tr*u*v
    p=a+b-bilinear;vs.append(tuple(p));uv.append((u,v))
  fs=[(j*nu+i,j*nu+i+1,(j+1)*nu+i+1,(j+1)*nu+i) for j in range(nv-1) for i in range(nu-1)]
  o=mesh(label,vs,fs,['wing-armor','black-iron'],uv);sol=o.modifiers.new('thin sheet stock','SOLIDIFY');sol.thickness=.0018;sol.offset=-1;sol.material_offset=1;sol.material_offset_rim=1
  bevel=o.modifiers.new('rolled free edge','BEVEL');bevel.width=.00035;bevel.segments=2
  o['cgBody09Rails']=json.dumps(rails);o['sheetThickness']=.0018
  records.append(dict(object=o.name,rails=rails,coveredRootRange=[0,.45],freeTipRange=[.75,1],controlVertices=vs,grid=[nu,nv],overlapOrder='course1 over course2 roots; course2 over course3 roots; course3 over course4 roots; free ends proud of following course'))
  # A narrow root ribbon only: no enclosed shell. It remains beneath this
  # individual root and terminates before the visible central/free-end face.
  ribvs=[];ribuv=[]
  for j in range(2):
   for i in range(13):
    u=i/12;p=bezier(rails['coveredRoot'],u)+Vector((.007,.003*j,-.010*j));ribvs.append(tuple(p));ribuv.append((u,float(j)))
  rib=mesh(label+' root rib',ribvs,[(i,i+1,i+14,i+13) for i in range(12)],['black-iron'],ribuv);rs=rib.modifiers.new('narrow support thickness','SOLIDIFY');rs.thickness=.003;rib['supportWidth']=.0105;rib['supportScope']='covered root only'
 bpy.context.view_layer.update()
 return dict(module='cg-supervised-body09',era=era,newMeshes=len(made),newSheets=8,narrowRootRibs=8,retainedHidden=HIDES,actualVisibleReceivingMaterialSources=sources,sourcePartitions=records,method='Eight unique 3D four-Bezier-rail Coons cages; narrow root ribbons; one side only',limits=['Every rail and depth control is inferred','Independent visual QC and owner artistic acceptance pending','Other body/front/neck hierarchy unresolved','No receiving material changes'])

def material_digest():
 result={}
 for m in bpy.data.materials:
  if not m.name.startswith('CG metal05 /'):continue
  values=[m.name,tuple(m.diffuse_color),m.use_nodes]
  if m.use_nodes:
   for n in m.node_tree.nodes:
    inputs=[]
    for inp in n.inputs:
     if hasattr(inp,'default_value'):
      v=inp.default_value
      try:v=list(v)
      except TypeError:pass
      inputs.append((inp.name,v))
    values.append((n.name,n.bl_idname,n.label,inputs,n.image.name if hasattr(n,'image') and n.image else None))
   values.append([(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links])
  result[m.name]=hashlib.sha256(repr(values).encode()).hexdigest()
 return result

def depth_validation(scene):
 from mathutils.bvhtree import BVHTree
 deps=bpy.context.evaluated_depsgraph_get();trees={}
 for o in scene.objects:
  if not o.get('cgSupervisedBody09'):continue
  ev=o.evaluated_get(deps);m=ev.to_mesh();trees[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);ev.to_mesh_clear()
 records=[]
 for o in scene.objects:
  if not o.get('cgBody09Rails'):continue
  points=[(v.co[:],i//13/24,'vertex') for i,v in enumerate(o.data.vertices)]
  for edge in o.data.edges:
   a,b=edge.vertices;points.append((tuple((o.data.vertices[a].co+o.data.vertices[b].co)/2),((a//13)+(b//13))/48,'edge-midpoint'))
  tested=hits=buried_free=buried_body=covered=0;minimum_free=None
  for co,v,kind in points:
   p=Vector(co);candidate=[]
   for name,tree in trees.items():
    if name==o.name:continue
    h,n,i,d=tree.ray_cast(Vector((-1,p.y,p.z)),Vector((1,0,0)))
    if h is not None:candidate.append((h.x,name))
   tested+=1
   if not candidate:continue
   hits+=1;xx,name=min(candidate);clearance=xx-p.x
   if v>=.75:
    minimum_free=clearance if minimum_free is None else min(minimum_free,clearance)
    if clearance<-.0008:buried_free+=1
   elif clearance<-.0008:
    if v<=.45:covered+=1
    else:buried_body+=1
  records.append(dict(object=o.name,sampledVerticesAndEdgeMidpoints=tested,adjacentSheetOrRootRibHits=hits,coveredRootSamplesBehind=covered,nonRootSamplesBehind=buried_body,freeTipSamplesBehind=buried_free,minimumFreeTipClearance=minimum_free))
 return dict(method='All control vertices and grid-edge midpoints raycast in outward -X direction against every evaluated adjacent cassette sheet/root-rib; covered v<=.45 treated as lap, v>=.75 free end. Local depth only; no pixel-visible area claim.',sheets=records)

def diagnostic():
 p=argparse.ArgumentParser();p.add_argument('--input-root',required=True);p.add_argument('--attempt',default='attempt01');p.add_argument('--resolution',type=int,default=800);p.add_argument('--samples',type=int,default=6);args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 root=Path(__file__).resolve().parents[1];inp=Path(args.input_root);out=root/'assets/audit/cg-supervised-body09'/args.attempt;out.mkdir(parents=True,exist_ok=True)
 source=inp/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend';ref=inp/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
 assert sha(source)==SOURCE_SHA;assert sha(ref)==REF_SHA
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
 saved_transforms={o.name:(o.location.copy(),o.rotation_euler.copy(),o.scale.copy()) for o in s.objects if o.type in ('CAMERA','LIGHT')};saved_camera=(s.camera.data.type,s.camera.data.ortho_scale,s.camera.data.shift_x,s.camera.data.shift_y);original_materials=material_digest()
 frozen={o.name:digest(o) for o in s.objects if o.type in ('MESH','EMPTY')};visibility={o.name:o.hide_render for o in s.objects if o.type=='MESH'}
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=args.samples;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
 cam=s.camera;cameras={};initiallights={o.name:(o.location.copy(),o.rotation_euler.copy(),o.data.energy,o.data.color[:],o.data.size) for o in s.objects if o.type=='LIGHT'}
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
 render('before-whole-pbr');render('before-whole-clay',claypass=True);result=apply(s,inp,'builder',allow_rejected_diagnostic=True);render('after-whole-pbr');render('after-whole-clay',claypass=True)
 for stage in ('before','after'):
  for o in s.objects:
   if o.get('cgSupervisedBody09'):o.hide_render=stage=='before'
   elif o.name in result['retainedHidden']:o.hide_render=stage=='after'
  render(stage+'-whole-clay',claypass=True);render(stage+'-whole-workshop',grazing=True);render(stage+'-body-grazing-clay','body',True,True);render(stage+'-front-clay','front',True);render(stage+'-side-clay','side',True);render(stage+'-body-pbr','body')
 s.view_layers[0].material_override=None
 for i in range(8):
  a=math.radians(i*45);target=Vector((0,-.04,1));cam.location=target+Vector((6*math.sin(a),-6*math.cos(a),1.02));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.15;cam.data.shift_x=cam.data.shift_y=0;s.render.resolution_x=640;s.render.resolution_y=427
  name=f'turn-{i*45:03d}';s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);cameras[name]={'location':list(cam.location),'rotation':list(cam.rotation_euler),'scale':cam.data.ortho_scale,'resolution':[640,427]}
 render('after-whole-pbr')
 s.view_layers[0].material_override=None
 for n,(loc,rot,scale) in saved_transforms.items():s.objects[n].location=loc;s.objects[n].rotation_euler=rot;s.objects[n].scale=scale
 cam.data.type,cam.data.ortho_scale,cam.data.shift_x,cam.data.shift_y=saved_camera
 bpy.context.view_layer.update();depth=depth_validation(s);assert original_materials==material_digest(),'Receiving graphs changed'
 changed=[n for n,d in frozen.items() if digest(s.objects[n])!=d];unexpected=[n for n,v in visibility.items() if s.objects[n].hide_render!=v and n not in result['retainedHidden']];assert not changed and not unexpected,(changed,unexpected)
 bpy.data.materials.remove(clay);bpy.context.preferences.filepaths.save_version=0;native=out/'murderbird-body09.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native));nativehash=sha(native)
 bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;finite=[]
 for o in s.objects:
  if not o.get('cgSupervisedBody09'):continue
  assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
  assert all(math.isfinite(c) and -.00001<=c<=1.00001 for uv in o.data.uv_layers for v in uv.data for c in v.uv)
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());md=ev.to_mesh();assert all(math.isfinite(c) for v in md.vertices for c in v.co);finite.append({'name':o.name,'vertices':len(md.vertices),'evaluatedFinite':True,'normalizedUV':True});ev.to_mesh_clear()
 changedreadback=[n for n,d in frozen.items() if digest(bpy.context.scene.objects[n])!=d];assert not changedreadback
 assert original_materials==material_digest(),'Receiving material readback changed'
 result.update(localAdjacentSheetAndSupportDepth=depth,receivingMaterialGraphsPreserved=True,receivingMaterialGraphDigests=original_materials,diagnosticCameraTransformsRestoredBeforeSave=True,finiteEvaluatedGeometryAndUV=finite,sourceSHA256=sha(source),sourceBinaryPreserved=sha(source)==SOURCE_SHA,referenceSHA256=sha(ref),nativeSHA256=nativehash,originalMeshesAndAnchorsChecked=len(frozen),receivingGeometryUVMaterialIndicesTransformsChanged=changed,savedNativePreservationReadback=changedreadback,unexpectedVisibilityChanges=unexpected,cameras=cameras,renderSettings={'engine':'CYCLES','samples':args.samples,'denoise':True,'viewTransform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure},images={f.name:sha(f) for f in out.glob('*.png')},status='Unaccepted CG proposal; likeness not established')
 result['criterion']=json.loads((root/'assets/audit/cg-supervised-body09/qc08-next-experiment.json').read_text());result['authoringScriptSHA256']=sha(Path(__file__));result['candidate03SHA256']=sha(inp/'assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png')
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('BODY09_COMPLETE',out)
if __name__=='__main__':diagnostic()
