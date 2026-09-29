"""V32 bounded passive cranial-frame receiving route.

Reconstructed construction proposal, not validated engineering. Four existing
head-owned solids only: bow legs route inside the distal side guards and
anterior to the posterior guard; seats move inward along the retained shaft.
No cervical guard, shaft, owner/rest, material, or runtime change.
"""
import math
import bpy,bmesh
from mathutils import Vector

# Head-local native metres. The last two skull receiving stations are retained.
ROWS=[(.068,0,.005,.013),(.068,-.011,.050,.014),(.072,-.027,.092,.015),
      (.100,-.050,.155,.015),(.101,-.067,.234,.014),(.112,-.123,.282,.010)]
SEAT_PROFILE=[(.058,.010),(.058,.017),(.070,.017),(.070,.010)]
NAMES=[f'V31 {kind} {side}' for side in (-1,1)
       for kind in ('passive cranial load bow','cranial load bow shaft seat')]

def sample(rows,t):
 u=max(0,min(1,t))*(len(rows)-1);i=min(int(u),len(rows)-2);s=u-i
 a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
 return [.5*(2*b[k]+(-a[k]+c[k])*s+(2*a[k]-5*b[k]+4*c[k]-d[k])*s*s+(-a[k]+3*b[k]-3*c[k]+d[k])*s*s*s) for k in range(len(b))]

def bow(side):
 nu,nv=50,10;v=[];norm=[]
 def point(u,t):
  q=sample(ROWS,u);a=sample(ROWS,max(0,u-.001));b=sample(ROWS,min(1,u+.001))
  dy=b[1]-a[1];dz=b[2]-a[2];length=math.hypot(dy,dz);s=2*t-1
  return Vector((side*(q[0]+.003*(1-s*s)),q[1]-dz/length*q[3]*s,q[2]+dy/length*q[3]*s))
 for i in range(nu+1):
  for j in range(nv+1):
   u=i/nu;t=j/nv;p=point(u,t)
   du=point(min(1,u+.0001),t)-point(max(0,u-.0001),t)
   dv=point(u,min(1,t+.0001))-point(u,max(0,t-.0001))
   n=du.cross(dv);assert n.length>1e-12;n.normalize()
   if n.dot(Vector((side,0,0)))<0:n=-n
   v.append(p);norm.append(n)
 count=len(v);v += [p-.006*n for p,n in zip(v.copy(),norm)]
 f=[];stride=nv+1
 for i in range(nu):
  for j in range(nv):
   a=i*stride+j;b=a+stride;f.extend([(a,a+1,b+1,b),(count+b,count+b+1,count+a+1,count+a)])
 boundary=list(range(stride))+[i*stride+nv for i in range(1,nu+1)]+[nu*stride+j for j in range(nv-1,-1,-1)]+[i*stride for i in range(nu-1,0,-1)]
 for i,a in enumerate(boundary):b=boundary[(i+1)%len(boundary)];f.append((a,b,count+b,count+a))
 return v,f

def seat(side):
 count=64;v=[];f=[]
 for x,r in SEAT_PROFILE:
  for k in range(count):a=math.tau*k/count;v.append(Vector((side*x,r*math.cos(a),r*math.sin(a))))
 for j in range(len(SEAT_PROFILE)):
  for k in range(count):f.append((j*count+k,j*count+(k+1)%count,((j+1)%len(SEAT_PROFILE))*count+(k+1)%count,((j+1)%len(SEAT_PROFILE))*count+k))
 return v,f

def signature(o):
 return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),
         tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(f.vertices) for f in o.data.polygons),
         tuple(m.name if m else None for m in o.data.materials))

def apply():
 bpy.context.view_layer.update();head=bpy.data.objects['head']
 protected={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in NAMES}
 nodes={o.name:tuple(tuple(r) for r in o.matrix_world) for o in bpy.data.objects if o.type=='EMPTY'}
 solids=[];errors=[]
 for side in (-1,1):
  for name,geo in [(f'V31 passive cranial load bow {side}',bow(side)),(f'V31 cranial load bow shaft seat {side}',seat(side))]:
   o=bpy.data.objects[name];assert o.parent==head and not o.modifiers
   old=o.data;materials=list(old.materials);verts,faces=geo
   bpy.context.view_layer.update();transform=o.matrix_world.inverted()@head.matrix_world
   mesh=bpy.data.meshes.new(name+' V32 finite routed mesh');mesh.from_pydata([transform@p for p in verts],[],faces);mesh.update()
   for mat in materials:mesh.materials.append(mat)
   bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
   assert all(e.is_manifold for e in bm.edges),name
   if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
   volume=bm.calc_volume(signed=True);assert volume>0,name;bm.to_mesh(mesh);bm.free()
   assert all(math.isfinite(c) for v in mesh.vertices for c in v.co),name
   for p in mesh.polygons:p.use_smooth=len(p.vertices)==4
   o.data=mesh
   error=max((o.matrix_world@v.co-head.matrix_world@p).length for v,p in zip(mesh.vertices,verts));assert error<1e-6;errors.append(error)
   solids.append({'name':name,'owner':'head','closed':True,'positiveVolumeM3':volume,'wallM':.006 if 'passive' in name else None})
 bpy.context.view_layer.update()
 assert protected=={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in NAMES}
 assert nodes=={o.name:tuple(tuple(r) for r in o.matrix_world) for o in bpy.data.objects if o.type=='EMPTY'}
 return {'region':'cranial-frame-receiving-route','status':'Reconstructed passive construction proposal; discrete fit evidence separate',
  'changedMeshes':NAMES,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],
  'finiteSolids':solids,'maximumInstallationErrorM':max(errors),'protectedMeshesExact':len(protected),
  'structuralContract':{'owner':'head','neckGuardsAndShaftsExact':True,'allRestTransformsExact':True,'materialsAndEraTagsRetained':True,
   'bowHeadLocalStations':ROWS,'seatHeadLocalProfile':SEAT_PROFILE,'retainedShaftSpanM':[-.09,.09],
   'seatBoreRadiusM':.010,'retainedShaftRadiusM':.008,'seatSpanWithinShaft':True,
   'upperSkullReceivingStationsExact':ROWS[-2:]},
  'limits':['Seven discrete neck poses are screened separately; not continuous collision or load-capacity proof.',
   'Seats keep the inherited 2mm radial bore allowance; no new fastener, bushing or force simulation is claimed.',
   'Original named bows retain identity for exact introduced/inherited comparisons.']}
