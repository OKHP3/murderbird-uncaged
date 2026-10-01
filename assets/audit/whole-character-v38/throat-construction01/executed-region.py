"""Throat-construction01: fresh directional finite plates and two open receiving arches.
Actual bill-relationship02 input; existing four cervical chain, controls and true hardware exact.
No historical throat topology/receiving-strip constraint is retained.
"""
import bpy,bmesh,math,json
from mathutils import Vector,Matrix
NAMES=[f'V33 tapered throat cheek plate {s} {r} {i}'for s in(-1,0,1)for r in(0,1)for i in range(3)]
ADDED=['V38 lower cranial throat receiving arch','V38 upper cranial throat receiving arch']
WATCH=[f'V23 cervical {c} directional guard {i}'for c in range(1,5)for i in range(1,11)]+NAMES+ADDED
def archfield(a,row):
 z=(1.562 if row==0 else 1.624)+.006*math.sin(2*a)
 rx=.108 if row==0 else .127;ry=.090 if row==0 else .104
 return Vector((rx*math.sin(a),-.344-ry*math.cos(a),z))
def radial(a):return Vector((math.sin(a),-math.cos(a),0))
def closed_grid(outer,inner,nu,nv):
 n=len(outer);faces=[]
 for i in range(nu):
  for j in range(nv):k=i*(nv+1)+j;q=k+nv+1;faces.extend([(k,q,q+1,k+1),(n+k+1,n+q+1,n+q,n+k)])
 stride=nv+1;border=list(range(stride))+[i*stride+nv for i in range(1,nu+1)]+[nu*stride+j for j in range(nv-1,-1,-1)]+[i*stride for i in range(nu-1,0,-1)]
 for i,k in enumerate(border):q=border[(i+1)%len(border)];faces.append((k,q,n+q,n+k))
 return outer+inner,faces

def apply():
 bpy.context.view_layer.update();records=[];footprints=[]
 def install(name,verts,faces,new=False,template=None):
  if new:
   source=bpy.data.objects[template];o=bpy.data.objects.new(name,bpy.data.meshes.new(name));bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects['head'];o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4)
   for k,v in source.items():o[k]=v
   o['exteriorEras']='maker,mechanic,builder';o['constructionClass']='inherited-passive';o['surfaceRole']='frame';o['constructionOwner']='head';mats=list(source.data.materials)
  else:o=bpy.data.objects[name];mats=list(o.data.materials)
  bpy.context.view_layer.update();inv=o.matrix_world.inverted();mesh=bpy.data.meshes.new(name+' fresh finite topology');mesh.from_pydata([inv@p for p in verts],[],faces);mesh.update()
  for m in mats:mesh.materials.append(m)
  o.data=mesh;o.modifiers.clear();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  volume=bm.calc_volume(signed=True);assert volume>0,name;bm.to_mesh(mesh);bm.free()
  for p in mesh.polygons:p.use_smooth=False
  o['v38ThroatConstruction']='Fresh supported directional throat/nape proposal; no fixed-to-moving owner bridge'
  records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in mats],'vertices':len(mesh.vertices),'positiveVolumeM3':volume,'closedEdgeManifold':True,'rigidPassive':True})
  return o
 # Two narrow structural open-back arches. They are receiving frames below
 # the plates, not an exterior armored cuff; actual bow interfaces remain diagnostic.
 for row,name in enumerate(ADDED):
  nu,nv=112,2;outer=[];inner=[]
  for i in range(nu+1):
   a=-2.86+5.72*i/nu;p=archfield(a,row);n=radial(a)
   for j in range(nv+1):q=p+Vector((0,0,(j/nv-.5)*.012));outer.append(q);inner.append(q-n*.004)
  verts,faces=closed_grid(outer,inner,nu,nv);install(name,verts,faces,True,'V31 passive cranial load bow 1')
  for side in(-1,1):
   target=bpy.data.objects[f'V31 passive cranial load bow {side}'];m=target.data;m.calc_loop_triangles();v=[target.matrix_world@x.co for x in m.vertices];center=Vector((side*(.100 if row==0 else .120),-.379,1.566 if row==0 else 1.616));tris=[]
   for t in m.loop_triangles:
    p=[v[k]for k in t.vertices];c=sum(p,Vector())/3
    if abs(c.x-center.x)<.009 and abs(c.y-center.y)<.010 and abs(c.z-center.z)<.011:tris.append({'triangle':t.index,'vertices':[list(q)for q in p]})
   footprints.append({'arch':name,'receiver':target.name,'chosenActualFinitePatchTriangles':tris,'state':'Actual regional bow triangles surveyed over approximately18x20x22mm box; receiving arch-vs-bow surface union/interference NOT accepted from box or centroid alone.'})
 # Individually swept broad short plates, source root strips discarded.
 for side in(-1,0,1):
  bands=[(-.64,-.205),(-.20,.20),(.205,.64)]if side==0 else[(.66,1.36),(1.49,2.24),(2.30,2.99)]
  for row in(0,1):
   for col,(lo,hi)in enumerate(bands):
    name=f'V33 tapered throat cheek plate {side} {row} {col}';nu,nv=24,14;outer=[];inner=[]
    for i in range(nu+1):
     t=i/nu;length=(.080 if row==0 else .079)*([1.00,.80,.69][col]if side else [1.0,.96,.92][col]);narrow=1-.17*t*t
     for j in range(nv+1):
      u=j/nv;a=(lo+hi)/2+(u-.5)*(hi-lo)*narrow+.08*t
      if side==-1:a=-a
      root=archfield(a,row);n=radial(a)
      # Upper root inner skin begins at actual authored arch outer field.
      # Swept sides taper toward the neck rather than flare outward.
      q=root+n*(.0035-.012*t*t)+Vector((0,-.006*t,-length*t+.006*(u-.5)*t))
      q.z+=.002*math.sin(math.pi*u)*math.sin(math.pi*t)
      outer.append(q);inner.append(q-n*.0035)
    verts,faces=closed_grid(outer,inner,nu,nv);install(name,verts,faces)
    records[-1]['receivingMember']=ADDED[row];records[-1]['rootInterface']='Root inner boundary matches shared archfield at sampled angular points; full intervening finite faces still screened, not point-hit attachment acceptance.';records[-1]['nominalLateralStockM']=.0035;records[-1]['spanM']=length
 return {'changedMeshes':NAMES,'changedNodes':[],'addedMeshes':ADDED,'removedMeshes':[],'watchMeshes':WATCH,'attachmentAndEraMap':records,'actualBowFootprintSurvey':footprints,'construction':'18 fresh closed directional grids with short tapered down/back outline; two narrow head-owned passive open-back receiving arches; all40 cervical guards exact.','rigidVsFlexible':'Rigid head-owned passive all-era plates/frame; separate sliding cervical overlap, no joint bridge or early sensing.','confirmation':'Actual V31 load-bow surfaces surveyed; true articulation/control frames retained.','reconstruction':'Plate outlines, arches, stock and compatible interfaces remain authored mechanical proposals.','protected':'Bill/jaw/socket/optic/crown/body, all4 cervical joint axes/rest/endpoints and40guards exact.','limits':['Closed topology and positive volume do not prove self-fit or support.','Shared root field vertices do not prove finite face conformity; screen actual root/arch/bow triangles.','Arches terminate at open rear; nape plates are cantilevered from head support, not attached to moving neck.','No source throat topology/receiving band preservation assertion; prior folded approximation replaced.']}
