"""V30 coarse breast form: continuous tapered mechanical mass and long guards.
Native Z-up/-Y-front; authored dimensions are construction proposals, not art
metrology. Changes body/breastplate exterior skins only, not hinge or machinery.
"""
import bpy,bmesh,math,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
PROFILE=((.785,.105,-.150,.148),(.845,.145,-.222,.181),(.950,.214,-.325,.211),(1.085,.277,-.413,.208),(1.205,.292,-.425,.185),(1.335,.274,-.386,.140),(1.380,.194,-.349,.107))
HINGE=(0,-.1576879918575287,.7646173238754272)

def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def section(z):
 z=max(PROFILE[0][0],min(PROFILE[-1][0],z));i=next((i for i in range(len(PROFILE)-1) if PROFILE[i][0]<=z<=PROFILE[i+1][0]),len(PROFILE)-2);a,b=PROFILE[i:i+2];u=(z-a[0])/(b[0]-a[0]);out=[]
 for k in range(1,4):
  slope=(b[k]-a[k])/(b[0]-a[0]);m0=slope if i==0 else (b[k]-PROFILE[i-1][k])/(b[0]-PROFILE[i-1][0]);m1=slope if i+2==len(PROFILE) else (PROFILE[i+2][k]-a[k])/(PROFILE[i+2][0]-a[0]);h=b[0]-a[0]
  out.append((2*u**3-3*u*u+1)*a[k]+(u**3-2*u*u+u)*h*m0+(-2*u**3+3*u*u)*b[k]+(u**3-u*u)*h*m1)
 return out

def door_angle(z):return .45+.45*ease((z-.825)/.225)
def point(z,angle,off=0):
 rx,front,back=section(z);co=math.cos(angle);p=Vector((rx*math.sin(angle),(front if co>=0 else back)*abs(co),z));return p+Vector((math.sin(angle),-math.cos(angle),0))*off

def solid_sheet(fn,nu=42,nv=18,wall=.005):
 verts=[];normals=[]
 for i in range(nu+1):
  u=i/nu
  for j in range(nv+1):
   t=j/nv;p=fn(u,t);a=fn(min(1,u+.0001),t)-fn(max(0,u-.0001),t);b=fn(u,min(1,t+.0001))-fn(u,max(0,t-.0001));n=a.cross(b);assert n.length>1e-15;n.normalize()
   if n.dot(Vector((p.x,p.y,0)))<0:n.negate()
   verts.append(p);normals.append(n)
 count=len(verts);verts +=[p-wall*n for p,n in zip(verts.copy(),normals)];faces=[];stride=nv+1
 for i in range(nu):
  for j in range(nv):
   a=i*stride+j;b=a+stride;faces.extend([(a,a+1,b+1,b),(count+b,count+b+1,count+a+1,count+a)])
  a=i*stride;b=a+stride;faces.append((b,a,count+a,count+b));a+=nv;b+=nv;faces.append((a,b,count+b,count+a))
 for j in range(nv):
  faces.append((j,j+1,count+j+1,count+j));a=nu*stride+j;faces.append((a+1,a,count+a,count+a+1))
 return verts,faces

def panel(z0,z1,a0,a1,off=0,door=False,taper=1,slant=0,side=0):
 def fn(u,v):
  z=z0+(z1-z0)*u+slant*math.sin(math.pi*v)*ease(u);angle=(a0+a1)/2+(v-.5)*(a1-a0)*(1-(1-taper)*ease(u));theta=angle*door_angle(z) if door else angle
  if side:theta=side*(door_angle(z)+.026+(1.72-door_angle(z)-.026)*v)
  return point(z,theta,off)
 return solid_sheet(fn)

def load_tab(points,width=.018,depth=.014,wall=.004):
 cross=[(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(width/2-wall,depth/2),(width/2-wall,-depth/2+wall),(-width/2+wall,-depth/2+wall),(-width/2+wall,depth/2),(-width/2,depth/2)];v=[];f=[];n=8
 for i,p in enumerate(points):
  axis=(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized();x=Vector((1,0,0));b=axis.cross(x).normalized();a=b.cross(axis).normalized()
  for xx,yy in cross:v.append(p+a*xx+b*yy)
 for i in range(len(points)-1):
  for j in range(n):a=i*n+j;b=i*n+(j+1)%n;f.append((a,b,b+n,a+n))
 f.extend([tuple(reversed(range(n))),tuple((len(points)-1)*n+j for j in range(n))]);return v,f

def evaluated_bvh(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.loop_triangles];e.to_mesh_clear();return BVHTree.FromPolygons(v,f,all_triangles=True)

def props(o):return json.dumps(dict(o.items()),sort_keys=True,default=lambda x:list(x))
def node(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),tuple(tuple(r) for r in o.matrix_local),props(o))
def mesh(o):return (node(o),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(f.vertices) for f in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),tuple((q.name,q.type) for q in o.modifiers),o.hide_render,o.hide_viewport)
def apply():
 bpy.context.view_layer.update();assert (bpy.data.objects['breastplate'].matrix_world.translation-Vector(HINGE)).length<1e-6;nodes={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'}
 removed=[o.name for o in bpy.data.objects if o.type=='MESH' and (o.name in ['V28 recessed shaped breast door','V28 compact dorsal receiving liner'] or o.name.startswith(('V28 longitudinal breast guard ','V28 fixed flank receiving guard ','V28 swept dorsal pelvic guard ')))];assert len(removed)==18,len(removed)
 protected={o.name:mesh(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in removed};template=bpy.data.objects['V28 longitudinal breast guard 0 1'];materials=list(template.data.materials);tags=dict(template.items());added=[];attachments=[]
 for name in removed:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 def install(name,geom,owner,role='plate'):
  v,f=geom;m=bpy.data.meshes.new(name+' V30 formed wall');o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects[owner];bpy.context.view_layer.update();inv=o.matrix_world.inverted();m.from_pydata([inv@p for p in v],[],f)
  for mat in ([bpy.data.materials['Neutral / frame']] if role=='frame' else materials):m.materials.append(mat)
  m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  assert bm.calc_volume(signed=True)>0,name;bm.to_mesh(m);bm.free()
  for p in m.polygons:p.use_smooth=len(p.vertices)==4
  for k,x in tags.items():o[k]=x
  o['region']='breast' if owner=='breastplate' else 'torso';o['surfaceRole']=role;o['exteriorEras']='maker,mechanic,builder';o['constructionClass']='proposed-passive';o['geometryStatus']='V30 coarse02 form proposal; source-supported hierarchy, likeness and fit pending';o['constructionOwner']=owner;o['wallM']=.005;added.append(name);return o
 install('V30 continuous tapered breast liner',panel(1.377,.809,-1,1,-.008,True),'breastplate','liner')
 install('V30 long central sternal keel',panel(1.361,.827,-.27,.27,.012,True,.72,-.008),'breastplate')
 for side in [-1,1]:
  lo,hi=(-.997,-.25) if side==-1 else (.25,.997)
  install(f'V30 long oblique breast cheek {side}',panel(1.374,.909,lo,hi,.011,True,.86,-.016),'breastplate')
  lo,hi=(-.995,-.12) if side==-1 else (.12,.995)
  install(f'V30 lower tapered sternal overlap {side}',panel(1.052,.813,lo,hi,.002,True,.64,-.014),'breastplate')
 install('V30 upper sternal receiving crown',panel(1.380,1.177,-.34,.34,.018,True,.86,-.009),'breastplate')
 for side in [-1,1]:install(f'V30 long fixed shoulder flank {side}',panel(1.374,.817,0,1,.003,side=side),'body')
 install('V30 continuous dorsal pelvic liner',panel(1.369,.793,1.48,math.tau-1.48,-.014),'body','liner')
 for side in [-1,1]:
  lo,hi=(1.55,3.12) if side==1 else (3.16,math.tau-1.55)
  install(f'V30 long swept dorsal cheek {side}',panel(1.367,.795,lo,hi,.006,taper=.90,slant=-.012),'body')
 # Receiving apertures retain the original actual shoulder/hip interfaces,
 # only cutting newly authored body skin. Machinery and pivots stay exact.
 apertures=[]
 for side,label in [(-1,'right'),(1,'left')]:
  c=bpy.data.objects[label+'-mantle'].matrix_world.translation.copy();N=96;v=[];f=[]
  for x in [side*.184,side*.345]:
   for j in range(N):a=math.tau*j/N;v.append((x,c.y+.112*math.cos(a),c.z+.112*math.sin(a)))
  for j in range(N):k=(j+1)%N;f.append((j,k,N+k,N+j))
  f.extend([tuple(reversed(range(N))),tuple(range(N,2*N))]);cm=bpy.data.meshes.new('V30 temporary receiving bore');cm.from_pydata(v,[],f);cm.update();bm=bmesh.new();bm.from_mesh(cm);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cm);bm.free();tool=bpy.data.objects.new(cm.name,cm);bpy.context.scene.collection.objects.link(tool)
  for name in [f'V30 long fixed shoulder flank {side}',f'V30 long swept dorsal cheek {side}','V30 continuous dorsal pelvic liner']:
   o=bpy.data.objects[name];q=o.modifiers.new('Finite original shoulder receiving envelope','BOOLEAN');q.operation='DIFFERENCE';q.solver='EXACT';q.object=tool
   with bpy.context.temp_override(object=o,active_object=o,selected_objects=[o],selected_editable_objects=[o]):bpy.ops.object.modifier_apply(modifier=q.name)
   apertures.append({'name':name,'joint':label+'-mantle','centerNative':list(c),'radiusM':.112})
  bpy.data.objects.remove(tool,do_unlink=True);bpy.data.meshes.remove(cm)
  hip=bpy.data.objects[label+'-thigh'].matrix_world.translation.copy();bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=.116,location=hip);tool=bpy.context.object;cm=tool.data
  for name in [f'V30 long swept dorsal cheek {side}','V30 continuous dorsal pelvic liner']:
   o=bpy.data.objects[name];q=o.modifiers.new('Finite original hip receiving envelope','BOOLEAN');q.operation='DIFFERENCE';q.solver='EXACT';q.object=tool
   with bpy.context.temp_override(object=o,active_object=o,selected_objects=[o],selected_editable_objects=[o]):bpy.ops.object.modifier_apply(modifier=q.name)
   apertures.append({'name':name,'joint':label+'-thigh','centerNative':list(hip),'radiusM':.116})
  bpy.data.objects.remove(tool,do_unlink=True);bpy.data.meshes.remove(cm)
 bpy.context.view_layer.update();liner=bpy.data.objects['V30 continuous tapered breast liner'];receiving=evaluated_bvh(liner)
 for side in [-1,1]:
  o=bpy.data.objects[f'V23 breast moving return {side}'];assert len(o.data.vertices)==248
  seat=sum([o.matrix_world@o.data.vertices[30*8+j].co for j in [0,1,4,5]],Vector())/4
  endpoint,_,_,distance=receiving.find_nearest(seat);name=f'V30 breast liner receiving tab {side}'
  install(name,load_tab([seat,seat.lerp(endpoint,.5),endpoint]),'breastplate','frame')
  attachments.append({'newMember':name,'preservedMember':o.name,'owner':'breastplate','skin':'V30 continuous tapered breast liner','actualRetainedRearWebSeatNative':list(seat),'actualLinerSeatNative':list(endpoint),'tabCenterlineLengthM':distance,'linerCenterSurfaceDistanceM':receiving.find_nearest(endpoint)[3],'construction':'Finite C-section passive receiving tab, one rigid breastplate owner; original return and hinge exact','limits':'Geometric endpoint seating only, not engineering attachment/physics acceptance'})
 bpy.context.view_layer.update();assert nodes=={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'};assert all(mesh(bpy.data.objects[n])==s for n,s in protected.items())
 return {'region':'breast/body contour and exterior panel hierarchy','study':'V30 coarse02 appearance gate before fit screening','status':'Inferred editable structural exterior proposal; no material finish or likeness/engineering acceptance','changedMeshes':[],'removed':removed,'added':added,'changedNodes':[],'namedNodesExact':len(nodes),'outsideMeshesExact':len(protected),'profile':PROFILE,'breastAxisNative':HINGE,'attachments':attachments,'receivingApertures':apertures,'construction':'Continuous tapered breast/shoulder envelope, long central keel and paired oblique cheek plates with local lower sternal overlaps; long fixed flanks connect the shoulder reading into a compact tapered dorsal mass. Broad horizontal pillow courses removed.','preserved':['V29 breast fixed/moving annular seats and forks, shaft, all frame members','Original breast axis/panel opening owner and named rig','All head/neck/wing/journal/leg/foot geometry and material definitions','Original era machinery; new skins passive all three eras'],'limits':['Authored coarse profile and panel hierarchy from reference appearance, not dimensional metrology','First rendered macroform gate precedes fit/attachment screen; no continuous clearance or physics claim']}
