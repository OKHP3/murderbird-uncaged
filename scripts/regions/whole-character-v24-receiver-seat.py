"""V24 technical correction of two newly parented orbital receivers only.

The frozen main constructor read a newly parented object's stale matrix_world
before dependency-graph synchronization. Its native-world polygon points were
therefore stored as local coordinates and transformed by head a second time.
Future constructors must update the view layer after parenting, BEFORE taking
matrix_world.inverted() to install native-world vertices. This helper explicitly
seats the two finite authored polygons in the synchronized head frame.
"""
import bpy,json
from mathutils import Vector
TARGETS=['V24 anterior orbital root receiver -1','V24 anterior orbital root receiver 1']
OUTLINE=[(-.549,1.806),(-.571,1.818),(-.589,1.790),(-.594,1.733),(-.582,1.704),(-.564,1.714),(-.563,1.763)]
def props(o):return json.dumps(dict(o.items()),default=lambda x:list(x),sort_keys=True)
def snapshot(o):
 return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(f.vertices) for f in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),props(o),o.hide_render,o.hide_viewport)
def bounds(points):return [[min(p[k] for p in points) for k in range(3)],[max(p[k] for p in points) for k in range(3)]]
def apply():
 bpy.context.view_layer.update()
 nodes={o.name:(o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),props(o)) for o in bpy.data.objects if o.type=='EMPTY'}
 protected={o.name:snapshot(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in TARGETS}
 results=[]
 for name in TARGETS:
  o=bpy.data.objects[name];assert o.parent.name=='head'
  side=-1 if name.endswith('-1') else 1
  authored=[Vector((side*x,y,z)) for x in (.125,.120) for y,z in OUTLINE]
  assert len(o.data.vertices)==len(authored)
  before=[o.matrix_world@v.co for v in o.data.vertices]
  world_error=max((p-q).length for p,q in zip(before,authored))
  # A corrected input is harmless; a different construction is not silently remapped.
  if world_error>1e-6:
   assert max((v.co-p).length for v,p in zip(o.data.vertices,authored))<1e-6,'Unexpected receiver input; only the frozen stale-matrix failure is supported'
   o.data=o.data.copy();o.data.name=name+' synchronized V24 seat'
   inv=o.matrix_world.inverted()
   for v,p in zip(o.data.vertices,authored):v.co=inv@p
   o.data.update()
  after=[o.matrix_world@v.co for v in o.data.vertices]
  error=max((p-q).length for p,q in zip(after,authored));assert error<1e-6
  results.append({'name':name,'parent':o.parent.name,'beforeRawWorldBounds':bounds(before),'authoredBounds':bounds(authored),'afterRawWorldBounds':bounds(after),'beforeAuthoredPointErrorM':world_error,'afterAuthoredPointErrorM':error})
 bpy.context.view_layer.update()
 assert nodes=={o.name:(o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),props(o)) for o in bpy.data.objects if o.type=='EMPTY'}
 assert protected=={o.name:snapshot(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in TARGETS}
 return {'region':'head-receiver-technical-seat','changed':TARGETS,'added':[],'removed':[],'primaryPivotChanges':[],'preservedOriginalNodes':len(nodes),'protectedMeshSnapshotsExact':len(protected),'materialDefinitionsChanged':False,'receivers':results,'rootCause':'new_form parent assigned then install read stale matrix_world before view_layer.update; authored absolute vertices received head transform twice','futureAuthoringRule':'synchronize after parenting before world-to-local installation; explicitly verify world vertices against authored points'}
