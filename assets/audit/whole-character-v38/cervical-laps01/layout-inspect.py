import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;R=P.parents[3]
bpy.ops.wm.open_mainfile(filepath=str(R/'assets/models/whole-character-v38/neck-envelope01/murderbird-v38-neck-envelope01.blend'));bpy.context.view_layer.update()
rows=[]
for o in bpy.data.objects:
 if o.type=='MESH'and any(s in o.name.lower()for s in ['cranial load bow','captive','head shaft','skull shaft','skull','cervical 4','head bearing','head race']):
  v=[o.matrix_world@p.co for p in o.data.vertices];rows.append({'name':o.name,'owner':o.parent.name if o.parent else None,'origin':list(o.matrix_world.translation),'bounds':[[min(p[i]for p in v),max(p[i]for p in v)]for i in range(3)],'vertices':len(v),'description':str(o.get('constructionDescription',''))[:600]})
for n in ['head','cervical-upper','jaw','upper-bill','cranial-cover','builder-optics']:
 o=bpy.data.objects.get(n)
 if o:rows.append({'name':n,'owner':o.parent.name if o.parent else None,'origin':list(o.matrix_world.translation),'local':list(o.location),'matrixLocal':[list(r)for r in o.matrix_local],'props':dict(o.items())})
(P/'layout-inspect.json').write_text(json.dumps(rows,indent=2,default=lambda v:list(v))+'\n');print(json.dumps(rows,default=lambda v:list(v)),flush=True)
