"""BODY02 fitted common anterior skin and crisp short courses. Import-safe retained-input API."""
import argparse,hashlib,importlib.util,json,math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
MANIFEST='47ed3ee74f0a06a9c470a427f8151dd032b0b48e1c68083f50d092cd1ec3308f'
REF='645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114'
RETIRE=[f'CGRB01 rounded course {c}-{r}' for c in range(6) for r in range(6)]+['CGB12 longitudinal formed panel '+n for n in ('0-2','1-2','2-2','3-2','4-1','5-2')]
Z=[1.50,1.44,1.37,1.30,1.22,1.15,1.08,1.00,.90,.82,.78]
A=[-1.12,-.90,-.65,-.35,0,.35,.65,.90,1.12]
SECTIONS=[(1.56,-.236,.095,.108),(1.48,-.270,.123,.128),(1.40,-.305,.153,.156),(1.37,-.321,.176,.180),(1.28,-.397,.234,.272),(1.15,-.442,.286,.353),(1.02,-.403,.276,.333),(.89,-.304,.222,.249),(.80,-.195,.132,.167),(.78,-.175,.120,.150)]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(root,name):
 p=Path(root)/'scripts'/name;q=importlib.util.spec_from_file_location(name.replace('-','_'),p);m=importlib.util.module_from_spec(q);q.loader.exec_module(m);return m

def apply(scene,root_path=None,era='builder',design=1):
 if any(o.get('cgRecursiveBody02') for o in scene.objects):raise RuntimeError('Reload retained02 before applying')
 originals=[scene.objects.get(n) for n in RETIRE];assert all(o and o.type=='MESH' and not o.hide_render for o in originals)
 mats=list(scene.objects['CGRB01 rounded course 2-2'].data.materials);assert len(mats)==2
 deps=bpy.context.evaluated_depsgraph_get();points=[];faces=[]
 for o in originals:
  ev=o.evaluated_get(deps);md=ev.to_mesh();offset=len(points);points.extend([o.matrix_world@v.co for v in md.vertices]);faces.extend([tuple(offset+i for i in p.vertices) for p in md.polygons]);ev.to_mesh_clear()
 tree=BVHTree.FromPolygons(points,faces)
 def prior(a,z):
  for i in range(len(SECTIONS)-1):
   z0,y0,x0,d0=SECTIONS[i];z1,y1,x1,d1=SECTIONS[i+1]
   if z>=z1:break
  t=max(0,min(1,(z0-z)/(z0-z1)));t=t*t*(3-2*t);y=y0*(1-t)+y1*t;rx=x0*(1-t)+x1*t;depth=d0*(1-t)+d1*t
  return Vector((rx*math.sin(a),y+depth*(1-math.cos(a)),z))
 # Fitted sparse common cage: actual retained sheet hits, fallback only at holes.
 controls=[];fits=[]
 for z in Z:
  for a in A:
   p=prior(a,z);hit,n,idx,d=tree.ray_cast(Vector((p.x,-2,z)),Vector((0,1,0)),3)
   used=hit is not None and abs(hit.y-p.y)<.055
   if used:p.y=hit.y+.0020
   controls.append(tuple(p));fits.append(dict(z=z,a=a,actualRetainedSurfaceHit=used,point=list(p)))
 coll=bpy.data.collections.new('BODY02 fitted shared anterior skin and short metal courses');scene.collection.children.link(coll)
 for i,img in enumerate(bpy.data.images):
  if img.packed_file:coll['receivingPackedImage%03d'%i]=img
 def make(name,vs,fs,uvs,skin=False):
  d=bpy.data.meshes.new(name+' editable fitted cage');d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(name,d);coll.objects.link(o)
  for mat in mats:d.materials.append(mat)
  layer=d.uv_layers.new(name='body02-normalized-shared-domain' if skin else 'body02-normalized-local-sheet')
  for p in d.polygons:
   p.use_smooth=True
   for li in p.loop_indices:layer.data[li].uv=uvs[d.loops[li].vertex_index]
  bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
  if sum((f.normal for f in bm.faces),Vector()).y>0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  bm.to_mesh(d);bm.free()
  if skin:
   sub=o.modifiers.new('sparse continuous fitted skin SubD','SUBSURF');sub.levels=sub.render_levels=2
  sol=o.modifiers.new('thin inward sheet stock','SOLIDIFY');sol.thickness=.0012;sol.offset=-1;sol.material_offset=sol.material_offset_rim=1
  o['cgRecursiveBody02']=True;o['cg1cRegion']='body';o['surfaceRole']='breast-armor';o['exteriorEras']='maker,mechanic,builder';o['cgConstructionStatus']='Fitted continuous source-guided anterior skin/course proposal; owner acceptance pending';o['cgBody02Skin']=skin
  return o
 nu=len(A);skin=make('CGRB02 continuous fitted anterior metal skin',controls,[(j*nu+i,j*nu+i+1,(j+1)*nu+i+1,(j+1)*nu+i) for j in range(len(Z)-1) for i in range(nu-1)],[(i/(nu-1),j/(len(Z)-1)) for j in range(len(Z)) for i in range(nu)],True)
 bpy.context.view_layer.update();ev=skin.evaluated_get(bpy.context.evaluated_depsgraph_get());md=ev.to_mesh();md.calc_loop_triangles();tuv=[];world=[];pp=[];layer=md.uv_layers.active
 for t in md.loop_triangles:
  if md.polygons[t.polygon_index].material_index:continue
  uv=[Vector((*layer.data[i].uv,0)) for i in t.loops];tuv.append(uv);world.append([skin.matrix_world@md.vertices[i].co for i in t.vertices]);pp.extend(uv)
 uv_tree=BVHTree.FromPolygons(pp,[(3*i,3*i+1,3*i+2) for i in range(len(tuv))],all_triangles=True)
 def surface(u,v):
  hit,n,idx,d=uv_tree.find_nearest(Vector((max(.001,min(.999,u)),max(.001,min(.999,v)),0)));a,b,c=tuv[idx];p0,p1,p2=world[idx];ab=b-a;ac=c-a;aq=hit-a;den=ab.x*ac.y-ab.y*ac.x;w1=(aq.x*ac.y-aq.y*ac.x)/den;w2=(ab.x*aq.y-ab.y*aq.x)/den;return p0*(1-w1-w2)+p1*w1+p2*w2
 def normal(u,v):
  n=(surface(u+.0001,v)-surface(u-.0001,v)).cross(surface(u,v+.0001)-surface(u,v-.0001)).normalized();return -n if n.y>0 else n
 # Shared neighboring domains; center remains continuous beneath narrow seams.
 tracks=[(.015,.165),(.140,.295),(.265,.425),(.397,.566),(.536,.700),(.675,.840),(.815,.985)]
 ends=[[0,.11,.235,.355,.475,.59,.71,.815,.91,1],[0,.13,.26,.38,.495,.61,.725,.83,.925,1],[0,.10,.225,.35,.48,.60,.72,.825,.915,1],[0,.125,.25,.37,.49,.605,.72,.825,.92,1],[0,.105,.235,.365,.485,.60,.715,.82,.915,1],[0,.13,.265,.385,.50,.615,.725,.835,.925,1],[0,.11,.24,.365,.49,.61,.73,.84,.93,1]]
 records=[];new=[skin.name]
 for col,(left,right) in enumerate(tracks):
  for row,(begin,end) in enumerate(zip(ends[col],ends[col][1:])):
   begin=max(0,begin-.018 if row else begin);end=min(1,end+.008 if row<8 else end);vs=[];uv=[];nx,ny=9,13
   for j in range(ny):
    v=j/(ny-1)
    for i in range(nx):
     u=i/(nx-1);clip=.035*abs(2*v-1)**10;gu=left+(right-left)*(clip+(1-2*clip)*u)
     if design==2:
      # Deterministic course direction traced as a coherent neck-to-breast flow.
      # Shared boundary warp changes across region, never independent noise.
      course=(begin+end)/2;flow=.058*math.sin(math.pi*course)*math.sin(math.pi*gu)
      gu+=flow+.008*(2*u-1)*v;gu=max(.008,min(.992,gu))
     # Source-observed oblique flank turning; center domains stay shared.
     shear=.022*(col-3)/3*math.sin(math.pi*(begin+end)/2);gv=begin+(end-begin)*v+shear*(2*u-1)+.006*(2*u-1)*v**5*(1 if row%2 else -1)
     if design==2:
      # Blunt angled sheet hems and nonuniform source course partitions.
      hem=[.020,-.014,.024,-.018,.013,-.022,.016][col]
      gv+=hem*(2*u-1)*v**5+.009*math.sin(math.pi*u)*v**7
      gu+=.008*v**4*(1 if col<3 else -1)
     gv=max(.001,min(.999,gv));p=surface(gu,gv);n=normal(gu,gv);relief=.0005+.0017*v**4
     if design==2:relief=.0004+.0010*v**4
     p+=n*relief;vs.append(tuple(p));uv.append((u,v))
   fs=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)];o=make(f'CGRB02 fitted short metal course {col}-{row}',vs,fs,uv);new.append(o.name);records.append(dict(name=o.name,sharedDomain=[left,right,begin,end],directionShear=shear))
 ev.to_mesh_clear();hides={}
 for o in originals:hides[o.name]=dict(before=[o.hide_render,o.hide_viewport,o.hide_get()],after=[True,o.hide_viewport,True]);o.hide_render=True;o.hide_set(True)
 bpy.context.view_layer.update()
 return dict(module='cg-recursive-body02',era=era,design=design,newMeshes=new,hideOverrides=hides,fittedCageSamples=fits,actualFitHits=sum(x['actualRetainedSurfaceHit'] for x in fits),panels=records,materialSources=[m.name for m in mats],construction='Actual retained surface fit to common sparse skin; shared plate domains with continuous curved metal support; no flat dark patch',status='Unaccepted source-guided visual proposal; native source depths inferred')

def run():
 p=argparse.ArgumentParser();p.add_argument('--input-root',default=str(ROOT));p.add_argument('--era',default='builder');p.add_argument('--design',type=int,default=1);p.add_argument('--resolution',type=int,default=640);p.add_argument('--samples',type=int,default=4);p.add_argument('--phase',choices=['early','expand'],default='early');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=Path(args.input_root);own=Path(__file__).resolve().parents[1];mp=root/'assets/audit/cg-recursive-three-loop01/loop02-preparation/receiving-manifest-loop02.json';assert sha(mp)==MANIFEST;manifest=json.loads(mp.read_text());ip=manifest['natives'][args.era];inp=root/ip['path'];assert sha(inp)==ip['sha256'];assert sha(root/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg')==REF
 out=own/'assets/audit/cg-recursive-body02'/f'attempt{args.design:02d}'/args.era;asset=own/'assets/models/cg-recursive-body02'/f'attempt{args.design:02d}';out.mkdir(parents=True,exist_ok=True);asset.mkdir(parents=True,exist_ok=True);native=asset/f'murderbird-body02-{args.era}.blend';receipt_path=out/'receipt.json';audit=module(root,'cg-supervised-body12.py');pres=module(root,'cg-supervised-preservation.py');prior=json.loads((root/'assets/audit/cg-supervised01/attempt09'/args.era/'receipt.json').read_text())
 bpy.ops.wm.open_mainfile(filepath=str(inp if args.phase=='early' else native));s=bpy.context.scene
 if args.phase=='early':
  frozen={o.name:audit.digest(o) for o in s.objects if o.type in ('MESH','EMPTY')};graphs=audit.material_digest();packed=pres.packed_image_snapshot();vis={o.name:[o.hide_render,o.hide_viewport,o.hide_get()] for o in s.objects};rig={o.name:dict(location=list(o.location),rotation=list(o.rotation_euler),scale=list(o.scale),data=dict(type=o.data.type,ortho_scale=o.data.ortho_scale,lens=o.data.lens,shift_x=o.data.shift_x,shift_y=o.data.shift_y) if o.type=='CAMERA' else dict(energy=o.data.energy,color=list(o.data.color),size=o.data.size)) for o in s.objects if o.type in ('CAMERA','LIGHT')};b=s.world.node_tree.nodes.get('Background');world=[list(b.inputs[0].default_value),b.inputs[1].default_value];receipt=dict(inputSHA256=sha(inp),manifestSHA256=MANIFEST,referenceSHA256=REF,originalPayloadDigests=frozen,receivingMaterialGraphs=graphs,packedImageSnapshot=packed,originalVisibility=vis,originalRig=rig,originalWorld=world,images={},cameras={})
 else:receipt=json.loads(receipt_path.read_text())
 clay=bpy.data.materials.new('BODY02 diagnostic clay');clay.use_nodes=True;clay.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.23,.23,.23,1);clay.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.64
 def setcamera(key):
  q=prior['cameras'][key];c=s.camera;c.location=q['location'];c.rotation_euler=q['rotation_euler'];c.data.type=q['projection'];c.data.ortho_scale=q['ortho_scale'];c.data.lens=q['lens_mm'];c.data.shift_x,c.data.shift_y=q['shift'];b=s.world.node_tree.nodes.get('Background');b.inputs[0].default_value=q['world_color'];b.inputs[1].default_value=q['world_strength'];lights=[o for o in s.objects if o.type=='LIGHT' and o.name.startswith('Supervised area')][-3:]
  for o,l in zip(lights,q['areas']):o.location=l['location'];o.rotation_euler=l['rotation_euler'];o.data.energy=l['power'];o.data.color=l['color'];o.data.size=l['size']
  s.render.resolution_x=args.resolution;s.render.resolution_y=round(args.resolution*q['resolution'][1]/q['resolution'][0]);s.render.resolution_percentage=100;bpy.context.view_layer.update();return q
 def render(name,key,cp=False):
  q=setcamera(key);s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=args.samples;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.image_settings.file_format='PNG';s.view_layers[0].material_override=clay if cp else None;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);qq=dict(q);qq['resolution']=[s.render.resolution_x,s.render.resolution_y];qq['actualSamples']=args.samples;qq['clay']=cp;receipt['cameras'][name]=qq;receipt['images'][name+'.png']=sha(out/(name+'.png'));receipt_path.write_text(json.dumps(receipt,indent=2));print('BODY02_IMAGE',out/(name+'.png'),flush=True)
 if args.phase=='early':
  for k in ('canon-neutral','neutral-000'):
   for cp in (False,True):render('before-'+k+('-clay' if cp else '-pbr'),k,cp)
  receipt['application']=apply(s,root,args.era,args.design)
  for k in ('canon-neutral','neutral-000'):
   for cp in (False,True):render('candidate-'+k+('-clay' if cp else '-pbr'),k,cp)
  # Recheck actual former gap rays in same front projection.
  setcamera('neutral-000');q=prior['cameras']['neutral-000'];c=s.camera;rot=c.matrix_world.to_quaternion();f=rot@Vector((0,0,-1));rr=rot@Vector((1,0,0));up=rot@Vector((0,1,0));w,h=q['resolution'];rays=[]
  for xn in (.5,.51):
   origin=c.location+rr*((xn-.5)*c.data.ortho_scale)+up*((.5-.465)*c.data.ortho_scale*h/w);hit,loc,n,idx,obj,matrix=s.ray_cast(bpy.context.evaluated_depsgraph_get(),origin,f,distance=30);rays.append(dict(x=xn,y=.465,object=obj.name if hit else None,point=list(loc) if hit else None,anteriorSuccessorHit=bool(hit and obj.get('cgRecursiveBody02') and loc.y<-.25)))
  receipt['formerGapRays']=rays;assert all(x['anteriorSuccessorHit'] for x in rays)
  s.view_layers[0].material_override=None
  for n,q in receipt['originalRig'].items():
   o=s.objects[n];o.location=q['location'];o.rotation_euler=q['rotation'];o.scale=q['scale']
   for k,v in q['data'].items():setattr(o.data,k,v)
  b=s.world.node_tree.nodes.get('Background');b.inputs[0].default_value=receipt['originalWorld'][0];b.inputs[1].default_value=receipt['originalWorld'][1];pres.retain_packed_image_ids(s);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False);receipt['nativeSHA256']=sha(native);bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene
 else:
  for stage in ('before','candidate'):
   for o in s.objects:
    if o.get('cgRecursiveBody02'):o.hide_render=stage=='before'
    if o.name in receipt['application']['hideOverrides']:o.hide_render=stage=='candidate'
   for k in ('body-detail','side-profile','neutral-180','canon-workshop'):
    for cp in (False,True):render(stage+'-'+k+('-clay' if cp else '-pbr'),k,cp)
  for o in s.objects:
   if o.get('cgRecursiveBody02'):o.hide_render=False
   if o.name in receipt['application']['hideOverrides']:o.hide_render=True
  bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene
 changed=[n for n,d in receipt['originalPayloadDigests'].items() if not s.objects.get(n) or audit.digest(s.objects[n])!=d];gafter=audit.material_digest();gchanged=[n for n,d in receipt['receivingMaterialGraphs'].items() if gafter.get(n)!=d];vchanged=[n for n,v in receipt['originalVisibility'].items() if n not in RETIRE and [s.objects[n].hide_render,s.objects[n].hide_viewport,s.objects[n].hide_get()]!=v];assert not changed and not gchanged and not vchanged,(changed,gchanged,vchanged);assert pres.packed_image_snapshot()==receipt['packedImageSnapshot'];assert all(s.objects[n].hide_render and s.objects[n].hide_get() and s.objects[n].hide_viewport==receipt['originalVisibility'][n][1] for n in RETIRE);assert sha(inp)==ip['sha256'];assert sha(native)==receipt['nativeSHA256'];receipt['readback']=dict(originalPayloadCount=len(receipt['originalPayloadDigests']),payloadChanged=changed,graphsChanged=gchanged,packedImagesExact=True,visibilityOutside42Changed=vchanged,all42RetiredRenderAndHideSet=True,globalViewportFlagsPreserved=True,originalRigRestored=True,inputBinaryPreserved=True);receipt_path.write_text(json.dumps(receipt,indent=2)+'\n');print('BODY02_COMPLETE',args.phase,args.era,out,flush=True)
if __name__=='__main__':run()
