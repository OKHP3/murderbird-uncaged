"""Read-only independent GLB change audit; not collision or likeness validation."""
import hashlib,json,struct,sys
from pathlib import Path

def load(path):
 b=path.read_bytes();assert b[:4]==b'glTF' and struct.unpack_from('<I',b,8)[0]==len(b)
 n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);return j,b[28+n:]

def geometry(doc,blob,node):
 if 'mesh' not in node:return None
 parts=[]
 for primitive in doc['meshes'][node['mesh']]['primitives']:
  attrs={**primitive.get('attributes',{})}
  if 'indices' in primitive:attrs['indices']=primitive['indices']
  result={}
  for name,i in attrs.items():
   accessor=doc['accessors'][i];view=doc['bufferViews'][accessor['bufferView']]
   start=view.get('byteOffset',0)+accessor.get('byteOffset',0)
   item={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}[accessor['componentType']]*{'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[accessor['type']]
   stride=view.get('byteStride',item)
   values=b''.join(blob[start+k*stride:start+k*stride+item]for k in range(accessor['count']))
   result[name]={'count':accessor['count'],'type':accessor['type'],'componentType':accessor['componentType'],'sha256':hashlib.sha256(values).hexdigest()}
  result['material']=doc['materials'][primitive['material']]['name'];parts.append(result)
 return parts

source,candidate=map(Path,sys.argv[1:3]);a,ab=load(source);b,bb=load(candidate)
sa={n['name']:n for n in a['nodes']};sb={n['name']:n for n in b['nodes']}
assert set(sa)==set(sb),'Node identities changed; inspect deliberately'
changed_geometry=[n for n in sa if geometry(a,ab,sa[n])!=geometry(b,bb,sb[n])]
# Mesh/accessor indices may change during export; compare semantic references.
def structure(doc,node):
 return {k:([doc['nodes'][i]['name']for i in v]if k=='children'else v)for k,v in node.items()if k not in ('mesh','extras')}
changed_structure=[n for n in sa if structure(a,sa[n])!=structure(b,sb[n])]
changed_extras=[n for n in sa if sa[n].get('extras')!=sb[n].get('extras')]
assert a['materials']==b['materials'],'Material definitions changed'
allowed=[f'V31 fixed temporal receiving wall {side}' for side in (-1,1)] + [f'V33 diagonal brow receiver {side} {i}' for side in (-1,1) for i in range(3)] + [f'V38 optic cheek shield {side} {i}' for side in (-1,1) for i in range(3)] + [f'V33 swept temporal leaf {side} {i}' for side in (-1,1) for i in range(2)] + [f'V31 temporal fitting root {side} {i}' for side in (-1,1) for i in range(3)] + [f'V31 passive temporal fitting {side} {i}' for side in (-1,1) for i in range(3)]
assert set(changed_geometry)==set(allowed),(changed_geometry,allowed)
assert not changed_structure,changed_structure
assert set(changed_extras).issubset(set(allowed)),changed_extras
print(json.dumps({'scope':'Actual exported geometry, hierarchy, transforms, material definitions; no movement, collision or likeness claim','source':str(source),'candidate':str(candidate),'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidateSHA256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'nodeCount':len(sa),'changedGeometry':changed_geometry,'changedStructure':changed_structure,'changedExtras':changed_extras,'materialDefinitionsExact':True,'materialCount':len(a['materials']),'unchangedGeometryNodes':len(sa)-len(changed_geometry),'status':'PASS'},indent=2))
