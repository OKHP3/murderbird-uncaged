"""Read-only apply17 determinism/original checks against all three immutable06 eras."""
import bpy,json,hashlib,importlib.util
from pathlib import Path
W=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
spec=importlib.util.spec_from_file_location('head17',W/'scripts/cg-supervised-head17.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
results={}
for era in ['builder','maker','mechanic']:
 path=R/'assets/models/cg-supervised01/attempt06'/('murderbird-supervised-'+era+'.blend');row={'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'runs':[]}
 for i in range(2):
  bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;before=h.snap();r=h.apply(s,W,era);after=h.snap()
  payload={n:h.digest(s.objects[n]) for n in r['new_objects']};row['runs'].append({'new_geometry_digest':hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest(),'new_objects':r['new_objects'],'materials':r['receiving_materials'],'changed_original_payloads':[n for n,v in before['objects'].items() if after['objects'].get(n)!=v],'changed_materials':[n for n,v in before['materials'].items() if after['materials'].get(n)!=v]})
 row['deterministic']=row['runs'][0]['new_geometry_digest']==row['runs'][1]['new_geometry_digest'];row['input_unchanged']=hashlib.sha256(path.read_bytes()).hexdigest()==row['input_sha256'];results[era]=row
 (O/'era-api-check.json').write_text(json.dumps(results,indent=2));print('ERA_API',era,row,flush=True)
