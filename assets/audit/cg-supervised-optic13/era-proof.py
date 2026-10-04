import bpy,importlib.util,json,hashlib
from pathlib import Path
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
W=Path('/Users/okh/.codex/worktrees/cg-supervised-optic-area13/murderbird-uncaged')
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
mod=load(W/'scripts/cg-supervised-optic13.py','optic13');hist=load(R/'scripts/cg-supervised-preservation.py','hist');audit=load(R/'scripts/cg-supervised-body12.py','audit');report={}
for era in ['maker','mechanic']:
 path=R/'assets/models/cg-supervised01/attempt06'/('murderbird-supervised-'+era+'.blend');before_sha=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False);s=bpy.context.scene
 snapshot=hist.packed_image_snapshot();original={o.name:audit.digest(o) for o in s.objects if o.type in ('MESH','EMPTY')};mats=audit.material_digest();q=mod.apply(s,R,era);hist.verify_receiving_images(snapshot)
 assert all(audit.digest(s.objects[n])==d for n,d in original.items());now=audit.material_digest();assert all(now[n]==d for n,d in mats.items())
 emiss=[(m.name,m.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value) for m in bpy.data.materials if m.get('cgOptic13Role')];assert all(v==0 for _,v in emiss)
 report[era]={'apply':q,'receivingObjects':len(original),'receivingPackedImages':len(snapshot),'newMaterialEmissionStrengths':emiss,'sourceSHA256':before_sha,'sourceUnchanged':hashlib.sha256(path.read_bytes()).hexdigest()==before_sha,'nativeSaveReopen':'Root integration owns era save/reopen; this is actual API/in-memory validation only'}
(W/'assets/audit/cg-supervised-optic13/era-proof.json').write_text(json.dumps(report,indent=2)+'\n')
