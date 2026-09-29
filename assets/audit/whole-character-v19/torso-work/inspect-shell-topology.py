import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[4]
bpy.ops.wm.open_mainfile(filepath=str(root/'assets/models/whole-character-v18/attempt-01/murderbird-whole-character-v18.blend'))
for name in ['Breast inner access shell','V17 breast directional lamina 1 4 left','V17 breast center keel return left','V17 breast captive overlap fasteners']:
 o=bpy.data.objects[name];print(name,len(o.data.vertices),len(o.data.polygons),[(m.name,m.type) for m in o.modifiers],dict(o))
