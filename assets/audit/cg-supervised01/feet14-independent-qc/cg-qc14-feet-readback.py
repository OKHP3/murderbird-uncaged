import bpy,importlib.util,json,math,hashlib,time
from pathlib import Path
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');W=Path('/Users/okh/.codex/worktrees/cg-supervised-foot-cover14/murderbird-uncaged');O=Path('/tmp/cg-qc14-feet-native.json')
def mod(n):
 s=importlib.util.spec_from_file_location(n,W/'scripts'/n);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
body=mod('cg-supervised-body12.py');pres=mod('cg-supervised-preservation.py');feet=mod('cg-supervised-feet14.py');ex=mod('cg-supervised-export.py')
manifest=json.loads((R/'assets/audit/cg-supervised01/feet-macro-diagnosis.json').read_text())['one_authoring_brief']['hide_manifest']['exact_names']
assert len(manifest)==74 and set(feet.whitelist())==set(manifest)
report={'exact74Allowlist':True,'eras':{},'readonly':True,'threads':2};new={}
for era in ['builder','maker','mechanic']:
 src=R/f'assets/models/cg-supervised01/attempt06/murderbird-supervised-{era}.blend'
 dst=W/('assets/audit/cg-supervised-feet14/replicated02/murderbird-feet14.blend' if era=='builder' else f'assets/audit/cg-supervised-feet14/replicated02/era-readback/murderbird-feet14-{era}.blend')
 bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
 old={o.name:body.digest(o) for o in s.objects if o.type in ('MESH','EMPTY')};vis={o.name:[o.hide_render,o.hide_viewport,o.hide_get()] for o in s.objects};imgs=pres.packed_image_snapshot();mats=body.material_digest()
 bpy.ops.wm.open_mainfile(filepath=str(dst));s=bpy.context.scene
 changed=[n for n,d in old.items() if n not in s.objects or body.digest(s.objects[n])!=d]
 flags=[n for n,v in vis.items() if n not in s.objects or [s.objects[n].hide_render,s.objects[n].hide_viewport,s.objects[n].hide_get()]!=([True,v[1],v[2]] if n in manifest else v)]
 mesh=[o for o in s.objects if o.get(feet.TAG)];bad=[];dg=bpy.context.evaluated_depsgraph_get()
 for o in mesh:
  ev=o.evaluated_get(dg);d=ev.to_mesh()
  if not d.uv_layers or any(not math.isfinite(q) for v in d.vertices for q in v.co) or any(not math.isfinite(q) or not 0<=q<=1 for u in d.uv_layers for d in u.data for q in d.uv):bad.append(o.name)
  ev.to_mesh_clear()
 new[era]={o.name:ex._digest_mesh(o.data) for o in mesh}
 report['eras'][era]={'originalCount':len(old),'changed':changed,'visibilityFailures':flags,'packed':pres.verify_receiving_images(imgs),'materialGraphsEqual':body.material_digest()==mats,'newCount':len(mesh),'finiteNormalizedUVFailures':bad,'candidateSHA256':hashlib.sha256(dst.read_bytes()).hexdigest()}
 O.write_text(json.dumps(report,indent=2));print('QC14 ERA DONE',era,report['eras'][era],flush=True)
report['newGeometryThreeEraEqual']=new['builder']==new['maker']==new['mechanic']
bpy.ops.wm.open_mainfile(filepath=str(R/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'));feet.apply(bpy.context.scene,R);fresh={o.name:ex._digest_mesh(o.data) for o in bpy.context.scene.objects if o.get(feet.TAG)};report['freshApplyMatchesSaved']=fresh==new['builder'];O.write_text(json.dumps(report,indent=2));print('QC14 COMPLETE',flush=True)
