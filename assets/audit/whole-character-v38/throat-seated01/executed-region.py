"""Throat-seated01 from actual bill-relationship02: six fitted directional rigid guards.
Root inner surfaces copy actual finite V31 bow triangles, not an analytic ring or ray proxy.
"""
import bpy,bmesh,math
from mathutils import Vector,Matrix
REMOVED=[f'V33 tapered throat cheek plate {s} {r} {i}'for s in(-1,0,1)for r in(0,1)for i in range(3)]
ADDED=[f'V38 seated throat guard {s} {i}'for s in(-1,1)for i in range(3)]
def smooth(t):return t*t*(3-2*t)
def apply():
 bpy.context.view_layer.update();template=bpy.data.objects[REMOVED[0]];materials=list(template.data.materials);props=dict(template.items());records=[];lands=[]
 for side in(-1,1):
  bow=bpy.data.objects[f'V31 passive cranial load bow {side}'];m=bow.data;m.calc_loop_triangles();v=[bow.matrix_world@p.co for p in m.vertices];assert len(v)==1122
  for course,start in enumerate([26,31,36]):
   name=f'V38 seated throat guard {side} {course}';outer=[];inner=[];mapping={};nu,nv=22,6
   for i in range(nu+1):
    for j in range(nv+1):
     u=j/nv
     if i<=2:
      source_index=(start+2-i)*11+2+j;q=v[source_index].copy();mapping[source_index]=i*7+j;wall=.003
     else:
      root=v[start*11+2+j];t=(i-2)/(nu-2);blend=smooth(t)
      if course==0:end=Vector((side*(.106-.096*u),-.380-.068*u,1.481-.018*u+.006*math.sin(math.pi*u)))
      elif course==1:end=Vector((side*(.112-.035*u),-.283-.076*u,1.535-.017*u+.005*math.sin(math.pi*u)))
      else:end=Vector((side*(.094-.079*u),-.231-.057*u,1.506+.010*u+.005*math.sin(math.pi*u)))
      q=root*(1-blend)+end*blend;q.x+=side*.010*math.sin(math.pi*t);q.y=root.y+(end.y-root.y)*(t**.72);q.z=root.z+(end.z-root.z)*t
      # Short broad returns taper smoothly; lateral stock is single valued.
      wall=.003
     inner.append(q);outer.append(q+Vector((side*wall,0,0)))
   count=len(inner);faces=[];actual=[]
   # Preserve the actual receiver triangulation over the ENTIRE root patch.
   for triangle in m.loop_triangles:
    ids=tuple(triangle.vertices)
    if all(k in mapping for k in ids):
     f=tuple(mapping[k]for k in ids);faces.append(f);faces.append(tuple(count+k for k in reversed(f)));actual.append({'receiverTriangle':triangle.index,'sourceVertexIndices':list(ids),'guardInnerIndices':[count+k for k in f]})
   assert len(actual)==24,(name,len(actual))
   for i in range(2,nu):
    for j in range(nv):k=i*7+j;l=k+7;faces.extend([(k,k+1,l+1),(k,l+1,l),(count+k,count+l+1,count+k+1),(count+k,count+l,count+l+1)])
   border=list(range(7))+[i*7+6 for i in range(1,nu+1)]+[nu*7+j for j in range(5,-1,-1)]+[i*7 for i in range(nu-1,0,-1)]
   for i,k in enumerate(border):q=border[(i+1)%len(border)];faces.append((k,q,count+q,count+k))
   mesh=bpy.data.meshes.new(name+' actual seat+connected directional finite plate');o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects['head'];o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update();inv=o.matrix_world.inverted();mesh.from_pydata([inv@q for q in outer+inner],[],faces);mesh.update()
   for mat in materials:mesh.materials.append(mat)
   for k,value in props.items():o[k]=value
   o['exteriorEras']='maker,mechanic,builder';o['constructionOwner']='head';o['constructionClass']='inherited-passive';o['surfaceRole']='plate';o['v38ThroatSeated']='Six reconstructed headowned short guards; integral rootreturn copies finite bow receiving triangles; separate moving cervical overlap'
   bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
   if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
   volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(mesh);bm.free()
   for p in mesh.polygons:p.use_smooth=False
   err=max((o.matrix_world@mesh.vertices[count+dest].co-v[src]).length for src,dest in mapping.items());assert err<3e-7
   lands.append({'guard':name,'receiver':bow.name,'actualReceiverRows':[start,start+2],'actualReceiverColumns':[2,8],'fullFiniteCorrespondence':actual,'maxRootVertexErrorM':err,'innerLandIndices':[count+i for i in range(21)],'completeReceiverTriangulationCopied':True,'receivingState':'Exact finite innerroot correspondence, but interobject/support/stock compatibility still separately screened. Not a centroid/ray/bounds attachment PASS.'})
   records.append({'name':name,'owner':'head','materialNames':[q.name if q else None for q in materials],'eras':'maker,mechanic,builder','vertices':len(mesh.vertices),'closedEdgeManifold':True,'positiveVolumeM3':volume,'nominalLateralStockM':.003,'rigidPassive':True,'rootReceiver':bow.name,'attachment':'Integral continuous finite return from actual24-triangle land into plate; no unsupported separate arch/cage.','movement':'Head-owned; moves with receiver bow. Free lap to cervical-upper is separate/sliding, not a rigid head-neck bridge.'})
 for name in REMOVED:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 return {'changedMeshes':[],'changedNodes':[],'removedMeshes':REMOVED,'addedMeshes':ADDED,'watchMeshes':REMOVED+ADDED,'attachmentAndEraMap':records,'fullFiniteRootLands':lands,'construction':'18 unapproved folded source collar solids removed; six broad short staggered guards with individually fitted connected roots, three per side. No ring arches.','rigidVsFlexible':'Rigid head-owned passive plates/supports, no flexible tissue or earlypoweredhardware.','confirmation':'Actual sourcebow1122vertex grid and24 receivingtriangles perplate surveyed/copied; fullpolygon support check follows before interpretation.','reconstruction':'Six plate outlines/hidden returns/3mmstock are authored proposals, not art dimensions orengineeringacceptance.','protected':'All40 cervical guards, all4joint frames/control endpoints, truebill/jaw/socket/optic/crown/body/wing asymmetry and12sourceprofiles exact.','limits':['Finite correspondence does not waive strict intersections in outgoing return, neighboring plate, hardware or posedguard.','No continuous movement/containment/engineering/ownerlikeness acceptance.']}
