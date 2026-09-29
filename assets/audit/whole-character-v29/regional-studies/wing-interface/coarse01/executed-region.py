"""V29 single coarse nesting proposal on the V28 compact wing hierarchy.
Preserves complete mantle exterior, machinery, rigid nodes and motion limits.
Native Z-up/-Y-front. Construction distances are proposals, not art measures.
"""
import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
RECESS_M=.045
FORK_RADIUS_M=.0045

def node(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),json.dumps(dict(o.items()),sort_keys=True,default=lambda x:list(x)))
def snapshot(o):return (node(o),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),tuple((q.name,q.type) for q in o.modifiers),o.hide_render,o.hide_viewport)
def evaluated_bvh(o):
    e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();v=[e.matrix_world@p.co for p in m.vertices];t=[tuple(f.vertices) for f in m.loop_triangles];e.to_mesh_clear();return BVHTree.FromPolygons(v,t,all_triangles=True)
def tube(o,points,r):
    verts=[];faces=[];N=16
    for i,p in enumerate(points):
        t=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized();u=t.cross(Vector((1,0,0)))
        if u.length<.01:u=t.cross(Vector((0,1,0)))
        u.normalize();v=t.cross(u).normalized()
        for k in range(N):verts.append(p+r*(u*math.cos(k*math.tau/N)+v*math.sin(k*math.tau/N)))
    for j in range(len(points)-1):
        for k in range(N):a=j*N+k;b=j*N+(k+1)%N;faces.append((a,b,b+N,a+N))
    faces.append(tuple(reversed(range(N))));faces.append(tuple((len(points)-1)*N+k for k in range(N)))
    bpy.context.view_layer.update();inv=o.matrix_world.inverted();old=o.data;mesh=bpy.data.meshes.new(o.name+' V29 inboard braced receiver');mesh.from_pydata([inv@p for p in verts],[],faces)
    for mat in old.materials:mesh.materials.append(mat)
    mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o.data=mesh
    for q in list(o.modifiers):o.modifiers.remove(q)
    for p in mesh.polygons:p.use_smooth=True
    return [list(p) for p in points]
def apply():
    bpy.context.view_layer.update();nodes={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'};original={o.name:snapshot(o) for o in bpy.data.objects if o.type=='MESH'};changed=[];receivers=[]
    for label,side in [('left',1),('right',-1)]:
        owner=label+'-wing-shield';joint=bpy.data.objects[owner].matrix_world.translation.copy();liner=bpy.data.objects[f'{label} profiled mantle backing v4 {owner}'];parts=[liner]+[o for o in bpy.data.objects if o.parent and o.parent.name==owner and (o.name.startswith(f'V28 {label} short nested shield ') or o.name==f'V28 {label} short shield leading fold')]
        for o in parts:
            o.data=o.data.copy();bpy.context.view_layer.update();inv=o.matrix_world.to_3x3().inverted();delta=inv@Vector((-side*RECESS_M,0,0))
            for v in o.data.vertices:v.co+=delta
            o.data.update();o['geometryStatus']='V29 coarse01 inferred inward nesting proposal, clearance and likeness pending';o['nestingRecessM']=RECESS_M;o['constructionClass']='proposed-passive';changed.append(o.name)
        bpy.context.view_layer.update();journal=bpy.data.objects[f'{label} coaxial elbow journal'];journal_bvh=evaluated_bvh(journal);liner_bvh=evaluated_bvh(liner)
        for k,dy in enumerate([-.012,.012]):
            # The retained inner journal face is an actual seat. Begin below
            # the upper load member, then turn inboard into the nested liner.
            seat_target=joint+Vector((-side*.018,dy,-.032));seat,_,_,seat_distance=journal_bvh.find_nearest(seat_target)
            end_target=Vector((side*.369,.109 if k==0 else .223,.966));end,_,_,end_distance=liner_bvh.find_nearest(end_target)
            first=seat+Vector((-side*.025,dy*.25,-.008));middle=first.lerp(end,.58);middle.x=side*min(abs(first.x),abs(end.x));points=[seat,first,middle,end];o=bpy.data.objects[f'V28 {label} nested shield receiving fork {k+1}'];tube(o,points,FORK_RADIUS_M)
            o['geometryStatus']='V29 coarse01 single-owner braced receiver proposal; measured journal-to-liner endpoints, fit pending';o['constructionClass']='proposed-passive';o['authoringRole']='Independent short-shield receiver follows inner elbow seat beneath retained upper load member into its own recessed liner';o['forkRadiusM']=FORK_RADIUS_M;o['seatObject']=journal.name;o['endpointObject']=liner.name;changed.append(o.name)
            receivers.append({'name':o.name,'owner':owner,'seatObject':journal.name,'endpointObject':liner.name,'centerlineWorldAtRest':[list(p) for p in points],'seatCenterSurfaceDistanceM':journal_bvh.find_nearest(seat)[3],'linerCenterSurfaceDistanceM':liner_bvh.find_nearest(end)[3],'authoredSeatTargetDistanceM':seat_distance,'authoredLinerTargetDistanceM':end_distance,'radiusM':FORK_RADIUS_M,'ownership':'One rigid owner shared with retained journal and nested liner; no rigid bridge across mantle elbow hinge'})
    bpy.context.view_layer.update();assert nodes=={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'};outside={n:s for n,s in original.items() if n not in changed};assert all(snapshot(bpy.data.objects[n])==s for n,s in outside.items())
    return {'region':'short-shield nested interface and captive receiving forks','study':'V29 coarse01; visual gate first','status':'inferred passive construction proposal; no clearance or engineering acceptance','changedMeshes':changed,'removed':[],'added':[],'changedNodes':[],'nodesExact':len(nodes),'outsideMeshesExact':len(outside),'nestingRecessM':RECESS_M,'receivers':receivers,'construction':'Whole canopy/coverage and outside silhouette unchanged. Independent short shield plates/fold/liner recessed inboard in tucked space; four new braced receiving forks start on evaluated inner elbow journal seats and terminate on evaluated recessed liner surfaces.','preserved':['All named pivots, current root/rest transforms and left restriction','Complete current mantle exterior, canopy return and backing','Actual journal/race/load machinery, body/head/neck/feet','Material definitions, passive three-era tags, runtime APIs'],'limits':['Shield-side nesting only; retained bearing-strap and inherited machinery crossings remain explicit screening subjects.','Finite passive proposal, not physical simulation or continuous collision proof.']}
