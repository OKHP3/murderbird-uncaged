"""Six shield fit correction: interior planar finite endlands and narrowed bridges."""
import bpy,bmesh,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ALLOWED=[f'V38 optic cheek shield {s} {i}' for s in (-1,1) for i in range(3)]
PATCHES=[(('V33 diagonal brow receiver {side} 0',(-.491,1.815)),('V31 fixed temporal receiving wall {side}',(-.366,1.815))), (('V31 fixed temporal receiving wall {side}',(-.484,1.691)),('V31 fixed temporal receiving wall {side}',(-.406,1.683))), (('V33 formed lower cheek receiver {side} 0',(-.638,1.676)),('V31 fixed temporal receiving wall {side}',(-.520,1.674)))]
def apply():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();records=[]
 def geometry(name):
  o=bpy.data.objects[name];e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();v=[e.matrix_world@q.co for q in m.vertices];t=[tuple(q.vertices) for q in m.loop_triangles];e.to_mesh_clear();return BVHTree.FromPolygons(v,t,all_triangles=True),v,t
 for side in (-1,1):
  for course,patches in enumerate(PATCHES):
   name=f'V38 optic cheek shield {side} {course}';o=bpy.data.objects[name];world=o.matrix_world.copy();inv=world.inverted();old=[v.co.copy() for v in o.data.vertices];assert len(old)==182;targets={n.format(side=side):geometry(n.format(side=side)) for n,_ in patches};ends=[];samples=[]
   for end,(target,(cy,cz)) in enumerate(patches):
    target=target.format(side=side);tree,vertices,triangles=targets[target];hit=tree.ray_cast(Vector((side*.8,cy,cz)),Vector((-side,0,0)));assert hit[0] is not None,(name,target,cy,cz)
    tri=[vertices[i] for i in triangles[hit[2]]];normal=(tri[1]-tri[0]).cross(tri[2]-tri[0]).normalized();normal=normal if normal.x*side>0 else -normal
    # Every land point lies in the interior of this one actual source triangle.
    # The barycentric patch is deliberately small enough not to cross its finite edges.
    center=sum(tri,Vector())/3
    # Common nativeY/Z grid orientation independent of receiver triangle winding.
    ey=Vector((-normal.y/normal.x,1,0));ez=Vector((-normal.z/normal.x,0,1))
    e0=tri[0]-tri[2];e1=tri[1]-tri[2];den=e0.y*e1.z-e0.z*e1.y;assert abs(den)>1e-12
    def bary(point):
     q=point-tri[2];a=(q.y*e1.z-q.z*e1.y)/den;b=(e0.y*q.z-e0.z*q.y)/den;return [a,b,1-a-b]
    rates=[bary(center+ey),bary(center+ez)];extent=.10/max(abs(rates[0][i]-1/3)+abs(rates[1][i]-1/3) for i in range(3))
    hits={}
    for row in range(3):
     for col in range(7):
      point=center+ey*((row-1)*extent)+ez*((col/6-.5)*2*extent);weights=bary(point);assert min(weights)>.22
      hits[row,col]=(point,normal);samples.append({'end':end,'row':row,'col':col,'target':target,'targetTriangle':hit[2],'targetTriangleVertices':[list(p) for p in tri],'barycentric':weights,'surfacePoint':list(point),'surfaceNormal':list(normal),'surfaceGapM':.003,'stockM':.0045})
    ends.append((target,hits))
   a=ends[0][1][1,3][0];b=ends[1][1][1,3][0];fronts=[];normals=[]
   for row in range(13):
    for col in range(7):
     v=col/6
     if row<=2:p,n=ends[0][1][row,col];front=p+n*.0075
     elif row>=10:p,n=ends[1][1][row-10,col];front=p+n*.0075
     else:
      t=(row-2)/8;ease=t*t*(3-2*t);start=ends[0][1][2,col];finish=ends[1][1][0,col];n=(start[1]*(1-t)+finish[1]*t).normalized()
      # Interpolate the actual finite outer edge sections, with short swept taper.
      front=(start[0]+start[1]*.0075)*(1-t)+(finish[0]+finish[1]*.0075)*t
      front.z += [-.004,-.004,-.014][course]*math.sin(math.pi*t)
      front.z += (v-.5)*[.014,.010,.008][course]*math.sin(math.pi*t)
      front.x += side*.003*math.sin(math.pi*t)
      # Only named real receiving surfaces constrain the inner bridge.
      floor=[]
      for target,(tree,_,_) in targets.items():
       hit=tree.ray_cast(Vector((side*.8,front.y,front.z)),Vector((-side,0,0)))
       if hit[0] is not None:floor.append(abs(hit[0].x))
      if floor:front.x=side*max(abs(front.x),max(floor)+.009)
     fronts.append(front);normals.append(n)
   points=fronts+[p-n*.0045 for p,n in zip(fronts,normals)];o.data=o.data.copy()
   for vert,p in zip(o.data.vertices,points):vert.co=inv@p
   o.data.update();bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));closed=all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);assert closed and volume>0,name;bm.to_mesh(o.data);bm.free();actual=[world@v.co for v in o.data.vertices];stock=[(actual[i]-actual[i+91]).length for i in range(91)];assert max(abs(x-.0045) for x in stock)<3e-7
   measured=[]
   for q in samples:
    idx=(q['row'] if q['end']==0 else q['row']+10)*7+q['col'];back=actual[idx+91];near=targets[q['target']][0].find_nearest(back);measured.append({**q,'actualInnerVertex':list(back),'nearestFinitePoint':list(near[0]),'nearestFiniteNormal':list(near[1]),'actualFiniteGapM':near[3]})
   edges=[]
   for end,(target,hits) in enumerate(ends):
    rows=[0,1,2] if end==0 else [10,11,12]
    for row in rows:
     for col in range(7):
      idx=row*7+col
      for other in ([idx+1] if col<6 and row in (rows[0],rows[-1]) else [])+([idx+7] if row<rows[-1] and col in (0,6) else []):
       point=(actual[idx+91]+actual[other+91])*.5;near=targets[target][0].find_nearest(point);edges.append({'end':end,'edge':[idx,other],'innerMidpoint':list(point),'receiver':target,'nearestFinitePoint':list(near[0]),'normal':list(near[1]),'distanceM':near[3]})
   o['v38CheekSeatedFit']='Six shield02: true finite triangle endlands,3mm nominal normal gap,4.5mm paired stock, shortened lower return'
   records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'constructionClass':o.get('constructionClass'),'materials':[m.name if m else None for m in o.data.materials],'method':'Two planar interior patches on named actual finite receiving triangles,3mm nominal normal gap; connected narrow swept bridge below upperleaf witness bounds. No proxy wall or other object changes.','changedVertexIndices':[i for i,v in enumerate(o.data.vertices) if v.co!=old[i]],'sameSourceVertexFaceCounts':True,'supportedFootprintSamples':measured,'perimeterMidpointWitnesses':edges,'footprintGapMinMaxM':[min(q['actualFiniteGapM'] for q in measured),max(q['actualFiniteGapM'] for q in measured)],'perimeterGapMinMaxM':[min(q['distanceM'] for q in edges),max(q['distanceM'] for q in edges)],'stockMinMaxM':[min(stock),max(stock)],'maximumMovementM':max((v.co-old[i]).length for i,v in enumerate(o.data.vertices)),'closedEdgeManifold':closed,'positiveVolumeM3':volume})
 return {'changedMeshes':ALLOWED,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'confirmation':'July HEAD ONLY controls directional cheek/brow/optic relationship,master03 wholebird. Actual finite named receiver triangles surveyed before bridge.','reconstruction':'Triangle endland dimensions and exact shield curvature are authored fit/form proposal,not art metrology or engineering acceptance.','limits':['Only6shields change. Opticfront/rear48,bill,jaw397,truehinge,crown,neck/body/materials/pivots exact.','Foot samples/perimeter demonstrate declared receiving surfaces and measured gaps,not fastening or continuous solid clearance.','Union36 seven-pose fullfinitepool same-owner strict screen is separate and introduced crossings remain HOLD.']}
