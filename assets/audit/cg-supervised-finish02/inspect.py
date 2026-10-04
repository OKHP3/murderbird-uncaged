import bpy,json,numpy as np
from pathlib import Path
root=Path(__file__).resolve().parents[3]
bpy.ops.wm.open_mainfile(filepath=str(root/'assets/models/cg-supervised01/surface01/murderbird-supervised-builder.blend'))
result=[]
for m in bpy.data.materials:
 if not m.get('cg2bFamily'):continue
 row={'name':m.name,'family':m.get('cg2bFamily'),'nodes':[],'maps':{}}
 for n in m.node_tree.nodes:
  row['nodes'].append({'type':n.bl_idname,'label':n.label})
  if n.type=='TEX_IMAGE':
   a=np.empty(n.image.size[0]*n.image.size[1]*4,dtype=np.float32);n.image.pixels.foreach_get(a);a=a.reshape(-1,4)[:,:3]
   row['maps'][n.label]={'name':n.image.name,'space':n.image.colorspace_settings.name,'min':a.min(axis=0).tolist(),'mean':a.mean(axis=0).tolist(),'max':a.max(axis=0).tolist()}
 row['links']=[(l.from_node.label or l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]
 result.append(row)
(root/'assets/audit/cg-supervised-finish02/graph-before.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
