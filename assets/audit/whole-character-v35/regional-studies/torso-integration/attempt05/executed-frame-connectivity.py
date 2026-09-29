from pathlib import Path
import bpy,bmesh,json,hashlib
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');A=Path(__file__).parent;N=R/'assets/models/whole-character-v35/regional-studies/torso-integration/attempt05/murderbird-torso-integration.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(N)=='2589ea9bef35caa5b65cbae3edddec856422f8f4729df0e8ec38b373d2136857';bpy.ops.wm.open_mainfile(filepath=str(N));rows=[]
for o in bpy.data.objects:
 if o.type!='MESH' or not o.name.startswith(('V35 lateral thoracic bay load rail','V35 posterior bay load rail')):continue
 bm=bmesh.new();bm.from_mesh(o.data);todo=set(bm.verts);components=[]
 while todo:
  q=[todo.pop()];group=[]
  while q:
   v=q.pop();group.append(v)
   for e in v.link_edges:
    n=e.other_vert(v)
    if n in todo:todo.remove(n);q.append(n)
  components.append({'vertices':len(group),'bounds':[[min((o.matrix_world@v.co)[k] for v in group),max((o.matrix_world@v.co)[k] for v in group)] for k in range(3)]})
 rows.append({'name':o.name,'owner':o.parent.name,'components':components,'componentCount':len(components),'closed':all(e.is_manifold for e in bm.edges),'positiveVolumeM3':bm.calc_volume(signed=True)});bm.free()
assert len(rows)==4
(A/'frame-connectivity.json').write_text(json.dumps({'nativeSHA256':sha(N),'executedSourceSHA256':sha(Path(__file__)),'method':'Read-only edge-connected components and finite closed positive raw solids; actual same-body rib receiving surfaces in module/strictpacket; no force/physics claim','rails':rows,'allFourRailsSingleConnectedSolid':all(r['componentCount']==1 and r['closed'] and r['positiveVolumeM3']>0 for r in rows),'nativeUnchanged':sha(N)=='2589ea9bef35caa5b65cbae3edddec856422f8f4729df0e8ec38b373d2136857'},indent=2)+'\n');print([(r['name'],r['componentCount']) for r in rows])
