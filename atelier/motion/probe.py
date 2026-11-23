import bpy
from mathutils import Vector
from collections import Counter
import json
def rounded(v):
    return [round(i,5) for i in v]
data={}
for o in bpy.context.scene.objects:
    coords = [o.matrix_world @ Vector(co) for co in o.bound_box]
    data[o.name] = {'type':o.type,'parent':o.parent and o.parent.name,'coll':[c.name for c in o.users_collection],'visible':o.visible_get(),'hide_render':o.hide_render,'loc':rounded(o.matrix_world.translation),'range':[rounded([min(c[i] for c in coords) for i in range(3)]),rounded([max(c[i] for c in coords) for i in range(3)])], 'mat':[s.material.name if s.material else None for s in o.material_slots]}
json.dump(data,open('native/atelier/motion/native-layout.json','w'),indent=1)
print(Counter(o.type for o in bpy.context.scene.objects))
print(Counter(row['parent'] for row in data.values()).most_common(60))
print(Counter(c for row in data.values() for c in row['coll']).most_common())
print([(o.name,rounded(o.matrix_world.translation)) for o in bpy.context.scene.objects if o.type not in ['MESH','CURVE']][:140])
