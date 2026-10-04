import bpy,json
from mathutils import Vector
from pathlib import Path
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O/'attempt01/layered-head17.blend'))
s=bpy.context.scene;f=s.objects['CG2b head frame'].matrix_world.inverted();r={}
for o in s.objects:
 if o.type=='MESH' and not o.hide_render and (o.get('cgSupervisedHead17') or 'vault' in o.name):
  q=[f@o.matrix_world@Vector(v) for v in o.bound_box];r[o.name]={'local_min':[min(v[a] for v in q) for a in range(3)],'local_max':[max(v[a] for v in q) for a in range(3)]}
(O/'attempt01/actual-bounds.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
