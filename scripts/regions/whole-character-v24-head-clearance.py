"""V24 narrow jaw-terminal fit after the frozen main head construction.

Retains upper hook/frontier and all rigid rest interfaces. Proposed cutting-edge
fit only; discrete pose checks do not imply whole motion/engineering approval.
"""
import bpy,math,json
from mathutils import Vector
TARGETS=['Forked forged mandible -1','Forked forged mandible 1','Distal mandible bridge']
def smooth(t):
 t=max(0.,min(1.,t));return t*t*(3-2*t)
def props(o):return json.dumps(dict(o.items()),default=lambda x:list(x),sort_keys=True)
def snapshot(o):
 return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),props(o))
def apply():
 bpy.context.view_layer.update()
 nodes={o.name:(tuple(tuple(r) for r in o.matrix_world),o.parent.name if o.parent else None,props(o)) for o in bpy.data.objects if o.type=='EMPTY'}
 protected={o.name:snapshot(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in TARGETS}
 bounds=[]
 for name in TARGETS:
  o=bpy.data.objects[name];assert o.parent.name=='jaw';before=[o.matrix_world@v.co for v in o.data.vertices];inv=o.matrix_world.inverted();o.data=o.data.copy();o.data.name=name+' V24 terminal seating'
  for v,p in zip(o.data.vertices,before):
   weight=smooth((-p.y-.565)/.055)
   q=p+Vector((0,.018*weight,-.002*weight));v.co=inv@q
  o.data.update();o['v24TerminalFit']='18mm aft/2mm down maximum smooth terminal retract; original journal/root retained'
  after=[o.matrix_world@v.co for v in o.data.vertices]
  bounds.append({'name':name,'beforeMinY':min(p.y for p in before),'afterMinY':min(p.y for p in after),'maximumDisplacementM':max((a-b).length for a,b in zip(after,before))})
 bpy.context.view_layer.update()
 assert nodes=={o.name:(tuple(tuple(r) for r in o.matrix_world),o.parent.name if o.parent else None,props(o)) for o in bpy.data.objects if o.type=='EMPTY'}
 assert protected=={o.name:snapshot(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in TARGETS},'Nonterminal head/other geometry changed'
 return {'region':'head-jaw-terminal-clearance','status':'bounded proposed cutting-edge rest fit; awaiting discrete native checks','changed':TARGETS,'added':[],'removed':[],'primaryPivotChanges':[],'preservedOriginalNodes':len(nodes),'protectedMeshSnapshotsExact':len(protected),'bounds':bounds,'parameters':{'fadeStartNativeY':-.565,'fadeEndNativeY':-.620,'maximumAftM':.018,'maximumDownM':.002},'construction':'Retract only formed jaw terminal cells behind thick hook posterior cutting surface; roots/journals and hooked bill/frontier stay exact. Smooth monotonic remap retains finite paired skins; no holes, trimming or concealment.','limits':['Rest and five jaw opening samples are discrete bounds, not continuous/full-head clearance.']}
