import bpy,json,hashlib,sys
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');P=R/'assets/audit/cg-recursive-three-loop01/loop01';static=json.loads(Path('/tmp/cg-recursive-loop01-final-safety-static.json').read_text());rep={}
for era in ['builder','maker','mechanic']:
 bpy.ops.wm.open_mainfile(filepath=str(P/f'delivery/retained02/{era}/murderbird-recursive-{era}.blend'));bpy.context.view_layer.update();s=bpy.context.scene;layer=bpy.context.view_layer;dg=bpy.context.evaluated_depsgraph_get();counts=Counter();visible=0;images={};roles=[]
 for o in s.objects:
  if o.type!='MESH' or o.hide_render or o.hide_viewport or not o.visible_get(view_layer=layer) or o.hide_get(view_layer=layer) or o.get('authoringGuide'):continue
  visible+=1;e=o.evaluated_get(dg);m=e.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
  try:
   m.calc_loop_triangles()
   for t in m.loop_triangles:counts[m.materials[t.material_index].name]+=1
  finally:e.to_mesh_clear()
 for im in bpy.data.images:
  if im.packed_file:images[im.name]={'sha256':hashlib.sha256(bytes(im.packed_file.data)).hexdigest(),'size':list(im.size),'filepath':im.filepath,'colorspace':im.colorspace_settings.name}
 used=[m for m in bpy.data.materials if m.name in counts]
 for m in used:
  roles.append({'name':m.name,'family':m.get('cgMetal05Family'),'era':m.get('cgMetal05Era'),'images':[{'node':n.name,'image':n.image.name,'filepath':n.image.filepath} for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if m.node_tree else []})
 exported=static['glbs'][era]['images'];exact={x['name']:[k for k,v in images.items() if v['sha256']==x['sha256']] for x in exported};unmatched=[k for k,v in exact.items() if not v]
 rep[era]={'visible_native_meshes':visible,'triangles':sum(counts.values()),'triangles_by_material':dict(counts),'glb_native_material_triangle_counts_exact':dict(counts)==static['glbs'][era]['triangles_by_material'],'glb_images_exact_packed_byte_matches':exact,'unmatched_glb_images':unmatched,'native_packed_images':images,'used_native_materials':roles}
 assert rep[era]['glb_native_material_triangle_counts_exact']
Path('/tmp/cg-recursive-loop01-final-safety-evaluated.json').write_text(json.dumps(rep,indent=2));print('INDEPENDENT_EVALUATED_READBACK',json.dumps({k:{a:b for a,b in v.items() if a not in ('native_packed_images','used_native_materials','triangles_by_material','glb_images_exact_packed_byte_matches')} for k,v in rep.items()}))
