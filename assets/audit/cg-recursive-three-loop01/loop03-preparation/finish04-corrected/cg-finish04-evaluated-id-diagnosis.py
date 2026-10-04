import bpy,json,hashlib,datetime
from pathlib import Path
p=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged/assets/audit/cg-recursive-three-loop01/loop02/delivery/retained03/builder/murderbird-recursive-builder.blend')
expected='86fee36a8df80f8bcaa3bba7e1c0ecc1dfc56fde178a708323949c2d23ba6288'
assert hashlib.sha256(p.read_bytes()).hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(p))
o=bpy.data.objects['CGH17 frontal crown root'];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=e.to_mesh();a=o.data.materials[2];b=mesh.materials[2]
def identity(x):
 return {'name':x.name,'pointer':x.as_pointer(),'is_evaluated':x.is_evaluated,'original_name':x.original.name,'original_pointer':x.original.as_pointer()}
def images(m):
 out=[]
 if m.node_tree:
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE':
    i=n.image
    out.append({'node':n.name,'image':identity(i) if i else None,'source':i.source if i else None,'packed_bytes':len(i.packed_file.data) if i and i.packed_file else None,'packed_sha256':hashlib.sha256(bytes(i.packed_file.data)).hexdigest() if i and i.packed_file else None})
 return out
ai=images(a);bi=images(b)
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native_path':str(p),'native_sha256':expected,'object':o.name,'scope':'Untouched original source only, direct depsgraph evaluation; no producer imports, material/visibility/scene edits, save/render/export.','faces_source':len(o.data.polygons),'faces_evaluated':len(mesh.polygons),'source_face_material_indices':sorted(set(x.material_index for x in o.data.polygons)),'evaluated_face_material_indices':sorted(set(x.material_index for x in mesh.polygons)),'source_slot2':identity(a),'evaluated_slot2':identity(b),'predicates':{'python_equal':b==a,'pointer_equal':b.as_pointer()==a.as_pointer(),'names_equal':b.name==a.name,'evaluated_original_equal_source':b.original==a,'evaluated_original_pointer_equal_source':b.original.as_pointer()==a.as_pointer(),'both_original_pointer_equal':b.original.as_pointer()==a.original.as_pointer(),'image_node_counts_equal':len(ai)==len(bi),'image_node_packed_hash_pairs_equal':[(x['node'],x['packed_sha256']) for x in ai]==[(x['node'],x['packed_sha256']) for x in bi]},'source_image_nodes':ai,'evaluated_image_nodes':bi,'limits':'Control establishes evaluated ID alias behavior only. It does not validate any stopped trial material, slot assignment or shading.','next_test':'If untouched control pointer equality is false but original identity and image bytes match, compare evaluated material.original identity to expected source original with face slots and explicit packed-map hashes. Any trial would require its own separately authorized validation; no failed method rerun authorized.'}
e.to_mesh_clear();r['native_sha256_after']=hashlib.sha256(p.read_bytes()).hexdigest()
Path('/tmp/cg-finish04-evaluated-id-diagnosis.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
