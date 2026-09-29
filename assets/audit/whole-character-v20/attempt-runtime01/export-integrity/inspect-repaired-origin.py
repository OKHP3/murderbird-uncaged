from pathlib import Path
import bpy,json,hashlib
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=ROOT/'assets/audit/whole-character-v20/attempt-runtime01/export-integrity';result=[]
for label,p in [('v19',ROOT/'assets/models/whole-character-v19/attempt-02/murderbird-whole-character-v19.blend'),('runtime01',ROOT/'assets/models/whole-character-v20/attempt-runtime01/murderbird-whole-character-v20.blend')]:
 sha=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p));o=bpy.data.objects['V17 breast directional lamina 1 1 left'];result.append({'label':label,'mergedGroupActiveObject':o.name,'parent':o.parent.name,'worldOriginNative':list(o.matrix_world.translation),'worldMatrix':[list(r) for r in o.matrix_world],'repairEffect':'Exporter Mesh.validate substitutes nonfinite source coordinates with group-local(0,0,0), pulling incident geometry to this world origin, not to the tiny source seam location.'});assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
(OUT/'repaired-origin.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
