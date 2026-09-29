import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/models/whole-character-v18/attempt-orbital-fit02/murderbird-whole-character-v18.blend'))
for n in ['Swept temporal lamina -1 0 0','Temporal lamina root pin']:
 o=bpy.data.objects[n];print(n,len(o.data.vertices),len(o.data.polygons),[m.type for m in o.modifiers]);points=[o.matrix_world@v.co for v in o.data.vertices]
 for i in range(min(12,len(points))):print(i,list(points[i]))
