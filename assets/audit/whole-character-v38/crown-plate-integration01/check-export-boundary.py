import json,struct,hashlib,sys
from pathlib import Path
base,candidate,out=map(Path,sys.argv[1:4])
def read(p):
 raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);return doc,raw[28+n:]
def digest(d,b,a):
 x=d['accessors'][a];v=d['bufferViews'][x['bufferView']];size={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}[x['componentType']]*{'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[x['type']];start=v.get('byteOffset',0)+x.get('byteOffset',0);stride=v.get('byteStride',size)
 return [x['componentType'],x['type'],x['count'],hashlib.sha256(b''.join(b[start+i*stride:start+i*stride+size] for i in range(x['count']))).hexdigest()]
def inventory(d,b):
 parents={child:d['nodes'][i]['name'] for i,n in enumerate(d['nodes']) for child in n.get('children',[])};r={}
 for i,n in enumerate(d['nodes']):
  shape=[]
  for p in d['meshes'][n['mesh']]['primitives'] if 'mesh'in n else []:
   shape.append({'attributes':{k:digest(d,b,v)for k,v in p['attributes'].items()},'indices':digest(d,b,p['indices'])if'indices'in p else None,'material':d['materials'][p['material']]['name']if'material'in p else None,'mode':p.get('mode',4)})
  r[n['name']]={'geometry':shape,'structure':{k:n.get(k)for k in ['matrix','translation','rotation','scale','skin']},'parent':parents.get(i),'extras':n.get('extras',{})}
 return r
bd,bb=read(base);cd,cb=read(candidate);a=inventory(bd,bb);b=inventory(cd,cb)
assert a.keys()==b.keys(),'Node identities changed'
assert {m['name']:m for m in bd['materials']}=={m['name']:m for m in cd['materials']},'Materials changed'
changed=[n for n in a if a[n]['geometry']!=b[n]['geometry']];allowed=json.loads(Path(sys.argv[4]).read_text())['changed'];assert set(changed)==set(allowed),(changed,allowed)
structure=[n for n in a if a[n]['structure']!=b[n]['structure'] or a[n]['parent']!=b[n]['parent']];assert structure==[],structure
extras=[n for n in a if a[n]['extras']!=b[n]['extras']];assert set(extras)<=set(allowed),extras
result={'status':'PASS','scope':'Actual exported geometry, material definitions, hierarchy and local transforms. No motion, collision, strength or likeness claim.','source':str(base),'candidate':str(candidate),'sourceSHA256':hashlib.sha256(base.read_bytes()).hexdigest(),'candidateSHA256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'nodeCount':len(a),'changedGeometry':changed,'changedStructure':structure,'changedExtras':extras,'materialDefinitionsExact':True,'unchangedGeometryCount':len(a)-len(changed),'preservation':'All other geometry, hierarchy, transforms and material definitions equal. No owner or marker transform changes permitted.'}
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
