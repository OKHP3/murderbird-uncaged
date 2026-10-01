import bpy,bmesh,math
from mathutils import Vector
OWNERS=['neck','cervical-mid-a','cervical-mid-b','cervical-upper','head']
POSITIONS=[(0,-.188,1.215),(0,-.245,1.277),(0,-.307,1.343),(0,-.356,1.423),(0,-.392,1.520)]
PROFILE=[(1.205,-.370,-.081,.154),(1.265,-.414,-.145,.133),(1.335,-.456,-.221,.111),(1.410,-.485,-.287,.092),(1.455,-.495,-.326,.078),(1.490,-.501,-.341,.076),(1.525,-.519,-.342,.086),(1.540,-.531,-.326,.103),(1.574,-.533,-.326,.107)]
CUTS=[1.205,1.282,1.350,1.430,1.529,1.574]
def profile(z):
 for k,(a,b)in enumerate(zip(PROFILE,PROFILE[1:])):
  if z<=b[0]:
   t=max(0,min(1,(z-a[0])/(b[0]-a[0])));d=b[0]-a[0];out=[]
   for j in(1,2,3):
    sec=(b[j]-a[j])/d
    sa=sec if k==0 else(b[j]-PROFILE[k-1][j])/(b[0]-PROFILE[k-1][0]);sb=sec if k+2>=len(PROFILE)else(PROFILE[k+2][j]-a[j])/(PROFILE[k+2][0]-a[0])
    if sec==0:sa=sb=0
    else:
     if sa*sec<=0:sa=0
     if sb*sec<=0:sb=0
     sa=math.copysign(min(abs(sa),3*abs(sec)),sec);sb=math.copysign(min(abs(sb),3*abs(sec)),sec)
    out.append((2*t**3-3*t*t+1)*a[j]+(t**3-2*t*t+t)*d*sa+(-2*t**3+3*t*t)*b[j]+(t**3-t*t)*d*sb)
   return out
 return list(PROFILE[-1][1:])
def make(name,owner,verts,faces,mat):
 m=bpy.data.meshes.new(name);m.from_pydata([bpy.data.objects[owner].matrix_world.inverted()@v for v in verts],[],faces);m.materials.append(mat);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));vol=bm.calc_volume(signed=True)
 if vol<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));vol=-vol
 assert all(e.is_manifold for e in bm.edges),name
 bm.to_mesh(m);bm.free();o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects[owner];o.matrix_parent_inverse.identity();o.location=(0,0,0);o['constructionClass']='proposed-passive-silhouette-proxy';o['exteriorEras']='maker,mechanic,builder';o['studyStatus']='Outline gate only, rigid shell not fitted armor or accepted production'
 for f in m.polygons:f.use_smooth=True
 return o,vol
def shell(ci,mat):
 nr=25;nc=96;v=[];basefaces=[];lo=CUTS[ci]+(.0015 if ci else 0);hi=CUTS[ci+1]-(.0015 if ci<4 else 0)
 for layer in(0,1):
  for r in range(nr):
   t=r/(nr-1)
   for c in range(nc):
    theta=-math.pi+math.tau*c/nc;slope=.010*math.sin(theta);z=lo+(hi-lo)*t+slope;front,rear,w=profile(z);cy=(front+rear)/2;ry=(rear-front)/2;d=-.0035*layer
    v.append(Vector(((w+d)*math.sin(theta),cy-(ry+d)*math.cos(theta),z)))
 for r in range(nr-1):
  for c in range(nc):
   th=-math.pi+math.tau*(c+.5)/nc
   # Short deliberate side windows only at stage2/3:16-22mm tall, roughly14mm wide. Not a long exposed channel.
   if ci in(1,2)and abs(abs(th)-math.pi/2)<.085 and 9<=r<=14:continue
   k=r*nc+c;k2=r*nc+(c+1)%nc;basefaces.append((k,k2,k2+nc,k+nc))
 n=nr*nc;faces=basefaces+[tuple(i+n for i in reversed(f))for f in basefaces];edges={}
 for f in basefaces:
  for j,a in enumerate(f):b=f[(j+1)%len(f)];key=tuple(sorted((a,b)));edges.setdefault(key,[]).append((a,b))
 for values in edges.values():
  if len(values)==1:a,b=values[0];faces.append((a,b,b+n,a+n))
 o,vol=make('V38 neck-profile rigid silhouette stage '+str(ci+1),OWNERS[ci],v,faces,mat);return {'name':o.name,'owner':OWNERS[ci],'zInterval':[lo,hi],'volumeM3':vol,'sectionThicknessRadialM':.0035,'purpose':'Simple continuous reference-taper outline, not final armor seams or movement clearance'}
def cylinder(o,a,b,rad):
 d=(b-a).normalized();u=d.cross(Vector((1,0,0))).normalized();vv=d.cross(u);verts=[];count=24
 for center in(a,b):
  for j in range(count):verts.append(center+rad*(u*math.cos(j*math.tau/count)+vv*math.sin(j*math.tau/count)))
 faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(j,(j+1)%count,(j+1)%count+count,j+count)for j in range(count)]
 m=bpy.data.meshes.new(o.name+' redistributed physical span');m.from_pydata([o.matrix_world.inverted()@v for v in verts],[],faces)
 for mat in o.data.materials:m.materials.append(mat)
 m.update();o.data=m;o['v38NeckProfile01']='Redistributed physical link between declared native endpoints; inherited fit annotations historical, not current fit proof';return {'name':o.name,'owner':o.parent.name,'newActualEndpointCentresNative':[list(a),list(b)],'role':'Rebuilt physical stage load link, proposal stock'}
def apply():
 bpy.context.view_layer.update();before={n:bpy.data.objects[n].matrix_world.translation.copy()for n in OWNERS};changednodes=[]
 for o in list(bpy.data.objects):
  if o.name.startswith('V38 neck-profile rigid silhouette stage '):bpy.data.objects.remove(o,do_unlink=True)
 for n,p in zip(OWNERS,POSITIONS):
  o=bpy.data.objects[n];children={c.name:c.matrix_world.copy()for c in o.children};mw=o.matrix_world.copy();mw.translation=Vector(p);o.matrix_world=mw;bpy.context.view_layer.update()
  for child,m in children.items():bpy.data.objects[child].matrix_world=m;changednodes.append(child)
  bpy.context.view_layer.update()
 bpy.context.view_layer.update();frame=[]
 for o in list(bpy.data.objects):
  if o.type!='MESH':continue
  if o.name.startswith('V23 cervical ')and'directional guard'not in o.name:
   parts=o.name.split();ci=int(parts[2])-1
   if 'load link'in o.name:
    side=int(parts[-1]);a=Vector(POSITIONS[ci])+Vector((side*.053,0,.006));b=Vector(POSITIONS[ci+1])+Vector((side*(.026 if ci==3 else .053),0,-.027 if ci==3 else 0));frame.append(cylinder(o,a,b,.006));continue
   target=ci if 'proximal race'in o.name else ci+1
   if ci==3 and('distal race'in o.name or'captive pin'in o.name):continue # Raised skull ball/socket already at preservedheadcentre.
   delta=Vector(POSITIONS[target])-before[OWNERS[target]];inv=o.matrix_world.inverted()
   if delta.length>0:
    for v in o.data.vertices:v.co=inv@(o.matrix_world@v.co+delta)
    o['v38NeckProfile01']='Physical bearing/pin stock relocated with named joint centre; inherited endpoint annotations historical';frame.append({'name':o.name,'owner':o.parent.name,'physicalInterfaceDeltaNative':list(delta)})
 hidden=[]
 for o in bpy.data.objects:
  if o.type=='MESH'and(('directional guard'in o.name and o.name.startswith('V23 cervical '))or o.name.startswith('V33 tapered throat cheek plate ')or o.name.startswith('V38 curved-neck formed yoke ')):
   o.hide_render=True;o.hide_viewport=True;o.hide_set(True);o['silhouetteStudyHistoricalHidden']=True;hidden.append(o.name)
 mat=bpy.data.objects['V23 cervical 1 directional guard 3'].data.materials[0];surfaces=[shell(i,mat)for i in range(5)]
 return {'status':'Simple editable rigid neck silhouette / redistributed-joint PROPOSAL, not full armor construction','oldPivotsNative':{n:list(v)for n,v in before.items()},'newPivotsNative':dict(zip(OWNERS,POSITIONS)),'stageZIntervalsM':[POSITIONS[i+1][2]-POSITIONS[i][2]for i in range(4)],'actualPhysicalFrameChanges':frame,'addedProxyShells':surfaces,'hiddenHistoricalSkins':hidden,'profileControlsNative':PROFILE,'headAndBreastWorldRest':'Intended exact boundary-child compensation; verify before any runtime export','limitations':['Five owner-rigid shell parts/four sloping seams are outline study, not sliding-lap or collision acceptance.','Historical58skins+10carriers stay preserved hidden in native; eventualexport must explicitly exclude, not rely on render visibility.','No export, texture, material finishing, owneracceptance or production change.']}
