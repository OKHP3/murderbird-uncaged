"""Orbital-clearance02, exact head-fit01 input: two rigid passive shield0 only.
Union-informed lateral contour, finite integral short lowerreceiver return; no hardware moves.
"""
import bpy,bmesh,math
from mathutils import Vector
NAMES=[f'V38 optic cheek shield {s} 0'for s in[-1,1]];ADDED=[]
WATCH=[f'V38 swept crown course {r} column {c} leaf {l}'for r,cs in[(0,range(7)),(1,range(7)),(2,range(7)),(3,range(1,6)),(4,range(2,5))]for c in cs for l in[1,2]]+[f'V31 fixed temporal receiving wall {s}'for s in[-1,1]]+[f'V38 optic cheek shield {s} {i}'for s in[-1,1]for i in range(3)]+[f'V33 formed lower cheek receiver {s} {i}'for s in[-1,1]for i in range(2)]+[f'V31 temporal fitting root {s} {i}'for s in[-1,1]for i in range(3)]+[f'V31 passive temporal fitting {s} {i}'for s in[-1,1]for i in range(3)]+['V38 fixed occipital closure plate']
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

def apply():
 records=[];feet=[];movement=[]
 for side in[-1,1]:
  o=bpy.data.objects[f'V38 optic cheek shield {side} 0'];old=o.data;n=len(old.vertices)//2;old.calc_loop_triangles();p=[o.matrix_world@v.co for v in old.vertices];faces=[tuple(t.vertices)for t in old.loop_triangles];dis=[]
  for q in p:
   # Lower crescent only: clear actual moving-bowl lateral union, leave orbital
   # YZ contour/upper stem exact. Smooth compact extrusion, no global surround shift.
   t=max(0,min(1,(1.711-q.z)/.035));t=t*t*(3-2*t);rear=max(0,min(1,(q.y+.610)/.035));rear=rear*rear*(3-2*rear);dx=.0065*t*rear;q.x+=side*dx;dis.append(dx)
  receiver=bpy.data.objects[f'V33 formed lower cheek receiver {side} 0'];receiver.data.calc_loop_triangles();rp=[receiver.matrix_world@v.co for v in receiver.data.vertices];rn=len(rp)//2
  candidates=[]
  for index,f in enumerate(faces):
   if not all(k<n for k in f):continue
   a=[p[k]for k in f]
   if not all(-.572<q.y<-.504 and 1.646<q.z<1.676 for q in a):continue
   at=[D(q.y,q.z)for q in a];area=abs(cross(at[1]-at[0],at[2]-at[0]))*.5;pieces=[];total=0
   for rt in receiver.data.loop_triangles:
    if not all(k>=rn for k in rt.vertices):continue
    b=[rp[k]for k in rt.vertices];bt=[D(q.y,q.z)for q in b]
    if abs(cross(bt[1]-bt[0],bt[2]-bt[0]))<1e-11:continue
    poly=clip(at,bt)
    for j in range(1,len(poly)-1):
     yz=[poly[0],poly[j],poly[j+1]];ar=abs(cross(yz[1]-yz[0],yz[2]-yz[0]))*.5
     if ar<1e-12:continue
     top=[plane_point(q,a)for q in yz];bottom=[plane_point(q,b)for q in yz];gaps=[side*(v.x-u.x)for u,v in zip(top,bottom)]
     if min(gaps)<.00020:continue
     pieces.append((yz,top,bottom,int(rt.index),b));total+=ar
   if area>1e-12 and abs(total-area)<max(1e-10,area*.0002):candidates.append((index,f,pieces,area))
  assert candidates,'No complete broad finite receiving patch'
  # Keep one connected source-face component to avoid scattered insertion feet.
  groups=[];todo=set(range(len(candidates)))
  while todo:
   seed=todo.pop();group={seed};run=[seed]
   while run:
    q=run.pop();near=[r for r in todo if len(set(candidates[q][1])&set(candidates[r][1]))>=2]
    for r in near:todo.remove(r);group.add(r);run.append(r)
   groups.append(group)
  selected=max(groups,key=lambda group:sum(candidates[q][3]for q in group));chosen=[candidates[q]for q in sorted(selected)];assert sum(q[3]for q in chosen)>2e-5,'Complete footprint too small'
  selected_indices={q[0]for q in chosen};oldfaces=faces;newfoot=[];footmeta=[];topids={};bottomids={}
  def add(point,cache):
   key=tuple(round(v,7)for v in point)
   if key not in cache:cache[key]=len(p);p.append(point)
   return cache[key]
  for index,f,pieces,area in chosen:
   orientation=cross(D(p[f[1]].y-p[f[0]].y,p[f[1]].z-p[f[0]].z),D(p[f[2]].y-p[f[0]].y,p[f[2]].z-p[f[0]].z))
   for yz,top,bottom,rt,b in pieces:
    if cross(yz[1]-yz[0],yz[2]-yz[0])*orientation<0:top.reverse();bottom.reverse()
    ti=[add(q,topids)for q in top];bi=[add(q,bottomids)for q in bottom];newfoot.append((tuple(ti),tuple(bi)));footmeta.append({'receiverTriangleIndex':rt,'receiverTriangle':[list(q)for q in b],'footTriangle':[list(q)for q in bottom],'bandTriangle':[list(q)for q in top]})
  # Refine old neighbouring edges to the same clipping vertices, then remove
  # cap patch and replace with exact receiver facets plus integral perimeter.
  from collections import Counter
  count=Counter(tuple(sorted((t[j],t[(j+1)%3])))for t,b in newfoot for j in range(3));boundary=[(t[j],t[(j+1)%3],b[j],b[(j+1)%3])for t,b in newfoot for j in range(3)if count[tuple(sorted((t[j],t[(j+1)%3]))) ]==1]
  splitpoints={i for a,b,c,d in boundary for i in[a,b]};faces=[]
  for index,f in enumerate(oldfaces):
   if index in selected_indices:continue
   loop=[]
   for j,a in enumerate(f):
    b=f[(j+1)%3];v=p[b]-p[a];cuts=[]
    for k in splitpoints:
     u=(p[k]-p[a]).dot(v)/v.length_squared
     if 1e-6<u<1-1e-6 and (p[k]-(p[a]+v*u)).length<2e-7:cuts.append((u,k))
    loop.append(a);loop +=[k for u,k in sorted(cuts)]
   if len(loop)==3:faces.append(tuple(loop))
   else:
    centre=sum((p[k]for k in loop),Vector())/len(loop);ci=len(p);p.append(centre)
    faces +=[(ci,loop[j],loop[(j+1)%len(loop)])for j in range(len(loop))]
  faces +=[b for t,b in newfoot]
  faces +=[(a,b,d,c)for a,b,c,d in boundary]
  m=bpy.data.meshes.new(o.name+' shared-tessellation finite receiver web');inv=o.matrix_world.inverted();m.from_pydata([inv@q for q in p],[],faces);m.update()
  for mat in old.materials:m.materials.append(mat)
  bm=bmesh.new();bm.from_mesh(m);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=[e for e in bm.edges if not e.is_manifold];print('BAD_EDGES',len(bad),[(len(e.link_faces),[list(v.co)for v in e.verts])for e in bad[:25]],flush=True);assert not bad,o.name
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  vol=bm.calc_volume(signed=True);assert vol>0;bm.to_mesh(m);bm.free();o.data=m;o['v38OrbitalClearance']='Union-informed corridor with shared-tessellation broad finite lowerreceiver inner-skin web'
  for face in m.polygons:face.use_smooth=False
  records.append({'name':o.name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'materials':[q.name if q else None for q in m.materials],'role':'Inherited passive rigid orbital crescent, integral lowerreceiver web','positiveVolumeM3':vol})
  triangles=[q['footTriangle']for q in footmeta];flat=[Vector(v)for t in triangles for v in t];gaps=[(Vector(v)-Vector(u)).length for q in footmeta for u,v in zip(q['bandTriangle'],q['footTriangle'])]
  feet.append({'shield':o.name,'receiver':receiver.name,'receiverSkin':'actual inner half of finite mesh','sourceBandFacesReplaced':len(chosen),'actualMatchedFootTriangles':footmeta,'footAreaYZM2':sum(q[3]for q in chosen),'footYZExtentM':[max(q[k]for q in flat)-min(q[k]for q in flat)for k in[1,2]],'returnSpanRangeM':[min(gaps),max(gaps)],'method':'Actual receiver triangles clipped against whole contiguous source-band face patch, shared boundary tessellation and closed integral perimeter. No long far-wall bridge; no centroid-only support. Dimensions are actual observations, not load-bearing approval.'})
  movement.append({'name':o.name,'maximumOriginalVertexOutboardShiftM':max(dis),'YZOriginalVerticesExact':True,'pairedAxialBandStockM':.0045,'limits':'Lateral-only field preserves original side profile; actual finite triangle screen and support check required, no universal clearance.'})
 return {'changedMeshes':NAMES,'watchMeshes':WATCH,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':records,'integralReceivingReturns':feet,'lateralField':movement,'construction':'Only two shield0 meshes; local lower crescent outboard field and connected rear finite lowerreceiver land; exact source YZ outline.','openingAttachment':'Head-owned only; cranial-cover/neck/jaw/body frames and all geometry untouched.','rigidVsFlexible':'Rigid inherited passive all3eras, no new powered hardware.','confirmation':'Actual source hardware union surveyed at jaw0/.10/.16/.32 and optical cup/floor/lip/aperture; source hashes pinned.','reconstruction':'6.5mm maximum proposed local lateral relief and4.5mm pairedbandstock; receiving web dimensions recorded, not engineering approval.','protected':'Repaired crown, optic hardware, bowl/socket/journals/bill/contact/body exact.','limits':['Integral land proof uses full actual finite receiving triangle, not nearest centroid. Its size/support role remains proposal.','All same83 watch and full neighbor pool remain mandatory; no hidden contact exclusions.']}
