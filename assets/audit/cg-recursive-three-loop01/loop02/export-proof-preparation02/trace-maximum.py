"""Read-only targeted inherited maximum normal-delta trace; no producer imports."""
import bpy,numpy as np,pathlib,json,hashlib,struct
from mathutils import Matrix,Vector,Quaternion
ROOT=pathlib.Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');OUT=pathlib.Path('/tmp/cg-recursive-export-proof02');x=json.load(open(OUT/'checker-results.json'));SW=Matrix(((1,0,0),(0,0,1),(0,-1,0)));results=[]
def payload(path,name):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);o=bpy.data.objects[name];dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);m=e.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
 try:
  m.calc_loop_triangles();w=e.matrix_world.copy();nm=w.to_3x3().inverted().transposed();uv=next((u for u in m.uv_layers if u.active_render),m.uv_layers.active);rows=[];slots=[]
  for t in m.loop_triangles:
   loops=list(t.loops)
   if w.determinant()<0:loops.reverse()
   for li in loops:
    p=SW@(w@m.vertices[m.loops[li].vertex_index].co);n=SW@((nm@m.corner_normals[li].vector).normalized());v=uv.data[li].uv;rows.append((*p,float(v[0]),float(np.float32(1)-np.float32(v[1])),*n))
   slots.append(m.materials[t.material_index].name)
  a=np.array(rows,np.float32);return {'joint_corner_float32_sha256':hashlib.sha256(a.astype('<f4').tobytes()).hexdigest(),'triangle_material_names_sha256':hashlib.sha256(json.dumps(slots).encode()).hexdigest(),'triangles':len(slots),'world_matrix':[list(v) for v in w],'UV_name':uv.name,'hide_render':o.hide_render}
 finally:e.to_mesh_clear()
def decode(path):
 raw=path.read_bytes();n,t=struct.unpack_from('<II',raw,12);d=json.loads(raw[20:20+n]);z,t=struct.unpack_from('<II',raw,20+n);return d,raw[28+n:28+n+z]
DT={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'};NC={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
def acc(d,b,i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];dt=np.dtype(DT[a['componentType']]);nc=NC[a['type']];return np.ndarray((a['count'],nc),dt,b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',nc*dt.itemsize),dt.itemsize)).copy()
def meshes(d):
 out=[]
 def rec(i,par):
  n=d['nodes'][i]
  if 'matrix'in n:w=Matrix(np.array(n['matrix']).reshape(4,4).T.tolist())
  else:
   q=n.get('rotation',[0,0,0,1]);w=Matrix.Translation(Vector(n.get('translation',[0,0,0])))@Quaternion((q[3],*q[:3])).to_matrix().to_4x4()@Matrix.Diagonal((*n.get('scale',[1,1,1]),1))
  w=par@w
  if 'mesh'in n:out.append((n['mesh'],w))
  for j in n.get('children',[]):rec(j,w)
 for i in d['scenes'][d.get('scene',0)]['nodes']:rec(i,Matrix.Identity(4))
 return out
for r in x['results']:
 era=r['era'];c=max(r['material_checks'],key=lambda c:c.get('normal_vector_max_L2',0));name=c['worst_normal_native_object'];before=payload(pathlib.Path(r['original_native_path']),name);after=payload(pathlib.Path(r['native_path']),name);path=ROOT/'assets/models/cg-supervised01/attempt09'/('murderbird-supervised-'+era+'.glb');d,b=decode(path);target=np.array(c['worst_normal_joint_triangle']['GLB_corners'],np.float32);matches=[]
 for mi,w in meshes(d):
  nm=w.to_3x3().inverted().transposed()
  for pr in d['meshes'][mi]['primitives']:
   if d['materials'][pr['material']]['name']!=c['material']:continue
   at=pr['attributes'];p=acc(d,b,at['POSITION']);idx=acc(d,b,pr['indices']).ravel();pos=np.array([tuple(w@Vector(v)) for v in p],np.float32)[idx].reshape(-1,3,3)
   for rot in range(3):
    pp=np.roll(pos,rot,axis=1);ix=np.flatnonzero(np.all(np.round(pp.astype(np.float64),5)==np.round(target[None,:,:3].astype(np.float64),5),axis=(1,2)))
    for t in ix:
     ids=np.roll(idx.reshape(-1,3)[t],rot);uv=acc(d,b,at['TEXCOORD_0'])[ids];n=acc(d,b,at['NORMAL'])[ids];n=np.array([tuple((nm@Vector(v)).normalized()) for v in n],np.float32);joint=np.concatenate((pp[t],uv,n),axis=1);matches.append({'position_max_abs':float(np.abs(joint[:,:3]-target[:,:3]).max()),'UV_max_abs':float(np.abs(joint[:,3:5]-target[:,3:5]).max()),'normal_max_L2_vs_retainedGLB':float(np.linalg.norm(joint[:,5:]-target[:,5:],axis=1).max()),'original09_GLB_joint_corners':joint.tolist()})
 results.append({'era':era,'native_object':name,'original09_payload':before,'retained02_payload':after,'unchanged_evaluated_joint_corner_payload':before==after,'original09_GLB_path':str(path),'original09_GLB_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'target_triangle_matches_in_original09_GLB':matches,'strict_max_normal_L2':c['normal_vector_max_L2'],'strict_max_normal_angle_degrees':c['normal_angle_max_degrees']});print('TRACE',era,before==after,len(matches),flush=True)
(OUT/'maximum-trace.json').write_text(json.dumps({'method':'Actual original09/retained02 maximum-delta receiving object evaluated corner position/active UV/transformed normalized normals/material assignments compared exactly; targeted original09 GLB oriented triangle compared with retained02 maximum triangle. No save/render/export.','results':results},indent=2)+'\n')
