import bpy,json,hashlib
from pathlib import Path
p=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/whole-character-v31/attempt-form01/murderbird-whole-character-v31.blend');assert hashlib.sha256(p.read_bytes()).hexdigest()=='fc1ef2fce58733afd68b08167f9823366cfb1a2f521c0bd21fccc25e8cb6372c';bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update()
for n in ['body','neck','cervical-mid-a','V23 root load fork -1','V23 root load fork 1','V23 cervical 1 load link -1','V23 cervical 1 load link 1','V23 root fixed journal -1','V23 root fixed journal 1']:
 o=bpy.data.objects[n];print(n,'owner',o.parent.name,'pivot',list(o.matrix_world.translation),'props',dict(o.items()))
 if o.type=='MESH':
  e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=[e.matrix_world@q.co for q in m.vertices];print('count',len(v),'bounds',[[min(q[k] for q in v),max(q[k] for q in v)] for k in range(3)]);print('sample',[(i,list(q)) for i,q in enumerate(v) if i%max(1,len(v)//12)==0]);e.to_mesh_clear()
