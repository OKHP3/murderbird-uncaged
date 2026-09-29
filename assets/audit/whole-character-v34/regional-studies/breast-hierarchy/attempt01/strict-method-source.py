from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
OUT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/audit/whole-character-v29/attempt-fit01/hinge-screen');NATIVE=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/whole-character-v29/attempt-fit01/murderbird-whole-character-v29.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads(Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/audit/whole-character-v29/regional-studies/breast-hinge/attempt02/receipt.json').read_text());bound=sha(NATIVE);assert bound=='04040543c39e98dd3d20da3d51a5ba40fd87151315ef074d328276eed97c63e7';bpy.ops.wm.open_mainfile(filepath=str(NATIVE));bpy.context.view_layer.update()
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
def inside(p,tri):
 a,b,c=tri;v0=b-a;v1=c-a;v2=p-a;d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);d20=v2.dot(v0);d21=v2.dot(v1);den=d00*d11-d01*d01
 if abs(den)<1e-18:return False
 u=(d11*d20-d01*d21)/den;v=(d00*d21-d01*d20)/den;return min(u,v,1-u-v)>1e-6
def edge(p,q,tri):
 n=(tri[1]-tri[0]).cross(tri[2]-tri[0])
 if n.length<1e-12:return False
 n.normalize();d0=n.dot(p-tri[0]);d1=n.dot(q-tri[0])
 if not(d0*d1<0 and abs(d0)>1e-7 and abs(d1)>1e-7):return False
 direction=q-p;hit=intersect_ray_tri(*tri,direction,p,True)
 if hit is None:return False
 t=(hit-p).dot(direction)/max(direction.length_squared,1e-30);return 1e-6<t<1-1e-6 and inside(hit,tri)
def mesh(o,dg):
 ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@x.co for x in m.vertices];t=[tuple(f.vertices) for f in m.loop_triangles];ev.to_mesh_clear();return (o.name,v,t,BVHTree.FromPolygons(v,t,all_triangles=True))



rest=bpy.data.objects['breastplate'].rotation_euler.copy();hinge=set(r['result']['changedMeshes']+r['result']['added']+['V23 breast opening captive shaft']);poses=[]
for angle in [0,.275,.55,.825,1.1]:
 bpy.data.objects['breastplate'].rotation_euler=rest;bpy.data.objects['breastplate'].rotation_euler.x+=angle;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();sources=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name=='breastplate'];targets=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name in ['body','neck','cervical-mid-a','cervical-mid-b','cervical-upper','left-mantle','right-mantle','left-wing-shield','right-wing-shield','left-thigh','right-thigh']];items={o.name:mesh(o,dg) for o in sources+targets};pairs=[]
 for oa in sources:
  a=items[oa.name]
  for ob in targets:
   b=items[ob.name];strict=[]
   for ia,ib in a[3].overlap(b[3]):
    A=[a[1][i] for i in a[2][ia]];B=[b[1][i] for i in b[2][ib]]
    if any(edge(A[k],A[(k+1)%3],B) or edge(B[k],B[(k+1)%3],A) for k in range(3)):strict.append((ia,ib))
   if strict:
    ia,ib=strict[0];w=sum([a[1][i] for i in a[2][ia]]+[b[1][i] for i in b[2][ib]],Vector())/6;pairs.append({'source':a[0],'neighbor':b[0],'owners':[oa.parent.name,ob.parent.name],'hingeInvolved':a[0] in hinge or b[0] in hinge,'trianglePairs':len(strict),'firstPairCentroidNative':list(w)})
 poses.append({'breastLocalXDelta':angle,'movingSourceMeshes':len(sources),'fixedAdjacentMeshes':len(targets),'strictPairCount':len(pairs),'hingeStrictPairs':sum(p['hingeInvolved'] for p in pairs),'pairs':pairs});print(angle,len(pairs),sum(p['hingeInvolved'] for p in pairs),flush=True)
(OUT/'opening-screen.json').write_text(json.dumps({'nativeSHA256':bound,'sourceSHA256':r['sourceSHA256'],'screenSHA256':sha(Path(__file__)),'method':'Evaluated triangle edge through triangle strict interior test,1e-7m planeepsilon/barycentric1e-6. Entire breastplate including hinge/shaft vs body,neck/upper,wing/thigh adjacencies atfiveXopenstates. Counts not penetrationdepth; no continuous or containment clearance claim.','poses':poses},indent=2)+'\n');assert sha(NATIVE)==bound
