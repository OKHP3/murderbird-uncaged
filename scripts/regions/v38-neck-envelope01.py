"""Coherent rigid neck crescent guards plus finite owner-local branched carriers.
Authored envelope/support reconstruction, not reference metrology or fit approval.
"""
import bpy,bmesh,math,json,itertools
from mathutils import Vector
GUARDS=[f'V23 cervical {c} directional guard {g}'for c in range(1,5)for g in range(1,11)]
THROAT=[f'V33 tapered throat cheek plate {s} {r} {c}'for s in(-1,0,1)for r in(0,1)for c in range(3)]
OWNERS=['neck','cervical-mid-a','cervical-mid-b','cervical-upper','head']
YOKES=[f'V38 curved-neck formed yoke {owner} {side}'for owner in OWNERS for side in(-1,1)]
ANGLES={1:-1.10,2:-.55,3:0,4:.55,5:1.10,6:1.78,7:2.46,8:-2.46,9:-1.78,10:math.pi}
# z/front/rear/halfwidth: strong swept cheek-to-breast C, deliberate side machinery reveal.
PROFILE=[(1.195,-.373,-.066,.173),(1.24,-.413,-.091,.164),(1.29,-.453,-.126,.153),(1.345,-.493,-.163,.146),(1.40,-.521,-.198,.140),(1.46,-.542,-.228,.134),(1.52,-.553,-.244,.129),(1.59,-.548,-.257,.126)]
BOUNDS=[(1.194,1.289),(1.246,1.340),(1.296,1.387),(1.341,1.455)]
def profile(z):
 for a,b in zip(PROFILE,PROFILE[1:]):
  if z<=b[0]:
   t=max(0,min(1,(z-a[0])/(b[0]-a[0])));t=t*t*(3-2*t);return [a[i]*(1-t)+b[i]*t for i in range(1,4)]
 return list(PROFILE[-1][1:])
def point(z,theta,offset=0):
 front,rear,w=profile(z);cy=(front+rear)/2;ry=(rear-front)/2
 return Vector(((w+offset)*math.sin(theta),cy-(ry+offset)*math.cos(theta),z))

def sector(z,theta,offset,ci):
 p=point(z,theta,offset)
 # Local-X bearing-centred surface of revolution only in an adjoining overlap band.
 # Distinct front/rear radii preserve the asymmetric rest C; side windows remain qualified.
 jointnames=['neck','cervical-mid-a','cervical-mid-b','cervical-upper','head']
 choices=[]
 if ci>0:choices.append((bpy.data.objects[jointnames[ci]].matrix_world.translation.copy(),1))
 if ci<4:choices.append((bpy.data.objects[jointnames[ci+1]].matrix_world.translation.copy(),-1))
 if not choices:return p
 pivot,order=min(choices,key=lambda q:abs(z-q[0].z));dz=z-pivot.z
 extent=.065 if pivot.z>1.38 else .030
 if abs(dz)>extent+.015:return p
 front,rear,w=profile(pivot.z);cy=(front+rear)/2;ry=(rear-front)/2
 ratio=min(.985,abs(p.x)/w);yedge=cy-ry*math.sqrt(1-ratio*ratio)*(1 if math.cos(theta)>=0 else-1)
 radius=abs(yedge-pivot.y)+order*.004+offset
 dz1=max(-radius*.86,min(radius*.86,dz));y=pivot.y+(1 if yedge>pivot.y else-1)*math.sqrt(max(1e-8,radius*radius-dz1*dz1))
 blend=1 if abs(dz)<=extent else max(0,1-(abs(dz)-extent)/.015)
 blend=blend*blend*(3-2*blend);return p*(1-blend)+Vector((p.x,y,pivot.z+dz1))*blend

def radial(z,theta):
 return Vector((math.sin(theta),-math.cos(theta),0)).normalized()
def amount(ci,z):
 lo,hi=BOUNDS[ci] if ci<4 else(1.395,1.59)
 return .006*max(0,min(1,(hi-z)/(hi-lo)))
def replace(o,verts,faces,description):
 inv=o.matrix_world.inverted();m=bpy.data.meshes.new(o.name+' coherent crescent construction');m.from_pydata([inv@v for v in verts],[],faces);m.update()
 for mat in o.data.materials:m.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),o.name
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(m);bm.free();o.data=m
 for p in m.polygons:p.use_smooth=True
 o['v38NeckEnvelope01']=description
 return {'name':o.name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'class':o.get('constructionClass'),'vertices':len(m.vertices),'nonManifoldEdges':0,'positiveVolumeM3':volume}
def skin(name,ci,lo,hi,theta,width,index):
 o=bpy.data.objects[name];outer=[];inner=[];nr=19;nc=19;side=1 if theta>=0 else-1
 for r in range(nr):
  t=r/(nr-1)
  for c in range(nc):
   u=c/(nc-1);th=theta+(u-.5)*width-.065*(t-.5)
   # Swept broad crescent ends; no horizontal shelf or uniform pointed scallop.
   slope=.015 if abs(theta)>.7 else .009
   z=hi*(1-t)+lo*t-slope*(u-.5)*side-.004*math.sin(math.pi*u)*t
   # Alternate lateral under/over stock lands within each rigid owner; moving stages use free-lap depth.
   seat=(.007 if ci==4 and int(name.split()[-2])==0 else 0);off=seat
   outer.append(sector(z,th,off,ci));inner.append(sector(z,th,off-.0035,ci))
 half=len(outer);faces=[]
 for r in range(nr-1):
  for c in range(nc-1):i=r*nc+c;faces.append((i,i+1,i+nc+1,i+nc))
 faces+=[tuple(i+half for i in reversed(f))for f in faces.copy()]
 boundary=list(range(nc))+[r*nc+nc-1 for r in range(1,nr)]+[(nr-1)*nc+c for c in range(nc-2,-1,-1)]+[r*nc for r in range(nr-2,0,-1)]
 for j,a in enumerate(boundary):b=boundary[(j+1)%len(boundary)];faces.append((a,b,b+half,a+half))
 rec=replace(o,outer+inner,faces,'New broad directional rigid crescent,3.5mm paired radial stock, own-stage receiving carrier; support/motion fit proposed not accepted.')
 rec.update({'zRange':[lo,hi],'thetaCenter':theta,'thetaWidth':width,'wallM':.0035,'diagonalSweepRad':-.13*side,'receivingDepthM':seat,'role':'Rigid guard, not cross-joint bridge'});return rec

def support(ownername,ci,side):
 o=bpy.data.objects[f'V38 curved-neck formed yoke {ownername} {side}'];source=bpy.data.objects[f'V23 cervical {ci+1} distal race {side}'if ci<4 else f'V31 passive cranial load bow {side}']
 face=source.data.polygons[60 if side<0 else 61]if ci<4 else source.data.polygons[518]
 raw=[source.matrix_world@source.data.vertices[i].co for i in face.vertices];center=sum(raw,Vector())/4
 # Genuine near-face embedded subsection on unchanged original bearing/bow.
 root=[center+(v-center)*.83-Vector((side*.0007,0,0))for v in raw]
 level=center.z if ci<4 else 1.497
 if ci<4:level=max(BOUNDS[ci][0]+.020,min(BOUNDS[ci][1]-.015,level))
 verts=[];faces=[];rings=41
 for j in range(rings):
  theta=side*(.08+(math.pi-.16)*j/(rings-1));z=level
  # Seat carrier across finite inner lands with broad stock, not a high fan to the opposite stage.
  d=-.0035+.0018
  verts.extend([sector(z-.004,theta,d-.004,ci),sector(z-.004,theta,d,ci),sector(z+.004,theta,d,ci),sector(z+.004,theta,d-.004,ci)])
 faces.append((3,2,1,0));faces.append(tuple((rings-1)*4+k for k in range(4)))
 branch=20;hole=None
 for j in range(rings-1):
  for k in range(4):
   f=(j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k)
   if j==branch and k==3:hole=f
   else:faces.append(f)
 # Replace one finite carrier inner wall face by a coherent connected bearing-root branch.
 cap=[verts[i]for i in hole];orders=[]
 for rev in(False,True):
  q=root[::-1]if rev else root
  for shift in range(4):
   v=q[shift:]+q[:shift];orders.append((sum((v[i]-cap[i]).length_squared for i in range(4)),v))
 root=min(orders,key=lambda x:x[0])[1];start=len(verts);verts.extend(root)
 for k in range(4):a=hole[k];b=hole[(k+1)%4];faces.append((a,b,start+(k+1)%4,start+k))
 faces.append(tuple(start+i for i in reversed(range(4))))
 endname=f'V33 tapered throat cheek plate {side} 1 0' if ci==4 else f'V23 cervical {ci+1} directional guard {1 if side<0 else 5}'
 guard=bpy.data.objects[endname];world=guard.matrix_world;target=sector(level,side*1.10,-.0035,ci);half=len(guard.data.vertices)//2
 candidates=[]
 for poly in guard.data.polygons:
  if len(poly.vertices)!=4 or not all(i>=half for i in poly.vertices):continue
  vs=[world@guard.data.vertices[i].co for i in poly.vertices];center2=sum(vs,Vector())/4;candidates.append(((center2-target).length,poly,vs))
 _,endface,end=min(candidates,key=lambda q:q[0]);normal=(end[1]-end[0]).cross(end[2]-end[0]).normalized();center2=sum(end,Vector())/4;end=[center2+(v-center2)*.82-normal*.0008 for v in end]
 jend=14;hole2=(jend*4+1,jend*4+2,(jend+1)*4+2,(jend+1)*4+1);faces.remove(hole2);cap2=[verts[i]for i in hole2];orders=[]
 for rev in(False,True):
  q=end[::-1]if rev else end
  for shift in range(4):
   v=q[shift:]+q[:shift];orders.append((sum((v[i]-cap2[i]).length_squared for i in range(4)),v))
 end=min(orders,key=lambda q:q[0])[1];start2=len(verts);verts.extend(end)
 for k in range(4):faces.append((hole2[k],hole2[(k+1)%4],start2+(k+1)%4,start2+k))
 faces.append(tuple(start2+i for i in reversed(range(4))))
 rec=replace(o,verts,faces,'Connected owner-local narrow perimeter carrier with direct finite branch from original unchanged bearing/bow face. Intended receiver connection; finite intersection/motion qualification pending.')
 rec.update({'sourceFrame':source.name,'selectedReceiver':endname,'selectedReceiverInnerFaceIndex':endface.index,'selectedReceiverActualEmbeddedCapNative':[list(v)for v in end],'sourceFaceIndex':face.index,'sourceFaceVertexIndices':list(face.vertices),'originalSourceFaceNative':[list(v)for v in raw],'actualEmbeddedRootNative':[list(v)for v in root],'receivingLevelNativeZ':level,'sourceRootZ':center.z,'rootLevelDistanceM':abs(center.z-level),'carrierSectionM':[.004,.008],'carrierThetaRange':[side*.08,side*(math.pi-.08)],'connectedConstruction':'One manifold branch joins existing finite carrier-wall loop, no Boolean islands or duplicated pasted seats. Receiver intersects local same-owner inner lands nominally; true support must be screened.'})
 return rec

def apply():
 rec=[]
 for ci,(lo,hi)in enumerate(BOUNDS):
  for g in range(1,11):
   ordered=sorted(ANGLES.values());theta=ANGLES[g];i=ordered.index(theta);prev=ordered[i-1] if i else ordered[-1]-2*math.pi;nxt=ordered[(i+1)%10] if i<9 else ordered[0]+2*math.pi
   left=(prev+theta)/2+.007;right=(theta+nxt)/2-.007;center=(left+right)/2;width=right-left
   rec.append(skin(f'V23 cervical {ci+1} directional guard {g}',ci,lo,hi,center,width,g))
 for side in(-1,0,1):
  for row in(0,1):
   for col in range(3):
    theta=[-.52,0,.52][col]if side==0 else side*[1.08,1.76,2.45][col]
    alltheta=sorted([-.52,0,.52]+[-1.08,-1.76,-2.45,1.08,1.76,2.45]);i=alltheta.index(theta);prev=alltheta[i-1]if i else alltheta[-1]-2*math.pi;nxt=alltheta[i+1]if i<8 else alltheta[0]+2*math.pi;left=(theta+prev)/2+.007;right=(theta+nxt)/2-.007;theta=(left+right)/2;width=right-left
    lo,hi=(1.509,1.586)if row==0 else(1.389,1.520)
    # Broad swept coverage is regional reconstruction, original arbitrary root rows are not protected.
    rec.append(skin(f'V33 tapered throat cheek plate {side} {row} {col}',4,lo,hi,theta,width,col+abs(side)+row))
 for ci,owner in enumerate(OWNERS):
  for side in(-1,1):rec.append(support(owner,ci,side))
 return {'changedMeshes':GUARDS+THROAT+YOKES,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':rec,'actualEnvelopeControlsNative':PROFILE,'construction':'58 independently rigid swept crescent skins across existing4 cervical owners/head;10 same-owner connected branched carrier reconstructions. Local side bearing windows replace broad full-height slit. No powered bronze or cross-joint collar.','protected':'Actual original races/shafts/loadlinks/cranial bows, all joint centres/rests/control sockets; headbill/jaw/crown/optic, breast33 exterior/liner/hinge/returns and all other regions/materials exact.','limits':['New plate roots and passive yokes intentionally reconstructed; existing arbitrary guard rows not shape authority.','Closed positive branched carrier topology and finite bearing-root subsection do not establish true receiving fit or continuous moving clearance.','3.5mm paired radial guard stock not constant normal thickness.','Final second bearing-sector/true-butt proposal; exact own selected receiver branch. Fit qualification follows, no third. No owner likeness or engineering approval.']}
