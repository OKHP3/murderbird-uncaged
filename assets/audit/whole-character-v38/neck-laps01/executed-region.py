"""Broad directional neck lames with short spherical sliding laps on actual head pivot."""
import bpy,bmesh,math
from mathutils import Vector
GUARDS=[f'V23 cervical 4 directional guard {g}'for g in range(1,11)]
THROAT=[f'V33 tapered throat cheek plate {s} {r} {c}'for s in[-1,0,1]for r in[0,1]for c in range(3)]
REMOVED=[f'V38 curved-neck formed yoke {owner} {s}'for owner in['head','cervical-upper']for s in[-1,1]]
ANGLES={1:-1.10,2:-.55,3:0,4:.55,5:1.10,6:1.76,7:2.46,8:-2.46,9:-1.76,10:math.pi}
PROFILE=[(1.20,-.208,.189,.178),(1.255,-.251,.156,.153),(1.31,-.30,.14,.149),(1.365,-.34,.135,.147),(1.425,-.365,.131,.131),(1.49,-.367,.137,.127),(1.565,-.369,.14,.116),(1.61,-.38,.14,.105)]
def profile(z):
 for a,b in zip(PROFILE,PROFILE[1:]):
  if z<=b[0]:t=max(0,min(1,(z-a[0])/(b[0]-a[0])));return [a[i]*(1-t)+b[i]*t for i in range(1,4)]
 return list(PROFILE[-1][1:])
def point(z,phi,offset):
 cy,rx,ry=profile(z);return Vector(((rx+offset)*math.sin(phi),cy-(ry+offset)*math.cos(phi),z))
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def closed(name,verts,faces,owner,mats,props):
 inv=owner.matrix_world.inverted();m=bpy.data.meshes.new(name+' shaped rigid finite stock');m.from_pydata([inv@p for p in verts],[],faces);m.update();o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);o.parent=owner;o.matrix_parent_inverse.identity();o.matrix_basis.identity()
 for mat in mats:m.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges)
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 vol=bm.calc_volume(signed=True);assert vol>0;bm.to_mesh(m);bm.free()
 for k,v in props.items():o[k]=v
 bpy.context.view_layer.update();return o,vol

def apply():
 C=bpy.data.objects['head'].matrix_world.translation.copy();assert (C-Vector((0,-.34060001373291016,1.3888840675354004))).length<1e-8
 rec=[];added=[];headR=.164;neckR=.150;mats=list(bpy.data.objects[THROAT[0]].data.materials);props={'region':'head-neck-interface','surfaceRole':'frame','constructionClass':'inherited-passive','exteriorEras':'maker,mechanic,builder','proposal':True,'constructionDescription':'Continuous narrow formed passive frame-to-inner receiving member; actual source finite endpoint faces recorded, fit/load acceptance unresolved.'}
 for name in THROAT+GUARDS:
  o=bpy.data.objects[name];world=o.matrix_world.copy();inv=world.inverted();v=[world@p.co for p in o.data.vertices];half=len(v)//2;assert half==475;out=[];inn=[];maximum=0;protected=[]
  if name in THROAT:
   side,row,col=map(int,name.split()[-3:]);oldphi=([-0.40,0,.40][col]if side==0 else side*[.82,1.46,2.33][col]);interval=[(-.585,-.215),(-.185,.185),(.215,.585)][col]if side==0 else[(.60,1.25),(1.27,1.95),(2.09,2.96)][col];a,b=interval
   if side<0:a,b=-b,-a
   lo=1.406 if row==0 else 1.488;hi=1.509 if row==0 else 1.592;offset=.024+.006*row
  else:g=int(name.split()[-1]);a=ANGLES[g]-(.27 if g in[1,2,3,4,5]else.27 if g in[6,9]else.285 if g in[7,8]else.32);b=2*ANGLES[g]-a
  for rr in range(25):
   t=rr/24
   for cc in range(19):
    u=cc/18;i=rr*19+cc;p=v[i]
    if name in THROAT:
     phi=a+(b-a)*u+.04*math.sin(math.pi*t)*(1 if side>=0 else-1)
     # Broad asymmetrical course direction; upper rootband stays actual source.
     z=hi*(1-t)+lo*t+.019*(u-.5)*(1 if side>=0 else-1)-.004*math.sin(math.pi*u)*t
     core=point(z,phi,offset);blend=smooth((rr-3)/5);q=p.lerp(core,blend)
     if row==0:
      # Only short bottom free lap approaches concentric spherical stock.
      lap=smooth((rr-16)/8);lat=-.035+.32*(1-math.cos(phi))*.5+.035*(u-.5)
      target=C+Vector((math.cos(lat)*math.sin(phi),-math.cos(lat)*math.cos(phi),math.sin(lat)))*headR;q=q.lerp(target,lap)
      normal=(q-C).normalized();inner=q-normal*.0035
     else:inner=v[i+half]+(q-p)
     if rr<=3:protected.append(i)
    else:
     phi=a+(b-a)*u+.035*math.sin(math.pi*t)*(1 if g%2 else-1);z=1.449*(1-t)+1.352*t+.018*(u-.5)*(1 if g%2 else-1);core=point(z,phi,.018);base=smooth((18-rr)/8);q=p.lerp(core,base)
     # Upper receiving tip grows behind headlap on a smaller true sphere,
     # with staggered front/rear latitude rather than an unbroken cuff.
     lap=smooth((11-rr)/11);lat=.64 if math.cos(phi)>.25 else.30 if abs(math.cos(phi))<=.25 else.43;lat+=.045*(u-.5)*(1 if g%2 else-1)
     target=C+Vector((math.cos(lat)*math.sin(phi),-math.cos(lat)*math.cos(phi),math.sin(lat)))*neckR;q=q.lerp(target,lap);inner=v[i+half]+(q-p)
     if rr>=18:protected.append(i)
    if (name in THROAT and rr<=3)or(name in GUARDS and rr>=18):q=p;inner=v[i+half]
    out.append(q);inn.append(inner);maximum=max(maximum,(q-p).length)
  o.data=o.data.copy()
  for i,p in enumerate(out+inn):o.data.vertices[i].co=inv@p
  o.data.update();bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges)
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  vol=bm.calc_volume(signed=True);assert vol>0;bm.to_mesh(o.data);bm.free();err=max((o.matrix_world@o.data.vertices[i].co-v[i]).length for i in protected);assert err<1e-7
  o['constructionDescriptionHistory']=str(o.get('constructionDescription','unrecorded'));o['constructionDescription']='V38 broad directional lame with short actual-headpivot spherical clearance lap. Head/neck independent original rigid owners; finite support and motion interfaces unaccepted.'
  rec.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'class':'inherited-passive','maximumWorldDisplacementM':maximum,'positiveVolumeM3':vol,'actualSourceRootCoordinatesMaxErrorM':err,'rootScope':'Headupper4rows or cervicalupperlower7rows bothskins exact','lapScope':'Lowerheadlast8rows /upperneckfirst11rows only; broad external core remains shaped curved envelope. No intermediate owner, no sphere projection of entire skins.','nominalSphereRadiusM':headR if name in THROAT else neckR,'sphericalGapMeaning':'Short clearance surfaces only; core blending/source wall and stock neighbors still require actual finite contact/yaw screen.'})
 # Continuous narrow loadmembers to ACTUAL candidate receiving faces, rooted
 # on original near-level native headbow/cervical loadlink faces.
 def choose(source,side,level):
  v=[source.matrix_world@p.co for p in source.data.vertices];faces=[p for p in source.data.polygons if len(p.vertices)==4];f=max(faces,key=lambda f:side*sum(v[i].x for i in f.vertices)/4-abs(sum(v[i].z for i in f.vertices)/4-level)*1.3+abs(f.normal.x)*.03);return f,[v[i]for i in f.vertices]
 for ownername in['head','cervical-upper']:
  for side in[-1,1]:
   owner=bpy.data.objects[ownername];source=bpy.data.objects[f'V31 passive cranial load bow {side}'if ownername=='head'else f'V23 cervical 4 load link {side}'];f,q=choose(source,side,1.526 if ownername=='head'else 1.377)
   skin=bpy.data.objects[f'V33 tapered throat cheek plate {side} 1 1'if ownername=='head'else f'V23 cervical 4 directional guard {6 if side>0 else 9}'];vs=[skin.matrix_world@p.co for p in skin.data.vertices];half=len(vs)//2;idx=[half+7*19+8,half+7*19+9,half+8*19+9,half+8*19+8]if ownername=='head'else[half+16*19+8,half+16*19+9,half+17*19+9,half+17*19+8];target=[vs[i]for i in idx]
   options=[]
   for seq in[target,list(reversed(target))]:
    for k in range(4):order=seq[k:]+seq[:k];options.append((sum((q[i]-order[i]).length_squared for i in range(4)),order))
   target=min(options,key=lambda x:x[0])[1];verts=[]
   for t in[0,.25,.5,.75,1]:verts.extend([q[i].lerp(target[i],t)for i in range(4)])
   faces=[(3,2,1,0)]+[(j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k)for j in range(4)for k in range(4)]+[(16,17,18,19)];name=f'V38 neck-lap load member {ownername} {side}';member,vol=closed(name,verts,faces,owner,mats,props);added.append(name);rec.append({'name':name,'owner':ownername,'eras':'maker,mechanic,builder','class':'inherited-passive','positiveVolumeM3':vol,'sourceFrame':source.name,'sourceFace':f.index,'sourceFrameRootQuad':[list(x)for x in q],'receivingSkin':skin.name,'receivingInnerIndices':idx,'actualTerminalQuad':[list(x)for x in target],'rootLevelDistanceM':abs(sum(x.z for x in q)/4-(1.526 if ownername=='head'else 1.377)),'supportQualification':'Partial finite support path for regional receivingcourse. Other plates/lands and full load/area seating remain unresolved; sameowner crossings not exempted. Not a broad fan or duplicate copied pad union.'})
 for n in REMOVED:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
 return {'changedMeshes':THROAT+GUARDS,'changedNodes':[],'addedMeshes':added,'addedNodes':[],'removedMeshes':REMOVED,'watchMeshes':THROAT+GUARDS+added,'attachmentAndEraMap':rec,'headPivotWorld':list(C),'sourceTransformsAllExact':True,'headLapRadiusM':headR,'neckLapRadiusM':neckR,'nominalRadialLapClearanceM':headR-neckR-.0035,'lapIntervals':'Headlowerrows16..24, neckupperrows0..11; actual source receivingrootbands retained. Lamecore/side/rear shaping separate; one narrow bounded side/rear functional opening remains.','construction':'Independent head/upperneck broad directional lames, short concentric spherical underlap on real headcentre for compound pitch/yaw; no newowner/runtime/translation. Fourbadhead/upperfans replacedby4continuous near-level frame-to-inner members;6lowerbadfans retained with inherited failures.','protected':'Originalallpivots/head/bill/crown/optic/jaw/rig/rest/body/wings/legs/feet/materialprofiles;30lowercervicalskins and6remaining sourcefans exact. Head/throat18passiveskins change, no headidentity core change.','limits':['Physical fit not established by sphere radialmath or finite samples; local blend/sameowner/fixedapparatus interfaces may fail.','Purposeful exposedmechanism window not blanketclosure; remaining gaps are shown.','Source wall vectors on neckblends/upperhead retained, lowerheadlap3.5mmradial sphere wall; constantnormal/genuinevolume/load acceptance unproven.','Partial4finite support members do not validateeveryroot/plate or inherited lowerframe.']}
