import bpy,json,math,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
HEAD17=Path('/Users/okh/.codex/worktrees/cg-supervised-layered-crown17/murderbird-uncaged')
def load(p):
 s=importlib.util.spec_from_file_location('api18_'+p.stem,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=load(ROOT/'scripts/cg-supervised-bill18.py');h=load(HEAD17/'scripts/cg-supervised-head17.py');p=load(BASE/'scripts/cg-supervised-preservation.py');out=ROOT/'assets/audit/cg-supervised-bill18/api-check.json';result={}
for era in ['maker','mechanic','builder']:
 source=BASE/('assets/models/cg-supervised01/attempt06/murderbird-supervised-'+era+'.blend');bpy.ops.wm.open_mainfile(filepath=str(source));before=h.snap();maps=p.packed_image_snapshot();r=b.apply(bpy.context.scene,ROOT,era);after=h.snap();new={n:h.digest(bpy.context.scene.objects[n]) for n in r['new_objects']}
 rec={'input_sha256':b.sha(source),'receiving_originals':len(before['objects']),'materials':len(before['materials']),'packed':p.verify_receiving_images(maps),'payload_changes':[n for n,v in before['objects'].items() if after['objects'].get(n)!=v],'graph_changes':[n for n,v in before['materials'].items() if after['materials'].get(n)!=v],'file_image_changes':[n for n,v in before['images'].items() if v['source']=='FILE' and after['images'].get(n)!=v],'visibility_changes':[n for n,v in before['visibility'].items() if after['visibility'].get(n)!=v],'new_payloads':new,'new_objects':r['new_objects'],'same_era_materials':r['material_graphs']}
 assert not any(rec[k] for k in ['payload_changes','graph_changes','file_image_changes']);assert set(rec['visibility_changes'])==set(b.HIDE)
 bpy.ops.wm.open_mainfile(filepath=str(source));r2=b.apply(bpy.context.scene,ROOT,era);new2={n:h.digest(bpy.context.scene.objects[n]) for n in r2['new_objects']};rec['deterministic_reapply']=new==new2;assert rec['deterministic_reapply'];result[era]=rec;out.write_text(json.dumps(result,indent=2)+'\n');print('BILL18_API',era,'PASS',flush=True)
# Receiving17 native must reproduce exactly the same builder new payloads.
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/audit/cg-supervised-bill18/attempt02/formed-bill18.blend'));native={n:h.digest(bpy.context.scene.objects[n]) for n in result['builder']['new_objects']};result['standalone06_builder_equals_saved17_new_payloads']=native==result['builder']['new_payloads'];assert result['standalone06_builder_equals_saved17_new_payloads'];out.write_text(json.dumps(result,indent=2)+'\n');print('BILL18_ALL_API_PASS',flush=True)
