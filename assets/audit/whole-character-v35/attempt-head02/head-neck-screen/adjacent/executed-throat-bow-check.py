from pathlib import Path
import bpy,hashlib,json
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).parent
NATIVE=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/whole-character-v35/attempt-head02/murderbird-whole-character-v35.blend')
BOUND='eb2e121af642d0620f062da4c3ecf11d0fbce121fef1f62f29d9b2c53f537d94'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(NATIVE)==BOUND
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));bpy.context.view_layer.update()
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
cover=bpy.data.objects['cranial-cover'];rest=cover.matrix_basis.copy()
kernel=(OUT.parent/'head'/'executed-strict-kernel.py').read_text()
exec(kernel[kernel.index('def inside'):kernel.index('poses=[]')],globals())
cheeks=sorted([o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('V33 tapered throat cheek plate')],key=lambda o:o.name)
bows=sorted([o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('V31 passive cranial load bow')],key=lambda o:o.name)
assert len(cheeks)==18,(len(cheeks),[o.name for o in cheeks])
assert len(bows)==2,(len(bows),[o.name for o in bows])
def meshdata(o,dg):
 ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@x.co for x in m.vertices];t=[tuple(f.vertices) for f in m.loop_triangles];ev.to_mesh_clear();return (o.name,o.parent.name,v,t,BVHTree.FromPolygons(v,t,all_triangles=True))
poses=[]
for dz in (0,.085,.175):
 cover.matrix_basis=rest;cover.location.z+=dz;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 left=[meshdata(o,dg) for o in cheeks];right=[meshdata(o,dg) for o in bows];pairs=[]
 for a in left:
  for b in right:
   witnesses=[]
   for ia,ib in a[4].overlap(b[4]):
    A=[a[2][j] for j in a[3][ia]];B=[b[2][j] for j in b[3][ib]]
    if any(edge(A[k],A[(k+1)%3],B) or edge(B[k],B[(k+1)%3],A) for k in range(3)):
     witnesses.append({'triangleIndices':[ia,ib],'cheekTriangle':[list(v) for v in A],'bowTriangle':[list(v) for v in B],'centroid':[sum(v[i] for v in A+B)/6 for i in range(3)]})
   if witnesses:pairs.append({'cheek':a[0],'cheekOwner':a[1],'bow':b[0],'bowOwner':b[1],'strictTrianglePairCount':len(witnesses),'firstWitness':witnesses[0]})
 poses.append({'cranialCoverLocalZLiftM':dz,'strictPairCount':len(pairs),'pairs':pairs})
 result={'nativeSHA256':BOUND,'executedScriptSHA256':sha(Path(__file__)),'strictKernelSHA256':sha(OUT.parent/'head'/'executed-strict-kernel.py'),'method':'Exact frozen V34 proper-crossing kernel, evaluated world-space triangle BVH candidates and strict noncoplanar edge-through-face confirmation; plane epsilon 1e-7, edge/barycentric margin 1e-6. Screen only the 18 head-owned tapered throat cheek plates against the 2 cranial-cover-owned passive load bows at rest and native cranial-cover local Z lifts .085m and .175m. Pair-level witnesses retained. Discrete shape-fit sample only; no continuous motion, containment or physical-clearance claim.','meshCounts':{'cheekPlates':len(cheeks),'cranialLoadBows':len(bows)},'owners':{'cheekPlates':sorted(set(o.parent.name for o in cheeks)),'cranialLoadBows':sorted(set(o.parent.name for o in bows))},'poses':poses}
(OUT/'screen.json').write_text(json.dumps(result,indent=2)+'\n')
assert sha(NATIVE)==BOUND
print(json.dumps({'nativeSHA256':BOUND,'poses':[{'lift':p['cranialCoverLocalZLiftM'],'pairCount':p['strictPairCount'],'pairs':[(x['cheek'],x['bow']) for x in p['pairs']]} for p in poses]},indent=2))
