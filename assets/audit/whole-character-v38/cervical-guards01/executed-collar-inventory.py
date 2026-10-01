import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='assets/models/whole-character-v38/bill-relationship02/murderbird-v38-bill-relationship02.blend');bpy.context.view_layer.update();rows=[]
for o in bpy.data.objects:
 if o.type!='MESH' or not o.parent:continue
 if o.parent.name not in ['head','neck','cervical-mid-a','cervical-mid-b','cervical-upper','cranial-cover']:continue
 p=[o.matrix_world@v.co for v in o.data.vertices]
 if not p:continue
 lo=[min(v[k]for v in p)for k in range(3)];hi=[max(v[k]for v in p)for k in range(3)]
 if lo[2]<1.58 and hi[2]>1.43:
  row={'name':o.name,'owner':o.parent.name,'nativeBounds':[lo,hi]};rows.append(row);print(row,flush=True)
Path('assets/audit/whole-character-v38/cervical-guards01/collar-inventory.json').write_text(json.dumps(rows,indent=2)+'\n')
