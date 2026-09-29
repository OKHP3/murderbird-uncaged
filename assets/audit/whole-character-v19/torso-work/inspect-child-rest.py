import bpy,runpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[4]
bpy.ops.wm.open_mainfile(filepath=str(root/'assets/models/whole-character-v18/attempt-01/murderbird-whole-character-v18.blend'))
before={o.name:o.matrix_world.copy() for o in bpy.data.objects if o.type=='EMPTY'}
runpy.run_path(str(root/'scripts/regions/whole-character-v19-torso-neck.py'))['apply']()
for name,m in before.items():
 o=bpy.data.objects[name];d=max(abs(o.matrix_world[r][c]-m[r][c]) for r in range(4) for c in range(4))
 if d:print(name,d,[list(r) for r in m],[list(r) for r in o.matrix_world])
