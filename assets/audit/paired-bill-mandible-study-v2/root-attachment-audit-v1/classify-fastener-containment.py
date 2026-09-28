"""Read-only parity classification of root fixing samples against evaluated blade 0."""
import bpy, os, json, math, hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree

TARGET='Profiled upper bill blade 0'
PINS=[f'Bill root fixing{s}' for s in ('','.001','.002','.003')]
DIRECTIONS=[Vector((1,math.sqrt(2),math.sqrt(3))).normalized(),Vector((math.sqrt(5),-1,math.sqrt(7))).normalized(),Vector((-math.sqrt(11),math.sqrt(13),1)).normalized(),Vector((-1,-math.sqrt(17),math.sqrt(19))).normalized()]

def world_mesh(obj,depsgraph):
    evaluated=obj.evaluated_get(depsgraph);mesh=evaluated.to_mesh();M=evaluated.matrix_world
    verts=[M@v.co for v in mesh.vertices]
    faces=[tuple(p.vertices) for p in mesh.polygons if len(p.vertices)>=3]
    tree=BVHTree.FromPolygons(verts,faces,all_triangles=False,epsilon=0)
    edge_use={}
    for poly in mesh.polygons:
        ids=list(poly.vertices)
        for a,b in zip(ids,ids[1:]+ids[:1]):
            key=(a,b) if a<b else (b,a);edge_use[key]=edge_use.get(key,0)+1
    boundary=sum(n==1 for n in edge_use.values());nonmanifold=sum(n!=2 for n in edge_use.values())
    evaluated.to_mesh_clear()
    return tree,verts,faces,{'vertices':len(verts),'faces':len(faces),'uniqueEdges':len(edge_use),'boundaryEdges':boundary,'nonManifoldEdges':nonmanifold,'watertightByEdgeIncidence':nonmanifold==0}

def ray_hit_count(tree,point,direction):
    origin=point.copy();count=0
    for _ in range(128):
        loc,normal,index,distance=tree.ray_cast(origin,direction,10.0)
        if loc is None:break
        count+=1
        origin=loc+direction*1e-6
    return count

def point_classification(tree,point):
    counts=[ray_hit_count(tree,point,d) for d in DIRECTIONS]
    parities=[n%2 for n in counts]
    if len(set(parities))==1:
        state='inside' if parities[0] else 'outside'
    else:
        state='direction-disagreement'
    return {'pointBlenderXYZM':[float(v) for v in point],'rayHitCounts':counts,'oddEvenParities':parities,'classification':state}

def evaluated_samples(obj,depsgraph):
    evaluated=obj.evaluated_get(depsgraph);mesh=evaluated.to_mesh();M=evaluated.matrix_world
    pts=[M@v.co for v in mesh.vertices]
    face_centers=[];edge_use={}
    for poly in mesh.polygons:
        ids=list(poly.vertices)
        if len(ids)>=3:face_centers.append(sum((pts[i] for i in ids),Vector())/len(ids))
        for a,b in zip(ids,ids[1:]+ids[:1]):
            key=(a,b) if a<b else (b,a);edge_use[key]=edge_use.get(key,0)+1
    bbox_center=sum(pts,Vector())/len(pts)
    topology={'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'uniqueEdges':len(edge_use),'boundaryEdges':sum(n==1 for n in edge_use.values()),'nonManifoldEdges':sum(n!=2 for n in edge_use.values())}
    evaluated.to_mesh_clear()
    return pts,face_centers,bbox_center,topology

target=bpy.data.objects.get(TARGET);assert target and target.type=='MESH'
deps=bpy.context.evaluated_depsgraph_get();tree,tverts,tfaces,topology=world_mesh(target,deps)
out={'nativePath':bpy.data.filepath,'blenderVersion':bpy.app.version_string,'target':TARGET,'targetTopology':topology,'rays':'Four non-axis, non-integer-ratio directions; odd/even intersection parity. Each fastener vertex, polygon center and vertex-average center classified against actual evaluated target triangles.','pins':{},'limits':['Parity is reliable only for a closed, consistently bounded target; edge-incidence watertightness is necessary but not sufficient to prove orientable manifold validity.','Finite sample classification is not full solid intersection/volume analysis. Points near shared boundaries may disagree; disagreement is retained.','Only each root fixing relative to blade 0 is classified.']}
for name in PINS:
    obj=bpy.data.objects.get(name);assert obj and obj.type=='MESH'
    pts,centers,centroid,pin_topology=evaluated_samples(obj,deps)
    pin_tree,_,_,_=world_mesh(obj,deps)
    bounds_min=[min(float(p[i]) for p in pts) for i in range(3)];bounds_max=[max(float(p[i]) for p in pts) for i in range(3)]
    dimensions=[bounds_max[i]-bounds_min[i] for i in range(3)]
    local_axes={name:[float(v) for v in (obj.matrix_world.to_3x3() @ axis).normalized()] for name,axis in [('localX',Vector((1,0,0))),('localY',Vector((0,1,0))),('localZ',Vector((0,0,1)))]}
    outer_direction=Vector((-1 if centroid.x<0 else 1,0,0));inner_direction=-outer_direction
    axis_rays={}
    for label,direction in [('towardOuterSide',outer_direction),('towardInnerSide',inner_direction)]:
        hit=tree.ray_cast(centroid,direction,2.0)
        axis_rays[label]=None if hit[0] is None else {'pointBlenderXYZM':[float(v) for v in hit[0]],'normalBlenderXYZ':[float(v) for v in hit[1]],'distanceM':float(hit[3]),'normalDotRayDirection':float(hit[1].dot(direction))}
    vertex_rows=[point_classification(tree,p) for p in pts]
    face_rows=[point_classification(tree,p) for p in centers]
    centroid_row=point_classification(tree,centroid)
    out['pins'][name]={'parent':obj.parent.name if obj.parent else None,'objectWorldTranslation':[float(v) for v in obj.matrix_world.translation],
      'pinTopology':pin_topology,'surfaceBVHCandidatePairsWithBlade0':len(tree.overlap(pin_tree)),
      'worldBoundsXYZMetres':{'min':bounds_min,'max':bounds_max},'worldBoundsDimensionsMetres':dimensions,
      'localAxesInWorld':local_axes,'worldXAxisSideWallRaysFromVertexAverage':axis_rays,
      'bboxCenterClassification':centroid_row,'vertexSampleCounts':{key:sum(row['classification']==key for row in vertex_rows) for key in ['inside','outside','direction-disagreement']},
      'faceCenterSampleCounts':{key:sum(row['classification']==key for row in face_rows) for key in ['inside','outside','direction-disagreement']},
      'vertexAmbiguityExamples':[r for r in vertex_rows if r['classification']=='direction-disagreement'][:4],
      'faceAmbiguityExamples':[r for r in face_rows if r['classification']=='direction-disagreement'][:4]}
path=os.environ['AUDIT_JSON_OUT']
with open(path,'x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'written':path,'targetTopology':topology,'pins':{n:{'center':v['bboxCenterClassification']['classification'],'verts':v['vertexSampleCounts'],'faces':v['faceCenterSampleCounts']} for n,v in out['pins'].items()}}))
