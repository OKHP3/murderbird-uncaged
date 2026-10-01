"""Twelve fixed head-owned brow/cheek shields, actual optic centred; proposal."""
import bpy,bmesh,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
NAMES=[f'V33 diagonal brow receiver {s} {i}'for s in[-1,1]for i in range(3)]+[f'V38 optic cheek shield {s} {i}'for s in[-1,1]for i in range(3)]
LAYOUT={'brow':[(20,67,.086,.101,.086,.165),(65,116,.088,.103,.083,.158),(114,158,.082,.094,.078,.165)],'cheek':[(163,212,.079,.099,.083,.164),(210,258,.083,.094,.078,.157),(256,326,.078,.100,.080,.164)]}
WALL=.0045
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def apply():
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
