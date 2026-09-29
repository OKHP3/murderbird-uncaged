"""V37 connected compact shoulder construction; native metres, Z up/-Y front.
One authored contour, separate fixed root/moving mantle/elbow owners. No runtime
scale or joint changes. Existing journals/races/left stop remain real solids.
"""
import bpy,bmesh,math
from mathutils import Vector,Matrix
ERAS='maker,mechanic,builder'
OWNERS={'left-mantle','right-mantle','left-wing-shield','right-wing-shield'}
# t, lateral centre, fore/aft centre, height, outboard depth, fore/aft half-span
PROFILE=((0,.180,-.045,1.255,.065,.104),(.13,.240,-.018,1.303,.120,.165),
 (.32,.280,.018,1.242,.164,.194),(.55,.302,.058,1.111,.152,.181),
 (.80,.325,.105,.978,.122,.137),(1,.353,.152,.871,.075,.097),
 (1.12,.361,.182,.836,.053,.070))
COURSES=((.003,.230,5,-1.45,1.50,.036),(.165,.445,7,-1.44,1.49,.029),
 (.360,.650,7,-1.43,1.47,.022),(.580,.830,6,-1.36,1.40,.015),
 (.760,.920,5,-1.30,1.31,.008))
ELBOW_COURSES=((.820,1.010,4,-1.18,1.31,.021),(.975,1.105,4,-1.10,1.25,.013))

def sample(t):
 t=max(PROFILE[0][0],min(PROFILE[-1][0],t));i=next((i for i in range(len(PROFILE)-1) if PROFILE[i][0]<=t<=PROFILE[i+1][0]),len(PROFILE)-2)
 a,b=PROFILE[i],PROFILE[i+1];h=b[0]-a[0];u=(t-a[0])/h;out=[]
 for k in range(1,6):
  sec=[(PROFILE[j+1][k]-PROFILE[j][k])/(PROFILE[j+1][0]-PROFILE[j][0]) for j in range(len(PROFILE)-1)];sl=[sec[0]]
  for j in range(1,len(PROFILE)-1):sl.append(0 if sec[j-1]*sec[j]<=0 else 2*sec[j-1]*sec[j]/(sec[j-1]+sec[j]))
  sl.append(sec[-1]);out.append((2*u**3-3*u*u+1)*a[k]+(u**3-2*u*u+u)*h*sl[i]+(-2*u**3+3*u*u)*b[k]+(u**3-u*u)*h*sl[i+1])
 return out

def point(side,t,a):
 x,y,z,rx,ry=sample(t);return Vector((side*(x+rx*math.cos(a)),y+ry*math.sin(a),z+.026*math.cos(a)*math.exp(-((t-.13)/.26)**2)-.020*math.sin(a)*math.sin(math.pi*t/1.12)))
def normal(side,t,a):
 e=.0001;n=(point(side,t,a+e)-point(side,t,a-e)).cross(point(side,t+e,a)-point(side,t-e,a)).normalized()
 if n.dot(Vector((side*math.cos(a),math.sin(a),.2)))<0:n.negate()
 return n

def signature(o):
 return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),str([(m.type,m.name) for m in o.modifiers]),str(dict(o.items())))
def solid(name,owner,verts,faces,mat,role,construction):
 # Author absolute points only after synchronizing the parent's world matrix.
 bpy.context.view_layer.update();o=bpy.data.objects.new(name,bpy.data.meshes.new(name+' finite mesh'));bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects[owner];o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update();inv=o.matrix_world.inverted()
 o.data.from_pydata([inv@v for v in verts],[],faces);o.data.materials.append(mat);o.data.update()
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 assert bm.calc_volume(signed=True)>0,name
 bm.to_mesh(o.data);bm.free();o.data.update()
 for f in o.data.polygons:f.use_smooth=True
 o['region']='shoulder';o['surfaceRole']=role;o['exteriorEras']=ERAS;o['constructionClass']='proposed-passive';o['authoringRole']=construction;o['wallM']=.004
 assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
 return o

def sheet(name,owner,fn,mat,role='plate',rows=12,cols=8,wall=.004):
 vs=[];ns=[];fs=[]
 for j in range(rows+1):
  t=j/rows
  for k in range(cols+1):
   u=k/cols;p,n=fn(t,u);vs.append(p);ns.append(n)
 count=len(vs);vs += [p-n*wall for p,n in zip(vs,ns)]
 for j in range(rows):
  for k in range(cols):
   i=j*(cols+1)+k;q=(i,i+1,i+cols+2,i+cols+1);fs.extend((q,tuple(count+x for x in reversed(q))))
 edge=list(range(cols+1))+[j*(cols+1)+cols for j in range(1,rows+1)]+[rows*(cols+1)+k for k in range(cols-1,-1,-1)]+[j*(cols+1) for j in range(rows-1,0,-1)]
 for i,a in enumerate(edge):b=edge[(i+1)%len(edge)];fs.append((a,b,b+count,a+count))
 return solid(name,owner,vs,fs,mat,role,'Finite directional formed wall; one rigid owner; no cross-joint plate')

def field(name,owner,side,start,end,center,half,layer,mat,role='plate',sweep=.10):
 def fn(t,u):
  w=(.98-.36*t*t);a=center+sweep*t+half*w*(2*u-1)
  station=start+(end-start)*t+.026*(1-(2*u-1)**2)*t*t
  n=normal(side,station,a);return point(side,station,a)+n*layer,n
 return sheet(name,owner,fn,mat,role)

def rail(name,owner,points,mat,side):
 # Rectangular formed load member, substantial 11x13 mm section, connected path.
 vs=[];fs=[]
 for i,p in enumerate(points):
  tangent=Vector(points[min(len(points)-1,i+1)])-Vector(points[max(0,i-1)]);a=Vector((side,0,0));b=tangent.cross(a).normalized()
  for x,y in ((-1,-1),(1,-1),(1,1),(-1,1)):vs.append(Vector(p)+a*.0055*x+b*.0065*y)
 for i in range(len(points)-1):
  for k in range(4):a=i*4+k;b=i*4+(k+1)%4;fs.append((a,b,b+4,a+4))
 fs.extend(((3,2,1,0),tuple((len(points)-1)*4+k for k in range(4))))
 return solid(name,owner,vs,fs,mat,'frame','Connected passive formed load rail from actual journal seat to mantle field; no actuator')

def apply():
 bpy.context.view_layer.update()
 nodes={o.name:(o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),str(dict(o.items()))) for o in bpy.data.objects if o.type=='EMPTY'}
 allmeshes={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH'}
 mat=bpy.data.objects['V28 left canopy oblique course 1 plate 4'].data.materials[0]
 removed=[];added=[];joints={n:list(bpy.data.objects[n].matrix_world.translation) for n in OWNERS}
 # Bearing solids and primary shoulder->elbow load member are preserved.
 for o in list(bpy.data.objects):
  if o.type!='MESH' or not o.parent:continue
  scoped=o.parent.name in OWNERS
  fixed=o.name.startswith('V35 scapular receiving plate ')
  keep=o.get('surfaceRole')=='bearing' or 'swept upper wing load member' in o.name or 'travel stop' in o.name
  if fixed or (scoped and not keep):
   removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
 for side,label in ((1,'left'),(-1,'right')):
  owner=label+'-mantle';shield=label+'-wing-shield';root=Vector(joints[owner]);elbow=Vector(joints[shield])
  # Fixed inboard upper clevis/receiver remains inside the original races' X extent.
  def receiver(t,u):
   a=-.15+3.42*u;r=.080+.046*t;x=.160+.061*t
   n=Vector((side*.3,math.cos(a),math.sin(a))).normalized()
   return Vector((side*x,root.y+r*math.cos(a),root.z+r*math.sin(a))),n
  o=sheet(f'V37 {label} fixed scapular clevis hood','body',receiver,mat,'guard',rows=10,cols=28);added.append(o.name)
  # A short nape-side return receives the moving canopy without bridging owners.
  def bridge(t,u):
   p=Vector((side*(.153+.066*u),-.170+.135*t,1.224+.043*math.sin(math.pi*t*.72)+.005*u));return p,Vector((side*.18,-.12,1)).normalized()
  o=sheet(f'V37 {label} fixed upper scapular bridge','body',bridge,mat,'frame',rows=12,cols=8,wall=.006);added.append(o.name)
  # Formed annular shoulder fork clears the preserved races; exposed circular face remains.
  def bonnet(t,u):
   a=-.24+3.57*u;r=.081+.020*t;x=.332+.025*t
   n=Vector((side*.45,math.cos(a),math.sin(a))).normalized()
   return Vector((side*x,root.y+r*math.cos(a),root.z+r*math.sin(a))),n
  o=sheet(f'V37 {label} moving shoulder fork bonnet',owner,bonnet,mat,'guard',rows=8,cols=28,wall=.006);added.append(o.name)
  # Compact open liner is a support under the varied directional plate field.
  o=field(f'V37 {label} formed shoulder load liner',owner,side,.005,.855,.04,1.41,0,mat,'frame',sweep=.02);added.append(o.name)
  for row,(start,end,count,a,b,layer) in enumerate(COURSES):
   step=(b-a)/count
   for k in range(count):
    center=a+(k+.5)*step+(.16 if row%2 else -.08)*step
    o=field(f'V37 {label} shoulder course {row+1} plate {k+1}',owner,side,start+.008*math.sin(k*1.7+row),end-.020*k/max(1,count-1),center,step*.485,layer,mat,sweep=.24+.12*math.cos(k*.7+row));added.append(o.name)
  # Leading shield follows the front of the actual upper member, not a long feather.
  o=field(f'V37 {label} stout anterior shoulder guard',owner,side,.17,.87,-1.45,.15,.041,mat,'guard',sweep=.21);added.append(o.name)
  for row,(start,end,count,a,b,layer) in enumerate(ELBOW_COURSES):
   step=(b-a)/count
   for k in range(count):
    o=field(f'V37 {label} elbow course {row+1} plate {k+1}',shield,side,start,end-.017*k,a+(k+.5)*step+(row*.14)*step,step*.48,layer+.023,mat,sweep=.22);added.append(o.name)
  o=field(f'V37 {label} formed elbow shield liner',shield,side,.805,1.105,.08,1.25,.024,mat,'frame',sweep=.14);added.append(o.name)
  # Two short axial journal seats support the oblique child guard; no transverse cuff.
  for k,sg in enumerate((-1,1)):
   p0=Vector((side*(abs(elbow.x)+.012),elbow.y+sg*.031,elbow.z+.043))
   p1=point(side,.94,sg*.50)+normal(side,.94,sg*.50)*.025
   o=rail(f'V37 {label} elbow shield seat {k+1}',shield,[p0,p0.lerp(p1,.45),p1],mat,side);added.append(o.name)
  for k,a in enumerate((-.95,.85)):
   seat=point(side,.28,a);tip=point(side,.69,a);p0=Vector((side*.305,root.y,root.z-.015));p1=Vector((side*.353,root.y+.035*math.sin(a),root.z+.080))
   o=rail(f'V37 {label} canopy load bow {k+1}',owner,[p0,p1,seat,tip],mat,side);added.append(o.name)
 bpy.context.view_layer.update()
 assert nodes=={o.name:(o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),str(dict(o.items()))) for o in bpy.data.objects if o.type=='EMPTY'}
 for n,s in allmeshes.items():
  if n not in removed:assert signature(bpy.data.objects[n])==s,n
 return {'region':'connected shoulder assembly','status':'Coarse reference-led proposal; no art/motion acceptance','changedMeshes':[],'addedMeshes':added,'removedMeshes':removed,'changedNodes':[],'retainedJoints':joints,'preservedOriginalNodes':len(nodes),'preservedOutsideAndBearingMeshes':len(allmeshes)-len(removed),'eraEligibility':ERAS,'materialsChanged':False,'construction':'Fixed scapular clevis/bridge, moving annular fork and actual retained journal share root centre. One compact curved folded section carries varied short upper roots, stout diagonal mantle guards and shorter elbow shields; separate owners retain the shoulder/elbow interfaces.','shapeControls':{'profile':PROFILE,'shoulderCourses':COURSES,'elbowCourses':ELBOW_COURSES,'wallM':.004},'limits':['First neutral render gate before scoped rest/guard/thrust/Maker strict screen.','Authoring controls are qualitative reference-led proportions, not dimensions measured from unmatched perspective art.','Fixed bridge receiving geometry and plate roots remain proposed construction; no force or continuous clearance proof.']}
