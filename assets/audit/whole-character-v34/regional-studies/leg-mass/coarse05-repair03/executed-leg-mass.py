"""V34 substantial paired passive leg frame, current rests / native Z-up.

A qualitative construction proposal composed on V33 Form06. Named rigid owners, rests, ground digits, metadata and materials remain.
Declared passive journal/race/truss meshes may be reconstructed together.
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


def _profile(centers,widths,depths,channel=False):
    # Fixed native-X section planes separate the nested rigid members even
    # when the knee folds; taper is an authored section, not a pose scale.
    cross=((-1,-1),(1,-1),(1,1),(.52,1),(.52,-.55),(-.52,-.55),(-.52,1),(-1,1)) if channel else ((-.72,-1),(.72,-1),(1,-.72),(1,.72),(.72,1),(-.72,1),(-1,.72),(-1,-.72))
    axis=centers[-1]-centers[0];v=Vector((0,axis.z,-axis.y)).normalized()
    if v.y>0:v.negate()
    verts=[];faces=[]
    for c,w,d in zip(centers,widths,depths):verts.extend(c+Vector((x*w,0,0))+v*y*d for x,y in cross)
    for j in range(len(centers)-1):
        for k in range(8):
            i=j*8+k;n=j*8+(k+1)%8;faces.append((i,n,n+8,i+8))
    faces.extend((tuple(reversed(range(8))),tuple(range((len(centers)-1)*8,len(centers)*8))))
    return verts,faces

def _ring(c,x,inner,outer,thickness,center_angle=None,sweep=math.pi*1.25):
    n=64;opened=center_angle is not None;count=n+1 if opened else n
    angles=[center_angle-sweep*.5+sweep*i/n if opened else 2*math.pi*i/n for i in range(count)]
    verts=[];faces=[]
    for dx in (-thickness*.5,thickness*.5):
        for r in (inner,outer):verts.extend(c+Vector((x+dx,r*math.cos(a),r*math.sin(a))) for a in angles)
    for i in range(n):
        j=(i+1)%count;faces.extend(((i,j,count+j,count+i),(2*count+i,3*count+i,3*count+j,2*count+j),(i,2*count+i,2*count+j,j),(count+i,count+j,3*count+j,3*count+i)))
    if opened:faces.extend(((0,count,3*count,2*count),(count-1,3*count-1,4*count-1,2*count-1)))
    return verts,faces

def _shaft(c,half,r):
    n=48;v=[];f=[]
    for x in (-half,half):v.extend(c+Vector((x,r*math.cos(2*math.pi*i/n),r*math.sin(2*math.pi*i/n))) for i in range(n))
    for i in range(n):f.append((i,(i+1)%n,(i+1)%n+n,i+n))
    f.extend((tuple(reversed(range(n))),tuple(range(n,2*n))));return v,f

def _joined(parts):
    v=[];f=[]
    for vv,ff in parts:
        n=len(v);v.extend(vv);f.extend(tuple(i+n for i in x) for x in ff)
    return v,f

# Ten actual V33 owner-relative transforms, frozen with the same diagnostic samples.
POSE_SAMPLE_SHA256='d9deb3bb14fd32287fa0789f4a1acdbb53301840967929c107a8101d8bcadf5b'
RECEIVER_RELATIVE_POSES={'body|left-thigh': [[[1.0, 0.0, 0.0, 0.2314999998], [0.0, 1.0, 0.0, 0.0554054165], [0.0, 0.0, 1.0, -0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, 0.1373688724, 0.024534975, 0.2314999998], [-0.139502, 0.9702580252, 0.1978346698, 0.0554054165], [0.0033710692, -0.1993217435, 0.9799283027, -0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.9882942292, 0.1460538607, 0.0440770507, 0.2314999998], [-0.1390336983, 0.7433262687, 0.6543207845, 0.0554054165], [0.0628024471, -0.6527896507, 0.7549314701, -0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.9905377951, 0.1355625913, 0.0213929976, 0.2314999998], [-0.1370634219, 0.9692594139, 0.2043276948, 0.0554054165], [0.0069638274, -0.2053265018, 0.9786687554, -0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.9961607081, 0.0841328399, 0.0241972891, 0.2314999998], [-0.0874687351, 0.9451238059, 0.3147859778, 0.0554054165], [0.0036144042, -0.3156939288, 0.9488541929, -0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.9912544782, 0.131293251, 0.0132906651, 0.2314999998], [-0.130983112, 0.9666237646, 0.220186108, 0.0554054165], [0.0160618772, -0.2200013182, 0.9753673339, -0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.9905739393, 0.1353561304, 0.0210235295, 0.2314999998], [-0.1367799336, 0.9691409835, 0.2050780432, 0.0554054165], [0.0073838063, -0.2060205621, 0.9785198043, -0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.9999056337, 0.0133110323, 0.0033970869, 0.2314999998], [-0.0128996497, 0.9947960818, -0.1010660904, 0.0554054165], [-0.0047247027, 0.1010127319, 0.9948739142, -0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, 0.1373688724, 0.024534975, 0.2314999998], [-0.139502, 0.9702580252, 0.1978346698, 0.0554054165], [0.0033710692, -0.1993217435, 0.9799283027, -0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.9907137872, 0.1336277409, 0.0250961882, 0.2314999998], [-0.1359195704, 0.9686582617, 0.2079111408, 0.0554054165], [0.003473066, -0.2093914968, 0.9778257201, -0.0050907731], [0.0, 0.0, 0.0, 1.0]]], 'body|right-thigh': [[[1.0, 0.0, 0.0, -0.2314999998], [0.0, 1.0, 0.0, 0.0554054165], [0.0, 0.0, 1.0, -0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, -0.1373688724, -0.024534975, -0.2314999998], [0.139502, 0.9702580252, 0.1978346698, 0.0554054165], [-0.0033710692, -0.1993217435, 0.9799283027, -0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, -0.1373688724, -0.024534975, -0.2314999998], [0.139502, 0.9702580252, 0.1978346698, 0.0554054165], [-0.0033710692, -0.1993217435, 0.9799283027, -0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.99038845, -0.1353967808, -0.0282565015, -0.2314999998], [0.1383137131, 0.9697760037, 0.2010070132, 0.0554054165], [0.0001867746, -0.2029832859, 0.9791821847, -0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.9934085327, -0.0912391263, -0.0693895447, -0.2314999998], [0.0958464412, 0.9931890899, 0.0662487087, 0.0554054165], [0.0628724644, -0.0724627734, 0.9953874621, -0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.9893285118, -0.0763598061, -0.1240897893, -0.2314999998], [0.0628960777, 0.9920482222, -0.1090156329, 0.0554054165], [0.1314274675, 0.1000475129, 0.9862643236, -0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.9901528679, -0.0803434232, -0.1146395769, -0.2314999998], [0.0672923902, 0.9912568906, -0.1134967448, 0.0554054165], [0.1227559875, 0.1046647562, 0.986902354, -0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.9996519966, -0.0258122798, -0.0054416834, -0.2314999998], [0.0258487264, 0.9996431627, 0.0067372509, 0.0554054165], [0.0052658378, -0.0068755669, 0.9999624981, -0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, -0.1373688724, -0.024534975, -0.2314999998], [0.139502, 0.9702580252, 0.1978346698, 0.0554054165], [-0.0033710692, -0.1993217435, 0.9799283027, -0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.9907137872, -0.1336277409, -0.0250961882, -0.2314999998], [0.1359195704, 0.9686582617, 0.2079111408, 0.0554054165], [-0.003473066, -0.2093914968, 0.9778257201, -0.0050907731], [0.0, 0.0, 0.0, 1.0]]], 'left-foot|left-shin': [[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, -0.1116000041], [0.0, 0.0, 1.0, 0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, 0.1258066025, -0.060372766, -0.0236392859], [-0.139502, 0.9029338052, -0.406509207, -0.165402372], [0.0033710692, 0.4109540633, 0.9116498197, 0.0990898275], [0.0, 0.0, 0.0, 1.0]], [[0.9882942292, 0.0765778835, -0.131948264, -0.0295258634], [-0.1460018585, 0.7256097166, -0.6724388422, -0.1878958095], [0.0442489991, 0.683832119, 0.7282964089, 0.0394834468], [0.0, 0.0, 0.0, 1.0]], [[0.9905562627, 0.122813245, -0.0609524178, -0.0233973918], [-0.1370634219, 0.8981974419, -0.4176780742, -0.1666496435], [0.003450906, 0.4220879792, 0.9065483049, 0.0970361417], [0.0, 0.0, 0.0, 1.0]], [[0.9960704909, 0.0769620991, -0.0438225102, -0.0155567488], [-0.0849476896, 0.6902895612, -0.7185292003, -0.191282446], [-0.0250492941, 0.7194283543, 0.6941148146, 0.030076034], [0.0, 0.0, 0.0, 1.0]], [[0.9913777082, 0.1153439107, -0.0621773426, -0.0227585771], [-0.130983112, 0.8856996818, -0.4453981343, -0.1696623824], [0.00369649, 0.4497019635, 0.8931710251, 0.0918274337], [0.0, 0.0, 0.0, 1.0]], [[0.990595413, 0.1224651059, -0.0610166014, -0.0233687447], [-0.1367799336, 0.897636307, -0.4189753098, -0.1667932812], [0.0034608611, 0.4233808667, 0.9059451772, 0.0967959581], [0.0, 0.0, 0.0, 1.0]], [[0.9999051439, 0.0125149841, -0.005751385, -0.0023111424], [-0.0121893654, 0.609654166, -0.7925737929, -0.1940566243], [-0.0064126926, 0.7925687182, 0.6097488863, 0.0084993882], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, 0.1258066025, -0.060372766, -0.0236392859], [-0.139502, 0.9029338052, -0.406509207, -0.165402372], [0.0033710692, 0.4109540633, 0.9116498197, 0.0990898275], [0.0, 0.0, 0.0, 1.0]], [[0.9907137872, 0.1214519252, -0.0611197323, -0.0232720715], [-0.135921512, 0.8959232945, -0.4229028173, -0.1672265827], [0.0033962306, 0.4272831382, 0.9041114895, 0.0960689083], [0.0, 0.0, 0.0, 1.0]]], 'right-foot|right-shin': [[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, -0.1116000041], [0.0, 0.0, 1.0, 0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, -0.1258066025, 0.060372766, 0.0236392859], [0.139502, 0.9029338052, -0.406509207, -0.165402372], [-0.0033710692, 0.4109540633, 0.9116498197, 0.0990898275], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, -0.1258066025, 0.060372766, 0.0236392859], [0.139502, 0.9029338052, -0.406509207, -0.165402372], [-0.0033710692, 0.4109540633, 0.9116498197, 0.0990898275], [0.0, 0.0, 0.0, 1.0]], [[0.9903828842, -0.1243832578, 0.0605850465, 0.0235141932], [0.1383137131, 0.9006462273, -0.4119535048, -0.1660127215], [-0.0033255745, 0.416371443, 0.9091885184, 0.098093901], [0.0, 0.0, 0.0, 1.0]], [[0.9666570819, -0.2329155605, 0.1064162943, 0.0429135661], [0.2520155279, 0.7916019698, -0.5566457538, -0.1768494465], [0.0454121096, 0.5649041186, 0.823905988, 0.0679577332], [0.0, 0.0, 0.0, 1.0]], [[0.9131919629, -0.3672107696, 0.176739044, 0.0690822278], [0.3897448863, 0.6602168486, -0.6420378776, -0.1757642124], [0.1190771285, 0.6551869683, 0.7460232396, 0.0454988114], [0.0, 0.0, 0.0, 1.0]], [[0.9114810833, -0.3731184934, 0.1731612678, 0.0691726634], [0.3938029476, 0.6699155534, -0.6293904907, -0.1748356536], [0.1188338051, 0.641868944, 0.7575505168, 0.0488179398], [0.0, 0.0, 0.0, 1.0]], [[0.9996525314, -0.022513045, 0.0137105563, 0.0046924341], [0.0249931268, 0.6442477251, -0.7644084067, -0.1934389698], [0.0083761661, 0.7644854684, 0.6445865407, 0.0171726653], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, -0.1258066025, 0.060372766, 0.0236392859], [0.139502, 0.9029338052, -0.406509207, -0.165402372], [-0.0033710692, 0.4109540633, 0.9116498197, 0.0990898275], [0.0, 0.0, 0.0, 1.0]], [[0.9907137872, -0.1214519252, 0.0611197323, 0.0232720715], [0.135921512, 0.8959232945, -0.4229028173, -0.1672265827], [-0.0033962306, 0.4272831382, 0.9041114895, 0.0960689083], [0.0, 0.0, 0.0, 1.0]]], 'left-thigh|left-shin': [[[1.0, 0.0, 0.0, 0.0735000074], [0.0, 1.0, 0.0, -0.1241999939], [0.0, 0.0, 1.0, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, -0.0, 0.0735000074], [0.0, 0.8114486014, -0.5844237908, -0.1241999939], [-0.0, 0.5844237908, 0.8114486014, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, 0.0735000074], [-0.0, 0.2306645205, -0.9730333391, -0.1241999939], [-0.0, 0.9730333391, 0.2306645205, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, -0.0, 0.0735000074], [-0.0, 0.8002774456, -0.5996298943, -0.1241999939], [-0.0, 0.5996298943, 0.8002774456, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, 0.0735000074], [-0.0, 0.5426838681, -0.8399370329, -0.1241999939], [-0.0, 0.8399370329, 0.5426838681, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, 0.0735000074], [-0.0, 0.7713007588, -0.6364708473, -0.1241999939], [-0.0, 0.6364708473, 0.7713007588, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, 0.0735000074], [0.0, 0.7989610596, -0.601382761, -0.1241999939], [-0.0, 0.601382761, 0.7989610596, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, 0.0, 0.0735000074], [-0.0, 0.7727450568, -0.634716533, -0.1241999939], [0.0, 0.634716533, 0.7727450568, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, -0.0, 0.0735000074], [0.0, 0.8114486014, -0.5844237908, -0.1241999939], [-0.0, 0.5844237908, 0.8114486014, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, -0.0, 0.0735000074], [0.0, 0.7949432876, -0.6066837475, -0.1241999939], [-0.0, 0.6066837475, 0.7949432876, -0.238800019], [0.0, 0.0, 0.0, 1.0]]], 'right-thigh|right-shin': [[[1.0, 0.0, 0.0, -0.0735000074], [0.0, 1.0, 0.0, -0.1241999939], [0.0, 0.0, 1.0, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, -0.0735000074], [-0.0, 0.8114486014, -0.5844237908, -0.1241999939], [0.0, 0.5844237908, 0.8114486014, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, -0.0735000074], [-0.0, 0.8114486014, -0.5844237908, -0.1241999939], [0.0, 0.5844237908, 0.8114486014, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, -0.0, -0.0735000074], [0.0, 0.8060396446, -0.5918615475, -0.1241999939], [0.0, 0.5918615475, 0.8060396446, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, -0.0, -0.0735000074], [0.0, 0.7825744955, -0.6225569524, -0.1241999939], [-0.0, 0.6225569524, 0.7825744955, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, -0.0735000074], [-0.0, 0.8145927291, -0.5800333488, -0.1241999939], [0.0, 0.5800333488, 0.8145927291, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, -0.0, -0.0735000074], [-0.0, 0.827030093, -0.5621576517, -0.1241999939], [0.0, 0.5621576517, 0.827030093, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, -0.0, -0.0735000074], [-0.0, 0.7310222679, -0.6823536062, -0.1241999939], [-0.0, 0.6823536062, 0.7310222679, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, -0.0735000074], [-0.0, 0.8114486014, -0.5844237908, -0.1241999939], [0.0, 0.5844237908, 0.8114486014, -0.238800019], [0.0, 0.0, 0.0, 1.0]], [[1.0, -0.0, 0.0, -0.0735000074], [-0.0, 0.7949432876, -0.6066837475, -0.1241999939], [0.0, 0.6066837475, 0.7949432876, -0.238800019], [0.0, 0.0, 0.0, 1.0]]], 'left-thigh|body': [[[1.0, 0.0, 0.0, -0.2314999998], [0.0, 1.0, 0.0, -0.0554054165], [0.0, 0.0, 1.0, 0.0050907731], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, -0.139502, 0.0033710692, -0.2214886878], [0.1373688724, 0.9702580252, -0.1993217435, -0.0865731457], [0.024534975, 0.1978346698, 0.9799283027, -0.0116523663], [0.0, 0.0, 0.0, 1.0]], [[0.9882942292, -0.1390336983, 0.0628024471, -0.2207671808], [0.1460538607, 0.7433262687, -0.6527896507, -0.0783189742], [0.0440770507, 0.6543207845, 0.7549314701, -0.042613568], [0.0, 0.0, 0.0, 1.0]], [[0.9905377951, -0.1370634219, 0.0069638274, -0.2216799921], [0.1355625913, 0.9692594139, -0.2053265018, -0.086130232], [0.0213929976, 0.2043276948, 0.9786687554, -0.0112911594], [0.0, 0.0, 0.0, 1.0]], [[0.9961607081, -0.0874687351, 0.0036144042, -0.2257465619], [0.0841328399, 0.9451238059, -0.3156939288, -0.0734488567], [0.0241972891, 0.3147859778, 0.9488541929, -0.0182121192], [0.0, 0.0, 0.0, 1.0]], [[0.9912544782, -0.130983112, 0.0160618772, -0.2221364702], [0.131293251, 0.9666237646, -0.2200013182, -0.0850705567], [0.0132906651, 0.220186108, 0.9753673339, -0.0103109182], [0.0, 0.0, 0.0, 1.0]], [[0.9905739393, -0.1367799336, 0.0073838063, -0.2217019282], [0.1353561304, 0.9691409835, -0.2060205621, -0.086079408], [0.0210235295, 0.2050780432, 0.9785198043, -0.0112479592], [0.0, 0.0, 0.0, 1.0]], [[0.9999056337, -0.0128996497, -0.0047247027, -0.2307874959], [0.0133110323, 0.9947960818, 0.1010127319, -0.0576843623], [0.0033970869, -0.1010660904, 0.9948739142, 0.0098778606], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, -0.139502, 0.0033710692, -0.2214886878], [0.1373688724, 0.9702580252, -0.1993217435, -0.0865731457], [0.024534975, 0.1978346698, 0.9799283027, -0.0116523663], [0.0, 0.0, 0.0, 1.0]], [[0.9907137872, -0.1359195704, 0.003473066, -0.2218018805], [0.1336277409, 0.9686582617, -0.2093914968, -0.0856697011], [0.0250961882, 0.2079111408, 0.9778257201, -0.012351282], [0.0, 0.0, 0.0, 1.0]]], 'left-thigh|breastplate': [[[1.0, 0.0, 0.0, -0.2314999998], [0.0, 1.0, 0.0, -0.2082879925], [0.0, 0.0, 1.0, -0.0231826901], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, -0.139502, 0.0033710692, -0.2002565745], [0.1373688724, 0.9702580252, -0.1993217435, -0.229273176], [0.024534975, 0.1978346698, 0.9799283027, -0.0696038071], [0.0, 0.0, 0.0, 1.0]], [[0.9882942292, -0.1390336983, 0.0628024471, -0.2012869936], [0.1460538607, 0.7433262687, -0.6527896507, -0.1735039848], [0.0440770507, 0.6543207845, 0.7549314701, -0.1639923422], [0.0, 0.0, 0.0, 1.0]], [[0.9905377951, -0.1370634219, 0.0069638274, -0.2009222746], [0.1355625913, 0.9692594139, -0.2053265018, -0.2285078167], [0.0213929976, 0.2043276948, 0.9786687554, -0.0701996588], [0.0, 0.0, 0.0, 1.0]], [[0.9961607081, -0.0874687351, 0.0036144042, -0.2124763081], [0.0841328399, 0.9451238059, -0.3156939288, -0.2090160581], [0.0241972891, 0.3147859778, 0.9488541929, -0.0931648046], [0.0, 0.0, 0.0, 1.0]], [[0.9912544782, -0.130983112, 0.0160618772, -0.2025655595], [0.131293251, 0.9666237646, -0.2200013182, -0.2266302886], [0.0132906651, 0.220186108, 0.9753673339, -0.0715505501], [0.0, 0.0, 0.0, 1.0]], [[0.9905739393, -0.1367799336, 0.0073838063, -0.2009994254], [0.1353561304, 0.9691409835, -0.2060205621, -0.2284192632], [0.0210235295, 0.2050780432, 0.9785198043, -0.0702669624], [0.0, 0.0, 0.0, 1.0]], [[0.9999056337, -0.0128996497, -0.0047247027, -0.2286817805], [0.0133110323, 0.9947960818, 0.1010127319, -0.2126273297], [0.0033970869, -0.1010660904, 0.9948739142, -0.0027994262], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, -0.139502, 0.0033710692, -0.2002565745], [0.1373688724, 0.9702580252, -0.1993217435, -0.229273176], [0.024534975, 0.1978346698, 0.9799283027, -0.0696038071], [0.0, 0.0, 0.0, 1.0]], [[0.9907137872, -0.1359195704, 0.003473066, -0.2011203421], [0.1336277409, 0.9686582617, -0.2093914968, -0.2278404486], [0.0250961882, 0.2079111408, 0.9778257201, -0.0717837924], [0.0, 0.0, 0.0, 1.0]]], 'left-shin|breastplate': [[[1.0, 0.0, 0.0, -0.3050000072], [0.0, 1.0, 0.0, -0.0840879986], [0.0, 0.0, 1.0, 0.2156173289], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, -0.139502, 0.0033710692, -0.2737565819], [0.1258066025, 0.9029338052, 0.4109540633, 0.0136208049], [-0.060372766, -0.406509207, 0.9116498197, 0.1987012969], [0.0, 0.0, 0.0, 1.0]], [[0.9882942292, -0.1390336983, 0.0628024471, -0.274787001], [0.0765778835, 0.8081349351, 0.5839980774, 0.0614176821], [-0.131948264, -0.5723526512, 0.8093219991, 0.0652299038], [0.0, 0.0, 0.0, 1.0]], [[0.9905377951, -0.1370634219, 0.0069638274, -0.274422282], [0.1213155652, 0.8981974419, 0.422520874, 0.0176226181], [-0.0641670488, -0.4176780742, 0.9063264402, 0.1974731544], [0.0, 0.0, 0.0, 1.0]], [[0.9961607081, -0.0874687351, 0.0036144042, -0.2859763155], [0.0659817342, 0.7773038431, 0.625655773, 0.0762961001], [-0.0575348094, -0.6230152132, 0.7800908856, 0.1502740348], [0.0, 0.0, 0.0, 1.0]], [[0.9912544782, -0.130983112, 0.0160618772, -0.2760655669], [0.109725705, 0.8856996818, 0.4511056898, 0.0274448472], [-0.0733132266, -0.4453981343, 0.8923259902, 0.1941935388], [0.0, 0.0, 0.0, 1.0]], [[0.9905739393, -0.1367799336, 0.0073838063, -0.2744994328], [0.1207874656, 0.897636307, 0.423862535, 0.018085737], [-0.064603862, -0.4189753098, 0.9056964341, 0.1973270214], [0.0, 0.0, 0.0, 1.0]], [[0.9999056337, -0.0128996497, -0.0047247027, -0.3021817879], [0.0124422216, 0.7045754362, 0.7095200108, 0.0814616915], [-0.0058236502, -0.7095118418, 0.7046694483, 0.2384945835], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, -0.139502, 0.0033710692, -0.2737565819], [0.1258066025, 0.9029338052, 0.4109540633, 0.0136208049], [-0.060372766, -0.406509207, 0.9116498197, 0.1987012969], [0.0, 0.0, 0.0, 1.0]], [[0.9907137872, -0.1359195704, 0.003473066, -0.2746203494], [0.1214519252, 0.8961646932, 0.4267766074, 0.0189377465], [-0.0611197323, -0.4223916584, 0.9043504106, 0.1956454077], [0.0, 0.0, 0.0, 1.0]]], 'right-shin|right-foot': [[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.1116000041], [0.0, 0.0, 1.0, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, 0.139502, -0.0033710692, 0.0], [-0.1258066025, 0.9029338052, 0.4109540633, 0.1116000041], [0.060372766, -0.406509207, 0.9116498197, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, 0.139502, -0.0033710692, 0.0], [-0.1258066025, 0.9029338052, 0.4109540633, 0.1116000041], [0.060372766, -0.406509207, 0.9116498197, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9903828842, 0.1383137131, -0.0033255745, -0.0], [-0.1243832578, 0.9006462273, 0.416371443, 0.1116000041], [0.0605850465, -0.4119535048, 0.9091885184, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9666570819, 0.2520155279, 0.0454121096, 0.0], [-0.2329155605, 0.7916019698, 0.5649041186, 0.1116000041], [0.1064162943, -0.5566457538, 0.823905988, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9131919629, 0.3897448863, 0.1190771285, -0.0], [-0.3672107696, 0.6602168486, 0.6551869683, 0.1116000041], [0.176739044, -0.6420378776, 0.7460232396, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9114810833, 0.3938029476, 0.1188338051, 0.0], [-0.3731184934, 0.6699155534, 0.641868944, 0.1116000041], [0.1731612678, -0.6293904907, 0.7575505168, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9996525314, 0.0249931268, 0.0083761661, -0.0], [-0.022513045, 0.6442477251, 0.7644854684, 0.1116000041], [0.0137105563, -0.7644084067, 0.6445865407, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, 0.139502, -0.0033710692, 0.0], [-0.1258066025, 0.9029338052, 0.4109540633, 0.1116000041], [0.060372766, -0.406509207, 0.9116498197, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9907137872, 0.135921512, -0.0033962306, -0.0], [-0.1214519252, 0.8959232945, 0.4272831382, 0.1116000041], [0.0611197323, -0.4229028173, 0.9041114895, -0.1589999795], [0.0, 0.0, 0.0, 1.0]]], 'left-shin|left-foot': [[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.1116000041], [0.0, 0.0, 1.0, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, -0.139502, 0.0033710692, -0.0], [0.1258066025, 0.9029338052, 0.4109540633, 0.1116000041], [-0.060372766, -0.406509207, 0.9116498197, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9882942292, -0.1460018585, 0.0442489991, 0.0], [0.0765778835, 0.7256097166, 0.683832119, 0.1116000041], [-0.131948264, -0.6724388422, 0.7282964089, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9905562627, -0.1370634219, 0.003450906, -0.0], [0.122813245, 0.8981974419, 0.4220879792, 0.1116000041], [-0.0609524178, -0.4176780742, 0.9065483049, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9960704909, -0.0849476896, -0.0250492941, 0.0], [0.0769620991, 0.6902895612, 0.7194283543, 0.1116000041], [-0.0438225102, -0.7185292003, 0.6941148146, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9913777082, -0.130983112, 0.00369649, -0.0], [0.1153439107, 0.8856996818, 0.4497019635, 0.1116000041], [-0.0621773426, -0.4453981343, 0.8931710251, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.990595413, -0.1367799336, 0.0034608611, -0.0], [0.1224651059, 0.897636307, 0.4233808667, 0.1116000041], [-0.0610166014, -0.4189753098, 0.9059451772, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9999051439, -0.0121893654, -0.0064126926, 0.0], [0.0125149841, 0.609654166, 0.7925687182, 0.1116000041], [-0.005751385, -0.7925737929, 0.6097488863, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9902160511, -0.139502, 0.0033710692, -0.0], [0.1258066025, 0.9029338052, 0.4109540633, 0.1116000041], [-0.060372766, -0.406509207, 0.9116498197, -0.1589999795], [0.0, 0.0, 0.0, 1.0]], [[0.9907137872, -0.135921512, 0.0033962306, 0.0], [0.1214519252, 0.8959232945, 0.4272831382, 0.1116000041], [-0.0611197323, -0.4229028173, 0.9041114895, -0.1589999795], [0.0, 0.0, 0.0, 1.0]]]}

def _receiving_relief(target,neighbor,reason):
    """Specific evaluated moving-part pockets; each sampled pose is cut separately.

    Independent pose hulls avoid a single large sweep hull deleting the load path.
    The retained neighbor is never hidden, moved, or exempted.
    """
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    ev=neighbor.evaluated_get(dg);mesh=ev.to_mesh();local=neighbor.parent.matrix_world.inverted()@ev.matrix_world
    points=[local@v.co for v in mesh.vertices];ev.to_mesh_clear()
    old=bmesh.new();old.from_mesh(target.data);old_volume=old.calc_volume(signed=True);old.free()
    margin=.0025;key=target.parent.name+'|'+neighbor.parent.name
    for row in RECEIVER_RELATIVE_POSES[key]:
        world=[target.parent.matrix_world@Matrix(row)@p for p in points]
        if any(max(p[k] for p in world)+margin<min((target.matrix_world@v.co)[k] for v in target.data.vertices) or min(p[k] for p in world)-margin>max((target.matrix_world@v.co)[k] for v in target.data.vertices) for k in range(3)):continue
        bm=bmesh.new()
        pp={tuple(round(c,7) for c in p+Vector(d)*margin) for p in world for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))}
        for p in pp:bm.verts.new(p)
        bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
        unused=[v for v in bm.verts if not v.link_faces]
        if unused:bmesh.ops.delete(bm,geom=unused,context='VERTS')
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));cm=bpy.data.meshes.new('V34 temporary specific receiving tool');bm.to_mesh(cm);bm.free()
        cutter=bpy.data.objects.new(cm.name,cm);bpy.context.scene.collection.objects.link(cutter)
        # Isolated raw target prevents existing bevel/skin modifiers being baked twice.
        temp=bpy.data.objects.new('V34 temporary raw receiver',target.data.copy());bpy.context.scene.collection.objects.link(temp);temp.matrix_world=target.matrix_world.copy()
        mod=temp.modifiers.new('Specific finite receiving relief','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
        bpy.context.view_layer.objects.active=temp;bpy.ops.object.modifier_apply(modifier=mod.name)
        target.data=temp.data;tmpmesh=temp.data;bpy.data.objects.remove(temp,do_unlink=True);bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.meshes.remove(cm)
    bm=bmesh.new();bm.from_mesh(target.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    assert len(bm.faces)>0 and all(e.is_manifold for e in bm.edges),target.name
    volume=bm.calc_volume(signed=True);assert volume>1e-10,target.name
    seen=set();components=0
    for v in bm.verts:
        if v in seen:continue
        components+=1;todo=[v];seen.add(v)
        while todo:
            for e in todo.pop().link_edges:
                for n in e.verts:
                    if n not in seen:seen.add(n);todo.append(n)
    assert components==1,(target.name,components)
    bm.to_mesh(target.data);bm.free()
    return {'target':target.name,'retainedNeighbor':neighbor.name,'actualSampleCount':10,'marginM':margin,'volumeBeforeM3':old_volume,'volumeAfterM3':volume,'retainedVolumeFraction':volume/old_volume,'connectedComponents':components,'reason':reason}

def apply():
    bpy.context.view_layer.update();rests={o.name:_record(o) for o in bpy.data.objects if o.type=='EMPTY'};transforms={o.name:_record(o) for o in bpy.data.objects}
    changed=[];contracts=[];foot=[];body=[];reliefs=[];modifier_changes=[]
    def change(n,owner,g):
        o=bpy.data.objects[n];assert o.parent.name==owner,n;changed.append(_replace(o,g))
        if owner.endswith('-foot'):foot.append(n)
    for side in ('left','right'):
        inward=-1 if side=='left' else 1
        for kind,nextkind in (('thigh','shin'),('shin','foot')):
            owner=side+'-'+kind;p0=bpy.data.objects[owner].matrix_world.translation.copy();p1=bpy.data.objects[side+'-'+nextkind].matrix_world.translation.copy();axis=(p1-p0).normalized();radial=Vector((0,axis.y,axis.z)).normalized();u,v=_basis(p1-p0)
            prefix=f'V25 {side} {kind} ';rails={}
            for lateral in (-1,1):
                if kind=='thigh':
                    centers=[p0+axis*.046+Vector((lateral*.055,0,0)),p0.lerp(p1,.30)+Vector((lateral*.085,0,0)),p0.lerp(p1,.61)+Vector((lateral*.090,0,0)),p1-axis*.068+Vector((lateral*.085,0,0))]
                    widths=[.021,.034,.033,.023];depths=[.030,.047,.044,.024]
                else:
                    centers=[p0+axis*.045+Vector((inward*.040+lateral*.034,0,0)),p0.lerp(p1,.42)+Vector((inward*.035+lateral*.025,0,0)),p0.lerp(p1,.54)+Vector((inward*.035+lateral*.025,0,0)),p1-axis*.079+Vector((lateral*.018,0,0))]
                    widths=[.018,.022,.021,.017];depths=[.026,.038,.037,.025]
                rails[lateral]=centers;change(prefix+f'primary load member {lateral}',owner,_profile(centers,widths,depths,True))
                for index,t in enumerate((.28,.72)):
                    c=centers[1] if index==0 else centers[2]
                    change(prefix+f'load channel collar {lateral} {t}',owner,_profile([c-axis*.009,c+axis*.009],[widths[index+1]+.002]*2,[depths[index+1]+.002]*2,True))
                ar=(centers[1] if kind=='shin' else centers[0].lerp(centers[1],.4))-v*.028;br=centers[2].lerp(centers[3],.6)-v*.028
                change(prefix+f'rear return member {lateral}',owner,_profile([ar,ar.lerp(br,.5),br],[.014,.019,.014],[.016,.023,.016]))
                if kind=='thigh':
                    prox=p0+Vector((lateral*.055,0,0))+radial*.047;end=p1+Vector((lateral*.085,0,0))-radial*.074
                    change(prefix+f'proximal terminal gusset {lateral}',owner,_profile([prox,centers[0]],[.019,.021],[.025,.029]))
                    change(prefix+f'distal terminal gusset {lateral}',owner,_profile([end,centers[-1]],[.019,.023],[.020,.024]))
                    change(prefix+f'distal captive cheek {lateral}',owner,_ring(p1,lateral*.085,.064,.075,.014))
                    change(f'V28 {side} thigh proximal formed load cheek {lateral}',owner,_profile([prox,centers[1]],[.020,.027],[.026,.034]))
                else:
                    prox=p0+Vector((lateral*.070,0,0))+radial*.046;end=p1+Vector((lateral*.018,0,0))-radial*.082
                    change(prefix+f'proximal terminal gusset {lateral}',owner,_profile([prox,centers[0]],[.014,.018],[.011,.023]))
                    change(prefix+f'distal terminal gusset {lateral}',owner,_profile([end,centers[-1]],[.017,.017],[.022,.025]))
                    change(prefix+f'proximal journal {lateral}',owner,_ring(p0,lateral*.070,.028,.058,.018))
                    change(prefix+f'proximal retainer rim {lateral}',owner,_ring(p0,lateral*.072,.044,.060,.007))
                    # Connected directional C-fork receives the complete
                    # football envelope, rather than a long excluded return.
                    angle=math.atan2(-axis.z,-axis.y)
                    change(prefix+f'distal captive cheek {lateral}',owner,_ring(p1,lateral*.018,.073,.085,.014,angle,sweep=math.radians(100)))
                    for i in range(6):
                        a=2*math.pi*i/6;c=p0+Vector((lateral*.076,.052*math.cos(a),.052*math.sin(a)))
                        change(prefix+f'journal keeper bolt {lateral} {i}',owner,_shaft(c,.004,.0045))
            for t,x in ((.28,-.027),(.72,.027)):change(prefix+f'transverse cross web {t}',owner,_shaft(p0+Vector((x,0,0)),.034,.032))
            # Source single guard becomes a connected forward channel lip,
            # keeping substantial exposed paired framing and no central cuff.
            c=rails[-1][1];d=rails[-1][2]
            change(prefix+'limited anterior wear guard',owner,_profile([c+v*.048,d+v*.045],[.027,.026],[.006,.006]))
            if kind=='shin':change(prefix+'proximal captive axle',owner,_shaft(p0,.094,.027))
            contracts.append({'owner':owner,'jointCentersWorld':[list(p0),list(p1)],'railStationsWorld':{str(k):[list(p) for p in c] for k,c in rails.items()},'kneeClevisInnerRadiusM':.064,'kneeMovingJournalOuterRadiusM':.060,'ankleDirectionalForkRadiusM':[.073,.085],'oneRigidOwner':True,'continuousTerminalWebs':True})
        owner=side+'-foot';p0=bpy.data.objects[owner].matrix_world.translation.copy()
        # Existing compact spherical/formed bearing core remains exact.
        for lateral in (-1,1):
            change(f'{side} open stepped bearing race {lateral}.002',owner,_ring(p0,lateral*.046,.032,.053,.012))
            change(f'{side} recessed axle cap {lateral}.002',owner,_shaft(p0+Vector((lateral*.054,0,0)),.003,.014))
            for i in range(4):
                a=2*math.pi*i/4+.45;c=p0+Vector((lateral*.055,.047*math.cos(a),.047*math.sin(a)))
                change(f'{side} bearing race pin {lateral} {i}.002',owner,_shaft(c,.0035,.005))
        # Retain the actual original truss/rail topology and distal toe fit.
        # Only the root X envelope nests between the shin's paired returns.
        for name in (f'{side} metatarsal passive rail',f'{side} metatarsal passive rail.001',f'{side.title()} metatarsus open passive truss',f'V21 {side} foot bearing receiver yoke'):
            o=bpy.data.objects[name]
            if 'metatarsus open passive truss' in name:
                end=bpy.data.objects[side+'-toes'].matrix_world.translation.copy();axis=(end-p0).normalized()
                a=p0+axis*.085;b=end-axis*.067
                
                obsolete=[m for m in o.modifiers if m.type=='SOLIDIFY']
                for m in obsolete:modifier_changes.append({'name':name,'removedModifier':m.name,'type':m.type,'reason':'New section is already finite closed metal; legacy open-skin Solidify would produce redundant layered material.'});o.modifiers.remove(m)
                changed.append(_replace(o,_profile([a,a.lerp(b,.5),b],[.014,.032,.040],[.018,.023,.017],True)));foot.append(name);continue
            if 'foot bearing receiver yoke' in name:
                end=bpy.data.objects[side+'-toes'].matrix_world.translation.copy();axis=(end-p0).normalized()
                changed.append(_replace(o,_profile([p0+axis*.041,p0+axis*.084,p0+axis*.130],[.012,.014,.021],[.017,.017,.020],True)));foot.append(name);continue
            world=[o.matrix_world@v.co for v in o.data.vertices];mapped=[]
            for v in world:
                radius=(v-p0).length;t=max(0,min(1,(radius-.065)/.105));blend=t*t*(3-2*t)
                q=v.copy();q.x=p0.x+(v.x-p0.x)*(.40+.60*blend);mapped.append(q)
            changed.append(_replace(o,(mapped,[tuple(p.vertices) for p in o.data.polygons])));foot.append(name)
    # Purposeful receiving arches at specific actual moving interfaces; dense
    # member midspans remain and every new part still has one existing owner.
    for side in ('left','right'):
        hipSide=1 if side=='left' else -1
        for target,neighbors in ((f'V28 spherical inboard hip receiving seat {hipSide}',[f'V25 {side} thigh primary load member {(-1 if side=="left" else 1)}',f'V25 {side} thigh load channel collar {(-1 if side=="left" else 1)} 0.28']), (f'V28 sternal to hip load bow {hipSide}',[f'V25 {side} thigh primary load member {(-1 if side=="left" else 1)}',f'V25 {side} thigh load channel collar {(-1 if side=="left" else 1)} 0.28'])):
            obj=bpy.data.objects[target]
            for name in neighbors:reliefs.append(_receiving_relief(obj,bpy.data.objects[name],'Fixed receiving side-wall follows actual upper-frame articulation; bearing/load bow retained connected.'))
            body.append(target);changed.append({'name':target,'owner':'body','localReceivingPocket':True})
        # Root instep surface and receiving web yield to actual fork metal;
        # toe/talon/hallux contacts remain entirely outside the edited set.
        for target in (f'{side.title()} metatarsus open passive truss',f'V21 {side} foot bearing receiver yoke'):
            for lateral in (-1,1):reliefs.append(_receiving_relief(bpy.data.objects[target],bpy.data.objects[f'V25 {side} shin distal captive cheek {lateral}'],'Local closed receiving lap around actual ankle socket arc; distal metatarsal load path retained connected.'))
        target=f'{side} curved instep guard';obj=bpy.data.objects[target]
        # A finite arched proximal metatarsal guard leaves the real rotating
        # ankle pocket open, while its distal receiving edge covers the truss.
        end=bpy.data.objects[side+'-toes'].matrix_world.translation.copy();axis=(end-bpy.data.objects[side+'-foot'].matrix_world.translation).normalized();p0=bpy.data.objects[side+'-foot'].matrix_world.translation.copy();normal=Vector((0,-axis.z,axis.y)).normalized()
        if normal.z<0:normal.negate()
        vs=[];fs=[];rows=8;cols=12
        for layer in (0,1):
            for j in range(rows):
                t=j/(rows-1);center=p0+axis*(.115+(.241-.115)*t);width=.044+(.057-.044)*t
                for i in range(cols):
                    x=2*i/(cols-1)-1;lift=.016+.016*(1-x*x)
                    vs.append(center+Vector((width*x,0,0))+normal*(lift-layer*.007))
        n=rows*cols
        for layer in (0,1):
            for j in range(rows-1):
                for i in range(cols-1):
                    q=layer*n+j*cols+i;fs.append((q,q+1,q+cols+1,q+cols) if layer==0 else (q,q+cols,q+cols+1,q+1))
        rim=list(range(cols))+[j*cols+cols-1 for j in range(1,rows)]+list(reversed(range((rows-1)*cols,(rows-1)*cols+cols-1)))+[j*cols for j in reversed(range(1,rows-1))]
        for i,q in enumerate(rim):r=rim[(i+1)%len(rim)];fs.append((q,r,r+n,q+n))
        _replace(obj,(vs,fs))
        for mod in list(obj.modifiers):modifier_changes.append({'name':target,'removedModifier':mod.name,'type':mod.type,'reason':'Finite arched metal guard has explicit thickness and curved rim, replacing legacy open skin and modifier thickness.'});obj.modifiers.remove(mod)
        foot.append(target);changed.append({'name':target,'owner':side+'-foot','localReceivingPocket':True})
    bpy.context.view_layer.update();assert rests=={o.name:_record(o) for o in bpy.data.objects if o.type=='EMPTY'};assert transforms=={o.name:_record(o) for o in bpy.data.objects}
    return {'region':'continuous paired lower-limb frames and curved nested joint receivers','changed':changed,'changedMeshes':[x['name'] for x in changed],'changedFootOwnedMeshes':foot,'changedFootMeshes':foot,'additionalChangedBodyMeshes':body,'receivingReliefs':reliefs,'modifierChanges':modifier_changes,'added':[],'removed':[],'structuralContract':contracts,'status':'Coarse05 nested continuous receiver proposal; actual discrete joint fit and visual review required','unchangedRigNodes':len(rests),'materialsOrEraTagsChanged':False,'limits':['Passive reconstructed load structure, not engineering or physics validation.','Actual original distal truss/rail ends and all toes/talons/hallux retained; explicit foot-root/race changes declared.','No movement reduced and no neighbor pairs exempted.','Discrete10-pose geometry screening remains required.']}
