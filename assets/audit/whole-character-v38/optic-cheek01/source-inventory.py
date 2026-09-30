import bpy,json,hashlib
from pathlib import Path
p=Path('/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged/assets/models/whole-character-v38/bill-identity01-socket-fit01/murderbird-v38-bill-identity01-socket-fit01.blend');assert hashlib.sha256(p.read_bytes()).hexdigest()=='073bdc678ea2911392b084981b1d2eaa42ce44e53e262b42b4ff14d4b266d665';bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update();rows=[]
for o in bpy.data.objects:
 if o.type=='MESH' and (o.parent and o.parent.name in ['upper-bill','jaw','head','builder-optics']):
  pts=[o.matrix_world@v.co for v in o.data.vertices];r={'name':o.name,'owner':o.parent.name,'vertices':len(pts),'faces':len(o.data.polygons),'bounds':[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)],'props':dict(o.items()),'materials':[m.name if m else None for m in o.data.materials]};
  if any(n in o.name for n in ('optic','orbital','cheek','lateral')):r['allWorldVertices']=[list(p) for p in pts];print(o.name,len(pts),[list(p) for p in pts[:10]],[list(p) for p in pts[len(pts)//2-10:len(pts)//2]])
  rows.append(r)
Path('/tmp/murderbird-optic-inventory.json').write_text(json.dumps(rows,indent=2,default=str))
print('PIVOTS',[(n,list(bpy.data.objects[n].matrix_world.translation)) for n in ['head','upper-bill','jaw']])
