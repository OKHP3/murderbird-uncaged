"""Read-only finite cover join adjunct: topology/components and actual same-owner pairs.
Uses unchanged strict triangle predicate; no full fit certificate.
"""
import bpy,bmesh,json,sys,runpy,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[4]
base,candidate,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists()
code=(ROOT/'scripts/validate-neck-guard-envelope.py').read_text();ns={'Vector':Vector,'intersect_ray_tri':intersect_ray_tri};exec(code[code.index('def inside('):code.index('def screen(')],ns);edge=ns['edge']
selected={f'V34 formed breast course {r} plate {i}'for r,n in [(1,5),(2,6)]for i in range(1,n+1)}|{'V30 continuous tapered breast liner'}
reports=[]
for label,path in [('baseline',base),('candidate',candidate)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));items=[];topology=[]
 for o in bpy.data.objects:
  if o.type!='MESH'or not o.parent or o.parent.name!='breastplate':continue
  m=o.data;m.calc_loop_triangles();v=[o.matrix_world@q.co for q in m.vertices];t=[tuple(q.vertices)for q in m.loop_triangles];tree=BVHTree.FromPolygons(v,t,all_triangles=True);items.append((o.name,v,t,tree))
  if o.name in selected:
   adj={i:set()for i in range(len(m.vertices))}
   for e in m.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
   todo=set(adj);components=[]
   while todo:
    stack=[todo.pop()];count=0
    while stack:
     i=stack.pop();count+=1
     for j in adj[i]&todo:todo.remove(j);stack.append(j)
    components.append(count)
   bm=bmesh.new();bm.from_mesh(m);closed=all(e.is_manifold for e in bm.edges);vol=abs(bm.calc_volume(signed=True));bm.free();topology.append({'name':o.name,'closedEdgeManifold':closed,'signedAbsoluteVolumeM3':vol,'finiteConnectedComponentVertexCounts':sorted(components),'receivingStockM':o.get('wallM')})
 rows=[]
 for i,a in enumerate(items):
  for b in items[i+1:]:
   if not(a[0]in selected or b[0]in selected):continue
   for ia,ib in a[3].overlap(b[3]):
    ta=[a[1][j]for j in a[2][ia]];tb=[b[1][j]for j in b[2][ib]]
    if any(edge(ta[k],ta[(k+1)%3],tb)or edge(tb[k],tb[(k+1)%3],ta)for k in range(3)):
     rows.append({'a':a[0],'b':b[0],'firstTrianglePair':[ia,ib],'witnessTriangles':[[list(p)for p in ta],[list(p)for p in tb]]});break
 reports.append({'label':label,'nativeSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'selected12Topology':topology,'sameCoverStrictPairs':rows})
key=lambda p:tuple(sorted((p['a'],p['b'])))
a={key(p)for p in reports[0]['sameCoverStrictPairs']};b={key(p)for p in reports[1]['sameCoverStrictPairs']}
out.write_text(json.dumps({'status':'Same-owner finite support/lap adjunct; inspect crossings, not construction acceptance','reports':reports,'delta':{'sourcePairs':len(a),'candidatePairs':len(b),'introducedPairs':sorted(b-a),'retainedPairs':sorted(b&a),'removedPairs':sorted(a-b)},'limits':['Rest only, all breastplate finite neighbors and12 reconstructed candidates selected. Separate union40 fullpool screen covers5inspection opens/otherowners/receiver adjunct.','Finite Boolean union connectivity/closure and nominal15mm longitudinal lap do not prove continuous stock or welded support. Strict crossing witnesses are recorded including intended joints, not silently waived.','No physicalload/manufacturing/containment/deformation proof.']},indent=2)+'\n')
