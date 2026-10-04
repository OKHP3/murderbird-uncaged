"""Compare saved02/03 geometry, visibility, light state and noncore shaders."""
from pathlib import Path
import bpy, json, importlib.util
root=Path(__file__).resolve().parents[4]
out=root/'assets/audit/cg-supervised-optic07/attempt03'
spec=importlib.util.spec_from_file_location('optic',root/'scripts/cg-supervised-optic07.py');o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
def value(v):
 if isinstance(v,(int,float,str,bool)):return v
 try:return list(v)
 except TypeError:return str(v)
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
 geometry={x.name:(o.digest(x),x.hide_render,x.hide_get()) for x in s.objects if x.type in ('MESH','EMPTY')}
 graphs={}
 for m in bpy.data.materials:
  if not m.use_nodes or m.get('cgOptic07Role')=='core':continue
  graphs[m.name]={'nodes':[(n.name,n.type,[(i.name,value(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in m.node_tree.nodes], 'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]}
 lights={x.name:(tuple(x.location),tuple(x.rotation_euler),x.data.energy,tuple(x.data.color),x.data.size,x.hide_render) for x in s.objects if x.type=='LIGHT'}
 return geometry,graphs,lights
before=snapshot(root/'assets/audit/cg-supervised-optic07/attempt02/murderbird-optic07.blend');after=snapshot(out/'murderbird-optic07.blend')
changes={name:[k for k in a if k not in b or a[k]!=b[k]]+['ADDED:'+k for k in b if k not in a] for name,a,b in zip(('geometryVisibility','noncoreMaterialGraphs','lights'),before,after)}
assert not any(changes.values()),changes
(out/'delta-readback.json').write_text(json.dumps({'comparedToAttempt02':'f95fa805584fd23b58f18a77c19c1428de90042c','originalAndAddedMeshesEmptiesChecked':len(before[0]),'noncoreMaterialsChecked':len(before[1]),'geometryVisibilityAndLightingChanges':changes,'result':'PASS; only Advanced core shader changes'},indent=2)+'\n')
print('DELTA_READBACK_PASS')
