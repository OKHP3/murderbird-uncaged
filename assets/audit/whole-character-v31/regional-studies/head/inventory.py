import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/whole-character-v30/attempt-form02/murderbird-whole-character-v30.blend');bpy.context.view_layer.update();r={}
for o in bpy.data.objects:
 if o.parent and o.parent.name=='processing':
  r[o.name]={'type':o.type,'vertices':len(o.data.vertices) if o.type=='MESH' else None,'materials':[m.name for m in o.data.materials] if o.type=='MESH' else [],'props':dict(o.items())}
Path('/tmp/v31-head-reconstruction/processing-inventory.json').write_text(json.dumps(r,default=lambda x:list(x),indent=2))
