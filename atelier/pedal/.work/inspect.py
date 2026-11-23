import bpy, json
from mathutils import Vector
from pathlib import Path
base=Path(__file__).parent
def get_box(o):
    ps=[o.matrix_world @ Vector(v) for v in o.bound_box]
    return [[round(f([p[i] for p in ps]),4) for i in range(3)] for f in (min,max)]
obj=[{'name':o.name,'type':o.type,'mesh':o.data.name if o.type=='MESH' else '', 'nvert':len(o.data.vertices) if o.type=='MESH' else None,
      'bbox': get_box(o),'mat':[s.material.name if s.material else None for s in o.material_slots], 'parent':o.parent.name if o.parent else '',
      'collections':[c.name for c in o.users_collection],'hide_viewport':o.hide_viewport,'hide_render':o.hide_render,
      'props':{k:str(o[k]) for k in o.keys()}} for o in bpy.context.scene.objects]
(base/'retained-inventory.json').write_text(json.dumps(obj,indent=1))
