"""V25 uniform whole-head mass proposal on exact V24 Form02.

Native metres/Z-up/-Y-forward. Uniform1.30 authoring transform is baked into
vertices, finite modifier dimensions and descendant owner translations; runtime
object scaling is not used. Two cervical attachment shafts stay exact. This is
an authored proportion study, not a dimension inferred from reference pixels.
"""
import bpy,json,math
from mathutils import Vector
FACTOR=1.30
BOUNDARY=['V21 head captive shaft','V23 cervical 4 captive pin']
CONTACTS=['bill-contact','anchor-beak']
def props(o):return json.dumps(dict(o.items()),default=lambda x:list(x),sort_keys=True)
def mesh_snapshot(o):
 return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),props(o),o.hide_render,o.hide_viewport)
def node_snapshot(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),props(o))
def bounds(points):return [[min(p[k] for p in points) for k in range(3)],[max(p[k] for p in points) for k in range(3)]]
def depth(o):
 n=0
 while o.parent:n+=1;o=o.parent
 return n

def apply():
 bpy.context.view_layer.update();head=bpy.data.objects['head'];pivot=head.matrix_world.translation.copy();desc=list(head.children_recursive)
 nodes=[o for o in desc if o.type=='EMPTY'];meshes=[o for o in desc if o.type=='MESH' and o.name not in BOUNDARY]
 curve_world={o.name:o.matrix_world.copy() for o in bpy.data.objects if o.type=='CURVE'}
 node_before={o.name:node_snapshot(o) for o in bpy.data.objects if o.type=='EMPTY'}
 protected={o.name:mesh_snapshot(o) for o in bpy.data.objects if o.type=='MESH' and o not in meshes}
 old_nodes={o.name:o.matrix_world.copy() for o in nodes}
 original={o.name:[o.matrix_world@v.co for v in o.data.vertices] for o in meshes}
 boundary_world={n:bpy.data.objects[n].matrix_world.copy() for n in BOUNDARY}
 def mapped(p):return pivot+FACTOR*(p-pivot)
 transforms=[]
 for o in sorted(nodes,key=depth):
  old=old_nodes[o.name];m=old.copy();m.translation=mapped(old.translation);o.matrix_world=m;bpy.context.view_layer.update()
  transforms.append({'name':o.name,'parent':o.parent.name,'beforeWorld':list(old.translation),'afterWorld':list(o.matrix_world.translation),'afterOwnerLocal':list(o.matrix_local.translation),'worldBasisMaxDelta':max(abs(o.matrix_world[r][c]-old[r][c]) for r in range(3) for c in range(3))})
 # Parent synchronization is explicit BEFORE every inverse used for vertices.
 bpy.context.view_layer.update();point_errors=[];modifier_changes=[]
 for o in meshes:
  o.data=o.data.copy();o.data.name=o.name+' V25 whole-head mass'
  inv=o.matrix_world.inverted()
  for v,p in zip(o.data.vertices,original[o.name]):v.co=inv@mapped(p)
  o.data.update()
  for mod in o.modifiers:
   keys={'SOLIDIFY':['thickness'],'BEVEL':['width'],'WELD':['merge_threshold']}.get(mod.type,[])
   for key in keys:
    old=getattr(mod,key);setattr(mod,key,old*FACTOR);modifier_changes.append({'object':o.name,'modifier':mod.name,'property':key,'before':old,'after':getattr(mod,key)})
  error=max((o.matrix_world@v.co-mapped(p)).length for v,p in zip(o.data.vertices,original[o.name]));assert error<1e-6,o.name;point_errors.append(error)
 # Boundary shafts and historical authoring guides retain source world geometry.
 for n,m in boundary_world.items():bpy.data.objects[n].matrix_world=m
 for n,m in curve_world.items():bpy.data.objects[n].matrix_world=m
 bpy.context.view_layer.update()
 # Refit markers to the actual evaluated leading upper-bill surface.
 dg=bpy.context.evaluated_depsgraph_get();front=None;front_name=None;headbounds=[]
 for o in meshes:
  ev=o.evaluated_get(dg);m=ev.to_mesh();points=[ev.matrix_world@v.co for v in m.vertices];assert all(math.isfinite(c) for p in points for c in p),o.name
  headbounds.append({'name':o.name,'parent':o.parent.name,'evaluatedBounds':bounds(points)})
  if o.parent.name=='upper-bill':
   for p in points:
    if front is None or p.y<front.y:front=p.copy();front_name=o.name
  ev.to_mesh_clear()
 assert front is not None
 for n in CONTACTS:
  o=bpy.data.objects[n];m=o.matrix_world.copy();m.translation=front;o.matrix_world=m
 bpy.context.view_layer.update()
 for o in nodes:
  s=o.matrix_world.to_scale();assert max(abs(v-1) for v in s)<1e-6,o.name
 for o in bpy.data.objects:
  if o.type=='EMPTY' and o not in nodes:assert node_snapshot(o)==node_before[o.name],o.name
 assert protected=={n:mesh_snapshot(bpy.data.objects[n]) for n in protected}
 curve_error=max(abs(bpy.data.objects[n].matrix_world[r][c]-m[r][c]) for n,m in curve_world.items() for r in range(4) for c in range(4));assert curve_error<1e-6
 socket_witnesses=[]
 for o in nodes:
  socket_witnesses.append({'name':o.name,'parent':o.parent.name,'oldWorld':list(old_nodes[o.name].translation),'newWorld':list(o.matrix_world.translation),'newOwnerLocal':list(o.matrix_local.translation)})
 return {'region':'head-mass','status':'whole-head proportion proposal; not likeness or movement acceptance','changedMeshes':[o.name for o in meshes],'changedNodes':[o.name for o in nodes],'added':[],'removed':[],'boundaryMeshesExact':BOUNDARY,'protectedMeshSnapshotsExact':len(protected),'nodeNamesParentsPreserved':len(node_before),'unchangedNodesExact':len(node_before)-len(nodes),'materialDefinitionsChanged':False,'eraTagsChanged':False,'maximumRawWorldPointErrorM':max(point_errors),'evaluatedHeadBounds':headbounds,'modifierDimensionChanges':modifier_changes,'transforms':transforms,'socketWitnesses':socket_witnesses,'billContactNativeWorld':list(front),'billContactSurface':front_name,'contactMethod':'minimum nativeY evaluated upper-bill vertex including formed wall; both bill-contact/anchor-beak seated','transformContract':{'factor':FACTOR,'pivotNativeWorld':list(pivot),'mapping':'pivot+1.30*(oldWorldPoint-pivot)','headAttachmentUnchanged':True,'nodeTranslationsBaked':True,'nodeBasesUnit':True,'runtimeScaling':False,'boundaryException':BOUNDARY,'historicalGuideWorldMaxDelta':curve_error},'runtimeSocketFollowup':{'makerJawControl':{'owner':'jaw','oldBrowserLocal':[-.18,-.06,.20],'proposedBrowserLocal':[-.234,-.078,.26],'status':'map existing procedural jaw attachment offset; not embedded or fit-proven'},'processingAndOpticAnchors':'Named descendants moved coherently; witness table gives rest positions'},'limits':['Uniform enlargement changes dominant head/body mass only; it does not reconstruct remaining smooth bill/crown/optic shapes.','Cervical attachment shafts retained; adjacent neck/head armor clearance is unproven.','No runtime, model selection, material finishing or publication changes.']}
