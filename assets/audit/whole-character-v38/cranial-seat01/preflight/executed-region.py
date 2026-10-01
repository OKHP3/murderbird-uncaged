"""Four fixed passive cranial shields with finite two-ended integral seat routes."""
import bpy,bmesh,math,json
from mathutils import Vector
REMOVED=[f'V33 diagonal brow receiver {s} {i}'for s in[-1,1]for i in range(3)]+[f'V38 optic cheek shield {s} {i}'for s in[-1,1]for i in range(3)]
PROFILES={'brow':[(-.478,1.801,1.775),(-.530,1.811,1.758),(-.585,1.793,1.757),(-.625,1.779,1.761),(-.668,1.753,1.733)],'cheek':[(-.442,1.730,1.680),(-.490,1.708,1.654),(-.530,1.657,1.623),(-.576,1.625,1.601),(-.621,1.631,1.613),(-.670,1.651,1.637)]}
WALL=.0045
def lerp(rows,y):
 for a,b in zip(rows,rows[1:]):
  if a[0]>=y>=b[0]:t=(y-a[0])/(b[0]-a[0]);return[a[k]+(b[k]-a[k])*t for k in[1,2]]
 return list(rows[-1][1:])
def stock(o):
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 non=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);todo=set(bm.verts);components=0
 while todo:
  components+=1;run=[todo.pop()]
  while run:
   for e in run.pop().link_edges:
    for v in e.verts:
     if v in todo:todo.remove(v);run.append(v)
 bm.to_mesh(o.data);bm.free();return{'nonmanifoldEdges':non,'signedVolumeM3':vol,'connectedComponents':components}
def obj(name,vertices,faces,parent,materials,extras):
 m=bpy.data.meshes.new(name+' finite stock');m.from_pydata(vertices,[],faces);m.update();o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);o.parent=parent;bpy.context.view_layer.update();o.matrix_world=__import__('mathutils').Matrix.Identity(4)
 for mat in materials:m.materials.append(mat)
 for k,v in extras.items():o[k]=v
 return o
def choose_patch(name,target,side,optic):
 o=bpy.data.objects[name];v=[o.matrix_world@p.co for p in o.data.vertices];choices=[]
 for f in o.data.polygons:
  ps=[v[i]for i in f.vertices];n=(ps[1]-ps[0]).cross(ps[2]-ps[0]).normalized();c=sum(ps,Vector())/len(ps)
  if side*c.x<=0 or not all(math.hypot(p.y-optic[0],p.z-optic[1])>.066 for p in ps):continue
  if name=='V31 frontal cranial cap receiving seat':
   if not(side*n.x>.2 or n.z>.4):continue
  elif side*n.x<.4:continue
  choices.append(((c-Vector(target)).length,f.index,ps,n))
 assert choices,('No real finite seat patch',name);distance,index,ps,n=min(choices,key=lambda p:p[0]);c=sum(ps,Vector())/len(ps);ps=[c+(p-c)*.70 for p in ps];return{'target':name,'face':index,'receiverCorners':[list(p)for p in ps],'normal':list(n),'desiredToActualFaceCentreM':distance},ps,n
def convex(name,points):
 m=bpy.data.meshes.new(name);bm=bmesh.new();vs=[bm.verts.new(p)for p in points];bmesh.ops.convex_hull(bm,input=vs,use_existing_faces=False);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(m);bm.free();o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);return o
def intersect_volume(a,b):
 o=a.copy();o.data=a.data.copy();bpy.context.scene.collection.objects.link(o);mod=o.modifiers.new('Finite commonstock diagnostic','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=b;bpy.context.view_layer.objects.active=o
 try:
  bpy.ops.object.modifier_apply(modifier=mod.name);r=stock(o);r['boundedByParticipatingVolumes']=0<r['signedVolumeM3']<=min(stock(a)['signedVolumeM3'],stock(b)['signedVolumeM3'])*1.001
 except Exception as error:r={'error':str(error)}
 bpy.data.objects.remove(o,do_unlink=True);return r
def apply():
 bpy.context.view_layer.update();head=bpy.data.objects['head'];materials={family:list(bpy.data.objects[f'V33 diagonal brow receiver -1 0'if family=='brow'else'V38 optic cheek shield -1 0'].data.materials)for family in['brow','cheek']};records=[];added={}
 for n in REMOVED:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
 for side in[-1,1]:
  aperture=bpy.data.objects[f'V31 Advanced optical aperture {side}'];ap=[aperture.matrix_world@v.co for v in aperture.data.vertices];optic=[(min(p.y for p in ap)+max(p.y for p in ap))/2,(min(p.z for p in ap)+max(p.z for p in ap))/2]
  for family in['brow','cheek']:
   name=f'V38 cranial-seat {family} shield {side}';rows=PROFILES[family];nu,nv=48,10;points=[];freeX=.162
   for r in range(nu+1):
    u=r/nu;y=rows[0][0]+(rows[-1][0]-rows[0][0])*u;top,bottom=lerp(rows,y);dy=y-optic[0]
    if abs(dy)<.0648:
     edge=math.sqrt(.0648**2-dy**2)+.001
     if family=='brow':bottom=max(bottom,optic[1]+edge)
     else:top=min(top,optic[1]-edge)
    assert top>bottom,(name,r)
    for j in range(nv+1):
     v=j/nv;points.append(Vector((side*(freeX+.0015*math.sin(math.pi*u)*math.sin(math.pi*v)),y,bottom+(top-bottom)*v)))
   half=len(points);vertices=points+[p-Vector((side*WALL,0,0))for p in points];faces=[];stride=nv+1
   for r in range(nu):
    for j in range(nv):a=r*stride+j;b=a+stride;faces.extend([(a,a+1,b+1,b),(half+b,half+b+1,half+a+1,half+a)])
   boundary=list(range(stride))+[i*stride+nv for i in range(1,nu+1)]+[nu*stride+j for j in range(nv-1,-1,-1)]+[i*stride for i in range(nu-1,0,-1)]
   for a,b in zip(boundary,boundary[1:]+boundary[:1]):faces.append((a,b,b+half,a+half))
   extras={'exteriorEras':'maker,mechanic,builder','region':'head','surfaceRole':'brow-shield'if family=='brow'else'cheek-shield','constructionClass':'inherited-passive','constructionDescription':'Fixed passive head-owned longitudinal shield and two integral finite cranial receiving routes. Actual surface/connected stock proof recorded; authored form/fit/likeness separately qualified.','v38CranialSeat01':'One supported construction proposal, not engineering/owner acceptance'}
   shield=obj(name,vertices,faces,head,materials[family],extras);stock(shield);lands=[]
   targets=([(f'V31 fixed temporal receiving wall {side}',(side*.096,-.490,1.775),(-.490,1.788)),('V31 frontal cranial cap receiving seat',(side*.095,-.635,1.780),(-.627,1.771))]if family=='brow'else[(f'V31 fixed temporal receiving wall {side}',(side*.095,-.460,1.688),(-.467,1.690)),(f'V33 formed lower cheek receiver {side} 0',(side*.149,-.660,1.628),(-.658,1.639))])
   for slot,(target,desired,endYZ)in enumerate(targets):
    rec,patch,n=choose_patch(target,desired,side,optic);endY,endZ=endYZ;end=[]
    for dx in[-.006,-.0015]:
     for dy,dz in[(-.003,-.003),(.003,-.003),(.003,.003),(-.003,.003)]:end.append(Vector((side*(freeX+dx),endY+dy,endZ+dz)))
    route=convex(name+' finite seat route '+str(slot),[p-n*.0008 for p in patch]+[p+n*.004 for p in patch]+end);rec['routeStock']=stock(route);rec['receivingCommonStock']=intersect_volume(route,bpy.data.objects[target]);rec['exteriorEndCommonStock']=intersect_volume(route,shield);rec['endLandNativeYZ']=list(endYZ)
    mod=shield.modifiers.new('Integral passive seat union','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=route;bpy.context.view_layer.objects.active=shield;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(route,do_unlink=True);lands.append(rec)
   finalStock=stock(shield)
   for f in shield.data.polygons:f.use_smooth=False
   records.append({'name':name,'owner':'head','actualOpticNativeYZ':optic,'longitudinalYZControls':rows,'nominalWallM':WALL,'stock':finalStock,'finiteSeatRoutes':lands});added[name]={'parent':'head','exteriorEras':'maker,mechanic,builder','region':'head','surfaceRole':extras['surfaceRole']}
 return{'changedMeshes':[],'added':added,'removed':REMOVED,'changedNodes':[],'construction':records,'constructionMethod':'Four broad longitudinal shields replace12 strips; each is united with two compact convex stock routes from genuine inset source face patches to broad shield inner lands. Finite root/end intersections, components and topology checked, no surface guesses/raycasts to absent receiver.','protected':'All surviving source meshgeometry/material definitions/nodeextras/transforms exact, including bill/contact, optics, jaw/socket/pivots, crown, neck/body.','limits':['Actual small patch/Boolean commonstock proves sampled static attachment only where manifold/positive/bounded; not manufacturing strength or continuous motion.','Root and shield overlap surface/neighbor clearance still qualified; full assembly not certified.','July head and Master03 guide form, not exact hidden structure dimensions.']}
