from pathlib import Path
import bpy,json,runpy,hashlib
R=Path('/Users/okh/.codex/worktrees/v38-facial-fit/murderbird-uncaged');A=Path(__file__).resolve().parent;N=R/'assets/models/whole-character-v38/facial-fit01/attempt02/murderbird-v38-facial-fit01-attempt02.blend'
bpy.ops.wm.open_mainfile(filepath=str(N));bpy.context.view_layer.update();fn=runpy.run_path(str(R/'scripts/regions/v38-facial-fit01.py'))['intersect_volume'];rows=[]
for s in[-1,1]:
 a=bpy.data.objects[f'V31 optic recessed receiving cup {s}'];b=bpy.data.objects[f'V38 facial-shell cheek bridge {s}'];rows.append({'identities':[a.name,b.name],'role':'Compact cup lower peripheral receiving overlap on formed cheek bridge, same rigid head assembly; not a moving part penetration exemption.','finiteCommonStock':fn(a,b)})
(A/'cup-cheek-stock.json').write_text(json.dumps({'recipeSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'nativeSHA256':hashlib.sha256(N.read_bytes()).hexdigest(),'contactProof':rows,'limitations':'Static finite stock/Boolean result; not strength/manufacturing certificate. Strict pair counts preserved in pre-freeze report; no shared-parent waiver.'},indent=2)+'\n');print(rows)
