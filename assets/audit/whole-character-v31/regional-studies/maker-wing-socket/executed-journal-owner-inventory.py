import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/whole-character-v30/attempt-form02/murderbird-whole-character-v30.blend');bpy.context.view_layer.update()
for n in ['right coaxial elbow journal','right stepped elbow race -0.015','right stepped elbow race 0.011']:
 o=bpy.data.objects[n];print(n,'parent',o.parent.name,'pivot',list(o.matrix_world.translation),'props',dict(o.items()))
 if o.type=='MESH':
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();vs=[ev.matrix_world@v.co for v in m.vertices];print('mesh',len(vs),'bounds',[[min(v[k] for v in vs),max(v[k] for v in vs)] for k in range(3)]);print('sample',[(i,list(v)) for i,v in enumerate(vs) if i%max(1,len(vs)//12)==0]);ev.to_mesh_clear()
