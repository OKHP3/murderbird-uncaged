import bpy,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
model,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists();root=Path(__file__).resolve().parents[4];code=(root/'scripts/validate-neck-guard-envelope.py').read_text();ns={'Vector':Vector,'intersect_ray_tri':intersect_ray_tri};exec(code[code.index('def inside('):code.index('def screen(')],ns);edge=ns['edge'];bpy.ops.wm.open_mainfile(filepath=str(model));o=bpy.data.objects['V32 returned upper bill course 2'];m=o.data;m.calc_loop_triangles();v=[o.matrix_world@q.co for q in m.vertices];tri=[tuple(t.vertices)for t in m.loop_triangles];tree=BVHTree.FromPolygons(v,tri,all_triangles=True);w=[];count=0
for a,b in tree.overlap(tree):
 if a>=b or set(tri[a])&set(tri[b]):continue
 ta=[v[i]for i in tri[a]];tb=[v[i]for i in tri[b]]
 if min(p.z for p in ta+tb)>1.58:continue
 if any(edge(ta[k],ta[(k+1)%3],tb)or edge(tb[k],tb[(k+1)%3],ta)for k in range(3)):
  count+=1
  if len(w)<12:w.append({'triangles':[a,b],'indices':[tri[a],tri[b]],'actualNativeXYZ':[[list(p)for p in ta],[list(p)for p in tb]]})
# Adjacent longitudinal inner stock field jump measures actual saved points, not art image attribution.
cols=48;half=49*cols;jumps=[]
for r in range(48):
 for c in range(cols):
  a=r*cols+c;b=(r+1)*cols+c;va=v[a+half]-v[a];vb=v[b+half]-v[b]
  if va.dot(vb)<0:jumps.append({'rows':[r,r+1],'column':c,'outerPoints':[list(v[a]),list(v[b])],'stockDirections':[list(va),list(vb)]})
out.write_text(json.dumps({'model':str(model),'actualObject':o.name,'nonAdjacentStrictTipTriangleCrossings':count,'firstWitnesses':w,'actualAdjacentStockDirectionSignReversals':jumps,'limits':'Same strict edge predicate, actual saved course2 triangles, skips shared vertices and upper non-tip pairs. Hidden/self crossings are not covered by interobject screen. No containment/depth/full solid certificate.'},indent=2)+'\n')
print('TIPSELF',count,'STOCK_SIGN_REVERSE',len(jumps),flush=True)
