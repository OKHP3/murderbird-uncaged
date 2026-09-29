from pathlib import Path
import bpy,bmesh,json,hashlib,math
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).parent;NATIVE=OUT/'orbital-construction.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();BOUND=json.loads((OUT/'receipt.json').read_text())['nativeSHA256'];assert sha(NATIVE)==BOUND;bpy.ops.wm.open_mainfile(filepath=str(NATIVE));bpy.context.view_layer.update()
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
rest={n:bpy.data.objects[n].matrix_basis.copy() for n in ('jaw','cranial-cover')}
def pose(jaw=0,cap=0):
 for n,m in rest.items():bpy.data.objects[n].matrix_basis=m
 bpy.data.objects['jaw'].rotation_euler.x+=jaw;bpy.data.objects['cranial-cover'].location.z+=cap;bpy.context.view_layer.update()
s=(OUT/'executed-strict-kernel.py').read_text();exec(s[s.index('def inside'):s.index('poses=[]')])
def headmesh(o):
 p=o.parent
 while p:
  if p.name=='head':return True
  p=p.parent
 return False
os=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and headmesh(o)];owners={o.name:o.parent.name for o in os};rows=[]
for kind,delta in [('jaw',0),('jaw',.08),('jaw',.16),('jaw',.24),('jaw',.32),('cap',0),('cap',.08)]:
 pose(delta if kind=='jaw' else 0,delta if kind=='cap' else 0);dg=bpy.context.evaluated_depsgraph_get();items=[mesh(o,dg) for o in os];active={o.name for o in os if o.parent.name==('jaw' if kind=='jaw' else 'cranial-cover')};pairs=[]
 for a in items:
  if a[0] not in active:continue
  for b in items:
   if b[0] in active or owners[a[0]]==owners[b[0]]:continue
   hits=0;first=None
   for ia,ib in a[3].overlap(b[3]):
    A=[a[1][i] for i in a[2][ia]];B=[b[1][i] for i in b[2][ib]]
    if any(edge(A[k],A[(k+1)%3],B) or edge(B[k],B[(k+1)%3],A) for k in range(3)):
     hits+=1
     if first is None:first={'indices':[ia,ib],'activeTriangle':[list(x) for x in A],'neighborTriangle':[list(x) for x in B],'centroid':list(sum(A+B,Vector())/6)}
   if hits:pairs.append({'active':a[0],'neighbor':b[0],'owners':[owners[a[0]],owners[b[0]]],'strictTrianglePairs':hits,'firstWitness':first})
  
 rows.append({'pose':kind,'delta':delta,'strictPairCount':len(pairs),'pairs':pairs});print(kind,delta,len(pairs),flush=True)
 (OUT/'screen.json').write_text(json.dumps({'nativeSHA256':BOUND,'executedScreenSHA256':sha(Path(__file__)),'kernelSHA256':sha(OUT/'executed-strict-kernel.py'),'allHeadMeshes':len(os),'meshNames':sorted(owners),'method':'Dynamic head-subtree meshes; active jaw/cap vs every other head-subtree rigid owner. Evaluated BVH strict edge-through-face crossings,1e-7 plane epsilon,1e-6 edge/barycentric margin. Tangencies/coplanar/contained and same-owner contacts excluded. Seven discrete poses, not continuous physics clearance.','poses':rows},indent=2)+'\n')
assert sha(NATIVE)==BOUND
print('COMPLETE',flush=True)

pose();dg=bpy.context.evaluated_depsgraph_get();finite=[]
for name in json.loads((OUT/'receipt.json').read_text())['result']['added']:
 o=bpy.data.objects[name];ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(m);finite.append({'name':name,'owner':o.parent.name,'nonFinite':sum(not math.isfinite(c) for v in m.vertices for c in v.co),'degenerateTriangles':sum((m.vertices[t.vertices[1]].co-m.vertices[t.vertices[0]].co).cross(m.vertices[t.vertices[2]].co-m.vertices[t.vertices[0]].co).length<1e-12 for t in m.loop_triangles),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'volumeM3':bm.calc_volume(signed=True),'exteriorEras':o.get('exteriorEras')});bm.free();ev.to_mesh_clear()
(OUT/'finite.json').write_text(json.dumps({'nativeSHA256':BOUND,'sourceSHA256':sha(Path(__file__)),'items':finite},indent=2)+'\n');print('finite failures',[x for x in finite if x['nonFinite'] or x['degenerateTriangles'] or x['nonManifoldEdges'] or x['volumeM3']<=0],flush=True)
