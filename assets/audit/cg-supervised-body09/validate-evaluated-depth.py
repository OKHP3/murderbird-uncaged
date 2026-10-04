"""Read-only depth/UV check over every evaluated new sheet vertex and edge."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
folder=Path(__file__).resolve().parent/'attempt02';native=folder/'murderbird-body09.blend';bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();trees={};meshes={}
for o in s.objects:
 if not o.get('cgSupervisedBody09'):continue
 ev=o.evaluated_get(deps);m=ev.to_mesh();vs=[tuple(o.matrix_world@v.co) for v in m.vertices];fs=[tuple(p.vertices) for p in m.polygons];trees[o.name]=BVHTree.FromPolygons(vs,fs)
 if o.get('cgBody09Rails'):
  assert all(math.isfinite(c) for v in vs for c in v)
  uv=m.uv_layers.get('body05-local-curved-uv');assert uv
  uvv=[[] for v in vs]
  for loop in m.loops:
   q=uv.data[loop.index].uv;assert all(math.isfinite(c) and -.00001<=c<=1.00001 for c in q);uvv[loop.vertex_index].append(q.y)
  meshes[o.name]=(vs,[tuple(e.vertices) for e in m.edges],[sum(q)/len(q) if q else None for q in uvv])
 ev.to_mesh_clear()
records=[]
for name,(vs,edges,params) in meshes.items():
 samples=[(Vector(p),v,'vertex') for p,v in zip(vs,params)]
 samples += [((Vector(vs[a])+Vector(vs[b]))/2,(params[a]+params[b])/2 if params[a] is not None and params[b] is not None else None,'edge') for a,b in edges]
 hits=free=covered=mid=0;worst=None
 for p,v,kind in samples:
  if v is None:continue
  candidates=[]
  for other,tree in trees.items():
   if name==other:continue
   h,n,i,d=tree.ray_cast(Vector((-1,p.y,p.z)),Vector((1,0,0)))
   if h is not None:candidates.append(h.x)
  if not candidates:continue
  hits+=1;clearance=min(candidates)-p.x
  if v>=.75:
   worst=clearance if worst is None else min(worst,clearance)
   if clearance<-.0008:free+=1
  elif clearance<-.0008:
   if v<=.45:covered+=1
   else:mid+=1
 records.append(dict(object=name,evaluatedVertices=len(vs),evaluatedEdges=len(edges),allVerticesAndEdgeMidpointsSampled=len(samples),adjacentSheetAndSupportHits=hits,coveredRootBurialSamples=covered,nonRootBurialSamples=mid,freeEndBurialSamples=free,worstFreeEndClearance=worst,evaluatedGeometryFinite=True,evaluatedUVFiniteNormalized=True))
r=dict(status='FAIL overlap; read-only diagnostic, no new design attempt',nativeSHA256=hashlib.sha256(native.read_bytes()).hexdigest(),method='Every evaluated SOLIDIFY/BEVEL vertex and every evaluated edge midpoint cast in outward -X against all other evaluated cassette sheets and root supports; v from evaluated local UVs distinguishes covered roots <=.45 and free ends >=.75. Includes back stock as well as front surface, not projected visible area; retained source meshes excluded.',sheets=records)
(folder/'evaluated-depth-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('EVALUATED_DEPTH',json.dumps(records))
