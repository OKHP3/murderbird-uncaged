"""One-side open-rib shoulder cassette. New 3D Coons cages from four Bezier rails.
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
 ('upper-front',(-.322,-.068,1.316),(-.386,-.014,1.204),.092,.009,.014),
 ('upper-rear',(-.321,.020,1.313),(-.388,.083,1.206),.096,.012,.010),
 ('middle-front',(-.367,-.063,1.264),(-.388,.016,1.135),.100,.012,.022),
 ('middle-center',(-.375,.011,1.261),(-.386,.093,1.130),.104,.016,.017),
 ('middle-rear',(-.364,.086,1.261),(-.369,.165,1.136),.105,.011,.022),
 ('lower-front',(-.373,-.004,1.201),(-.365,.066,1.068),.105,.013,.025),
 ('lower-center',(-.373,.070,1.199),(-.357,.143,1.075),.103,.010,.019),
 ('lower-rear',(-.350,.145,1.202),(-.336,.213,1.084),.097,.009,.026),
]
def bezier(c,t):
 return sum((Vector(p)*w for p,w in zip(c,((1-t)**3,3*t*(1-t)**2,3*t*t*(1-t),t**3))),Vector())
def digest(o):
 h=hashlib.sha256();data=[[tuple(r) for r in o.matrix_world],o.parent.name if o.parent else None,sorted(o.keys()),[(k,repr(o[k])) for k in sorted(o.keys())],sorted(c.name for c in o.users_collection)]
 if o.type=='MESH':data += [[tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],[(u.name,[tuple(v.uv) for v in u.data]) for u in o.data.uv_layers],[(a.name,a.domain,a.data_type,repr([repr(v) for v in a.data])) for a in o.data.color_attributes],[m.name if m else None for m in o.data.materials],[p.material_index for p in o.data.polygons]]
 for v in data:h.update(repr(v).encode())
 return h.hexdigest()
def apply(scene,root_path=None,era='builder'):
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
  records.append(dict(object=o.name,rails=rails,coveredRootRange=[0,.25],freeTipRange=[.75,1],controlVertices=vs,grid=[nu,nv],overlapOrder='upper sheets over middle roots; middle sheets over lower roots; free ends proud of following courses'))
  # A narrow root ribbon only: no enclosed shell. It remains beneath this
  # individual root and terminates before the visible central/free-end face.
  ribvs=[];ribuv=[]
  for j in range(2):
   for i in range(13):
    u=i/12;p=bezier(rails['coveredRoot'],u)+Vector((.007,.003*j,-.010*j));ribvs.append(tuple(p));ribuv.append((u,float(j)))
  rib=mesh(label+' root rib',ribvs,[(i,i+1,i+14,i+13) for i in range(12)],['black-iron'],ribuv);rs=rib.modifiers.new('narrow support thickness','SOLIDIFY');rs.thickness=.003;rib['supportWidth']=.0105;rib['supportScope']='covered root only'
 bpy.context.view_layer.update()
 return dict(module='cg-supervised-body09',era=era,newMeshes=len(made),newSheets=8,narrowRootRibs=8,retainedHidden=HIDES,actualVisibleReceivingMaterialSources=sources,sourcePartitions=records,method='Eight unique 3D four-Bezier-rail Coons cages; narrow root ribbons; one side only',limits=['Every rail and depth control is inferred','Independent visual QC and owner artistic acceptance pending','Other body/front/neck hierarchy unresolved','No receiving material changes'])

def diagnostic():
 p=argparse.ArgumentParser();p.add_argument('--input-root',required=True);p.add_argument('--attempt',default='attempt01');p.add_argument('--resolution',type=int,default=800);p.add_argument('--samples',type=int,default=6);args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 root=Path(__file__).resolve().parents[1];inp=Path(args.input_root);out=root/'assets/audit/cg-supervised-body09'/args.attempt;out.mkdir(parents=True,exist_ok=True)
 source=inp/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend';ref=inp/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
 assert sha(source)==SOURCE_SHA;assert sha(ref)==REF_SHA
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
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
 render('before-whole-pbr');render('before-whole-clay',claypass=True);result=apply(s,inp,'builder');render('after-whole-pbr');render('after-whole-clay',claypass=True)
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
 changed=[n for n,d in frozen.items() if digest(s.objects[n])!=d];unexpected=[n for n,v in visibility.items() if s.objects[n].hide_render!=v and n not in result['retainedHidden']];assert not changed and not unexpected,(changed,unexpected)
 bpy.context.preferences.filepaths.save_version=0;native=out/'murderbird-body09.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native));nativehash=sha(native)
 bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;finite=[]
 for o in s.objects:
  if not o.get('cgSupervisedBody09'):continue
  assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
  assert all(math.isfinite(c) and -.00001<=c<=1.00001 for uv in o.data.uv_layers for v in uv.data for c in v.uv)
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());md=ev.to_mesh();assert all(math.isfinite(c) for v in md.vertices for c in v.co);finite.append({'name':o.name,'vertices':len(md.vertices),'evaluatedFinite':True,'normalizedUV':True});ev.to_mesh_clear()
 changedreadback=[n for n,d in frozen.items() if digest(bpy.context.scene.objects[n])!=d];assert not changedreadback
 result.update(finiteEvaluatedGeometryAndUV=finite,sourceSHA256=sha(source),sourceBinaryPreserved=sha(source)==SOURCE_SHA,referenceSHA256=sha(ref),nativeSHA256=nativehash,originalMeshesAndAnchorsChecked=len(frozen),receivingGeometryUVMaterialIndicesTransformsChanged=changed,savedNativePreservationReadback=changedreadback,unexpectedVisibilityChanges=unexpected,cameras=cameras,renderSettings={'engine':'CYCLES','samples':args.samples,'denoise':True,'viewTransform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure},images={f.name:sha(f) for f in out.glob('*.png')},status='Unaccepted CG proposal; likeness not established')
 result['criterion']=json.loads(Path('/tmp/cg-qc08-body.json').read_text())['next_experiment'];result['authoringScriptSHA256']=sha(Path(__file__));result['candidate03SHA256']=sha(inp/'assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png')
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('BODY09_COMPLETE',out)
if __name__=='__main__':diagnostic()
