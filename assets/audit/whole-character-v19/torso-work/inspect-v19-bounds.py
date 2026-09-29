import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[4]
bpy.ops.wm.open_mainfile(filepath=str(root/'assets/models/whole-character-v19/attempt-torso01/murderbird-whole-character-v19.blend'))
dg=bpy.context.evaluated_depsgraph_get();out={}
for name in ['Breast inner access shell','Throat formed lamina 3','Throat formed lamina 4','Throat formed lamina 5','Throat formed lamina 6','Lower cervical open backing','Cervical flank lamina -1 6','Cervical flank lamina 1 6']:
 o=bpy.data.objects[name];e=o.evaluated_get(dg);m=e.to_mesh();p=[e.matrix_world@v.co for v in m.vertices]
 out[name]={'owner':o.parent.name,'min':[min(v[i] for v in p) for i in range(3)],'max':[max(v[i] for v in p) for i in range(3)]};e.to_mesh_clear()
(root/'assets/audit/whole-character-v19/attempt-torso01/evaluated-junction-bounds.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
