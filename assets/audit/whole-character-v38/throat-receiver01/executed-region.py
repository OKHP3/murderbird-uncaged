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
 # Lower nine rigid leaves move as one independently supported receiver owner.
 for name in LOWER+UPPER+GUARDS:
  o=bpy.data.objects[name];oldworld=o.matrix_world.copy();inv=oldworld.inverted();source=[oldworld@v.co for v in o.data.vertices];half=len(source)//2;stride=19;rows=half//stride;assert rows==25
  if name in LOWER:
   world=oldworld.copy();o.parent=receiver;o.matrix_parent_inverse=receiver.matrix_world.inverted();o.matrix_world=world
  o.data=o.data.copy();mx=0
  for i in range(half):
   row=i//stride;col=i%stride;v=source[i];theta=math.atan2(v.z-C.z,-(v.y-C.y));theta=theta if theta>=0 else theta+2*math.pi
   if name in LOWER:
    th=max(.025,min(3.10,theta));r=radius(v.x,th,0);q=p(v.x,th,r);targetinner=p(v.x,th,r-.0035)
   elif name in UPPER:
    # Only free lower lap changes; upper receiving attachment stays exact.
    t=max(0,min(1,(row-15)/9));th=theta
    if theta<1.57:th=max(.37,theta-.15*t)
    elif theta<math.pi:th=min(2.98,theta+.13*t)
    r=radius(v.x,th,.010);target=p(v.x,th,r);q=v.lerp(target,t);targetinner=source[i+half]+(q-v)
   else:
    # Free upper guard lips concentric with headXshaft; original lower roots
    # and their remaining source fan/frame relation retained unchanged.
    t=max(0,min(1,(12-row)/12));r=radius(v.x,theta,-.010);target=p(v.x,theta,r);q=v.lerp(target,t);targetinner=source[i+half]+(q-v)
   mx=max(mx,(q-v).length);o.data.vertices[i].co=inv@q;o.data.vertices[i+half].co=inv@targetinner
  o.data.update();o['constructionDescriptionHistory']=str(o.get('constructionDescription','unrecorded'));o['constructionDescription']='V38 independently rigid nested headshaft sector lap; explicit receiving owner/stock, support and finite motion fit unaccepted.';o['v38ThroatReceiver']='Receiver lower9 follows halfheaddelta; upperhead9 and cervicalupper10 remain original owners. No organic deformation or jointbridge.'
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));vol=bm.calc_volume(signed=True);assert all(e.is_manifold for e in bm.edges)
  if vol<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));vol=-vol
  bm.to_mesh(o.data);bm.free();rec.append({'name':name,'owner':o.parent.name,'previousOwner':'head'if name in LOWER else o.parent.name,'eras':o.get('exteriorEras'),'class':'inherited-passive','positiveVolumeM3':vol,'maximumWorldDisplacementM':mx,'receivingMeaning':'HeadXshaft-centred front/rear circles with10mm layerspacing; side transition deliberately open/qualified. Exact circles apply to receiver all and upper/lower free lap only; unchanged root blends still require actual posed test.'})
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
  for label,theta in [('front',.60),('rear',2.60)]:
   # Narrow integral load member's annular root lands on new journal outer
   # sector; receiver carrier lands receive its external end.
   out=[];inn=[]
   for j in range(17):
    t=j/16;r=.018*(1-t)+(radius(side*.076,theta,0)-.0035)*t
    for k in range(3):
     th=theta+(k-1)*.035;out.append(p(side*.081,th,r));inn.append(p(side*.071,th,r))
   name=f'V38 receiver load bow {side} {label}';o,vol=grid(name,out,inn,17,3,receiver,mats,props);added.append(name);rec.append({'name':name,'owner':receiver.name,'eras':'maker,mechanic,builder','positiveVolumeM3':vol,'root':'New receiver journal finite outer arc','terminal':'New receiver carrier finite inner arc','class':'inherited-passive','supportMeaning':'One narrow continuous radial loadmember per front/rear side, no broad radial fan or duplicate seat Boolean.'})
 for label,a,b in [('front',.015,1.40),('rear',1.85,3.14)]:
  out=[];inn=[]
  for j in range(33):
   th=a+(b-a)*j/32
   for k in range(33):
    x=-.148+.296*k/32;r=radius(x,th,0)-.0035;out.append(p(x,th,r));inn.append(p(x,th,r-.0035))
  name='V38 receiver recessed carrier '+label;o,vol=grid(name,out,inn,33,33,receiver,mats,props);added.append(name);rec.append({'name':name,'owner':receiver.name,'eras':'maker,mechanic,builder','positiveVolumeM3':vol,'class':'inherited-passive','sectorRadians':[a,b],'pairedRadialWallM':.0035,'supportMeaning':'Finite recessed matching-circle carrier directly behind receiver leaves. Outer radius coincides with leafinner only where covered; unsupported seam/side intervals not claimed fitted.'})
 for name in REMOVED:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 return {'changedMeshes':LOWER+UPPER+GUARDS,'changedNodes':['body'],'addedMeshes':[n for n in added if bpy.data.objects[n].type=='MESH'],'addedNodes':['cervical-skull-cover'],'removedMeshes':REMOVED,'watchMeshes':LOWER+UPPER+GUARDS+[n for n in added if bpy.data.objects[n].type=='MESH'],'attachmentAndEraMap':rec,'reparentedMeshes':{n:{'from':'head','to':receiver.name,'restWorldTransformPreserved':True}for n in LOWER},'skullReceiver':{'name':receiver.name,'parent':upper.name,'localPosition':list(receiver.matrix_local.translation),'worldCentre':list(C),'headLocalPositionExact':True,'orientationRule':'Rigid half head delta relative rest; no position interpolation.','capturedContactReceiverLocalXDelta':-.5090505059024657*.5,'restMatrixLocal':[list(r)for r in receiver.matrix_local]},'construction':'First full curvedneck coverage retained except28head/upperneckinterface skins; nested front/rear Xshaft concentric circles, receiver owns lower9only. Replace two failed headfans with2journals/4narrow loadbows/2recessed carriers. Other eight inherited bad neckfans remain explicitly unresolved.','protected':'Original head/cervical pivots/rest/transforms, load frame/shaft/bow/seats, crown/jaw/optic/bill identity, other30cervicalskins/torso/wings/legs/feet/materialprofiles exact. Runtimemetadataonly body.cervicalLayoutV2.skullReceiver added, no app edits.','limits':['Not full support or movement clearance acceptance; paired source stock and blend seams remain finite-screen evidence.','Other inherited fans/skin/body/neck crossings retained and reported independently, no blanket fit claim.','Side transition front/rear sectors is not a continuous annular ball joint; attention yaw samples needed.','Nominal finite bearings/loadmember/receiving correspondence not engineered load or full area seating.']}
