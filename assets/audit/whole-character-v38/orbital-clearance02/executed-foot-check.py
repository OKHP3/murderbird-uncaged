"""Read-only actual saved full receiving footprint check; no strict predicate changes."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
model,receipt,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(model));d=json.loads(receipt.read_text());rows=[]
def tree(o):
 o.data.calc_loop_triangles();p=[o.matrix_world@v.co for v in o.data.vertices];return p,BVHTree.FromPolygons(p,[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True)
def bary(p,t):
 a,b,c=t;u=b-a;v=c-a;q=p-a;uu=u.dot(u);uv=u.dot(v);vv=v.dot(v);qu=q.dot(u);qv=q.dot(v);den=uu*vv-uv*uv;return [(vv*qu-uv*qv)/den,(uu*qv-uv*qu)/den]
for r in d['contract']['integralReceivingReturns']:
 receiver=bpy.data.objects[r['receiver']];shield=bpy.data.objects[r['shield']];rp,rt=tree(receiver);sp,st=tree(shield);plane=[];mins=[];receiving=[];saved=[];norm=[]
 for foot in r['actualMatchedFootTriangles']:
  original=receiver.data.loop_triangles[foot['receiverTriangleIndex']];actual=[rp[k]for k in original.vertices];assert all((a-Vector(b)).length<1e-7for a,b in zip(actual,foot['receiverTriangle']));tri=[Vector(q)for q in foot['footTriangle']];n=(actual[1]-actual[0]).cross(actual[2]-actual[0]).normalized();fn=(tri[1]-tri[0]).cross(tri[2]-tri[0]).normalized();norm.append(abs(n.dot(fn)))
  for p in tri+[sum(tri,Vector())/3]+[(tri[j]+tri[(j+1)%3])*.5for j in range(3)]:
   plane.append(abs((p-actual[0]).dot(n)));u,v=bary(p,actual);mins.append(min(u,v,1-u-v));receiving.append(rt.find_nearest(p)[3]);saved.append(st.find_nearest(p)[3])
 rows.append({'shield':shield.name,'receiver':receiver.name,'actualFullPatchTriangles':len(r['actualMatchedFootTriangles']),'fullFootAreaYZM2':r['footAreaYZM2'],'actualYZExtentM':r['footYZExtentM'],'returnSpanRangeM':r['returnSpanRangeM'],'actualReceiverTrianglesExact':True,'cornerEdgeCentroidSamples':len(plane),'maximumReceivingPlaneDistanceM':max(plane),'minimumInsideTriangleBarycentric':min(mins),'minimumAbsoluteFootReceiverNormalDot':min(norm),'maximumActualReceiverNearestGapM':max(receiving),'maximumSavedShieldNearestGapM':max(saved),'limits':'Full original receiving triangle/foot facet correspondence plus corners/edge/centroid; finite patch size recorded. Float barycentric seam errors remain disclosed. Strict receiving-edge crossings and inherited interfaces are not waived; no load/engineering or continuous-motion approval.'})
out.write_text(json.dumps({'status':'Bounded actual finite full-foot evidence; assembly HOLD remains','rows':rows,'attachmentMotion':'Both parts remain head-owned with exact matrices; same relative footprint across jaw/neck/crown-inspection poses. Fixed/moving neighbor interfaces are separately screened.'},indent=2)+'\n');print(rows)
