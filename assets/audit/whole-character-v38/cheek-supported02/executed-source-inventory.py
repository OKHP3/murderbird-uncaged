import bpy,json
from pathlib import Path
p=Path('/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged/assets/models/whole-character-v38/jaw-fit02/murderbird-v38-jaw-fit02.blend');bpy.ops.wm.open_mainfile(filepath=str(p));rows=[]
for o in bpy.data.objects:
 if o.type!='MESH' or not any(x in o.name for x in ('fixed temporal receiving wall','diagonal brow receiver','optic cheek shield','formed lower cheek receiver','swept temporal leaf','frontal cranial cap receiving seat','temporal fitting root','passive temporal fitting','temporal fitting yoke','temporal aft')):continue
 pts=[o.matrix_world@v.co for v in o.data.vertices];rows.append({'name':o.name,'owner':o.parent.name if o.parent else None,'eras':o.get('exteriorEras'),'bounds':[[min(p[k]for p in pts),max(p[k]for p in pts)]for k in range(3)]})
Path('/tmp/cheek-supported-inventory.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
