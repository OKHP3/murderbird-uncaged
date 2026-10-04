import json,struct,hashlib,io
from pathlib import Path
from collections import Counter
import numpy as np
from PIL import Image
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');results=[]
for era in ['builder','maker','mechanic']:
 p=R/f'assets/models/cg-supervised01/attempt09/murderbird-supervised-{era}.glb';raw=p.read_bytes();magic,version,total=struct.unpack_from('<4sII',raw);assert magic==b'glTF' and version==2 and total==len(raw);offset=12;chunks={}
 while offset<len(raw):
  size,kind=struct.unpack_from('<II',raw,offset);offset+=8;assert offset+size<=len(raw);chunks[kind]=raw[offset:offset+size];offset+=size
 d=json.loads(chunks[0x4e4f534a]);binary=chunks[0x004e4942];issues=[];accessors=[];counts=Counter();uvrefs=[]
 def ar(i):
  a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];assert v.get('buffer',0)==0 and not a.get('sparse');dt=np.dtype({5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]);n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',dt.itemsize*n);assert start+(a['count']-1)*stride+dt.itemsize*n<=v.get('byteOffset',0)+v['byteLength']<=len(binary);return np.ndarray((a['count'],n),dtype=dt,buffer=binary,offset=start,strides=(stride,dt.itemsize))
 for mesh in d['meshes']:
  assert 'guide' not in mesh.get('name','').lower()
  for prim in mesh['primitives']:
   assert prim.get('mode',4)==4;attrs=prim['attributes'];assert all(k in attrs for k in ['POSITION','NORMAL','TEXCOORD_0']);pos=ar(attrs['POSITION']);inds=ar(prim['indices']);assert inds.size%3==0 and inds.min()>=0 and inds.max()<len(pos);mi=prim['material'];assert 0<=mi<len(d['materials']);mat=d['materials'][mi];counts[mat['name']]+=inds.size//3
   for key,index in attrs.items():
    v=ar(index);assert len(v)==len(pos) and np.isfinite(v).all();r={'mesh':mesh['name'],'attribute':key,'accessor':index,'count':len(v),'min':v.min(axis=0).tolist(),'max':v.max(axis=0).tolist()}
    if key=='NORMAL':r['max_unit_error']=float(np.max(abs(np.linalg.norm(v,axis=1)-1)));assert r['max_unit_error']<2e-5
    accessors.append(r)
   def refs(x):
    if isinstance(x,dict):
     if 'index' in x and isinstance(x['index'],int) and 'Texture' in str(x):pass
     for k,v in x.items():
      if 'texture' in k.lower() and isinstance(v,dict) and 'index' in v:
       tex=d['textures'][v['index']];assert 0<=tex['source']<len(d['images']);coord=v.get('texCoord',0);assert f'TEXCOORD_{coord}' in attrs;uvrefs.append({'material':mat['name'],'property':k,'texCoord':coord,'image':d['images'][tex['source']].get('name')})
      refs(v)
    elif isinstance(x,list):
     for v in x:refs(v)
   refs(mat)
 def uris(x):
  if isinstance(x,dict):return ['uri'] if 'uri' in x else sum((uris(v) for v in x.values()),[])
  if isinstance(x,list):return sum((uris(v) for v in x),[])
  return []
 assert not uris(d) and not d.get('skins') and not d.get('animations');images=[]
 for im in d['images']:
  assert 'bufferView' in im;view=d['bufferViews'][im['bufferView']];start=view.get('byteOffset',0);blob=binary[start:start+view['byteLength']];assert len(blob)==view['byteLength'];img=Image.open(io.BytesIO(blob));img.load();images.append({'name':im.get('name'),'dimensions':list(img.size),'mode':img.mode,'sha256':hashlib.sha256(blob).hexdigest()})
 receipt=json.loads((R/f'assets/audit/cg-supervised01/attempt09/{era}/receipt.json').read_text())['browser_export'];assert dict(counts)==receipt['triangles_by_material'];assert len(d['materials'])==receipt['batched_meshes'];result={'era':era,'path':str(p.relative_to(R)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'status':'PASS','meshes':len(d['meshes']),'materials':len(d['materials']),'images':images,'triangles':sum(counts.values()),'triangles_by_material':dict(counts),'all_attributes_finite':True,'indices_and_buffer_bounds_valid':True,'no_uri_skin_animation_or_guide_mesh':True,'receipt_triangle_material_counts_match':True,'uv_shader_references_present':True,'uv_refs':uvrefs,'optic_materials':[m for m in d['materials'] if 'CGO13' in m.get('name','')],'limits':['Binary attributes/material assignments and image decodability checked independently. No independent native-to-GLB corner-by-corner equivalence or pixel equivalence test.']};results.append(result);print(era,'PASS',len(d['meshes']),len(images),sum(counts.values()))
Path('/tmp/cg-eq09-evidence-glb-independent.json').write_text(json.dumps({'method':'Independent binary decoder and accessor bounds/finite/unit normal/index/material/UV reference/image decode checks; receipt count crosscheck only.', 'results':results},indent=2))
