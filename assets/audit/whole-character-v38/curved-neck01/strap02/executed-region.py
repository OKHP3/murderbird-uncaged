"""Full curved neck envelope, independently rigid courses and owner-local formed support proposals."""
import bpy,bmesh,math
from mathutils import Vector
GUARDS=[f'V23 cervical {c} directional guard {g}'for c in range(1,5)for g in range(1,11)]
THROAT=[f'V33 tapered throat cheek plate {s} {r} {c}'for s in(-1,0,1)for r in(0,1)for c in range(3)]
OWNERS=['neck','cervical-mid-a','cervical-mid-b','cervical-upper','head']
ANGLES={1:-1.10,2:-.55,3:0,4:.55,5:1.10,6:1.76,7:2.46,8:-2.46,9:-1.76,10:math.pi}
PROFILES=[(1.20,-.208,.189,.178),(1.255,-.251,.156,.153),(1.31,-.30,.14,.149),(1.365,-.34,.135,.147),(1.425,-.365,.131,.131),(1.49,-.367,.124,.121),(1.565,-.375,.117,.108),(1.61,-.38,.121,.105)]
def profile(z):
 for a,b in zip(PROFILES,PROFILES[1:]):
  if z<=b[0]:
   t=max(0,min(1,(z-a[0])/(b[0]-a[0])));return [a[i]*(1-t)+b[i]*t for i in range(1,4)]
 return list(PROFILES[-1][1:])
def point(z,theta,offset=0):
 cy,rx,ry=profile(z);return Vector(((rx+offset)*math.sin(theta),cy-(ry+offset)*math.cos(theta),z))
def close(name,outer,inner,rows,cols,o=None,owner=None,mats=None,props=None):
 verts=outer+inner;half=len(outer);faces=[]
 for r in range(rows-1):
  for c in range(cols-1):k=r*cols+c;faces.append((k,k+1,k+cols+1,k+cols))
 faces += [tuple(half+i for i in reversed(f))for f in faces.copy()]
 border=list(range(cols))+[r*cols+cols-1 for r in range(1,rows)]+[(rows-1)*cols+c for c in range(cols-2,-1,-1)]+[r*cols for r in range(rows-2,0,-1)]
 for j,k in enumerate(border):n=border[(j+1)%len(border)];faces.append((k,n,half+n,half+k))
 if o is None:
  m=bpy.data.meshes.new(name+' formed finite stock');o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);o.parent=owner;o.matrix_parent_inverse=owner.matrix_world.inverted();o.matrix_world.identity()
 else:m=bpy.data.meshes.new(name+' authored curved course')
 inv=o.matrix_world.inverted();m.from_pydata([inv@v for v in verts],[],faces);m.update()
 for mat in mats or list(o.data.materials):m.materials.append(mat)
 o.data=m;o.modifiers.clear();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges)
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 vol=bm.calc_volume(signed=True);assert vol>0;bm.to_mesh(m);bm.free()
 for f in m.polygons:f.use_smooth=len(f.vertices)==4
 if props:
  for k,v in props.items():o[k]=v
 return o,vol

def skin(name,zlo,zhi,theta,width,course,wall=.0035):
 o=bpy.data.objects[name];outer=[];inner=[];rows=25;cols=19
 for r in range(rows):
  t=r/(rows-1)
  for c in range(cols):
   u=c/(cols-1);th=theta+(u-.5)*width*(.94+.06*t)+.065*math.sin(math.pi*t)*(1 if theta>=0 else-1)
   # Diagonal course boundary, gently squared pointed lap; no uniform scallop.
   edge=.026*(u-.5)*(1 if theta>=0 else-1);z=zhi*(1-t)+zlo*t+edge
   if r<7:z-=.006*math.sin(math.pi*u)*(1-r/7)
   p=point(z,th,.006*course);q=point(z,th,.006*course-wall);outer.append(p);inner.append(q)
 props={'constructionDescriptionHistory':str(o.get('constructionDescription','unrecorded')),'constructionDescription':'V38 full curved-neck independent rigid course,3.5mm paired radial stock; owner-local formed yoke receiving proposal. Actual support/clearance not established by parent.','v38CurvedNeck':'Authored backward-C silhouette with diagonal free seams; no joint bridging or organic tissue; root/stock contact requires finite diagnostic.'}
 o,vol=close(name,outer,inner,rows,cols,o=o,props=props)
 return {'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'class':'inherited-passive','positiveVolumeM3':vol,'pairedRadialWallM':wall,'rootZ':zlo,'topZ':zhi,'centerTheta':theta,'angularWidth':width}

def source_quad(o,side,level):
 w=[o.matrix_world@v.co for v in o.data.vertices];choices=[]
 for p in o.data.polygons:
  if len(p.vertices)!=4:continue
  vs=[w[i]for i in p.vertices];n=(vs[1]-vs[0]).cross(vs[2]-vs[0]).normalized();center=sum(vs,Vector())/4
  choices.append((side*center.x+abs(n.x)*.04-abs(center.z-level)*1.4,p,vs,n))
 _,p,vs,n=max(choices,key=lambda x:x[0]);
 if n.x*side<0:n=-n
 return p,vs,n

def apply():
 rec=[];added=[];seats=[];mats=list(bpy.data.objects[GUARDS[0]].data.materials)
 bases=[1.211,1.261,1.307,1.352]
 for course,lo in enumerate(bases,1):
  hi=([1.280,1.328,1.374,1.449][course-1])
  for g in range(1,11):
   width=.57 if g in[1,2,3,4,5]else .65 if g in[6,9]else .64 if g in[7,8]else .64
   rec.append(skin(f'V23 cervical {course} directional guard {g}',lo,hi,ANGLES[g],width,course-1))
 for side in(-1,0,1):
  for row in(0,1):
   for col in range(3):
    th=([-0.40,0,.40][col]if side==0 else side*[.82,1.46,2.33][col]);width=.37 if side==0 else [.46,.38,.66][col]
    lo=1.406 if row==0 else 1.485;hi=1.518 if row==0 else 1.586
    rec.append(skin(f'V33 tapered throat cheek plate {side} {row} {col}',lo,hi,th,width,4+row))
 # One narrow continuous perimeter receiving strap per cervical owner/side;
 # two per head side serve the two head levels. Roots use near-level frame
 # faces, not high optic-height faces or radial shelf fans.
 for ci,ownername in enumerate(OWNERS):
  owner=bpy.data.objects[ownername]
  levels=[(bases[ci]+.031,.006*ci-.0035)]if ci<4 else[(1.452,.024-.0035),(1.540,.030-.0035)]
  for li,(level,offset)in enumerate(levels):
   for side in(-1,1):
    source=bpy.data.objects[f'V23 cervical {ci+1} load link {side}'if ci<4 else f'V31 passive cranial load bow {side}'];face,quad,norm=source_quad(source,side,level);verts=list(quad);faces=[]
    # Finite original quad closes the actual root; four-corner loft reaches
    # the receiving path then continues around just this owner's half-neck.
    def section(theta):return [point(level-.0025,theta,offset-.003),point(level-.0025,theta,offset),point(level+.0025,theta,offset),point(level+.0025,theta,offset-.003)]
    start=section(side*.028)
    for t in(.33,.66,1):verts.extend([quad[k]*(1-t)+start[k]*t for k in range(4)])
    for j in range(1,37):verts.extend(section(side*(.028+(math.pi-.056)*j/36)))
    count=len(verts)//4;faces.append(tuple(range(3,-1,-1)))
    for j in range(count-1):
     for k in range(4):faces.append((j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k))
    faces.append(tuple((count-1)*4+k for k in range(4)))
    name=f'V38 curved-neck receiving strap {ownername} {side} {li}';mesh=bpy.data.meshes.new(name+' continuous near-frame stock');obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj);obj.parent=owner;obj.matrix_parent_inverse=owner.matrix_world.inverted();obj.matrix_world.identity();inv=obj.matrix_world.inverted();mesh.from_pydata([inv@v for v in verts],[],faces);mesh.update()
    for mat in mats:mesh.materials.append(mat)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges)
    if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
    vol=bm.calc_volume(signed=True);assert vol>0;bm.to_mesh(mesh);bm.free()
    for k,v in{'region':'neck','surfaceRole':'frame','constructionClass':'inherited-passive','exteriorEras':'maker,mechanic,builder','constructionOwner':ownername,'proposal':True,'constructionDescription':'Continuous narrow perimeter receiving strap, actual near-level original finite frame-face root; own owner only. Intended support unaccepted until actual finite stock contact/pose tests.'}.items():obj[k]=v
    added.append(name);seats.append({'name':name,'owner':ownername,'eras':'maker,mechanic,builder','class':'inherited-passive','sourceFrame':source.name,'sourceFaceIndex':face.index,'sourceVertexIndices':list(face.vertices),'actualSourceQuadWorld':[list(v)for v in quad],'sourceRootCentroidZ':sum(v.z for v in quad)/4,'intendedReceivingLevelZ':level,'rootLevelDistanceM':abs(sum(v.z for v in quad)/4-level),'positiveVolumeM3':vol,'sourceRootMeaning':'One original finite quad spans actual root cap; no duplicated Boolean pads. Actual correspondence and interference separately screened; no engineered bearing acceptance.','receivingArc':'3mm radial by5mm tall finite perimeter stock at owner-specific receiving level, direct loft to source frame quad. Source proximity/parenting not support proof.'})
 return {'changedMeshes':GUARDS+THROAT,'changedNodes':[],'addedMeshes':added,'removedMeshes':[],'watchMeshes':GUARDS+THROAT+added,'attachmentAndEraMap':rec+seats,'fullEnvelopeProposal':PROFILES,'construction':'Full backward-C front/rear silhouette divided into58independent rigid courses;12owner-local narrow receiving strap proposals. Purposeful narrow side hardware reveals; all source load frame and articulation exact.','protected':'Original loadlinks/races/shafts/bows/journals, all pivots/transforms/headidentity/bill/jaw/optic/crown/torso/wings/legs/feet/materialprofiles exact.','limits':['Finite source roots and planned receiving arcs do not establish supported construction; actual fit/sameowner/crossowner contact separately reported.','Paired radial3.5mm wall not constant-normal or fabricated engineered armor.','No continuous motion or owner likeness acceptance; stock remains proposal.']}
