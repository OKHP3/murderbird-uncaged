import bpy
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged/assets/models/whole-character-v38/mantle-study02/murderbird-v38-mantle-study02.blend')
for o in bpy.data.objects:
 if o.name.startswith('V34 formed breast course '):
  pts=[o.matrix_world@v.co for v in o.data.vertices];n=len(pts)//2
  if len(pts)%2==0:
   d=[(pts[i]-pts[i+n]).length for i in range(n)];print(o.name,len(pts),min(d),max(d),sum(.002<q<.006 for q in d))
