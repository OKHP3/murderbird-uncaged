import json, bpy
from mathutils import Vector
def row(o):
    box=[o.matrix_world@Vector(p) for p in o.bound_box]
    mn=[round(min(p[i] for p in box),4) for i in range(3)]
    mx=[round(max(p[i] for p in box),4) for i in range(3)]
    return dict(n=o.name,t=o.type,par=o.parent.name if o.parent else "",collection=[c.name for c in o.users_collection],mn=mn,mx=mx,v=len(o.data.vertices) if o.type=="MESH" else 0,mats=[s.material.name for s in o.material_slots if s.material] if o.type=="MESH" else [],props=list(o.keys()),hide=o.hide_render)
from pathlib import Path
Path(__file__).with_name("inventory.json").write_text(json.dumps([row(o) for o in bpy.context.scene.objects]))
