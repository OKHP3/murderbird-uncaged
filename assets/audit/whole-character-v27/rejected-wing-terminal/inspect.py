from pathlib import Path
import bpy,json,hashlib
P=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/whole-character-v26/attempt-form01/murderbird-whole-character-v26.blend');assert hashlib.sha256(P.read_bytes()).hexdigest()=='f897b3310af0c9d8b5e079484bcd9b8863e35c12e6b2be26601ad56700b65564';bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.view_layer.update();rows=[]
for o in bpy.data.objects:
 if o.type!='MESH' or not o.parent or o.parent.name not in ['left-wing-shield','right-wing-shield','left-mantle','right-mantle']:continue
 p=[o.matrix_world@v.co for v in o.data.vertices];rows.append({'name':o.name,'owner':o.parent.name,'role':o.get('surfaceRole'),'vertices':len(p),'polys':len(o.data.polygons),'mods':[m.type for m in o.modifiers],'min':[min(v[k] for v in p) for k in range(3)],'max':[max(v[k] for v in p) for k in range(3)]})
print(json.dumps(rows));Path('/tmp/v27-wing-terminal/geometry.json').write_text(json.dumps(rows,indent=2)+'\n');print('PIVOTS',[(n,tuple(bpy.data.objects[n].matrix_world.translation),dict(bpy.data.objects[n].items())) for n in ['left-mantle','right-mantle','left-wing-shield','right-wing-shield']])
