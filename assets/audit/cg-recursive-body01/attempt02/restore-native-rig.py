import bpy,hashlib,json,importlib.util
from pathlib import Path
root=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');own=Path('/Users/okh/.codex/worktrees/cg-supervised-oblique-breast15/murderbird-uncaged');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('audit',root/'scripts/cg-supervised-body12.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for era in ('builder','maker'):
 inp=root/'assets/models/cg-supervised01/attempt09'/f'murderbird-supervised-{era}.blend';bpy.ops.wm.open_mainfile(filepath=str(inp));s=bpy.context.scene;rig={o.name:dict(location=list(o.location),rotation=list(o.rotation_euler),scale=list(o.scale),data=dict(type=o.data.type,ortho_scale=o.data.ortho_scale,lens=o.data.lens,shift_x=o.data.shift_x,shift_y=o.data.shift_y) if o.type=='CAMERA' else dict(energy=o.data.energy,color=list(o.data.color),size=o.data.size)) for o in s.objects if o.type in ('CAMERA','LIGHT')};b=s.world.node_tree.nodes.get('Background');world=[list(b.inputs[0].default_value),b.inputs[1].default_value];src=own/'assets/models/cg-recursive-body01/attempt02'/f'murderbird-recursive-body-{era}.blend';sourcehash=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;payload={o.name:m.digest(o) for o in s.objects if o.type in ('MESH','EMPTY')}
 for n,q in rig.items():
  o=s.objects[n];o.location=q['location'];o.rotation_euler=q['rotation'];o.scale=q['scale']
  for k,v in q['data'].items():setattr(o.data,k,v)
 b=s.world.node_tree.nodes.get('Background');b.inputs[0].default_value=world[0];b.inputs[1].default_value=world[1];bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;out=src.with_name(src.stem+'-rig-restored.blend');bpy.ops.wm.save_as_mainfile(filepath=str(out),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(out));s=bpy.context.scene;assert all(m.digest(s.objects[n])==v for n,v in payload.items());assert sha(src)==sourcehash
 for n,q in rig.items():
  o=s.objects[n];assert list(o.location)==q['location'] and list(o.rotation_euler)==q['rotation'] and list(o.scale)==q['scale']
  for k,v in q['data'].items():
   actual=getattr(o.data,k);actual=list(actual) if k=='color' else actual;assert actual==v,(n,k,actual,v)
 rpath=own/'assets/audit/cg-recursive-body01/attempt02'/era/'receipt.json';r=json.loads(rpath.read_text());r['rigRestoredNative']=dict(path=str(out),SHA256=sha(out),receivingCameraLightTransformsAndDataExact=True,receivingWorldRestored=True,allCandidateAndOriginalMeshEmptyPayloadsExact=True,earlierDiagnosticNativeRetained=True);rpath.write_text(json.dumps(r,indent=2)+'\n');print('RESTORED_NATIVE',out,flush=True)
