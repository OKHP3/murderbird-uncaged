"""Readback validation of final design API against each receiving09 era."""
import bpy,importlib.util,json,hashlib,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
def load(p):
 s=importlib.util.spec_from_file_location(p.stem.replace('-','_'),p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
h=load(BASE/'scripts/cg-supervised-head17.py');p=load(BASE/'scripts/cg-supervised-preservation.py');m=load(ROOT/'scripts/cg-recursive-head01.py')
results={}
for era in ['maker','mechanic']:
 inp=BASE/f'assets/models/cg-supervised01/attempt09/murderbird-supervised-{era}.blend';expected=json.loads((BASE/f'assets/audit/cg-supervised01/attempt09/{era}/receipt.json').read_text())['native_sha256'];assert m.sha(inp)==expected
 bpy.ops.wm.open_mainfile(filepath=str(inp));scene=bpy.context.scene;before=h.snap();images=p.packed_image_snapshot();p.retain_packed_image_ids(scene);changes=m.apply(scene,ROOT,era)
 native=ROOT/f'assets/models/cg-recursive-head01/murderbird-recursive-head01-attempt02-{era}.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(native));after=h.snap()
 result={'input_sha256':expected,'native_sha256':m.sha(native),'receiving_mesh_empty_count':len(before['objects']),'payload_changes':[n for n,v in before['objects'].items() if after['objects'].get(n)!=v],'material_changes':[n for n,v in before['materials'].items() if after['materials'].get(n)!=v],'file_image_changes':[n for n,v in before['images'].items() if v['source']=='FILE' and after['images'].get(n)!=v],'packed_images':p.verify_receiving_images(images),'visibility_changes':[n for n,v in before['visibility'].items() if after['visibility'].get(n)!=v],'changes':changes,'new_meshes':[]}
 for name in changes['added_objects']:
  o=bpy.context.scene.objects[name];uv=[c for d in o.data.uv_layers.active.data for c in d.uv];result['new_meshes'].append({'name':name,'vertices':len(o.data.vertices),'finite':all(math.isfinite(c) for v in o.data.vertices for c in v.co),'uv_range':[min(uv),max(uv)]})
 assert not any(result[k] for k in ['payload_changes','material_changes','file_image_changes']);assert set(result['visibility_changes'])==set(changes['hidden_originals']);assert all(r['finite'] for r in result['new_meshes']);assert all(o.data.materials[0].get('cgMetal05Era')==era for n in changes['added_objects'] for o in [bpy.context.scene.objects[n]])
 results[era]=result;(ROOT/'assets/audit/cg-recursive-head01/attempt02/era-api-readback.json').write_text(json.dumps(results,indent=2)+'\n');print('ERA_API_READBACK_PASS',era,len(result['new_meshes']),flush=True)
