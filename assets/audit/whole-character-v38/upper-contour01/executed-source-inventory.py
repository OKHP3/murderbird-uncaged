import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[4];bpy.ops.wm.open_mainfile(filepath=str(R/'assets/models/whole-character-v38/bill-relationship02/murderbird-v38-bill-relationship02.blend'));rows=[]
for o in bpy.data.objects:
 if o.name in ['body','breastplate','neck','cervical-mid-a','cervical-mid-b','cervical-upper','head'] or o.parent and o.parent.name in ['neck','cervical-mid-a','cervical-mid-b','cervical-upper'] or o.name.startswith('V34 formed breast course') or o.name.startswith('V30 continuous'):
  row={'name':o.name,'owner':o.parent.name if o.parent else None,'type':o.type,'worldMatrix':[list(r)for r in o.matrix_world],'localMatrix':[list(r)for r in o.matrix_local],'props':dict(o.items())}
  if o.type=='MESH':
   v=[o.matrix_world@q.co for q in o.data.vertices];row['bounds']=[[min(p[k]for p in v),max(p[k]for p in v)]for k in range(3)];row['vertices']=len(v)
  rows.append(row)
(R/'assets/audit/whole-character-v38/upper-contour01/source-inventory.json').write_text(json.dumps(rows,indent=2,default=list)+'\n')
for o in rows:print(o['name'],o['owner'],o.get('bounds'), 'LOC', [r[3]for r in o['worldMatrix'][:3]],flush=True)
