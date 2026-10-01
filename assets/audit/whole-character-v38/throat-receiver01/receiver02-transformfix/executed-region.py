"""Nested headshaft-centred throat sectors with explicit half-head rigid receiver."""
import bpy,bmesh,math,json
from mathutils import Vector
LOWER=[f'V33 tapered throat cheek plate {s} 0 {c}'for s in(-1,0,1)for c in range(3)]
UPPER=[f'V33 tapered throat cheek plate {s} 1 {c}'for s in(-1,0,1)for c in range(3)]
GUARDS=[f'V23 cervical 4 directional guard {g}'for g in range(1,11)]
REMOVED=['V38 curved-neck formed yoke head -1','V38 curved-neck formed yoke head 1']
def closed(name,verts,faces,owner,mats,props):
 inv=owner.matrix_world.inverted();m=bpy.data.meshes.new(name+' nested finite rigid stock');m.from_pydata([inv@v for v in verts],[],faces);m.update();o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);o.parent=owner;o.matrix_parent_inverse.identity();o.matrix_basis.identity()
 for mat in mats:m.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges)
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 vol=bm.calc_volume(signed=True);assert vol>0;bm.to_mesh(m);bm.free()
 for k,v in props.items():o[k]=v
 bpy.context.view_layer.update() # Transform-read implementation repair only; geometry design unchanged.
 return o,vol

def grid(name,outer,inner,rows,cols,owner,mats,props):
 half=len(outer);faces=[]
 for r in range(rows-1):
  for c in range(cols-1):k=r*cols+c;faces.append((k,k+1,k+cols+1,k+cols))
 faces += [tuple(half+i for i in reversed(f))for f in faces.copy()]
 border=list(range(cols))+[r*cols+cols-1 for r in range(1,rows)]+[(rows-1)*cols+c for c in range(cols-2,-1,-1)]+[r*cols for r in range(rows-2,0,-1)]
 for j,k in enumerate(border):n=border[(j+1)%len(border)];faces.append((k,n,half+n,half+k))
 return closed(name,outer+inner,faces,owner,mats,props)

def apply():
 head=bpy.data.objects['head'];upper=bpy.data.objects['cervical-upper'];C=head.matrix_world.translation.copy();assert (C-Vector((0,-.34060001373291016,1.3888840675354004))).length<1e-8
 receiver=bpy.data.objects.new('cervical-skull-cover',None);bpy.context.scene.collection.objects.link(receiver);receiver.parent=upper;receiver.matrix_parent_inverse=head.matrix_parent_inverse.copy();receiver.matrix_basis=head.matrix_basis.copy();receiver['constructionClass']='inherited-passive';receiver['exteriorEras']='maker,mechanic,builder';receiver['constructionDescription']='Explicit rigid skull receiver shares original head pivot/rest; follows half head orientation delta in runtime. No translation or headidentity movement.'
 bpy.context.view_layer.update();assert (receiver.matrix_local.translation-head.matrix_local.translation).length==0
 body=bpy.data.objects['body'];layout=json.loads(body['cervicalLayoutV2']);layout['skullReceiver']='cervical-skull-cover';body['cervicalLayoutV2']=json.dumps(layout,separators=(',',':'));mats=list(bpy.data.objects[LOWER[0]].data.materials);rec=[];added=['cervical-skull-cover'];props={'region':'head-neck-interface','surfaceRole':'frame','constructionClass':'inherited-passive','exteriorEras':'maker,mechanic,builder','constructionOwner':'cervical-skull-cover','proposal':True,'constructionDescription':'Finite headshaft-centred rigid annular receiver support; source bearing clearances and paired skin seating remain qualified, not engineering acceptance.'}
 def radius(x,theta,layer):
  # Two concentric guide sectors (front/rear), with an exposed side mechanism
  # transition. Each sector's radius depends on shaft axisX, never its angle.
  base=(.180 if theta<1.57 else.159)+layer
  return math.sqrt(max(.01,base*base-.18*x*x))
 def p(x,theta,r):return C+Vector((x,-r*math.cos(theta),r*math.sin(theta)))
 # Exact full58 source exterior/rest geometry invariant, lower9 owners only.
 for name in LOWER:
  o=bpy.data.objects[name];world=o.matrix_world.copy();sourcehash=str(o.get('constructionDescription','unrecorded'));o.parent=receiver;o.matrix_parent_inverse=receiver.matrix_world.inverted();o.matrix_world=world;o['constructionOwner']=receiver.name;o['v38ThroatReceiver']='Rest geometry exact FIRST curvedneck; lower9 now independent half-head receiver, finite support/joint seams unaccepted.'
  rec.append({'name':name,'owner':receiver.name,'previousOwner':'head','eras':o.get('exteriorEras'),'class':'inherited-passive','allSourceMeshCoordinatesFacesMaterialsExact':True,'restWorldTransformPreserved':True,'maximumWorldDisplacementM':0,'receivingMeaning':'Full original skin retained, no exterior circular warp or free coverage trimming. Actual lowerlap movement/contact/yaw checked independently.'})
 # One full annular journal per side surrounds the original head captive shaft.
 for side in(-1,1):
  x0=side*.071;x1=side*.081;v=[]
  for x in[x0,x1]:
   for r in[.0095,.018]:
    for j in range(48):v.append(p(x,2*math.pi*j/48,r))
  f=[]
  for j in range(48):
   k=(j+1)%48
   for a,b in[(0,48),(48,144),(144,96),(96,0)]:f.append((a+j,a+k,b+k,b+j))
  name=f'V38 receiver shaft journal {side}';o,vol=closed(name,v,f,receiver,mats,props);added.append(name);rec.append({'name':name,'owner':receiver.name,'eras':'maker,mechanic,builder','sourceInterface':'V21 head captive shaft','axis':'nativeX','centre':list(C),'axialSpanM':[x0,x1],'innerRadiusM':.0095,'outerRadiusM':.018,'nominalShaftOuterRadiusM':.008,'radialRunningGapM':.0015,'positiveVolumeM3':vol,'supportMeaning':'Actual shaft-centred running journal with1.5mm nominal radial space; support/bearing reaction geometry proposal, actual source finite clearance screened separately.'})
 # Two recessed circular sliding guide sectors. Their radii fit UNDER the
 # preserved external skin; they are not replacement exterior bands.
 guides=[]
 for label,a,b,rad in [('front',.015,1.40,.125),('rear',1.85,3.14,.114)]:
  out=[];inn=[]
  for j in range(33):
   th=a+(b-a)*j/32
   for k in range(25):
    x=-.09+.18*k/24;r=math.sqrt(rad*rad-.18*x*x);out.append(p(x,th,r));inn.append(p(x,th,r-.0035))
  name='V38 receiver recessed guide '+label;o,vol=grid(name,out,inn,33,25,receiver,mats,props);added.append(name);guides.append(o);rec.append({'name':name,'owner':receiver.name,'eras':'maker,mechanic,builder','class':'inherited-passive','positiveVolumeM3':vol,'sectorRadians':[a,b],'shaftCentre':list(C),'nominalCentralRadiusM':rad,'receivingMeaning':'True Xshaft circular inner sliding guide underneath exact external skin; support to skin through finite unique backing lands and narrow links. Continuous head/upper moving sector fit unproven.'})
 def loft(name,quad,terminal):
  # Match cyclic terminal corner order to minimize a twisted four-corner loft.
  possibilities=[]
  for seq in[terminal,list(reversed(terminal))]:
   for shift in range(4):ordered=seq[shift:]+seq[:shift];possibilities.append((sum((quad[k]-ordered[k]).length_squared for k in range(4)),ordered))
  terminal=min(possibilities,key=lambda x:x[0])[1];v=[]
  for t in[0,.25,.5,.75,1]:v.extend([quad[k].lerp(terminal[k],t)for k in range(4)])
  f=[(3,2,1,0)]
  for j in range(4):
   for k in range(4):f.append((j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k))
  f.append((16,17,18,19));return closed(name,v,f,receiver,mats,props)
 # Exact finite receiving stock behind each preserved skin's inner root band.
 # Each land is a DISTINCT original leaf patch, never reused bow pads.
 lands=[];reserved=set()
 for name in LOWER:
  o=bpy.data.objects[name];world=[o.matrix_world@v.co for v in o.data.vertices];half=len(world)//2;outer=[];inner=[];sourceindices=[]
  for row in range(3,7):
   for col in range(3,16):
    i=row*19+col;v=world[i+half];normal=(v-world[i]).normalized();outer.append(v);inner.append(v+normal*.0035);sourceindices.append(i+half)
  landname='V38 receiver leaf backing '+name.removeprefix('V33 tapered throat cheek plate ');land,vol=grid(landname,outer,inner,4,13,receiver,mats,props);added.append(landname);land.data.calc_loop_triangles();target=[land.matrix_world@land.data.vertices[i].co for i in[52+19,52+20,52+33,52+32]];centre=sum(target,Vector())/4
  choices=[]
  for guide in guides:
   for face in guide.data.polygons:
    if face.index>=32*24:continue
    key=(guide.name,face.index)
    if key in reserved:continue
    q=[guide.matrix_world@guide.data.vertices[i].co for i in face.vertices];choices.append(((sum(q,Vector())/4-centre).length_squared,key,q))
  _,key,root=min(choices,key=lambda x:x[0]);reserved.add(key);linkname='V38 receiver leaf load link '+name.removeprefix('V33 tapered throat cheek plate ');link,linkvol=loft(linkname,root,target);added.append(linkname)
  rec.append({'name':landname,'owner':receiver.name,'eras':'maker,mechanic,builder','class':'inherited-passive','sourceLeaf':name,'sourceInnerIndices':sourceindices,'sourceRows':[3,6],'sourceColumns':[3,15],'actualSourceInnerRootCoordinates':[list(v)for v in outer],'positiveVolumeM3':vol,'supportMeaning':'Finite backing outer surface coincides with distinct original leafinner4x13root band; actual area/pose/stock overlap separately screened, not blanket fit.'})
  rec.append({'name':linkname,'owner':receiver.name,'eras':'maker,mechanic,builder','class':'inherited-passive','sourceGuideFace':list(key),'actualGuideRootQuad':[list(v)for v in root],'terminalBackingQuad':[list(v)for v in target],'positiveVolumeM3':linkvol,'supportMeaning':'One continuous finite loft from unique guide face to actual backinginner face. No Boolean copied pad union; links/stock intersections and finite support unaccepted.'});lands.append(land)
 # Two narrow front/rear members per side join journal to actual guide face;
 # actual finite endpoints on each new part retained in the receipt.
 for side in[-1,1]:
  journal=bpy.data.objects[f'V38 receiver shaft journal {side}']
  for label,theta in[('front',.60),('rear',2.60)]:
   face=min(journal.data.polygons,key=lambda f:((journal.matrix_world@f.center)-p(side*.076,theta,.018)).length_squared);root=[journal.matrix_world@journal.data.vertices[i].co for i in face.vertices];guide=bpy.data.objects['V38 receiver recessed guide '+label];faces=[f for f in guide.data.polygons if f.index>=32*24 and f.index<2*32*24];targetface=min(faces,key=lambda f:((guide.matrix_world@f.center)-p(side*.076,theta,.119 if label=='front'else.108)).length_squared);terminal=[guide.matrix_world@guide.data.vertices[i].co for i in targetface.vertices];name=f'V38 receiver narrow load bow {side} {label}';obj,vol=loft(name,root,terminal);added.append(name);rec.append({'name':name,'owner':receiver.name,'eras':'maker,mechanic,builder','positiveVolumeM3':vol,'sourceJournalFace':face.index,'sourceGuideFace':targetface.index,'actualRootQuad':[list(v)for v in root],'actualTerminalQuad':[list(v)for v in terminal],'class':'inherited-passive','supportMeaning':'Narrow continuous journal-guide member with actual finite endpoint faces. Load/union quality and other apparatus clearance not established.'})
 for name in REMOVED:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 return {'changedMeshes':LOWER,'geometryChangedMeshes':[],'changedNodes':['body'],'addedMeshes':[n for n in added if bpy.data.objects[n].type=='MESH'],'addedNodes':['cervical-skull-cover'],'removedMeshes':REMOVED,'watchMeshes':LOWER+UPPER+GUARDS+[n for n in added if bpy.data.objects[n].type=='MESH'],'attachmentAndEraMap':rec,'reparentedMeshes':{n:{'from':'head','to':receiver.name,'restWorldTransformPreserved':True}for n in LOWER},'skullReceiver':{'name':receiver.name,'parent':upper.name,'localPosition':list(receiver.matrix_local.translation),'worldCentre':list(C),'headLocalPositionExact':True,'orientationRule':'Rigid half head delta relative rest; no position interpolation.','capturedContactReceiverLocalXDelta':-.5090505059024657*.5,'restMatrixLocal':[list(r)for r in receiver.matrix_local]},'construction':'FIRST full58 exterior geometry exact atrest; receiver owns lower9only. Recessed Xshaft circular guide sectors with distinct actual original leafinner backing lands and continuous finite load links; replace two failed headfans with2journals/2guides/9backings/9links/4narrowloadbows. Other eight inherited bad neckfans remain explicitly unresolved.','protected':'Original head/cervical pivots/rest/transforms, load frame/shaft/bow/seats, crown/jaw/optic/bill identity, all40cervicalskins/upper9throatskins/torso/wings/legs/feet/materialprofiles exact. Runtimemetadataonly body.cervicalLayoutV2.skullReceiver added, no app edits.','limits':['Not full support or movement clearance acceptance; paired source stock and blend seams remain finite-screen evidence.','Other inherited fans/skin/body/neck crossings retained and reported independently, no blanket fit claim.','Side transition front/rear sectors is not a continuous annular ball joint; attention yaw samples needed.','Nominal finite bearings/loadmember/receiving correspondence not engineered load or full area seating.']}
