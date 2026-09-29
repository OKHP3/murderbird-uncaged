import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend')
bpy.context.view_layer.update()
rows=[]
for o in bpy.data.objects:
 if o.type=='EMPTY' and any(w in o.name for w in ('foot','toes','digit','shin')): print('NODE',o.name,o.parent.name if o.parent else None,list(o.matrix_world.translation),list(o.rotation_euler))
 if o.type=='MESH' and o.parent and any(w in o.parent.name for w in ('foot','toes','digit')):
  pts=[o.matrix_world@v.co for v in o.data.vertices]
  row={'name':o.name,'owner':o.parent.name,'bounds':[[min(v[k] for v in pts),max(v[k] for v in pts)] for k in range(3)],'props':dict(o.items()),'materials':[m.name if m else None for m in o.data.materials]};rows.append(row);print(json.dumps(row,default=list))
Path('assets/audit/whole-character-v37/regional-studies/foot-assembly/source-inventory.json').write_text(json.dumps(rows,indent=2,default=list))
