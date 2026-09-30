import bpy,json
from pathlib import Path
r=Path(__file__).resolve().parents[4];bpy.ops.wm.open_mainfile(filepath=str(r/'assets/models/whole-character-v38/jaw-fit02/murderbird-v38-jaw-fit02.blend'));names=[o.name for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith('V38 swept crown course')or o.name.startswith(('V31 fixed temporal receiving wall','V33 diagonal brow receiver','V38 optic cheek shield','V33 swept temporal leaf','V31 temporal fitting root','V31 passive temporal fitting')))]
rows=[]
for name in sorted(names):
 o=bpy.data.objects[name];p=[o.matrix_world@v.co for v in o.data.vertices];rows.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'nativeWorldBounds':[[min(q[i]for q in p),max(q[i]for q in p)]for i in range(3)]})
p=r/'assets/audit/whole-character-v38/cranial-transition01/scope-inventory.json';assert not p.exists();p.write_text(json.dumps(rows,indent=2)+'\n');print('count',len(rows));print('crown bounds',[[min(x['nativeWorldBounds'][i][0]for x in rows if x['owner']=='cranial-cover'),max(x['nativeWorldBounds'][i][1]for x in rows if x['owner']=='cranial-cover')]for i in range(3)])
