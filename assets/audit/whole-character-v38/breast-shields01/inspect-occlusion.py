import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged');A=R/'assets/audit/whole-character-v38/breast-shields01';bpy.ops.wm.open_mainfile(filepath=str(R/'assets/models/whole-character-v38/breast-shields01/murderbird-v38-breast-shields01.blend'));bpy.context.view_layer.update();s=bpy.data.objects['V30 continuous tapered breast liner'];s.data.calc_loop_triangles();tree=BVHTree.FromPolygons([s.matrix_world@v.co for v in s.data.vertices],[tuple(t.vertices)for t in s.data.loop_triangles],all_triangles=True);out=[]
for o in bpy.data.objects:
 if not o.name.startswith('V38 breast hanging shield '):continue
 o.data.calc_loop_triangles();half=len(o.data.vertices)//2;vals=[];witness=[]
 for t in o.data.loop_triangles:
  if not all(k<half for k in t.vertices):continue
  p=sum((o.matrix_world@o.data.vertices[k].co for k in t.vertices),Vector())/3;q,n,idx,d=tree.find_nearest(p)
  if n.dot(Vector((q.x,q.y+.08,0)))<0:n=-n
  signed=(p-q).dot(n);vals.append(signed)
  if signed<-.001 and len(witness)<3:witness.append({'plateOuterTriangle':t.index,'centroid':list(p),'signedM':signed,'linerTriangle':idx})
 out.append({'name':o.name,'outerCentroidSamples':len(vals),'minSignedM':min(vals),'maxSignedM':max(vals),'behindByOver1mm':sum(x<-.001 for x in vals),'firstBurialWitnesses':witness})
(A/'inspect-occlusion.json').write_text(json.dumps({'method':'Outer triangle centroids vs closest actual liner triangle; normal oriented radially outward; attribution only, not finite clearance','parts':out},indent=2)+'\n');print(out)
