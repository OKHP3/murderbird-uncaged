"""Four local body-fixed receiver returns, breast-study02 entirely exact."""
import bpy,bmesh,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
NAMES=[f'V24 rising thoracic receiving cheek {s}' for s in (-1,1)]+[f'V35 oblique thoracic side guard {s} 0' for s in (-1,1)]
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def tree(o):
 o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices) for t in o.data.loop_triangles],all_triangles=True)
def apply():
 bpy.context.view_layer.update();records=[]
 for name in NAMES:
  o=bpy.data.objects[name];assert o.parent.name=='body';side=-1 if ' -1' in name else 1;cheek=name.startswith('V24');original=[v.co.copy() for v in o.data.vertices];world=o.matrix_world.copy();inv=world.inverted();pts=[world@p for p in original]
  supportNames=[f'V24 shoulder lower load fork {side}',f'V23 root load fork {side}',f'V35 lateral thoracic bay load rail {side}',f'V35 posterior bay load rail {side}'];supportTrees={n:tree(bpy.data.objects[n]) for n in supportNames}
  seats={n:[i for i,p in enumerate(pts) if supportTrees[n].find_nearest(p)[3]<.002] for n in supportNames};railTree=supportTrees[f'V35 lateral thoracic bay load rail {side}'];railProtected={i for i,p in enumerate(pts) if cheek and railTree.find_nearest(p)[3]<.008};protected={i for i,p in enumerate(pts) if p.y>=-.18}|{i for v in seats.values() for i in v}|railProtected;moves={}
  for i,p in enumerate(pts):
   w=ease((-.235-p.y)/.035)*ease((1.125-p.z)/.025) if cheek else ease((1.035-p.z)/.030)*ease((-.190-p.y)/.040)
   moves[i]=Vector((-side*.009*w,.017*w,0)) if i not in protected else Vector()
  # Recover finite skin vectors locally through opposite normals; index-half
  # pairing is invalid on these historically trimmed finite meshes.
  normals=[(world.to_3x3().inverted().transposed()@v.normal).normalized() for v in o.data.vertices];kd=KDTree(len(pts))
  for i,p in enumerate(pts):kd.insert(p,i)
  kd.balance();candidates=[]
  for i,p in enumerate(pts):
   for q,j,d in kd.find_range(p,.008):
    if j>i and d>.0015 and normals[i].dot(normals[j])<-.25:candidates.append((d,i,j))
  used=set();pairs=[]
  for _,i,j in sorted(candidates):
   if i in used or j in used:continue
   used.update((i,j));pairs.append((i,j));common=Vector() if i in protected or j in protected else (moves[i]+moves[j])*.5;moves[i]=moves[j]=common
  o.data=o.data.copy()
  for i,p in enumerate(pts):
   if moves[i].length:o.data.vertices[i].co=inv@(p+moves[i])
  o.data.update();assert all(o.data.vertices[i].co==original[i] for i in protected)
  after=[world@v.co for v in o.data.vertices];error=max(((after[i]-after[j])-(pts[i]-pts[j])).length for i,j in pairs) if pairs else 0;assert error<3e-7
  bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);volume=abs(bm.calc_volume(signed=True));bm.free();assert closed and volume>0,name
  o['v38BreastClearance']='breast-clearance02 local inward/posterior formed receiving return; breast36 exact; fit proposal'
  records.append({'name':name,'owner':'body','surfaceRole':o.get('surfaceRole'),'constructionClass':o.get('constructionClass'),'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in o.data.materials],'vertexScope':'Only exact listed displaced indices; all remaining vertices/edges/faces exact.','changedVertexIndices':[i for i,p in enumerate(original) if o.data.vertices[i].co!=p],'unchangedPosteriorAndSupportVertexIndices':sorted(protected),'protectedActualLateralRailVicinityIndices':sorted(railProtected),'sourceCheekReceivingCorridor':'Zero atsourceY>=-.235,35mm ramp tofull<=-.270; source lateralrail surface distance<8mm exact. Sideguard01 unchanged.','supportSeatIndices':seats,'supportSeatsBeforeAfter':{n:[{'index':i,'sourceNearestM':supportTrees[n].find_nearest(pts[i])[3],'candidateNearestM':supportTrees[n].find_nearest(after[i])[3]} for i in indices] for n,indices in seats.items()},'maximumMovementM':max(m.length for m in moves.values()),'recoveredFiniteStockPairs':pairs,'maximumRetainedStockVectorErrorM':error,'unpairedVertices':len(pts)-len(used),'closedEdgeManifold':closed,'positiveVolumeM3':volume})
 return {'changedMeshes':NAMES,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'confirmed':'Exact four introduced breast02 rest witness footprints in source inventory; breast36 contour, pivots and all unrelated geometry retained.','reconstruction':'Finite local receiving return is authored repair, not reference metrology/fabrication acceptance.','rigidVsFlexible':'Four finite body-fixed plates, rigid at runtime; no flexible skin, moving-owner bridge or stock subtraction.','limits':['Named support nearest-source vertex seats within2mm retained exactly; nearest vertices are not complete joining/load proof.','Recoverable finite stock vectors retained; unmatched Boolean vertices follow smooth local return, no all-wall metrology claim.','Same-body contacts require separate disclosure; same hierarchy alone is not a fit PASS.']}
