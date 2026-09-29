from pathlib import Path
import bpy,json,hashlib,collections
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');P=ROOT/'assets/models/whole-character-v20/attempt-runtime02/murderbird-whole-character-v20.blend';EXPECTED='eb15a9d87de56fb8a06004d9c69448c38089f0ecacd888e3e7fde921a353d42a';assert hashlib.sha256(P.read_bytes()).hexdigest()==EXPECTED;bpy.ops.wm.open_mainfile(filepath=str(P));meshes=[];nodes=[]
for o in bpy.data.objects:
 if o.type=='EMPTY':nodes.append({'name':o.name,'parent':o.parent.name if o.parent else None,'world':[list(r) for r in o.matrix_world],'props':dict(o.items())})
 if o.type!='MESH':continue
 pts=[o.matrix_world@v.co for v in o.data.vertices];meshes.append({'name':o.name,'owner':o.parent.name if o.parent else None,'region':o.get('region'),'role':o.get('surfaceRole'),'eras':o.get('exteriorEras'),'vertices':len(pts),'bounds':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]})
r={'native':str(P.relative_to(ROOT)),'sha256':EXPECTED,'nodes':nodes,'meshes':meshes};(ROOT/'assets/audit/whole-character-v21/input/boundaries.json').write_text(json.dumps(r,indent=2))
for owner in ('neck','cervical-upper','breastplate','body'):
 group=[m for m in meshes if m['owner']==owner];print(owner,len(group),collections.Counter((m['region'],m['role']) for m in group))
 for m in group:
  if owner=='body':print(m['name'],m['region'],m['role'])
print('unchanged native',hashlib.sha256(P.read_bytes()).hexdigest()==EXPECTED)
