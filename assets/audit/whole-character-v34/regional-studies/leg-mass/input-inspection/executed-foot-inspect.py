import bpy,json
from pathlib import Path
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');bpy.ops.wm.open_mainfile(filepath=str(R/'assets/models/whole-character-v33/attempt-form06/murderbird-whole-character-v33.blend'));bpy.context.view_layer.update();r=[]
for o in bpy.data.objects:
 if o.type=='MESH' and o.parent and o.parent.name=='right-foot':
  v=[o.matrix_world@x.co for x in o.data.vertices];d={'name':o.name,'props':dict(o.items()),'min':[min(p[k] for p in v) for k in range(3)],'max':[max(p[k] for p in v) for k in range(3)],'material':[m.name for m in o.data.materials]};r.append(d);print(o.name,[round(x,3) for x in d['min']],[round(x,3) for x in d['max']])
(R/'assets/audit/whole-character-v34/regional-studies/leg-mass/input-inspection/foot-inventory.json').write_text(json.dumps(r,indent=2,default=lambda x:list(x)))
