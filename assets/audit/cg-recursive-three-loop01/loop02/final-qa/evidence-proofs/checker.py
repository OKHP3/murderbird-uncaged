"""Read-only native/GLB triangle-corner correspondence checker. Run in Blender.
No producer helpers; no save, render or export. Outputs only --out directory.
Predeclared tolerances: position 1e-5 coordinate key, UV absolute 2e-6,
normalized world normal vector L2 2e-5. Failures remain failures.
"""
import bpy,numpy as np,pathlib,json,struct,hashlib,collections,datetime,argparse,sys
from mathutils import Matrix,Quaternion,Vector
args=argparse.ArgumentParser();args.add_argument('--root',required=True);args.add_argument('--base',required=True);args.add_argument('--out',required=True);args.add_argument('--eras',default='builder');opt=args.parse_args(sys.argv[sys.argv.index('--')+1:]);ROOT=pathlib.Path(opt.root);BASE=ROOT/opt.base;OUT=pathlib.Path(opt.out);assert OUT.resolve().is_relative_to(pathlib.Path("/tmp/cg-recursive-loop02-evidence-1933").resolve()), "output must remain under assigned temporary proof root";OUT.mkdir(parents=True,exist_ok=True)
DT={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'};NC={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode(path):
 raw=path.read_bytes();magic,version,total=struct.unpack_from('<III',raw);assert(magic,version,total)==(0x46546c67,2,len(raw));n,t=struct.unpack_from('<II',raw,12);assert t==0x4e4f534a;d=json.loads(raw[20:20+n]);off=20+n;z,t=struct.unpack_from('<II',raw,off);assert t==0x004e4942 and off+8+z==len(raw);return d,raw[off+8:]
def acc(d,blob,i):
 a=d['accessors'][i];assert 'sparse' not in a,'sparse accessor unsupported';v=d['bufferViews'][a['bufferView']];assert v.get('buffer',0)==0;n=NC[a['type']];dtype=np.dtype(DT[a['componentType']]);start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',n*dtype.itemsize);assert start+(a['count']-1)*stride+n*dtype.itemsize<=v.get('byteOffset',0)+v['byteLength']<=len(blob);x=np.ndarray((a['count'],n),dtype=dtype,buffer=blob,offset=start,strides=(stride,dtype.itemsize)).copy()
 if a.get('normalized'):
  info=np.iinfo(dtype);x=np.maximum(x.astype(np.float32)/info.max,-1) if info.min<0 else x.astype(np.float32)/info.max
 return x
def node_matrix(n):
 if 'matrix'in n:return Matrix(np.array(n['matrix'],np.float32).reshape(4,4).T.tolist())
 q=n.get('rotation',[0,0,0,1]);return Matrix.Translation(Vector(n.get('translation',[0,0,0])))@Quaternion((q[3],*q[:3])).to_matrix().to_4x4()@Matrix.Diagonal((*n.get('scale',[1,1,1]),1))
def scene_meshes(d):
 found=[];seen=set()
 def visit(i,parent):
  assert i not in seen,'shared/cyclic scene node unsupported';seen.add(i);n=d['nodes'][i];world=parent@node_matrix(n)
  if 'mesh'in n:found.append((i,n['mesh'],world))
  for j in n.get('children',[]):visit(j,world)
 for i in d['scenes'][d.get('scene',0)]['nodes']:visit(i,Matrix.Identity(4))
 return found
SW=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
def canonical(tri):
 # Rotate each triangle by lowest rounded position corner. Preserve cyclic
 # winding and complete corner-associated attributes; never independent sets.
 keys=np.round(tri[:,:,:3].astype(np.float64),5);ix=np.zeros(len(tri),np.int64)
 for i in (1,2):
  a=keys[:,i];b=keys[np.arange(len(keys)),ix];less=(a[:,0]<b[:,0])|((a[:,0]==b[:,0])&((a[:,1]<b[:,1])|((a[:,1]==b[:,1])&(a[:,2]<b[:,2]))));ix=np.where(less,i,ix)
 tri=tri[np.arange(len(tri))[:,None],(ix[:,None]+np.arange(3))%3];pk=np.round(tri[:,:,:3].astype(np.float64),5).reshape(len(tri),9);pk[pk==0]=0
 # Geometry first; duplicate identical triangles are ordered by UV/normal
 # attributes together, and their ambiguity is disclosed.
 full=np.concatenate((pk,np.round(tri[:,:,3:].astype(np.float64),7).reshape(len(tri),-1)),axis=1);order=np.lexsort(tuple(full[:,i] for i in range(full.shape[1]-1,-1,-1)));tri=tri[order];pk=pk[order];dups=int(np.sum(np.all(pk[1:]==pk[:-1],axis=1))) if len(pk)>1 else 0
 return tri,pk,dups,order
results=[]
for era in opt.eras.split(','):
 original=ROOT/'assets/models/cg-supervised01/attempt09'/('murderbird-supervised-'+era+'.blend');bpy.ops.wm.open_mainfile(filepath=str(original),load_ui=False,use_scripts=False);original_names=set(bpy.data.objects.keys());native=BASE/era/('murderbird-recursive-'+era+'.blend');glb=BASE/era/('murderbird-recursive-'+era+'.glb');bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False);dg=bpy.context.evaluated_depsgraph_get();groups=collections.defaultdict(list);sourcegroups=collections.defaultdict(list);uv_inventory=collections.defaultdict(set);negative=0
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.hide_render or o.get('authoringGuide'):continue
  ev=o.evaluated_get(dg);m=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
  try:
   m.calc_loop_triangles();world=ev.matrix_world.copy();normalmat=world.to_3x3().inverted().transposed();neg=world.determinant()<0;negative+=neg
   renderuv=next((u for u in m.uv_layers if u.active_render),m.uv_layers.active)
   for t in m.loop_triangles:
    mat=m.materials[t.material_index];assert mat is not None;required={n.uv_map for n in mat.node_tree.nodes if n.type=='UVMAP' and n.uv_map} if mat.use_nodes else set();explicit=[u for u in m.uv_layers if u.name in required];assert required<={u.name for u in explicit},'missing native explicitly named UV map'
    uv_inventory[mat.name].add(tuple(['active:'+renderuv.name] if renderuv else ['zero-active'])+tuple(u.name for u in explicit));layers=[renderuv]+explicit
    # One active channel plus explicit maps, in native order; when renderUV
    # is explicitly referenced it is intentionally also present as named map.
    loops=list(t.loops)
    if neg:loops.reverse()
    corners=[]
    for li in loops:
     pos=SW@(world@m.vertices[m.loops[li].vertex_index].co);normal=SW@((normalmat@m.corner_normals[li].vector).normalized());uv=[]
     for u in layers:
      v=u.data[li].uv if u else Vector((0.,0.));uv.extend((float(v[0]),float(np.float32(1)-np.float32(v[1]))))
     corners.append((*pos,*uv,*normal))
    groups[mat.name].append(corners);sourcegroups[mat.name].append(o.name)
  finally:ev.to_mesh_clear()
 d,blob=decode(glb);ggroups=collections.defaultdict(list);priminfo=[]
 for ni,mi,world in scene_meshes(d):
  nm=world.to_3x3().inverted().transposed()
  for pr in d['meshes'][mi]['primitives']:
   assert pr.get('mode',4)==4;idx=acc(d,blob,pr['indices']).ravel();at=pr['attributes'];p=acc(d,blob,at['POSITION']);no=acc(d,blob,at['NORMAL']);assert len(idx)%3==0 and idx.max()<len(p) and len(no)==len(p);name=d['materials'][pr['material']]['name'];channels=sorted(int(k.split('_')[1]) for k in at if k.startswith('TEXCOORD_'));assert channels==list(range(len(channels))),'noncontiguous UV channels unsupported';uvs=[acc(d,blob,at['TEXCOORD_'+str(i)]) for i in channels];assert all(len(a)==len(p) for a in uvs);mat=d['materials'][pr['material']];textures=[mat.get(k) for k in ['normalTexture','occlusionTexture','emissiveTexture']]+[mat.get('pbrMetallicRoughness',{}).get(k) for k in ['baseColorTexture','metallicRoughnessTexture']];refs=[]
   for tex in [t for t in textures if t]:
    assert tex.get('texCoord',0) in channels;assert 0<=tex['index']<len(d['textures']);ti=d['textures'][tex['index']];assert 'source'in ti and 0<=ti['source']<len(d['images']);refs.append({'texture_index':tex['index'],'image_index':ti['source'],'UV_channel':tex.get('texCoord',0)})
   stored_normal_lengths=np.linalg.norm(no.astype(np.float64),axis=1);p=np.array([tuple(world@Vector(v)) for v in p],np.float32);no=np.array([tuple((nm@Vector(v)).normalized()) for v in no],np.float32);rows=np.concatenate([p,*uvs,no],axis=1);assert np.isfinite(rows).all();ggroups[name].append(rows[idx].reshape(-1,3,rows.shape[1]));priminfo.append({'node':ni,'material':name,'triangles':len(idx)//3,'UV_channels':channels,'world_matrix':[list(row) for row in world],'texture_binding_refs':refs,'stored_normal_length_min':float(stored_normal_lengths.min()),'stored_normal_length_max':float(stored_normal_lengths.max())})
 checks=[]
 for name in sorted(set(groups)|set(ggroups)):
  nr=np.asarray(groups[name],np.float32);gr=np.concatenate(ggroups[name]) if name in ggroups else np.empty((0,3,0));record={'material':name,'native_triangles':len(nr),'GLB_triangles':len(gr),'native_UV_layouts':[list(v) for v in sorted(uv_inventory[name])]}
  if nr.shape!=gr.shape:record.update(status='FAIL',reason='triangle or channel shape mismatch',native_shape=list(nr.shape),GLB_shape=list(gr.shape));checks.append(record);continue
  a,pk,dups,order=canonical(nr);b,gpk,gdups,gorder=canonical(gr);source_names=np.array(sourcegroups[name],dtype=object)[order];geom=np.all(pk==gpk,axis=1);record.update(duplicate_geometry_triangles=dups,GLB_duplicate_geometry_triangles=gdups,oriented_position_triangle_key_mismatches=int(np.sum(~geom)))
  if not geom.all():record.update(status='FAIL',reason='strict oriented triangle geometry mismatch; UV/normal correspondence not certified');checks.append(record);continue
  uv_err=np.abs(a[:,:,3:-3].astype(np.float64)-b[:,:,3:-3]);normal_err=np.linalg.norm(a[:,:,-3:].astype(np.float64)-b[:,:,-3:],axis=2);pos_err=np.abs(a[:,:,:3].astype(np.float64)-b[:,:,:3]);uv_bad=np.any(uv_err>2e-6,axis=(1,2));normal_bad=np.any(normal_err>2e-5,axis=1);length=np.linalg.norm(b[:,:,-3:].astype(np.float64),axis=2)
  record.update(status='PASS' if not uv_bad.any() and not normal_bad.any() else 'FAIL',position_triangle_material_status='PASS',UV_joint_corner_status='PASS' if not uv_bad.any() else 'FAIL',normal_joint_corner_status='PASS' if not normal_bad.any() else 'FAIL',position_max_abs=float(pos_err.max(initial=0)),UV_max_abs=float(uv_err.max(initial=0)),UV_bad_triangles=int(uv_bad.sum()),normal_vector_max_L2=float(normal_err.max(initial=0)),normal_bad_triangles=int(normal_bad.sum()),normal_GLBlength_min=float(length.min()),normal_GLBlength_max=float(length.max()),normal_L2_percentiles={str(v):float(np.percentile(normal_err,v)) for v in (50,90,99,100)},normal_angle_max_degrees=float(2*np.arcsin(min(1,float(normal_err.max(initial=0))/2))*180/np.pi))
  worst=int(np.argmax(np.max(normal_err,axis=1)));record['worst_normal_native_object']=str(source_names[worst]);record['worst_normal_object_existed_in_original09']=str(source_names[worst]) in original_names;record['worst_normal_joint_triangle']={'native_corners':a[worst].tolist(),'GLB_corners':b[worst].tolist()};bad=np.flatnonzero(uv_bad|normal_bad);record['first_failure_joint_triangles']=[{'native_corners':a[i].tolist(),'GLB_corners':b[i].tolist()} for i in bad[:3]];checks.append(record)
 packed={hashlib.sha256(bytes(i.packed_file.data)).hexdigest():i.name for i in bpy.data.images if i.source=='FILE' and i.packed_file};images=[];imdir=OUT/(era+'-embedded');imdir.mkdir(exist_ok=True)
 for j,im in enumerate(d.get('images',[])):
  assert 'uri'not in im;v=d['bufferViews'][im['bufferView']];raw=blob[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];h=hashlib.sha256(raw).hexdigest();ext={'image/png':'.png','image/jpeg':'.jpg'}.get(im.get('mimeType'),'.bin');p=imdir/(str(j)+ext);p.write_bytes(raw);images.append({'index':j,'name':im.get('name'),'mimeType':im.get('mimeType'),'path':str(p),'sha256':h,'native_packed_name':packed.get(h),'native_packed_exact':h in packed})
 result={'era':era,'original_native_path':str(original),'original_native_sha256':sha(original),'native_path':str(native),'native_sha256':sha(native),'GLB_path':str(glb),'GLB_sha256':sha(glb),'status':'PASS' if all(c['status']=='PASS' for c in checks) and all(i['native_packed_exact'] for i in images) else 'FAIL','material_checks':checks,'primitives':priminfo,'embedded_images':images,'negative_transform_native_objects':negative,'skins':len(d.get('skins',[])),'animations':len(d.get('animations',[]))};results.append(result);(OUT/('raw-'+era+'.json')).write_text(json.dumps(result,indent=2)+'\n');print('ERA_COMPLETE',era,result['status'],[(c['material'],c['status'],c.get('UV_max_abs'),c.get('normal_vector_max_L2')) for c in checks if c['status']!='PASS'],flush=True)
(OUT/'checker-results.json').write_text(json.dumps({'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'position_key_decimal_places':5,'UV_absolute_tolerance':2e-6,'normalized_normal_vector_L2_tolerance':2e-5,'results':results,'limits':['No producer helper imports; read-only native evaluation and GLB decode, outputs only configured temp directory.','Default GLB scene node transforms supported; sparse accessors or shared/cyclic scene node rejected.','UV0 is native active render UV, additional named shader UV maps native layer order; duplicate/multiple layouts reported, not assumed hidden.','Oriented cyclic triangle canonicalization retains per-corner position, all emitted UV channels, normal and material association. Duplicate identical geometry is sorted by associated attributes; ambiguity count disclosed.','Predeclared strict normal tolerance may fail Blender custom split-normal encoding; failures are evidence, not tuned away.','No full shader, texture color-management, lighting, rendered-pixel or owner acceptance proof.']},indent=2)+'\n')
