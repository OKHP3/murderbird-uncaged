"""Short swept cranial leaves, authored in native metres about the head.

The July head and owner whole-bird control directional flow, not recovered
dimensions. Exact concealed backing and the count of plates are proposals.
Cranial-cover and fixed temporal plates change; all nodes/outside meshes exact.
"""
from pathlib import Path
import bpy,bmesh,math,runpy,hashlib
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2]

def finite_leaf(fn,nu,nv,wall,side=None):
 # Blender vectors store float32. The wider derivative stencil keeps a
 # finite pointed leaf's tiny terminal span above numerical cancellation.
 # Every resulting polygon is independently required to have finite area.
 vertices=[];normals=[]
 for i in range(nu+1):
  for j in range(nv+1):
   u=i/nu;v=j/nv;p=Vector(fn(u,v))
   du=Vector(fn(min(1,u+.001),v))-Vector(fn(max(0,u-.001),v));dv=Vector(fn(u,min(1,v+.001)))-Vector(fn(u,max(0,v-.001)))
   n=du.cross(dv);assert n.length>1e-14,(u,v,p);n.normalize()
   reference=Vector((side,0,0)) if side else Vector((p.x,0,1))
   if n.dot(reference)<0:n=-n
   vertices.append(p);normals.append(n)
 count=len(vertices);vertices += [p-wall*n for p,n in zip(vertices.copy(),normals)];faces=[];stride=nv+1
 for i in range(nu):
  for j in range(nv):
   a=i*stride+j;b=a+stride;faces.extend([(a,a+1,b+1,b),(count+b,count+b+1,count+a+1,count+a)])
 boundary=list(range(stride))+[i*stride+nv for i in range(1,nu+1)]+[nu*stride+j for j in range(nv-1,-1,-1)]+[i*stride for i in range(nu-1,0,-1)]
 for i,a in enumerate(boundary):b=boundary[(i+1)%len(boundary)];faces.append((a,b,count+b,count+a))
 return vertices,faces

def apply():
 helper=ROOT/'scripts/regions/whole-character-v31-head-reconstruction.py'
 assert hashlib.sha256(helper.read_bytes()).hexdigest()=='76c8bad1825ede7cf3fac5d068ab60f29a4e8e5059a78dfc5a9cabfd03d39022'
 h=runpy.run_path(str(helper));origin=bpy.data.objects['head'].matrix_world.translation.copy()
 old=[o for o in bpy.data.objects if o.name.startswith(('V32 swept crown plate ','V32 swept temporal plate '))]
 assert len(old)==31
 removed=[o.name for o in old];template={'props':dict(old[0].items()),'materials':list(old[0].data.materials)}
 protected={o.name:h['snap'](o) for o in bpy.data.objects if o.type=='MESH' and o.name not in removed}
 nodes={o.name:h['node'](o) for o in bpy.data.objects if o.type=='EMPTY'}
 for o in old:bpy.data.objects.remove(o,do_unlink=True)
 added=[];solids=[]
 def add(name,owner,verts,faces):
  mesh=bpy.data.meshes.new(name+' finite mesh');o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o)
  o.parent=bpy.data.objects[owner];o.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update();inv=o.matrix_world.inverted()
  mesh.from_pydata([inv@(origin+v) for v in verts],[],faces);mesh.update()
  for m in template['materials']:mesh.materials.append(m)
  for k,v in template['props'].items():o[k]=v
  o['constructionDescription']='V33 finite shorter swept leaf with formed shallow rib and directional lap';o['constructionOwner']=owner;o['proposal']=True
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(mesh);bm.free();mesh.update()
  assert all(p.area>1e-12 for p in mesh.polygons),name
  for p in mesh.polygons:p.use_smooth=len(p.vertices)==4
  added.append(name);solids.append({'name':name,'owner':owner,'closed':True,'positiveVolumeM3':volume})
 def lifted(y,theta,root_lift,free_lift,side=1):
  # Common skull surface normal: radial offsets become almost tangential
  # on the steep aft skull and let finite plate walls cross. The free edge
  # therefore stands off along this actual normal, not a global radius.
  z,rx,rz=h['section'](y)
  za,xa,ra=h['section'](y-.0001);zb,xb,rb=h['section'](y+.0001)
  dy=Vector(((xb-xa)/.0002*math.cos(theta),1,(zb-za)/.0002+(rb-ra)/.0002*math.sin(theta)))
  dt=Vector((-rx*math.sin(theta),0,rz*math.cos(theta)))
  normal=dy.cross(dt).normalized()
  base=Vector(((rx+root_lift)*math.cos(theta),y,z+(rz+root_lift)*math.sin(theta)))
  p=base+free_lift*normal;p.x*=side;return p
 # Progressively shorter courses follow the narrowing aft skull. The first
 # course sits aft of the retained brow clearance; succeeding courses lap
 # beneath the preceding free tips with actual radial separation.
 courses=[(-.281,-.089,range(7)),(-.174,-.003,range(7)),(-.092,.075,range(7)),(-.002,.137,range(1,6)),(.074,.166,range(2,5))]
 for row,(a,b,columns) in enumerate(courses):
  for col in columns:
   center=.980+col*.197
   # Symmetric underlying construction, modest row alternation. No random
   # damage, invented asymmetric height or generic whole-body scale field.
   root_lift=.007
   stagger=.007 if col%2 else -.004
   aa=a+stagger;bb=b+stagger*.5
   if row==0 and col in (0,1,5,6):aa=max(aa,-.252)
   width=.182 if col%2 else .186
   lean=(col-3)*.009
   def fn(u,v):
    shoulder=.78+.22*h['smooth'](u/.24)
    taper=1-.91*h['smooth']((u-.28)/.72)
    angle=center+lean*u+(v-.5)*width*shoulder*taper
    y=aa+(bb-aa)*u+.004*math.sin(math.pi*v)**2*u
    z,rx,rz=h['section'](y)
    # A shallow formed centre rib reinforces each rigid leaf; the free
    # margin stays finite and the back remains below the original contour.
    rib=.0025*math.sin(math.pi*v)**2*math.sin(math.pi*u)
    return lifted(y,angle,root_lift,.016*u+rib)
   verts,faces=finite_leaf(fn,nu=30,nv=14,wall=.0025)
   name=f'V33 swept cranial leaf {row} {col}'
   add(name,'cranial-cover',verts,faces)
 # Short fixed side leaves sweep around an exposed temple machinery bay.
 # Their roots are offset in both longitudinal and angular directions;
 # no uniform transverse scalp bands or new historical machinery are added.
 temporal=[(-.175,-.020,.70,.53,.27),(-.104,.065,.62,.43,.27),(-.018,.140,.49,.26,.29),(.045,.173,.26,-.04,.34),(-.004,.134,.05,-.18,.25),(-.025,.143,-.20,-.43,.25),(.033,.168,-.42,-.62,.25)]
 for side in (-1,1):
  for i,(a,b,first,last,width) in enumerate(temporal):
   def fn(u,v):
    theta=first+(last-first)*u+(v-.5)*width*(.80+.20*h['smooth'](u/.22))*(1-.90*h['smooth']((u-.28)/.72))
    y=a+(b-a)*u+.003*math.sin(math.pi*v)**2*u;z,rx,rz=h['section'](y)
    return lifted(y,theta,.010,.016*u,side)
   v,f=finite_leaf(fn,nu=30,nv=14,wall=.0025,side=side)
   add(f'V33 swept temporal leaf {side} {i}','head',v,f)
 bpy.context.view_layer.update()
 assert all(h['node'](bpy.data.objects[n])==r for n,r in nodes.items())
 assert all(h['snap'](bpy.data.objects[n])==r for n,r in protected.items())
 return {'region':'cranial-directional-flow','status':'Neutral construction proposal; fit and artistic acceptance separate','removed':removed,'added':added,'changedMeshes':[],'changedNodes':[],'finiteSolids':solids,'protectedMeshesExact':len(protected),'materialsChanged':False,'sourceLed':'Shorter aft-swept overlapping crown plates','reconstructed':'Exact counts, shallow ribs and hidden seating','limits':['No perspective dimensions claimed','Requires combined cap/face and same-owner leaf checks','No finish or optic changes']}
