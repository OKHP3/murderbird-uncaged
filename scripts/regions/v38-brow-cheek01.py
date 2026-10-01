"""Twelve fixed head-owned brow/cheek shields, actual optic centred; proposal."""
import bpy,bmesh,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
NAMES=[f'V33 diagonal brow receiver {s} {i}'for s in[-1,1]for i in range(3)]+[f'V38 optic cheek shield {s} {i}'for s in[-1,1]for i in range(3)]
LAYOUT={'brow':[(20,67,.086,.101,.086,.165),(65,116,.088,.103,.083,.158),(114,158,.082,.094,.078,.165)],'cheek':[(163,212,.079,.099,.083,.164),(210,258,.083,.094,.078,.157),(256,326,.078,.100,.080,.164)]}
WALL=.0045
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def apply(second=False):
 if second:return apply_contours()
 bpy.context.view_layer.update();records=[]
 for side in[-1,1]:
  aperture=bpy.data.objects[f'V31 Advanced optical aperture {side}'];ap=[aperture.matrix_world@v.co for v in aperture.data.vertices];cy=(min(p.y for p in ap)+max(p.y for p in ap))/2;cz=(min(p.z for p in ap)+max(p.z for p in ap))/2
  supports=[]
  for n in [f'V31 fixed temporal receiving wall {side}']+[f'V33 formed lower cheek receiver {side} {i}'for i in range(2)]:
   o=bpy.data.objects[n];o.data.calc_loop_triangles();verts=[o.matrix_world@v.co for v in o.data.vertices];supports.append((n,BVHTree.FromPolygons(verts,[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True)))
  for family in ['brow','cheek']:
   for course,(start,end,r0,rm,r1,freeX)in enumerate(LAYOUT[family]):
    name=f'V33 diagonal brow receiver {side} {course}'if family=='brow'else f'V38 optic cheek shield {side} {course}';o=bpy.data.objects[name];points=[];roots=[];nu,nv=32,10
    for row in range(nu+1):
     u=row/nu;theta=math.radians(start+(end-start)*u);outer=(r0+(rm-r0)*math.sin(math.pi*u/2) if u<=.5 else r1+(rm-r1)*math.sin(math.pi*(1-u)/2));inner=.0648+.003*math.sin(math.pi*u)**2
     for col in range(nv+1):
      v=col/nv;r=inner+(outer-inner)*v;y=cy+r*math.cos(theta);z=cz+r*math.sin(theta);x=freeX+.0015*math.sin(math.pi*u)*math.sin(math.pi*v)
      if v>=.7:
       hits=[]
       for target,tree in supports:
        hit=tree.ray_cast(Vector((side*.5,y,z)),Vector((-side,0,0)))
        if hit[0] is not None:hits.append((abs(hit[0].x),target,hit))
       if hits:
        hx,target,hit=max(hits,key=lambda q:q[0]);blend=ease((v-.7)/.3);x=x*(1-blend)+(hx+WALL-.0005)*blend
        if col==nv:roots.append({'outerVertex':len(points),'target':target,'triangle':hit[2],'receiverPointNative':list(hit[0]),'authoredCommonStockDepthM':.0005})
      points.append(Vector((side*x,y,z)))
    half=len(points);world=points+[p-Vector((side*WALL,0,0))for p in points];faces=[];stride=nv+1
    for row in range(nu):
     for col in range(nv):a=row*stride+col;b=a+stride;faces.extend([(a,a+1,b+1,b),(half+b,half+b+1,half+a+1,half+a)])
    boundary=list(range(stride))+[i*stride+nv for i in range(1,nu+1)]+[nu*stride+j for j in range(nv-1,-1,-1)]+[i*stride for i in range(nu-1,0,-1)]
    for a,b in zip(boundary,boundary[1:]+boundary[:1]):faces.append((a,b,b+half,a+half))
    inv=o.matrix_world.inverted();m=bpy.data.meshes.new(name+' broad formed orbital shield');m.from_pydata([inv@p for p in world],[],faces);m.update()
    for mat in o.data.materials:m.materials.append(mat)
    bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));non=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True)
    if vol<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));vol=bm.calc_volume(signed=True)
    assert non==0 and vol>0,(name,non,vol);bm.to_mesh(m);bm.free();o.data=m
    for f in m.polygons:f.use_smooth=f.index<nu*nv*2
    o['constructionDescription']='Fixed head-owned broad swept brow/cheek shield with4.5mm axial paired wall and integral outside-orbit receiving returns; actual optic centre used. Support/clearance and likeness qualified separately.';o['v38BrowCheek01']='Inherited passive all3eras; no optical geometry, bill/jaw linkage, crown, parent or pivot change'
    records.append({'name':name,'owner':o.parent.name,'exteriorEras':o.get('exteriorEras'),'angularRangeDegrees':[start,end],'authoredOuterRadiusControlsM':[r0,rm,r1],'openingMinRadiusM':.0648,'nominalLapAxialLayerM':freeX,'closedNonmanifoldEdges':non,'signedVolumeM3':vol,'rootWitnesses':roots,'rootReceivingRows':len(roots),'rootSupportQualification':'Finite vertex rays identify actual named receiving triangles;0.5mm authored union-depth at outer root. Wholepatch union/continuous load route not proven by these points.','actualOpticNativeYZ':[cy,cz]})
 return {'changedMeshes':NAMES,'changedNodes':[],'added':[],'removed':[],'construction':records,'constructionMethod':'Three varied broad brow/temple shields plus three swept rear/lower cheeks per side; actual optic-centred partial crescents, nonuniform radial outlines, layered7mm axial steps/2degree laps. Integral compact receiving returns stay outside actual optic lip. No complete annular helmet or head-jaw bridge.','protected':'Bill-vault geometry/contact, jaw socket/pivots, optic/lip/cup/aperture, crown, neck/body/othermesh/era/material/owner transforms exact.','limits':['Authored plate/control dimensions are reconstruction, not July metrology or approval.','Closed stock does not establish self/interpart clearance; ray root witnesses are not full finite seating proof.','Adjacent layer/lap/return fit and moving jaw clearance require bounded source comparison after first visible gate.']}

# Final variant: longitudinal contour paths; optic is a cutout, not the outer layout.
CONTOURS={
'brow':[
 [(-.49,1.794,1.766),(-.54,1.805,1.756),(-.59,1.800,1.757),(-.64,1.781,1.741),(-.685,1.754,1.717)],
 [(-.355,1.772,1.729),(-.405,1.800,1.753),(-.46,1.814,1.776),(-.52,1.799,1.775)],
 [(-.635,1.781,1.754),(-.663,1.770,1.743),(-.690,1.741,1.713),(-.718,1.706,1.691)]],
'cheek':[
 [(-.442,1.728,1.678),(-.49,1.707,1.660),(-.53,1.657,1.619),(-.56,1.634,1.610),(-.60,1.624,1.605),(-.64,1.641,1.613),(-.68,1.650,1.628)],
 [(-.335,1.744,1.698),(-.39,1.752,1.704),(-.442,1.738,1.699),(-.49,1.712,1.684)],
 [(-.355,1.678,1.646),(-.41,1.687,1.641),(-.467,1.667,1.626),(-.527,1.646,1.617)]]}
def sample_path(rows,y):
 for a,b in zip(rows,rows[1:]):
  if a[0]>=y>=b[0]:
   t=(y-a[0])/(b[0]-a[0]);return [a[k]+(b[k]-a[k])*t for k in[1,2]]
 return list(rows[-1][1:])
def apply_contours():
 bpy.context.view_layer.update();records=[]
 for side in[-1,1]:
  aperture=bpy.data.objects[f'V31 Advanced optical aperture {side}'];ap=[aperture.matrix_world@v.co for v in aperture.data.vertices];cy=(min(p.y for p in ap)+max(p.y for p in ap))/2;cz=(min(p.z for p in ap)+max(p.z for p in ap))/2
  supports=[]
  for n in [f'V31 fixed temporal receiving wall {side}','V31 frontal cranial cap receiving seat']+[f'V33 formed lower cheek receiver {side} {i}'for i in range(2)]:
   target=bpy.data.objects[n];target.data.calc_loop_triangles();supports.append((n,BVHTree.FromPolygons([target.matrix_world@v.co for v in target.data.vertices],[tuple(t.vertices)for t in target.data.loop_triangles],all_triangles=True)))
  for family in ['brow','cheek']:
   for course,rows in enumerate(CONTOURS[family]):
    name=f'V33 diagonal brow receiver {side} {course}'if family=='brow'else f'V38 optic cheek shield {side} {course}';o=bpy.data.objects[name];freeX=([.164,.157,.171]if family=='brow'else[.164,.157,.171])[course];points=[];roots=[];nu,nv=40,10
    for row in range(nu+1):
     u=row/nu;y=rows[0][0]+(rows[-1][0]-rows[0][0])*u;top,bottom=sample_path(rows,y);dy=y-cy
     if abs(dy)<.0648:
      edge=math.sqrt(.0648**2-dy**2)+.001
      if family=='brow':bottom=max(bottom,cz+edge)
      else:top=min(top,cz-edge)
     assert top>bottom,(name,row,top,bottom)
     for col in range(nv+1):
      v=col/nv;z=bottom+(top-bottom)*v;x=freeX-.003*ease((u-.72)/.28)+.0008*math.sin(math.pi*u)*math.sin(math.pi*v);rootv=v if family=='brow'else 1-v
      if rootv>=.7:
       hits=[]
       for target,tree in supports:
        hit=tree.ray_cast(Vector((side*.5,y,z)),Vector((-side,0,0)))
        if hit[0]is not None:hits.append((abs(hit[0].x),target,hit))
       if hits:
        hx,target,hit=max(hits,key=lambda q:q[0]);blend=ease((rootv-.7)/.3);x=x*(1-blend)+(hx+WALL-.0005)*blend
        if rootv==1:roots.append({'outerVertex':len(points),'target':target,'triangle':hit[2],'receiverPointNative':list(hit[0]),'authoredCommonStockDepthM':.0005})
      points.append(Vector((side*x,y,z)))
    half=len(points);world=points+[p-Vector((side*WALL,0,0))for p in points];faces=[];stride=nv+1
    for row in range(nu):
     for col in range(nv):a=row*stride+col;b=a+stride;faces.extend([(a,a+1,b+1,b),(half+b,half+b+1,half+a+1,half+a)])
    boundary=list(range(stride))+[i*stride+nv for i in range(1,nu+1)]+[nu*stride+j for j in range(nv-1,-1,-1)]+[i*stride for i in range(nu-1,0,-1)]
    for a,b in zip(boundary,boundary[1:]+boundary[:1]):faces.append((a,b,b+half,a+half))
    inv=o.matrix_world.inverted();m=bpy.data.meshes.new(name+' longitudinal shield optic cutout');m.from_pydata([inv@p for p in world],[],faces);m.update()
    for mat in o.data.materials:m.materials.append(mat)
    bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));non=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True)
    if vol<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));vol=bm.calc_volume(signed=True)
    assert non==0 and vol>0,(name,non,vol);bm.to_mesh(m);bm.free();o.data=m
    for f in m.polygons:f.use_smooth=f.index<nu*nv*2
    o['constructionDescription']='Fixed head-owned broad longitudinal brow/cheek shield with optic keepout cutout,4.5mm axial stock and integral returns to actual frontal-cap/temporal/lower-cheek receivers. Hidden support and clearance qualified separately.';o['v38BrowCheek01']='Finallongitudinal method; inheritedpassive all3eras, no jawbridge or optic/bill/crown/owner/pivot change'
    records.append({'name':name,'owner':o.parent.name,'exteriorEras':o.get('exteriorEras'),'longitudinalNativeYZControls':rows,'actualOpticNativeYZ':[cy,cz],'openingMinRadiusM':.0648,'closedNonmanifoldEdges':non,'signedVolumeM3':vol,'rootWitnesses':roots,'rootReceivingRows':len(roots),'rootSupportQualification':'Actual finite surface rays at selected root edge vertices with0.5mm authored commonstock; no fullpatch seating/load claim.'})
 return {'changedMeshes':NAMES,'changedNodes':[],'added':[],'removed':[],'construction':records,'constructionMethod':'Long rear-temple to billroot brow/cheek contour paths, nonuniform broad formed faces, smaller transition laps; actual optic keepout is cutout within longitudinal planes rather than organising exterior ring. Samehead passive receiving returns, no jawbridge.','protected':'Billvault/contact, opticalcenter/cup/lip/aperture/material, jaw mechanism/socket/pivots, crown, neck/body/othergeometry/owners/eras exact.','limits':['Authored contours not reference metrology or owner acceptance.','Actualray root correspondence is vertex evidence, not finitewholepatch load/union proof.','Closed stock requires scoped self/neighbor rest/Makerjaw comparison; no complete engineering/motion claim.']}
