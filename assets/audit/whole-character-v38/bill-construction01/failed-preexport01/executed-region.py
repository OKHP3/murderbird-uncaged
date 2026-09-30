"""Bill-construction01: paired curved rigid bill and narrowed mouth return.
Actual breast-course02. Original root/jaw/socket and era identities retained;
actual contact triangles and bill-contact marker updated together.
"""
import bpy,bmesh,math,json
from mathutils import Vector
from mathutils.kdtree import KDTree
ALLOWED=[f'V32 returned upper bill course {i}'for i in range(3)]+['V32 formed mandibular bowl']+[f'V33 formed lower cheek receiver {s} {i}'for s in(-1,1)for i in range(2)]
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def curve(rows,t):
 q=max(0,min(1,t))*(len(rows)-1);i=min(int(q),len(rows)-2);u=q-i;a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
 return b+.5*((c-a)*u+(2*a-5*b+4*c-d)*u*u+(-a+3*b-3*c+d)*u*u*u)
def contact():
 bpy.context.view_layer.update();pts=[(o.name,o.matrix_world@v.co)for o in bpy.data.objects if o.type=='MESH'and o.parent and o.parent.name=='upper-bill'for v in o.data.vertices];lead=min(pts,key=lambda p:p[1].y)
 return {'leadingObject':lead[0],'leadingPointNativeXYZ':list(lead[1]),'actualTriangleVertexBounds':[[min(p[k]for _,p in pts),max(p[k]for _,p in pts)]for k in range(3)]}
def finite_pairs(o,p):
 normals=[(o.matrix_world.to_3x3().inverted().transposed()@v.normal).normalized()for v in o.data.vertices];tree=KDTree(len(p))
 for i,q in enumerate(p):tree.insert(q,i)
 tree.balance();candidates=[]
 for i,q in enumerate(p):
  for a,j,d in tree.find_range(q,.010):
   if j>i and d>.0015 and normals[i].dot(normals[j])<-.25:candidates.append((d,i,j))
 used=set();pairs=[]
 for _,i,j in sorted(candidates):
  if i not in used and j not in used:used.update((i,j));pairs.append((i,j))
 return pairs
def apply():
 bpy.context.view_layer.update();before=contact();records=[];eye=Vector((0,-.577800006,1.725484014));jaw=bpy.data.objects['jaw'];socket=Vector((-.1276221073,-.1072232199,.0101978016));bowl=bpy.data.objects['V32 formed mandibular bowl'];socketworld=jaw.matrix_world@socket
 for name in ALLOWED:
  o=bpy.data.objects[name];matrix=o.matrix_world.copy();inv=matrix.inverted();old=[v.co.copy()for v in o.data.vertices];world=[matrix@p for p in old]
  if name.startswith('V32 returned'):
   course=int(name[-1]);half=len(world)//2 if course<2 else len(world);rings=half//10;nu,nv=48,24;outer=[];inner=[]
   rows=[world[i*10:(i+1)*10]for i in range(rings)];inside=[world[half+i*10:half+(i+1)*10]for i in range(rings)]if course<2 else None
   for i in range(nu+1):
    u=i/nu;q=(course+u)/3;ring=[curve([r[k]for r in rows],u)for k in range(10)];center=(ring[0]+ring[5])*.5;axis=(ring[0]-ring[5])*.5;axis*=1-.25*math.sin(math.pi*q)**2;width=max(abs(p.x)for p in ring)*(1-.12*math.sin(math.pi*q)**2-.25*ease((q-.70)/.30));shift=Vector((0,.008*math.sin(math.pi*q)**2,.030*ease((q-.65)/.35)))
    for k in range(nv):
     theta=math.tau*k/nv;oldk=k/nv*10;ix=int(oldk);f=oldk-ix;raw=ring[ix%10]*(1-f)+ring[(ix+1)%10]*f
     formed=center+axis*math.cos(theta)+Vector((width*math.sin(theta),0,0))+shift
     blend=ease(u/.16)if course==0 else 1;point=raw*(1-blend)+formed*blend;outer.append(point)
     if inside:
      innerring=[curve([r[j]for r in inside],u)for j in range(10)];offset=(innerring[ix%10]-ring[ix%10])*(1-f)+(innerring[(ix+1)%10]-ring[(ix+1)%10])*f;inner.append(point+offset)
   verts=outer+inner;faces=[];count=len(outer)
   for i in range(nu):
    for k in range(nv):a=i*nv+k;b=i*nv+(k+1)%nv;faces.append((a,b,b+nv,a+nv));
    if inside:
     for k in range(nv):a=count+i*nv+k;b=count+i*nv+(k+1)%nv;faces.append((a+nv,b+nv,b,a))
   if inside:
    for k in range(nv):n=(k+1)%nv;faces.extend([(n,k,count+k,count+n),(nu*nv+k,nu*nv+n,count+nu*nv+n,count+nu*nv+k)])
   else:faces.extend([tuple(reversed(range(nv))),tuple(nu*nv+k for k in range(nv))])
   mesh=bpy.data.meshes.new(name+' smoothly sampled formed shell');mesh.from_pydata([inv@p for p in verts],[],faces);mesh.update()
   for mat in o.data.materials:mesh.materials.append(mat)
   o.data=mesh;method='48 smoothly curved profile intervals,24 formed section sides; substantial root section retained, middle depth reduced25%, tapered width, hook terminal raised30mm. Inherited paired stock vectors interpolated, no zero-thickness skin.';pairs=[];stockerror=None
  else:
   pairs=finite_pairs(o,world);fixed=set();moves={};o.data=o.data.copy()
   for i,p in enumerate(world):
    if name.endswith('bowl'):
     d=(p-socketworld).length;w=ease((-.565-p.y)/.145)*(1-ease((.055-d)/.03));moves[i]=Vector((-p.x*.32*w,-.025*w,.065*w))
     if d<.055 or p.y>=-.565:fixed.add(i);moves[i]=Vector()
    else:
     r=math.hypot(p.y-eye.y,p.z-eye.z);jr=(p-jaw.matrix_world.translation).length;w=ease((r-.079)/.040)*ease((jr-.042)/.035)*ease((eye.z-p.z-.010)/.050);moves[i]=Vector((0,-.010*w,-.008*w))
     if r<=.079 or jr<=.042:fixed.add(i);moves[i]=Vector()
   for i,j in pairs:
    move=Vector()if i in fixed or j in fixed else(moves[i]+moves[j])*.5;moves[i]=moves[j]=move
   for i,p in enumerate(world):
    if moves[i].length:o.data.vertices[i].co=inv@(p+moves[i])
   assert all(o.data.vertices[i].co==old[i]for i in fixed);new=[matrix@v.co for v in o.data.vertices];stockerror=max(((new[i]-new[j])-(world[i]-world[j])).length for i,j in pairs)if pairs else0;assert stockerror<3e-7
   method='Distal mandibular return raised65mm/swept forward25mm/narrowed32% with exact55mm socket neighborhood; recovered paired stock moved together.'if name.endswith('bowl')else'Coordinated10mm anterior/8mm lower outer cheek root return; exact optic/journal protected zones.'
  o.data.update();bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  vol=bm.calc_volume(signed=True);assert vol>0;bm.to_mesh(o.data);bm.free()
  for p in o.data.polygons:p.use_smooth=True
  o['v38BillConstruction']='Paired smoothly sampled curved bill/compact narrowed mandibular opening; proposal'
  records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in o.data.materials],'method':method,'closedEdgeManifold':True,'positiveVolumeM3':vol,'recoveredStockPairs':pairs,'stockVectorErrorM':stockerror,'sourceVertexCount':len(old),'candidateVertexCount':len(o.data.vertices)})
 after=contact();marker=bpy.data.objects['bill-contact'];oldmatrix=[list(r)for r in marker.matrix_world];matrix=marker.matrix_world.copy();matrix.translation=Vector(after['leadingPointNativeXYZ']);marker.matrix_world=matrix;bpy.context.view_layer.update()
 return {'changedMeshes':ALLOWED,'changedNodes':['bill-contact'],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':records,'contactBefore':before,'contactAfter':after,'contactMarkerBeforeWorld':oldmatrix,'contactMarkerAfterWorld':[list(r)for r in marker.matrix_world],'contactLandmarksChanged':True,'contactMeaning':'bill-contact placed on actual leading upper-bill surface vertex; solver derives actual exported triangles, no hidden fixed-tip substitute.','confirmation':'ActualJuly HEADONLY constructed curved hook/narrow paired mouth, Master03/Maker-clean wholebird crosscheck.','reconstruction':'Exact course profiles/stock/root geometry authored; no art dimensions/engineering acceptance.','limits':['Unmatched mandible stock and interpolated upper-shell stock not full manufacturing thickness proof.','Jaw/socket/optic/cover pivots and body unchanged; targeted contact/jaw checks separate after visualgate.']}
