"""V31 coordinated head reconstruction, editable native metre/Z-up profiles.

July is HEAD ONLY; owner whole-bird controls the almost-closed neutral jaw.
Coordinates below are direct offsets from the retained head attachment.
No nested historical mass map, runtime scaling, body/neck change or finish.
Hidden skull and processor construction remains a proposal.
"""
import bpy,bmesh,math,json
from mathutils import Vector,Matrix

OWNERS={'head','jaw','upper-bill','cranial-cover','builder-optics','processing'}
BOUNDARY={'V21 head captive shaft','V23 cervical 4 captive pin'}
# Outer blade / posterior cutting seat / half-width. Tip returns aft.
BILL=[(-.285,.341,-.278,.205,.094),(-.327,.323,-.299,.182,.101),(-.368,.286,-.309,.153,.090),(-.402,.220,-.317,.115,.067),(-.411,.139,-.330,.090,.052),(-.408,.064,-.347,.058,.036),(-.373,.020,-.346,.035,.019),(-.345,.004,-.345,.010,.0015)]
# Formed paired lower blades rise from the compact rear journal and curve
# into the posterior cutting seat, rather than crossing beneath as a shelf.
JAW=[(.114,-.135,.165,.017),(.117,-.187,.185,.019),(.108,-.240,.198,.015),(.091,-.270,.199,.011),(.069,-.287,.176,.009),(.049,-.299,.147,.007),(.032,-.307,.109,.005),(.021,-.322,.084,.003),(.012,-.339,.052,.0018)]
SKULL=[(-.30,.272,.090,.065),(-.21,.266,.156,.110),(-.10,.232,.153,.155),(.025,.182,.132,.140),(.13,.107,.078,.085),(.18,.065,.025,.034)]
BROW=[(.120,-.065,.326,.025),(.144,-.125,.342,.032),(.166,-.192,.330,.031),(.160,-.246,.303,.031),(.104,-.289,.267,.027)]
CHEEK=[(.103,-.040,.207,.022),(.139,-.095,.230,.032),(.156,-.158,.210,.035),(.153,-.208,.192,.030),(.131,-.253,.202,.026),(.098,-.282,.222,.019)]
EYE=(.158,-.220,.260)
JAW_PIVOT=(0,-.135,.165)
PROCESSOR_CENTER=(0,-.085,.245)

def sample(rows,t):
 u=max(0,min(1,t))*(len(rows)-1);i=min(int(u),len(rows)-2);s=u-i;a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
 return [.5*(2*b[k]+(-a[k]+c[k])*s+(2*a[k]-5*b[k]+4*c[k]-d[k])*s*s+(-a[k]+3*b[k]-3*c[k]+d[k])*s*s*s) for k in range(len(b))]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def props(o):return json.dumps(dict(o.items()),default=lambda x:list(x),sort_keys=True)
def node(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),props(o),o.hide_render,o.hide_viewport)
def snap(o):return (node(o),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),tuple((m.name,m.type) for m in o.modifiers))

def finite_sheet(fn,nu=28,nv=10,wall=.004,side=None,reference=None):
 v=[];norm=[]
 for i in range(nu+1):
  for j in range(nv+1):
   u=i/nu;t=j/nv;p=Vector(fn(u,t));du=Vector(fn(min(1,u+.0001),t))-Vector(fn(max(0,u-.0001),t));dv=Vector(fn(u,min(1,t+.0001)))-Vector(fn(u,max(0,t-.0001)));n=du.cross(dv);assert n.length>1e-12;n.normalize()
   ref=reference(p) if reference else (Vector((side,0,0)) if side else Vector((p.x,0,p.z-section(p.y)[0])))
   if n.dot(ref)<0:n=-n
   v.append(p);norm.append(n)
 n=len(v);v += [p-wall*nn for p,nn in zip(v.copy(),norm)];f=[];stride=nv+1
 for i in range(nu):
  for j in range(nv):a=i*stride+j;b=a+stride;f.extend([(a,a+1,b+1,b),(n+b,n+b+1,n+a+1,n+a)])
 boundary=list(range(stride))+[i*stride+nv for i in range(1,nu+1)]+[nu*stride+j for j in range(nv-1,-1,-1)]+[i*stride for i in range(nu-1,0,-1)]
 for i,a in enumerate(boundary):b=boundary[(i+1)%len(boundary)];f.append((a,b,n+b,n+a))
 return v,f

def ribbon(side,rows,wall=.004,bulge=.003):
 def fn(u,v):
  q=sample(rows,u);a=sample(rows,max(0,u-.001));b=sample(rows,min(1,u+.001));dy=b[1]-a[1];dz=b[2]-a[2];length=math.hypot(dy,dz);s=2*v-1
  return Vector((side*(q[0]+bulge*(1-s*s)),q[1]-dz/length*q[3]*s,q[2]+dy/length*q[3]*s))
 return finite_sheet(fn,nu=40,nv=10,wall=wall,side=side)

def section(y):
 for a,b in zip(SKULL,SKULL[1:]):
  if y<=b[0]:t=smooth((y-a[0])/(b[0]-a[0]));return [a[k]*(1-t)+b[k]*t for k in range(1,4)]
 return list(SKULL[-1][1:])
def crown(a,b,lo,hi,offset,tip,lean=0,root=.95):
 def fn(u,v):
  width=(root+(1-root)*smooth(u/.25))*(1-(1-tip)*smooth((u-.45)/.55));theta=(lo+hi)/2+lean*u+(v-.5)*(hi-lo)*width;y=a+(b-a)*u+.007*math.sin(math.pi*v)**2*u;z,rx,rz=section(y)
  # Continuous spatial fan; taper retains finite rounded tip width.
  return Vector(((rx+offset)*math.cos(theta),y,z+(rz+offset)*math.sin(theta)))
 return finite_sheet(fn,nu=32,nv=16,wall=.004)

def blade(a,b,hollow=True):
 ring=[(0,0),(.62,.04),(1,.19),(1,.63),(.74,.91),(0,1),(-.74,.91),(-1,.63),(-1,.19),(-.62,.04)];n=len(ring);steps=34;v=[];f=[]
 for inner in range(2 if hollow else 1):
  for j in range(steps+1):
   dy,dz,py,pz,w=sample(BILL,a+(b-a)*j/steps);cy=(dy+py)/2;cz=(dz+pz)/2
   for x,t in ring:
    y=dy*(1-t)+py*t;z=dz*(1-t)+pz*t;ww=w
    if inner:
     ww=max(.001,w-.004);length=max(.010,math.hypot(dy-py,dz-pz));scale=max(.25,1-.008/length);y=cy+(y-cy)*scale;z=cz+(z-cz)*scale
    v.append(Vector((ww*x,y,z)))
 m=(steps+1)*n
 for j in range(steps):
  for k in range(n):p=j*n+k;q=j*n+(k+1)%n;f.append((p,q,q+n,p+n))
  if hollow:
   for k in range(n):p=j*n+k;q=j*n+(k+1)%n;f.append((m+p+n,m+q+n,m+q,m+p))
 if hollow:
  for k in range(n):q=(k+1)%n;f.extend([(q,k,m+k,m+q),(steps*n+k,steps*n+q,m+steps*n+q,m+steps*n+k)])
 else:f.extend([tuple(reversed(range(n))),tuple(steps*n+k for k in range(n))])
 return v,f

def mandible_shell():
 # A single finite curved U section has visible formed plate area, not two
 # disconnected fork rails. Open top is the actual mouth cavity.
 def fn(u,v):
  x,y,z,w=sample(JAW,u);t=2*v-1;depth=.033*(1-u)+.007*u
  return Vector((x*t,y,z-depth*(1-t*t)))
 return finite_sheet(fn,nu=44,nv=24,wall=.0045)

def lower_nape(side):
 # Head-owned receiving hood returns from the cheek to the retained skull
 # joint. The open anterior bay is the jaw cavity; no neck-owner bridge.
 rows=[(.081,.003,.038,.028),(.102,.012,.079,.037),(.113,-.017,.134,.039),(.121,-.062,.187,.034),(.119,-.102,.221,.022)]
 return ribbon(side,rows,wall=.005,bulge=.001)

LOWER_SKULL=[(.024,-.036,.089,.100),(.065,-.038,.098,.099),(.106,-.027,.106,.096),(.148,-.019,.115,.100),(.182,-.015,.122,.119)]
ORBIT_OUTER=[(-.105,.265),(-.135,.326),(-.225,.355),(-.287,.326),(-.325,.269),(-.290,.217),(-.220,.195),(-.135,.209)]
def skull_hood(which):
 # Three directional finite receiving plates end at the jaw-root, not as
 # a flared top cup. Their upper boundaries seat below the temple shell.
 lo,hi=(-.65,.65) if which==0 else (.670,math.pi-.018)
 def fn(u,v):
  z,cy,rx,ry=sample(LOWER_SKULL,u);a=lo+(hi-lo)*v
  x=rx*math.sin(a);y=cy-ry*math.cos(a)
  if which==-1:x=-x
  rear=smooth((a/math.pi-.50)/.50);z-=.029*u*u*u*rear
  # Side root free edge sweeps upward/back, no circumferential cuff line.
  if which:z+=.010*math.sin(a)*math.sin(math.pi*u)
  # Partial concentric native-X posterior receiver. Its bore envelope
  # clears the measured guard10 contact sweep without trimming volume.
  if which:
   w=smooth((a-1.43)/.28);r=math.hypot(y,z);seat=.117-.030*(abs(x)/.085)**2
   if seat>r and r>1e-8:
    ratio=1+w*(seat/r-1);y*=ratio;z*=ratio
  return Vector((x,y,z))
 return finite_sheet(fn,nu=32,nv=32,wall=.005,reference=lambda p:Vector((p.x,p.y+.035,0)))

def orbital_facade(side):
 # Explicit profile-led outer corners define diagonal brow/cheek planes.
 # Radial interpolation is topology; outer shape is not a radius formula.
 n=64;radial=8;verts=[];faces=[]
 for inner in (False,True):
  for j in range(radial+1):
   t=j/radial
   for k in range(n):
    q=k/n*8;i=int(q)%8;f=q-int(q);a=ORBIT_OUTER[i];b=ORBIT_OUTER[(i+1)%8]
    # Rounded corner interpolation preserves the authored polygon's form.
    yout=a[0]*(1-f)+b[0]*f;zout=a[1]*(1-f)+b[1]*f
    a=math.tau*k/n;c=math.cos(a);ss=math.sin(a)
    y=EYE[1]+.047*c;z=EYE[2]+.047*ss
    # Profile's first corner is posterior and follows clockwise Y/Z.
    y=y*(1-t)+yout*t;z=z*(1-t)+zout*t
    x=.143*(1-t)+(.123+.009*ss-.008*c+.018*max(0,-ss))*t+.007*math.sin(math.pi*t)
    if inner:x-=.0045
    verts.append(Vector((side*x,y,z)))
 m=len(verts)//2
 for j in range(radial):
  for k in range(n):q=j*n+k;r=j*n+(k+1)%n;faces.extend([(q,r,r+n,q+n),(m+q+n,m+r+n,m+r,m+q)])
 for j in (0,radial):
  for k in range(n):q=j*n+k;r=j*n+(k+1)%n;faces.append((q,r,m+r,m+q))
 return verts,faces

def annular(side,cy,cz,profile,count=64):
 v=[];f=[]
 for x,r in profile:
  for k in range(count):a=math.tau*k/count;v.append(Vector((side*x,cy+r*math.cos(a),cz+r*math.sin(a))))
 for j in range(len(profile)):
  for k in range(count):f.append((j*count+k,j*count+(k+1)%count,((j+1)%len(profile))*count+(k+1)%count,((j+1)%len(profile))*count+k))
 return v,f

def cylinder(side,cy,cz,x0,x1,r,count=48):
 v=[Vector((side*x,cy+r*math.cos(math.tau*k/count),cz+r*math.sin(math.tau*k/count))) for x in (x0,x1) for k in range(count)];f=[(k,(k+1)%count,(k+1)%count+count,k+count) for k in range(count)]+[tuple(reversed(range(count))),tuple(range(count,2*count))];return v,f

def bar(a,b,width=.007,depth=.009):
 a=Vector(a);b=Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1)))
 if u.length<1e-6:u=axis.cross(Vector((0,1,0)))
 u.normalize();v=axis.cross(u);cross=[(-1,-1),(1,-1),(1,1),(-1,1)];verts=[c+u*x*width+v*y*depth for c in (a,b) for x,y in cross];faces=[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]+[(3,2,1,0),(4,5,6,7)];return verts,faces

def apply():
 bpy.context.view_layer.update();head=bpy.data.objects['head'];origin=head.matrix_world.translation.copy();nodes={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'}
 old=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name in OWNERS and o.name not in BOUNDARY];oldnames=[o.name for o in old];protected={o.name:snap(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in oldnames};templates={}
 for label,name in [('plate','Forged orbital brow -1'),('bearing','Coaxial mandible journal'),('optic','Seated Advanced optic -1'),('passive','Seated passive optic housing -1'),('processor','Processing lattice rail')]:
  o=bpy.data.objects[name];templates[label]={'props':dict(o.items()),'materials':list(o.data.materials)}
 # Actual jaw articulation is native X; move its hinge once with its frame.
 for n,p in [('jaw',JAW_PIVOT),('processing',PROCESSOR_CENTER)]:
  o=bpy.data.objects[n];m=o.matrix_world.copy();m.translation=origin+Vector(p);o.matrix_world=m;bpy.context.view_layer.update()
 mind=bpy.data.objects['anchor-mind'];m=mind.matrix_world.copy();m.translation=origin+Vector(PROCESSOR_CENTER);mind.matrix_world=m;bpy.context.view_layer.update()
 for o in old:bpy.data.objects.remove(o,do_unlink=True)
 added=[];errors=[];finite=[]
 def add(name,owner,geo,template='plate',role='plate',smooth_faces=True):
  verts,faces=geo;t=templates[template];mesh=bpy.data.meshes.new(name+' finite mesh');o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects[owner];o.matrix_basis=Matrix.Identity(4);o.matrix_parent_inverse=Matrix.Identity(4);bpy.context.view_layer.update();inv=o.matrix_world.inverted();world=[origin+Vector(p) for p in verts];mesh.from_pydata([inv@p for p in world],[],faces);mesh.update()
  for mat in t['materials']:mesh.materials.append(mat)
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  volume=bm.calc_volume(signed=True);assert volume>0,name;bm.to_mesh(mesh);bm.free()
  for p in mesh.polygons:p.use_smooth=smooth_faces and len(p.vertices)==4
  for k,v in t['props'].items():o[k]=v
  o['region']='head-reconstruction';o['surfaceRole']=role;o['proposal']=True;o['constructionOwner']=owner;o['articulatesAcrossJoint']=False;o['constructionDescription']='V31 direct native profile-led finite rigid construction study'
  if template not in ('optic','processor'):o['exteriorEras']='maker,mechanic,builder';o['constructionClass']='inherited-passive'
  error=max((o.matrix_world@v.co-p).length for v,p in zip(mesh.vertices,world));assert error<1e-6;errors.append(error);added.append(name);finite.append({'name':name,'owner':owner,'closed':True,'positiveVolumeM3':volume,'worldBounds':[[min(p[k] for p in world),max(p[k] for p in world)] for k in range(3)]});return o
 # Deep returned blade, substantial root, formed side flats and cutting edge.
 for i,(a,b,h) in enumerate([(0,.355,True),(.360,.710,True),(.715,1,False)]):add(f'V31 formed upper bill course {i}','upper-bill',blade(a,b,h),smooth_faces=False)
 for side in (-1,1):
  add(f'V31 formed diagonal orbital facade {side}','head',orbital_facade(side),smooth_faces=False)

  add(f'V31 bill root formed return {side}','upper-bill',ribbon(side,[(.106,-.286,.277,.017),(.092,-.304,.255,.016),(.081,-.315,.219,.012)],wall=.004))
  cy,cz=EYE[1:]
  add(f'V31 optic structural outer seat {side}','head',annular(side,cy,cz,[(.145,.044),(.146,.055),(.138,.057),(.130,.046)]),'bearing','bearing')
  add(f'V31 optic recessed receiving cup {side}','head',annular(side,cy,cz,[(.141,.048),(.139,.051),(.119,.040),(.115,.035),(.111,.035),(.113,.042),(.134,.049)]),'passive','recess')
  add(f'V31 Advanced optical aperture {side}','builder-optics',cylinder(side,cy,cz,.115,.119,.033),'optic','optic')
  # A non-luminous passive receiving floor remains in the earlier eras.
  add(f'V31 passive optic cavity floor {side}','head',cylinder(side,cy,cz,.102,.105,.0345),'passive','recess')
  # Compact journal is part of the swept cheek, not a large detached coin.
  jy,jz=JAW_PIVOT[1:]
  add(f'V31 jaw fixed annular journal {side}','head',annular(side,jy,jz,[(.133,.012),(.133,.023),(.145,.023),(.145,.012)]),'bearing','bearing')
  add(f'V31 jaw moving journal cap {side}','jaw',cylinder(side,jy,jz,.125,.131,.015),'bearing','bearing')
  add(f'V31 jaw captive rotating axle {side}','jaw',cylinder(side,jy,jz,.109,.148,.008),'bearing','bearing')
  add(f'V31 jaw fixed journal rim return {side}','head',bar((side*.117,jy+.021,jz+.020),(side*.142,jy+.021,jz+.020),.006,.006),'plate','frame',False)
  add(f'V31 jaw cheek clevis {side}','head',ribbon(side,[(.106,-.062,.212,.010),(.117,-.093,.190,.013),(.122,-.114,.183,.007)],wall=.005),'plate','frame')
  # A shaped bow connects retained neck shaft into the actual skull frame.
  rows=[(.064,0,.005,.013),(.076,.012,.077,.014),(.084,-.016,.153,.015),(.101,-.067,.234,.014),(.112,-.123,.282,.010)]
  add(f'V31 passive cranial load bow {side}','head',ribbon(side,rows,wall=.006),'plate','frame')
  # Actual aft fittings and their receiving yokes remain readable through
  # a purposeful temple machinery bay; no fictitious sensors are added.
  for i,(y,z,r) in enumerate([(-.076,.269,.025),(-.022,.230,.022),(.025,.177,.019)]):
   add(f'V31 passive temporal fitting {side} {i}','head',annular(side,y,z,[(.142,r*.43),(.142,r),(.155,r),(.155,r*.43)]),'bearing','bearing')
   add(f'V31 temporal fitting root {side} {i}','head',bar((side*.109,y,z),(side*.141,y,z),.008,.008),'plate','frame',False)
 for which in (0,-1,1):add(f'V31 formed throat receiving guard {which}','head',skull_hood(which),smooth_faces=False)
 # Continuous curved mandible plate retains an open cavity above its U.
 add('V31 formed curved mandible shell','jaw',mandible_shell(),smooth_faces=False)
 # Fixed lateral receiving shells return into the orbital and lower hood
 # assembly. Dorsal cap remains independently owned/opening.
 for side in (-1,1):
  lo,hi=(-.44,.91) if side==1 else (math.pi-.91,math.pi+.44)
  add(f'V31 fixed temporal receiving wall {side}','head',crown(-.240,.123,lo,hi,-.004,.87),smooth_faces=False)
 # Functional optic aperture in each fixed receiving wall. The cylindrical
 # bore is around the real recessed cup, leaving a continuous outer load
 # wall; no lighting/material substitute and no temporary exported object.
 for side in (-1,1):
  wall=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];v,f=cylinder(side,EYE[1],EYE[2],.080,.230,.061,count=96)
  data=bpy.data.meshes.new('V31 temporary optic bore mesh');data.from_pydata([origin+p for p in v],[],f);data.update();cut=bpy.data.objects.new('V31 temporary optic bore',data);bpy.context.scene.collection.objects.link(cut);bpy.context.view_layer.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
  modifier=wall.modifiers.new('Finite optic receiving bore','BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cut;bpy.context.view_layer.objects.active=wall;wall.select_set(True);bpy.ops.object.modifier_apply(modifier=modifier.name);wall.select_set(False);bpy.data.objects.remove(cut,do_unlink=True);bpy.data.meshes.remove(data)
  bm=bmesh.new();bm.from_mesh(wall.data);assert all(e.is_manifold for e in bm.edges),wall.name;volume=bm.calc_volume(signed=True);assert volume>0;bm.free()
  for record in finite:
   if record['name']==wall.name:record['positiveVolumeM3']=volume;record['functionalAperture']='Native-X finite61mm radius bore around optic cup; outer temple load path retained'
 # Staggered short swept patches follow the same actual curved skull.
 # Lateral edges use small butt seams; longitudinal roots overlap radially.
 add('V31 frontal cranial cap receiving seat','head',crown(-.286,-.155,.75,2.37,.001,.94))
 for row,(a,b) in enumerate([(-.286,-.085),(-.144,.065),(-.005,.148)]):
  for column in range(5):
   center=.78+column*.395;stagger=(-.011 if column%2 else .009)*(1 if row%2 else -1);aa=a+stagger;bb=b+stagger*.5
   if row==0 and column in (0,4):aa=max(aa,-.251);bb+=.012;center+=(.10 if column==0 else -.10)
   width=.378;tip=[.89,.82,.76][row]-.035*(column%2);lean=(column-2)*.012
   add(f'V31 swept dorsal crown course {row} {column}','cranial-cover',crown(aa,bb,center-width/2,center+width/2,.009+row*.007+(.021 if row==0 and column in (0,4) else 0),tip,lean,root=.99))
 fan=[(-.168,.080,.43,.52,.008,.61,-.08),(-.091,.134,.04,.54,.017,.63,-.05),(-.013,.158,-.29,.47,.023,.61,-.04)]
 for side in (-1,1):
  for i,(a,b,theta,span,off,tip,lean) in enumerate(fan):
   lo=theta-span/2;hi=theta+span/2
   if side==-1:lo,hi=math.pi-hi,math.pi-lo;lean=-lean
   add(f'V31 swept temporal fan {side} {i}','head',crown(a,b,lo,hi,off,tip,lean,root=.96))
 # The Advanced processor stays distinct from power and remains protected
 # inside the cranium. Compact rack edges replace the exposed chin lattice.
 edges=[]
 for y in (-.140,-.024):
  for z in (.208,.300):edges.append(((-.052,y,z),(.052,y,z)))
 for x in (-.052,.052):
  for z in (.208,.300):edges.append(((x,-.140,z),(x,-.024,z)))
 for x in (-.052,.052):
  for y in (-.140,-.024):edges.append(((x,y,.208),(x,y,.300)))
 for i,(a,b) in enumerate(edges):add('Processing lattice rail'+('' if i==0 else f'.{i:03d}'),'processing',bar(a,b,.0035,.0035),'processor','inner',False)
 for i in range(12):
  z=.229 if i<6 else .279;j=i%6
  if j<3:y=-.116+j*.034;a=(-.048,y,z);b=(.048,y,z)
  else:x=-.038+(j-3)*.038;a=(x,-.136,z);b=(x,-.028,z)
  add('Processing crosspiece'+('' if i==0 else f'.{i:03d}'),'processing',bar(a,b,.002,.002),'processor','inner',False)
 # Non-exporting editable guides are curves, not hidden armor substitutes.
 guides=[]
 for label,points in [('upper-profile',[(0,q[0],q[1]) for q in BILL]),('cutting-seat',[(0,q[2],q[3]) for q in BILL]),('mandible-profile',[(q[0],q[1],q[2]) for q in JAW])]:
  data=bpy.data.curves.new('V31 authoring '+label,'CURVE');data.dimensions='3D';sp=data.splines.new('POLY');sp.points.add(len(points)-1);guide=bpy.data.objects.new(data.name,data);bpy.context.scene.collection.objects.link(guide);guide.parent=head;guide.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update();inv=guide.matrix_world.inverted()
  for v,p in zip(sp.points,points):v.co=(*list(inv@(origin+Vector(p))),1)
  guide.hide_render=True;guide.hide_viewport=False;guide['authoringGuide']=True;guide['exportExclude']=True;guides.append(guide.name)
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();front=None;frontname=None
 for name in added:
  o=bpy.data.objects[name]
  if o.parent.name!='upper-bill':continue
  ev=o.evaluated_get(dg);m=ev.to_mesh()
  for v in m.vertices:
   p=ev.matrix_world@v.co
   if front is None or p.y<front.y:front=p.copy();frontname=name
  ev.to_mesh_clear()
 for n in ('bill-contact','anchor-beak'):
  o=bpy.data.objects[n];m=o.matrix_world.copy();m.translation=front;o.matrix_world=m
 # External Maker jaw control uses a real point on the finite formed
 # negative-X lower blade, with useful lever arm from the relocated hinge.
 jaw=bpy.data.objects['jaw'];receiver=bpy.data.objects['V31 formed curved mandible shell'];ev=receiver.evaluated_get(dg);mesh=ev.to_mesh();aim=origin+Vector((-.110,-.227,.201));socket=min((ev.matrix_world@v.co for v in mesh.vertices),key=lambda p:(p-aim).length).copy();ev.to_mesh_clear();local=jaw.matrix_world.inverted()@socket
 socket_record={'schema':1,'point':[local.x,local.z,-local.y],'coordinateSpace':'gltf-node-local','surfaceObject':receiver.name,'status':'reconstructed external control attachment'};jaw['makerControlSocketV1']=json.dumps(socket_record,sort_keys=True)
 restsocket=socket.copy();restrotation=jaw.rotation_euler.copy();jaw.rotation_euler.x+=.32;bpy.context.view_layer.update();opensocket=jaw.matrix_world@local;jaw.rotation_euler=restrotation
 bpy.context.view_layer.update();allowed={'jaw','processing','anchor-mind','bill-contact','anchor-beak'};assert all(node(bpy.data.objects[n])==v for n,v in nodes.items() if n not in allowed);assert all(snap(bpy.data.objects[n])==v for n,v in protected.items());assert len([o for o in bpy.data.objects if o.type=='EMPTY'])==len(nodes)
 return {'region':'coordinated-head-reconstruction','status':'Coarse reference-led reconstruction; artistic and motion HOLD','changedMeshes':[n for n in added if n in oldnames],'added':[n for n in added if n not in oldnames],'removed':[n for n in oldnames if n not in added],'reconstructedMeshes':added,'changedNodes':sorted(allowed),'primaryPivotChanges':[{'name':'jaw','afterWorld':list(bpy.data.objects['jaw'].matrix_world.translation),'localXOpening':True},{'name':'processing','afterWorld':list(bpy.data.objects['processing'].matrix_world.translation),'advancedOnly':True}],'protectedMeshSnapshotsExact':len(protected),'headAttachmentAndBoundaryShaftsExact':sorted(BOUNDARY),'namedNodeParentsPreserved':True,'materialDefinitionsChanged':False,'advancedOnlyMeshes':[n for n in added if bpy.data.objects[n].get('exteriorEras')=='builder'],'billContactNativeWorld':list(front),'contactObject':frontname,'contactMethod':'minimum nativeY evaluated upper-bill surface vertex','maximumAuthoredWorldErrorM':max(errors),'finiteConstructedSolids':finite,'authoringGuides':guides,'makerControlSocket':{'metadata':socket_record,'restWorld':list(restsocket),'open32World':list(opensocket),'attachmentSurfaceDistanceM':0.0,'method':'Exact evaluated receiver vertex selected nearest authored lever-seat aim, then converted native jawlocal(X,Y,Z)→glTF(X,Z,−Y).','leverArmM':local.length},'profileContract':{'origin':list(origin),'coordinateSpace':'direct metres, nativeX lateral/Zup/−Yfront; no massmap','bill':BILL,'jaw':JAW,'brow':BROW,'cheek':CHEEK,'skull':SKULL,'lowerSkull':LOWER_SKULL,'orbitalOuter':ORBIT_OUTER,'eye':EYE,'jawPivot':JAW_PIVOT,'processorCenter':PROCESSOR_CENTER},'limits':['First actual visual gate precedes collision refinement.','Unseen frame/cup/rack seating remains proposed; not engineering approval.','New jaw/optic placement requires refreshed socket/contact interpretation after native review.','Jaw/cranial opening poses require strict evaluated checks after coarse visual gate.']}
