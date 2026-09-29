import bpy,bmesh,json,runpy,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A=Path(__file__).resolve().parent;R=Path.cwd();receipt=json.loads((A/'receipt.json').read_text());base=R/receipt['native']['path']
s=(A/'executed-strict-foot-motion-screen.py').read_text();scope={};exec(s.split('def screen(')[0].split('def inside(')[1].join(['def inside(', '']) if False else 'def inside('+s.split('def inside(')[1].split('def screen(')[0],{'math':math,'intersect_ray_tri':__import__('mathutils.geometry',fromlist=['intersect_ray_tri']).intersect_ray_tri},scope)
# Bind shared helper for the unchanged strict crossing kernel.
scope['edge'].__globals__['inside']=scope['inside'];edge=scope['edge']
bpy.ops.wm.open_mainfile(filepath=str(base));bpy.context.view_layer.update();results=[]
for name in receipt['result']['receivingSeatRevision']['changedMeshes']:
 o=bpy.data.objects[name];m=o.data;m.calc_loop_triangles();vertices=[o.matrix_world@v.co for v in m.vertices]
 adjacent={i:set() for i in range(len(m.vertices))}
 for e in m.edges:a,b=e.vertices;adjacent[a].add(b);adjacent[b].add(a)
 unseen=set(adjacent);comps=[]
 while unseen:
  stack=[unseen.pop()];component=set(stack)
  while stack:
   for j in adjacent[stack.pop()]&unseen:unseen.remove(j);component.add(j);stack.append(j)
  comps.append(component)
 items=[]
 for comp in comps:
  tri=[tuple(t.vertices) for t in m.loop_triangles if t.vertices[0] in comp];items.append((comp,tri,BVHTree.FromPolygons(vertices,tri,all_triangles=True)))
 links=[];graph={i:set() for i in range(len(items))}
 for i,x in enumerate(items):
  for j,y in enumerate(items[i+1:],i+1):
   method=None
   for tx,ty in x[2].overlap(y[2]):
    a=[vertices[k] for k in x[1][tx]];b=[vertices[k] for k in y[1][ty]]
    if any(edge(a[k],a[(k+1)%3],b) or edge(b[k],b[(k+1)%3],a) for k in range(3)):method='strict stock-surface crossing: positive fabrication overlap';break
   if method is None:
    shared=[]
    for ix in x[0]:
     if any((vertices[ix]-vertices[iy]).length<1e-8 for iy in y[0]):shared.append(vertices[ix])
    if len(shared)>=3 and any((shared[i]-shared[0]).cross(shared[j]-shared[0]).length>1e-10 for i in range(1,len(shared)) for j in range(i+1,len(shared))):method='at least three coincident noncollinear stock vertices: fixed face/edge contact'
   if method:links.append({'componentA':i,'componentB':j,'method':method});graph[i].add(j);graph[j].add(i)
 visited={0};stack=[0]
 while stack:
  for j in graph[stack.pop()]-visited:visited.add(j);stack.append(j)
 results.append({'name':name,'stockComponents':len(items),'fixedContactGraphConnected':len(visited)==len(items),'reachableComponents':sorted(visited),'contactEdges':links,'interpretation':'Union/contact graph of closed proposed fabrication stock, not Boolean union, watertight single-body topology or engineering certification.'})
# Curves retain historical geometry/props; moved-node children may relocate only.
h=runpy.run_path(str(R/'scripts/build-uncaged-alignment-v7.py'));after=h['scene_snapshot']();bpy.ops.wm.open_mainfile(filepath=str(R/receipt['base']['path']));before=h['scene_snapshot']()
curves=[]
for n,v in before['curves'].items():
 if after['curves'][n]!=v:
  same={k:v[k] for k in v if k!='matrix'}=={k:after['curves'][n][k] for k in v if k!='matrix'};assert same,n;curves.append(n)
with (A/'connected-stock-and-curves.json').open('x') as f:json.dump({'stockResults':results,'changedCurvesMatrixOnly':curves,'allCurveLocalGeometryPropertiesIdentityExact':True,'allStockContactGraphsConnected':all(q['fixedContactGraphConnected'] for q in results),'limits':['Positive stock overlap/contact means the conceptual solid union is connected; independent stocks remain distinct closed surfaces in one fixed part.','Internal stock surfaces/self-intersections have not been Boolean-unioned; no manufactured-body topology or strength claim.']},f,indent=2)
print(json.dumps([(r['name'],r['stockComponents'],r['fixedContactGraphConnected']) for r in results]));print('changed curves',curves)
