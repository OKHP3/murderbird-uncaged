import bpy,bmesh,json
from pathlib import Path
root=Path(__file__).resolve().parents[4];bpy.ops.wm.open_mainfile(filepath=str(root/'assets/models/whole-character-v19/attempt-torso05/murderbird-whole-character-v19.blend'));rows=[]
for o in bpy.data.objects:
 if o.type!='MESH' or 'breast' not in o.name or 'fasteners' not in o.name:continue
 bm=bmesh.new();bm.from_mesh(o.data);seen=set();count=0
 for v in bm.verts:
  if v in seen:continue
  count+=1;todo=[v]
  while todo:
   a=todo.pop()
   if a in seen:continue
   seen.add(a);todo.extend(e.other_vert(a) for e in a.link_edges)
 rows.append({'name':o.name,'owner':o.parent.name,'declaredHeadCount':o.get('anchorHeadCount'),'actualCompleteIslandCount':count,'sourceCount':o.get('sourceAnchorHeadCount')});bm.free()
j={'status':'PASS' if sum(r['actualCompleteIslandCount'] for r in rows)==78 and all(r['declaredHeadCount']==r['actualCompleteIslandCount'] for r in rows) else 'FAIL','originalCompleteHeadCount':78,'objects':rows};(root/'assets/audit/whole-character-v19/attempt-torso05/fastener-count-check.json').write_text(json.dumps(j,indent=2));print(json.dumps(j,indent=2))
