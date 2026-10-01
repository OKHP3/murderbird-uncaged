"""Bill-relationship02: paired curved upper hook and substantial open lower return.
Actual HELD orbital-clearance02. Four geometry meshes, contact-marker transform only.
Source cheek receivers, actual jaw roots/socket283 and all other parts exact.
"""
import bpy,bmesh,math
from mathutils import Vector
NAMES=[f'V32 returned upper bill course {i}'for i in range(3)]+['V32 formed mandibular bowl']
PROFILE=[(-.65320,1.81944,-.59870,1.663,.094),(-.713,1.783,-.650,1.645,.083),(-.768,1.730,-.692,1.615,.062),(-.794,1.658,-.726,1.582,.042),(-.792,1.580,-.753,1.550,.022),(-.765,1.524,-.756,1.514,.006)]
COURSES=[(0,.36),(.36,.72),(.72,1)]
WALL=.003

def ease(u):u=max(0,min(1,u));return u*u*(3-2*u)
def sample(rows,t):
 q=max(0,min(1,t))*(len(rows)-1);i=min(int(q),len(rows)-2);u=q-i;a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
 r=[.5*(2*b[k]+(-a[k]+c[k])*u+(2*a[k]-5*b[k]+4*c[k]-d[k])*u*u+(-a[k]+3*b[k]-3*c[k]+d[k])*u*u*u)for k in range(len(b))]
 alpha=.36*math.sin(math.pi*t)**2+.10*t**4
 r[2]=r[0]+(1-alpha)*(r[2]-r[0]);r[3]=r[1]+(1-alpha)*(r[3]-r[1])
 return r
def ring(q,t,inner=False):
 dy,dz,cy,cz,width=sample(PROFILE,q);span=math.hypot(cy-dy,cz-dz);stock=min(WALL,.20*span,.30*width);eta=stock/span if inner else 0;w=width-stock if inner else width
 section=t*4;i=int(section)%4;u=section-int(section)
 # Explicit oriented perimeter: right flank, cutting bridge, left flank, dorsal bridge.
 if i==0:v=u;x=w*(.80+.20*math.sin(math.pi*u))
 elif i==1:v=1;x=.80*w*(1-2*u)
 elif i==2:v=1-u;x=-w*(.80+.20*math.sin(math.pi*u))
 else:v=0;x=.80*w*(-1+2*u)
 v=eta+(1-2*eta)*v
 return Vector((x,dy*(1-v)+cy*v,dz*(1-v)+cz*v))
def surface(q,t):return ring(q,t),ring(q,t,True)
def domain_checks():
 minimum=1;stock=[]
 for i in range(1001):
  q=i/1000;r=sample(PROFILE,q);assert r[2]>r[0] and r[1]>r[3] and r[4]>.003
  a=sample(PROFILE,max(0,q-.00001));b=sample(PROFILE,min(1,q+.00001));den=min(1,q+.00001)-max(0,q-.00001)
  for v in (0,.25,.5,.75,1):
   dy=((b[0]-a[0])*(1-v)+(b[2]-a[2])*v)/den;dz=((b[1]-a[1])*(1-v)+(b[3]-a[3])*v)/den;j=dy*(r[3]-r[1])-dz*(r[2]-r[0]);assert j>1e-7,(q,v,j);minimum=min(minimum,j)
  stock.append(min(WALL,.20*math.hypot(r[2]-r[0],r[3]-r[1]),.30*r[4]))
 return {'sampledOrderedDomainJacobianMin':minimum,'denseLongitudinalSamples':1001,'domainWidthSamplesPerRow':5,'explicitStockBoundMinMaxM':[min(stock),max(stock)],'method':'Direct consistently oriented right/cutting/left/dorsal perimeter, analytic inner inset within side domain. No radial normal signs. Local regularity samples not global intersection proof.'}

def contact():
 bpy.context.view_layer.update();pts=[(o.name,o.matrix_world@v.co)for o in bpy.data.objects if o.type=='MESH'and o.parent and o.parent.name=='upper-bill'for v in o.data.vertices];lead=min(pts,key=lambda p:p[1].y)
 return {'leadingObject':lead[0],'leadingPointNativeXYZ':list(lead[1]),'actualTriangleVertexBounds':[[min(p[k]for _,p in pts),max(p[k]for _,p in pts)]for k in range(3)]}
def apply():
 bpy.context.view_layer.update();originalContact=contact();records=[];seams=[];actualrings=[]
 domain=domain_checks()
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
  o['v38BillRelationship']='One globally parameterized finite plate shell, three shared seam courses; proposal'
  actual=[world@v.co for v in mesh.vertices];stock=[(actual[i]-actual[i+half]).length for i in range(half)];actualrings.append({'outerStart':actual[:nv],'outerEnd':actual[nu*nv:(nu+1)*nv],'innerStart':actual[half:half+nv],'innerEnd':actual[half+nu*nv:half+(nu+1)*nv]})
  records.append({'name':o.name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in o.data.materials],'globalParameterRange':[lo,hi],'method':'Direct lateral plate walls over ordered dorsal/cutting side domain, fixed perimeter orientation and analytic finite inner inset; all boundaries share field','closedEdgeManifold':True,'positiveVolumeM3':volume,'actualPairedThicknessVectorLengthMinMaxM':[min(stock),max(stock)],'newVertices':len(mesh.vertices)})
 for i in range(2):
  a,b=actualrings[i],actualrings[i+1];seams.append({'coursePair':[i,i+1],'parameter':COURSES[i][1],'actualOuterSeamMaxDistanceM':max((p-q).length for p,q in zip(a['outerEnd'],b['outerStart'])),'actualInnerSeamMaxDistanceM':max((p-q).length for p,q in zip(a['innerEnd'],b['innerStart'])),'tangent':'Both sides use the same global derivative, no independent courseframe','join':'Shared finite butt seam; coincident endlands not a separate lap/fastener/load certificate'})
 o=bpy.data.objects[NAMES[-1]];world=o.matrix_world.copy();inv=world.inverted();old=[v.co.copy()for v in o.data.vertices];points=[world@p for p in old];oldkeys=[(r,k)for r in range(53)for k in range(33)if r<=5 or k<=6 or k>=26];sourcehalf=len(oldkeys);assert len(points)==1712;oldlookup={k:i for i,k in enumerate(oldkeys)}
 keys=[(r,k)for r in range(53)for k in range(33)if r<=5 or k<=6 or k>=26 or r>=49];lookup={k:i for i,k in enumerate(keys)}
 root=[points[oldlookup[(14,k)]]for k in range(33)if (14,k)in oldlookup];previous=[points[oldlookup[(13,k)]]for k in range(33)if(13,k)in oldlookup];c=(root[0]+root[-1])*.5;cp=(previous[0]+previous[-1])*.5;w0=max(abs(p.x)for p in root);wp=max(abs(p.x)for p in previous)
 def hermite(a,b,m0,m1,t):return(2*t**3-3*t*t+1)*a+(t**3-2*t*t+t)*m0+(-2*t**3+3*t*t)*b+(t**3-t*t)*m1
 new=[];inner=[]
 for row,col in keys:
  if row<=14:
   i=oldlookup[(row,col)];new.append(points[i]);inner.append(points[i+sourcehalf]);continue
  u=(row-14)/38;turn=ease(u/.28);side=-1 if col<=16 else 1;edge=col/6 if col<=6 else(32-col)/6 if col>=26 else 1
  y=hermite(c.y,-.720,(c.y-cp.y)*38,-.009,u);z=hermite(c.z,1.551,(c.z-cp.z)*38,.025,u);width=hermite(w0,.009,(w0-wp)*38,-.012,u);assert width>.004
  sourceband=abs(root[6].x-root[0].x);band=min(sourceband*(1-turn)+(.023*(1-u)+.005*u)*turn,width*.72)
  sourcecol=col if col<=6 or col>=26 else 6;sourcep=points[oldlookup[(14,sourcecol)]];rootdrop=c.z-sourcep.z;depth=.038*(1-u)**.80+.0028*u
  x=side*(width-band*edge) if col<=6 or col>=26 else(width-band)*(col-16)/10
  q=Vector((x,y,z-rootdrop*(1-turn)-depth*edge*turn));stock0=points[oldlookup[(14,sourcecol)]+sourcehalf]-sourcep
  distal=ease((u-.62)/.38);stock=stock0*(1-turn)+((1-distal)*stock0.normalized()*.0045+distal*Vector((0,0,-.002)))*turn
  assert stock.length>.0015;new.append(q);inner.append(q+stock)
 half=len(new);frontfaces=[]
 for row in range(52):
  for col in range(32):
   ks=[(row,col),(row,col+1),(row+1,col+1),(row+1,col)]
   if all(k in lookup for k in ks):frontfaces.append(tuple(lookup[k]for k in ks))
 from collections import Counter
 edges=Counter(tuple(sorted((f[j],f[(j+1)%4])))for f in frontfaces for j in range(4));faces=frontfaces+[tuple(half+i for i in reversed(f))for f in frontfaces]
 for f in frontfaces:
  for j,a in enumerate(f):
   b=f[(j+1)%4]
   if edges[tuple(sorted((a,b)))]==1:faces.append((b,a,half+a,half+b))
 mesh=bpy.data.meshes.new(o.name+' united narrowing finite distal hook');mesh.from_pydata([inv@p for p in new+inner],[],faces);mesh.update()
 for mat in o.data.materials:mesh.materials.append(mat)
 o.data=mesh;bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges)
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(mesh);bm.free()
 for f in mesh.polygons:f.use_smooth=True
 assert all((mesh.vertices[lookup[(row,col)]].co-old[oldlookup[(row,col)]]).length==0 and(mesh.vertices[lookup[(row,col)]+half].co-old[oldlookup[(row,col)]+sourcehalf]).length==0 for row,col in oldkeys if row<=14)
 assert mesh.vertices[283].co==old[283];o['v38BillRelationship']='Source physicalsocket/root exact; paired substantial curved mandible unites in finite narrowing distal cap, no doubled prongs'
 records.append({'name':o.name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in o.data.materials],'closedEdgeManifold':True,'positiveVolumeM3':volume,'physicalSocketIndex283Exact':True,'sourceRootRows0to14OuterInnerExact':True,'profileDepthProposalM':'38mm nearroot tapering to2.8mm terminal; pairedstock gradually stabilizes into2mm closingwedge.','topology':'Central mouth void rows6..48,cols7..25 retained; only final4rows49..52 join both rails into one18mm-wide tapering finite distal cap. No filled gape floor.','actualNewOuterHalf':half})
 afterContact=contact();marker=bpy.data.objects['bill-contact'];oldmatrix=[list(r)for r in marker.matrix_world];m=marker.matrix_world.copy();m.translation=Vector(afterContact['leadingPointNativeXYZ']);marker.matrix_world=m;bpy.context.view_layer.update()
 return {'changedMeshes':NAMES,'changedNodes':['bill-contact'],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':records,'actualSharedSeams':seams,'orderedSideDomainChecks':domain,'globalDorsalCuttingProfile':PROFILE,'contactBefore':originalContact,'contactAfter':afterContact,'contactMarkerBeforeWorld':oldmatrix,'contactMarkerAfterWorld':[list(r)for r in marker.matrix_world],'confirmation':'Actual July head-only open constructed mouth; Master03/Maker-clean wholebird crosscheck. Native restjaw axis preserved; negative rotation not used.','reconstruction':'Paired silhouette, stock and unseen construction authored proposal, not exact rasterdimensions or ownerapproval.','protected':'Truejaw axle/journals/clevis, physicalsocket283/root0..14, optics/cheek/crown/body/materials/pivots exact.','limits':['Shared seams and closed finite topology not proof of self/interpart clearance or engineering.','Both realbill/jaw silhouettes may change; actual billcontact marker follows actual exportedupper geometry.','No runtime/sourceapp edits.']}
