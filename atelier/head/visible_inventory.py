import bpy
from collections import Counter
from mathutils import Vector
import json
from pathlib import Path
rows=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH': continue
 c=[ob.matrix_world @ Vector(v) for v in ob.bound_box]
 rows.append(dict(name=ob.name,collection=[co.name for co in ob.users_collection],vis=ob.visible_get(),render=not ob.hide_render, lo=[round(min(v[i] for v in c),4) for i in range(3)], hi=[round(max(v[i] for v in c),4) for i in range(3)],mats=[s.material.name if s.material else None for s in ob.material_slots],props=dict((k,str(ob[k])[:120]) for k in ob.keys()),verts=len(ob.data.vertices)))
Path('native/atelier/head/visible.json').write_text(json.dumps(rows))
print(Counter((r['vis'],r['render']) for r in rows))
print(Counter((r['collection'][0]) for r in rows if r['vis'] and r['render']))
print([ (o.name, o.location[:]) for o in bpy.context.scene.objects if o.type=='CAMERA'][:20])
