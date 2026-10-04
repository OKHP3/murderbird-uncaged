import bpy,hashlib,json,importlib.util
from pathlib import Path
from mathutils import Vector
r=Path('/Users/okh/.codex/worktrees/cg-supervised-anterior-cage11/murderbird-uncaged');a=r/'assets/audit/cg-supervised-body11';source=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged/assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend')
def scalar(block):
 data={}
 for p in block.bl_rna.properties:
  if p.is_readonly or p.type not in ('BOOLEAN','INT','FLOAT','STRING','ENUM'):continue
  try:
   v=getattr(block,p.identifier)
   if p.is_array:v=list(v)
   data[p.identifier]=v
  except Exception:pass
 return data
def audit():
 objects={}
 for o in bpy.context.scene.objects:
  vals={'matrix':[list(v) for v in o.matrix_world],'modifiers':[scalar(m) for m in o.modifiers],'constraints':[scalar(c) for c in o.constraints],'vertexGroupNames':[v.name for v in o.vertex_groups]}
  if o.type=='MESH':vals['attributeDefinitions']=[(v.name,v.domain,v.data_type,len(v.data)) for v in o.data.attributes]
  objects[o.name]=hashlib.sha256(json.dumps(vals,sort_keys=True).encode()).hexdigest()
 return objects
bpy.ops.wm.open_mainfile(filepath=str(source));old=audit()
result={'originalCount':len(old),'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'checks':'All original object world matrices, modifier/constraint writable scalar RNA parameters, vertex group names and mesh attribute definitions. Geometry/UV/color/metadata/material/packed-pixel checks are in native receipts.','attempts':{}}
for attempt in ['attempt01','attempt02']:
 native=a/attempt/'murderbird-body11.blend';bpy.ops.wm.open_mainfile(filepath=str(native));now=audit();diff=[n for n,d in old.items() if now.get(n)!=d];assert not diff,diff[:20]
 bounds={};deps=bpy.context.evaluated_depsgraph_get()
 for label,objects in [('receivingBreast',[o for o in bpy.context.scene.objects if 'CGB05 breast curved feather' in o.name]),('newCage',[o for o in bpy.context.scene.objects if o.get('cgSupervisedBody11')])]:
  points=[]
  for o in objects:
   ev=o.evaluated_get(deps);mesh=ev.to_mesh();points.extend([tuple(o.matrix_world@v.co) for v in mesh.vertices]);ev.to_mesh_clear()
  bounds[label]={'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]}
 result['attempts'][attempt]={'nativeSHA256':hashlib.sha256(native.read_bytes()).hexdigest(),'originalExtraPayloadChanges':diff,'bounds':bounds}
(a/'extra-preservation-and-extents.json').write_text(json.dumps(result,indent=2)+'\n');print('EXTRA_PASS',result)
