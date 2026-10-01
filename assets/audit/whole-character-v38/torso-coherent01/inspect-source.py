import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/models/whole-character-v38/ribcage-envelope01/attempt02/murderbird-v38-ribcage-envelope01-attempt02.blend'))
bpy.context.view_layer.update()
for o in bpy.data.objects:
 if o.type=='MESH' and ('breast' in o.name or 'sternal' in o.name):
  v=[o.matrix_world@p.co for p in o.data.vertices]
  print('BOUND',o.name,len(v),o.parent.name,[[min(p[i]for p in v),max(p[i]for p in v)]for i in range(3)],flush=True)
liner=bpy.data.objects['V30 continuous tapered breast liner'];v=[liner.matrix_world@p.co for p in liner.data.vertices]
for z in [.70,.75,.8,.85,.9,.95,1,1.05,1.1,1.15,1.2,1.25]:
 p=[p for p in v if abs(p.z-z)<.014]
 if p:print('SECTION',z,len(p),[[min(q[i]for q in p),max(q[i]for q in p)]for i in range(3)],flush=True)
