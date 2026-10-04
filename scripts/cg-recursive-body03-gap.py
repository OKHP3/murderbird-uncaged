"""BODY03 additive local metal returns. Importing is inert; original payloads untouched."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,bmesh
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
MANIFEST='47ed3ee74f0a06a9c470a427f8151dd032b0b48e1c68083f50d092cd1ec3308f'
REF='645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114'
DEFAULT_DESIGN=1
RETIRE=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(root,name):
 p=Path(root)/'scripts'/name;q=importlib.util.spec_from_file_location(name.replace('-','_'),p);m=importlib.util.module_from_spec(q);q.loader.exec_module(m);return m
BOUNDS=[{'name': 'CGRB03 center interlocking underlap return', 'vertices': [[-0.002, -0.422, 1.179], [0.023, -0.421, 1.174], [0.073, -0.403, 1.085], [0.058, -0.4, 1.079], [-0.038, -0.406, 1.083], [-0.045, -0.41, 1.094]]}, {'name': 'CGRB03 near throat narrow stepped underlap 0', 'vertices': [[-0.15105043351650238, -0.21441947734355926, 1.3677915172576904], [-0.14750783145427704, -0.22851830041408538, 1.3699742393493652], [-0.12406253069639206, -0.24219895219802856, 1.3946691589355469], [-0.11136061698198318, -0.2685319266319275, 1.3581034784317016], [-0.1322658360004425, -0.24509310042858123, 1.3580827360153198], [-0.14877328276634216, -0.21804424440860748, 1.3580600862503052]]}, {'name': 'CGRB03 near throat narrow stepped underlap 1', 'vertices': [[-0.12601980566978455, -0.25417734003067016, 1.3752853708267212], [-0.10988856852054596, -0.28954655742645263, 1.35066996383667], [-0.07835187762975693, -0.3106233558654785, 1.3481713371276856], [-0.05571708083152771, -0.30299169635772705, 1.3581330423355102], [-0.08537762612104416, -0.28845293140411377, 1.3581201677322388], [-0.11179067194461823, -0.26812899923324585, 1.358102882385254]]}]

def apply(scene,root_path=None,era='builder'):
 if any(o.get('cgRecursiveBody03Gap') for o in scene.objects):raise RuntimeError('Reload retained02 before applying')
 mats=list(scene.objects['CGRB01 rounded course 2-2'].data.materials);assert len(mats)==2
 coll=bpy.data.collections.new('BODY03 three localized interlocking metal underlaps');scene.collection.children.link(coll)
 # Retain original packed IDs through native save, without editing their bytes or graphs.
 for i,img in enumerate(bpy.data.images):
  if img.packed_file:coll['receivingPackedImage%03d'%i]=img
 new=[]
 for spec in BOUNDS:
  edge=[Vector(v) for v in spec['vertices']];center=sum(edge,Vector())/len(edge)
  # Center return has a very shallow convex bend; narrow throat returns follow the edge fit.
  if 'center' in spec['name']:center.y-=.0015
  vs=[tuple(v) for v in edge]+[tuple(center)];fs=[(i,(i+1)%len(edge),len(edge)) for i in range(len(edge))]
  d=bpy.data.meshes.new(spec['name']+' editable local sheet');d.from_pydata(vs,[],fs);d.update()
  bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
  if sum((f.normal for f in bm.faces),Vector()).y>0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  bm.to_mesh(d);bm.free();o=bpy.data.objects.new(spec['name'],d);coll.objects.link(o)
  for mat in mats:d.materials.append(mat)
  uv=d.uv_layers.new(name='body03-local-return-normalized');xmin=min(v[0] for v in vs);xmax=max(v[0] for v in vs);zmin=min(v[2] for v in vs);zmax=max(v[2] for v in vs)
  for poly in d.polygons:
   poly.use_smooth=True
   for li in poly.loop_indices:
    v=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=((v.x-xmin)/max(.000001,xmax-xmin),(v.z-zmin)/max(.000001,zmax-zmin))
  sol=o.modifiers.new('thin inward metal return','SOLIDIFY');sol.thickness=.0012;sol.offset=-1;sol.material_offset=sol.material_offset_rim=1
  o['cgRecursiveBody03Gap']=True;o['cg1cRegion']='body';o['surfaceRole']='breast-armor';o['exteriorEras']='maker,mechanic,builder';o['constructionStatus']='Localized source-guided gap return; inferred depth; artistic acceptance pending';new.append(o.name)
 bpy.context.view_layer.update()
 return dict(module='cg-recursive-body03-gap',era=era,design=1,newMeshes=new,hideOverrides={},materialSources=[m.name for m in mats],boundaryWorldCoordinates=BOUNDS,status='Three additive local returns; no original retirement or visibility changes; actual pixel gate pending')

def run():
 p=argparse.ArgumentParser();p.add_argument('--input-root',default=str(ROOT));p.add_argument('--era',default='builder');p.add_argument('--design',type=int,default=DEFAULT_DESIGN);p.add_argument('--resolution',type=int,default=640);p.add_argument('--samples',type=int,default=4);p.add_argument('--phase',choices=['early','expand'],default='early');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=Path(args.input_root);own=Path(__file__).resolve().parents[1];mp=root/'assets/audit/cg-recursive-three-loop01/loop02-preparation/receiving-manifest-loop02.json';assert sha(mp)==MANIFEST;manifest=json.loads(mp.read_text());ip=manifest['natives'][args.era];inp=root/ip['path'];assert sha(inp)==ip['sha256'];assert sha(root/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg')==REF
 out=own/'assets/audit/cg-recursive-body03-gap'/f'attempt{args.design:02d}'/args.era;asset=own/'assets/models/cg-recursive-body03-gap'/f'attempt{args.design:02d}';out.mkdir(parents=True,exist_ok=True);asset.mkdir(parents=True,exist_ok=True);native=asset/f'murderbird-body03-gap-{args.era}.blend';receipt_path=out/'receipt.json'
 if args.phase=='early' and native.exists():raise RuntimeError('Frozen attempt native already exists; do not overwrite a reviewed checkpoint')
 audit=module(root,'cg-supervised-body12.py');pres=module(root,'cg-supervised-preservation.py');prior=json.loads((root/'assets/audit/cg-supervised01/attempt09'/args.era/'receipt.json').read_text())
 bpy.ops.wm.open_mainfile(filepath=str(inp if args.phase=='early' else native));s=bpy.context.scene
 if args.phase=='early':
  frozen={o.name:audit.digest(o) for o in s.objects if o.type in ('MESH','EMPTY')};graphs=audit.material_digest();packed=pres.packed_image_snapshot();vis={o.name:[o.hide_render,o.hide_viewport,o.hide_get()] for o in s.objects};rig={o.name:dict(location=list(o.location),rotation=list(o.rotation_euler),scale=list(o.scale),data=dict(type=o.data.type,ortho_scale=o.data.ortho_scale,lens=o.data.lens,shift_x=o.data.shift_x,shift_y=o.data.shift_y) if o.type=='CAMERA' else dict(energy=o.data.energy,color=list(o.data.color),size=o.data.size)) for o in s.objects if o.type in ('CAMERA','LIGHT')};b=s.world.node_tree.nodes.get('Background');world=[list(b.inputs[0].default_value),b.inputs[1].default_value];receipt=dict(inputSHA256=sha(inp),manifestSHA256=MANIFEST,referenceSHA256=REF,originalPayloadDigests=frozen,receivingMaterialGraphs=graphs,packedImageSnapshot=packed,originalVisibility=vis,originalRig=rig,originalWorld=world,images={},cameras={})
 else:receipt=json.loads(receipt_path.read_text())
 clay=bpy.data.materials.new('BODY03 diagnostic clay');clay.use_nodes=True;clay.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.23,.23,.23,1);clay.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.64
 def setcamera(key):
  q=prior['cameras'][key];c=s.camera;c.location=q['location'];c.rotation_euler=q['rotation_euler'];c.data.type=q['projection'];c.data.ortho_scale=q['ortho_scale'];c.data.lens=q['lens_mm'];c.data.shift_x,c.data.shift_y=q['shift'];b=s.world.node_tree.nodes.get('Background');b.inputs[0].default_value=q['world_color'];b.inputs[1].default_value=q['world_strength'];lights=[o for o in s.objects if o.type=='LIGHT' and o.name.startswith('Supervised area')][-3:]
  for o,l in zip(lights,q['areas']):o.location=l['location'];o.rotation_euler=l['rotation_euler'];o.data.energy=l['power'];o.data.color=l['color'];o.data.size=l['size']
  s.render.resolution_x=args.resolution;s.render.resolution_y=round(args.resolution*q['resolution'][1]/q['resolution'][0]);s.render.resolution_percentage=100;bpy.context.view_layer.update();return q
 def render(name,key,cp=False):
  q=setcamera(key);s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=args.samples;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.image_settings.file_format='PNG';s.view_layers[0].material_override=clay if cp else None;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);qq=dict(q);qq['resolution']=[s.render.resolution_x,s.render.resolution_y];qq['actualSamples']=args.samples;qq['clay']=cp;receipt['cameras'][name]=qq;receipt['images'][name+'.png']=sha(out/(name+'.png'));receipt_path.write_text(json.dumps(receipt,indent=2));print('BODY03_IMAGE',out/(name+'.png'),flush=True)
 if args.phase=='early':
  for k in ('canon-neutral','neutral-000'):
   for cp in (False,True):render('before-'+k+('-clay' if cp else '-pbr'),k,cp)
  receipt['application']=apply(s,root,args.era)
  for k in ('canon-neutral','neutral-000'):
   for cp in (False,True):render('candidate-'+k+('-clay' if cp else '-pbr'),k,cp)
  # Recheck actual former gap rays in same front projection.
  setcamera('neutral-000');q=prior['cameras']['neutral-000'];c=s.camera;rot=c.matrix_world.to_quaternion();f=rot@Vector((0,0,-1));rr=rot@Vector((1,0,0));up=rot@Vector((0,1,0));w,h=q['resolution'];rays=[]
  for xn in (.5,.51):
   origin=c.location+rr*((xn-.5)*c.data.ortho_scale)+up*((.5-.465)*c.data.ortho_scale*h/w);hit,loc,n,idx,obj,matrix=s.ray_cast(bpy.context.evaluated_depsgraph_get(),origin,f,distance=30);rays.append(dict(x=xn,y=.465,object=obj.name if hit else None,point=list(loc) if hit else None,anteriorSuccessorHit=bool(hit and obj.get('cgRecursiveBody03Gap') and loc.y<-.25)))
  receipt['formerGapRays']=rays;assert all(x['anteriorSuccessorHit'] for x in rays)
  s.view_layers[0].material_override=None
  bpy.data.materials.remove(clay)
  for n,q in receipt['originalRig'].items():
   o=s.objects[n];o.location=q['location'];o.rotation_euler=q['rotation'];o.scale=q['scale']
   for k,v in q['data'].items():setattr(o.data,k,v)
  b=s.world.node_tree.nodes.get('Background');b.inputs[0].default_value=receipt['originalWorld'][0];b.inputs[1].default_value=receipt['originalWorld'][1];pres.retain_packed_image_ids(s);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False);receipt['nativeSHA256']=sha(native);bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene
 else:
  for stage in ('before','candidate'):
   for o in s.objects:
    if o.get('cgRecursiveBody03Gap'):o.hide_render=stage=='before'
    if o.name in receipt['application']['hideOverrides']:o.hide_render=stage=='candidate'
   for k in ('body-detail','side-profile','neutral-180'):
    for cp in (False,True):render(stage+'-'+k+('-clay' if cp else '-pbr'),k,cp)
  for o in s.objects:
   if o.get('cgRecursiveBody03Gap'):o.hide_render=False
   if o.name in receipt['application']['hideOverrides']:o.hide_render=True
  bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene
 changed=[n for n,d in receipt['originalPayloadDigests'].items() if not s.objects.get(n) or audit.digest(s.objects[n])!=d];gafter=audit.material_digest();gchanged=[n for n,d in receipt['receivingMaterialGraphs'].items() if gafter.get(n)!=d];vchanged=[n for n,v in receipt['originalVisibility'].items() if n not in RETIRE and [s.objects[n].hide_render,s.objects[n].hide_viewport,s.objects[n].hide_get()]!=v];assert not changed and not gchanged and not vchanged,(changed,gchanged,vchanged);assert pres.packed_image_snapshot()==receipt['packedImageSnapshot'];assert all(s.objects[n].hide_render and s.objects[n].hide_get() and s.objects[n].hide_viewport==receipt['originalVisibility'][n][1] for n in RETIRE);assert sha(inp)==ip['sha256'];assert sha(native)==receipt['nativeSHA256'];receipt['readback']=dict(originalPayloadCount=len(receipt['originalPayloadDigests']),payloadChanged=changed,graphsChanged=gchanged,packedImagesExact=True,originalVisibilityChanged=vchanged,zeroRetirements=True,globalViewportFlagsPreserved=True,originalRigRestored=True,inputBinaryPreserved=True);receipt_path.write_text(json.dumps(receipt,indent=2)+'\n');print('BODY03_COMPLETE',args.phase,args.era,out,flush=True)
if __name__=='__main__':run()
