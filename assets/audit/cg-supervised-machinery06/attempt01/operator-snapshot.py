"""Connected machinery CG inference on completed05. No armor/head/pose changes.
apply(scene, root_path=None, era='builder'); root owns final material rerouting.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector

INPUT_SHA='1c449c25ea48c22cc5e3a1781c26a49ee3268b9170298da2df4c923ed6171cc6'
REF_SHA='645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114'
TAG='cgSupervisedMachinery06'
def center(o):
 return sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
def apply(scene,root_path=None,era='builder'):
 if any(o.get(TAG) for o in scene.objects):raise RuntimeError('Reload completed05 before machinery06')
 originals=list(scene.objects);mats={};made=[];mounts=[];clusters={}
 for o in originals:
  if o.type!='MESH':continue
  try:fs=json.loads(o.get('cgSurfaceFamilies','[]'))
  except (ValueError,TypeError):fs=[]
  for i,f in enumerate(fs):
   if i<len(o.data.materials) and o.data.materials[i]:mats.setdefault(f,o.data.materials[i])
 # completed05 has no explicit forged-steel slot; bind inherited black iron
 # temporarily while keeping ordered family tag for root's finish rerouting.
 mats.setdefault('forged-steel',mats.get('black-iron'))
 for f in ('black-iron','worn-bronze','machined-steel','forged-steel'):
  if f not in mats:raise RuntimeError('Missing inherited family '+f)
 def mesh(name,vs,faces,uv,family,cluster,region,joins):
  if cluster not in clusters:
   c=bpy.data.collections.new('CGM06 '+cluster);scene.collection.children.link(c);clusters[cluster]=c
  d=bpy.data.meshes.new('CGM06 '+name);d.from_pydata(vs,[],faces);d.update();o=bpy.data.objects.new(d.name,d);clusters[cluster].objects.link(o)
  d.materials.append(mats[family]);layer=d.uv_layers.new(name='machinery06-local-uv')
  for p in d.polygons:
   p.use_smooth=True
   for li in p.loop_indices:layer.data[li].uv=uv[d.loops[li].vertex_index]
  bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(d);bm.free()
  for k,v in {TAG:True,'cg1cRegion':region,'cg2bRegion':region,'surfaceRole':family,'cgSurfaceFamilies':json.dumps([family]),'exteriorEras':'maker,mechanic,builder','cgAssemblyCluster':cluster,'cgConstructionStatus':'Source-directed CG inference; not engineering; owner acceptance pending','cgInferredMounts':json.dumps(joins)}.items():o[k]=v
  made.append(o);mounts.append({'mesh':o.name,'joins':joins,'tier':'INFERRED'});return o
 def sweep(name,pts,radii,family,cluster,region,joins,ratio=1,n=24):
  pts=[Vector(p) for p in pts];vs=[];uv=[];fs=[]
  for j,p in enumerate(pts):
   t=(pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)]).normalized();u=t.cross(Vector((1,0,0)))
   if u.length<.01:u=t.cross(Vector((0,1,0)))
   u.normalize();v=t.cross(u).normalized()
   for k in range(n):
    a=math.tau*k/n;vs.append(tuple(p+radii[j]*(u*math.cos(a)+v*math.sin(a)*ratio)));uv.append((k/n,j/(len(pts)-1)))
  for j in range(len(pts)-1):
   for k in range(n):fs.append((j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k))
  fs += [tuple(reversed(range(n))),tuple(range((len(pts)-1)*n,len(pts)*n))]
  return mesh(name,vs,fs,uv,family,cluster,region,joins)
 def turned(name,c,axis,profile,family,cluster,region,joins,n=40):
  c=Vector(c);axis=Vector(axis).normalized();u=axis.cross(Vector((0,0,1)))
  if u.length<.01:u=axis.cross(Vector((0,1,0)))
  u.normalize();v=axis.cross(u);vs=[];uv=[];fs=[]
  for j,(depth,r) in enumerate(profile):
   for k in range(n):
    a=math.tau*k/n;vs.append(tuple(c+axis*depth+r*(u*math.cos(a)+v*math.sin(a))));uv.append((k/n,j/(len(profile)-1)))
  for j in range(len(profile)):
   for k in range(n):fs.append((j*n+k,j*n+(k+1)%n,((j+1)%len(profile))*n+(k+1)%n,((j+1)%len(profile))*n+k))
  return mesh(name,vs,fs,uv,family,cluster,region,joins)
 # Receiver faces remain visible; deep turned housings and webs root each ring.
 neck=[]
 for i in range(5):
  obj=scene.objects['CGN03 recessed transmission receiver '+str(i)];c=center(obj);a=(-.86,-.79,-.68,-.73,-.80)[i];axis=Vector((math.sin(a),-math.cos(a),0));r=(.019,.021,.026,.029,.024)[i];neck.append((c,axis,obj.name))
  turned('neck receiver stepped gearbox '+str(i),c,axis,[(-.022,r*.73),(-.019,r*1.12),(-.010,r*1.15),(-.004,r*1.03),(.003,r*.90),(.003,r*.64),(-.020,r*.64)],'black-iron','neck receiver chain','neck' if c.z>1.31 else 'body',[obj.name,'inferred recessed cervical frame'])
  turned('neck recessed spindle '+str(i),c,axis,[(-.015,r*.56),(.008,r*.56),(.010,r*.36),(.010,r*.10),(-.015,r*.10)],'machined-steel','neck receiver chain','neck' if c.z>1.31 else 'body',[obj.name])
 for i in range(4):
  a,na,an=neck[i];b,nb,bn=neck[i+1];a-=na*.012;b-=nb*.012
  sweep('neck forged connecting web '+str(i),[a,a.lerp(b,.22),a.lerp(b,.70),b],[.018,.020,.014,.018],'black-iron','neck receiver chain','neck' if a.z>1.31 else 'body',[an,bn],ratio=.56)
 for side in (-1,1):
  pts=[c+Vector((side*.012,0,0))-n*.011 for c,n,_ in neck]
  sweep('neck continuous return conduit '+str(side),pts,[.0055]*5,'worn-bronze','neck receiver chain','neck',[x[2] for x in neck])
 # Flank transmission housing pair connects retained shield barrels to hips.
 for side,sign in (('left',-1),('right',1)):
  cluster=side+' flank transmission';hip=center(scene.objects['CG1c '+side+' hip concentric hinge']);tops=[]
  for i in range(2):
   ob=scene.objects['CG shield03 '+str(sign)+' flank barrel '+str(i)];c=center(ob);p=center(scene.objects['CG shield03 '+str(sign)+' flank piston '+str(i)]);axis=(c-p).normalized();top=c+axis*.065;low=p-axis*.04;tops.append(top)
   sweep(side+' reinforced flank barrel '+str(i),[low,low.lerp(top,.44),low.lerp(top,.50),low.lerp(top,.90),top],[.014,.014,.025,.025,.017],'black-iron',cluster,'body',[ob.name,'CG shield03 '+str(sign)+' flank piston '+str(i)])
   turned(side+' flank gland '+str(i),low.lerp(top,.49),axis,[(-.008,.028),(.008,.028),(.010,.015),(-.008,.015)],'worn-bronze',cluster,'body',[ob.name])
  sweep(side+' flank lower yoke',[hip,hip+Vector((sign*.042,-.035,.034)),tops[0].lerp(hip,.68),tops[1].lerp(hip,.68)],[.028,.026,.018,.018],'forged-steel',cluster,'body',['CG1c '+side+' hip concentric hinge','inferred common flank ram mount'],ratio=.6)
  sweep(side+' flank hydraulic return',[tops[1],tops[1]+Vector((sign*.008,.022,-.06)),hip+Vector((sign*.030,.025,.05)),hip],[.006]*4,'black-iron',cluster,'body',['CG shield03 '+str(sign)+' flank barrel 1','CG1c '+side+' hip concentric hinge'])
  # Nested races stay centered on receiving knee/hock/ankle anchors.
  cluster=side+' articulated leg';joints=[]
  for label,r in (('hip',.065),('knee',.061),('hock',.043),('ankle',.033)):
   ob=scene.objects['CG1c '+side+' '+label+' concentric hinge'];c=center(ob);joints.append(c)
   if label=='hip':continue
   axis=Vector((sign,0,0));turned(side+' '+label+' nested joint race',c,axis,[(.023,r*.94),(.037,r*.94),(.041,r*.76),(.041,r*.55),(.032,r*.55),(.028,r*.72)],'black-iron',cluster,'leg',[ob.name])
  for i,seg in enumerate(('upper','shank','tarsus')):
   a,b=joints[i],joints[i+1];d=(b-a).normalized();span=(b-a).length;off=Vector((sign*.030,0,0));start=a+d*.035;end=b-d*.028
   sweep(side+' '+seg+' cast transmission case',[start,start.lerp(end,.12),start.lerp(end,.48),start.lerp(end,.85),end],[.028,.035,.034,.030,.025],'black-iron',cluster,'leg',['CG1c '+side+' '+seg+' dark structural core'],ratio=.72)
   for k in (-1,1):
    delta=off+Vector((0,k*.025,0));aa=start+delta;bb=end+delta
    sweep(side+' '+seg+' paired ram '+str(k),[aa,aa.lerp(bb,.10),aa.lerp(bb,.64),aa.lerp(bb,.68),bb],[.013,.017,.017,.009,.009],'machined-steel' if k<0 else 'black-iron',cluster,'leg',['CG1c '+side+' '+seg+' piston sleeve '+str(k),'inferred joint yoke'],ratio=1)
   sweep(side+' '+seg+' joint yoke',[a-off*.2,a+off,a+off+d*.025,a+d*.035],[.020,.023,.020,.018],'forged-steel',cluster,'leg',['CG1c '+side+' '+('hip','knee','hock')[i]+' concentric hinge','inferred paired ram root'],ratio=.6)
  # Coupling routes terminate in existing proximal toe-shell volumes; contour retained.
  cluster=side+' digit root manifold';ankle=joints[-1]
  for digit in ('forward toe 1','forward toe 2','forward toe 3','rear toe'):
   ob=scene.objects['CGF03 '+side+' '+digit+' interlocking toe shell 0'];c=center(ob);a=ankle+Vector((0,-.010,-.023));b=c+Vector((0,0,.010));mid=a.lerp(b,.58);mid.z+=.009
   sweep(side+' '+digit+' grounded root coupling',[a,a.lerp(mid,.5),mid,b],[.018,.020,.018,.014],'black-iron',cluster,'foot',['CG1c '+side+' ankle concentric hinge',ob.name],ratio=.65)
 bpy.context.view_layer.update()
 assert len(made)<=80,len(made)
 return {'module':'cg-supervised-machinery06','newMeshes':len(made),'clusters':list(clusters),'retainedHidden':[],'mounts':mounts,'channel':'Existing neck03 receivers a≈-0.75 ±0.20; recessed assembly, body06 worker preserves corridor','geometryStatus':'INFERRED CG construction; not engineering','limits':['Exact source component anatomy and attachment topology unknown','Unseen rear assemblies inferred','Likeness and owner acceptance pending','Root owns surface03/finish04/metal05 and integrated browser export']}
def digest(o):
 data=[o.type,[tuple(r) for r in o.matrix_world],o.parent.name if o.parent else None,o.hide_render,o.hide_get()]
 if o.type=='MESH':data += [[tuple(v.co) for v in o.data.vertices],[(tuple(p.vertices),p.material_index) for p in o.data.polygons],[(uv.name,[tuple(d.uv) for d in uv.data]) for uv in o.data.uv_layers],[m.name if m else None for m in o.data.materials],[(m.name,m.type) for m in o.modifiers]]
 return hashlib.sha256(repr(data).encode()).hexdigest()
def diagnostic():
 p=argparse.ArgumentParser();p.add_argument('--input-root',required=True);p.add_argument('--resolution',type=int,default=640);p.add_argument('--samples',type=int,default=3);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=Path(__file__).resolve().parents[1];inp=Path(a.input_root);out=root/'assets/audit/cg-supervised-machinery06/attempt01';out.mkdir(parents=True,exist_ok=True)
 source=inp/'assets/models/cg-supervised01/attempt05/murderbird-supervised-builder.blend';ref=inp/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(source)==INPUT_SHA;assert sha(ref)==REF_SHA
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;frozen={o.name:digest(o) for o in s.objects if o.type in ('MESH','EMPTY')};cam=s.camera;canon=json.loads((inp/'assets/audit/cg-supervised-camera04/receipt.json').read_text());canon=canon['hypotheses'][canon['proposed_hypothesis']]['camera'];lights={o.name:(o.location.copy(),o.rotation_euler.copy(),o.data.energy,o.data.color[:],o.data.size) for o in s.objects if o.type=='LIGHT'};cameras={}
 s.render.engine='CYCLES';s.cycles.samples=a.samples;s.cycles.device='CPU';s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
 clay=bpy.data.materials.new('Machinery06 diagnostic clay');clay.diffuse_color=(.31,.31,.31,1);clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.31,.31,.31,1);bs.inputs['Roughness'].default_value=.66
 views={'neck':((-6,-2.5,1.62),(0,-.16,1.32),.83),'front':((0,-6,1.33),(0,-.09,.98),1.67),'profile':((-6,0,1.1),(0,-.02,1.00),1.98),'leg':((-6,-2.5,.60),(0,0,.42),1.13),'foot':((-3,-4,1.05),(0,-.03,.11),.87)}
 def render(name,view='whole',claypass=False,grazing=False):
  s.view_layers[0].material_override=clay if claypass else None
  if view=='whole':cam.location=canon['location'];cam.rotation_euler=canon['rotation_euler'];cam.data.ortho_scale=canon['ortho_scale'];cam.data.shift_x,cam.data.shift_y=canon['shift'];cam.data.type=canon['projection'];cam.data.lens=canon['lens_mm']
  else:
   loc,target,scale=views[view];cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale;cam.data.shift_x=cam.data.shift_y=0
  for n,vals in lights.items():
   o=s.objects[n];o.location,o.rotation_euler,o.data.energy,o.data.color,o.data.size=vals
  if grazing:
   ls=[s.objects[n] for n in lights];ls[0].location=(-1,-.8,2.5);ls[0].rotation_euler=(Vector((0,-.1,1.1))-ls[0].location).to_track_quat('-Z','Y').to_euler();ls[0].data.size=.28;ls[0].data.energy=140
   for o in ls[1:]:o.data.energy*=.18
  s.render.resolution_x=a.resolution;s.render.resolution_y=round(a.resolution*853/1280);s.render.filepath=str(out/(name+'.png'));cameras[name]={'location':list(cam.location),'rotation':list(cam.rotation_euler),'orthoScale':cam.data.ortho_scale,'shift':[cam.data.shift_x,cam.data.shift_y],'projection':cam.data.type,'resolution':[s.render.resolution_x,s.render.resolution_y],'clay':claypass,'grazing':grazing,'lights':{n:{'location':list(s.objects[n].location),'rotation':list(s.objects[n].rotation_euler),'energy':s.objects[n].data.energy,'size':s.objects[n].data.size,'color':list(s.objects[n].data.color)} for n in lights}}
  bpy.ops.render.render(write_still=True)
 for name,view,cl,graz in [('whole-clay','whole',True,False),('whole-pbr','whole',False,False),('neck-pbr','neck',False,False),('leg-pbr','leg',False,False),('front-clay','front',True,False),('profile-clay','profile',True,False),('neck-grazing-clay','neck',True,True),('feet-pbr','foot',False,False)]:render('before-'+name,view,cl,graz)
 receipt=apply(s,inp)
 for name,view,cl,graz in [('whole-clay','whole',True,False),('whole-pbr','whole',False,False),('neck-pbr','neck',False,False),('leg-pbr','leg',False,False),('front-clay','front',True,False),('profile-clay','profile',True,False),('neck-grazing-clay','neck',True,True),('feet-pbr','foot',False,False)]:render('after-'+name,view,cl,graz)
 s.view_layers[0].material_override=None;changed=[n for n,d in frozen.items() if digest(s.objects[n])!=d];assert not changed,changed
 graph=bpy.context.evaluated_depsgraph_get();bad=[]
 for o in s.objects:
  if not o.get(TAG):continue
  ev=o.evaluated_get(graph);m=ev.to_mesh()
  if any(not math.isfinite(q) for v in m.vertices for q in v.co):bad.append(o.name)
  if any(not math.isfinite(q) for uv in m.uv_layers for d in uv.data for q in d.uv):bad.append(o.name+' UV')
  ev.to_mesh_clear()
 assert not bad,bad
 bpy.context.preferences.filepaths.save_version=0;native=out/'murderbird-machinery06.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;readback=[n for n,d in frozen.items() if digest(s.objects[n])!=d];assert not readback,readback
 bpy.ops.object.select_all(action='DESELECT')
 for o in s.objects:
  if o.get(TAG):o.select_set(True)
 smoke=out/'machinery06-static-smoke.glb';bpy.ops.export_scene.gltf(filepath=str(smoke),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_materials='NONE',export_texcoords=True)
 receipt.update(inputSHA256=sha(source),inputBinaryPreserved=sha(source)==INPUT_SHA,referenceSHA256=sha(ref),nativeSHA256=sha(native),nativePath=str(native.relative_to(root)),receivingMeshAnchorCount=len(frozen),changedReceivingPayloads=changed,savedNativePreservationReadback=readback,evaluatedFiniteFailures=bad,staticExport={'sha256':sha(smoke),'bytes':smoke.stat().st_size,'scope':'new machinery only; no materials; no animation'},cameras=cameras,renderSettings={'engine':'CYCLES','samples':a.samples,'device':'CPU','denoising':True,'viewTransform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma},images={f.name:sha(f) for f in out.glob('*.png')},scriptSHA256=sha(Path(__file__)),artisticStatus='Unaccepted CG inference; source likeness not established')
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('MACHINERY06_COMPLETE',len(receipt['mounts']),flush=True)
if __name__=='__main__':diagnostic()
