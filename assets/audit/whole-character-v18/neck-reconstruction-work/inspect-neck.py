import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/models/whole-character-v17/attempt-02/murderbird-whole-character-v17.blend'))
for name in ['Throat formed lamina 3','Throat formed lamina 4','Throat formed lamina 5','Throat formed lamina 6','Cervical flank lamina -1 4','Cervical flank lamina -1 5','Lower cervical open backing']:
 o=bpy.data.objects[name];p=[o.matrix_world@v.co for v in o.data.vertices];print(name,len(p),[m.type for m in o.modifiers])
 for row in [p[:13],p[-13:]]:
  print('row',list(sum(row,Vector())/len(row)), 'center',list(row[len(row)//2]))
