"""Throat-seated02: separate compact actual-bow brackets and staggered exterior plates.
Input actual bill-relationship02. Geometry is a reconstruction proposal, not accepted engineering.
"""
import bpy,bmesh,math
from mathutils import Vector,Matrix
REMOVED=[f'V33 tapered throat cheek plate {s} {r} {i}'for s in(-1,0,1)for r in(0,1)for i in range(3)]
ADDED=[f'V38 {kind} {s} {i}'for kind in('seated throat guard','compact throat cover')for s in(-1,1)for i in range(3)]
def apply():
 bpy.context.view_layer.update();template=bpy.data.objects[REMOVED[0]];materials=list(template.data.materials);props=dict(template.items());records=[];lands=[];pads=[]
 def solid(name,inner,outer,nu,nv,rootfaces=None):
  count=len(inner);faces=[]
  for i in range(nu):
   for j in range(nv):
    k=i*(nv+1)+j;l=k+nv+1;faces.extend([(k,k+1,l+1),(k,l+1,l),(count+k,count+l+1,count+k+1),(count+k,count+l,count+l+1)])
  if rootfaces:
   faces=faces[4*2*nv:]
   for f in rootfaces:faces.extend([f,tuple(count+k for k in reversed(f))])
  border=list(range(nv+1))+[i*(nv+1)+nv for i in range(1,nu+1)]+[nu*(nv+1)+j for j in range(nv-1,-1,-1)]+[i*(nv+1)for i in range(nu-1,0,-1)]
  for i,k in enumerate(border):q=border[(i+1)%len(border)];faces.append((k,q,count+q,count+k))
  mesh=bpy.data.meshes.new(name+' finite construction');o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects['head'];o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update();inv=o.matrix_world.inverted();mesh.from_pydata([inv@q for q in outer+inner],[],faces);mesh.update()
  for mat in materials:mesh.materials.append(mat)
  for k,value in props.items():o[k]=value
  o['exteriorEras']='maker,mechanic,builder';o['constructionOwner']='head';o['constructionClass']='inherited-passive';o['surfaceRole']='plate';o['v38ThroatSeated']='Compact supported bracket and independently authored overlapping exterior; true finite receiving triangles, no head-neck rigid bridge'
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(mesh);bm.free()
  for q in mesh.polygons:q.use_smooth=False
  records.append({'name':name,'owner':'head','eras':'maker,mechanic,builder','materials':[m.name if m else None for m in materials],'vertices':len(mesh.vertices),'closedEdgeManifold':True,'positiveVolumeM3':volume,'lateralStockM':.003})
  return o
 for side in(-1,1):
  bow=bpy.data.objects[f'V31 passive cranial load bow {side}'];m=bow.data;m.calc_loop_triangles();v=[bow.matrix_world@p.co for p in m.vertices];assert len(v)==1122
  for course,start in enumerate([26,31,36]):
   name=f'V38 compact throat cover {side} {course}';nu,nv=20,40;inn=[];out=[]
   lo,hi=[(.08,1.88),(.17,2.02),(.94,2.62)][course];ztop=[1.583,1.636,1.686][course];height=[.097,.089,.089][course];rx=[.113,.126,.126][course];ry=[.086,.085,.080][course]
   for i in range(nu+1):
    t=i/nu
    for j in range(nv+1):
     u=j/nv;theta=lo+(hi-lo)*u;edge=.006*math.sin(math.pi*u)+.009*u
     # Broad curved throat faces follow the existing curved neck; distinct slanted short ends.
     z=ztop-height*t-edge*t;radx=rx-.013*t; rady=ry-.005*t
     q=Vector((side*radx*math.sin(theta),-.373-rady*math.cos(theta),z));inn.append(q);out.append(q+Vector((side*.003,0,0)))
   cover=solid(name,inn,out,nu,nv)
   # Full finite 2x6-cell receiving patch on the actual cover inner surface, chosen near bow root.
   target=min(range((nu+1)*(nv+1)),key=lambda k:(inn[k]-v[start*11+5]).length);ri=max(0,min(nu-2,target//(nv+1)));cj=max(0,min(nv-6,target%(nv+1)-3));end=[inn[(ri+i)*(nv+1)+cj+j]for i in range(3)for j in range(7)]
   guard=f'V38 seated throat guard {side} {course}';bi=[];bo=[];mapping={};gnu=7
   for i in range(gnu+1):
    for j in range(7):
     if i<=2:
      src=(start+2-i)*11+2+j;q=v[src];mapping[src]=i*7+j
     elif i>=5:q=end[(i-5)*7+j]-Vector((side*.003,0,0))
     else:
      t=(i-2)/3;q=v[start*11+2+j]*(1-t)+(end[j]-Vector((side*.003,0,0)))*t
     bi.append(q.copy());bo.append(q+Vector((side*.003,0,0)))
   actual=[];rootfaces=[]
   for tri in m.loop_triangles:
    if all(k in mapping for k in tri.vertices):
     f=tuple(mapping[k]for k in tri.vertices);rootfaces.append(f);actual.append({'receiverTriangle':tri.index,'sourceIndices':list(tri.vertices),'supportInnerIndices':[len(bi)+k for k in f]})
   assert len(actual)==24
   support=solid(guard,bi,bo,gnu,6,rootfaces)
   error=max((support.matrix_world@support.data.vertices[len(bi)+dest].co-v[src]).length for src,dest in mapping.items());assert error<3e-7
   pads.append({'support':guard,'receivingCover':name,'coverInnerGridRows':[ri,ri+2],'coverInnerGridColumns':[cj,cj+6],'coverInnerVertexIndices':[(nu+1)*(nv+1)+(ri+i)*(nv+1)+cj+j for i in range(3)for j in range(7)],'supportOuterVertexIndices':[(5+i)*7+j for i in range(3)for j in range(7)],'surfaceCorrespondence':'Exact 24 finite triangular cells with common grid diagonal; support outer surface meets cover inner surface. Side returns and neighbors separately screened.','nominalExtentM':[ (end[6]-end[0]).length,(end[14]-end[0]).length],'maxSurfaceVertexErrorM':max((bo[(5+i)*7+j]-end[i*7+j]).length for i in range(3)for j in range(7))})
   lands.append({'support':guard,'receiver':bow.name,'complete24TriangleRootCorrespondence':actual,'maxRootVertexErrorM':error,'stockM':.003,'fullFiniteRootCorrespondence':True,'limits':'Exact root triangles do not certify transition/edge volume or engineering attachment.'})
 for name in REMOVED:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 return {'changedMeshes':[],'changedNodes':[],'removedMeshes':REMOVED,'addedMeshes':ADDED,'watchMeshes':REMOVED+ADDED,'attachmentAndEraMap':records,'fullFiniteRootLands':lands,'fullFiniteCoverPads':pads,'construction':'Six compact bow-fitted brackets plus six independently authored broad curved staggered outer plates; removed18 unapproved source collar solids.','protected':'All40 cervical guards,4joint axes, controls, true bill/jaw/socket/optic/crown/body exact.','limits':['Designed finite root and cover-face contact is not universal stock/contact/motion acceptance.','Head-owned free cervical laps remain separate/sliding; no rigid bridge.','Exact outlines/stock/hidden supports are reconstruction proposals.']}
