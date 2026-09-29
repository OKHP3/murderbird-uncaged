from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
root=Path.cwd();native=root/'assets/models/whole-character-v17/attempt-02/murderbird-whole-character-v17.blend'
assert hashlib.sha256(native.read_bytes()).hexdigest()=='7d371907b279eb3d625e67164d84a78b2901a5cb6a79917def07f48ff8792d7b'
bpy.ops.wm.open_mainfile(filepath=str(native))
rows=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  pts=[o.matrix_world@Vector(p) for p in o.bound_box]
  rows.append({'name':o.name,'owner':o.parent.name if o.parent else None,'region':o.get('region'),'role':o.get('surfaceRole'),'eras':o.get('exteriorEras'),'materials':[m.name for m in o.data.materials if m],'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)],'visible':not o.hide_render})
output=root/'assets/audit/whole-character-v18/input-native-inventory/inventory.json'
assert not output.exists()
output.write_text(json.dumps({'native':str(native.relative_to(root)),'sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'note':'Native authored world-space bounds, not dimensions recovered from references; no model edit.','nodes':[{ 'name':o.name,'parent':o.parent.name if o.parent else None,'position':list(o.matrix_world.translation)} for o in bpy.data.objects if o.type=='EMPTY'],'meshes':rows},indent=2)+'\n')
print('Inventory saved; native unchanged')
