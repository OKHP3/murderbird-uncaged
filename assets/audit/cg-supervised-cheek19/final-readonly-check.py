import bpy,importlib.util,json,math,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parents[2];B=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
s=importlib.util.spec_from_file_location('h17',W/'scripts/cg-supervised-head17.py');h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
I=B/'assets/audit/cg-supervised-bill18/attempt02/formed-bill18.blend';F=R/'attempt01/formed-cheek19.blend'
bpy.ops.wm.open_mainfile(filepath=str(I));before=h.snap();bpy.ops.wm.open_mainfile(filepath=str(F));after=h.snap();sc=bpy.context.scene
r={'native_sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'receiving_objects':len(before['objects']),'original_payload_changes':[n for n,v in before['objects'].items() if after['objects'].get(n)!=v],'material_graph_count':len(after['materials']),'original_graph_changes':[n for n,v in before['materials'].items() if after['materials'].get(n)!=v],'FILE_metadata_changes':[n for n,v in before['images'].items() if v['source']=='FILE' and after['images'].get(n)!=v],'original_visibility_changes':[n for n,v in before['visibility'].items() if after['visibility'].get(n)!=v],'new_materials':sorted(set(after['materials'])-set(before['materials'])),'new_meshes':[]}
for o in sc.objects:
 if o.get('cgSupervisedCheek19'):
  e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();uv=[v for d in m.uv_layers.active.data for v in d.uv];r['new_meshes'].append({'name':o.name,'visible':not o.hide_render and not o.hide_get(),'cage_vertices':len(o.data.vertices),'evaluated_vertices':len(m.vertices),'finite_coordinates':all(math.isfinite(v) for q in m.vertices for v in q.co),'finite_uv':all(math.isfinite(v) for v in uv),'uv_range':[min(uv),max(uv)],'material_slots':[m.name for m in o.data.materials]});e.to_mesh_clear()
(R/'final-native-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
assert not any(r[k] for k in ['original_payload_changes','original_graph_changes','FILE_metadata_changes','original_visibility_changes','new_materials'])
assert r['material_graph_count']==56 and len(r['new_meshes'])==4
assert all(q['visible'] and q['finite_coordinates'] and q['finite_uv'] for q in r['new_meshes'])
