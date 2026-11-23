import bpy
import json
from mathutils import Vector
from pathlib import Path

def row(o):
    coords = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return dict(name=o.name, parent=o.parent.name if o.parent else None, type=o.type, lo=[round(min(c[i] for c in coords),4) for i in range(3)], hi=[round(max(c[i] for c in coords),4) for i in range(3)], mats=[s.material.name if s.material else None for s in o.material_slots], verts=len(o.data.vertices) if o.type=='MESH' else 0, props=dict((k,str(o[k])[:150]) for k in o.keys() if k not in ('_RNA_UI',)))
obs=[row(o) for o in bpy.context.scene.objects]
out=Path.cwd()/'native'/'atelier'/'head'/'inventory.json'
out.write_text(json.dumps(obs,indent=1))
print('Inventory',len(obs),'objects',sum(o['verts'] for o in obs),'vertices')
