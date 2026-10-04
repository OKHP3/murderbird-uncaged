import bpy,json,hashlib,importlib.util,math
from pathlib import Path
root=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged'); worker=Path('/Users/okh/.codex/worktrees/cg-supervised-breast-planform13/murderbird-uncaged'); p=worker/'assets/audit/cg-supervised-body13/attempt01';r=json.loads((p/'receipt.json').read_text())
spec=importlib.util.spec_from_file_location('body12',root/'scripts/cg-supervised-body12.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def metadata():
 return {i.name:dict(items=dict(i.items()),size=list(i.size),channels=i.channels,alphaMode=i.alpha_mode,colorSpace=i.colorspace_settings.name,fileFormat=i.file_format,source=i.source,filepath=i.filepath,packedSHA256=hashlib.sha256(bytes(i.packed_file.data)).hexdigest()) for i in bpy.data.images if i.packed_file}
bpy.ops.wm.open_mainfile(filepath=str(root/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'))
s=bpy.context.scene; original={o.name:m.digest(o) for o in s.objects if o.type in ('MESH','EMPTY')}; vis={o.name:[o.hide_render,o.hide_viewport,o.hide_get()] for o in s.objects}; graphs=m.material_digest(); packed=m.packed_image_digest(); meta=metadata()
bpy.ops.wm.open_mainfile(filepath=str(p/'murderbird-body13.blend'));s=bpy.context.scene
changed=[n for n,h in original.items() if n not in s.objects or m.digest(s.objects[n])!=h];vc=[n for n,v in vis.items() if n not in m.HIDE_MANIFEST and (n not in s.objects or [s.objects[n].hide_render,s.objects[n].hide_viewport,s.objects[n].hide_get()]!=v)]
pts=[];uvbad=[];panels=[o for o in s.objects if o.get('cgSupervisedBody13') or o.get('cgSupervisedBody12')];deps=bpy.context.evaluated_depsgraph_get()
for o in panels:
 ev=o.evaluated_get(deps);md=ev.to_mesh();pts.extend(o.matrix_world@v.co for v in md.vertices)
 if any(not math.isfinite(c) or c< -1e-6 or c>1.000001 for l in md.uv_layers for uv in l.data for c in uv.uv):uvbad.append(o.name)
 ev.to_mesh_clear()
result=dict(originalCount=len(original),changed=changed,visibilityChangesOutsideWhitelist=vc,hideWhitelistCount=len(m.HIDE_MANIFEST),allWhitelistHidden=all(s.objects[n].hide_render and s.objects[n].hide_get() for n in m.HIDE_MANIFEST),graphsCount=len(graphs),graphsExact=graphs==m.material_digest(),packedCount=len(packed),packedIDsAndBytesExact=packed==m.packed_image_digest(),metadataExact=meta==metadata(),retained25Exact=all(m.digest(s.objects[n])==h for n,h in r['upperBody12RetainedDigests'].items()),guideHidden=s.objects[r['hiddenGuide']].hide_render and s.objects[r['hiddenGuide']].hide_get(),panelCount=len(panels),newPanelCount=sum(bool(o.get('cgSupervisedBody13')) for o in panels),evaluatedUVBad=uvbad,envelope=dict(min=[min(v[i] for v in pts) for i in range(3)],max=[max(v[i] for v in pts) for i in range(3)]),nativeSHA256=hashlib.sha256((p/'murderbird-body13.blend').read_bytes()).hexdigest())
Path('/tmp/cg-qc13-native-check.json').write_text(json.dumps(result,indent=2));print('QC13_NATIVE_CHECK',json.dumps(result),flush=True)
