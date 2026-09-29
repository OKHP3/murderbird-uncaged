"""V30 major head-form study. July controls head; owner whole-bird controls closed rest.
Editable pre-mass profile coordinates are baked into the retained V29 head mass.
No runtime deformation, head-root movement, new materials or body edits.
"""
import bpy,bmesh,math,json
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
OWNERS={'head','jaw','upper-bill','cranial-cover','builder-optics'}
BOUNDARY={'V21 head captive shaft','V23 cervical 4 captive pin'}
BILL=[(-.526,1.825,-.526,1.715,.090),(-.569,1.817,-.548,1.699,.096),(-.611,1.791,-.564,1.684,.085),(-.642,1.751,-.578,1.670,.067),(-.649,1.704,-.594,1.650,.048),(-.639,1.662,-.608,1.629,.031),(-.616,1.628,-.609,1.618,.014),(-.594,1.607,-.596,1.603,.0025)]
PROFILE=[(-.574,1.776,.100,.050),(-.505,1.777,.149,.081),(-.429,1.765,.153,.112),(-.352,1.746,.146,.115),(-.279,1.718,.118,.092),(-.216,1.687,.075,.047)]
def sample(rows,t):
 u=max(0,min(1,t))*(len(rows)-1);i=min(int(u),len(rows)-2);s=u-i
 a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
 return [.5*(2*b[k]+(-a[k]+c[k])*s+(2*a[k]-5*b[k]+4*c[k]-d[k])*s*s+(-a[k]+3*b[k]-3*c[k]+d[k])*s*s*s) for k in range(len(b))]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def props(o):return json.dumps(dict(o.items()),default=lambda x:list(x),sort_keys=True)
def snap(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(f.vertices) for f in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),props(o),o.hide_render,o.hide_viewport)
def node(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),props(o))
def ribbon(side,rows,wall=.004,along=30,across=8):
 verts=[];faces=[];n=(along+1)*(across+1)
 for inner in (0,1):
  for j in range(along+1):
   t=j/along;q=sample(rows,t);a=sample(rows,max(0,t-.002));b=sample(rows,min(1,t+.002));dy=b[1]-a[1];dz=b[2]-a[2];L=max(1e-10,math.hypot(dy,dz))
   for k in range(across+1):
    s=2*k/across-1;w=q[3]*s;verts.append((side*(q[0]+.001*(1-s*s)-inner*wall),q[1]-dz/L*w,q[2]+dy/L*w))
 stride=across+1
 for j in range(along):
  for k in range(across):
   a=j*stride+k;b=a+stride;faces.extend([(a,a+1,b+1,b),(n+b,n+b+1,n+a+1,n+a)])
  a=j*stride;b=a+stride;faces.append((b,a,n+a,n+b));a+=across;b+=across;faces.append((a,b,n+b,n+a))
 for k in range(across):
  faces.append((k,k+1,n+k+1,n+k));a=along*stride+k;faces.append((a+1,a,n+a,n+a+1))
 return verts,faces

def polygon(side,outline,x=.148,wall=.005):
 n=len(outline);v=[(side*xx,y,z) for xx in (x,x-wall) for y,z in outline];f=[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];return v,f

def orbital_facade(side):
 # Formed asymmetric receiver follows the actual optic aperture, with a
 # broad posterior cranium seat. The finite receiver backs the brow/cheek,
 # rather than leaving a detached arch above an exposed full retaining disk.
 n=64;v=[];f=[];cy=-.5055;cz=1.756
 for innerwall in (0,1):
  for outer in (0,1):
   for k in range(n):
    a=2*math.pi*k/n;co=math.cos(a);si=math.sin(a)
    r=.048 if not outer else .070+.013*max(0,co)+.013*max(0,si)-.006*max(0,-co)
    y=cy+r*co;z=cz+r*si;x=.126+.005*si-.012*innerwall
    if outer:y+=.014*max(0,co)**3
    v.append((side*x,y,z))
 for k in range(n):
  j=(k+1)%n
  f.extend([(k,j,n+j,n+k),(2*n+k,3*n+k,3*n+j,2*n+j),(k,2*n+k,2*n+j,j),(n+k,n+j,3*n+j,3*n+k)])
 return v,f

def bill(start,end,hollow=True):
 # Twelve-point formed section: dorsal ridge, broad planar side and a thinner
 # posterior cutting seat, unlike the old inflated elliptical nasal cells.
 ring=[(0,0),(.45,.07),(.90,.18),(1,.43),(.95,.75),(.63,.94),(0,1),(-.63,.94),(-.95,.75),(-1,.43),(-.90,.18),(-.45,.07)]
 rows=32;n=len(ring);v=[];f=[];sets=2 if hollow else 1
 for inner in range(sets):
  for j in range(rows+1):
   dY,dZ,pY,pZ,w=sample(BILL,start+(end-start)*j/rows);cy=(dY+pY)/2;cz=(dZ+pZ)/2
   for x,t in ring:
    yy=dY*(1-t)+pY*t;zz=dZ*(1-t)+pZ*t
    if inner:
     w=max(.001,w-.0045);L=max(.010,math.hypot(dY-pY,dZ-pZ));scale=max(.2,1-.009/L);yy=cy+(yy-cy)*scale;zz=cz+(zz-cz)*scale
    v.append((w*x,yy,zz))
 m=(rows+1)*n
 for j in range(rows):
  for k in range(n):
   a=j*n+k;b=j*n+(k+1)%n;f.append((a,b,b+n,a+n))
   if hollow:f.append((m+a+n,m+b+n,m+b,m+a))
 if hollow:
  for k in range(n):
   a=k;b=(k+1)%n;f.append((b,a,m+a,m+b));a=rows*n+k;b=rows*n+(k+1)%n;f.append((a,b,m+b,m+a))
 else:f.extend([tuple(reversed(range(n))),tuple(rows*n+k for k in range(n))])
 return v,f

def crown_sheet(rows):
 # Narrow swept sagittal crest with a finite closed skin.
 along=28;across=10;v=[];f=[];n=(along+1)*(across+1)
 for inner in (0,1):
  for j in range(along+1):
   y,z,w=sample(rows,j/along)
   for k in range(across+1):
    s=2*k/across-1;v.append((w*s,y+.002*s*s,z-.004*s*s-inner*.004))
 stride=across+1
 for j in range(along):
  for k in range(across):
   a=j*stride+k;b=a+stride;f.extend([(a,a+1,b+1,b),(n+b,n+b+1,n+a+1,n+a)])
  a=j*stride;b=a+stride;f.append((b,a,n+a,n+b));a+=across;b+=across;f.append((a,b,n+b,n+a))
 for k in range(across):
  f.append((k,k+1,n+k+1,n+k));a=along*stride+k;f.append((a+1,a,n+a,n+a+1))
 return v,f

def section(y):
 for a,b in zip(PROFILE,PROFILE[1:]):
  if y<=b[0]:
   t=max(0,min(1,(y-a[0])/(b[0]-a[0])));t=smooth(t);return [a[k]*(1-t)+b[k]*t for k in range(1,4)]
 return list(PROFILE[-1][1:])
def scalp(y,theta,offset=0):
 zc,rx,rz=section(y);return Vector(((rx+offset)*math.cos(theta),y,zc+(rz+offset)*math.sin(theta)))
def facade_x(y,z):
 zc,rx,rz=section(y);v=(z-zc)/rz;xx=rx*math.sqrt(max(.015,1-v*v));floor=.128*(1-smooth((z-1.803)/.060))+.058*smooth((z-1.803)/.060);return max(floor,xx)
def closed_patch(fn,nu=30,nv=20,wall=.0035,periodic=False,side=None):
 # Numerical surface normals carry finite wall into the curved receiving
 # envelope. Periodic annuli have welded seam topology, no duplicate rings.
 vs=[];norms=[];countv=nv if periodic else nv+1
 for i in range(nu+1):
  u=i/nu
  for j in range(countv):
   v=j/nv;p=fn(u,v);du=fn(min(1,u+.0001),v)-fn(max(0,u-.0001),v);dv=fn(u,v+.0001 if periodic else min(1,v+.0001))-fn(u,v-.0001 if periodic else max(0,v-.0001));n=du.cross(dv)
   assert n.length>1e-15,(u,v)
   n.normalize();ref=Vector((side,0,0)) if side else p-Vector((0,p.y,section(p.y)[0]))
   if n.dot(ref)<0:n=-n
   vs.append(p);norms.append(n)
 total=len(vs);vs+= [p-wall*n for p,n in zip(vs.copy(),norms)];faces=[]
 for i in range(nu):
  for j in range(nv):
   k=(j+1)%countv;a=i*countv+j;b=i*countv+k;c=(i+1)*countv+k;d=(i+1)*countv+j;faces.extend([(a,b,c,d),(total+d,total+c,total+b,total+a)])
 for j in range(nv):
  k=(j+1)%countv;faces.append((k,j,total+j,total+k));a=nu*countv+j;b=nu*countv+k;faces.append((a,b,total+b,total+a))
 if not periodic:
  for i in range(nu):
   a=i*countv;b=(i+1)*countv;faces.append((a,b,total+b,total+a));a+=nv;b+=nv;faces.append((b,a,total+a,total+b))
 return vs,faces

def skull_band(y0,y1,angle0,angle1,offset=0,tip=.95,lean=.0,root_width=1.,seat_front=None):
 def fn(u,v):
  width=(root_width+(1-root_width)*smooth(u/.28))*(1-(1-tip)*smooth((u-.45)/.55));center=(angle0+angle1)/2+lean*u;theta=center+(v-.5)*(angle1-angle0)*width;y=y0+(y1-y0)*u+.010*math.sin(math.pi*v)**2*u+.014*math.cos(math.pi*v)*(1-u)**2;rad=offset if seat_front is None else seat_front+(offset-seat_front)*smooth(u/.48);return scalp(y,theta,rad)
 return closed_patch(fn)
def face_sheet(side,outline,wall=.0045):
 # Triangulated curved plate includes recursively sampled interior vertices,
 # not merely a warped perimeter/flat n-gon.
 keys={};coords=[];tris=[]
 def ix(p):
  key=(round(p.x,7),round(p.y,7))
  if key not in keys:keys[key]=len(coords);coords.append((p.x,p.y))
  return keys[key]
 def sub(a,b,c,depth):
  if depth:
   ab=(a+b)/2;bc=(b+c)/2;ca=(c+a)/2;sub(a,ab,ca,depth-1);sub(ab,b,bc,depth-1);sub(ca,bc,c,depth-1);sub(ab,bc,ca,depth-1)
  else:tris.append((ix(a),ix(b),ix(c)))
 polygonpoints=[Vector((y,z,0)) for y,z in outline]
 for tri in tessellate_polygon([polygonpoints]):sub(*[polygonpoints[t] if isinstance(t,int) else t for t in tri],2)
 points=[];norms=[]
 for y,z in coords:
  x=facade_x(y,z);dy=(facade_x(y+.0001,z)-facade_x(y-.0001,z))/.0002;dz=(facade_x(y,z+.0001)-facade_x(y,z-.0001))/.0002;n=Vector((side,-dy,-dz)).normalized();points.append(Vector((side*x,y,z)));norms.append(n)
 n=len(points);v=points+[p-wall*nn for p,nn in zip(points,norms)];f=list(tris)+[tuple(n+i for i in reversed(t)) for t in tris];edge={}
 for t in tris:
  for a,b in zip(t,t[1:]+t[:1]):edge.setdefault(tuple(sorted((a,b))),[]).append((a,b))
 for e,x in edge.items():
  if len(x)==1:a,b=x[0];f.append((a,b,n+b,n+a))
 return v,f

def orbital(side):
 def fn(u,v):
  a=math.tau*v;co=math.cos(a);si=math.sin(a);r=.048*(1-u)+(.070+.013*max(0,co)+.013*max(0,si)-.006*max(0,-co))*u;y=-.5055+r*co+.014*max(0,co)**3*u;z=1.756+r*si;x=(.126+.005*si)*(1-u)+facade_x(y,z)*u;return Vector((side*x,y,z))
 return closed_patch(fn,nu=14,nv=72,wall=.005,periodic=True,side=side)

def narrow_receiver(side):
 def fn(u,v):
  a=math.tau*v;co=math.cos(a);si=math.sin(a)
  # Deliberately asymmetric shallow seat: substantial diagonal upper/back
  # receiver, narrow lower/front return, rather than a blank full eye disk.
  outer=.054+.009*max(0,si)+.004*max(0,co)
  r=.048*(1-u)+outer*u;y=-.5055+r*co;z=1.756+r*si
  x=(.126+.005*si)*(1-u)+(facade_x(y,z)-.005)*u
  return Vector((side*x,y,z))
 return closed_patch(fn,nu=10,nv=72,wall=.004,periodic=True,side=side)

def apply():
 bpy.context.view_layer.update();pivot=bpy.data.objects['head'].matrix_world.translation.copy()
 oldpivot=Vector((0,-.3226,1.6028));factor=1.456
 nodes={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'}
 targets=['Profiled upper bill blade 0','Overlapping nasal hood','Profiled upper bill blade 1','Distal mandible bridge']+[f'{p} {side}' for p in ('Cere root transition','Forked forged mandible','Forged orbital brow','Broad swept cheek band','Forged orbital mounting plate','V24 anterior orbital root receiver') for side in (-1,1)]
 opticnames=[f'{p} {side}' for p in ('Seated passive optic housing','Seated Advanced optic','Recessed orbital bearing','Orbital passive retaining race') for side in (-1,1)]
 targets+=opticnames
 capnames=['V27 fixed frontal cranial receiving return','V27 dorsal swept cranial course 0']
 protected={o.name:snap(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in set(targets+capnames)}
 changed=[];errors=[]
 def mapped(p):return pivot+factor*(Vector(p)-oldpivot)
 def install(n,v,f):
  o=bpy.data.objects[n];assert o.parent and o.parent.name in OWNERS
  bpy.context.view_layer.update();inv=o.matrix_world.inverted();world=[mapped(p) for p in v]
  m=bpy.data.meshes.new(n+' V30 formed solid');m.from_pydata([inv@p for p in world],[],f);m.update()
  for material in o.data.materials:m.materials.append(material)
  bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  assert all(e.is_manifold for e in bm.edges),n
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  assert bm.calc_volume(signed=True)>0,n
  bm.to_mesh(m);bm.free();o.data=m;o.modifiers.clear()
  for face in m.polygons:face.use_smooth=len(face.vertices)==4
  errors.append(max((o.matrix_world@q.co-p).length for q,p in zip(m.vertices,world)));changed.append(n)
 for n,a,b,hollow in [('Profiled upper bill blade 0',0,.345,True),('Overlapping nasal hood',.349,.715,True),('Profiled upper bill blade 1',.719,1,False)]:
  v,f=bill(a,b,hollow);install(n,v,f)
 for side in (-1,1):
  v,f=ribbon(side,[(.093,-.527,1.803,.014),(.098,-.557,1.774,.018),(.083,-.580,1.736,.017),(.062,-.593,1.689,.009)],wall=.0045);install(f'Cere root transition {side}',v,f)
  # Rear jaw is inboard of the unchanged orbital races; closed distal edge
  # follows the blade's posterior curve, while the original hinge opens it.
  v,f=ribbon(side,[(.119,-.432,1.663,.020),(.097,-.470,1.670,.014),(.075,-.514,1.681,.011),(.061,-.555,1.679,.010),(.049,-.580,1.660,.008),(.031,-.597,1.637,.005),(.021,-.605,1.621,.0025)],wall=.005,along=40);install(f'Forked forged mandible {side}',v,f)
  outline=[(-.374,1.810),(-.397,1.847),(-.438,1.850),(-.478,1.829),(-.519,1.811),(-.546,1.795),(-.550,1.782),(-.535,1.791),(-.520,1.803),(-.502,1.811),(-.484,1.807),(-.465,1.792),(-.446,1.795),(-.418,1.807),(-.396,1.793)]
  v,f=face_sheet(side,outline,wall=.005);install(f'Forged orbital brow {side}',v,f)
  outline=[(-.407,1.783),(-.429,1.745),(-.456,1.721),(-.483,1.711),(-.510,1.709),(-.540,1.719),(-.565,1.735),(-.584,1.730),(-.567,1.707),(-.538,1.696),(-.509,1.695),(-.479,1.700),(-.447,1.720),(-.422,1.750),(-.398,1.775)]
  v,f=face_sheet(side,outline,wall=.005);install(f'Broad swept cheek band {side}',v,f)
  v,f=narrow_receiver(side);install(f'Forged orbital mounting plate {side}',v,f)
  outline=[(-.543,1.792),(-.552,1.800),(-.569,1.779),(-.578,1.741),(-.567,1.724),(-.556,1.741),(-.553,1.770)]
  v,f=face_sheet(side,outline,wall=.004);install(f'V24 anterior orbital root receiver {side}',v,f)
 # Seat the transverse jaw bridge on the actual paired midspan returns,
 # posterior to the hook cutting envelope; distal rails retain their seam.
 v,f=crown_sheet([(-.551,1.679,.059),(-.555,1.678,.060),(-.559,1.676,.058)]);install('Distal mandible bridge',v,f)
 # Lower the anterior roof into the diagonal brow. Retain the swept aft
 # crown courses exactly: this is a seated forehead correction, no curtain.
 specs=[('V27 fixed frontal cranial receiving return',(-.552,-.397,.80,math.pi-.80,.002,.88,0,.87,None)),('V27 dorsal swept cranial course 0',(-.550,-.354,1.12,2.02,.022,.43,.04,.72,.007))]
 for n,(a,b,lo,hi,off,tip,lean,rw,seat) in specs:
  v,f=skull_band(a,b,lo,hi,off,tip=tip,lean=lean,root_width=rw,seat_front=seat);install(n,v,f)
 # A finite annular receiving cup carries the smaller actual lens aperture.
 # Coordinates here are CURRENT native world metres (not pre-mass profile).
 # The old passive housing remains passive; sensing eligibility stays on
 # the unchanged independently owned Advanced optic mesh.
 def current_install(n,v,f):
  install(n,[(oldpivot+(Vector(p)-pivot)/factor) for p in v],f)
 for side in (-1,1):
  lens=bpy.data.objects[f'Seated Advanced optic {side}'];points=[lens.matrix_world@v.co for v in lens.data.vertices]
  cy=(min(p.y for p in points)+max(p.y for p in points))/2;cz=(min(p.z for p in points)+max(p.z for p in points))/2
  inv=lens.matrix_world.inverted();lens.data=lens.data.copy()
  for v,p in zip(lens.data.vertices,points):
   p.y=cy+(p.y-cy)*.67;p.z=cz+(p.z-cz)*.67;p.x-=side*.025;v.co=inv@p
  lens.data.update();changed.append(lens.name)
  # Closed swept cup wall, with a deliberate lip and recessed inner seat.
  profile=[(.158,.069),(.153,.071),(.137,.050),(.130,.042),(.125,.042),(.133,.052),(.149,.067),(.153,.067)]
  v=[];f=[];n=72
  for x,r in profile:
   for k in range(n):a=math.tau*k/n;v.append((side*x,cy+r*math.cos(a),cz+r*math.sin(a)))
  for j in range(len(profile)):
   for k in range(n):f.append((j*n+k,j*n+(k+1)%n,((j+1)%len(profile))*n+(k+1)%n,((j+1)%len(profile))*n+k))
  current_install(f'Seated passive optic housing {side}',v,f)
  for prefix,scale in [('Recessed orbital bearing',.87),('Orbital passive retaining race',.85)]:
   o=bpy.data.objects[f'{prefix} {side}'];inv=o.matrix_world.inverted();o.data=o.data.copy()
   for vert in o.data.vertices:
    p=o.matrix_world@vert.co;p.y=cy+(p.y-cy)*scale;p.z=cz+(p.z-cz)*scale;vert.co=inv@p
   o.data.update();changed.append(o.name)
 bpy.context.view_layer.update();front=None;frontname=None;dg=bpy.context.evaluated_depsgraph_get()
 for o in bpy.data.objects:
  if o.type=='MESH' and o.parent and o.parent.name=='upper-bill':
   ev=o.evaluated_get(dg);mesh=ev.to_mesh()
   for v in mesh.vertices:
    p=ev.matrix_world@v.co
    if front is None or p.y<front.y:front=p.copy();frontname=o.name
   ev.to_mesh_clear()
 for n in ('bill-contact','anchor-beak'):
  o=bpy.data.objects[n];m=o.matrix_world.copy();m.translation=front;o.matrix_world=m
 bpy.context.view_layer.update()
 assert protected=={n:snap(bpy.data.objects[n]) for n in protected}
 assert all(node(bpy.data.objects[n])==v for n,v in nodes.items() if n not in ('bill-contact','anchor-beak'))
 return {'region':'head-major-form','status':'Coarse visual proposal, likeness and movement HOLD','changedMeshes':changed,'added':[],'removed':[],'changedNodes':['bill-contact','anchor-beak'],'primaryPivotChanges':[],'technicalFitRepair':{'bridge':'Finite transverse connector reseated at actual paired jaw midspan, posterior to distal hook swept envelope; paired distal cutting rails retained.','originalDorsalCoursesRetainedExact':[1,2]},'outsideAndUnselectedMeshesExact':len(protected),'headRootAndCervicalInterfaceExact':True,'materialDefinitionsChanged':False,'eraEligibilityChanged':False,'billContactNativeWorld':list(front),'contactObject':frontname,'contactMethod':'minimum nativeY evaluated upper-bill surface vertex','maximumAuthoredWorldErrorM':max(errors),'transformContract':{'authoredOrigin':list(oldpivot),'currentOrigin':list(pivot),'bakedUniformHeadFactor':factor,'nodeScaling':'none','jawHinge':'unchanged'},'billProfile':BILL,'foreheadProfile':PROFILE,'opticContract':{'lensYZFactor':.67,'lensInwardSeatM':.025,'passiveCupOuterRadiusM':.071,'passiveCupInnerSeatRadiusM':.042,'raceYZFactor':.85,'bearingYZFactor':.87,'existingEraTagsPreserved':True},'limits':['First coarse visible candidate; no full collision or motion clearance claim.','Hidden receiving surfaces are proposals. Crown opening remains independent and requires fresh checks.']}
