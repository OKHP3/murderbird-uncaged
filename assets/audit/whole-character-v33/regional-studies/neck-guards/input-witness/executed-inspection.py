from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path(__file__).parent
N=ROOT/'assets/models/whole-character-v32/attempt-form01/murderbird-whole-character-v32.blend';assert hashlib.sha256(N.read_bytes()).hexdigest()=='676c7226c57d492c6f63e1ce873c1d89e6222fdd46d4ec954aa4ec0db26bc26f';bpy.ops.wm.open_mainfile(filepath=str(N));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();items=[]
for o in bpy.data.objects:
 if o.type!='MESH' or not(o.name.startswith('V23 cervical ') and 'directional guard' in o.name or o.name.startswith('V24 rising thoracic receiving cheek')):continue
 e=o.evaluated_get(dg);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];items.append({'name':o.name,'owner':o.parent.name,'baseVertices':len(o.data.vertices),'evaluatedVertices':len(v),'modifiers':[(q.name,q.type) for q in o.modifiers],'bounds':[[min(p[k] for p in v),max(p[k] for p in v)] for k in range(3)]});e.to_mesh_clear()
poses=json.loads((ROOT/'assets/audit/whole-character-v32/attempt-form01/neck-screen/screen.json').read_text())['poses']
result={'inputSHA256':hashlib.sha256(N.read_bytes()).hexdigest(),'pivots':{n:list(bpy.data.objects[n].matrix_world.translation) for n in ['neck','cervical-mid-a','cervical-mid-b','cervical-upper','head']},'parts':items,'currentSevenPoseWitnesses':poses}
(OUT/'inspection.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'pivots':result['pivots'],'samples':[(i['name'],i['baseVertices'],i['evaluatedVertices'],i['bounds']) for i in items[:10]]}),flush=True)
