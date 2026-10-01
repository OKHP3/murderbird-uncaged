import bpy,json
from pathlib import Path
R=Path('/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged');bpy.ops.wm.open_mainfile(filepath=str(R/'assets/models/whole-character-v38/jaw-stock01/murderbird-v38-jaw-stock01.blend'));out=[]
for o in bpy.data.objects:
 if not o.name.startswith('V38 swept crown course ')or o.type!='MESH':continue
 v=[o.matrix_world@p.co for p in o.data.vertices];h=len(v)//2;out.append({'name':o.name,'owner':o.parent.name,'count':len(v),'bounds':[[min(p[k]for p in v),max(p[k]for p in v)]for k in range(3)],'extras':{k:str(o[k])for k in o.keys()},'first15Native':[list(p)for p in v[:15]],'last15OuterNative':[list(p)for p in v[h-15:h]],'firstFaces':[list(p.vertices)for p in o.data.polygons[:10]]})
A=R/'assets/audit/whole-character-v38/crown-plate01';(A/'inspect-current.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(next(p for p in out if p['name']=='V38 swept crown course 0 column 3 leaf 1'),indent=2))
