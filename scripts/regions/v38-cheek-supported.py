"""Cheek-supported02: actual enclosing skull wall plus common-triangle armor.
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
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));print('TOPOLOGY',name,[(len(e.link_faces),list(e.verts[0].co),list(e.verts[1].co))for e in bm.edges if not e.is_manifold][:12],flush=True);assert all(e.is_manifold for e in bm.edges),name
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 volume=bm.calc_volume(signed=True);assert volume>0,name;bm.to_mesh(mesh);bm.free();o.data=mesh
 for f in mesh.polygons:f.use_smooth=True
 o['v38CheekSupported']='Passive reconstructed enclosing compound-curved cheek and paired supported fitting; proposal'
 records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in mesh.materials],'kind':kind,'closedEdgeManifold':True,'positiveVolumeM3':volume,'vertices':len(mesh.vertices)})

def sample(rows,t):
 q=max(0,min(1,t))*(len(rows)-1);i=min(int(q),len(rows)-2);u=q-i;a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
 return [.5*(2*b[k]+(-a[k]+c[k])*u+(2*a[k]-5*b[k]+4*c[k]-d[k])*u*u+(-a[k]+3*b[k]-3*c[k]+d[k])*u*u*u)for k in range(len(b))]

def apply():
 from mathutils.bvhtree import BVHTree
 bpy.context.view_layer.update();records=[];lands=[];fits=[]
 for side in(-1,1):
  wall=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];mesh=wall.data.copy();wall.data=mesh
  for v in mesh.vertices:
   p=wall.matrix_world@v.co;y,z=p.y,p.z;p.x+=side*.003*max(0,1-((y+.386)/.222)**2)*max(0,1-((z-1.738)/.21)**2);v.co=wall.matrix_world.inverted()@p
  for f in mesh.polygons:f.use_smooth=True
  wall['v38CheekSupported']='Actual whole-skull wall/bore retained, restrained compound camber; passive receiving support'
  records.append({'name':wall.name,'owner':'head','kind':'Retained closed skull/aperture topology, restrained3mm compound camber'})
  def bvh(o):
   o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True)
  tree=bvh(wall);cap=bvh(bpy.data.objects['V31 frontal cranial cap receiving seat']);projection=[];panel_trees={}
  def actualx(y,z):
   start=Vector((side*.40,y,z));direction=Vector((-side,0,0));hit=tree.ray_cast(start,direction,.38)
   if hit[0]is not None:return abs(hit[0].x),wall.name,'actual receiver ray'
   hit=cap.ray_cast(start,direction,.38)
   if hit[0]is not None:return abs(hit[0].x),'V31 frontal cranial cap receiving seat','actual declared frontal seat ray'
   # Free edges can cantilever over orbital bore. Nearest receiver only sets
   # their lateral continuity; it is explicitly NOT an attachment footprint.
   near=tree.find_nearest(Vector((side*.15,y,z)));return abs(near[0].x),wall.name,'unsupported free-span lateral guide; not a seat'
  def plate(name,curve,width,start=0,end=1,stock=.0045):
   nu,nv=40,10;pts=[];support=[]
   for rr in range(nu+1):
    t=start+(end-start)*rr/nu;y,z=sample(curve,t);a=sample(curve,max(0,t-.001));b=sample(curve,min(1,t+.001));dy,dz=b[0]-a[0],b[1]-a[1];l=math.hypot(dy,dz)
    taper=.70+.30*math.sin(math.pi*rr/nu)**.7
    for cc in range(nv+1):
     v=cc/nv;yy=y-dz/l*(v-.5)*width*taper;zz=z+dy/l*(v-.5)*width*taper;x,target,method=actualx(yy,zz)
     relief=.0015*math.sin(math.pi*v)**2*math.sin(math.pi*rr/nu);pts.append(Vector((side*(x+stock+.001+relief),yy,zz)));support.append((target,method))
   count=len(pts);verts=pts+[p-Vector((side*stock,0,0))for p in pts];faces=[];stride=nv+1
   for i in range(nu):
    for j in range(nv):
     a=i*stride+j;b=a+stride;faces.extend([(a,a+1,b+1,b),(count+b,count+b+1,count+a+1,count+a)])
   boundary=list(range(stride))+[i*stride+nv for i in range(1,nu+1)]+[nu*stride+j for j in range(nv-1,-1,-1)]+[i*stride for i in range(nu-1,0,-1)]
   for i,a in enumerate(boundary):b=boundary[(i+1)%len(boundary)];faces.append((a,b,count+b,count+a))
   install(name,verts,faces,'Smooth purpose-shaped curved tapered plate outline over declared enclosing backing; narrow finite stand-off',records)
   panel_trees[name]=bvh(bpy.data.objects[name]);projection.append({'part':name,'actualReceiverRayVertices':sum(m[1]!='unsupported free-span lateral guide; not a seat'for m in support),'freeSpanVertices':sum(m[1]=='unsupported free-span lateral guide; not a seat'for m in support),'totalOuterVertices':len(pts),'nominalAxialStockM':stock,'innerAxialGapM':.001,'limits':'Projected vertices and true supporting field; intervening triangles require strict surface screen. No conforming-foot or attachment acceptance from ray hits.'})
  rail=[(-.618,1.810),(-.565,1.845),(-.481,1.839),(-.389,1.787)]
  for i,(a,b)in enumerate([(0,.36),(.34,.70),(.68,1)]):plate(f'V33 diagonal brow receiver {side} {2-i}',rail,.042,a,b)
  # Broad lower orbital crescent and two shorter staggered rear guards.
  plate(f'V38 optic cheek shield {side} 0',[(-.464,1.773),(-.437,1.722),(-.483,1.667),(-.537,1.651)],.035)
  plate(f'V38 optic cheek shield {side} 1',[(-.407,1.771),(-.357,1.735),(-.326,1.691)],.068)
  plate(f'V38 optic cheek shield {side} 2',[(-.366,1.698),(-.316,1.656),(-.278,1.605)],.066)
  plate(f'V33 swept temporal leaf {side} 0',[(-.443,1.830),(-.375,1.811),(-.305,1.779)],.054)
  plate(f'V33 swept temporal leaf {side} 1',[(-.315,1.682),(-.273,1.645),(-.239,1.594)],.052)
  # Full circular footprint returns, not a single tiny selected triangle.
  for i,(target,yy,zz)in enumerate([(f'V38 optic cheek shield {side} 1',-.358,1.735),(f'V38 optic cheek shield {side} 2',-.316,1.656),(f'V33 swept temporal leaf {side} 1',-.274,1.645)]):
   pt=panel_trees[target];radius=.0065;count=32;inner=[];hits=[]
   for j in range(count):
    th=2*math.pi*j/count;y=yy+radius*math.cos(th);z=zz+radius*math.sin(th);hit=pt.ray_cast(Vector((side*.40,y,z)),Vector((-side,0,0)),.38)
    assert hit[0]is not None,(target,'actual full fitting footprint missing',j);inner.append(hit[0]);hits.append(list(hit[1]))
   outer_x=max(abs(p.x)for p in inner)+.004;outer=[Vector((side*outer_x,p.y,p.z))for p in inner];faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(j,(j+1)%count,(j+1)%count+count,j+count)for j in range(count)]
   install(f'V31 temporal fitting root {side} {i}',inner+outer,faces,'Finite13mm diameter full circular return footprint on named guard, planar outer foot for paired round fitting',records)
   fitting=bpy.data.objects[f'V31 passive temporal fitting {side} {i}'];old=[fitting.matrix_world@v.co for v in fitting.data.vertices];center=sum(old,Vector())/len(old);lo=min(p.x*side for p in old);moved=[Vector((side*(outer_x+(p.x*side-lo)*.65),yy+(p.y-center.y)*.65,zz+(p.z-center.z)*.65))for p in old]
   install(fitting.name,moved,[tuple(f.vertices)for f in fitting.data.polygons],'Smaller paired passive round fitting, actual base plane shares return outer plane',records)
   fits.append({'root':f'V31 temporal fitting root {side} {i}','fitting':fitting.name,'receiver':target,'actualFootPerimeterNative':[list(p)for p in inner],'actualNormals':hits,'footprintDiameterM':radius*2,'actualFittingInnerSeatNativeX':side*outer_x,'limits':'Full circular perimeter ray hits actual finite plate; polygonal inner return cap may cross/interpolate receiver between samples. Actual full triangle screen and finite fitting underside gap measurement take precedence.'})
 return {'changedMeshes':NAMES,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':records,'actualFootlands':projection,'pairedFittingSeats':fits,'construction':'Retained source compound-curved enclosing skull with smooth swept brow crescent/lower orbital rim, two fuller staggered rear cheek plates and short temporal returns; restrained axial relief, narrow hardware reveals.','rigidVsFlexible':'All30 passive existing meshes remain rigid/head-owned/all-era, true optics and movable joints excluded.','confirmation':'Actual July HEAD ONLY; Master03/Maker-clean wholebird crosschecks','reconstruction':'Exact new guard boundaries, stock and passive mount relocation authored proposal, not art metrology.','protected':'Jaw-fit02 hook, mandible/source283socket, truejournal/opticseat/aperture and independent cranial-cover plus wholebody exact.','limits':['No silhouette/adoption or seat acceptance before visual and strict triangle gate.','Free spans over orbital bore guided only laterally from named receiving wall, explicitly not seat footprints.','Inner receiver point rays cannot certify intervening faces or continuous clearance.']}
