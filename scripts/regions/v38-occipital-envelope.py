"""Occipital-envelope02, pinned orbital-clearance02.18 existing passive meshes.
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
   rear=smooth((q.y+.34)/.080);upper=smooth((q.z-1.73)/.025);q.x-=side*(.007*rear+.003*upper*smooth((q.y+.50)/.09));q.y-=.039*rear
  install(o.name,p,[tuple(f.vertices)for f in o.data.polygons],'Tapered recessed fixed skull support; exact finite root receiving lands, no global head-thinning',records,len(o.data.polygons)-144);root_land.append({'wall':o.name,'protectedSourceVertexIndices':protected,'sourceFiniteRootRectanglesYZ':rectangles})
 o=bpy.data.objects['V38 compact cranial inner shell'];p=[o.matrix_world@v.co for v in o.data.vertices]
 for q in p:
  t=smooth((q.y+.425)/.178);q.x*=1-.13*t;q.y-=.047*t;q.z-=.022*t
 install(o.name,p,[tuple(f.vertices)for f in o.data.polygons],'Recessed rear moving inner shell beneath retained swept crown; exact front, vertical withdrawal owner retained',records,len(o.data.polygons)-136)
 # Fixed compound-curved receiving skin and eight wrapped downward courses share
 # the same surface; upper temporal leaves0/5/6 remain exact source geometry.
 def surface(theta,v):
  return Vector((.084*math.sin(theta)*(.73+.27*v),-.314+.044*math.cos(theta),1.580+.180*v-.012*math.sin(theta)**2))
 grid('V38 fixed occipital closure plate',lambda u,v:surface((2*u-1)*1.48,v),52,32,.004,'Compound curved fixed nape receiving shell, recessed beneath independent descending leaves',records,Vector((0,1,0)))
 for side in[-1,1]:
  for index,base in enumerate([.76,.53,.30,.055],start=1):
   # Full plates wrap from the lateral skull toward the back, differing sweep
   # and vertical reach rather than a common scalloped outer blanket.
   def fn(u,v,side=side,index=index,base=base):
    theta=side*(.12+(1.35-.055*(index%2))*u)
    h=base+(.30+.015*(index%2))*v+.055*math.sin(math.pi*u)-(.095+.015*(index%2))*u
    q=surface(theta,h)
    # Upper plates are outboard of lower laps. Their own top receiving return
    # descends to the common support field, preserving nominal3.2mm stock.
    layer=(4-index)*.0036
    q.y+=.0008+.0032+layer*(1-smooth((v-.80)/.20))
    return q
   name=f'V33 swept temporal leaf {side} {index}'
   grid(name,fn,24,14,.0032,'Short broad swept occipital course; direct shared support surface, closed3.2mm axialstock and formed upper return',records,Vector((0,1,0)))
   lands.append({'plate':name,'receiver':'V38 fixed occipital closure plate','surfaceParameter':'theta side(.12+(1.35-.055parity)u), height base+(.30+.015parity)v+.055sin(pi u)-(.095+.015parity)u','baseHeightParameter':base,'nominalAxialStockRangeM':[.0032,.0032],'upperReceivingLand':'v>=1 top inner boundary is shared support surface+.0008m inY; finite formed return above0.8. Full faces/side returns require strict screen; nominalgap not supported-attachment acceptance.','lowerLap':'3.6mm stepped layer separation between descending courses; actual volume/lap check separately, not nominalPASS'})
 return {'changedMeshes':[n for n in NAMES if not n.startswith('V33 swept temporal leaf') or int(n.split()[-1]) in [1,2,3,4]],'watchMeshes':NAMES,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':records,'plateReceivingLands':lands,'protectedWallLands':root_land,'construction':'12 actual changed existing meshes within18watch: rear support and eight broader wrapped nape courses with shared curved support, recessed moving inner shell; upper temporal leaves0/5/6 source-exact. No orbital rings or new nodes.','openingAttachment':'Crown58 exterior/repair exact; cover independently withdraws nativeZ/runtimeY .08open+.14separation; fixedwall/leaves/skirt head-owned and do not bridge neck.','rigidVsFlexible':'Rigid inherited passive Maker/Mechanic/Builder, no new powered hardware.','confirmation':'Actual inventory identifies blank rear wall+coverinner mass; JulyHEADONLY and Master/Maker scope.','reconstruction':'Named silhouette, stock, receiving plate topology are authored proposal, not precise dimensions from art.','protected':'Trueoptic/bill/jaw/socket/journals/contactmarker/body and all pivots/material profiles exact.','limits':['18watch differs from prior83watch; baseline recomputed in same18 scope.','Actual finite stock/self/neighbor poses separately reported; no universal sweep or attachment acceptance.']}
