from pathlib import Path
import bpy,runpy,json
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');h=runpy.run_path(str(R/'scripts/build-uncaged-alignment-v7.py'));bpy.ops.wm.open_mainfile(filepath=str(R/'assets/models/whole-character-v30/attempt-form02/murderbird-whole-character-v30.blend'));r=runpy.run_path('/tmp/v31-head-reconstruction/attempt01/executed-head-reconstruction.py')['apply']();a=h['scene_snapshot']();bpy.ops.wm.open_mainfile(filepath='/tmp/v31-head-reconstruction/attempt01/head-reconstruction.blend');b=h['scene_snapshot']();out={'result':r,'difference':{}}
for k in a:
 if a[k]==b[k]:continue
 if isinstance(a[k],dict):
  out['difference'][k]={n:{'before':a[k].get(n),'after':b[k].get(n)} for n in set(a[k])|set(b[k]) if a[k].get(n)!=b[k].get(n)}
 else:out['difference'][k]={'before':a[k],'after':b[k]}
Path('/tmp/v31-head-reconstruction/attempt01/reopen-diagnosis.json').write_text(json.dumps(out,indent=2,default=str));print({k:list(v) if isinstance(v,dict) else 'other' for k,v in out['difference'].items()})
