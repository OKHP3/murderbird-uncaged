import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/models/whole-character-v38/lower-support02/murderbird-v38-lower-support02.blend'))
bpy.context.view_layer.update();records=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 ancestors=[];p=o.parent
 while p:ancestors.append(p.name);p=p.parent
 if not(any(x in ancestors for x in ('neck','cervical-mid-a','cervical-mid-b','cervical-upper','head','jaw')) or any(t in o.name.lower() for t in ('neck','cheek','throat','collar','mandible'))):continue
 v=[o.matrix_world@v.co for v in o.data.vertices]
 records.append({'name':o.name,'owner':o.parent.name if o.parent else None,'verts':len(v),'faces':len(o.data.polygons),'bounds':[[min(p[i]for p in v),max(p[i]for p in v)]for i in range(3)],'props':json.loads(json.dumps(dict(o.items()),default=lambda v:list(v))),'modifiers':[(m.name,m.type)for m in o.modifiers],'rowWorldCenters':[[sum(p[k]for p in v[row*19:(row+1)*19])/19 for k in range(3)]for row in range(21)] if len(v)in(399,798) else []})
(OUT/'source-inventory.json').write_text(json.dumps(records,indent=2)+'\n')
for o in bpy.data.objects:
 if o.type=='EMPTY'and o.name in ('neck','cervical-mid-a','cervical-mid-b','cervical-upper','head','jaw'):print('PIVOT',o.name,list(o.matrix_world.translation),list(o.rotation_euler))
for r in records:
 if any(t in r['name'].lower()for t in ('guard','cheek','mandible','throat','neck shell')):print(r['name'],r['owner'],r['verts'],r['bounds'],r['modifiers'])
