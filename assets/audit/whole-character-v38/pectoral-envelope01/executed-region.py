"""Breast-study01: upper lateralpectoraltransition on original inspection owner.
Actual raster references guide form, not dimensions; fixed frame remains exact.
"""
import bpy,bmesh,math
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
PLATES=[f'V34 formed breast course {r} plate {c}' for r,n in [(1,5),(2,6),(3,7),(4,6),(5,5),(6,4)] for c in range(1,n+1)]
NAMES=PLATES+['V30 continuous tapered breast liner']+[f'V30 breast liner receiving tab {s}' for s in (-1,1)]
# World-Z controls: lower hinge and neck boundaries held; upper breast wider
# and forward-full, lower front retreats toward the retained pelvic structure.
CAGE=[(.98,0,0),(1.05,.025,.022),(1.13,.038,.020),(1.18,.030,.010),(1.225,0,0)]
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def delta(p):
 if p.z<=CAGE[0][0]or p.z>=CAGE[-1][0]:return Vector()
 a,b=next((a,b)for a,b in zip(CAGE,CAGE[1:])if a[0]<=p.z<=b[0]);w=ease((p.z-a[0])/(b[0]-a[0]));lateral=a[1]+w*(b[1]-a[1]);flatten=a[2]+w*(b[2]-a[2]);front=ease((-p.y-.13)/.15);side=ease((abs(p.x)-.08)/.18)
 return Vector(((1 if p.x>=0 else -1)*lateral*side*front,flatten*front*(1-.35*side),0))

def pairs(points,normals):
 # Preserve actual existing finite-stock vectors, including inherited thickened
 # lower plates. Boolean-trimmed top meshes cannot assume index-half pairing.
 n=len(points);half=n//2
 if n%2==0 and max((points[i]-points[i+half]).length for i in range(half))<.006:
  return [(i,i+half) for i in range(half)]
 tree=KDTree(n)
 for i,p in enumerate(points):tree.insert(p,i)
 tree.balance();candidates=[]
 for i,p in enumerate(points):
  for q,j,d in tree.find_range(p,.006):
   if j>i and d>.0015 and normals[i].dot(normals[j])<-.25:candidates.append((d,i,j))
 used=set();result=[]
 for _,i,j in sorted(candidates):
  if i not in used and j not in used:used.update((i,j));result.append((i,j))
 return result
def apply():
 bpy.context.view_layer.update();records=[];changed=[]
 for name in NAMES:
  o=bpy.data.objects[name];assert o.parent.name=='breastplate';originalLocal=[v.co.copy() for v in o.data.vertices];world=o.matrix_world.copy();inv=world.inverted();points=[world@v.co for v in o.data.vertices];normal=world.to_3x3().inverted().transposed();normals=[(normal@v.normal).normalized() for v in o.data.vertices]
  bm=bmesh.new();bm.from_mesh(o.data);sourceClosed=all(e.is_manifold for e in bm.edges);sourceVolume=abs(bm.calc_volume(signed=True));bm.free();o.data=o.data.copy();moves={i:delta(p) for i,p in enumerate(points)};paired=[];fixed=[]
  if 'receiving tab' in name:
   assert len(points)==24;fixed=list(range(8));end=sum(points[16:24],Vector())/8;liner=bpy.data.objects['V30 continuous tapered breast liner'];dg=bpy.context.evaluated_depsgraph_get();ev=liner.evaluated_get(dg);data=ev.to_mesh();tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in data.vertices],[tuple(f.vertices) for f in data.polygons]);ev.to_mesh_clear();actualSeat=tree.find_nearest(end+delta(end))[0];change=actualSeat-end
   for i in range(24):moves[i]=change*(0 if i<8 else .5 if i<16 else 1)
  else:
   paired=pairs(points,normals)
   for i,j in paired:
    common=delta((points[i]+points[j])*.5);moves[i]=moves[j]=common
  for i,p in enumerate(points):o.data.vertices[i].co=inv@(p+moves[i]) if moves[i].length else originalLocal[i]
  # Exact retained return seat vertices avoid a numerical roundtrip drift.
  for i in fixed:o.data.vertices[i].co=originalLocal[i]
  assert all(o.data.vertices[i].co==originalLocal[i] for i in fixed)
  o.data.update();bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);volume=abs(bm.calc_volume(signed=True));bm.free();assert closed==sourceClosed and volume>0,name
  after=[world@v.co for v in o.data.vertices];error=max(((after[i]-after[j])-(points[i]-points[j])).length for i,j in paired) if paired else 0;assert error<3e-7,name
  if max(v.length for v in moves.values())>1e-10:
   changed.append(name);o['v38PectoralEnvelope']='Pectoral01 lateraluppertransition and modestfrontflattening; preserveddeep lower taper; sameinspectioncover; reconstructedfit/likeness proposal'
  records.append({'name':name,'owner':'breastplate','surfaceRole':o.get('surfaceRole'),'constructionClass':o.get('constructionClass'),'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in o.data.materials],'vertexScope':'All existing vertices except retained return-side first8 vertices of each receiving tab. Topology and finite stock retained.','vertices':len(points),'fixedTabVertexIndices':fixed,'maximumMovementM':max(v.length for v in moves.values()),'preservedStockPairs':paired,'maximumStockVectorErrorM':error,'unpairedVertices':len(points)-2*len(paired) if paired else len(points),'sourceClosedEdgeManifold':sourceClosed,'candidateClosedEdgeManifold':closed,'sourcePositiveVolumeM3':sourceVolume,'candidatePositiveVolumeM3':volume,'nominalSourceWallM':o.get('wallM'),'tabSourceReturnSeat':list(sum(points[:8],Vector())/8) if fixed else None,'tabCandidateReturnSeat':list(sum(after[:8],Vector())/8) if fixed else None,'tabSourceLinerSeat':list(sum(points[16:24],Vector())/8) if fixed else None,'tabCandidateLinerSeat':list(sum(after[16:24],Vector())/8) if fixed else None,'tabEndSeating':'Actual new liner nearest triangle surface at section center; same-owner finite joined tab, not engineering weld/fit certificate.' if fixed else None})
 return {'changedMeshes':changed,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'authoredControlCage':CAGE,'retainedRegionMeshes':[n for n in NAMES if n not in changed],'allExcludedPivotsMaterialsEraIdentityExact':True,'rigidVsFlexible':'Finite rigid formed cover plates/continuous liner and receiving tabs; all on breastplate, no flexible tissue or cross-owner bridge.','confirmed':'Actual master03/Maker-clean/Mechanic show upper breast volume continuing into compact shoulder with lower taper; July head-only.','reconstruction':'Dimensions, unseen liner stock and support seating are authored proposal, not art metrology or load validation.','supportCoherence':'Continuous liner under all33 cover plates; two liner tabs retain their actual return-side seats and update only liner-side sections. Original thoracic ribs/frame, moving returns, shaft/bearings and inspection hinge exact.','clearanceScope':'Actual source hinge, frame, neck and mantle kept; targeted baseline/candidate opening surfaces still required.','limits':['Matched finite stock vectors preserved where recoverable, Boolean-trimmed unmatched vertices use smooth finite-surface morph; no all-wall metrology claim.','No forward swelling/shelf; upper lateral/posterior redistribution and frontflattening only. Lower taper andneckboundary exact. No new hardware/texturelayer.','Same ownership/pivots do not prove continuous opening or motion clearance.']}
