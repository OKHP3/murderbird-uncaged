import json,struct,hashlib
from pathlib import Path
import numpy as np
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');OUT=Path('/tmp/cg-loop03-evidence-2121')
def read(p):
 raw=p.read_bytes();n,t=struct.unpack_from('<II',raw,12);d=json.loads(raw[20:20+n]);off=20+n;z,t=struct.unpack_from('<II',raw,off);return d,raw[off+8:]
def acc(d,b,i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];assert a['componentType'] in [5123,5125,5126] and not a.get('normalized') and 'sparse' not in a;dt={5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];nc={'SCALAR':1,'VEC2':2,'VEC3':3}[a['type']];sz=np.dtype(dt).itemsize;return np.ndarray((a['count'],nc),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',nc*sz),sz)).copy()
def triangles(d,b,mat):
 out=[]
 for nd in d['nodes']:
  if 'mesh' not in nd:continue
  assert nd.get('matrix',[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1])==[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
  assert nd.get('translation',[0,0,0])==[0,0,0] and nd.get('rotation',[0,0,0,1])==[0,0,0,1] and nd.get('scale',[1,1,1])==[1,1,1]
  for pr in d['meshes'][nd['mesh']]['primitives']:
   if d['materials'][pr['material']]['name']!=mat:continue
   at=pr['attributes'];idx=acc(d,b,pr['indices']).ravel();rows=np.concatenate([acc(d,b,at['POSITION']),acc(d,b,at['TEXCOORD_0']),acc(d,b,at['NORMAL'])],axis=1);out.append(rows[idx].reshape(-1,3,8))
 return np.concatenate(out)
def key(tri):
 k=np.round(tri[:,:5].astype(np.float64),6);ix=min(range(3),key=lambda j:tuple(k[j]));return tuple(k[np.roll(np.arange(3),-ix)].ravel()),tri[np.roll(np.arange(3),-ix)]
rows=[]
for era in ['builder','maker','mechanic']:
 old=R/f'assets/audit/cg-recursive-three-loop01/loop02/delivery/retained03/{era}/murderbird-recursive-{era}.glb';new=R/f'assets/audit/cg-recursive-three-loop01/loop03/delivery/retained04/{era}/murderbird-recursive-{era}.glb'
 a,b=read(old);c,e=read(new);ot=triangles(a,b,f'CG metal05 / worn-bronze / {era} / retained-uv.001');nt=triangles(c,e,f'CGRS04 {era} uv-method02-visual02-heldnormal formed crown');lookup={};dups=0
 for t in ot:
  k,v=key(t)
  if k in lookup:dups+=1
  lookup[k]=v
 unmatched=0;maxdelta=0;changed=0
 for t in nt:
  k,v=key(t)
  if k not in lookup:unmatched+=1;continue
  err=float(np.max(np.abs(v[:,-3:].astype(np.float64)-lookup[k][:,-3:])));maxdelta=max(maxdelta,err);changed+=err!=0
 rows.append({'era':era,'new_crown_triangles':len(nt),'old_shared_material_triangles':len(ot),'old_duplicate_position_UV0_keys':dups,'unmatched_new_joint_position_UV0_triangles':unmatched,'triangles_with_changed_stored_normal_components':changed,'max_stored_normal_component_delta_old_GLB_to_new_GLB':maxdelta,'old_GLB_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'new_GLB_sha256':hashlib.sha256(new.read_bytes()).hexdigest()})
(OUT/'crown-normal-association.json').write_text(json.dumps({'method':'Read-only actual prior/final GLB accessor comparison, material-indexed oriented joint position+UV0 triangle keys rounded6; all actual node transforms asserted identity. New extra explicit UV channel not compared here (full checker covers it). Stored normals compared component-exact after joint association.','results':rows,'limits':'This isolates encoded crown normals across static exports, not a proven cause of native/export mismatch or full shader equivalence.'},indent=2)+'\n');print(rows)
