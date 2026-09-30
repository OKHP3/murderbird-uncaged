"""Cheek-supported01: actual enclosing skull wall plus common-triangle armor.
Jaw-fit02 source; thirty explicit passive meshes, all true joints unchanged.
"""
import bpy,bmesh,math
from mathutils import Vector
WALLS=[f'V31 fixed temporal receiving wall {s}'for s in(-1,1)]
BROWS=[f'V33 diagonal brow receiver {s} {i}'for s in(-1,1)for i in range(3)]
SHIELDS=[f'V38 optic cheek shield {s} {i}'for s in(-1,1)for i in range(3)]
LEAVES=[f'V33 swept temporal leaf {s} {i}'for s in(-1,1)for i in range(2)]
ROOTS=[f'V31 temporal fitting root {s} {i}'for s in(-1,1)for i in range(3)]
FITTINGS=[f'V31 passive temporal fitting {s} {i}'for s in(-1,1)for i in range(3)]
NAMES=WALLS+BROWS+SHIELDS+LEAVES+ROOTS+FITTINGS

def install(name,world,faces,kind,records):
 o=bpy.data.objects[name];mesh=bpy.data.meshes.new(name+' enclosing common-surface armor');inv=o.matrix_world.inverted();mesh.from_pydata([inv@p for p in world],[],faces);mesh.update()
 for m in o.data.materials:mesh.materials.append(m)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 volume=bm.calc_volume(signed=True);assert volume>0,name;bm.to_mesh(mesh);bm.free();o.data=mesh
 for f in mesh.polygons:f.use_smooth=True
 o['v38CheekSupported']='Passive reconstructed enclosing compound-curved cheek and paired supported fitting; proposal'
 records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in mesh.materials],'kind':kind,'closedEdgeManifold':True,'positiveVolumeM3':volume,'vertices':len(mesh.vertices)})

def apply():
 bpy.context.view_layer.update();records=[];lands=[];fits=[]
 for side in(-1,1):
  wall=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];mesh=wall.data.copy();wall.data=mesh
  # Preserve source mass/bore/connectivity. Smooth the actual source skull field,
  # restrained lateral camber only, tapering to zero at its physical boundary.
  for v in mesh.vertices:
   p=wall.matrix_world@v.co;y,z=p.y,p.z
   dy=max(0,1-((y+.386)/.222)**2);dz=max(0,1-((z-1.738)/.21)**2)
   p.x+=side*.003*dy*dz;v.co=wall.matrix_world.inverted()@p
  for p in mesh.polygons:p.use_smooth=True
  wall['v38CheekSupported']='Source enclosed compound curved wall and actual orbital bore retained; common finite receiving field'
  records.append({'name':wall.name,'owner':wall.parent.name,'eras':wall.get('exteriorEras'),'kind':'Source whole skull enclosure and finite orbital bore; 3mm restrained camber','sourceTopologyRetained':True})
  # Subdivide actual finite outer receiving triangles, then assign directional
  # courses. Their full inner triangles are the actual wall receiving surfaces.
  mesh.calc_loop_triangles();pts=[wall.matrix_world@v.co for v in mesh.vertices];triangles=[]
  for t in mesh.loop_triangles:
   a,b,c=[pts[i]for i in t.vertices];n=(b-a).cross(c-a).normalized()
   if n.x*side>.20:
    triangles.append((a,b,c))
  def split(t):
   a,b,c=t;ab=(a+b)*.5;bc=(b+c)*.5;ca=(c+a)*.5
   return [(a,ab,ca),(ab,b,bc),(ca,bc,c),(ab,bc,ca)]
  triangles=[q for t in triangles for q in split(t)]
  triangles=[q for t in triangles for q in split(t)]
  groups=[[]for i in range(8)]
  def category(p):
   y,z=p.y,p.z;u=(y+.60)/.43
   flow=(1.904-z)/.39+.20*u+.035*math.sin(math.pi*u*2)
   thresholds=[.15,.28,.40,.54,.69,.85,1.02]
   return sum(flow>x for x in thresholds)
  for t in triangles:groups[category(sum(t,Vector())/3)].append(t)
  names=[f'V33 diagonal brow receiver {side} 2',f'V33 diagonal brow receiver {side} 1',f'V33 diagonal brow receiver {side} 0',f'V33 swept temporal leaf {side} 0',f'V38 optic cheek shield {side} 0',f'V38 optic cheek shield {side} 1',f'V38 optic cheek shield {side} 2',f'V33 swept temporal leaf {side} 1']
  patch_outer={}
  for index,(name,ts)in enumerate(zip(names,groups)):
   assert ts,(name,'empty receiving domain');vs=[];lookup={};ff=[]
   def add(p):
    k=tuple(round(x,7)for x in p)
    if k not in lookup:lookup[k]=len(vs);vs.append(p.copy())
    return lookup[k]
   for t in ts:ff.append(tuple(add(p)for p in t))
   h=.0045+(.001*(index%3));count=len(vs);world=vs+[p+Vector((side*h,0,0))for p in vs];faces=[tuple(reversed(t))for t in ff]+[tuple(count+i for i in t)for t in ff]
   from collections import Counter
   ec=Counter(tuple(sorted((f[j],f[(j+1)%3])))for f in ff for j in range(3))
   for f in ff:
    for j in range(3):
     a,b=f[j],f[(j+1)%3]
     if ec[tuple(sorted((a,b)))]==1:faces.append((a,b,b+count,a+count))
   install(name,world,faces,'Broad oblique curved armor from actual receiving triangles, shared inner face patches, no radial ornamental tabs',records)
   patch_outer[name]=[(tuple(world[count+i]for i in t),h)for t in ff]
   lands.append({'part':name,'receiver':wall.name,'receivingTriangleCount':len(ff),'actualInnerTriangleKeys':[tuple(tuple(round(x,7)for x in vs[i])for i in t)for t in ff[:2]],'fullSurfaceMethod':'Actual subdivided receiver triangle field; all full inner faces coincide with actual wall triangles, not merely vertex hits','axialPlateStockM':h,'limits':'Coincident full receiving faces are intentional contacts; adjacency/interobject screen not waived. Normal stock varies with wall slope.'})
  # Each passive cosmetic fitting/root travels geometrically (not by pivot)
  # to a deliberate actual receiving triangle on one of the three cheek plates.
  targets=[(f'V38 optic cheek shield {side} {i}',y,z)for i,(y,z)in enumerate([(-.380,1.742),(-.325,1.690),(-.294,1.629)])]
  for i,(target,yy,zz)in enumerate(targets):
   ts=patch_outer[target];t,h=min(ts,key=lambda q:(sum(q[0],Vector())/3-Vector((side*.15,yy,zz))).length);seat=sum(t,Vector())/3
   n=(t[1]-t[0]).cross(t[2]-t[0]).normalized()
   if n.x*side<0:n=-n
   fitting=bpy.data.objects[f'V31 passive temporal fitting {side} {i}'];old=[fitting.matrix_world@v.co for v in fitting.data.vertices];center=sum(old,Vector())/len(old);lo=min(p.x*side for p in old)
   # Preserve recognizable round passive journal; smaller diameter and depth.
   moved=[]
   for p in old:
    moved.append(Vector((seat.x+side*((p.x*side-lo)*.65+.004),seat.y+(p.y-center.y)*.65,seat.z+(p.z-center.z)*.65)))
   install(fitting.name,moved,[tuple(p.vertices)for p in fitting.data.polygons],'Paired passive round fitting reshaped and explicitly seated on actual cheek triangle',records)
   # Triangular finite return lands share an actual complete receiving face;
   # outer face extends4mm out to the matching fitting inner seat.
   vs=list(t)+[p+Vector((side*.004,0,0))for p in t];faces=[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]
   install(f'V31 temporal fitting root {side} {i}',vs,faces,'Finite complete-triangle fitting return meeting named cheek receiving face and paired fitting',records)
   fits.append({'root':f'V31 temporal fitting root {side} {i}','fitting':fitting.name,'receiver':target,'actualReceiverTriangle':[list(p)for p in t],'fullReturnInnerFaceExact':True,'seatCenterNative':list(seat),'surfaceNormalNative':list(n),'rootAxialDepthM':.004,'fittingActualInnerSeatNativeX':seat.x+side*.004,'limits':'Actual shared face/root attachment proposal; full fitting underside is circular while return is finite triangular land, finite perimeter gap separately measured, not a load/fabrication certificate.'})
 return {'changedMeshes':NAMES,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':records,'actualFootlands':lands,'pairedFittingSeats':fits,'construction':'Source closed compound-curved skull mass and real optic bore retained, broad diagonal curved receiving-face armor encloses temple with small hardware reveals. Paired passive fittings reconstructed on named actual armor triangles.','rigidVsFlexible':'All30 passive existing meshes remain rigid/head-owned/all-era, true optics and all movable joints excluded.','confirmation':'Actual July HEAD ONLY constructed optic/cheek; Master03/Maker-clean wholebird crosschecks','reconstruction':'Exact plate boundaries/counts, stock, passive mount relocation and hidden supports authored proposal, not art metrology.','protected':'Jaw-fit02 hook, mandible/source283socket, truejournal/opticseat/aperture and independent cranial-cover plus wholebody exact.','limits':['Full triangle/self screen follows actual visual gate; receiving face contact does not waive introduced crossings.','Direct source triangle subsets may have multiple connected armor patches around orbital bore; component counts require disposition.','All receiving contacts are deliberate geometric support proposals, not engineering, owner acceptance or continuous motion certificate.']}
