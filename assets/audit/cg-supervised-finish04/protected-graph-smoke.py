"""Synthetic optical-slot routing regression. No artistic assets or receipts changed."""
import bpy, importlib.util, json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent/'protected-graph-smoke'
spec=importlib.util.spec_from_file_location('finish04',ROOT/'scripts/cg-supervised-finish04.py');finish=importlib.util.module_from_spec(spec);spec.loader.exec_module(finish)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
bpy.ops.mesh.primitive_cube_add();obj=bpy.context.object;obj.name='Synthetic optical housing'
def material(name):
 mat=bpy.data.materials.new(name);mat.use_nodes=True;mat['cg2bFamily']='black-iron'
 mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.003,.003,.003,1)
 return mat
optic=material('Stale family optic');glass=material('Stale family glass');flagged=material('Preserve flag despite unprotected family');flagged['cg2aPreserveMaterial']=True
for mat in (optic,glass,flagged):obj.data.materials.append(mat)
obj['cgSurfaceFamilies']=json.dumps(['protected-optic','protected-glass','black-iron'])
def graph(mat):
 return {'material_pointer':mat.as_pointer(),'node_tree_pointer':mat.node_tree.as_pointer(),'nodes':[(n.as_pointer(),n.name,n.type,[(i.name,str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in mat.node_tree.nodes],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in mat.node_tree.links],'props':dict(mat.items())}
before=[graph(m) for m in obj.data.materials]
receipt=finish.apply(scene,OUT,'builder');after=[graph(m) for m in obj.data.materials]
assert before==after,'Protected graph identity changed'
assert receipt['assigned_slots']==0 and receipt['preserved_other_slots']['count']==3
assert len(receipt['preserved_other_slots']['first20names'])==3
report={'protected_stale_tag_graph_identity':'PASS','before':before,'after':after,'receipt':receipt}
# A truly unprotected malformed family must raise a contextual error.
obj['cgSurfaceFamilies']=json.dumps(['black-iron','protected-glass','black-iron'])
try:finish.apply(scene,OUT/'malformed','builder')
except ValueError as exc:
 report['malformed_unprotected_error']=str(exc)
 assert 'slot 0' in str(exc) and 'malformed unprotected' in str(exc) and 'color' in str(exc) and 'orm' in str(exc)
else:raise AssertionError('Malformed unprotected graph was not rejected')
assert before==[graph(m) for m in obj.data.materials]
# Ordered mapping count must not silently fall back to stale material tags.
obj['cgSurfaceFamilies']=json.dumps(['protected-optic'])
try:finish.apply(scene,OUT/'bad-slot-count','builder')
except ValueError as exc:report['slot_count_error']=str(exc)
else:raise AssertionError('Wrong explicit slot count was not rejected')
# One shared source material routed differently by ordered slot index.
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
bpy.ops.mesh.primitive_cube_add();obj=bpy.context.object;obj.name='Ordered routing witness'
mat=material('Shared stale black iron source');texnodes=mat.node_tree.nodes
import numpy as np
for label,value in (('color',(.1,.2,.1)),('orm',(1,.5,.6))):
 node=texnodes.new('ShaderNodeTexImage');node.label=label
 pixels=np.ones((8,8,4),np.float32);pixels[:,:,:3]=value
 im=bpy.data.images.new('Synthetic '+label,width=8,height=8);im.pixels.foreach_set(pixels.ravel());node.image=im
for i in range(2):obj.data.materials.append(mat)
obj['cgSurfaceFamilies']=json.dumps(['head-armor','breast-armor'])
routed=finish.apply(scene,OUT/'ordered-routing','builder')
assert [m['family'] for m in routed['materials']]==['head-armor','breast-armor']
assert obj.data.materials[0]!=obj.data.materials[1]
assert [m.get('cgFinish04Family') for m in obj.data.materials]==['head-armor','breast-armor']
report['ordered_slot_family_overrides_stale_shared_tag']='PASS'
report['ordered_routing_receipt']=routed
(OUT/'smoke.json').write_text(json.dumps(report,indent=2)+'\n')
print('PROTECTED_GRAPH_SMOKE_PASS')
