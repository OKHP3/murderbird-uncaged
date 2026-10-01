import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('/Users/okh/.codex/worktrees/v38-facial-fit/murderbird-uncaged');bpy.ops.wm.open_mainfile(filepath=str(R/'assets/models/whole-character-v38/facial-shell01/attempt02/murderbird-v38-facial-shell01-attempt02.blend'));bpy.context.view_layer.update()
for name in ['V31 passive cranial load bow -1','V33 swept temporal leaf -1 5']:
 o=bpy.data.objects[name];ps=[o.matrix_world@v.co for v in o.data.vertices];rows=[]
 for f in o.data.polygons:
  vs=[ps[i]for i in f.vertices];c=sum(vs,Vector())/len(vs)
  if c.z>1.68 and c.y<-.42:rows.append((f.index,list(c)))
 print(name,'top spatialpatches',rows[::max(1,len(rows)//18)])
