import bpy,importlib.util,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'assets/audit/cg-supervised-head04';S=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');I=S/'assets/models/cg-supervised01/attempt03/murderbird-supervised-builder.blend'
sp=importlib.util.spec_from_file_location('head04',R/'scripts/cg-supervised-head04.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
res={}
for era in ('maker','mechanic','builder'):
 bpy.ops.wm.open_mainfile(filepath=str(I));s=bpy.context.scene;receipt=m.apply(s,R,era);new=[o for o in s.objects if o.get('cgSupervisedHead04')];cores=[o for o in new if o.get('surfaceRole')=='core'];glasses=[o for o in new if o.get('surfaceRole')=='glass'];bad=[o.name for o in new if len(json.loads(o['cgSurfaceFamilies']))!=len(o.data.materials)];em=[o.data.materials[0].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value for o in cores]
 res[era]={'new_meshes':len(new),'invalid_family_counts':bad,'core_emission_strengths':em,'glass_transmission':[o.data.materials[0].node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value for o in glasses],'pass':not bad and all(v==(.8 if era=='builder' else 0) or abs(v-.8)<1e-6 and era=='builder' for v in em)}
 assert res[era]['pass']
res['render_scope']='Blender diagnostics only. Browser and runtime checks are integrator work; no runtime asset changes.'
(O/'validation.json').write_text(json.dumps(res,indent=2)+'\n')
