"""FEET14 bounded formed-cover proposal; completed06 payload and stance retained.
apply(scene, root_path=None, era='builder') defaults to six forward toes; pilot
is explicitly requested through scene['cgFeet14Pilot']. Unseen returns inferred.
"""
import argparse,hashlib,importlib.util,json,math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
TAG='cgSupervisedFeet14'
INPUT_SHA='72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4'
REF_SHA='645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114'

def load(root,name):
 spec=importlib.util.spec_from_file_location(name,root/'scripts'/name);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def center(o):return sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
def points(o):return [o.matrix_world@v.co for v in o.data.vertices]
def whitelist(pilot=False):
 out=[]
 for side in ('left',) if pilot else ('left','right'):
  for digit in (2,) if pilot else (1,2,3):
   label=side+' forward toe '+str(digit)
   out += ['CGF03 '+label+' interlocking toe shell '+str(i) for i in range(5)]
   out += ['CGF03 '+label+' warm seam band '+str(i) for i in range(5)]
   out += ['CGF03 '+label+' talon-root cuff']
  out += ['CG1c '+side+' tarsus collar '+str(i) for i in (3,4,5)]+['CG2b '+side+' armored ankle ferrule']
 return out

def apply(scene,root_path=None,era='builder'):
 if any(o.get(TAG) for o in scene.objects):raise RuntimeError('Reload receiving06 before FEET14')
 pilot=bool(scene.get('cgFeet14Pilot',False));originals=list(scene.objects);hidden=whitelist(pilot);made=[];records=[]
 assert all(n in scene.objects for n in hidden)
 coll=bpy.data.collections.new('CG FEET14 formed forward covers');scene.collection.children.link(coll)
 def mesh(name,vs,fs,uv,source,black=False):
  d=bpy.data.meshes.new('CGF14 '+name);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(d.name,d);coll.objects.link(o)
  material=source.data.materials[0]
  if black:
   material=scene.objects['CGF03 left forward toe 2 recessed tendon body'].data.materials[0]
  d.materials.append(material);layer=d.uv_layers.new(name='feet14-normalized-across-down')
  for p in d.polygons:
   p.use_smooth=False
   for li in p.loop_indices:layer.data[li].uv=uv[d.loops[li].vertex_index]
  bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(d);bm.free()
  family='black-iron' if black else json.loads(source.get('cgSurfaceFamilies','["feet-armor"]'))[0]
  for k,v in {TAG:True,'cg1cRegion':'foot','cg2bRegion':'foot','surfaceRole':family,'cgSurfaceFamilies':json.dumps([family]),'exteriorEras':'maker,mechanic,builder','era':era,'sourceImageSHA256':REF_SHA,'cgConstructionStatus':'Source-inferred formed covers; owner acceptance pending','cgFoot14Receiver':source.name}.items():o[k]=v
  made.append(o);return o
 def plate(name,rows,source,black=False,stock=.0013):
  # Open formed dorsal crown with sharp side returns; finite inward stock only.
  vs=[];uv=[];fs=[];n=len(rows[0])
  for j,row in enumerate(rows):
   for k,p in enumerate(row):vs.append(tuple(p));uv.append((k/(n-1),j/(len(rows)-1)))
  top=len(vs)
  vs += [tuple(Vector(p)-Vector((0,0,stock))) for p in vs];uv += list(uv)
  for j in range(len(rows)-1):
   for k in range(n-1):
    q=(j*n+k,j*n+k+1,(j+1)*n+k+1,(j+1)*n+k);fs += [q,tuple(i+top for i in reversed(q))]
  border=list(range(n))+[j*n+n-1 for j in range(1,len(rows))]+list(reversed(range((len(rows)-1)*n,(len(rows)-1)*n+n-1)))+[j*n for j in range(len(rows)-2,0,-1)]
  fs += [(a,b,b+top,a+top) for a,b in zip(border,border[1:]+border[:1])]
  return mesh(name,vs,fs,uv,source,black)
 for side in ('left',) if pilot else ('left','right'):
  for digit in (2,) if pilot else (1,2,3):
   label=side+' forward toe '+str(digit)
   old=[scene.objects['CGF03 '+label+' interlocking toe shell '+str(i)] for i in range(5)]
   direction=(center(old[-1])-center(old[0]));direction.z=0;direction.normalize();across=Vector((-direction.y,direction.x,0))
   for i,src in enumerate(old):
    ps=points(src);c=center(src);along=[(p-c).dot(direction) for p in ps];wide=max(abs((p-c).dot(across)) for p in ps);low=min(p.z for p in ps);high=max(p.z for p in ps);mid=(low+high)*.5
    # Section inherited from receiver, with a broad flattened crown and deep,
    # planar side return. No ballooned rounded sleeve and no added thickness.
    span=max(along)-min(along)
    # Cover ends approach the next inherited cover, leaving a narrow recessed
    # separation instead of the previous broad missing-cover slots.
    def neighbor_gap(other,forward):
     ops=points(other)
     return (min((p-c).dot(direction) for p in ops)-max(along)) if forward else (min(along)-max((p-c).dot(direction) for p in ops))
    prior_gap=max(0,neighbor_gap(old[i-1],False)) if i else 0
    next_gap=max(0,neighbor_gap(old[i+1],True)) if i<4 else 0
    lo=min(along)-prior_gap*.25;hi=max(along)+next_gap*.42
    profile=[(-1,.08),(-.95,.47),(-.72,.90),(-.32,1),(.32,1),(.72,.90),(.95,.47),(1,.08)]
    def row(t,drop=0):
     pos=c+direction*t
     nearest=sorted(ps,key=lambda p:abs((p-c).dot(direction)-t))[:24]
     # The receiving section supplies longitudinal taper; broad crown changes
     # the cross-section only, with every top inside its prior local envelope.
     local_w=max(abs((p-c).dot(across)) for p in nearest)
     local_hi=max(p.z for p in nearest)
     return [Vector((pos.x,pos.y,mid))+across*(local_w*x)+Vector((0,0,(local_hi-mid)*z-drop)) for x,z in profile]
    rows=[row(lo),row(lo+span*.10),row(hi-span*.08),row(hi)]
    plate(label+' dorsal formed cover '+str(i),rows,src)
    # Folded, down-stepped distal rim exposes thickness above recessed dark joint.
    plate(label+' folded distal rim '+str(i),[row(hi-span*.025),row(hi+next_gap*.24,.0009)],src,stock=.0010)
    plate(label+' recessed joint '+str(i),[row(hi+next_gap*.24,.0018),row(hi+next_gap*.40,.0018)],src,black=True,stock=.0008)
    records.append({'receiver':src.name,'center':list(c),'direction':list(direction),'half_width':wide,'inherited_z':[low,high],'longitudinal_bounds':[lo,hi],'inherited_neighbor_gaps':[prior_gap,next_gap],'joint_fill_fractions':[.25,.42,.24,.40],'construction':'broad faceted crown, planar returns, down-stepped free rim, recessed dark joint'})
   src=scene.objects['CGF03 '+label+' talon-root cuff'];ps=points(src);c=center(src);w=max(abs((p-c).dot(across)) for p in ps);h=max(p.z for p in ps);mid=min(p.z for p in ps)+(h-min(p.z for p in ps))*.46;als=[(p-c).dot(direction) for p in ps]
   rows=[]
   for t,drop in ((min(als),0),(max(als)*.85,.002)):
    p=c+direction*t;rows.append([Vector((p.x,p.y,mid))+across*(w*x)+Vector((0,0,(h-mid)*z-drop)) for x,z in profile])
   plate(label+' formed talon seat',rows,src)
  # A stepped distal cuff follows the actual three old collar centers and axis.
  collars=[scene.objects['CG1c '+side+' tarsus collar '+str(i)] for i in (3,4,5)];axis=(center(collars[0])-center(collars[-1])).normalized();u=Vector((1,0,0));u=(u-axis*u.dot(axis)).normalized();v=axis.cross(u).normalized()
  for i,src in enumerate(collars):
   c=center(src);ps=points(src);r=max(math.hypot((p-c).dot(u),(p-c).dot(v)) for p in ps);depth=max(abs((p-c).dot(axis)) for p in ps)
   vs=[];uv=[];fs=[];N=24;prof=[(-depth,r*.90),(-depth*.55,r),(depth*.55,r),(depth,r*.92),(depth,r*.72),(-depth,r*.72)]
   for j,(t,rr) in enumerate(prof):
    for k in range(N):
     a=k*math.tau/N;vs.append(tuple(c+axis*t+rr*(u*math.cos(a)+v*math.sin(a))));uv.append((k/N,j/(len(prof)-1)))
   for j in range(len(prof)):
    for k in range(N):fs.append((j*N+k,j*N+(k+1)%N,((j+1)%len(prof))*N+(k+1)%N,((j+1)%len(prof))*N+k))
   mesh(side+' stepped distal cuff '+str(i),vs,fs,uv,src)
  src=scene.objects['CG2b '+side+' armored ankle ferrule'];ps=points(src);c=center(src);lo=min(p.z for p in ps);hi=max(p.z for p in ps);width=(max(p.x for p in ps)-min(p.x for p in ps))*.5;front=min(p.y for p in ps);rear=max(p.y for p in ps)
  # Ferrule becomes a formed saddle bridging ankle into retained instep covers;
  # the side hubs remain exposed. Receiver bounds supply every endpoint.
  rows=[]
  for y,z,w in ((rear,hi,width*.76),((rear+front)*.5,hi,width*.90),(front,hi-.004,width*.92)):
   rows.append([Vector((c.x+w*x,y,z-(hi-lo)*(.55*(abs(x)**3)))) for x in (-1,-.75,-.32,.32,.75,1)])
  plate(side+' distal ankle bridge saddle',rows,src)
 for n in hidden:scene.objects[n].hide_render=True
 bpy.context.view_layer.update()
 return {'module':'cg-supervised-feet14','pilot':pilot,'era':era,'newMeshes':[o.name for o in made],'hiddenOriginals':hidden,'sectionReceipts':records,'method':'Formed sections derived from each receiving shell world vertices; stock inward; no anchor changes','limits':['Unseen returns inferred','Rear toes/talons/tendon and all leg machinery unchanged','Static CG proposal; no engineering or owner acceptance']}

def diagnostic():
 p=argparse.ArgumentParser();p.add_argument('--input-root',required=True);p.add_argument('--pilot',action='store_true');p.add_argument('--attempt',default='pilot02');p.add_argument('--resolution',type=int,default=640);p.add_argument('--samples',type=int,default=3);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=Path(__file__).resolve().parents[1];inp=Path(a.input_root);out=root/'assets/audit/cg-supervised-feet14'/(a.attempt if a.pilot else 'replicated02');out.mkdir(parents=True,exist_ok=True)
 sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();source=inp/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend';assert sha(source)==INPUT_SHA
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;checks=load(root,'cg-supervised-body12.py');pres=load(root,'cg-supervised-preservation.py');originals={o.name:checks.digest(o) for o in s.objects if o.type in ('MESH','EMPTY')};vis={o.name:[o.hide_render,o.hide_viewport,o.hide_get()] for o in s.objects};graphs=checks.material_digest();images=pres.packed_image_snapshot();pres.retain_packed_image_ids(s)
 canon=json.loads((inp/'assets/audit/cg-supervised-camera04/receipt.json').read_text())['hypotheses']['ortho-35']['camera'];cam=s.camera;camera_state=(cam.location.copy(),cam.rotation_euler.copy(),cam.data.type,cam.data.ortho_scale,cam.data.shift_x,cam.data.shift_y);s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';cameras={}
 clay=bpy.data.materials.new('Feet14 diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.32,.32,.32,1);bs.inputs['Roughness'].default_value=.63
 def render(name,view,cl=False):
  s.view_layers[0].material_override=clay if cl else None
  if view=='whole':cam.location=canon['location'];cam.rotation_euler=canon['rotation_euler'];cam.data.type=canon['projection'];cam.data.ortho_scale=canon['ortho_scale'];cam.data.shift_x,cam.data.shift_y=canon['shift']
  else:
   pos={'feet':(-2.8,-3.6,1.02),'front':(0,-6,.9),'side':(-6,0,.65),'oblique':(-3,-4,.78)}[view];cam.location=pos;cam.rotation_euler=(Vector((0,-.03,.14))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.92;cam.data.shift_x=cam.data.shift_y=0
  s.render.resolution_x=a.resolution;s.render.resolution_y=round(a.resolution*853/1280) if view=='whole' else a.resolution;s.render.filepath=str(out/(name+'.png'));cameras[name]={'location':list(cam.location),'rotation':list(cam.rotation_euler),'scale':cam.data.ortho_scale,'shift':[cam.data.shift_x,cam.data.shift_y],'resolution':[s.render.resolution_x,s.render.resolution_y],'clay':cl};bpy.ops.render.render(write_still=True)
 # First actual pair immediately, then early save/reopen before supplementary views.
 render('before-whole35-pbr','whole');render('before-feet-pbr','feet');s['cgFeet14Pilot']=a.pilot;result=apply(s,inp);del s['cgFeet14Pilot'];render('after-whole35-pbr','whole');render('after-feet-pbr','feet')
 s.view_layers[0].material_override=None;bpy.data.materials.remove(clay);cam.location,cam.rotation_euler,cam.data.type,cam.data.ortho_scale,cam.data.shift_x,cam.data.shift_y=camera_state
 changed=[n for n,d in originals.items() if checks.digest(s.objects[n])!=d];assert not changed,changed
 assert checks.material_digest()==graphs;pres.verify_receiving_images(images)
 flags=[n for n,v in vis.items() if [s.objects[n].hide_render,s.objects[n].hide_viewport,s.objects[n].hide_get()]!=([True,v[1],v[2]] if n in result['hiddenOriginals'] else v)];assert not flags,flags
 graph=bpy.context.evaluated_depsgraph_get();bad=[]
 for o in s.objects:
  if not o.get(TAG):continue
  ev=o.evaluated_get(graph);m=ev.to_mesh()
  if any(not math.isfinite(q) for v in m.vertices for q in v.co) or any(not math.isfinite(q) or q<0 or q>1 for uv in m.uv_layers for d in uv.data for q in d.uv):bad.append(o.name)
  ev.to_mesh_clear()
 assert not bad,bad
 bpy.context.preferences.filepaths.save_version=0;native=out/'murderbird-feet14.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;cam=s.camera;assert all(checks.digest(s.objects[n])==d for n,d in originals.items());assert checks.material_digest()==graphs;pres.verify_receiving_images(images)
 receipt={'application':result,'nativeInputSHA256':sha(source),'sourcePreserved':sha(source)==INPUT_SHA,'nativeOutputSHA256':sha(native),'originalPayloadCount':len(originals),'originalPayloadDigests':originals,'materialGraphsPreserved':True,'packedImageReadback':pres.verify_receiving_images(images),'visibilityFailures':flags,'evaluatedFiniteNormalizedUVFailures':bad,'cameras':cameras,'images':{f.name:sha(f) for f in out.glob('*.png')},'ownerAcceptance':'pending','sourceArtifacts':[{**x,'current_sha256':sha(inp/x['path'])} for x in json.loads((inp/'assets/audit/cg-supervised01/feet-macro-diagnosis.json').read_text())['source_artifacts']],'scriptSHA256':sha(Path(__file__))}
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('FEET14_FIRST_PAIR_COMPLETE',out,flush=True)
 clay=bpy.data.materials.new('Feet14 diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.32,.32,.32,1);bs.inputs['Roughness'].default_value=.63
 for label,view,cl in [('after-feet-clay','feet',True),('after-front-clay','front',True),('after-side-clay','side',True),('after-oblique-pbr','oblique',False)]:render(label,view,cl)
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;cam=s.camera
 for label,view,cl in [('before-feet-clay','feet',True),('before-front-clay','front',True),('before-side-clay','side',True)]:
  if cl and 'Feet14 diagnostic clay' not in bpy.data.materials:
   clay=bpy.data.materials.new('Feet14 diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.32,.32,.32,1);bs.inputs['Roughness'].default_value=.63
  render(label,view,cl)
 receipt['cameras']=cameras;receipt['images']={f.name:sha(f) for f in out.glob('*.png')};(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('FEET14_COMPLETE',out,flush=True)
if __name__=='__main__':diagnostic()
