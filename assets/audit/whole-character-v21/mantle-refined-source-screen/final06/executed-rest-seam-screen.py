import hashlib
assert hashlib.sha256(open('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/audit/whole-character-v21/mantle-refined-source-screen/final06/executed-mantle-refined.py','rb').read()).hexdigest()=='c83d7a4932f4fbf4afea985ee0863e59efe0879750df30f9a0b7d57694e10937'
assert hashlib.sha256(open('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/whole-character-v21/attempt-envelope03/murderbird-whole-character-v21.blend','rb').read()).hexdigest()=='720c343645ef2de298a50e53c82fad66448c187b1eaf9311de2514cac079f280'
import bpy,json
from mathutils.bvhtree import BVHTree
r='/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged';bpy.ops.wm.open_mainfile(filepath=r+'/assets/models/whole-character-v21/attempt-envelope03/murderbird-whole-character-v21.blend');s={};exec(open('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/audit/whole-character-v21/mantle-refined-source-screen/final06/executed-mantle-refined.py').read(),s);receipt=s['apply']();dg=bpy.context.evaluated_depsgraph_get();parts={}
for o in bpy.data.objects:
 if o.type!='MESH' or not o.parent or o.parent.name not in s['OWNERS']:continue
 ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();p=[ev.matrix_world@v.co for v in m.vertices];f=[tuple(t.vertices) for t in m.loop_triangles];parts[o.name]=(o.parent.name,BVHTree.FromPolygons(p,f,all_triangles=True),[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]);ev.to_mesh_clear()
pairs=[]
for side in ('left','right'):
 for na,a in parts.items():
  if a[0]!=side+'-mantle':continue
  for nb,b in parts.items():
   if b[0]!=side+'-wing-shield' or any(a[3][i]<b[2][i] or b[3][i]<a[2][i] for i in range(3)):continue
   hits=a[1].overlap(b[1])
   if hits:pairs.append([na,nb,len(hits)])
print('REST_SEAM_SCREEN',json.dumps({'pairs':len(pairs),'identities':pairs}))
