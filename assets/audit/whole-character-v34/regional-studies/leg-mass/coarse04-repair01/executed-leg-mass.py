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

def apply():
    bpy.context.view_layer.update();rests={o.name:_record(o) for o in bpy.data.objects if o.type=='EMPTY'};transforms={o.name:_record(o) for o in bpy.data.objects}
    changed=[];contracts=[];foot=[]
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
                    centers=[p0+axis*.046+Vector((lateral*.055,0,0)),p0.lerp(p1,.30)+Vector((lateral*.085,0,0)),p0.lerp(p1,.61)+Vector((lateral*.100,0,0)),p1-axis*.068+Vector((lateral*.105,0,0))]
                    widths=[.021,.034,.033,.023];depths=[.030,.047,.044,.024]
                else:
                    centers=[p0+axis*.045+Vector((inward*.040+lateral*.034,0,0)),p0.lerp(p1,.42)+Vector((inward*.045+lateral*.034,0,0)),p0.lerp(p1,.54)+Vector((inward*.025+lateral*.034,0,0)),p1-axis*.079+Vector((lateral*.034,0,0))]
                    widths=[.018,.022,.021,.017];depths=[.026,.038,.037,.025]
                rails[lateral]=centers;change(prefix+f'primary load member {lateral}',owner,_profile(centers,widths,depths,True))
                for index,t in enumerate((.28,.72)):
                    c=centers[1] if index==0 else centers[2]
                    change(prefix+f'load channel collar {lateral} {t}',owner,_profile([c-axis*.009,c+axis*.009],[widths[index+1]+.002]*2,[depths[index+1]+.002]*2,True))
                ar=centers[0].lerp(centers[1],.4)-v*.028;br=centers[2].lerp(centers[3],.6)-v*.028
                change(prefix+f'rear return member {lateral}',owner,_profile([ar,ar.lerp(br,.5),br],[.014,.019,.014],[.016,.023,.016]))
                if kind=='thigh':
                    prox=p0+Vector((lateral*.055,0,0))+radial*.047;end=p1+Vector((lateral*.105,0,0))-radial*.074
                    change(prefix+f'proximal terminal gusset {lateral}',owner,_profile([prox,centers[0]],[.019,.021],[.025,.029]))
                    change(prefix+f'distal terminal gusset {lateral}',owner,_profile([end,centers[-1]],[.019,.023],[.020,.024]))
                    change(prefix+f'distal captive cheek {lateral}',owner,_ring(p1,lateral*.105,.064,.080,.016))
                    change(f'V28 {side} thigh proximal formed load cheek {lateral}',owner,_profile([prox,centers[1]],[.020,.027],[.026,.034]))
                else:
                    prox=p0+Vector((lateral*.105,0,0))+radial*.046;end=p1+Vector((lateral*.034,0,0))-radial*.082
                    change(prefix+f'proximal terminal gusset {lateral}',owner,_profile([prox,centers[0]],[.014,.018],[.011,.023]))
                    change(prefix+f'distal terminal gusset {lateral}',owner,_profile([end,centers[-1]],[.017,.017],[.022,.025]))
                    change(prefix+f'proximal journal {lateral}',owner,_ring(p0,lateral*.105,.028,.058,.018))
                    change(prefix+f'proximal retainer rim {lateral}',owner,_ring(p0,lateral*.118,.044,.060,.007))
                    # Connected directional C-fork receives the complete
                    # football envelope, rather than a long excluded return.
                    angle=math.atan2(-axis.z,-axis.y)
                    change(prefix+f'distal captive cheek {lateral}',owner,_ring(p1,lateral*.034,.077,.089,.014,angle))
                    for i in range(6):
                        a=2*math.pi*i/6;c=p0+Vector((lateral*.127,.052*math.cos(a),.052*math.sin(a)))
                        change(prefix+f'journal keeper bolt {lateral} {i}',owner,_shaft(c,.004,.0045))
            for t,x in ((.28,-.027),(.72,.027)):change(prefix+f'transverse cross web {t}',owner,_shaft(p0+Vector((x,0,0)),.034,.032))
            # Source single guard becomes a connected forward channel lip,
            # keeping substantial exposed paired framing and no central cuff.
            c=rails[-1][1];d=rails[-1][2]
            change(prefix+'limited anterior wear guard',owner,_profile([c+v*.048,d+v*.045],[.027,.026],[.006,.006]))
            if kind=='shin':change(prefix+'proximal captive axle',owner,_shaft(p0,.132,.027))
            contracts.append({'owner':owner,'jointCentersWorld':[list(p0),list(p1)],'railStationsWorld':{str(k):[list(p) for p in c] for k,c in rails.items()},'kneeClevisInnerRadiusM':.064,'kneeMovingJournalOuterRadiusM':.060,'ankleDirectionalForkRadiusM':[.077,.089],'oneRigidOwner':True,'continuousTerminalWebs':True})
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
                a=p0+axis*.073;b=end-axis*.067
                changed.append(_replace(o,_profile([a,a.lerp(b,.5),b],[.024,.036,.040],[.019,.023,.017],True)));foot.append(name);continue
            world=[o.matrix_world@v.co for v in o.data.vertices];mapped=[]
            for v in world:
                radius=(v-p0).length;t=max(0,min(1,(radius-.065)/.105));blend=t*t*(3-2*t)
                q=v.copy();q.x=p0.x+(v.x-p0.x)*(.40+.60*blend);mapped.append(q)
            changed.append(_replace(o,(mapped,[tuple(p.vertices) for p in o.data.polygons])));foot.append(name)
    bpy.context.view_layer.update();assert rests=={o.name:_record(o) for o in bpy.data.objects if o.type=='EMPTY'};assert transforms=={o.name:_record(o) for o in bpy.data.objects}
    return {'region':'continuous paired lower-limb frames and curved nested joint receivers','changed':changed,'changedMeshes':[x['name'] for x in changed],'changedFootOwnedMeshes':foot,'added':[],'removed':[],'structuralContract':contracts,'status':'Coarse04 connected C-frame proposal; actual discrete joint fit and visual review required','unchangedRigNodes':len(rests),'materialsOrEraTagsChanged':False,'limits':['Passive reconstructed load structure, not engineering or physics validation.','Actual original distal truss/rail ends and all toes/talons/hallux retained; explicit foot-root/race changes declared.','No movement reduced and no neighbor pairs exempted.','Discrete10-pose geometry screening remains required.']}
