import bpy,json,hashlib
from pathlib import Path
R=Path('/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged');p=R/'assets/models/whole-character-v38/cheek-seated03/murderbird-v38-cheek-seated03.blend';assert hashlib.sha256(p.read_bytes()).hexdigest()=='b7c46ad051aaacd26abc3ee7d5a29deabe9d57b7693e696b5f0424cdc40be122';bpy.ops.wm.open_mainfile(filepath=str(p));rows=[]
for o in bpy.data.objects:
 if o.type!='MESH' or 'V38 ' not in o.name or not ('mantle' in o.name or 'elbow' in o.name):continue
 pts=[o.matrix_world@v.co for v in o.data.vertices];rows.append({'name':o.name,'owner':o.parent.name,'vertices':len(pts),'bounds':[[min(p[k]for p in pts),max(p[k]for p in pts)]for k in range(3)],'rowCenters':[list(sum(pts[i*11:i*11+11],pts[0]*0)/11)for i in [0,2,6,10,12]] if len(pts)==286 else None})
Path('/tmp/murderbird-compact-mantle-inventory.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows[:5],indent=2))
