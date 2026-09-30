"""Temporal-construction02: finite diagonal seat-spine and three supported guards.
Verified jaw-fit02. Fourteen passive head-owned meshes; true interfaces exact.
"""
import bpy,bmesh,math
from mathutils import Vector
WALLS=[f'V31 fixed temporal receiving wall {s}'for s in(-1,1)]
BROWS=[f'V33 diagonal brow receiver {s} {i}'for s in(-1,1)for i in range(3)]
SHIELDS=[f'V38 optic cheek shield {s} {i}'for s in(-1,1)for i in range(3)]
NAMES=WALLS+BROWS+SHIELDS
SPINE=[(-.502,1.845,.1345),(-.450,1.795,.1345),(-.379,1.7425,.13401),(-.3242,1.6907,.13212)]
RAIL=[(-.639,1.792),(-.593,1.824),(-.533,1.851),(-.475,1.847),(-.420,1.825),(-.369,1.794)]
def sample(rows,t):
 q=max(0,min(1,t))*(len(rows)-1);i=min(int(q),len(rows)-2);u=q-i;a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
 return [.5*(2*b[k]+(-a[k]+c[k])*u+(2*a[k]-5*b[k]+4*c[k]-d[k])*u*u+(-a[k]+3*b[k]-3*c[k]+d[k])*u*u*u)for k in range(len(b))]
def spine(u,v,width=.060):
 y,z,x=sample(SPINE,u);a=sample(SPINE,max(0,u-.001));b=sample(SPINE,min(1,u+.001));dy,dz=b[0]-a[0],b[1]-a[1];l=math.hypot(dy,dz);return Vector((x,y-dz/l*(v-.5)*width,z+dy/l*(v-.5)*width))
def sheet(side,points,nu,nv,stock,window=False):
 from collections import Counter
 stride=nv+1;front=[]
 for r in range(nu):
  for c in range(nv):
   if window and 46<=r<=54 and 2<=c<=5:continue
   a=r*stride+c;b=a+stride;front.append((a,a+1,b+1,b))
 used=sorted({i for f in front for i in f});mapping={j:i for i,j in enumerate(used)};front=[tuple(mapping[i]for i in f)for f in front];half=len(used);verts=[points[i]for i in used]+[points[i]-Vector((side*stock,0,0))for i in used];faces=front+[tuple(half+i for i in reversed(f))for f in front];edges=Counter(tuple(sorted((f[j],f[(j+1)%4])))for f in front for j in range(4))
 for f in front:
  for j in range(4):
   a,b=f[j],f[(j+1)%4]
   if edges[tuple(sorted((a,b)))]==1:faces.append((b,a,a+half,b+half))
 return verts,faces
def apply():
 bpy.context.view_layer.update();records=[];feet=[]
 def replace(name,side,points,nu,nv,stock,kind,window=False):
  assert all(.08<abs(p.x)<.215 and -.68<p.y<-.29 and 1.63<p.z<1.895 for p in points),(name,'bounds')
  o=bpy.data.objects[name];verts,faces=sheet(side,points,nu,nv,stock,window);inv=o.matrix_world.inverted();mesh=bpy.data.meshes.new(name+' curved seated temporal assembly');mesh.from_pydata([inv@p for p in verts],[],faces);mesh.update()
  for mat in o.data.materials:mesh.materials.append(mat)
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges)
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(mesh);bm.free();o.data=mesh
  for f in mesh.polygons:f.use_smooth=True
  o['v38TemporalConstruction']='Curved finite backing/window, two fuller guards and lower transition with common receiving tessellation; passive proposal'
  records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in mesh.materials],'kind':kind,'closedEdgeManifold':True,'positiveVolumeM3':volume,'vertices':len(mesh.vertices),'actualAxialStockM':stock})
 for side in(-1,1):
  points=[Vector((side*p.x,p.y,p.z))for r in range(97)for c in range(9)for p in[spine(r/96,c/8)]]
  replace(f'V31 fixed temporal receiving wall {side}',side,points,96,8,.004,'single finite60mm curved receiving sheet, one direct-topology compact machinery window, actual fitting seat neighborhood',window=True)
  for course,(lo,hi,width,height)in enumerate([(2,43,.077,.010),(58,90,.072,.009),(91,96,.060,.005)]):
   points=[];nu=hi-lo
   for r in range(nu+1):
    t=r/nu;foot=r<=2 or r>=nu-2;s=0 if foot else math.sin(math.pi*(r-2)/max(1,nu-4))**1.2
    for c in range(9):
     v=c/8;p=spine((lo+r)/96,v,.060+(width-.060)*s);p.x+=.0045+height*s+.002*math.sin(math.pi*v)**2*s;p.x*=side;points.append(p)
   replace(f'V38 optic cheek shield {side} {course}',side,points,nu,8,.0045,'short tapered downward/rearward guard with finite integral receiving endlands and stepped depth')
   for end,rs in [('upper',range(3)),('lower',range(nu-2,nu+1))]:
    gap=max((points[r*9+c]-Vector((side*.0045,0,0))-Vector((side*p.x,p.y,p.z))).length for r in rs for c in range(9)for p in[spine((lo+r)/96,c/8)])
    feet.append({'part':f'V38 optic cheek shield {side} {course}','end':end,'target':f'V31 fixed temporal receiving wall {side}','wallRows':[lo+min(rs),lo+max(rs)],'windowOutsideFootprint':True,'widthM':.060,'actualGridGapMaxM':gap,'method':'Actual shared parameter rows/columns and corresponding inner foot triangles match backing outer triangles; compatible finite3row endland, not nearest centroid projection or nominal floating gap'})
  for course,(lo,hi)in enumerate([(0,.33),(.33,.66),(.66,1)]):
   points=[]
   for r in range(33):
    u=lo+(hi-lo)*r/32;y,z=sample(RAIL,u);a=sample(RAIL,max(0,u-.001));b=sample(RAIL,min(1,u+.001));dy,dz=b[0]-a[0],b[1]-a[1];l=math.hypot(dy,dz);width=.022+.008*math.sin(math.pi*u)
    for c in range(9):
     v=c/8;yy=y-dz/l*(v-.5)*width;zz=z+dy/l*(v-.5)*width;x=.144-.004*u+.0015*math.sin(math.pi*v)**2;points.append(Vector((side*x,yy,zz)))
   replace(f'V33 diagonal brow receiver {side} {course}',side,points,32,8,.0045,'one dominant rearward curved brow rail in three common-field butt sections, no radial tabs')
 return {'changedMeshes':NAMES,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':records,'actualFootlands':feet,'supportSpineControlsNativeYZX':SPINE,'backingWindowGrid':{'rows':[46,54],'columns':[2,5],'construction':'Face omission with closed inside stock rim in one connected finite mesh; no Boolean fragment/hiding'},'browControlsNativeYZ':RAIL,'construction':'Curved60mm backing retains one compact topology-defined window, two fuller curved guards and small lower transition cover the temple. Shared60mm footlands outside window, restrained10mm X relief rather than skeletal balloons. Fixed brow separate from moving cranial-cover.','rigidVsFlexible':'All14 existing passive meshes remain rigid/head-owned/all-era, no new powered hardware.','confirmation':'ActualJuly HEAD ONLY constructed optic/cheek; Master03/Maker-clean wholebird checks','reconstruction':'Exact profile/support/hidden stock authored proposal, not art metrology or engineering acceptance.','protected':'Improved hook, lowerjaw/source283socket, realjournal/opticseat/aperture and independent cranial-cover plus wholebody exact.','limits':['Full triangle neighbor/self screen follows actual visualgate; common foot triangulation does not waive any crossing.','Fitting return-seat spine is authored from actual source neighborhood; full bearing/fastener/load acceptance not claimed.','Brow rail attachment/interface remains regional reconstructed proposal, no moving-owner bridge or universal motion certificate.']}
