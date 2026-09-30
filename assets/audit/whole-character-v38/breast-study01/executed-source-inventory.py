import bpy,json,hashlib
from pathlib import Path
p=Path('/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged/assets/models/whole-character-v38/mantle-study02/murderbird-v38-mantle-study02.blend');assert hashlib.sha256(p.read_bytes()).hexdigest()=='d1e2cbf3b7d89432780668ca2e4aefbd9815bd8e2afe4af167ff8bf54515de62';bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update();rows=[]
for o in bpy.data.objects:
 if o.type!='MESH' or o.get('authoringGuide') is True:continue
 if o.parent and o.parent.name in ['body','chest-cover','breast-cover'] or any(s in o.name.lower() for s in ['breast','thoracic','sternal','scapular','rib','pelvic liner']):
  pts=[o.matrix_world@v.co for v in o.data.vertices];rows.append({'name':o.name,'owner':o.parent.name if o.parent else None,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'bounds':[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)],'props':dict(o.items()),'materials':[m.name if m else None for m in o.data.materials],'modifiers':[(m.name,m.type) for m in o.modifiers]})
Path('/tmp/murderbird-breast-inventory.json').write_text(json.dumps(rows,indent=2,default=str))
for o in rows:print(o['name'],o['owner'],o['vertices'],o['bounds'],o['props'].get('region'))
