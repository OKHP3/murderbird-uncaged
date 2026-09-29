import bpy,json
from pathlib import Path
bpy.context.view_layer.update()
out=[]
for o in bpy.data.objects:
 if o.type=='EMPTY' and any(t in o.name for t in ('thigh','shin','foot')):out.append({'node':o.name,'world':list(o.matrix_world.translation),'scale':list(o.scale)})
 if o.type=='MESH' and o.parent and o.parent.name in ('left-thigh','right-thigh','left-shin','right-shin'):
  p=[o.matrix_world@v.co for v in o.data.vertices]
  out.append({'mesh':o.name,'owner':o.parent.name,'verts':len(p),'bounds':[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)],'materials':[m.name for m in o.data.materials],'role':o.get('surfaceRole')})
Path('/tmp/v25-leg-structure/inspect.json').write_text(json.dumps(out,indent=2))
