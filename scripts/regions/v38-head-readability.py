"""Head-readability02: twelve existing fixed brow/cheek plates, actual seated03.
No bill/optic/jaw/cover/body edits; six bridge endlands and optic root bands exact.
"""
import bpy,bmesh,math
from mathutils import Vector
BROWS=[f'V33 diagonal brow receiver {s} {i}'for s in(-1,1)for i in range(3)]
SHIELDS=[f'V38 optic cheek shield {s} {i}'for s in(-1,1)for i in range(3)]
NAMES=BROWS+SHIELDS

def ease(u):u=max(0,min(1,u));return u*u*(3-2*u)
def apply():
 bpy.context.view_layer.update();records=[]
 for name in NAMES:
  o=bpy.data.objects[name];assert o.parent.name=='head';world=o.matrix_world.copy();inv=world.inverted();old=[v.co.copy()for v in o.data.vertices];pts=[world@p for p in old];half=len(pts)//2;side=int(name.split()[-2]);course=int(name.split()[-1]);fixed=set();moves={}
  if name in BROWS:
   assert half==363
   for i,p in enumerate(pts[:half]):
    row,col=divmod(i,11);u=row/32;v=col/10
    # Actual optical inner receiving band exact; preserve named upper shield
    # endland's complete receiving vicinity on brow0, not metadata alone.
    foot=course==0 and abs(p.y+.491)<.014 and abs(p.z-1.815)<.014
    protected=col<=2 or foot
    if protected:fixed.update([i,i+half]);d=Vector()
    else:
     w=ease((v-.2)/.8);flow=math.sin(math.pi*u)
     dy=[.024,.032,.055][course]*w*flow
     dz=[-.004,-.008,.012][course]*w*flow
     # Varied oblique boundaries sweep into the posterior temple instead
     # of retaining a broad parallel top sheet. Inner bore never changes.
     dz+=.004*w*(u-.5)
     d=Vector((0,dy,dz))
    moves[i]=moves[i+half]=d
  else:
   assert half==91
   for i,p in enumerate(pts[:half]):
    row,col=divmod(i,7);t=(row-2)/8;v=col/6
    if row<=2 or row>=10:fixed.update([i,i+half]);d=Vector()
    else:
     w=math.sin(math.pi*t)**2
     # Free bridge sweeps rearward with compact tapered margins;
     # supported10mm endland rows and their4.5mm stock remain exact.
     width=[.025,.018,.012][course];dz=w*((v-.5)*width+[-.004,-.004,-.002][course]);dy=w*[.020,.012,.007][course]*(.70+.30*(v-.5))
     d=Vector((side*.002*w,dy,dz))
    moves[i]=moves[i+half]=d
  o.data=o.data.copy()
  for i,p in enumerate(pts):o.data.vertices[i].co=old[i]if i in fixed or moves[i].length==0 else inv@(p+moves[i])
  o.data.update();assert all(o.data.vertices[i].co==old[i]for i in fixed);after=[world@v.co for v in o.data.vertices];stockError=max((((after[i]-after[i+half])-(pts[i]-pts[i+half])).length for i in range(half)));assert stockError<3e-7
  bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);volume=abs(bm.calc_volume(signed=True));bm.free();assert closed and volume>0,name
  o['v38HeadReadability']='Final02 rearward swept compact brow/cheek course proposal; optical receiving bands/endlands exact'
  records.append({'name':name,'owner':'head','eras':o.get('exteriorEras'),'surfaceRole':o.get('surfaceRole'),'constructionClass':o.get('constructionClass'),'materials':[m.name if m else None for m in o.data.materials],'sourceTopologyExact':True,'protectedVertexIndices':sorted(fixed),'maximumMovementM':max(d.length for d in moves.values()),'allPairedStockVectorErrorM':stockError,'closedEdgeManifold':closed,'positiveVolumeM3':volume,'attachment':'Brow innercolumns0–2 and actual brow0 receiving footprint around shield0 end exact; shieldrows0–2/10–12 bothhalves exact to seated03 finite wall/brow endlands. No floating proxy or wall move.','limits':'Freeface displacement may introduce adjacency contacts; exactroots/stock vectors do not certify fullface fit.'})
 return {'changedMeshes':NAMES,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'rigidVsFlexible':'Twelve passive rigid head-owned plates; no flexiblebody/newhardware or bridge to moving cranialcover.','confirmed':'July head-only layered swept brow/cheek around recessed optic; Master03/Maker-clean crosscheck wholebird, not Julybody.','reconstruction':'Exact outerplate outlines/flow dimensions and unseen side authored, not image metrology/engineering acceptance.','protected':'Actual optical cups/lips/floors/Builderapertures/seats, bill triangles/extrema,jaw bowl397/socket/hinge, crown/cover roots, neck/body/materials/allpivots unchanged. Source breastcourse02 gain+nineunresolvedlapcontacts retained.','limits':['Finite endland/root preservation is actual surface correspondence, not wholeplate fastening/load approval.','Strict changedregion fullpool contact check after visualcandidate; no depth/continuous sweep/manufacturing/ownerclaim.']}
