"""Finite shoulder canopy attachment fit, composed after V34 shoulder envelope.

Only four receiving bows and two existing folded returns are reconstructed.
No pivot, circular journal, saddle, skin-field, metadata or material change.
"""
from pathlib import Path
import bpy,bmesh,math,runpy
from mathutils import Vector
ROOT=Path(globals().get('SOURCE_ROOT',Path(__file__).resolve().parents[2]))

def tube(points,r=.007,N=16):
 verts=[];faces=[]
 for i,p in enumerate(points):
  p=Vector(p);t=(Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)])).normalized();u=t.cross(Vector((1,0,0)))
  if u.length<.01:u=t.cross(Vector((0,1,0)))
  u.normalize();v=t.cross(u).normalized()
  for k in range(N):verts.append(p+r*(u*math.cos(k*math.tau/N)+v*math.sin(k*math.tau/N)))
 for j in range(len(points)-1):
  for k in range(N):a=j*N+k;b=j*N+(k+1)%N;faces.append((a,b,b+N,a+N))
 faces.extend([tuple(reversed(range(N))),tuple((len(points)-1)*N+k for k in range(N))]);return verts,faces

def apply():
 bpy.context.view_layer.update();h=runpy.run_path(str(ROOT/'scripts/regions/whole-character-v31-head-reconstruction.py'))
 names=[f'V28 {side} canopy receiving load bow {i}' for side in ('left','right') for i in (1,2)]+[f'V28 {side} canopy anterior folded return' for side in ('left','right')]
 assert all(n in bpy.data.objects for n in names)
 nodes={o.name:h['node'](o) for o in bpy.data.objects if o.type=='EMPTY'};protected={o.name:h['snap'](o) for o in bpy.data.objects if o.type=='MESH' and o.name not in names};notes=[]
 for label,side in [('left',1),('right',-1)]:
  pivot=bpy.data.objects[label+'-mantle'].matrix_world.translation.copy()
  assert abs(abs(pivot.x)-.266275)<1e-4 and abs(pivot.z-1.139462)<1e-4,'Expected fixed shoulder06 rest contract'
  for k in (1,2):
   o=bpy.data.objects[f'V28 {label} canopy receiving load bow {k}'];v=[o.matrix_world@v.co for v in o.data.vertices];assert len(v)==30,o.name
   start=sum(v[:10],Vector())/10;end=sum(v[-10:],Vector())/10
   # First transfer exits below the retained bonnet/saddle, then rises
   # outside their actual X maximum .3543m. The existing terminal canopy
   # seat stays exact; the journal root stays a finite welded root.
   dy=-.010 if k==1 else .010
   points=[start,Vector((side*.377,start.y+dy,start.z)),Vector((side*.382,start.y+dy,1.251)),end]
   verts,faces=tube(points);mesh=o.data.copy();mesh.clear_geometry();inv=o.matrix_world.inverted();mesh.from_pydata([inv@v for v in verts],[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free();o.data=mesh
   for p in mesh.polygons:p.use_smooth=len(p.vertices)==4
   notes.append({'name':o.name,'owner':o.parent.name,'pathNativeWorld':[list(p) for p in points],'radiusM':.007,'attachment':'Original circular journal root and canopy terminal centres retained. Horizontal root transfer below bonnet, followed by outboard rise beyond saddle.'})
  o=bpy.data.objects[f'V28 {label} canopy anterior folded return'];o.data=o.data.copy();o.data.update();normal=o.matrix_world.to_3x3().inverted().transposed();inv=o.matrix_world.inverted()
  old=[o.matrix_world@v.co for v in o.data.vertices];moved=[]
  for v,p in zip(o.data.vertices,old):
   n=(normal@v.normal).normalized()
   # Source normals are oriented outward, independently of side.
   if n.x*side<0:n=-n
   q=p-.006*n;v.co=inv@q;moved.append(q)
  o.data.update();notes.append({'name':o.name,'owner':o.parent.name,'method':'Existing formed folded return recessed6mm along its actual outward vertex normals; finite3.5mm Solidify wall retained. Receives first oblique course beneath outer leaf, no removed/hide faces.','maximumDisplacementM':max((a-b).length for a,b in zip(old,moved))})
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();finite=[]
 for name in names:
  o=bpy.data.objects[name];e=o.evaluated_get(dg);m=e.to_mesh();assert all(math.isfinite(c) for v in m.vertices for c in v.co),name;bm=bmesh.new();bm.from_mesh(m);assert all(x.is_manifold for x in bm.edges),name;vol=bm.calc_volume(signed=True);assert vol>0,name;bm.free();e.to_mesh_clear();finite.append({'name':name,'evaluatedClosed':True,'evaluatedPositiveVolumeM3':vol})
 assert all(h['node'](bpy.data.objects[n])==r for n,r in nodes.items());assert all(h['snap'](bpy.data.objects[n])==r for n,r in protected.items())
 return {'region':'shoulder-support-fit','changedMeshes':names,'changedNodes':[],'added':[],'removed':[],'nodesExact':len(nodes),'protectedMeshesExact':len(protected),'materialsChanged':False,'attachments':notes,'finiteSolids':finite,'sameOwnerConnections':'Bow original root is a proposed fixed welded transfer into its same-owner journal, bow pair root and canopy terminal liner. Such identities are reported separately by exact witnesses; none excluded from the screen.','limits':['Six-object technical fit; broader shoulder artist approval and continuous mechanics not established.']}
