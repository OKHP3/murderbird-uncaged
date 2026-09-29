import json,struct,math,hashlib
from pathlib import Path
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=ROOT/'assets/audit/whole-character-v20/attempt-runtime01/export-integrity';results=[]
for label,path in [('v19',ROOT/'assets/models/whole-character-v19/attempt-02/murderbird-whole-character-v19.glb'),('runtime01',ROOT/'assets/models/whole-character-v20/attempt-runtime01/murderbird-whole-character-v20.glb')]:
 raw=path.read_bytes();jn=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+jn]);bn=20+jn;length,typ=struct.unpack_from('<II',raw,bn);b=raw[bn+8:bn+8+length]
 def array(i):
  a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];fmt,s={5126:('f',4),5125:('I',4),5123:('H',2)}[a['componentType']];w={'VEC3':3,'SCALAR':1}[a['type']];offset=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',s*w);return [struct.unpack_from('<'+fmt*w,b,offset+n*stride) for n in range(a['count'])]
 node=next(n for n in j['nodes'] if n.get('name')=='breastplate-breast-plate');mesh=j['meshes'][node['mesh']];p=mesh['primitives'][0];pos=array(p['attributes']['POSITION']);ix=[x[0] for x in array(p['indices'])];zeros={i for i,x in enumerate(pos) if sum(a*a for a in x)<1e-20};tris=[]
 for ti,t in enumerate(zip(ix[::3],ix[1::3],ix[2::3])):
  if not any(i in zeros for i in t):continue
  pts=[pos[i] for i in t];longest=max(math.dist(a,c) for a,c in zip(pts,pts[1:]+pts[:1]));tris.append({'triangle':ti,'indices':t,'longestEdgeM':longest,'positions':pts})
 results.append({'label':label,'sha256':hashlib.sha256(raw).hexdigest(),'mergedNode':node['name'],'originVertexIndices':sorted(zeros),'incidentTriangleCount':len(tris),'triangles':tris,'caveat':'Origin incidences are consistent with validated NaN vertices; explicit stage evidence establishes two coordinates were reset to this group origin.'})
(OUT/'exported-origin-triangles.json').write_text(json.dumps(results,indent=2));print(json.dumps([{k:v for k,v in r.items() if k!='triangles'} for r in results],indent=2))
