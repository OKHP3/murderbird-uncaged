import bpy,json,hashlib,importlib.util
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'assets/audit/cg-supervised-head03';I=R/'assets/models/cg-supervised01/attempt01/murderbird-supervised-builder.blend'
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,default=str).encode()).hexdigest()
def snap():
 result={}
 for o in bpy.context.scene.objects:
  if o.type not in ('MESH','EMPTY'):continue
  q={'type':o.type,'matrix':[list(r) for r in o.matrix_world],'parent':o.parent.name if o.parent else None,'props':dict(o.items())}
  if o.type=='MESH':
   d=o.data;q.update(data_name=d.name,vertices=[list(v.co) for v in d.vertices],edges=[list(e.vertices) for e in d.edges],faces=[list(p.vertices) for p in d.polygons],slots=[m.name if m else None for m in d.materials],indices=[p.material_index for p in d.polygons],uv={l.name:[list(x.uv) for x in l.data] for l in d.uv_layers},colors={a.name:[list(x.color) for x in a.data] for a in d.color_attributes},modifiers=[(m.name,m.type) for m in o.modifiers])
  result[o.name]={'digest':digest(q),'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hide_set':o.hide_get(),'region':o.get('cg1cRegion'),'type':o.type}
 return result
bpy.ops.wm.open_mainfile(filepath=str(I));before=snap()
bpy.ops.wm.open_mainfile(filepath=str(O/'source-head03.blend'));after=snap()
changed=[n for n,q in before.items() if n not in after or q['digest']!=after[n]['digest']]
visibility=[n for n,q in before.items() if n in after and any(q[k]!=after[n][k] for k in ('hide_render','hide_viewport','hide_set'))]
wrong_vis=[n for n in visibility if before[n]['region']!='head' or before[n]['type']!='MESH']
new=[o for o in bpy.context.scene.objects if o.get('cgSupervisedHead03')]
slots=[o.name for o in new if len(json.loads(o['cgSurfaceFamilies']))!=len(o.data.materials)]
receipt={'original_objects':len(before),'original_meshes':sum(q['type']=='MESH' for q in before.values()),'original_anchors':sum(q['type']=='EMPTY' for q in before.values()),'changed_geometry_transform_parent_props_uv_colors_material_slots_indices_modifiers':changed,'visibility_changes':visibility,'non_head_visibility_changes':wrong_vis,'new_meshes':len(new),'invalid_slot_family_count':slots,'native_sha256':hashlib.sha256((O/'source-head03.blend').read_bytes()).hexdigest(),'input_sha256':hashlib.sha256(I.read_bytes()).hexdigest(),'era_optics':{}}
spec=importlib.util.spec_from_file_location('h03',R/'scripts/cg-supervised-head03.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for era in ['maker','mechanic']:
 bpy.ops.wm.open_mainfile(filepath=str(I));m.apply(bpy.context.scene,R,era)
 rows=[]
 for o in bpy.context.scene.objects:
  if o.get('cgSupervisedHead03') and o.get('surfaceRole') in ('optic','optic-core'):
   bs=o.data.materials[0].node_tree.nodes.get('Principled BSDF');rows.append({'name':o.name,'emission':bs.inputs['Emission Strength'].default_value})
 receipt['era_optics'][era]=rows
receipt['status']='PASS' if not changed and not wrong_vis and not slots and all(x['emission']==0 for v in receipt['era_optics'].values() for x in v) else 'FAIL'
(O/'preservation.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PRESERVATION',receipt['status'],len(changed),len(wrong_vis))
