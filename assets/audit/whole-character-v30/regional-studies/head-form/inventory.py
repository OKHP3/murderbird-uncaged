import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/whole-character-v29/attempt-fit01/murderbird-whole-character-v29.blend')
bpy.context.view_layer.update();out={'headPivot':list(bpy.data.objects['head'].matrix_world.translation),'meshes':{}}
for o in bpy.data.objects:
 if o.type=='MESH' and o.parent and o.parent.name in {'head','jaw','upper-bill','cranial-cover','builder-optics'}:
  p=[o.matrix_world@v.co for v in o.data.vertices];out['meshes'][o.name]={'owner':o.parent.name,'bounds':[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)],'verts':len(p),'mods':[m.type for m in o.modifiers]}
Path('/tmp/v30-head-form/inventory.json').write_text(json.dumps(out,indent=2))
