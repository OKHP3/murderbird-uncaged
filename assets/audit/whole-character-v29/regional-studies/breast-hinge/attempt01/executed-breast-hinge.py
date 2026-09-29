"""V29 finite breast hinge fit; native metres, Z-up, -Y-forward.
Composable at the unchanged V28 breast pivot. No shell or rest-node changes.
Fixed clevis cheeks clear the rotating shaft/seat; returns join the moving
seat's outer wall, never begin as a solid member through the bearing bore.
"""
import bpy,bmesh,math,json
from mathutils import Vector,Matrix
ERAS='maker,mechanic,builder'
CHANGED=tuple(f'V23 breast {part} {side}' for part in ('opening bearing','hinge fixed fork','moving return') for side in (-1,1))
HINGE=(0,-.1576879918575287,.7646173238754272)
FIXED_X=(.133,.177);FIXED_WIDTH=.008;FIXED_BORE=.0095;FIXED_RADIUS=.025
MOVING_X=.155;MOVING_WIDTH=.014;MOVING_BORE=.0065;MOVING_RADIUS=.026

def props(o):return tuple((k,repr(o[k])) for k in sorted(o.keys()))
def node(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),tuple(tuple(r) for r in o.matrix_local),props(o),o.hide_viewport,o.hide_render,o.hide_select)
def mesh(o):return (node(o),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(e.vertices) for e in o.data.edges),tuple((tuple(p.vertices),p.material_index,p.use_smooth) for p in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),tuple((m.name,m.type) for m in o.modifiers))
def join(parts):
 vv=[];ff=[]
 for v,f in parts:
  n=len(vv);vv.extend(v);ff.extend(tuple(n+i for i in face) for face in f)
 return vv,ff

def annulus(x,cy,cz,ri,ro,width):
 n=96;v=[];f=[]
 for xx in (x-width/2,x+width/2):
  for r in (ri,ro):
   for j in range(n):a=math.tau*j/n;v.append((xx,cy+r*math.cos(a),cz+r*math.sin(a)))
 for j in range(n):
  k=(j+1)%n;f.extend([(j,k,n+k,n+j),(2*n+j,3*n+j,3*n+k,2*n+k),(j,2*n+j,2*n+k,k),(n+j,n+k,3*n+k,3*n+j)])
 return v,f

def sample(rows,t):
 u=max(0,min(1,t))*(len(rows)-1);i=min(int(u),len(rows)-2);s=u-i;a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
 return Vector([.5*(2*b[k]+(-a[k]+c[k])*s+(2*a[k]-5*b[k]+4*c[k]-d[k])*s*s+(-a[k]+3*b[k]-3*c[k]+d[k])*s*s*s) for k in range(3)])
def channel(rows,width,depth,wall,steps=30):
 cross=[(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(width/2-wall,depth/2),(width/2-wall,-depth/2+wall),(-width/2+wall,-depth/2+wall),(-width/2+wall,depth/2),(-width/2,depth/2)];v=[];f=[];n=len(cross)
 for i in range(steps+1):
  t=i/steps;p=sample(rows,t);axis=(sample(rows,min(1,t+.001))-sample(rows,max(0,t-.001))).normalized();x=Vector((1,0,0))
  if abs(axis.dot(x))>.9:x=Vector((0,1,0))
  b=axis.cross(x).normalized();a=b.cross(axis).normalized()
  for xx,yy in cross:v.append(p+a*xx+b*yy)
 for i in range(steps):
  for j in range(n):a=i*n+j;b=i*n+(j+1)%n;f.append((a,b,b+n,a+n))
 f.extend([tuple(reversed(range(n))),tuple(steps*n+j for j in range(n))]);return v,f

def apply():
 bpy.context.view_layer.update();pivot=bpy.data.objects['breastplate'];axis=pivot.matrix_world.to_3x3();assert max(abs(axis[r][c]-(1 if r==c else 0)) for r in range(3) for c in range(3))<1e-8
 assert (pivot.matrix_world.translation-Vector(HINGE)).length<1e-6
 assert all(n in bpy.data.objects for n in CHANGED);assert all(bpy.data.objects[n].get('exteriorEras')==ERAS for n in CHANGED)
 nodes={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'};protected={o.name:mesh(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in CHANGED};added=[];witness=[]
 c=pivot.matrix_world.translation.copy();cy,cz=c.y,c.z
 def install(name,geometry,owner=None,role='frame'):
  v,f=geometry
  if owner:
   assert name not in bpy.data.objects
   m=bpy.data.meshes.new(name+' finite metal');o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects[owner];o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4)
   o['region']='breast';o['surfaceRole']=role;o['exteriorEras']=ERAS;o['constructionClass']='inherited-passive';o['constructionOwner']=owner;o['proposal']=True
   o['constructionDescription']='Passive rotating annular breast seat; formed return joins outer metal wall. No motor or actuator.';o['geometryStatus']='V29 bounded hinge construction proposal; not engineering or artistic acceptance';materials=list(bpy.data.objects['V23 breast opening bearing 1'].data.materials);added.append(name)
  else:
   o=bpy.data.objects[name];materials=list(o.data.materials);m=bpy.data.meshes.new(name+' V29 fitted metal')
  assert o.parent.name in ['body','breastplate'];bpy.context.view_layer.update();inv=o.matrix_world.inverted();m.from_pydata([inv@Vector(p) for p in v],[],f);m.update()
  for a in materials:m.materials.append(a)
  bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  assert bm.calc_volume(signed=True)>0,name;bm.to_mesh(m);bm.free();o.data=m;o.modifiers.clear()
  for p in m.polygons:p.use_smooth=role=='bearing' and len(p.vertices)==4
  assert max((o.matrix_world@q.co-Vector(p)).length for q,p in zip(m.vertices,v))<1e-6
  witness.append({'name':name,'owner':o.parent.name,'evaluatedRestBoundsNative':[[min(p[k] for p in v),max(p[k] for p in v)] for k in range(3)],'singleRigidOwner':True,'finiteClosed':True})
 for side in (-1,1):
  # Two fixed bored cheeks straddle the separately moving central seat.
  rings=[annulus(side*x,cy,cz,FIXED_BORE,FIXED_RADIUS,FIXED_WIDTH) for x in FIXED_X]
  install(f'V23 breast opening bearing {side}',join(rings),role='bearing')
  # Aft/up clevis fingers start in annular metal, not at the shaft axis.
  # The bridge is radially outside the rotatingseat and front-return sweep.
  arms=[]
  for x in FIXED_X:
   arms.append(channel([(side*x,cy+.017,cz+.017),(side*x,cy+.030,cz+.032),(side*x,cy+.042,cz+.042)],.012,.012,.0035))
  arms.append(channel([(side*.133,cy+.042,cz+.042),(side*.155,cy+.042,cz+.042),(side*.177,cy+.042,cz+.042)],.018,.014,.004))
  arms.append(channel([(side*.177,cy+.042,cz+.042),(side*.177,-.076,.859),(side*.178,-.035,.910)],.022,.020,.005))
  install(f'V23 breast hinge fixed fork {side}',join(arms))
  install(f'V29 breast moving annular seat {side}',annulus(side*MOVING_X,cy,cz,MOVING_BORE,MOVING_RADIUS,MOVING_WIDTH),'breastplate','bearing')
  # Original distal return follows the door. Its first end is now rooted on
  # the seat's formed outside wall and remains forward of the fixed clevis.
  root=(side*.155,cy-.018,cz+.018)
  install(f'V23 breast moving return {side}',channel([root,(side*.128,-.177,.842),(side*.087,-.244,.922),(side*.108,-.330,1.095)],.024,.024,.005))
 bpy.context.view_layer.update();assert nodes=={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'};assert all(mesh(bpy.data.objects[n])==s for n,s in protected.items())
 return {'region':'breast-hinge','status':'Finite bored clevis/moving annular seats; discrete pose review required','changedMeshes':list(CHANGED),'added':added,'removed':[],'changedNodes':[],'checks':{'namedNodesExact':len(nodes),'protectedMeshesExact':len(protected),'breastExteriorShaftPivotExact':True,'noNewMaterialOrDrive':True},'construction':{'pivotNative':list(c),'axisNative':'x','fixedCheekCentersAbsX':list(FIXED_X),'fixedCheekWidthM':FIXED_WIDTH,'fixedBoreRadiusM':FIXED_BORE,'shaftRadiusM':.0065,'nominalShaftToFixedBoreRadialGapM':.003,'polygonMinimumBoreGapM':FIXED_BORE*math.cos(math.pi/96)-.0065,'movingSeatAbsX':MOVING_X,'movingSeatWidthM':MOVING_WIDTH,'movingSeatOuterRadiusM':MOVING_RADIUS,'movingSeatToFixedCheekAxialGapsM':[MOVING_X-MOVING_WIDTH/2-(FIXED_X[0]+FIXED_WIDTH/2),FIXED_X[1]-FIXED_WIDTH/2-(MOVING_X+MOVING_WIDTH/2)],'channelReturnWallM':.005,'clevisFingerWallM':.0035,'classification':'Passive all eras; fixedclevis body, annular movingseat/return breastplate. Originalshaft unchanged.'},'restWitnesses':witness,'limits':['No continuous motion or engineering clearance claim.','Unchanged upperbreast/neck rest intersections remain a separate root scope.','Same-owner seat/shaft/return and fork/cheek mating represent assembled construction, not independently articulating overlaps.']}
