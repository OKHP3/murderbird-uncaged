import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/whole-character-v29/attempt-fit01/murderbird-whole-character-v29.blend');bpy.context.view_layer.update();r={'nodes':{},'meshes':{}}
for o in bpy.data.objects:
 if o.type=='EMPTY':r['nodes'][o.name]={'parent':o.parent.name if o.parent else None,'world':list(o.matrix_world.translation),'basis':[[float(o.matrix_world[i][j]) for j in range(3)] for i in range(3)]}
 elif o.type=='MESH' and o.parent and any(k in o.parent.name for k in ['thigh','shin','foot','digit']):
  p=[o.matrix_world@v.co for v in o.data.vertices];r['meshes'][o.name]={'owner':o.parent.name,'role':o.get('surfaceRole'),'verts':len(p),'bounds':[[min(v[k] for v in p),max(v[k] for v in p)] for k in range(3)]}
Path('/tmp/v30-support-proportion/inventory.json').write_text(json.dumps(r,indent=2))
