import bpy,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
base,candidate,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists();root=Path(__file__).resolve().parents[4];code=(root/'scripts/validate-neck-guard-envelope.py').read_text();ns={'Vector':Vector,'intersect_ray_tri':intersect_ray_tri};exec(code[code.index('def inside('):code.index('def screen(')],ns);edge=ns['edge'];names=[f'V32 returned upper bill course {i}'for i in range(3)]+['V32 formed mandibular bowl'];models=[]
for label,path in [('baseline',base),('candidate',candidate)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));rows=[]
 for name in names:
  o=bpy.data.objects[name];m=o.data;m.calc_loop_triangles();v=[o.matrix_world@q.co for q in m.vertices];tri=[tuple(t.vertices)for t in m.loop_triangles];tree=BVHTree.FromPolygons(v,tri,all_triangles=True);count=0;first=None
  for a,b in tree.overlap(tree):
   if a>=b or set(tri[a])&set(tri[b]):continue
   ta=[v[i]for i in tri[a]];tb=[v[i]for i in tri[b]]
   if any(edge(ta[k],ta[(k+1)%3],tb)or edge(tb[k],tb[(k+1)%3],ta)for k in range(3)):
    count+=1
    if first is None:first={'triangleIndices':[a,b],'vertices':[tri[a],tri[b]],'actualNativeTriangles':[[list(p)for p in ta],[list(p)for p in tb]]}
  rows.append({'name':name,'nonAdjacentStrictTrianglePairCount':count,'firstWitness':first});print(label,name,count,flush=True)
 models.append({'model':label,'path':str(path),'meshes':rows})
out.write_text(json.dumps({'models':models,'predicate':'Unchanged strict1e-7 plane/1e-6 edge/bary; each nonadjacent triangle unordered pair once, actual all saved triangles of each of4changedmeshes','limits':['Shared-vertex adjacent triangles excluded; no containment, coplanar-overlap certification, penetration depth or continuous sweep.','A zero report is a bounded mesh diagnostic, not universal manifold/engineering/artistic acceptance.']},indent=2)+'\n')
