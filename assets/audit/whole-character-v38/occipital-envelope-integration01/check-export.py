"""Read-only independent GLB change audit; not collision or likeness validation."""
import hashlib,json,struct,sys
from pathlib import Path

def load(path):
 b=path.read_bytes();assert b[:4]==b'glTF' and struct.unpack_from('<I',b,4)[0]==2 and struct.unpack_from('<I',b,8)[0]==len(b)
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

source,candidate,scope_path=map(Path,sys.argv[1:4]);scope=json.loads(scope_path.read_text());a,ab=load(source);b,bb=load(candidate)
sa={n['name']:n for n in a['nodes']};sb={n['name']:n for n in b['nodes']}
assert len(sa)==len(a['nodes']) and len(sb)==len(b['nodes']),'Duplicate node names'
added=set(sb)-set(sa);removed=set(sa)-set(sb)
assert added==set(scope['added']),('Unexpected added nodes',added)
assert removed==set(scope.get('removed',[])),('Unexpected removed nodes',removed)
common=set(sa)&set(sb)
changed_geometry=sorted(n for n in common if geometry(a,ab,sa[n])!=geometry(b,bb,sb[n]))
def structure(doc,node):
 return {k:([doc['nodes'][i]['name']for i in v if doc['nodes'][i]['name'] not in added]if k=='children'else v)for k,v in node.items()if k not in ('mesh','extras')}
changed_structure=sorted(n for n in common if structure(a,sa[n])!=structure(b,sb[n]))
changed_extras=sorted(n for n in common if sa[n].get('extras')!=sb[n].get('extras'))
assert a['materials']==b['materials'],'Material definitions changed'
assert set(changed_geometry).issubset(scope['changed']),set(changed_geometry)-set(scope['changed'])
assert not changed_structure,changed_structure
assert set(changed_extras).issubset(scope['changed']),changed_extras
parents={b['nodes'][i]['name']:n['name']for n in b['nodes']for i in n.get('children',[])}
for name in added:
 assert parents.get(name)==scope['added'][name]['parent'],('Added owner',name,parents.get(name))
 node=sb[name];assert 'mesh'in node,('Added non-mesh',name)
 assert node.get('extras',{}).get('exteriorEras')==scope['added'][name]['exteriorEras'],('Added era role',name,node.get('extras'))
print(json.dumps({'scope':'Actual exported geometry, hierarchy, transforms, material definitions and explicitly reviewed additive scope; no movement, collision or likeness claim','source':str(source),'candidate':str(candidate),'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidateSHA256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'sourceNodeCount':len(sa),'candidateNodeCount':len(sb),'changedGeometry':changed_geometry,'added':sorted(added),'removed':sorted(removed),'changedStructure':changed_structure,'changedExtras':changed_extras,'materialDefinitionsExact':True,'materialCount':len(a['materials']),'unchangedGeometryNodes':len(common)-len(changed_geometry),'status':'PASS'},indent=2))
