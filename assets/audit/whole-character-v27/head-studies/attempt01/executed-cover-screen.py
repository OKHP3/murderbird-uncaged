from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
OUT=Path('/tmp/v27-cranial-wrap/attempt01');NATIVE=OUT/'cranial-wrap.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bound=sha(NATIVE);r=json.loads((OUT/'receipt.json').read_text());assert r['nativeSHA256']==bound
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));bpy.context.view_layer.update()
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
rest=bpy.data.objects['jaw'].rotation_euler.copy()
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

cover=bpy.data.objects['cranial-cover'];coverrest=cover.location.copy();poses=[]
for amount in [0,.02,.04,.06,.08]:
 cover.location=coverrest;cover.location.z+=amount;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();items=[mesh(o,dg) for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name in ['jaw','head','upper-bill','cranial-cover','builder-optics']];moving={o.name for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name=='cranial-cover'};pairs=[]
 for a in items:
  if a[0] not in moving:continue
  for b in items:
   if b[0] in moving:continue
   strict=[]
   for ia,ib in a[3].overlap(b[3]):
    A=[a[1][i] for i in a[2][ia]];B=[b[1][i] for i in b[2][ib]]
    if any(edge(A[k],A[(k+1)%3],B) or edge(B[k],B[(k+1)%3],A) for k in range(3)):strict.append((ia,ib))
   if strict:pairs.append({'cover':a[0],'neighbor':b[0],'trianglePairs':len(strict),'firstTrianglePair':list(strict[0])})
 poses.append({'cranialLocalNativeZDelta':amount,'strictPairCount':len(pairs),'pairs':pairs})
assert sha(NATIVE)==bound
out={'nativeSHA256':bound,'headSourceSHA256':r['sourceSHA256'],'screenSHA256':sha(Path(__file__)),'method':'Evaluated native triangle edge-through-face strict interior crossing; 1e-7m plane epsilon,barycentric1e-6. Every cranial-cover mesh vs other head-subtree meshes. Five vertical cover opening translations0..80mm only; not continuous clearance.','poses':poses}
(OUT/'cover-screen.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
