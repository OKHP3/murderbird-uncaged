from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
A=Path(__file__).parent;R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');rec=json.loads((A/'receipt.json').read_text());N=R/'assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(N)=='d2c704ccf89f3f0e7dbeb3613dcdbdd964c4ba69991783783830803eecf59cb0';bpy.ops.wm.open_mainfile(filepath=str(N));bpy.context.view_layer.update();s=(A/'head-screen/executed-strict-kernel.py').read_text();exec(s[s.index('def inside'):s.index('poses=[]')]);dg=bpy.context.evaluated_depsgraph_get();objects=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('V33 swept temporal leaf ')];assert len(objects)==14;items=[mesh(o,dg) for o in objects];pairs=[]
for i,a in enumerate(items):
 for b in items[i+1:]:
  hits=0;first=None
  for ia,ib in a[3].overlap(b[3]):
   X=[a[1][n] for n in a[2][ia]];Y=[b[1][n] for n in b[2][ib]]
   if any(edge(X[k],X[(k+1)%3],Y) or edge(Y[k],Y[(k+1)%3],X) for k in range(3)):
    hits+=1
    if first is None:first={'indices':[ia,ib],'aWorld':[list(x) for x in X],'bWorld':[list(x) for x in Y]}
  if hits:pairs.append({'a':a[0],'b':b[0],'strictTrianglePairs':hits,'firstWitness':first})
(A/'baseline-temporal-pair-check.json').write_text(json.dumps({'nativeSHA256':sha(N),'baseline':'Exact incoming V35Form01; no V36 geometry applied','executedSourceSHA256':sha(Path(__file__)),'method':'Same exact strict edge-through-face kernel on all91distinct temporal leaf pairs in actual rest geometry; excludes intra-mesh, tangencies/coplanarity/containment and continuous motion','screenedLeaves':sorted(o.name for o in objects),'distinctPairCombinations':91,'strictPairCount':len(pairs),'pairs':pairs,'nativeUnchanged':sha(N)=='d2c704ccf89f3f0e7dbeb3613dcdbdd964c4ba69991783783830803eecf59cb0'},indent=2)+'\n');print('TEMPORAL REST',len(pairs));assert sha(N)=='d2c704ccf89f3f0e7dbeb3613dcdbdd964c4ba69991783783830803eecf59cb0'
