import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[4]
bpy.ops.wm.open_mainfile(filepath=str(root/'assets/models/whole-character-v38/cheek-interface01/murderbird-v38-cheek-interface01.blend'))
rows=[]
for o in bpy.data.objects:
 if o.name in ['head','jaw','cranial-cover'] or any(t in o.name for t in ['recessed optic retaining lip','fixed annular journal','cheek clevis','optic recessed receiving cup']):
  row={'name':o.name,'owner':o.parent.name if o.parent else None,'originNativeWorld':list(o.matrix_world.translation)}
  if o.type=='MESH':
   p=[o.matrix_world@v.co for v in o.data.vertices];row['actualNativeBounds']=[[min(q[i]for q in p),max(q[i]for q in p)]for i in range(3)];row['boundsCenterNative']=[sum(a)/2 for a in row['actualNativeBounds']]
  rows.append(row)
p=root/'assets/audit/whole-character-v38/cheek-layout01/landmark-inventory.json';assert not p.exists();p.write_text(json.dumps(rows,indent=2)+'\n');print(rows)
