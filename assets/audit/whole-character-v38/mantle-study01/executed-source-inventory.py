import bpy,json
from pathlib import Path
p=Path('/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged');bpy.ops.wm.open_mainfile(filepath=str(p/'assets/models/whole-character-v38/neck-clearance01/murderbird-v38-neck-clearance01.blend'));bpy.context.view_layer.update();rows=[]
for o in bpy.data.objects:
 if o.type=='MESH' and o.parent and o.parent.name in ['left-mantle','right-mantle','left-wing-shield','right-wing-shield']:
  pts=[o.matrix_world@v.co for v in o.data.vertices];rows.append({'name':o.name,'owner':o.parent.name,'verts':len(pts),'bounds':[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)],'materials':[m.name for m in o.data.materials],'props':dict(o.items())})
Path('/tmp/murderbird-mantle-inventory.json').write_text(json.dumps(rows,indent=2))
for side in ['left','right']:
 plates=[o for o in rows if o['name'].startswith('V38 '+side+' mantle')];print(side,'count',len(plates),'bounds',[[min(o['bounds'][i][0] for o in plates),max(o['bounds'][i][1] for o in plates)] for i in range(3)])
for o in rows:
 if o['name'].startswith('V38 left mantle') and o['name'].endswith('plate 3'):print(o['name'],o['bounds'])
