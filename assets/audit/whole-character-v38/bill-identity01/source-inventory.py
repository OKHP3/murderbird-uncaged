import bpy,json,hashlib
from pathlib import Path
p=Path('/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged/assets/models/whole-character-v38/breast-clearance02/murderbird-v38-breast-clearance02.blend');assert hashlib.sha256(p.read_bytes()).hexdigest()=='a57898797d040ed2ea52aa1b8b30749d77a8c49ebc3ba785ed3169ada587aad8';bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update();rows=[]
for o in bpy.data.objects:
 if o.type=='MESH' and (o.parent and o.parent.name in ['upper-bill','jaw','head','builder-optics']):
  pts=[o.matrix_world@v.co for v in o.data.vertices];r={'name':o.name,'owner':o.parent.name,'vertices':len(pts),'faces':len(o.data.polygons),'bounds':[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)],'props':dict(o.items()),'materials':[m.name if m else None for m in o.data.materials]};
  if o.name.startswith('V32 returned upper bill'):r['allWorldVertices']=[list(p) for p in pts];print(o.name,len(pts),[list(p) for p in pts[:10]],[list(p) for p in pts[len(pts)//2-10:len(pts)//2]])
  rows.append(r)
Path('/tmp/murderbird-bill-inventory.json').write_text(json.dumps(rows,indent=2,default=str))
print('PIVOTS',[(n,list(bpy.data.objects[n].matrix_world.translation)) for n in ['head','upper-bill','jaw']])
