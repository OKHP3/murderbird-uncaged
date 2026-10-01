import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged');bpy.ops.wm.open_mainfile(filepath=str(R/'assets/models/whole-character-v38/bill-gape01/attempt02/murderbird-v38-bill-gape01-attempt02.blend'));o=bpy.data.objects['V32 formed mandibular bowl'];keys=[(r,c)for r in range(53)for c in range(33)if r<=5 or c<=6 or c>=26 or r>=49];idx={k:i for i,k in enumerate(keys)};h=len(keys)
for row in [14,20,40,44,45,47,48,49,50,52]:
 print(row,[(c,list(o.matrix_world@o.data.vertices[idx[(row,c)]].co),list(o.matrix_world.to_3x3()@(o.data.vertices[h+idx[(row,c)]].co-o.data.vertices[idx[(row,c)]].co)))for c in[0,3,6,26,29,32]+([16]if row>=49 else[])])
