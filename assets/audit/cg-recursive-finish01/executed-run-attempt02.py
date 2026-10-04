from pathlib import Path
import bpy, importlib.util, json, sys, hashlib
from types import SimpleNamespace
ROOT=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');OWN=Path(__file__).resolve().parents[3]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
 s=importlib.util.spec_from_file_location(Path(p).stem.replace('-','_'),p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];era=args[0] if args else 'builder';expand='expand' in args
out=OWN/'assets/audit/cg-recursive-finish01'/'attempt02'/era;out.mkdir(parents=True,exist_ok=True)
delivery=load(ROOT/'scripts/cg-recursive-delivery01.py');strong=load(ROOT/'scripts/cg-supervised-head17.py');payload=load(ROOT/'scripts/cg-supervised-body12.py');pres=load(ROOT/'scripts/cg-supervised-preservation.py');body=load(ROOT/'scripts/cg-recursive-body01.py');finish=load(OWN/'scripts/cg-recursive-finish01.py')
assert sha(ROOT/'scripts/cg-recursive-body01.py')=='f4d2ece4d97d64946ecda97dde24713d69b9ea5c361927b30c6491dd999e124e'
inp=ROOT/'assets/models/cg-supervised01/attempt09'/f'murderbird-supervised-{era}.blend'
bpy.ops.wm.open_mainfile(filepath=str(inp));scene=bpy.context.scene;before=delivery.snapshot(scene,strong,payload)
receipt=dict(input=str(inp),inputSHA=sha(inp),finishScriptSHA=sha(OWN/'scripts/cg-recursive-finish01.py'),bodyScriptSHA=sha(ROOT/'scripts/cg-recursive-body01.py'),era=era,originalCounts={k:len(v) for k,v in before.items()},status='IN_PROGRESS')
(out/'receiving-snapshot.json').write_text(json.dumps(before,indent=2));camera=json.loads((ROOT/'assets/audit/cg-supervised01/attempt09'/era/'receipt.json').read_text());renderargs=SimpleNamespace(samples=6,resolution=640)
br=body.apply(scene,ROOT,era);receipt['body']=br
baseline=out/'before';baseline.mkdir();receipt['beforeRenders']=delivery.render_views(scene,camera,['canon-neutral','canon-workshop'],baseline,renderargs)
fr=finish.apply(scene,ROOT,era);receipt['finish']=fr
declared={n:dict(name=n,hide_set=True) for n in set(br['hideOverrides'])|set(fr['hideOverrides']) if n in before['visibility']}
receipt['beforeSaveCustody']=delivery.verify(scene,before,strong,payload,declared)
pres.retain_packed_image_ids(scene);native=OWN/'assets/models/cg-recursive-finish01'/'attempt02'/f'murderbird-finish01-{era}.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene
receipt['saveReopenCustody']=delivery.verify(scene,before,strong,payload,declared);receipt['nativeSHA']=sha(native);receipt['native']=str(native)
candidate=out/'candidate';candidate.mkdir();keys=['canon-neutral','canon-workshop'];
if expand:keys+=['head-neck','body-detail','side-profile','neutral-180']
receipt['candidateRenders']=delivery.render_views(scene,camera,keys,candidate,renderargs);receipt['afterRenderCustody']=delivery.verify(scene,before,strong,payload,declared)
receipt['status']='PASS';(out/'receipt.json').write_text(json.dumps(receipt,indent=2));print('FINISH01_COMPLETE',str(out),flush=True)
