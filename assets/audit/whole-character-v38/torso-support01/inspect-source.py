import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/models/whole-character-v38/torso-coherent01/murderbird-v38-torso-coherent01.blend'))
bpy.context.view_layer.update()
N=[f'V35 lateral thoracic bay load rail {s}'for s in(-1,1)]+[f'V24 rising thoracic receiving cheek {s}'for s in(-1,1)]+['neck','breastplate']
for n in N:
 o=bpy.data.objects[n];print('STOCK',n,len(o.data.vertices)if o.type=='MESH'else 0,list(o.matrix_world.translation),json.dumps(dict(o.items()),default=lambda x:list(x)),flush=True)
 if o.type=='MESH':
  v=[o.matrix_world@q.co for q in o.data.vertices];print('EXTREMES',[[min(v,key=lambda p:p[i])[:],max(v,key=lambda p:p[i])[:]]for i in range(3)],flush=True)
