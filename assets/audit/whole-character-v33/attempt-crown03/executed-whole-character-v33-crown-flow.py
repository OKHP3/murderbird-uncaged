"""Short swept cranial leaves, authored in native metres about the head.

The July head and owner whole-bird control directional flow, not recovered
dimensions. Exact concealed backing and the count of plates are proposals.
Only cranial-cover plates change; every rigid node and outside mesh is exact.
"""
from pathlib import Path
import bpy,bmesh,math,runpy,hashlib
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2]

def apply():
 helper=ROOT/'scripts/regions/whole-character-v31-head-reconstruction.py'
 assert hashlib.sha256(helper.read_bytes()).hexdigest()=='76c8bad1825ede7cf3fac5d068ab60f29a4e8e5059a78dfc5a9cabfd03d39022'
 h=runpy.run_path(str(helper));origin=bpy.data.objects['head'].matrix_world.translation.copy()
 old=[o for o in bpy.data.objects if o.name.startswith('V32 swept crown plate ')]
 assert len(old)==21
 removed=[o.name for o in old];template={'props':dict(old[0].items()),'materials':list(old[0].data.materials)}
 protected={o.name:h['snap'](o) for o in bpy.data.objects if o.type=='MESH' and o.name not in removed}
 nodes={o.name:h['node'](o) for o in bpy.data.objects if o.type=='EMPTY'}
 for o in old:bpy.data.objects.remove(o,do_unlink=True)
 added=[];solids=[]
 # Progressively shorter courses follow the narrowing aft skull. The first
 # course sits aft of the retained brow clearance; succeeding courses lap
 # beneath the preceding free tips with actual radial separation.
 courses=[(-.281,-.089,range(7)),(-.174,-.003,range(7)),(-.092,.075,range(7)),(-.002,.137,range(1,6)),(.074,.166,range(2,5))]
 for row,(a,b,columns) in enumerate(courses):
  for col in columns:
   center=.805+col*.255
   # Symmetric underlying construction, modest row alternation. No random
   # damage, invented asymmetric height or generic whole-body scale field.
   root_lift=.011
   if row==0 and col in (0,6):root_lift+=.017;center+=(.09 if col==0 else -.09)
   if row==1 and col in (0,6):root_lift+=.009
   stagger=.007 if col%2 else -.004
   aa=a+stagger;bb=b+stagger*.5
   if row==0 and col in (0,1,5,6):aa=max(aa,-.252)
   width=.239 if col%2 else .245
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
    r=root_lift+.019*h['smooth'](u/.75)+rib
    return Vector(((rx+r)*math.cos(angle),y,z+(rz+r)*math.sin(angle)))
   verts,faces=h['finite_sheet'](fn,nu=30,nv=14,wall=.0035)
   name=f'V33 swept cranial leaf {row} {col}'
   mesh=bpy.data.meshes.new(name+' finite mesh');o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o)
   o.parent=bpy.data.objects['cranial-cover'];o.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update();inv=o.matrix_world.inverted()
   mesh.from_pydata([inv@(origin+v) for v in verts],[],faces);mesh.update()
   for m in template['materials']:mesh.materials.append(m)
   for k,v in template['props'].items():o[k]=v
   o['constructionDescription']='V33 finite shorter swept leaf with formed shallow rib and directional lap';o['constructionOwner']='cranial-cover';o['proposal']=True
   bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
   if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
   volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(mesh);bm.free()
   for p in mesh.polygons:p.use_smooth=len(p.vertices)==4
   added.append(name);solids.append({'name':name,'owner':'cranial-cover','closed':True,'positiveVolumeM3':volume})
 bpy.context.view_layer.update()
 assert all(h['node'](bpy.data.objects[n])==r for n,r in nodes.items())
 assert all(h['snap'](bpy.data.objects[n])==r for n,r in protected.items())
 return {'region':'cranial-directional-flow','status':'Neutral construction proposal; fit and artistic acceptance separate','removed':removed,'added':added,'changedMeshes':[],'changedNodes':[],'finiteSolids':solids,'protectedMeshesExact':len(protected),'materialsChanged':False,'sourceLed':'Shorter aft-swept overlapping crown plates','reconstructed':'Exact counts, shallow ribs and hidden seating','limits':['No perspective dimensions claimed','Requires combined cap/face and same-owner leaf checks','No finish or optic changes']}
