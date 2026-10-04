import sys,json,struct,hashlib,math,datetime
from pathlib import Path
import numpy as np
ROOT=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
def validate(era):
 p=ROOT/f'assets/models/cg-supervised01/attempt09/murderbird-supervised-{era}.glb';raw=p.read_bytes();assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
 off=12;doc=None;binary=None
 while off<len(raw):
  n,k=struct.unpack_from('<II',raw,off);off+=8;chunk=raw[off:off+n];off+=n
  if k==0x4e4f534a:doc=json.loads(chunk)
  elif k==0x004e4942:binary=chunk
 assert doc is not None and binary is not None
 assert not doc.get('skins') and not doc.get('animations')
 uris=[]
 def walk(x):
  if isinstance(x,dict):
   if 'uri' in x:uris.append(x['uri'])
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 walk(doc);assert not uris,uris
 for im in doc.get('images',[]):assert 'bufferView' in im
 types={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'};shapes={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
 def acc(i):
  a=doc['accessors'][i];assert not a.get('sparse');v=doc['bufferViews'][a['bufferView']];dt=np.dtype(types[a['componentType']]);k=shapes[a['type']];start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',dt.itemsize*k);assert start+(a['count']-1)*stride+dt.itemsize*k<=v.get('byteOffset',0)+v['byteLength']
  return np.ndarray((a['count'],k),dtype=dt,buffer=binary,offset=start,strides=(stride,dt.itemsize))
 checked={};prims=[];triangles=0
 for mesh in doc.get('meshes',[]):
  for prim in mesh['primitives']:
   assert prim.get('mode',4)==4
   attrs=prim['attributes'];assert 'POSITION' in attrs and 'NORMAL' in attrs
   for name,i in attrs.items():
    if name not in ('POSITION','NORMAL') and not name.startswith('TEXCOORD_'):continue
    a=acc(i);assert np.isfinite(a).all(),(mesh['name'],name);record={'semantic':name,'count':len(a),'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist(),'finite':True}
    if name=='NORMAL':
     norms=np.linalg.norm(a,axis=1);error=float(np.max(np.abs(norms-1)));record['max_unit_length_error']=error;assert error<=2e-5,(mesh['name'],error)
    checked[str(i)]=record
   index=acc(prim['indices']);assert len(index)%3==0 and int(index.max())<len(acc(attrs['POSITION']));triangles+=len(index)//3
   prims.append({'mesh':mesh.get('name'),'material':doc['materials'][prim['material']]['name'],'uv_semantics':[k for k in attrs if k.startswith('TEXCOORD_')]})
 result={'era':era,'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'materials':len(doc.get('materials',[])),'embedded_images':len(doc.get('images',[])),'meshes':len(doc.get('meshes',[])),'animations':0,'skins':0,'uri_count':0,'triangles':triangles,'accessors':checked,'primitives':prims,'status':'PASS','limits':['Independent binary accessor check; all UVs finite, historical original UVs may wrap. New normalized UV bounds checked separately in reopened native.','No browser or likeness judgment.']}
 Path(f'/tmp/cg-delivery09-glb-{era}.json').write_text(json.dumps(result,indent=2));print(era,'GLB_PASS',len(checked),triangles,flush=True)
if __name__=='__main__':
 for era in sys.argv[1:] or ['builder','maker','mechanic']:validate(era)
