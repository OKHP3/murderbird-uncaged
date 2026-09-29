import bpy,runpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[4]
h=runpy.run_path(str(root/'scripts/build-uncaged-alignment-v7.py'))
bpy.ops.wm.open_mainfile(filepath=str(root/'assets/models/whole-character-v18/attempt-01/murderbird-whole-character-v18.blend'))
a=h['scene_snapshot']()
runpy.run_path(str(root/'scripts/regions/whole-character-v19-torso-neck.py'))['apply']()
b=h['scene_snapshot']();out=[]
for n,x in a['curves'].items():
 y=b['curves'][n]
 if x!=y:
  out.append({'name':n,'maxMatrixDelta':max(abs(x['matrix'][r][c]-y['matrix'][r][c]) for r in range(4) for c in range(4)),'differingKeys':[k for k in x if x[k]!=y[k]]})
print(json.dumps(out,indent=2));(root/'assets/audit/whole-character-v19/torso-work/curve-rest-differences.json').write_text(json.dumps(out,indent=2))
