"""Supported02: disjoint original upper-throat receiving lands and two explicit shared bow-rooted carriers."""
import bpy,bmesh,math,json
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
LOWER=[f'V33 tapered throat cheek plate {s} 0 {c}'for s in(-1,0,1)for c in range(3)]
CARRIERS=[f'V38 shared head throat carrier {s}'for s in(-1,1)]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def closed(name,verts,faces,materials,owner,props):
 inv=owner.matrix_world.inverted();m=bpy.data.meshes.new(name+' finite supported stock');m.from_pydata([inv@p for p in verts],[],faces);m.update()
 for mat in materials:m.materials.append(mat)
 o=bpy.data.objects.get(name)
 if o:o.data=m;o.modifiers.clear()
 else:
  o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);o.parent=owner;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4)
 for k,v in props.items():o[k]=v
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(m);bm.free()
 for f in m.polygons:f.use_smooth=False
 return o,volume
def paired(outer,inner,quads):
 n=len(outer);faces=quads+[tuple(n+i for i in reversed(f))for f in quads];edges={}
 for f in quads:
  for a,b in zip(f,f[1:]+f[:1]):edges.setdefault(tuple(sorted((a,b))),[]).append((a,b))
 for e in edges.values():
  if len(e)==1:a,b=e[0];faces.append((a,b,n+b,n+a))
 return outer+inner,faces
def patch(source,rows,cols,inner=False,wall=.009,outward=True):
 source.data.calc_loop_triangles();v=[source.matrix_world@p.co for p in source.data.vertices];half=len(v)//2;stride=11 if half==561 else 15;inds=[row*stride+col for row in rows for col in cols];points=[v[i+half]if inner else v[i]for i in inds];norm=[(v[i]-v[i+half]).normalized()for i in inds];mapping={i:k for k,i in enumerate(inds)};tri=[];proof=[]
 for t in source.data.loop_triangles:
  actual=[i-half for i in t.vertices]if inner else list(t.vertices)
  if inner and not all(i>=half for i in t.vertices):continue
  if all(i in mapping for i in actual):tri.append(tuple(mapping[i]for i in actual));proof.append({'sourceTriangle':t.index,'sourceIndices':list(t.vertices)})
 assert len(tri)==24,(source.name,len(tri));other=[p+(wall if outward else -wall)*n for p,n in zip(points,norm)]
 if outward:geo=paired(other,points,tri)
 else:geo=paired(points,other,tri)
 return geo,points,norm,proof
def bar_geo(a,b,width=.008):
 d=(b-a).normalized();u=d.cross(Vector((1,0,0)))
 if u.length<.01:u=d.cross(Vector((0,1,0)))
 u.normalize();v=d.cross(u).normalized();points=[p+u*x*width/2+v*y*.005/2 for p in(a,b)for x,y in((-1,-1),(1,-1),(1,1),(-1,1))];return points,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def union(receiver,part):
 mod=receiver.modifiers.new('Actual connected shared support stock','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=part
 with bpy.context.temp_override(object=receiver,active_object=receiver,selected_objects=[receiver],selected_editable_objects=[receiver]):bpy.ops.object.modifier_apply(modifier=mod.name)
 mesh=part.data;bpy.data.objects.remove(part,do_unlink=True);bpy.data.meshes.remove(mesh)
def components(m):
 adjacency={i:set()for i in range(len(m.vertices))}
 for e in m.edges:a,b=e.vertices;adjacency[a].add(b);adjacency[b].add(a)
 seen=set();total=0
 for i in adjacency:
  if i in seen:continue
  total+=1;todo=[i]
  while todo:
   j=todo.pop()
   if j in seen:continue
   seen.add(j);todo.extend(adjacency[j]-seen)
 return total
def apply():
 bpy.context.view_layer.update();head=bpy.data.objects['head'];origin=head.matrix_world.translation.copy();records=[];lands=[];carrierlands={s:[]for s in(-1,1)};material=list(bpy.data.objects[LOWER[0]].data.materials);baseprops=dict(bpy.data.objects[LOWER[0]].items());baseprops.update({'region':'head-neck-interface','surfaceRole':'frame','constructionClass':'inherited-passive','exteriorEras':'maker,mechanic,builder','constructionOwner':'head','articulatesAcrossJoint':False,'proposal':True,'constructionDescription':'V38 explicit shared passive bow-rooted carrier with distinct supported plate lands; planned finite lands; left carrier fails assembled corner seating criterion, HOLD; no accepted support proof'})
 for name in LOWER:
  o=bpy.data.objects[name];side,col=map(int,(name.split()[-3],name.split()[-1]));upper=bpy.data.objects[f'V33 tapered throat cheek plate {side} 1 {col}'];upper.data.calc_loop_triangles();uv=[upper.matrix_world@p.co for p in upper.data.vertices];mapping={};root=[];inner=[];outer=[];nu=24;nv=6;normal=[];wall=.0035
  # Each lower leaf seats on a unique original upper-throat stock patch.
  # Upper face is unchanged; shared carrier contacts its actual inner face.
  for i in range(nu+1):
   for j in range(7):
    if i<=2:
     src=(14-i)*15+4+j;q=uv[src];n=(uv[src]-uv[src+495]).normalized();mapping[src]=i*7+j
    else:
     t=(i-2)/(nu-2);u=j/6;seed=uv[12*15+4+j]
     if side==0:
      lo,hi=[(-.102,-.036),(-.031,.031),(.036,.102)][col];x=lo+(hi-lo)*u;R=.168-.017*(abs(x)/.12)**2;angle=math.radians(166+7*(u-.5));target=Vector((x,origin.y+R*math.cos(angle),origin.z+R*math.sin(angle)))
     else:
      lo,hi=[(.74,1.45),(1.53,2.25),(2.33,2.92)][col];a=lo+(hi-lo)*u;rx=.125;ry=.128;x=side*rx*math.sin(a);y=origin.y-ry*math.cos(a);rear=max(0,y-origin.y);z=origin.z+.045+.37*rear+.008*(u-.5);target=Vector((x,y,z))
     # Convex descending leaf, with no circumferential horizontal root rim.
     q=seed.lerp(target,t);bulge=.008*math.sin(math.pi*t);q.y+=(-1 if q.y<origin.y else 1)*bulge;n=Vector((q.x,q.y-origin.y,0)).normalized()
    inner.append(q);outer.append(q+wall*n);normal.append(n)
  nverts=len(outer);faces=[];seat=[]
  for tri in upper.data.loop_triangles:
   if all(k in mapping for k in tri.vertices):
    f=tuple(mapping[k]for k in tri.vertices);faces.extend([f,tuple(nverts+k for k in reversed(f))]);seat.append({'receiver':upper.name,'actualSourceTriangle':tri.index,'sourceIndices':list(tri.vertices),'leafInnerIndices':[nverts+k for k in f]})
  assert len(seat)==24
  quads=[]
  for i in range(2,nu):
   for j in range(6):k=i*7+j;l=k+7;f=(k,k+1,l+1,l);faces.extend([f,tuple(nverts+x for x in reversed(f))]);quads.append(f)
  border=list(range(7))+[i*7+6 for i in range(1,nu+1)]+[nu*7+j for j in range(5,-1,-1)]+[i*7 for i in range(nu-1,0,-1)]
  for i,k in enumerate(border):q=border[(i+1)%len(border)];faces.append((k,q,nverts+q,nverts+k))
  props={'constructionDescriptionHistory':str(o.get('constructionDescription','unrecorded')),'constructionDescription':'V38 supported02 descending passive leaf, root on unique actual original upper-throat receiving patch with bow-connected shared inner carrier; independently head-owned, free cervical overlap proposed','v38NeckInterface':'No duplicated bow seat; unique original upper plate root patch and explicit inner carrier load path. Same-owner contacts/adjacent overlap and motion screen remain qualified.'}
  o,vol=closed(name,outer+inner,faces,list(o.data.materials),head,props);world=[o.matrix_world@v.co for v in o.data.vertices];error=max((world[e['leafInnerIndices'][j]]-uv[e['sourceIndices'][j]]).length for e in seat for j in range(3));assert error<1e-7
  receivergeo,points,norms,proof=patch(upper,range(12,15),range(4,11),inner=True,outward=False);supportside=side if side else(-1 if col<2 else 1);carrierlands[supportside].append({'geo':receivergeo,'points':points,'normals':norms,'receiver':upper.name,'proof':proof,'leaf':name});lands.append({'leaf':name,'receiver':upper.name,'patchRows':[12,14],'patchColumns':[4,10],'actualRootTriangles':seat,'worldTriangles':[[list(uv[i])for i in e['sourceIndices']]for e in seat]});records.append({'name':name,'owner':'head','eras':o.get('exteriorEras'),'class':'inherited-passive','positiveVolumeM3':vol,'copiedSeatMaximumErrorM':error,'receivingSurfaceTriangles':24,'receiver':upper.name,'carrier':f'V38 shared head throat carrier {supportside}','supportMeaning':'Leaf inner surface contacts24 unique actual upper-plate outer triangles; explicit shared carrier is intended to reach the corresponding original inner patch, but left carrier fails planned corner fit. Original finite stock thickness exists; assembled support is unproven and HOLD.'})
 bowSeats=[]
 for side in(-1,1):
  bow=bpy.data.objects[f'V31 passive cranial load bow {side}'];geo,points,norms,proof=patch(bow,range(18,21),range(2,9),wall=.012,outward=True);name=f'V38 shared head throat carrier {side}';carrier,vol=closed(name,*geo,material,head,baseprops);root=sum(points,Vector())/len(points)+sum(norms,Vector()).normalized()*.008
  for i,land in enumerate(carrierlands[side]):
   pad,_=closed(f'temporary head carrier pad {side} {i}',*land['geo'],material,head,{});end=sum(land['points'],Vector())/len(land['points'])-sum(land['normals'],Vector()).normalized()*.006
   arm,_=closed(f'temporary head carrier branch {side} {i}',*bar_geo(root,end),material,head,{});union(carrier,arm);union(carrier,pad)
  bpy.context.view_layer.update();bm=bmesh.new();bm.from_mesh(carrier.data);manifold=all(e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free();assert manifold and vol>0,(name,manifold,vol);count=components(carrier.data);assert count==1,(name,'disconnected support carrier',count)
  carrier.data.calc_loop_triangles();cv=[carrier.matrix_world@v.co for v in carrier.data.vertices];cf=[tuple(t.vertices)for t in carrier.data.loop_triangles];bvh=BVHTree.FromPolygons(cv,cf,all_triangles=True);errors=[]
  # Finite source patch corners sample planned lands only,
  # not a projected marker. Boolean assembly can retriangulate the pad.
  for geoPoints in [points]+[d['points']for d in carrierlands[side]]:
   for p in geoPoints:errors.append(bvh.find_nearest(p)[3])
  err=max(errors);print('FINITE_LAND_DIAGNOSTIC_HOLD',name,err,flush=True)
  records.append({'name':name,'owner':'head','eras':'maker,mechanic,builder','class':'inherited-passive','role':'One connected explicit shared carrier with unique actual bow seat and distinct original upper-throat inner receiving lands','bow':bow.name,'bowActualRootRows':[18,20],'bowActualRootColumns':[2,8],'bowSeatSourceTriangles':proof,'supportedLeaves':[d['leaf']for d in carrierlands[side]],'carrierConnectedComponents':count,'closedEdgeManifold':manifold,'positiveVolumeM3':vol,'maximumFiniteLandCornerSurfaceErrorM':err,'plannedSupportLandingStatus':'HOLD: Boolean union no longer reaches all planned finite landing corners'if err>1e-6 else 'Sampled finite corners retained; area fit still requires separate screen','seatingLimit':'Corner source correspondence sampled only; no area seating proof. Assembled strict surface crossings checked separately. Proposed rigid stock, not validated weld/load capacity.'});bowSeats.append({'carrier':name,'receiver':bow.name,'rows':[18,20],'columns':[2,8],'actualSourceTriangles':proof})
 return {'changedMeshes':LOWER,'changedNodes':[],'addedMeshes':CARRIERS,'removedMeshes':[],'watchMeshes':LOWER+CARRIERS,'attachmentAndEraMap':records,'actualLeafReceivingPatches':lands,'actualSharedCarrierBowSeats':bowSeats,'receivingAllocation':'Each leaf uses a distinct source upper-throat identity/patch; exactly one shared carrier per bow, one actual bow patch each, disjoint left/right. All original cervical guard geometry restored exact, including7/8/10 source receiver tongues. No repeated bow pad among leaves.','protected':'Original all40 cervical guards, lower30/captive frame, original uppernine throat plates, bows/shaft seats/journals/pivots/runtimeendpoints, crown/bill/optic/jaw/head identity, body/wing/leg/feet/material/era roles exact. No rigid joint bridge.','construction':'HOLD actual carrier land loss measured, not accepted supported construction. Nine oblique descending leaves and two explicit shared carrier proposals; original upper-cervical7/8/10 finite tongues receive freely moving head leaves. Leaf roots coincide with original upper-stock patches, but connected carrier Boolean union loses planned left landing corners. No assembled supported-construction claim; motion acceptance unresolved.','limits':['Measured carrier land gaps are HOLD; source-patch allocation is not an assembled support PASS. Finite support contact/corner checks and source triangle allocation do not replace coplanar-root overlap or actual stock motion screen.','All new and same-owner interfaces and inherited count increases included; no intended joint exemption.','Paired leaf3.5mm extrusion nominal, carrier pad/branch stock explicit; normal wall/load/fabrication/containment/continuous motion unproven.']}
