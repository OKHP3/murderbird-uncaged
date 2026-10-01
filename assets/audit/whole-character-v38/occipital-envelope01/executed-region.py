"""Occipital-envelope01, pinned orbital-clearance02.18 existing passive meshes.
Rear support volume and swept plates together; no additions/reparents/hardware moves.
"""
import bpy,bmesh,math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from collections import Counter
def install(name,verts,faces,kind,records,smooth_cap_count=0):
 o=bpy.data.objects[name];m=bpy.data.meshes.new(name+' direct clean finite shell');inv=o.matrix_world.inverted();m.from_pydata([inv@p for p in verts],[],faces);m.update()
 for mat in o.data.materials:m.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(m);bm.free();o.data=m
 for i,f in enumerate(m.polygons):f.use_smooth=i<smooth_cap_count
 o['v38OccipitalEnvelope']='Direct compound-curved finite passive head assembly proposal'
 records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'role':kind,'closedEdges':True,'positiveVolumeM3':volume,'materials':[q.name if q else None for q in m.materials]})

def grid(name,fn,nu,nv,stock,kind,records,normal_axis=None):
 p=[fn(i/nu,j/nv)for i in range(nu+1)for j in range(nv+1)];normals=[]
 for i in range(nu+1):
  for j in range(nv+1):
   if normal_axis is not None:n=normal_axis(i/nu,j/nv) if callable(normal_axis) else normal_axis
   else:
    du=fn(min(1,i/nu+.0001),j/nv)-fn(max(0,i/nu-.0001),j/nv);dv=fn(i/nu,min(1,j/nv+.0001))-fn(i/nu,max(0,j/nv-.0001));n=du.cross(dv).normalized()
    if n.z<0:n=-n
   normals.append(n)
 n=len(p);verts=p+[q-stock*k for q,k in zip(p,normals)];faces=[];stride=nv+1
 for i in range(nu):
  for j in range(nv):
   k=i*stride+j;faces.extend([(k,k+stride,k+stride+1,k+1),(n+k+1,n+k+stride+1,n+k+stride,n+k)])
 border=list(range(stride))+[i*stride+nv for i in range(1,nu+1)]+[nu*stride+j for j in range(nv-1,-1,-1)]+[i*stride for i in range(nu-1,0,-1)]
 for i,a in enumerate(border):b=border[(i+1)%len(border)];faces.append((a,b,n+b,n+a))
 install(name,verts,faces,kind,records,2*nu*nv);return p,normals

def rounded(poly):
 for it in range(1):
  poly=[q for a,b in zip(poly,poly[1:]+poly[:1])for q in ([.88*a[k]+.12*b[k]for k in range(2)],[.12*a[k]+.88*b[k]for k in range(2)])]
 return poly

class D:
 def __init__(self,x,y):self.x=float(x);self.y=float(y)
 def __add__(self,q):return D(self.x+q.x,self.y+q.y)
 def __sub__(self,q):return D(self.x-q.x,self.y-q.y)
 def __mul__(self,v):return D(self.x*v,self.y*v)
 @property
 def length_squared(self):return self.x*self.x+self.y*self.y
def cross(a,b):return a.x*b.y-a.y*b.x
def clip(poly,tri):
 orient=cross(tri[1]-tri[0],tri[2]-tri[0]);sign=1 if orient>0 else -1
 for a,b in zip(tri,tri[1:]+tri[:1]):
  old=poly;poly=[]
  for p,q in zip(old,old[1:]+old[:1]):
   vp=sign*cross(b-a,p-a);vq=sign*cross(b-a,q-a)
   if vp>=-1e-10:poly.append(p)
   if (vp>=0)!=(vq>=0):poly.append(p+(q-p)*(vp/(vp-vq)))
  if not poly:break
 return poly

def plane_point(yz,tri):
 a,b,c=tri;u=D(b.y-a.y,b.z-a.z);v=D(c.y-a.y,c.z-a.z);p=yz-D(a.y,a.z);den=cross(u,v);s=cross(p,v)/den;t=cross(u,p)/den;return Vector((a.x+(b.x-a.x)*s+(c.x-a.x)*t,yz.x,yz.y))


NAMES=[f'V31 fixed temporal receiving wall {s}'for s in[-1,1]]+['V38 compact cranial inner shell','V38 fixed occipital closure plate']+[f'V33 swept temporal leaf {s} {i}'for s in[-1,1]for i in range(7)]
ADDED=[]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def apply():
 records=[];lands=[];bounds=[];root_land=[]
 # Preserve full finite source mounting lands, not just authored centres.
 rectangles=[]
 for side in[-1,1]:
  for i in range(3):
   o=bpy.data.objects[f'V31 temporal fitting root {side} {i}'];p=[o.matrix_world@v.co for v in o.data.vertices];rectangles.append((min(q.y for q in p)-.002,max(q.y for q in p)+.002,min(q.z for q in p)-.002,max(q.z for q in p)+.002))
 for side in[-1,1]:
  o=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];p=[o.matrix_world@v.co for v in o.data.vertices];protected=[]
  for i,q in enumerate(p):
   if any(a<=q.y<=b and c<=q.z<=d for a,b,c,d in rectangles):protected.append(i);continue
   rear=smooth((q.y+.34)/.080);upper=smooth((q.z-1.73)/.025);q.x-=side*(.007*rear+.003*upper*smooth((q.y+.50)/.09));q.y-=.021*rear
  install(o.name,p,[tuple(f.vertices)for f in o.data.polygons],'Tapered recessed fixed skull support; exact finite root receiving lands, no global head-thinning',records,len(o.data.polygons)-144);root_land.append({'wall':o.name,'protectedSourceVertexIndices':protected,'sourceFiniteRootRectanglesYZ':rectangles})
 o=bpy.data.objects['V38 compact cranial inner shell'];p=[o.matrix_world@v.co for v in o.data.vertices]
 for q in p:
  t=smooth((q.y+.425)/.178);q.x*=1-.085*t;q.y-=.018*t;q.z-=.011*t
 install(o.name,p,[tuple(f.vertices)for f in o.data.polygons],'Recessed rear moving inner shell beneath retained swept crown; exact front, vertical withdrawal owner retained',records,len(o.data.polygons)-136)
 # Closed source-derived head skirt, narrower lower taper but no neck bridge.
 grid('V38 fixed occipital closure plate',lambda u,v:Vector((.081*math.sin((2*u-1)*1.45)*(.71+.29*v),-.383+.107*math.cos((2*u-1)*1.45)-.018*(1-v),1.578+.103*v-.017*math.sin((2*u-1)*1.45)**2)),28,18,.004,'Tapered fixed occipital skirt, sliding overlap proposal above separately owned upper neck',records,Vector((0,1,0)))
 outlines=[
 [[-.453,1.807],[-.406,1.793],[-.305,1.742],[-.351,1.752]],
 [[-.405,1.759],[-.373,1.760],[-.278,1.697],[-.330,1.701]],
 [[-.368,1.716],[-.333,1.704],[-.289,1.637],[-.338,1.655]],
 [[-.360,1.670],[-.330,1.644],[-.316,1.592],[-.363,1.621]],
 [[-.425,1.718],[-.392,1.691],[-.362,1.646],[-.414,1.666]],
 [[-.483,1.786],[-.452,1.780],[-.393,1.725],[-.448,1.744]],
 [[-.471,1.812],[-.430,1.823],[-.362,1.785],[-.403,1.783]]]
 for side in[-1,1]:
  wall=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];wall.data.calc_loop_triangles();wp=[wall.matrix_world@v.co for v in wall.data.vertices];wn=len(wp)//2
  for i,poly in enumerate(outlines):
   # Convex directional footprints intersect actual supporting triangle faces.
   yz=[D(y,z)for y,z in poly];pieces=[]
   for tri in wall.data.loop_triangles:
    if not all(k<wn for k in tri.vertices):continue
    receiving=[wp[k]for k in tri.vertices];domain=[D(q.y,q.z)for q in receiving]
    if abs(cross(domain[1]-domain[0],domain[2]-domain[0]))<1e-11:continue
    row=clip(domain,yz)
    for j in range(1,len(row)-1):
     t=[row[0],row[j],row[j+1]];area=abs(cross(t[1]-t[0],t[2]-t[0]))*.5
     if area>1e-11:pieces.append(([plane_point(q,receiving)for q in t],int(tri.index)))
   assert pieces,(side,i,'No finite support beneath plate footprint');points=[];index={};fs=[];facekeys=[]
   for tri,source_index in pieces:
    row=[]
    for q in tri:
     key=tuple(round(v,7)for v in q)
     if key not in index:index[key]=len(points);points.append(q)
     row.append(index[key])
    if len(set(row))==3:fs.append(tuple(row));facekeys.append(source_index)
   n=len(points);lo=min(q.y for q in points);hi=max(q.y for q in points);outer=[];rootfaces=[]
   for q in points:
    u=(q.y-lo)/(hi-lo);lift=.0025*smooth((u-.32)/.68);outer.append(q+Vector((side*(.0035+lift),0,0)))
   vertices=outer+points;faces=fs+[tuple(n+k for k in reversed(t))for t in fs];ec=Counter(tuple(sorted((t[j],t[(j+1)%3])))for t in fs for j in range(3))
   for t,source_index in zip(fs,facekeys):
    if all((points[k].y-lo)/(hi-lo)<.32 for k in t):rootfaces.append({'receiverTriangleIndex':source_index,'innerTriangle':[list(points[k])for k in t]})
    for j,a in enumerate(t):b=t[(j+1)%3]
    # Boundary full side closures retain finite stock, no scalloped subdivision.
   for t in fs:
    for j,a in enumerate(t):
     b=t[(j+1)%3]
     if ec[tuple(sorted((a,b)))]==1:faces.append((a,b,n+b,n+a))
   name=f'V33 swept temporal leaf {side} {i}';install(name,vertices,faces,'Individual short swept occipital plate with clipped actual wall inner receiving surface, positive3.5–6mm axialstock',records,2*len(fs));lands.append({'plate':name,'receiver':wall.name,'actualFullInnerTriangles':len(fs),'actualRootTriangles':rootfaces,'nominalAxialStockRangeM':[.0035,.006],'YZBounds':[[min(q[k]for q in points),max(q[k]for q in points)]for k in[1,2]],'limits':'Inner surface tessellates source fixed wall, plate root contact is deliberate. Exact adjacent plate lap and moving-cover/neck clearance require separate finite screen; no engineering/load certificate.'})
 return {'changedMeshes':NAMES,'watchMeshes':NAMES,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':records,'plateReceivingLands':lands,'protectedWallLands':root_land,'construction':'18 existing meshes: tapered rear support and actual-wall seated short swept plates, recessed moving inner shell, head-owned tapered skirt. No orbital rings or new nodes.','openingAttachment':'Crown58 exterior/repair exact; cover independently withdraws nativeZ/runtimeY .08open+.14separation; fixedwall/leaves/skirt head-owned and do not bridge neck.','rigidVsFlexible':'Rigid inherited passive Maker/Mechanic/Builder, no new powered hardware.','confirmation':'Actual inventory identifies blank rear wall+coverinner mass; JulyHEADONLY and Master/Maker scope.','reconstruction':'Named silhouette, stock, receiving plate topology are authored proposal, not precise dimensions from art.','protected':'Trueoptic/bill/jaw/socket/journals/contactmarker/body and all pivots/material profiles exact.','limits':['18watch differs from prior83watch; baseline recomputed in same18 scope.','Actual finite stock/self/neighbor poses separately reported; no universal sweep or attachment acceptance.']}
