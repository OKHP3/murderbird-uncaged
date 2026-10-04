import bpy,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;INP=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
bpy.ops.wm.open_mainfile(filepath=str(INP/'assets/audit/cg-supervised-body05/attempt02/murderbird-body05.blend'))
sp=importlib.util.spec_from_file_location('metal',ROOT.parents[2]/'scripts/cg-supervised-metal05.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);f=m.helper(INP)
digests={o.name:f.digest(o) for o in bpy.context.scene.objects if o.type=='MESH' and not o.get('authoringGuide')}
expected=json.loads((ROOT/'attempt02/metal05-builder-receipt.json').read_text())['preservation']['before_digest'];actual=m.aggregate(digests)
assert actual==expected,(actual,expected)
(ROOT/'input-preservation.json').write_text(json.dumps({'input_meshes':len(digests),'input_digest':actual,'correct_linear_baseline_digest':expected,'same_geometry_uv_transforms_slot_counts_indices':actual==expected},indent=2)+'\n')
print('INPUT_DIGEST_PASS',len(digests),actual)
