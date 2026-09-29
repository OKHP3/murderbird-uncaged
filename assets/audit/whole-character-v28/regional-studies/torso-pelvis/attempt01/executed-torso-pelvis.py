"""V28 coherent coarse torso/pelvis construction on the held V27 form.
Owner whole-bird and scoped candidate03 guide silhouette; coordinates are
editable authored metre/Z-up/-Y-forward proposals, not raster metrology.
All pivots, legs/feet, head, wings and material definitions remain exact.
"""
import bpy,bmesh,math,json
from mathutils import Vector
PROFILE=[(.740,.126,-.085,.155),(.820,.146,-.185,.210),(.910,.190,-.265,.224),(1.020,.238,-.349,.223),(1.145,.273,-.400,.213),(1.255,.260,-.405,.173),(1.346,.187,-.365,.092)]
HIP=(.2315,.0506,.7878);HINGE=(0,-.15768799,.76461732)
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def section(z):
 for a,b in zip(PROFILE,PROFILE[1:]):
  if z<=b[0]:
   t=smooth((z-a[0])/(b[0]-a[0]));return [a[k]*(1-t)+b[k]*t for k in range(1,4)]
 return list(PROFILE[-1][1:])
def door_angle(z):return .34+.59*smooth((z-.820)/.210)
def point(z,theta,offset=0):
 rx,front,back=section(z);co=math.cos(theta);p=Vector((rx*math.sin(theta),(front if co>=0 else back)*abs(co),z));normal=Vector((math.sin(theta),-math.cos(theta),0));return p+normal*offset

def sheet(fn,nu=30,nv=20,wall=.005):
 v=[];ns=[]
 for i in range(nu+1):
  u=i/nu
  for j in range(nv+1):
   t=j/nv;p=fn(u,t);a=fn(min(1,u+.0001),t)-fn(max(0,u-.0001),t);b=fn(u,min(1,t+.0001))-fn(u,max(0,t-.0001));n=a.cross(b);assert n.length>1e-15;n.normalize()
   ref=Vector((p.x,p.y,0))
   if n.dot(ref)<0:n=-n
   v.append(p);ns.append(n)
 n=len(v);v +=[p-wall*q for p,q in zip(v.copy(),ns)];f=[];stride=nv+1
 for i in range(nu):
  for j in range(nv):
   a=i*stride+j;b=a+stride;f.extend([(a,a+1,b+1,b),(n+b,n+b+1,n+a+1,n+a)])
  a=i*stride;b=a+stride;f.append((b,a,n+a,n+b));a+=nv;b+=nv;f.append((a,b,n+b,n+a))
 for j in range(nv):
  f.append((j,j+1,n+j+1,n+j));a=nu*stride+j;f.append((a+1,a,n+a,n+a+1))
 return v,f

def panel(z0,z1,a0,a1,off=0,door=False,taper=1,slant=0):
 def fn(u,v):
  z=z0+(z1-z0)*u+slant*math.sin(math.pi*v)*smooth(u);angle=(a0+a1)/2+(v-.5)*(a1-a0)*(1-(1-taper)*smooth((u-.55)/.45));theta=angle*door_angle(z) if door else angle;return point(z,theta,off)
 return sheet(fn)

def sample(rows,t):
 u=max(0,min(1,t))*(len(rows)-1);i=min(int(u),len(rows)-2);s=u-i;a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
 return Vector([.5*(2*b[k]+(-a[k]+c[k])*s+(2*a[k]-5*b[k]+4*c[k]-d[k])*s*s+(-a[k]+3*b[k]-3*c[k]+d[k])*s*s*s) for k in range(3)])
def channel(rows,width=.033,depth=.028,wall=.006):
 # Actual closed C-section metal, visibly open channel rather than actuator.
 cross=[(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(width/2-wall,depth/2),(width/2-wall,-depth/2+wall),(-width/2+wall,-depth/2+wall),(-width/2+wall,depth/2),(-width/2,depth/2)];v=[];f=[];steps=30;n=len(cross)
 for i in range(steps+1):
  t=i/steps;p=sample(rows,t);tangent=(sample(rows,min(1,t+.001))-sample(rows,max(0,t-.001))).normalized();x=Vector((1,0,0))
  if abs(tangent.dot(x))>.9:x=Vector((0,1,0))
  b=tangent.cross(x).normalized();a=b.cross(tangent).normalized()
  for xx,yy in cross:v.append(p+a*xx+b*yy)
 for i in range(steps):
  for j in range(n):a=i*n+j;b=i*n+(j+1)%n;f.append((a,b,b+n,a+n))
 f.extend([tuple(reversed(range(n))),tuple(steps*n+j for j in range(n))]);return v,f

def hip_seat(side):
 # Spherical receiving sector centered on the actual multi-axis hip. Only
 # inboard hemisphere is occupied; no transverse-X sleeve around thigh.
 c=Vector((side*HIP[0],HIP[1],HIP[2]));nu=18;nv=64;v=[];f=[]
 for inner in (0,1):
  r=.131 if inner==0 else .125
  for i in range(nu+1):
   theta=.08+(.57-.08)*i/nu
   for j in range(nv):
    a=math.tau*j/nv;v.append(c+Vector((-side*r*math.cos(theta),r*math.sin(theta)*math.cos(a),r*math.sin(theta)*math.sin(a))))
 n=(nu+1)*nv
 for i in range(nu):
  for j in range(nv):a=i*nv+j;b=i*nv+(j+1)%nv;f.extend([(a,b,b+nv,a+nv),(n+a+nv,n+b+nv,n+b,n+a)])
 for j in range(nv):
  k=(j+1)%nv;f.append((j,k,n+k,n+j));a=nu*nv+j;b=nu*nv+k;f.append((b,a,n+a,n+b))
 return v,f

def props(o):return json.dumps(dict(o.items()),default=lambda x:list(x),sort_keys=True)
def snap(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(f.vertices) for f in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),props(o),o.hide_render,o.hide_viewport)
def node(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),props(o))
def apply():
 bpy.context.view_layer.update();assert (bpy.data.objects['left-thigh'].matrix_world.translation-Vector(HIP)).length<1e-6;assert (bpy.data.objects['breastplate'].matrix_world.translation-Vector(HINGE)).length<1e-6
 nodes={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'}
 removed=[o.name for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith(('Dorsal lap ','V24 breast course ','V23 fixed thoracic side ')) or o.name in ['Short dorsal shell','V24 continuous recessed breast backing','V24 lower side receiving liner -1','V24 lower side receiving liner 1'])]
 changed=['V23 thoracic formed rib -1','V23 thoracic formed rib 1','V23 lower sternal return','V23 breast moving return -1','V23 breast moving return 1'];owned=set(removed+changed);protected={o.name:snap(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in owned};added=[];witness=[]
 template=bpy.data.objects['V24 breast course 03 panel 03']
 matlist=list(template.data.materials);templateprops=dict(template.items())
 for name in removed:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 def install(name,v,f,owner=None,role='plate'):
  if owner:
   m=bpy.data.meshes.new(name+' V28 formed metal');o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects[owner]
   for k,x in templateprops.items():o[k]=x
   o['region']='breast' if owner=='breastplate' else 'torso-pelvis';o['surfaceRole']=role;o['exteriorEras']='maker,mechanic,builder';o['constructionClass']='inherited-passive';added.append(name)
  else:o=bpy.data.objects[name];m=bpy.data.meshes.new(name+' V28 shaped member')
  assert o.parent.name in ['body','breastplate'];bpy.context.view_layer.update();inv=o.matrix_world.inverted();m.from_pydata([inv@Vector(p) for p in v],[],f);m.update()
  for mat in (matlist if owner else list(o.data.materials)):m.materials.append(mat)
  bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  assert bm.calc_volume(signed=True)>0,name;bm.to_mesh(m);bm.free();o.data=m;o.modifiers.clear()
  for q in m.polygons:q.use_smooth=len(q.vertices)==4 and role not in ['frame']
  assert max((o.matrix_world@q.co-Vector(p)).length for q,p in zip(m.vertices,v))<1e-6
  witness.append({'name':name,'owner':o.parent.name,'classification':o.get('constructionClass','retained passive'),'bounds':[[min(p[k] for p in v) for k in range(3)],[max(p[k] for p in v) for k in range(3)]]})
 # Finite front door; entire moving skin stays forward of the retained axis.
 v,f=panel(1.346,.821,-1,1,-.010,door=True);install('V28 recessed shaped breast door',v,f,'breastplate','shell')
 for course,(a,b,off) in enumerate([(1.346,1.137,.018),(1.188,.976,.010),(1.025,.821,.002)]):
  for side in [-1,1]:
   lo,hi=(-.994,-.014) if side==-1 else (.014,.994);v,f=panel(a,b,lo,hi,off,door=True,taper=.96,slant=-.013);install(f'V28 longitudinal breast guard {course} {side}',v,f,'breastplate')
 # Purposeful fixed receiving sides and compact rear; lower width stays
 # inboard of moving hip journals, while front door remains independent.
 for side in [-1,1]:
  for i,(a,b) in enumerate([(1.333,1.095),(1.137,.871)]):
   lo,hi=(.96,1.71) if side==1 else (-1.71,-.96);v,f=panel(a,b,lo,hi,.002+(.008 if i==0 else 0),taper=.90,slant=-.012);install(f'V28 fixed flank receiving guard {side} {i}',v,f,'body')
 v,f=panel(1.329,.752,1.48,math.tau-1.48,-.014);install('V28 compact dorsal receiving liner',v,f,'body','recess')
 for i,(a,b,off) in enumerate([(1.330,1.075,.012),(1.119,.868,.004),(.912,.758,-.004)]):
  for side in [-1,1]:
   lo,hi=(1.50,3.12) if side==1 else (3.16,math.tau-1.50);v,f=panel(a,b,lo,hi,off,taper=.91,slant=-.014);install(f'V28 swept dorsal pelvic guard {side} {i}',v,f,'body')
 for side in [-1,1]:
  v,f=channel([(side*.155,-.157688,.764617),(side*.128,-.177,.842),(side*.087,-.244,.922),(side*.108,-.330,1.095)],.024,.024,.005);install(f'V23 breast moving return {side}',v,f,role='frame')
  # Forged ribs join retained shoulder/root loads to pelvic bridge.
  rows=[(side*.172,-.143,1.272),(side*.188,-.105,1.145),(side*.143,-.033,.970),(side*.104,.048,.826)];v,f=channel(rows,.038,.033,.0065);install(f'V23 thoracic formed rib {side}',v,f,role='frame')
  v,f=channel([(side*.10,.055,.825),(side*.115,.129,.899),(side*.16,.131,1.083),(side*.211,.081,1.225)],.037,.032,.006);install(f'V28 posterior pelvic load rail {side}',v,f,'body','frame')
  v,f=hip_seat(side);install(f'V28 spherical inboard hip receiving seat {side}',v,f,'body','bearing')
  v,f=channel([(side*.119,.055,.842),(side*.10,.06,.866),(side*.084,.113,.928)],.029,.026,.006);install(f'V28 hip seat upper load bow {side}',v,f,'body','frame')
  v,f=channel([(side*.119,-.005,.788),(side*.092,-.065,.836),(side*.09,-.136,.894)],.034,.030,.006);install(f'V28 sternal to hip load bow {side}',v,f,'body','frame')
 v,f=channel([(-.12,.079,.835),(-.054,.105,.852),(.054,.105,.852),(.12,.079,.835)],.038,.034,.007);install('V28 transverse pelvic load bridge',v,f,'body','frame')
 v,f=panel(.832,.758,-.68,.68,-.026);install('V23 lower sternal return',v,f)
 bpy.context.view_layer.update();assert nodes=={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'};assert protected=={n:snap(bpy.data.objects[n]) for n in protected}
 return {'region':'torso-pelvis','status':'Coarse connected torso/pelvic construction proposal; visual and movement acceptance pending','changedMeshes':changed,'added':added,'removed':removed,'ownedOriginals':sorted(owned),'changedNodes':[],'allNamedNodesExact':len(nodes),'protectedMeshSnapshotsExact':len(protected),'materialsAndEraEligibilityPreserved':True,'newPartsClassification':'All passive, maker/mechanic/builder; single rigid body or breastplate owner','authoredProfile':PROFILE,'hipCentersNative':[list(HIP),[-HIP[0],HIP[1],HIP[2]]],'hipReceivingInnerRadiusM':.125,'hipReceivingSectorRadians':[.08,.57],'doorAxisNative':HINGE,'boundWitnesses':witness,'limits':['Finite rigid coarse construction, not engineering or likeness acceptance.','Multi-axis leg and breast opening require discrete evaluated screens; no X sleeve or geometry hiding.']}
