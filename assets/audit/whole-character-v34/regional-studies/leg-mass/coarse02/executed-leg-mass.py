"""V34 substantial paired passive leg frame, current rests / native Z-up.

A qualitative construction proposal composed on V33 Form06. Existing rigid
owners, journal geometry, foot/claw geometry, metadata and materials remain.
No powered components, hidden parts, altered travel or engineering claims.
"""
import bpy,bmesh,math
from mathutils import Vector,Matrix

OWNERS=('left-thigh','left-shin','right-thigh','right-shin')
BASE_SHA256='5fdfe66693db848fcf624b28484c3eaba220a8d7f389248390a4f21a571d108d'

def _record(o):
    return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),tuple(tuple(r) for r in o.matrix_local),tuple((k,repr(o[k])) for k in sorted(o.keys())))

def _basis(delta):
    axis=delta.normalized();u=Vector((1,0,0)) if abs(axis.x)<.9 else Vector((0,1,0));u=(u-axis*u.dot(axis)).normalized()
    v=axis.cross(u).normalized()
    if v.y>0:v.negate()
    return u,v

def _member(a,b,width,depth,scales=(.68,1.10,1.08,.66),channel=False):
    u,v=_basis(b-a)
    # Open forward C section: substantial rear web and two exposed flanges.
    # Finite caps close the metal section, not the central service space.
    cross=((-1,-1),(1,-1),(1,1),(.55,1),(.55,-.58),(-.55,-.58),(-.55,1),(-1,1)) if channel else ((-.72,-1),(.72,-1),(1,-.72),(1,.72),(.72,1),(-.72,1),(-1,.72),(-1,-.72))
    vs=[];fs=[]
    for t,s in zip((0,.27,.70,1),scales):
        c=a.lerp(b,t);vs.extend(c+u*x*width*s+v*y*depth*s for x,y in cross)
    for j in range(3):
        for k in range(8):
            i=j*8+k;n=j*8+(k+1)%8;fs.append((i,n,n+8,i+8))
    fs.extend((tuple(reversed(range(8))),tuple(range(24,32))))
    return vs,fs

def _replace(o,geometry):
    # Owner and object transforms remain exact; evaluated rest used explicitly.
    bpy.context.view_layer.update();inv=o.matrix_world.inverted();vs,fs=geometry
    old=o.data;mesh=bpy.data.meshes.new(o.name+' V34 frame mesh')
    mesh.from_pydata([inv@p for p in vs],[],fs);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges),o.name
    volume=bm.calc_volume(signed=True);assert volume>1e-10,o.name
    bm.to_mesh(mesh);bm.free()
    assert all(math.isfinite(c) for x in mesh.vertices for c in x.co),o.name
    for m in old.materials:mesh.materials.append(m)
    o.data=mesh
    return {'name':o.name,'owner':o.parent.name,'finiteClosedPositiveVolumeM3':volume,'vertices':len(mesh.vertices),'faces':len(mesh.polygons)}

# Frozen relative joint samples from actual V33 GLB/controller, not guessed angles.
POSE_SAMPLE_SHA256='d9deb3bb14fd32287fa0789f4a1acdbb53301840967929c107a8101d8bcadf5b'
RECEIVER_RELATIVE_POSES={'left-thigh|left-shin': [[[1.0, 0.0, 0.0, 0.0735000074], [0.0, 1.0, 0.0, -0.1241999939], [0.0, 0.0, 1.0, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, -0.0, 0.0735000074], [0.0, 0.8114486014, -0.5844237908, -0.1241999939], [-0.0, 0.5844237908, 0.8114486014, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, 0.0735000074], [-0.0, 0.2306645205, -0.9730333391, -0.1241999939], [-0.0, 0.9730333391, 0.2306645205, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, -0.0, 0.0735000074], [-0.0, 0.8002774456, -0.5996298943, -0.1241999939], [-0.0, 0.5996298943, 0.8002774456, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, 0.0735000074], [-0.0, 0.5426838681, -0.8399370329, -0.1241999939], [-0.0, 0.8399370329, 0.5426838681, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, 0.0735000074], [-0.0, 0.7713007588, -0.6364708473, -0.1241999939], [-0.0, 0.6364708473, 0.7713007588, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, 0.0735000074], [0.0, 0.7989610596, -0.601382761, -0.1241999939], [-0.0, 0.601382761, 0.7989610596, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, 0.0, 0.0735000074], [-0.0, 0.7727450568, -0.634716533, -0.1241999939], [0.0, 0.634716533, 0.7727450568, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, -0.0, 0.0735000074], [0.0, 0.8114486014, -0.5844237908, -0.1241999939], [-0.0, 0.5844237908, 0.8114486014, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, -0.0, 0.0735000074], [0.0, 0.7949432876, -0.6066837475, -0.1241999939], [-0.0, 0.6066837475, 0.7949432876, -0.238800019], [0.0, 0.0, 0.0, 1.0]]], 'left-shin|left-thigh': [[[1.0, 0.0, 0.0, -0.0735000074], [0.0, 1.0, 0.0, 0.1241999939], [0.0, 0.0, 1.0, 0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, -0.0, -0.0735000074], [0.0, 0.8114486014, 0.5844237908, 0.2403423237], [-0.0, -0.5844237908, 0.8114486014, 0.1211885102], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, -0.0, -0.0735000074], [-0.0, 0.2306645205, 0.9730333391, 0.2610089119], [0.0, -0.9730333391, 0.2306645205, -0.0657680429], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, -0.0, -0.0735000074], [-0.0, 0.8002774456, 0.5996298943, 0.242586084], [-0.0, -0.5996298943, 0.8002774456, 0.11663224], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, -0.0, -0.0735000074], [-0.0, 0.5426838681, 0.8399370329, 0.2679783126], [0.0, -0.8399370329, 0.5426838681, 0.0252727437], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, -0.0, -0.0735000074], [-0.0, 0.7713007588, 0.6364708473, 0.2477848], [0.0, -0.6364708473, 0.7713007588, 0.1051369605], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, -0.0, -0.0735000074], [-0.0, 0.7989610596, 0.601382761, 0.2428411735], [0.0, -0.601382761, 0.7989610596, 0.116100181], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, -0.0735000074], [0.0, 0.7727450568, 0.634716533, 0.2475452515], [0.0, -0.634716533, 0.7727450568, 0.1056997447], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, -0.0, -0.0735000074], [0.0, 0.8114486014, 0.5844237908, 0.2403423237], [-0.0, -0.5844237908, 0.8114486014, 0.1211885102], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, -0.0, -0.0735000074], [0.0, 0.7949432876, 0.6066837475, 0.2436080419], [-0.0, -0.6066837475, 0.7949432876, 0.1144823545], [0.0, 0.0, 0.0, 1.0]]], 'left-shin|left-foot': [[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.1116000041], [0.0, 0.0, 1.0, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, -0.139502, 0.0033710692, -0.0], [0.1258066025, 0.9029338052, 0.4109540633, 0.1116000041], [-0.060372766, -0.406509207, 0.9116498197, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9882942292, -0.1460018585, 0.0442489991, 0.0], [0.0765778835, 0.7256097166, 0.683832119, 0.1116000041], [-0.131948264, -0.6724388422, 0.7282964089, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9905562627, -0.1370634219, 0.003450906, -0.0], [0.122813245, 0.8981974419, 0.4220879792, 0.1116000041], [-0.0609524178, -0.4176780742, 0.9065483049, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9960704909, -0.0849476896, -0.0250492941, 0.0], [0.0769620991, 0.6902895612, 0.7194283543, 0.1116000041], [-0.0438225102, -0.7185292003, 0.6941148146, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9913777082, -0.130983112, 0.00369649, -0.0], [0.1153439107, 0.8856996818, 0.4497019635, 0.1116000041], [-0.0621773426, -0.4453981343, 0.8931710251, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.990595413, -0.1367799336, 0.0034608611, -0.0], [0.1224651059, 0.897636307, 0.4233808667, 0.1116000041], [-0.0610166014, -0.4189753098, 0.9059451772, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9999051439, -0.0121893654, -0.0064126926, 0.0], [0.0125149841, 0.609654166, 0.7925687182, 0.1116000041], [-0.005751385, -0.7925737929, 0.6097488863, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, -0.139502, 0.0033710692, -0.0], [0.1258066025, 0.9029338052, 0.4109540633, 0.1116000041], [-0.060372766, -0.406509207, 0.9116498197, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9907137872, -0.135921512, 0.0033962306, 0.0], [0.1214519252, 0.8959232945, 0.4272831382, 0.1116000041], [-0.0611197323, -0.4229028173, 0.9041114895, -0.1589999795], [0.0, 0.0, 0.0, 1.0]]], 'right-thigh|right-shin': [[[1.0, 0.0, 0.0, -0.0735000074], [0.0, 1.0, 0.0, -0.1241999939], [0.0, 0.0, 1.0, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, -0.0735000074], [-0.0, 0.8114486014, -0.5844237908, -0.1241999939], [0.0, 0.5844237908, 0.8114486014, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, -0.0735000074], [-0.0, 0.8114486014, -0.5844237908, -0.1241999939], [0.0, 0.5844237908, 0.8114486014, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, -0.0, -0.0735000074], [0.0, 0.8060396446, -0.5918615475, -0.1241999939], [0.0, 0.5918615475, 0.8060396446, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, -0.0, -0.0735000074], [0.0, 0.7825744955, -0.6225569524, -0.1241999939], [-0.0, 0.6225569524, 0.7825744955, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, -0.0735000074], [-0.0, 0.8145927291, -0.5800333488, -0.1241999939], [0.0, 0.5800333488, 0.8145927291, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, -0.0, -0.0735000074], [-0.0, 0.827030093, -0.5621576517, -0.1241999939], [0.0, 0.5621576517, 0.827030093, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, -0.0, -0.0735000074], [-0.0, 0.7310222679, -0.6823536062, -0.1241999939], [-0.0, 0.6823536062, 0.7310222679, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, -0.0735000074], [-0.0, 0.8114486014, -0.5844237908, -0.1241999939], [0.0, 0.5844237908, 0.8114486014, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, -0.0735000074], [-0.0, 0.7949432876, -0.6066837475, -0.1241999939], [0.0, 0.6066837475, 0.7949432876, -0.238800019], [0.0, 0.0, 0.0, 1.0]]], 'right-shin|right-thigh': [[[1.0, 0.0, 0.0, 0.0735000074], [0.0, 1.0, 0.0, 0.1241999939], [0.0, 0.0, 1.0, 0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, 0.0735000074], [-0.0, 0.8114486014, 0.5844237908, 0.2403423237], [0.0, -0.5844237908, 0.8114486014, 0.1211885102], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, 0.0735000074], [-0.0, 0.8114486014, 0.5844237908, 0.2403423237], [0.0, -0.5844237908, 0.8114486014, 0.1211885102], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, 0.0, 0.0735000074], [-0.0, 0.8060396446, 0.5918615475, 0.2414466677], [-0.0, -0.5918615475, 0.8060396446, 0.1189730819], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, -0.0, 0.0735000074], [0.0, 0.7825744955, 0.6225569524, 0.2458623597], [-0.0, -0.6225569524, 0.7825744955, 0.1095572347], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, 0.0735000074], [-0.0, 0.8145927291, 0.5800333488, 0.2396843867], [0.0, -0.5800333488, 0.8145927291, 0.1224846208], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, 0.0735000074], [0.0, 0.827030093, 0.5621576517, 0.2369603904], [-0.0, -0.5621576517, 0.827030093, 0.127674825], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, -0.0, 0.0735000074], [0.0, 0.7310222679, 0.6823536062, 0.2537390154], [-0.0, -0.6823536062, 0.7310222679, 0.0898198178], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, 0.0735000074], [-0.0, 0.8114486014, 0.5844237908, 0.2403423237], [0.0, -0.5844237908, 0.8114486014, 0.1211885102], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, 0.0735000074], [-0.0, 0.7949432876, 0.6066837475, 0.2436080419], [0.0, -0.6066837475, 0.7949432876, 0.1144823545], [0.0, 0.0, 0.0, 1.0]]], 'right-shin|right-foot': [[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.1116000041], [0.0, 0.0, 1.0, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, 0.139502, -0.0033710692, 0.0], [-0.1258066025, 0.9029338052, 0.4109540633, 0.1116000041], [0.060372766, -0.406509207, 0.9116498197, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, 0.139502, -0.0033710692, 0.0], [-0.1258066025, 0.9029338052, 0.4109540633, 0.1116000041], [0.060372766, -0.406509207, 0.9116498197, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9903828842, 0.1383137131, -0.0033255745, -0.0], [-0.1243832578, 0.9006462273, 0.416371443, 0.1116000041], [0.0605850465, -0.4119535048, 0.9091885184, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9666570819, 0.2520155279, 0.0454121096, 0.0], [-0.2329155605, 0.7916019698, 0.5649041186, 0.1116000041], [0.1064162943, -0.5566457538, 0.823905988, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9131919629, 0.3897448863, 0.1190771285, -0.0], [-0.3672107696, 0.6602168486, 0.6551869683, 0.1116000041], [0.176739044, -0.6420378776, 0.7460232396, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9114810833, 0.3938029476, 0.1188338051, 0.0], [-0.3731184934, 0.6699155534, 0.641868944, 0.1116000041], [0.1731612678, -0.6293904907, 0.7575505168, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9996525314, 0.0249931268, 0.0083761661, -0.0], [-0.022513045, 0.6442477251, 0.7644854684, 0.1116000041], [0.0137105563, -0.7644084067, 0.6445865407, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, 0.139502, -0.0033710692, 0.0], [-0.1258066025, 0.9029338052, 0.4109540633, 0.1116000041], [0.060372766, -0.406509207, 0.9116498197, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9907137872, 0.135921512, -0.0033962306, -0.0], [-0.1214519252, 0.8959232945, 0.4272831382, 0.1116000041], [0.0611197323, -0.4229028173, 0.9041114895, -0.1589999795], [0.0, 0.0, 0.0, 1.0]]]}

def _receiving_relief(target,neighbor,description):
    """Finite local pocket around retained actual hardware's sampled sweep."""
    bpy.context.view_layer.update()
    local=neighbor.parent.matrix_world.inverted()@neighbor.matrix_world
    key=target.parent.name+'|'+neighbor.parent.name
    points=[];margin=.0025
    for row in RECEIVER_RELATIVE_POSES[key]:
        rel=Matrix(row)
        for v in neighbor.data.vertices:
            p=target.parent.matrix_world@rel@local@v.co
            points.extend(p+Vector(d)*margin for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)))
    # Convex hull of the actual swept boundary makes a generous finite
    # receiving arch. It never edits or hides the retained neighboring part.
    bm=bmesh.new();uniq={tuple(round(c,7) for c in p) for p in points}
    for p in uniq:bm.verts.new(p)
    bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
    unused=[v for v in bm.verts if not v.link_faces]
    if unused:bmesh.ops.delete(bm,geom=unused,context='VERTS')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    mesh=bpy.data.meshes.new('V34 temporary sampled receiver hull');bm.to_mesh(mesh);bm.free()
    cutter=bpy.data.objects.new(mesh.name,mesh);bpy.context.scene.collection.objects.link(cutter)
    before=bmesh.new();before.from_mesh(target.data);old_volume=before.calc_volume(signed=True);before.free()
    modifier=target.modifiers.new('V34 finite receiving relief','BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
    bpy.context.view_layer.objects.active=target
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.meshes.remove(mesh)
    result=bmesh.new();result.from_mesh(target.data);bmesh.ops.recalc_face_normals(result,faces=list(result.faces))
    assert all(e.is_manifold for e in result.edges),target.name
    volume=result.calc_volume(signed=True);assert volume>1e-10,target.name
    seen=set();components=0
    for v in result.verts:
        if v in seen:continue
        components+=1;todo=[v];seen.add(v)
        while todo:
            for e in todo.pop().link_edges:
                for n in e.verts:
                    if n not in seen:seen.add(n);todo.append(n)
    assert components==1,(target.name,components)
    result.to_mesh(target.data);result.free()
    return {'target':target.name,'retainedNeighbor':neighbor.name,'actualSampleCount':len(RECEIVER_RELATIVE_POSES[key]),'receivingMarginM':margin,'volumeBeforeM3':old_volume,'volumeAfterM3':volume,'retainedVolumeFraction':volume/old_volume,'connectedComponents':components,'reason':description}

def apply():
    bpy.context.view_layer.update();rests={o.name:_record(o) for o in bpy.data.objects if o.type=='EMPTY'}
    transforms={o.name:_record(o) for o in bpy.data.objects}
    changed=[];contracts=[]
    for side in ('left','right'):
        for kind,nextkind in (('thigh','shin'),('shin','foot')):
            owner=bpy.data.objects[side+'-'+kind];distal=bpy.data.objects[side+'-'+nextkind]
            p0=owner.matrix_world.translation.copy();p1=distal.matrix_world.translation.copy();axis=(p1-p0).normalized();u,v=_basis(p1-p0)
            gap=.055 if kind=='thigh' else .061;endgap=.085 if kind=='thigh' else .080
            width=.035 if kind=='thigh' else .031;depth=.046 if kind=='thigh' else .043
            radius=.055 if kind=='thigh' else .058;douter=.075 if kind=='thigh' else .084
            rails={}
            def change(label,geometry):
                name=f'V25 {side} {kind} {label}';o=bpy.data.objects[name]
                assert o.parent==owner and o.get('exteriorEras')=='maker,mechanic,builder',name
                changed.append(_replace(o,geometry));return o
            for lateral in (-1,1):
                # Splayed endpoints use actual X-axis journals, not historical
                # rail offsets. Broad midspan transitions taper at each pivot.
                a=p0+Vector((lateral*gap,0,0))+axis*.046
                b=p1+Vector((lateral*endgap,0,0))-axis*.060
                rails[lateral]=(a,b)
                change(f'primary load member {lateral}',_member(a,b,width,depth,channel=True))
                radial=Vector((0,axis.y,axis.z)).normalized()
                for label,c,anchor,r,offset in (('proximal',p0,a,radius,gap),('distal',p1,b,douter,endgap)):
                    seat=c+Vector((lateral*offset,0,0))+radial*(r*.84 if label=='proximal' else -r*.91)
                    change(f'{label} terminal gusset {lateral}',_member(seat,anchor,.024,.030,(.65,.93,1,.84)))
                for t in (.28,.72):
                    c=a.lerp(b,t)
                    # The old narrow collar is rebuilt as an actual channel
                    # station with the same forward opening, not extra bolts.
                    change(f'load channel collar {lateral} {t}',_member(c-axis*.010,c+axis*.010,width*1.12,depth*1.10,(1,1,1,1),True))
                ar=a.lerp(b,.13)-v*depth*.78;br=a.lerp(b,.88)-v*depth*.78
                change(f'rear return member {lateral}',_member(ar,br,.019,.023,(.72,1,1,.72)))
            for t in (.28,.72):
                a=rails[-1][0].lerp(rails[-1][1],t);b=rails[1][0].lerp(rails[1][1],t)
                # Cross ties are rear-seated. The central forward aperture
                # stays open instead of becoming a flat armored shin sleeve.
                change(f'transverse cross web {t}',_member(a-v*.024,b-v*.024,.017,.030,(1,1,1,1)))
            c0=p0.lerp(p1,.34)+v*(depth*.99);c1=p0.lerp(p1,.62)+v*(depth*.99)
            change('limited anterior wear guard',_member(c0,c1,.025,.006,(.72,1,.88,.56)))
            if kind=='thigh':
                for lateral in (-1,1):
                    n=f'V28 {side} thigh proximal formed load cheek {lateral}';o=bpy.data.objects[n]
                    assert o.parent==owner
                    seat=p0+Vector((lateral*gap,0,0))+Vector((0,axis.y,axis.z)).normalized()*(radius*.87)
                    end=rails[lateral][0].lerp(rails[lateral][1],.13)
                    changed.append(_replace(o,_member(seat,end,.027,.035,(.60,1,1,.87))))
            contracts.append({'owner':owner.name,'proximal':owner.name,'distal':distal.name,'jointCentersWorld':[list(p0),list(p1)],'pairedRailEndpointsWorld':{str(k):[list(a),list(b)] for k,(a,b) in rails.items()},'nominalChannelHalfWidthDepthM':[width,depth],'channelMidspanWidthDepthM':[2*width*1.10,2*depth*1.10],'channelFlangeFraction':.45,'channelRearWebFraction':.42,'actualXJournalOffsetsM':[gap,endgap],'jointsAndFeetUnchanged':True,'oneRigidOwnerPerPart':True})
    reliefs=[]
    for side in ('left','right'):
        # Actual neutral witnesses selected these local ends. The receiving
        # pocket uses actual controller samples at the same unchanged pivot.
        for lateral in (-1,1):
            pairs=[(f'V25 {side} shin distal terminal gusset {lateral}',f'{side} bearing race pin {lateral} 1.002','Ankle gusset receives the retained foot-side race-pin sweep.'),
                   (f'V25 {side} shin rear return member {lateral}',f'V25 {side} thigh distal captive cheek {lateral}','Rear return proximal end receives the upstream knee cheek envelope.')]
            active=1 if side=='left' else -1
            if lateral==active:
                pairs.extend([(f'V25 {side} thigh distal terminal gusset {lateral}',f'V25 {side} shin journal keeper bolt {lateral} 1','Thigh gusset receives retained knee keeper head.'),
                              (f'V25 {side} thigh primary load member {lateral}',f'V25 {side} shin proximal journal {lateral}','Distal channel mouth receives retained knee journal, while broad midspan remains.')])
            for target,neighbor,reason in pairs:reliefs.append(_receiving_relief(bpy.data.objects[target],bpy.data.objects[neighbor],reason))
    bpy.context.view_layer.update()
    assert rests=={o.name:_record(o) for o in bpy.data.objects if o.type=='EMPTY'}
    assert transforms=={o.name:_record(o) for o in bpy.data.objects},'Transforms or inherited metadata changed'
    return {'region':'lower-limb passive structural mass','changed':changed,'changedMeshes':[x['name'] for x in changed],'added':[],'removed':[],'structuralContract':contracts,'receivingReliefs':reliefs,'actualControllerPoseSampleSHA256':POSE_SAMPLE_SHA256,'status':'One coarse inferred construction proposal; visual gate and movement fit remain pending','unchangedRigNodes':len(rests),'materialsOrEraTagsChanged':False,'limits':['Finite solids and exact rests do not prove load capacity.','Receiving reliefs derive from10 discrete actual V33 controller samples; continuous movement clearance is not established.','Foot/claw geometry and circular journals remain exact.','Section dimensions are qualitative construction choices, not measurements from art.']}
