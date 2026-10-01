import bpy,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
ROOT=Path(__file__).resolve().parents[4];AUDIT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/models/whole-character-v38/breast-envelope02/murderbird-v38-breast-envelope02.blend'));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
def data(name):
 o=bpy.data.objects[name];e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(t.vertices)for t in m.loop_triangles];e.to_mesh_clear();return v,f,BVHTree.FromPolygons(v,f,all_triangles=True,epsilon=0)
d=json.loads((AUDIT/'surface-screen.json').read_text());records=[]
for scope in('frame','apparatus'):
 for r in d['neutral']['comparison'][scope]['newPairs']:
  av,af,at=data(r['changed']);bv,bf,bt=data(r['other']);points=[]
  for ia,ib in at.overlap(bt):
   a=[av[i]for i in af[ia]];b=[bv[i]for i in bf[ib]]
   for edges,tri in((a,b),(b,a)):
    for i in range(3):
     p,q=edges[i],edges[(i+1)%3];delta=q-p;hit=intersect_ray_tri(*tri,delta,p,True)
     if hit is not None and -1e-7<=(hit-p).dot(delta)/max(1e-20,delta.length_squared)<=1.0000001:points.append(hit)
  unique={tuple(round(x,8)for x in p)for p in points};records.append({'changed':r['changed'],'other':r['other'],'actualFiniteEdgeTriangleIntersectionWitnessesWorld':list(unique),'method':'Actual finite edge/triangle intersections on BVH-reported native evaluated triangle pairs; no penetration volume inferred'})
(AUDIT/'crossing-witnesses.json').write_text(json.dumps(records,indent=2)+'\n');print([(x['changed'],x['other'],len(x['actualFiniteEdgeTriangleIntersectionWitnessesWorld']))for x in records])
