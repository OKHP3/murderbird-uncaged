"""V31 metadata-only Maker wing receiving-point proposal.
Actual passive mantle load member supplies a finite surface and shoulder lever arm.
No mesh, material, rest, whole-layout, era or runtime changes.
"""
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OWNER='right-mantle'
SURFACE='right swept upper wing load member'
def apply():
    owner=bpy.data.objects[OWNER];surface=bpy.data.objects[SURFACE]
    assert surface.type=='MESH' and surface.parent==owner
    assert surface.get('surfaceRole')=='frame'
    assert set(surface.get('exteriorEras','').split(','))=={'maker','mechanic','builder'}
    assert surface.get('constructionClass') in {'inherited-passive','proposed-passive'}
    bpy.context.view_layer.update()
    ev=surface.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles()
    vertices=[ev.matrix_world@v.co for v in m.vertices];triangles=[tuple(t.vertices) for t in m.loop_triangles]
    shoulder=owner.matrix_world.translation.copy();elbow=bpy.data.objects['right-wing-shield'].matrix_world.translation.copy()
    # Near the distal load-member / elbow receiving opening, rather than a new
    # arbitrary exterior-plate hole. Outboard native -X is anatomical right.
    desired=shoulder.lerp(elbow,.88)+Vector((-.022,0,.006))
    point,normal,index,distance=BVHTree.FromPolygons(vertices,triangles,all_triangles=True).find_nearest(desired)
    assert point is not None and all(math.isfinite(v) for v in point)
    local=owner.matrix_world.inverted()@point
    gltf=(local.x,local.z,-local.y)
    lever=math.hypot(local.y,local.z);assert lever>.15
    vertexIds=triangles[index];witness=[list(vertices[i]) for i in vertexIds]
    nearestVertex=min(range(len(vertices)),key=lambda i:(vertices[i]-point).length_squared)
    ev.to_mesh_clear()
    socket={'schema':1,'coordinateSpace':'gltf-node-local','point':list(gltf),'surfaceObject':SURFACE,
        'status':'Inferred passive external-control receiving point; actual exported seating and route need review',
        'constructionPurpose':'Maker push/pull horn terminates on the existing mantle-owned upper load member near its elbow receiving opening, with nonzero shoulder lever arm; no powered bronze',
        'source':'V31 reconstructed attachment from actual evaluated passive load frame'}
    owner['makerControlSocketV1']=json.dumps(socket,separators=(',',':'))
    return {'region':'maker-wing-control-socket','status':'Metadata-only reconstructed receiving-point proposal',
        'changedNodes':[OWNER],'changedProperties':[OWNER+'.makerControlSocketV1'],
        'changedMeshes':[],'added':[],'removed':[],'socket':socket,
        'authoredNativeWorldPoint':list(point),'authoredNativeOwnerLocalPoint':list(local),
        'desiredNativeWorldPoint':list(desired),'selectedEvaluatedTriangleIndex':index,
        'selectedEvaluatedTriangleVertexIds':list(vertexIds),'selectedEvaluatedTriangleWorldVertices':witness,
        'nearestEvaluatedVertexIndex':nearestVertex,'nearestVertexNativeWorld':list(vertices[nearestVertex]),
        'nearestVertexDistanceM':(vertices[nearestVertex]-point).length,'evaluatedSurfaceDistanceM':0,
        'searchPointSurfaceDistanceM':distance,'surfaceNormalNativeWorld':list(normal),
        'shoulderLeverArmM':lever,'surfaceOwner':OWNER,
        'preserved':['Every mesh, object transform, material definition and original era tag','Named pivots, left restriction and passive load path','No activation of priorV21_mechanismLayoutV1'],
        'limits':['Point-on-triangle seating, not hardware-fastener engineering or canopy/rod route clearance.','Finite receiving/load member remains exactly unchanged; no new lug is claimed.','Final exported V31 must verify named mesh resolution and actual Maker articulation.']}
