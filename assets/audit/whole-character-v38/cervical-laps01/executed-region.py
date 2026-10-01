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
  d=amount(ci,z)-.0035+.0018
  verts.extend([point(z-.004,theta,d-.004),point(z-.004,theta,d),point(z+.004,theta,d),point(z+.004,theta,d-.004)])
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
 rec=replace(o,verts,faces,'Connected owner-local narrow perimeter carrier with direct finite branch from original unchanged bearing/bow face. Intended receiver connection; finite intersection/motion qualification pending.')
 rec.update({'sourceFrame':source.name,'sourceFaceIndex':face.index,'sourceFaceVertexIndices':list(face.vertices),'originalSourceFaceNative':[list(v)for v in raw],'actualEmbeddedRootNative':[list(v)for v in root],'receivingLevelNativeZ':level,'sourceRootZ':center.z,'rootLevelDistanceM':abs(center.z-level),'carrierSectionM':[.004,.008],'carrierThetaRange':[side*.08,side*(math.pi-.08)],'connectedConstruction':'One manifold branch joins existing finite carrier-wall loop, no Boolean islands or duplicated pasted seats. Receiver intersects local same-owner inner lands nominally; true support must be screened.'})
 return rec


NEW_HEAD=Vector((0,-.392,1.520));WALL=.0035
PIVOTS=[];LANDS={};TRANSLATIONS=[];FRAME_RECORDS=[]
def base_section(z):
 f,r,w=profile(z);return f+.012,r-.005,w*.88

def radius(c,x,back=False):
 f,r,w=base_section(c.z);cy=(f+r)/2;ry=(r-f)/2
 # Defined on actual axial cross-sections; no radius clamp or angle-dependent deformation.
 q=1-(x/w)**2
 assert q>0,(list(c),x,w)
 return (cy-c.y if back else c.y-cy)+ry*math.sqrt(q)

def circular(c,theta,phi,offset,back=False):
 w=base_section(c.z)[2];x=w*(.80 if back else 1)*math.sin(theta);rr=radius(c,x,back)+offset
 return c+Vector((x,(1 if back else -1)*rr*math.cos(phi),rr*math.sin(phi)))

def sphere(theta,lat,rad):return NEW_HEAD+Vector((rad*math.cos(lat)*math.sin(theta),-rad*math.cos(lat)*math.cos(theta),rad*math.sin(lat)))

AB={1:(-1.44,-.825),2:(-.825,-.275),3:(-.275,.275),4:(.275,.825),5:(.825,1.44),6:(1.60,2.12),7:(2.12,2.80),8:(-2.80,-2.12),9:(-2.12,-1.60),10:(2.80,3.483185307)}
def patch(name,outer,inner,nr,nc,description):
 half=len(outer);faces=[]
 for i in range(nr-1):
  for j in range(nc-1):k=i*nc+j;faces.append((k,k+1,k+nc+1,k+nc))
 faces+=[tuple(k+half for k in reversed(f))for f in faces.copy()]
 bd=list(range(nc))+[i*nc+nc-1 for i in range(1,nr)]+[(nr-1)*nc+j for j in range(nc-2,-1,-1)]+[i*nc for i in range(nr-2,0,-1)]
 for i,a in enumerate(bd):b=bd[(i+1)%len(bd)];faces.append((a,b,b+half,a+half))
 return replace(bpy.data.objects[name],outer+inner,faces,description)

def cervical_skin(ci,g):
 lo,hi=AB[g];lo+=.010;hi-=.010;back=g>=6;outer=[];inner=[];nr=25;nc=19;c0=PIVOTS[ci];c1=PIVOTS[ci+1]
 for i in range(nr):
  t=i/(nr-1)
  for j in range(nc):
   th=lo+(hi-lo)*j/(nc-1);sl=.024*math.sin(th)
   if t<=.25:
    phi=-.12+(.25)*(t/.25)+sl
    p=circular(c0,th,phi,0,back);q=circular(c0,th,phi,-WALL,back)
   elif t>=.75:
    a=(t-.75)/.25
    if ci==3:
     lat=-.58+.66*a+sl;p=sphere(th,lat,.143);q=sphere(th,lat,.143-WALL)
    else:
     phi=-.10+.22*a+sl;p=circular(c1,th,phi,-.007,back);q=circular(c1,th,phi,-.007-WALL,back)
   else:
    u=(t-.25)/.5
    # Straight monotonic cross-section loft between explicit endpoint sections. No blended sector or clamps.
    a=circular(c0,th,.13+sl,0,back);ai=circular(c0,th,.13+sl,-WALL,back)
    if ci==3:b=sphere(th,-.58+sl,.143);bi=sphere(th,-.58+sl,.143-WALL)
    else:b=circular(c1,th,-.10+sl,-.007,back);bi=circular(c1,th,-.10+sl,-.007-WALL,back)
    assert b.z>a.z,('Nonmonotonic core',ci,g,th,a.z,b.z)
    p=a.lerp(b,u);q=ai.lerp(bi,u)
   outer.append(p);inner.append(q)
 rec=patch(f'V23 cervical {ci+1} directional guard {g}',outer,inner,nr,nc,'Direct stage-owned monotonic panel with own bearing-root circular sector and next-bearing recessed free sliding sector; irregular axial butt boundaries. Top stage spherical free lap at relocated skull joint. Proposal, not clearance acceptance.')
 rec.update({'ownPivot':list(c0),'nextPivot':list(c1),'angularBounds':list((lo,hi)),'layerOrder':'Child own-root stock outside parent next-joint free lap by7mm nominal outer difference;3.5mm walls','wallM':WALL});return rec

def head_skin(side,row,col):
 th=[-.52,0,.52][col]if side==0 else side*[1.08,1.76,2.45][col]
 centers=sorted([-.52,0,.52]+[s*a for s in(-1,1)for a in(1.08,1.76,2.45)])
 k=centers.index(th);lo=(centers[k-1]+th)/2 if k else-2.86;hi=(centers[k+1]+th)/2 if k<len(centers)-1 else 2.86;lo+=.008;hi-=.008
 lat0,lat1,rad=(-.60,.18,.151)if row==1 else(.10,.62,.158)
 out=[];inn=[];nr=25;nc=19
 for i in range(nr):
  t=i/(nr-1)
  for j in range(nc):
   a=lo+(hi-lo)*j/(nc-1);lat=lat0+(lat1-lat0)*t+.022*math.sin(a)
   out.append(sphere(a,lat,rad));inn.append(sphere(a,lat,rad-WALL))
 rec=patch(f'V33 tapered throat cheek plate {side} {row} {col}',out,inn,nr,nc,'Direct spherical compound-motion cheek shingle at raised skullbase pivot; finite angular butt seams, lowercourse outer layer151mm, uppercourse158mm. Intended separate rigid lap stock, not full sweep proof.')
 rec.update({'sphereCentreNative':list(NEW_HEAD),'radiusM':rad,'latitudeBounds':[lat0,lat1],'azimuthBounds':[lo,hi]});return rec

def tube(name,a,b,rad,segments=24):
 d=(b-a).normalized();u=d.cross(Vector((1,0,0))).normalized()
 if u.length<.5:u=d.cross(Vector((0,1,0))).normalized()
 v=d.cross(u);verts=[]
 for c in(a,b):
  for i in range(segments):verts.append(c+rad*(u*math.cos(i*math.tau/segments)+v*math.sin(i*math.tau/segments)))
 faces=[tuple(reversed(range(segments))),tuple(range(segments,2*segments))]
 for i in range(segments):j=(i+1)%segments;faces.append((i,j,j+segments,i+segments))
 rec=replace(bpy.data.objects[name],verts,faces,'Reconstructed finite rigid stock between declared actual attachment centres; seat/neighbor fit proposed.')
 rec.update({'endpointCentresNative':[list(a),list(b)],'sectionRadiusM':rad});return rec

def frame_rebuild(delta):
 # Existing compound-motion joint becomes ball/parted cup; fixed upper links reach cup, head bow roots reach rotating shaft seats.
 rec=[]
 name='V21 head captive shaft';o=bpy.data.objects[name];tmp=bmesh.new();bmesh.ops.create_uvsphere(tmp,u_segments=32,v_segments=20,radius=.032)
 for v in tmp.verts:v.co+=NEW_HEAD
 tmp.verts.ensure_lookup_table();tmp.verts.index_update();vv=[v.co.copy()for v in tmp.verts];ff=[tuple(v.index for v in f.verts)for f in tmp.faces];tmp.free();rec.append(replace(o,vv,ff,'Reconstructed head-owned spherical bearing ball32mm at new skullbase pivot; replaces obsolete transverse shaft volume.'))
 rec.append(tube('V23 cervical 4 captive pin',NEW_HEAD,NEW_HEAD+Vector((0,0,.056)),.010))
 for side in(-1,1):
  # Upstream socket halves leave a real upper stem window; no cross-owner bridge.
  out=[];inn=[];nr=17;nc=25;lo=(0 if side>0 else math.pi)+.008;hi=(math.pi if side>0 else math.tau)-.008
  for i in range(nr):
   polar=math.radians(50)+(math.radians(165)-math.radians(50))*i/(nr-1)
   for j in range(nc):
    az=lo+(hi-lo)*j/(nc-1);n=Vector((math.sin(polar)*math.cos(az),math.sin(polar)*math.sin(az),math.cos(polar)))
    out.append(NEW_HEAD+n*.039);inn.append(NEW_HEAD+n*.0332)
  rec.append(patch(f'V23 cervical 4 distal race {side}',out,inn,nr,nc,'Reconstructed cervical-upper-owned split spherical receiver cup:33.2mm inner/39mm outer,50degree stem aperture; original upstream bearing preserved, compound skull motion newly proposed.'))
  lower=PIVOTS[3]+Vector((side*.053,0,.007));upper=NEW_HEAD+Vector((side*.026,0,-.027));rec.append(tube(f'V23 cervical 4 load link {side}',lower,upper,.006))
  o=bpy.data.objects[f'V31 cranial load bow shaft seat {side}'];inv=o.matrix_world.inverted()
  for v in o.data.vertices:v.co=inv@(o.matrix_world@v.co+delta)
  rec.append({'name':o.name,'owner':o.parent.name,'role':'Existing head-owned shaft-seat stock translated to raised joint; actual route fit pending','deltaNative':list(delta)})
  o=bpy.data.objects[f'V31 passive cranial load bow {side}'];inv=o.matrix_world.inverted();changed=0
  for v in o.data.vertices:
   p=o.matrix_world@v.co
   if p.z<1.570:
    f=max(0,min(1,(1.570-p.z)/(1.570-1.3908046)));p.y+=delta.y*f;p.z+=delta.z*f;v.co=inv@p;changed+=1
  rec.append({'name':o.name,'owner':o.parent.name,'role':'Root branch raised into relocated own shaft seat; upper cranial identity retained','affectedVertices':changed,'rootDeltaNative':list(delta),'stockQualification':'Compressed monotonic root transition, finite/self proof pending'})
 return rec

def carrier(ci,side):
 owner=OWNERS[ci];o=bpy.data.objects[f'V38 curved-neck formed yoke {owner} {side}'];skin=bpy.data.objects[f'V23 cervical {ci+1} directional guard {1 if side<0 else 5}']if ci<4 else bpy.data.objects[f'V33 tapered throat cheek plate {side} 1 0']
 # Actual receiving quad from newly authored inner skin, not nominal profile proxy.
 nr=25;nc=19;n=nr*nc;r=12;c=9;ids=[n+r*nc+c,n+r*nc+c+1,n+(r+1)*nc+c+1,n+(r+1)*nc+c];land=[skin.matrix_world@skin.data.vertices[i].co for i in ids]
 source=bpy.data.objects[f'V23 cervical {ci+1} distal race {side}']if ci<4 else bpy.data.objects[f'V31 cranial load bow shaft seat {side}']
 target=sum(land,Vector())/4
 face=min((f for f in source.data.polygons if len(f.vertices)==4),key=lambda f:((sum((source.matrix_world@source.data.vertices[i].co for i in f.vertices),Vector())/4)-target).length)
 raw=[source.matrix_world@source.data.vertices[i].co for i in face.vertices];rootcenter=sum(raw,Vector())/4;root=[rootcenter+(p-rootcenter)*.82 for p in raw]
 normal=(land[1]-land[0]).cross(land[3]-land[0]).normalized();end=[p+normal*.0008 for p in land]
 orders=[]
 for reverse in(False,True):
  q=root[::-1]if reverse else root
  for shift in range(4):v=q[shift:]+q[:shift];orders.append((sum((v[k]-end[k]).length_squared for k in range(4)),v))
 root=min(orders,key=lambda x:x[0])[1];verts=root+end;faces=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4)for i in range(4)]
 rec=replace(o,verts,faces,'Compact owner-local direct finite root-to-actual inner guard land bracket; no fan ring or nominal carrier proxy. Single connected stock; support/clearance pending.')
 rec.update({'sourceFrame':source.name,'sourceFaceIndex':face.index,'sourceRootQuadNative':[list(v)for v in root],'selectedReceiver':skin.name,'selectedReceiverVertexIndices':ids,'receiverQuadNative':[list(v)for v in land],'rootToLandDistanceM':(target-rootcenter).length});return rec

def apply():
 global PIVOTS
 bpy.context.view_layer.update();h=bpy.data.objects['head'];old=h.matrix_world.translation.copy();delta=NEW_HEAD-old
 moved=['head']
 if bpy.data.objects.get('cervical-skull-cover'):moved.append('cervical-skull-cover')
 children={n:{c.name:c.matrix_world.copy()for c in bpy.data.objects[n].children}for n in moved}
 for name in moved:
  o=bpy.data.objects[name];mw=o.matrix_world.copy();mw.translation=NEW_HEAD;o.matrix_world=mw;bpy.context.view_layer.update()
  for child,m in children[name].items():bpy.data.objects[child].matrix_world=m
 bpy.context.view_layer.update();PIVOTS=[bpy.data.objects[n].matrix_world.translation.copy()for n in OWNERS]
 rec=frame_rebuild(delta)
 for ci in range(4):
  for g in range(1,11):rec.append(cervical_skin(ci,g))
 for side in(-1,0,1):
  for row in(0,1):
   for col in range(3):rec.append(head_skin(side,row,col))
 for ci in range(5):
  for side in(-1,1):rec.append(carrier(ci,side))
 changes=GUARDS+THROAT+YOKES+[x['name']for x in rec if x['name']not in GUARDS+THROAT+YOKES]
 changednodes=sorted(set(moved+[c for n in children for c in children[n]]))
 return {'changedMeshes':changes,'changedNodes':changednodes,'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':rec,'headPivotProposal':{'oldNative':list(old),'newNative':list(NEW_HEAD),'deltaNative':list(delta),'directChildWorldRestCompensation':{n:list(v)for n,v in [(c,m.translation)for group in children.values()for c,m in group.items()]},'jointMechanism':'Proposed ball/split spherical cup with rotating head stem; pitch+yaw route newly authored, not validated'},'construction':'Direct bearing-coordinate mid-X laps with monotonic core loft; relocated compound-motion skullbase spherical overlap; no pointwise blended/clamped sector deformation. All structural dimensions proposals.','protected':'Unrelated head identity/rest-world crown/bill/jaw/optic geometry, jaw-local socket, body33plate shape/liner/hinge/limbs/materials/era roles. Head and receiver centres intentionally relocated with explicit direct-child local compensation; old unchanged-node claim invalid.','limits':['One complete candidate; stock/root/receiver/motion fit unaccepted.','Source head pivot shown incompatible with short skin; raised/recentered pivot and spherical bearing are proposals requiring fresh contact/runtime evidence.','3.5mm nominal paired wall is not constant-normal-wall certification.','Mid fixture onlycertifies narrow ideal mating layer, not full skin, support or compound sweep.']}
