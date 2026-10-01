"""Orbital-clearance01, exact head-fit01 input: two rigid passive shield0 only.
Union-informed lateral contour, finite integral rear wall return; no hardware moves.
"""
import bpy,bmesh,math
from mathutils import Vector
NAMES=[f'V38 optic cheek shield {s} 0'for s in[-1,1]];ADDED=[]
WATCH=[f'V38 swept crown course {r} column {c} leaf {l}'for r,cs in[(0,range(7)),(1,range(7)),(2,range(7)),(3,range(1,6)),(4,range(2,5))]for c in cs for l in[1,2]]+[f'V31 fixed temporal receiving wall {s}'for s in[-1,1]]+[f'V38 optic cheek shield {s} {i}'for s in[-1,1]for i in range(3)]+[f'V33 formed lower cheek receiver {s} {i}'for s in[-1,1]for i in range(2)]+[f'V31 temporal fitting root {s} {i}'for s in[-1,1]for i in range(3)]+[f'V31 passive temporal fitting {s} {i}'for s in[-1,1]for i in range(3)]+['V38 fixed occipital closure plate']
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
 a,b,c=tri;u=Vector((b.y-a.y,b.z-a.z));v=Vector((c.y-a.y,c.z-a.z));p=yz-Vector((a.y,a.z));den=cross(u,v);s=cross(p,v)/den;t=cross(u,p)/den;return a+(b-a)*s+(c-a)*t

def apply():
 records=[];feet=[];movement=[]
 for side in[-1,1]:
  o=bpy.data.objects[f'V38 optic cheek shield {side} 0'];old=o.data;n=len(old.vertices)//2;old.calc_loop_triangles();p=[o.matrix_world@v.co for v in old.vertices];faces=[tuple(t.vertices)for t in old.loop_triangles];dis=[]
  for q in p:
   # Lower crescent only: clear actual moving-bowl lateral union, leave orbital
   # YZ contour/upper stem exact. Smooth compact extrusion, no global surround shift.
   t=max(0,min(1,(1.711-q.z)/.035));t=t*t*(3-2*t);rear=max(0,min(1,(q.y+.610)/.035));rear=rear*rear*(3-2*rear);dx=.008*t*rear;q.x+=side*dx;dis.append(dx)
  wall=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];wall.data.calc_loop_triangles();wp=[wall.matrix_world@v.co for v in wall.data.vertices];wn=len(wp)//2;best=None
  for index,f in enumerate(faces):
   if not all(k>=n for k in f):continue
   a=[p[k]for k in f]
   if not all(q.y<-.605 and q.z>1.651 for q in a):continue
   at=[Vector((q.y,q.z))for q in a]
   for wt in wall.data.loop_triangles:
    if not all(k<wn for k in wt.vertices):continue
    b=[wp[k]for k in wt.vertices];bt=[Vector((q.y,q.z))for q in b];poly=clip(at,bt)
    for j in range(1,len(poly)-1):
     t=[poly[0],poly[j],poly[j+1]];area=abs(cross(t[1]-t[0],t[2]-t[0]))*.5
     if best is None or area>best[0]:best=(area,index,f,t,a,b,int(wt.index))
  assert best and best[0]>1e-7, 'No actual supported integral return'
  area,index,f,foot,band,receiving,wt=best
  if cross(foot[1]-foot[0],foot[2]-foot[0])*cross(Vector((band[1].y-band[0].y,band[1].z-band[0].z)),Vector((band[2].y-band[0].y,band[2].z-band[0].z)))<0:foot.reverse()
  foot=min([foot[i:]+foot[:i]for i in range(3)],key=lambda row:sum((row[k]-Vector((band[k].y,band[k].z))).length_squared for k in range(3)))
  top=[plane_point(q,band)for q in foot];bottom=[plane_point(q,receiving)for q in foot];start=len(p);p+=top+bottom;faces.pop(index)
  for k in range(3):j=(k+1)%3;faces.append((f[k],f[j],start+j,start+k));faces.append((start+k,start+j,start+3+j,start+3+k))
  faces.append((start+3,start+4,start+5));m=bpy.data.meshes.new(o.name+' union crescent + integral finite wall return');inv=o.matrix_world.inverted();m.from_pydata([inv@q for q in p],[],faces);m.update()
  for mat in old.materials:m.materials.append(mat)
  bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),o.name
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  vol=bm.calc_volume(signed=True);assert vol>0;bm.to_mesh(m);bm.free();o.data=m;o['v38OrbitalClearance']='Union-informed lateral crescent plus finite connected rear receiving return'
  for i,face in enumerate(m.polygons):face.use_smooth=i<len(faces)-7
  records.append({'name':o.name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'materials':[q.name if q else None for q in m.materials],'role':'Inherited passive rigid orbital crescent, integral wall return','positiveVolumeM3':vol})
  feet.append({'shield':o.name,'receiver':wall.name,'receiverOuterTriangleIndex':wt,'actualReceiverTriangle':[list(q)for q in receiving],'footCorners':[list(q)for q in bottom],'bandReturnCorners':[list(q)for q in top],'footAreaM2':area,'footEdgeLengthsM':[(bottom[k]-bottom[(k+1)%3]).length for k in range(3)],'returnSpanM':[(bottom[k]-top[k]).length for k in range(3)],'footBottomVertexIndices':list(range(start+3,start+6)),'method':'Whole triangular land clipped within a single actual receiving triangle, exact shared plane/inside footprint; connected closed solid web. Area/span are actual observations, not load-bearing acceptance.'})
  movement.append({'name':o.name,'maximumOriginalVertexOutboardShiftM':max(dis),'YZOriginalVerticesExact':True,'pairedAxialBandStockM':.0045,'limits':'Lateral-only field preserves original side profile; actual finite triangle screen and support check required, no universal clearance.'})
 return {'changedMeshes':NAMES,'watchMeshes':WATCH,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':records,'integralReceivingReturns':feet,'lateralField':movement,'construction':'Only two shield0 meshes; local lower crescent outboard field and connected rear finite wall land; exact source YZ outline.','openingAttachment':'Head-owned only; cranial-cover/neck/jaw/body frames and all geometry untouched.','rigidVsFlexible':'Rigid inherited passive all3eras, no new powered hardware.','confirmation':'Actual source hardware union surveyed at jaw0/.10/.16/.32 and optical cup/floor/lip/aperture; source hashes pinned.','reconstruction':'8mm maximum proposed local lateral relief and4.5mm pairedbandstock; receiving web dimensions recorded, not engineering approval.','protected':'Repaired crown, optic hardware, bowl/socket/journals/bill/contact/body exact.','limits':['Integral land proof uses full actual finite receiving triangle, not nearest centroid. Its size/support role remains proposal.','All same83 watch and full neighbor pool remain mandatory; no hidden contact exclusions.']}
