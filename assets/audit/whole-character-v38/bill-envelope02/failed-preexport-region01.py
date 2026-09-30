"""Bill-envelope02: one global outer/inner curved shell; shared course seams.
Actual breast-course02. Four geometry meshes, contact-marker transform only.
Source cheek receivers, actual jaw roots/socket397 and all other parts exact.
"""
import bpy,bmesh,math
from mathutils import Vector
NAMES=[f'V32 returned upper bill course {i}'for i in range(3)]+['V32 formed mandibular bowl']
PROFILE=[(-.65320,1.81944,-.59870,1.663,.105),(-.714,1.803,-.660,1.655,.099),(-.778,1.755,-.724,1.621,.076),(-.810,1.690,-.772,1.587,.055),(-.811,1.606,-.797,1.562,.032),(-.765,1.496,-.758,1.494,.007)]
COURSES=[(0,.36),(.36,.72),(.72,1)]
WALL=.003

def ease(u):u=max(0,min(1,u));return u*u*(3-2*u)
def sample(rows,t):
 q=max(0,min(1,t))*(len(rows)-1);i=min(int(q),len(rows)-2);u=q-i;a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
 return [.5*(2*b[k]+(-a[k]+c[k])*u+(2*a[k]-5*b[k]+4*c[k]-d[k])*u*u+(-a[k]+3*b[k]-3*c[k]+d[k])*u*u*u)for k in range(len(b))]
def outer(q,t):
 dy,dz,cy,cz,width=sample(PROFILE,q);angle=math.tau*t;f=(1-math.cos(angle))*.5;sgn=1 if math.sin(angle)>=0 else-1;x=sgn*width*abs(math.sin(angle))**.65
 # Actual dorsal and cutting contours stay independent, side surface spans them.
 return Vector((x,dy*(1-f)+cy*f-.002*math.sin(math.pi*f)**2,dz*(1-f)+cz*f))
def surface(q,t):
 p=outer(q,t);du=outer(min(1,q+.0001),t)-outer(max(0,q-.0001),t);dv=outer(q,(t+.0001)%1)-outer(q,(t-.0001)%1);n=du.cross(dv);assert n.length>1e-12,(q,t);n.normalize();row=sample(PROFILE,q);ref=Vector((p.x,p.y-(row[0]+row[2])*.5,p.z-(row[1]+row[3])*.5))
 if n.dot(ref)<0:n=-n
 span=math.hypot(row[0]-row[2],row[1]-row[3]);stock=min(WALL,.28*span,.35*row[4])
 return p,p-stock*n

def contact():
 bpy.context.view_layer.update();pts=[(o.name,o.matrix_world@v.co)for o in bpy.data.objects if o.type=='MESH'and o.parent and o.parent.name=='upper-bill'for v in o.data.vertices];lead=min(pts,key=lambda p:p[1].y)
 return {'leadingObject':lead[0],'leadingPointNativeXYZ':list(lead[1]),'actualTriangleVertexBounds':[[min(p[k]for _,p in pts),max(p[k]for _,p in pts)]for k in range(3)]}
def apply():
 bpy.context.view_layer.update();originalContact=contact();records=[];seams=[];actualrings=[]
 dense=[sample(PROFILE,i/1000)for i in range(1001)]
 assert all(r[2]>r[0] and r[1]>r[3] and r[4]>.003 for r in dense),'Global dorsal/cutting ordering or finite tip width failed'
 for course,(lo,hi)in enumerate(COURSES):
  o=bpy.data.objects[NAMES[course]];world=o.matrix_world.copy();inv=world.inverted();nu,nv=48,48;front=[];back=[]
  for i in range(nu+1):
   q=lo+(hi-lo)*i/nu
   for k in range(nv):a,b=surface(q,k/nv);front.append(a);back.append(b)
  verts=front+back;half=len(front);faces=[]
  for i in range(nu):
   for k in range(nv):a=i*nv+k;b=i*nv+(k+1)%nv;faces.extend([(a,b,b+nv,a+nv),(half+a+nv,half+b+nv,half+b,half+a)])
  for k in range(nv):n=(k+1)%nv;faces.extend([(n,k,half+k,half+n),(nu*nv+k,nu*nv+n,half+nu*nv+n,half+nu*nv+k)])
  mesh=bpy.data.meshes.new(o.name+' global finite envelope course');mesh.from_pydata([inv@p for p in verts],[],faces);mesh.update()
  for m in o.data.materials:mesh.materials.append(m)
  o.data=mesh;bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),o.name
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(mesh);bm.free()
  for f in mesh.polygons:f.use_smooth=True
  o['v38BillEnvelope']='One globally parameterized finite plate shell, three shared seam courses; proposal'
  actual=[world@v.co for v in mesh.vertices];stock=[(actual[i]-actual[i+half]).length for i in range(half)];actualrings.append({'outerStart':actual[:nv],'outerEnd':actual[nu*nv:(nu+1)*nv],'innerStart':actual[half:half+nv],'innerEnd':actual[half+nu*nv:half+(nu+1)*nv]})
  records.append({'name':o.name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in o.data.materials],'globalParameterRange':[lo,hi],'method':'Side shell between independently authored dorsal/cutting profile, restrained transverse camber; outer/inner fields identical across allcourse boundaries','closedEdgeManifold':True,'positiveVolumeM3':volume,'normalStockMinMaxM':[min(stock),max(stock)],'newVertices':len(mesh.vertices)})
 for i in range(2):
  a,b=actualrings[i],actualrings[i+1];seams.append({'coursePair':[i,i+1],'parameter':COURSES[i][1],'actualOuterSeamMaxDistanceM':max((p-q).length for p,q in zip(a['outerEnd'],b['outerStart'])),'actualInnerSeamMaxDistanceM':max((p-q).length for p,q in zip(a['innerEnd'],b['innerStart'])),'tangent':'Both sides use the same global derivative, no independent courseframe','join':'Shared finite butt seam; coincident endlands not a separate lap/fastener/load certificate'})
 o=bpy.data.objects[NAMES[-1]];world=o.matrix_world.copy();inv=world.inverted();old=[v.co.copy()for v in o.data.vertices];points=[world@v for v in old];assert len(points)==3498;sourcehalf=1749;stride=33;seam=14
 root=points[seam*stride:(seam+1)*stride];prev=points[(seam-1)*stride:seam*stride];c=(root[0]+root[-1])*.5;cp=(prev[0]+prev[-1])*.5;w0=max(abs(p.x)for p in root);wp=max(abs(p.x)for p in prev)
 def hermite(a,b,m0,m1,t):return(2*t**3-3*t*t+1)*a+(t**3-2*t*t+t)*m0+(-2*t**3+3*t*t)*b+(t**3-t*t)*m1
 keys=[(r,k)for r in range(53)for k in range(33)if r<=seam or k<=4 or k>=28];lookup={k:i for i,k in enumerate(keys)};front=[];back=[]
 for row,col in keys:
  src=row*stride+col
  if row<=seam:front.append(points[src]);back.append(points[src+sourcehalf]);continue
  u=(row-seam)/(52-seam);turn=ease(u/.28);side=-1 if col<=4 else 1;edge=col/4 if side<0 else(32-col)/4
  y=hermite(c.y,-.754,(c.y-cp.y)*(52-seam),-.018,u);z=hermite(c.z,1.565,(c.z-cp.z)*(52-seam),.045,u);width=hermite(w0,.009,(w0-wp)*(52-seam),-.009,u);assert width>.004
  sourceband=abs(root[4].x-root[0].x);band=sourceband*(1-turn)+.007*turn;band=min(band,width*.6)
  x=side*(width-band*edge);rootdrop=c.z-root[col].z;drop=rootdrop*(1-turn)+.006*edge*turn;pnt=Vector((x,y,z-drop));oldstock=points[seam*stride+col+sourcehalf]-points[seam*stride+col];stock=oldstock*(1-turn)+Vector((0,0,-.0045))*turn
  assert stock.length>.002;front.append(pnt);back.append(pnt+stock)
 half=len(front);faces=[];frontfaces=[]
 for row in range(52):
  for col in range(32):
   ks=[(row,col),(row,col+1),(row+1,col+1),(row+1,col)]
   if all(k in lookup for k in ks):frontfaces.append(tuple(lookup[k]for k in ks))
 from collections import Counter
 edges=Counter(tuple(sorted((f[j],f[(j+1)%4])))for f in frontfaces for j in range(4));faces.extend(frontfaces);faces.extend(tuple(half+i for i in reversed(f))for f in frontfaces)
 for f in frontfaces:
  for j in range(4):
   a,b=f[j],f[(j+1)%4]
   if edges[tuple(sorted((a,b)))]==1:faces.append((b,a,half+a,half+b))
 mesh=bpy.data.meshes.new(o.name+' open paired finite lower return');mesh.from_pydata([inv@v for v in front+back],[],faces);mesh.update()
 for m in o.data.materials:mesh.materials.append(m)
 o.data=mesh;assert o.data.vertices[397].co==old[397];assert all((o.data.vertices[i].co-old[i]).length<1e-7 for i in range(495))
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),'Open rails must be finite closed stock'
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(mesh);bm.free()
 for f in mesh.polygons:f.use_smooth=True
 o['v38BillEnvelope']='Exact functional socket root; true through-opening between narrow paired descending rails with closed inside rims'
 new=[world@v.co for v in mesh.vertices];stock=[(new[i]-new[i+half]).length for i in range(half)];records.append({'name':o.name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in o.data.materials],'method':'First15 source rows outer/inner exact; distal central floor topologically absent; two narrow rails connect to root with closed inside/outer rims and finite underside. No filled distal mouth sheet.','closedEdgeManifold':True,'positiveVolumeM3':volume,'newVertices':len(mesh.vertices),'sourceOuterRootVerticesExact':495,'sourceInnerRootVerticesExact':495,'socket397Exact':True,'innerRootIndexMap':'source1749+i becomes new'+str(half)+'+i, i0..494','pairedStockLengthMinMaxM':[min(stock),max(stock)],'distalStock':'4.5mm vertical paired wall at completed transition; length not claimed equal normal thickness','throughOpening':'Rows15..52 columns5..27 absent; inner perimeter walls close stock, source root joins both rails'})
 afterContact=contact();marker=bpy.data.objects['bill-contact'];oldmatrix=[list(r)for r in marker.matrix_world];m=marker.matrix_world.copy();m.translation=Vector(afterContact['leadingPointNativeXYZ']);marker.matrix_world=m;bpy.context.view_layer.update()
 return {'changedMeshes':NAMES,'changedNodes':['bill-contact'],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':records,'actualSharedSeams':seams,'globalDorsalCuttingProfile':PROFILE,'contactBefore':originalContact,'contactAfter':afterContact,'contactMarkerBeforeWorld':oldmatrix,'contactMarkerAfterWorld':[list(r)for r in marker.matrix_world],'contactLandmarksChanged':True,'confirmation':'ActualJuly HEAD ONLY blade-like broadroot curved hook/narrow pairedmouth; Master03/Maker-clean wholebird crosscheck','reconstruction':'Exactprofiles, finite stock/seams/hidden interfaces authored, not rasterdimensions/manufacturing acceptance','limits':['Four lowercheek receivers and real coaxial hardware untouched; original socket397/first15 root rows exact; distal bowl topology reconstructed.','Shared seam/pairednormalstock not continuouscollision/selfintersection/fabrication certificate.','Runtime actualtrianglecontact solver root-owned, no fixedmarker substitute.']}
