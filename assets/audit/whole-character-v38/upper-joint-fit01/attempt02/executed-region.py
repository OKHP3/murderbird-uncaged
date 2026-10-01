"""Bounded first upper-joint-fit01: rigid short lower lames and finite race-root routes."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2]
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def components(m):
 links=[set()for _ in m.vertices]
 for e in m.edges:a,b=e.vertices;links[a].add(b);links[b].add(a)
 u=set(range(len(links)));s=[]
 while u:
  q=[u.pop()];n=0
  while q:
   a=q.pop();n+=1
   for b in links[a]&u:u.remove(b);q.append(b)
  s.append(n)
 return sorted(s,reverse=True)
def stock(o):
 bm=bmesh.new();bm.from_mesh(o.data);r={'components':components(o.data),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True)};bm.free();return r
def annotate(o,description):
 o['upperJointFitHistory']=json.dumps({k:json.loads(json.dumps(v,default=lambda x:list(x)))for k,v in o.items()if k in ['constructionDescription','authoringRole','geometryStatus'] or k.endswith('Revision')},separators=(',',':'));o['constructionDescription']=description;o['geometryStatus']='upper-joint-fit01 proposed passive rigid assembly; finite support/motion and owner acceptance unresolved';o['upperJointFitRevision']='upper-joint-fit01'
def install(o,v,f):
 old=o.data;m=bpy.data.meshes.new(o.name+' neck bearing stock');m.from_pydata([o.matrix_world.inverted()@p for p in v],[],f);m.update()
 for a in old.materials:m.materials.append(a)
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();o.data=m
 for p in m.polygons:p.use_smooth=True

def intersection_volume(a,b):
 # Temporary evaluated Boolean proves finite shared stock volume, not weld/fastener validity.
 m=a.data.copy();temp=bpy.data.objects.new('temporary seat-volume diagnosis',m);bpy.context.scene.collection.objects.link(temp);temp.matrix_world=a.matrix_world.copy();bpy.context.view_layer.update();mod=temp.modifiers.new('finite seat intersection','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=b
 dg=bpy.context.evaluated_depsgraph_get();ev=temp.evaluated_get(dg);q=ev.to_mesh();bm=bmesh.new();bm.from_mesh(q);volume=abs(bm.calc_volume(signed=True));count=len(q.vertices);bm.free();ev.to_mesh_clear();bpy.data.objects.remove(temp,do_unlink=True);bpy.data.meshes.remove(m);return {'intersectionVolumeM3':volume,'intersectionVertices':count,'qualification':'Actual finite common stock volume at intended rigid seat, not continuous welded route/fastener/load proof.'}
def apply():
 bpy.context.view_layer.update();changed=[];records=[];routes=[];axis=bpy.data.objects['head'].matrix_world.translation.copy()
 for side in(-1,0,1):
  for col in range(3):
   name=f'V33 tapered throat cheek plate {side} 0 {col}';o=bpy.data.objects[name];local=[v.co.copy()for v in o.data.vertices];old=[o.matrix_world@p for p in local];v=old[:950];faces=[tuple(p.vertices)for p in o.data.polygons if max(p.vertices)<950];edgeO=[24*19+c for c in range(19)];edgeI=[475+i for i in edgeO];cap=set(edgeO+edgeI);faces=[f for f in faces if not set(f)<=cap]
   # All upper receiving rows0–15 byte-exact; only the last9 free rows
   # coordinate exterior layer order. Head overlap remains OUTSIDE receiver.
   for i in range(950):
    row=(i%475)//19
    if row<16:continue
    p=old[i];d=p-axis;w=ease((row-16)/8);targetR=(.178 if side==0 else .175) if i<475 else((.178 if side==0 else .175)-.0035);q=axis+d.normalized()*targetR
    if side and col in(0,1):
     centerPoint=old[(i//475)*475+row*19+9]-axis;centerPhi=math.atan2(centerPoint.x,-centerPoint.y);phi=math.atan2(d.x,-d.y);phi=centerPhi+(phi-centerPhi)*(1.22 if col==0 else 1.14);q.x=targetR*math.cos(math.atan2(d.z,math.hypot(d.x,d.y)))*math.sin(phi);q.y=axis.y-targetR*math.cos(math.atan2(d.z,math.hypot(d.x,d.y)))*math.cos(phi);q.x+=axis.x
    v[i]=p.lerp(q,w)
   loopsO=[edgeO];loopsI=[edgeI];levels=10
   for k in range(1,levels+1):
    t=k/levels;lo=[];li=[]
    for c,i in enumerate(edgeO):
     d=v[i]-axis;phi=math.atan2(d.x,-d.y);lat=math.atan2(d.z,math.hypot(d.x,d.y));front=max(0,math.cos(phi))
     # Front covers actual counter-pitch gap; lateral/rear windows deliberately
     # exclude deep skirt so upper neck support can leave the bearing.
     endlat=-.30 if side==0 else(-.16 if col==0 else -.035 if col==1 else .095)
     if side and col in(0,1):
      dd=v[edgeO[9]]-axis;centerPhi=math.atan2(dd.x,-dd.y);phi=centerPhi+(phi-centerPhi)*(1.07 if col==0 else 1.04)
     newlat=lat*(1-t)+endlat*t;radial=Vector((math.sin(phi)*math.cos(newlat),-math.cos(phi)*math.cos(newlat),math.sin(newlat)))
     radius=.178 if side==0 else .175;lo.append(len(v));v.append(axis+radial*radius);li.append(len(v));v.append(axis+radial*(radius-.0025))
    loopsO.append(lo);loopsI.append(li)
   for k in range(levels):
    a,b=loopsO[k],loopsO[k+1];c,d=loopsI[k],loopsI[k+1]
    for j in range(18):faces.append((a[j],a[j+1],b[j+1],b[j]));faces.append((c[j],d[j],d[j+1],c[j+1]))
    faces.append((a[0],b[0],d[0],c[0]));faces.append((a[-1],c[-1],d[-1],b[-1]))
   a,b=loopsO[-1],loopsI[-1]
   for j in range(18):faces.append((a[j],a[j+1],b[j+1],b[j]))
   install(o,v,faces)
   for i in list(range(16*19))+list(range(475,475+16*19)):o.data.vertices[i].co=local[i]
   o.data.update();annotate(o,'Upper-joint-fit01: short head-owned OUTSIDE overlapfront178/175.5mm and side175/172.5mm short overlap, front−.30/side−.16 latitude with narrow oblique side sweep, shallow lateral/rear windows. Original upper receiving rows0–15 exact, lower free rows coordinate layer transition. Shared-edge finite2.5mm stock; no hidden separate layer, owner or joint movement. Actual clearance remains qualified.')
   changed.append(name);records.append({'name':name,'owner':'head','upper16ReceivingRowsByteExact':True,'originalSharedRootIndices':edgeO,'underlapOuterRadiusM':.178 if side==0 else .175,'underlapInnerRadiusM':.1755 if side==0 else .1725,'latitudeEnd':endlat,'lateralWindowMeaning':'Head sidecol1/2 skirt stays near original upper seam; does not descend through lateral neck-bearing route. Original exterior leaf still present.','newUnderlapVertices':len(v)-950,'stock':stock(o)})
 for g in range(1,6):
  o=bpy.data.objects[f'V23 cervical 4 directional guard {g}'];local=[v.co.copy()for v in o.data.vertices];world=[o.matrix_world@p for p in local];o.data=o.data.copy();inv=o.matrix_world.inverted();delta=[]
  for i,p in enumerate(world):
   row=(i%475)//19
   if row>=16:continue
   w=1-ease(max(0,(row-8)/8));d=p-axis;outerR=.163 if g in(1,5)else .168;targetR=outerR if i<475 else outerR-.0035;q=p.lerp(axis+d.normalized()*targetR,w);o.data.vertices[i].co=inv@q;delta.append((q-p).length)
  o.data.update();assert all(o.data.vertices[i].co==local[i]for i in range(950)if(i%475)//19>=16);annotate(o,'Upper-joint-fit01 cervical-upper receiving segment: both outer and inner upper travel rows formed about true head axis,front168/164.5mm and side163/159.5mm sectors inside178/175.5mm and175/172.5mm head overlap; lower9 rows exact. Deliberate exterior layer order and local3.5mm radial wall, no blind subtraction or added annulus; same owner, actual supports reconstructed separately.')
  changed.append(o.name);records.append({'name':o.name,'owner':'cervical-upper','receivingOuterRadiusM':outerR,'receivingInnerRadiusM':outerR-.0035,'nominalRadialSeparationM':.0075 if g in(2,3,4)else .0095,'lowerRows16Through24ByteExact':True,'maximumReceivingDeltaM':max(delta),'stock':stock(o)})
 for owner in('cervical-upper','head'):
  for side in(-1,1):
   o=bpy.data.objects[f'V38 curved-neck formed yoke {owner} {side}'];frame=bpy.data.objects[f'V23 cervical 4 distal race {side}'if owner=='cervical-upper'else f'V31 passive cranial load bow {side}'];guard=bpy.data.objects[f'V23 cervical 4 directional guard {1 if side<0 else 5}'if owner=='cervical-upper'else f'V33 tapered throat cheek plate {side} 0 0']
   row=15 if owner=='cervical-upper'else 8;ids=[475+row*19+8,475+row*19+9,475+(row+1)*19+9,475+(row+1)*19+8];endraw=[guard.matrix_world@guard.data.vertices[i].co for i in ids];ec=sum(endraw,Vector())/4;points=[frame.matrix_world@v.co for v in frame.data.vertices];faces=[p for p in frame.data.polygons if len(p.vertices)==4]
   if owner=='cervical-upper':
    capfaces=[p for p in faces if max(points[i].x for i in p.vertices)-min(points[i].x for i in p.vertices)<1e-6]
    outerX=max(side*sum(points[i].x for i in p.vertices)/4 for p in capfaces);capfaces=[p for p in capfaces if abs(side*sum(points[i].x for i in p.vertices)/4-outerX)<1e-6];face=min(capfaces,key=lambda p:sum(points[i].y for i in p.vertices)/4)
   else:face=min(faces,key=lambda p:(sum((points[i]for i in p.vertices),Vector())/4-ec).length)
   raw=[points[i]for i in face.vertices];rc=sum(raw,Vector())/4;normal=(raw[1]-raw[0]).cross(raw[3]-raw[0]).normalized()
   # Source face normal signed toward end; embed700µm of finite face land.
   if normal.dot(ec-rc)<0:normal=-normal
   root=[rc+(p-rc)*.8-normal*.0007 for p in raw];end=[p+(p-axis).normalized()*.001 for p in endraw]
   if owner=='cervical-upper':
    # Actual finite OUTER portion of the existing ring face, not an invented
    # enlarged bearing or duplicated seat stock. Preserve face/axis itself.
    centerYZ=Vector((rc.x,axis.y,axis.z));outerR=max(math.hypot(p.y-axis.y,p.z-axis.z)for p in raw)
    root=[]
    for p in raw:
     d=Vector((0,p.y-axis.y,p.z-axis.z));r=outerR*(.80 if d.length<outerR*.8 else .96);q=centerYZ+d.normalized()*r;q.x-=side*.0007;root.append(q)
   mc=Vector((side*.100,axis.y-.026,axis.z+.002))if owner=='cervical-upper'else Vector((side*.090,axis.y-.030,max(rc.z,ec.z)-.012))
   a=Vector((0,0,.0025));b=Vector((0,.003,0));mid=[mc-a-b,mc-a+b,mc+a+b,mc+a-b]
   choices=[mid[k:]+mid[:k]for k in range(4)]+[list(reversed(mid[k:]+mid[:k]))for k in range(4)];mid=min(choices,key=lambda a:sum((root[i]-a[i]).length_squared for i in range(4)))
   choices=[end[k:]+end[:k]for k in range(4)]+[list(reversed(end[k:]+end[:k]))for k in range(4)];end=min(choices,key=lambda a:sum((mid[i]-a[i]).length_squared for i in range(4)))
   if owner=='head':
    # Remove the backward dogleg entirely. Both genuine finite cap polygons
    # are ordered CCW around one common route axis; never reverse one cap
    # independently to minimize distances (the first recipe's twist).
    direction=(sum(end,Vector())/4-sum(root,Vector())/4).normalized();u=(root[1]-root[0]);u=(u-direction*u.dot(direction)).normalized();w=direction.cross(u)
    def order(loop):
     c=sum(loop,Vector())/4;return sorted(loop,key=lambda p:math.atan2((p-c).dot(w),(p-c).dot(u)))
    root=order(root);end=order(end);end=min([end[k:]+end[:k]for k in range(4)],key=lambda a:sum((root[i]-a[i]).length_squared for i in range(4)));mid=[];v=root+end;f=[(3,2,1,0),(4,5,6,7)]+[(j,(j+1)%4,4+(j+1)%4,4+j)for j in range(4)]
   else:
    v=root+mid+end;f=[(3,2,1,0),(8,9,10,11)]
    for k in(0,4):
     for j in range(4):f.append((k+j,k+(j+1)%4,k+4+(j+1)%4,k+4+j))
   install(o,v,f);annotate(o,'Upper-joint-fit01 compact same-owner supported route replaces broad fan: original finite frame face to protected/formed actual inner receiving quad; cervical-upper route leaves through lateral skirt window, head route rises inside its own leaf. No radial support through front rotating skirt, no moved frame or cross-owner bridge. Seat volume and stock are targeted evidence, not engineering acceptance.')
   changed.append(o.name);routes.append({'name':o.name,'owner':owner,'frame':frame.name,'endGuard':guard.name,'sourceFaceIndex':face.index,'sourceFaceIndices':list(face.vertices),'actualRootWorld':[list(p)for p in root],'actualMidWorld':[list(p)for p in mid],'actualEndWorld':[list(p)for p in end],'actualEndIndices':ids,'sameOwner':frame.parent.name==guard.parent.name==owner,'rootSeat':intersection_volume(o,frame),'endSeat':intersection_volume(o,guard),'stock':stock(o),'lateralWindowRoute':owner=='cervical-upper','rootRelocation':'Original own distal annular race outer-front cap subsection replaces former loadlink terminal land'if owner=='cervical-upper'else 'Same first actual cranialbow and guard cap coordinates; ordered straight two-cap stock replaces twisted backward dogleg'})
 return {'changedMeshes':changed,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'upperInterface':records,'supportRoutes':routes,'actualHeadAxis':list(axis),'layerOrder':'HEAD overlap OUTSIDE cervical-upper receiver; front178/175.5mm vs168/164.5mm; side175/172.5mm vs163/159.5mm nominal radii. 7.5mm radial separation is authored, not physical finite clearance.','construction':'Coordinated short directional overlap/receiver18mesh assembly; lateral windows and four compact original-face supported stock routes replace failed broad fans.','protected':'All joint centres/rest/owners/frames/bearings/body33plates/liner/returns/limbs/materials/era profiles exact; all other neckcourses unchanged. Head crown/bill/jaw/optics remain exact.','limits':['Originalupperroot16rows exact, but lower head free exterior and cervical4 receiving exterior change explicitly; no whole neck silhouette exact claim.','Final bounded side sweep/retracted radii and genuine ring-face roots are authored controls, not reference metrology.','Finite common stock volume and connected topology do not prove weld/fastener/bearing load or swept fit.','Inherited lowerbody, othercervical fan/guard crossings remain disclosed; no blanket physical or owner acceptance.']}
