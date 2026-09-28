"""Validate neutral correction source/export ownership without changing receipts."""
from pathlib import Path
import json,struct,hashlib,math
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/audit/neutral-v2';OUT.mkdir(parents=True,exist_ok=True)
inv=json.loads((ROOT/'assets/models/uncaged-neutral-v2/neutral-inventory.json').read_text())
checks=[]
for file in inv['generatedFiles']:
 p=ROOT/file['path'];raw=p.read_bytes();assert len(raw)==file['bytes'];assert hashlib.sha256(raw).hexdigest()==file['sha256'];assert not raw.startswith(b'version https://git-lfs')
checks.append('Native source, runtime and three explicit previews match recorded bytes/SHA; actual binaries')
p=ROOT/'assets/models/uncaged-neutral-v2/murderbird-neutral-v2.glb';data=p.read_bytes();assert data[:4]==b'glTF';length,kind=struct.unpack_from('<II',data,12);g=json.loads(data[20:20+length]);bo=20+length+8;binary=data[bo:]
assert struct.unpack_from('<I',data,8)[0]==len(data)
assert not g.get('skins');assert not g.get('images');assert not g.get('textures');assert not any(b.get('uri') for b in g.get('buffers',[]))
checks.append('Rigid neutral geometry; no skinning, texture maps or external buffers')
for a in g['accessors']:
 if a['componentType']!=5126:continue
 size={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];view=g['bufferViews'][a['bufferView']];offset=view.get('byteOffset',0)+a.get('byteOffset',0);stride=view.get('byteStride',size*4)
 for i in range(a['count']):assert all(math.isfinite(v) for v in struct.unpack_from('<'+'f'*size,binary,offset+i*stride))
checks.append('All float attributes finite')
nodes={n['name']:i for i,n in enumerate(g['nodes'])};parent={ch:i for i,n in enumerate(g['nodes']) for ch in n.get('children',[])}
for child,par in {'neck':'body','head':'neck','jaw':'head','upper-bill':'head','cranial-cover':'head','breastplate':'body','left-wing-shield':'left-mantle','right-wing-shield':'right-mantle'}.items():assert parent[nodes[child]]==nodes[par],child
for side in ['left','right']:
 for digit in [1,2,3]:
  name=f'{side}-digit-{digit}'
  assert parent[nodes[name+'-proximal']]==nodes[side+'-toes'];assert parent[nodes[name+'-distal']]==nodes[name+'-proximal']
checks.append('Opening panels, cervical/skull joints and 12 independent digit transforms retain one rigid owner')
late=[part for part in inv['parts'] if part['role']=='optic' or part['parent'] in ['processing','power-core','builder-optics']];assert late and all(p['eras']==['builder'] for p in late)
repair=[p for p in inv['parts'] if p['class']=='later-repair'];assert repair and all('maker' not in p['eras'] for p in repair)
checks.append('Earlier-era eligibility excludes powered lenses/processor/power and later repair')
original=json.loads((ROOT/'assets/models/uncaged-neutral-v2/reference-packet.json').read_text())
# The source packet may contain ancillary fields; verify every explicit file row.
refs=[]
def visit(v):
 if isinstance(v,dict):
  if isinstance(v.get('path'),str) and v.get('sha256') and (ROOT/v['path']).is_file():
   actual=hashlib.sha256((ROOT/v['path']).read_bytes()).hexdigest();assert actual==v['sha256'],v['path'];refs.append(v['path'])
  for item in v.values():visit(item)
 elif isinstance(v,list):
  for item in v:visit(item)
visit(original);assert refs
checks.append(f'{len(set(refs))} source packet file hashes remain unchanged')
triangles=sum(g['accessors'][primitive['indices']]['count']//3 for mesh in g['meshes'] for primitive in mesh['primitives'])
report={'status':'passed','modelSha256':hashlib.sha256(data).hexdigest(),'modelBytes':len(data),'nodes':len(g['nodes']),'meshes':len(g['meshes']),'triangles':triangles,'editableParts':len(inv['parts']),'checks':checks,'limits':'No artistic, swept collision, physical balance or final surface certification'}
(OUT/'asset-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
