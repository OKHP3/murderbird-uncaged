"""Inspect existing GLBs only; no export or source/native changes."""
from pathlib import Path
import struct,json,hashlib,math,collections
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=ROOT/'assets/audit/whole-character-v20/attempt-runtime01/export-integrity'
FILES=[('v19',ROOT/'assets/models/whole-character-v19/attempt-02/murderbird-whole-character-v19.glb'),('runtime01',ROOT/'assets/models/whole-character-v20/attempt-runtime01/murderbird-whole-character-v20.glb')]
SIZE={5120:('b',1),5121:('B',1),5122:('h',2),5123:('H',2),5125:('I',4),5126:('f',4)};NUM={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
for label,path in FILES:
 raw=path.read_bytes();original=hashlib.sha256(raw).hexdigest();magic,version,size=struct.unpack_from('<4sII',raw);assert magic==b'glTF' and version==2 and size==len(raw)
 cursor=12;doc=None;binchunk=None
 while cursor<len(raw):
  n,t=struct.unpack_from('<II',raw,cursor);data=raw[cursor+8:cursor+8+n];assert len(data)==n
  if t==0x4E4F534A:doc=json.loads(data)
  if t==0x004E4942:binchunk=data
  cursor+=8+n
 def access(i):
  a=doc['accessors'][i];bv=doc['bufferViews'][a['bufferView']];f,n=SIZE[a['componentType']];width=NUM[a['type']];offset=bv.get('byteOffset',0)+a.get('byteOffset',0);stride=bv.get('byteStride',n*width)
  assert offset+(a['count']-1)*stride+n*width<=len(binchunk)
  assert not a.get('sparse');return [struct.unpack_from('<'+f*width,binchunk,offset+j*stride) for j in range(a['count'])]
 records=[];totals=collections.Counter()
 for i,m in enumerate(doc['meshes']):
  stats=collections.Counter();stats['primitives']=len(m['primitives']);parts=[];allpts=[];alltris=[]
  for pi,p in enumerate(m['primitives']):
   assert p.get('mode',4)==4;pos=access(p['attributes']['POSITION']);idx=[x[0] for x in access(p['indices'])] if 'indices' in p else list(range(len(pos)))
   assert len(idx)%3==0
   invalid=sum(j<0 or j>=len(pos) for j in idx);stats['outOfRangeIndices']+=invalid
   finitebad=sum(not all(math.isfinite(x) for x in q) for q in pos);stats['nonfinitePositionVertices']+=finitebad
   normal=access(p['attributes']['NORMAL']) if 'NORMAL' in p['attributes'] else []
   stats['nonfiniteNormalVertices']+=sum(not all(math.isfinite(x) for x in q) for q in normal)
   stats['zeroLengthNormalVertices']+=sum(dot(q,q)<=1e-20 for q in normal)
   deg=0;vol=0
   if not invalid:
    for t in zip(idx[::3],idx[1::3],idx[2::3]):
     a,b,c=[pos[x] for x in t];norm=cross(sub(b,a),sub(c,a))
     if dot(norm,norm)<=4e-28:deg+=1
     vol+=dot(a,cross(b,c))/6
   stats['triangles']+=len(idx)//3;stats['vertices']+=len(pos);stats['degenerateTrianglesAreaLE1e14']+=deg
   parts.append({'primitive':pi,'vertices':len(pos),'triangles':len(idx)//3,'degenerateTrianglesAreaLE1e14':deg,'signedVolumeOwnerLocalM3':vol,'attributes':list(p['attributes'])})
   start=len(allpts);allpts.extend(pos);alltris.extend(tuple(start+x for x in t) for t in zip(idx[::3],idx[1::3],idx[2::3]))
  rec={'meshIndex':i,'name':m.get('name'),'nodes':[n.get('name') for n in doc['nodes'] if n.get('mesh')==i],'counts':dict(stats),'primitives':parts}
  if any('breastplate-breast-plate'==n for n in rec['nodes']):
   # Weld only coincident glTF shading splits; coincident construction interfaces can
   # produce topological multiplicities and therefore do not prove running clearance.
   keys=[tuple(round(x,7) for x in p) for p in allpts];edges=collections.Counter();duplicate=collections.Counter()
   for t in alltris:
    k=[keys[x] for x in t];duplicate[tuple(sorted(k))]+=1
    for a,b in zip(k,k[1:]+k[:1]):edges[tuple(sorted((a,b)))]+=1
   rec['positionWeldedTopology1e7m']={'boundaryEdges':sum(n==1 for n in edges.values()),'edgesMoreThanTwoUses':sum(n>2 for n in edges.values()),'duplicateTriangleCopies':sum(n-1 for n in duplicate.values() if n>1),'limit':'Coincident construction interfaces may weld; not proof of finite solidity or clearance.'}
   rec['bounds']=[[min(q[j] for q in allpts),max(q[j] for q in allpts)] for j in range(3)]
  records.append(rec);totals.update(stats)
 out={'path':path.relative_to(ROOT).as_posix(),'sha256':original,'meshCount':len(records),'totals':dict(totals),'meshes':records,'sourceUnchanged':hashlib.sha256(path.read_bytes()).hexdigest()==original,'limits':['Inspects exported buffer and triangle integrity; does not prove source surface parity, visibility, motion, self-intersection or engineering acceptance.','Position-welded topology is approximate and can merge coincident independent construction pieces.']}
 (OUT/f'{label}-glb-integrity.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:out[k] for k in ('path','sha256','meshCount','totals','sourceUnchanged')}))
