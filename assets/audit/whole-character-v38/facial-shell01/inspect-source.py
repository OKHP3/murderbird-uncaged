import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged')
bpy.ops.wm.open_mainfile(filepath=str(R/'assets/models/whole-character-v38/bill-vault01/attempt02/murderbird-v38-bill-vault01-attempt02.blend'));bpy.context.view_layer.update();out=[]
for o in bpy.data.objects:
 if o.type!='MESH' or not any(k in o.name for k in ['compact cranial inner shell','fixed temporal receiving wall','optic recessed receiving cup','cavity floor','retaining lip','Advanced optical aperture']):continue
 ps=[o.matrix_world@v.co for v in o.data.vertices];out.append({'name':o.name,'parent':o.parent.name if o.parent else None,'vertices':len(ps),'faces':len(o.data.polygons),'bounds':[[min(v[k]for v in ps),max(v[k]for v in ps)]for k in range(3)],'materials':[m.name if m else None for m in o.data.materials],'sampleVerts':[list(ps[i])for i in range(0,len(ps),max(1,len(ps)//20))]})
(R/'assets/audit/whole-character-v38/facial-shell01/inspect-source.json').write_text(json.dumps(out,indent=2));print(json.dumps([{k:v for k,v in q.items()if k not in ['sampleVerts','extras']}for q in out],indent=2))
