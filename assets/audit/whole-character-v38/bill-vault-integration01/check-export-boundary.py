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
scope=json.loads(Path(sys.argv[4]).read_text())
removed=sorted(a.keys()-b.keys());added=sorted(b.keys()-a.keys());common=a.keys()&b.keys()
assert set(removed)==set(scope.get('removed',[])),removed
assert set(added)==set(scope.get('added',[])),added
assert removed == [], removed
assert added == [], added
assert {m['name']:m for m in bd['materials']}=={m['name']:m for m in cd['materials']},'Materials changed'
changed=sorted(n for n in common if a[n]['geometry']!=b[n]['geometry']);allowed=scope['changed'];assert set(changed)==set(allowed),(changed,allowed)
assert set(changed)=={f'V32 returned upper bill course {i}' for i in range(3)},changed
structure=sorted(n for n in common if a[n]['structure']!=b[n]['structure'] or a[n]['parent']!=b[n]['parent']);assert set(structure)<= {'bill-contact'},structure
for n in structure:
 assert a[n]['parent']==b[n]['parent']
 assert {k:v for k,v in a[n]['structure'].items() if k!='translation'}=={k:v for k,v in b[n]['structure'].items() if k!='translation'}
extras=sorted(n for n in common if a[n]['extras']!=b[n]['extras']);assert set(extras)<=set(allowed),extras
for n in extras:
 delta={k for k in a[n]['extras'].keys()|b[n]['extras'].keys() if a[n]['extras'].get(k)!=b[n]['extras'].get(k)}
 assert delta<=set(scope.get('allowedExtras',{}).get(n,[])),(n,delta)
 assert not delta & {'exteriorEras','era','eras','mechanism','role','partId'},(n,delta)
result={'status':'PASS','scope':'Actual exported geometry, material definitions, hierarchy and local transforms. No motion, collision, strength or likeness claim.','source':str(base),'candidate':str(candidate),'sourceSHA256':hashlib.sha256(base.read_bytes()).hexdigest(),'candidateSHA256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'sourceNodeCount':len(a),'candidateNodeCount':len(b),'removedNodes':removed,'addedNodes':added,'changedGeometry':changed,'changedStructure':structure,'changedExtras':extras,'materialDefinitionsExact':True,'unchangedGeometryCount':len(common)-len(changed),'preservation':'All other geometry, hierarchy, transforms, metadata and material definitions equal. Only a documented bill-contact translation is allowed; no owner transform changes.'}
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
