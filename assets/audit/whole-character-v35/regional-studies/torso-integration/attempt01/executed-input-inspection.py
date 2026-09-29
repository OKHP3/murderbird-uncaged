import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/whole-character-v34/attempt-form01/murderbird-whole-character-v34.blend')
dg=bpy.context.evaluated_depsgraph_get();rows=[]
for o in bpy.data.objects:
 if o.type=='MESH' and o.parent and o.parent.name in ('body','breastplate'):
  e=o.evaluated_get(dg);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];e.to_mesh_clear();rows.append({'name':o.name,'owner':o.parent.name,'role':o.get('surfaceRole'), 'bounds':[[min(p[k] for p in v),max(p[k] for p in v)] for k in range(3)],'vertices':len(o.data.vertices),'materials':[m.name if m else None for m in o.data.materials]})
Path('/tmp/v35-torso-integration/input.json').write_text(json.dumps(rows,indent=2))
print('\n'.join(f'{r["name"]} {r["role"]} {r["bounds"]}' for r in rows))
