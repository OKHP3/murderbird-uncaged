import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
model,out,version=sys.argv[sys.argv.index('--')+1:];model=Path(model);out=Path(out);assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(model));rows=[]
intervals=[(2,40),(32,67),(59,91)]if version=='01'else[(2,43),(58,90),(91,96)]
def key(points):return tuple(sorted(tuple(round(x,6)for x in p)for p in points))
for side in(-1,1):
 wall=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];m=wall.data;m.calc_loop_triangles();wp=[wall.matrix_world@v.co for v in m.vertices];wt=[tuple(t.vertices)for t in m.loop_triangles];tree=BVHTree.FromPolygons(wp,wt,all_triangles=True);wallkeys={key([wp[i]for i in t])for t in wt}
 for course,(lo,hi)in enumerate(intervals):
  o=bpy.data.objects[f'V38 optic cheek shield {side} {course}'];mesh=o.data;mesh.calc_loop_triangles();pts=[o.matrix_world@v.co for v in mesh.vertices];half=len(pts)//2;nu=hi-lo
  for end,rs in [('upper',set(range(3))),('lower',set(range(nu-2,nu+1)))]:
   indices={half+r*9+c for r in rs for c in range(9)};samples=[pts[i]for i in sorted(indices)];tri=[tuple(t.vertices)for t in mesh.loop_triangles if set(t.vertices)<=indices];matches=sum(key([pts[i]for i in t])in wallkeys for t in tri);perimeter=[]
   for a,b in zip(sorted(indices),sorted(indices)[1:]):
    if a//9==b//9:perimeter.append((pts[a]+pts[b])*.5)
   for c in(0,8):
    for r in range(min(rs),max(rs)):perimeter.append((pts[half+r*9+c]+pts[half+(r+1)*9+c])*.5)
   distances=[tree.find_nearest(p)[3]for p in samples+perimeter];rows.append({'part':o.name,'end':end,'target':wall.name,'actualFootVertices':len(samples),'perimeterMidpointSamples':len(perimeter),'innerFootActualTriangles':len(tri),'actualTriangleCoordinateKeysMatchedAt1Micrometre':matches,'finiteSurfaceGapMinMaxM':[min(distances),max(distances)],'wallRowRange':[lo+min(rs),lo+max(rs)],'normals':[list(tree.find_nearest(p)[1])for p in(samples[0],samples[-1])],'limits':'Rounded triangle-coordinate correspondence plus actual vertex/perimeter surface distances; not exact manufacturing/depth/load proof, full interobject screen takes priority'})
 for i in range(3):
  o=bpy.data.objects[f'V31 temporal fitting root {side} {i}'];pts=[o.matrix_world@v.co for v in o.data.vertices];xmin=min(abs(p.x)for p in pts);foot=[p for p in pts if abs(abs(p.x)-xmin)<1e-6];dist=[tree.find_nearest(p)[3]for p in foot];rows.append({'sourceFitting':o.name,'target':wall.name,'actualReturnSectionVertices':len(foot),'finiteReturnToWallDistanceMinMaxM':[min(dist),max(dist)],'returnSectionActualBounds':[[min(p[k]for p in foot),max(p[k]for p in foot)]for k in range(3)],'limits':'Actual fixed source return vertices vs reconstructed wall; not a seated-bearing/load-path acceptance. Strict source/new intersections remain disclosed.'})
out.write_text(json.dumps({'model':str(model),'records':rows,'browInterface':'No finite integral posterior brow descent was authored; closer crown/wall placement is unproven receiving proposal. Unsupported appearance remains visual HOLD.','limits':'All real optic/jaw/socket/cover/bill geometry unchanged. These local seat measurements do not waive cross-part crossings or establish full assembly/sweep acceptance.'},indent=2)+'\n')
