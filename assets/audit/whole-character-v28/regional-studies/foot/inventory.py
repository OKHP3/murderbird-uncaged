import bpy, json
from mathutils import Vector
p='assets/models/whole-character-v27/attempt-form01/murderbird-whole-character-v27.blend'
bpy.ops.wm.open_mainfile(filepath=p)
sc=bpy.context.scene; sc.frame_set(1); bpy.context.view_layer.update()
out=[]
terms=('dorsal guard','tapered claw sheath','inner link')
for o in bpy.data.objects:
 if o.type=='MESH' and any(t in o.name.lower() for t in terms):
  pts=[o.matrix_world @ v.co for v in o.data.vertices]
  b=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)] if pts else []
  local=[[min(v.co[i] for v in o.data.vertices),max(v.co[i] for v in o.data.vertices)] for i in range(3)]
  out.append(dict(name=o.name,parent=o.parent.name if o.parent else None,verts=len(o.data.vertices),faces=len(o.data.polygons),bounds=b,localBounds=local,location=list(o.location),scale=list(o.scale),props={k:str(o[k]) for k in o.keys() if k not in ('_RNA_UI',)}))
print(json.dumps(out,indent=2))
