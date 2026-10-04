import bpy,importlib.util,json,hashlib
from pathlib import Path
ROOT=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');OWN=Path(__file__).resolve().parents[3]
p=ROOT/'scripts/cg-supervised-export.py';s=importlib.util.spec_from_file_location('finish01_export',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
native=OWN/'assets/models/cg-recursive-finish01/attempt02/murderbird-finish01-builder.blend';h=hashlib.sha256(native.read_bytes()).hexdigest()
out=OWN/'assets/models/cg-recursive-finish01/attempt02/murderbird-finish01-builder.glb'
r=m.export(bpy.context.scene,out,batched=True);r['scope']='Diagnostic of second failed visual attempt; not root-retained or owner-accepted';r['nativeSHA']=h;r['nativeUnchanged']=hashlib.sha256(native.read_bytes()).hexdigest()==h
(OWN/'assets/audit/cg-recursive-finish01/attempt02/builder/export-parity.json').write_text(json.dumps(r,indent=2)+'\n');print('FINISH01_EXPORT_COMPLETE',flush=True)
