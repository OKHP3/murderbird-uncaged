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

def _ring(c,x,inner,outer,thickness):
    n=64;verts=[];faces=[]
    for dx in (-thickness*.5,thickness*.5):
        for r in (inner,outer):verts.extend(c+Vector((x+dx,r*math.cos(2*math.pi*i/n),r*math.sin(2*math.pi*i/n))) for i in range(n))
    for i in range(n):
        j=(i+1)%n;faces.extend(((i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)))
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
        for kind,nextkind in (('thigh','shin'),('shin','foot')):
            owner=side+'-'+kind;p0=bpy.data.objects[owner].matrix_world.translation.copy();p1=bpy.data.objects[side+'-'+nextkind].matrix_world.translation.copy();axis=(p1-p0).normalized();radial=Vector((0,axis.y,axis.z)).normalized();u,v=_basis(p1-p0)
            prefix=f'V25 {side} {kind} '
            planes=.145 if kind=='thigh' else .086
            rails={}
            for lateral in (-1,1):
                if kind=='thigh':
                    centers=[p0+axis*.055+Vector((lateral*.055,0,0)),p0.lerp(p1,.30)+Vector((lateral*.105,0,0)),p0.lerp(p1,.57)+Vector((lateral*planes,0,0)),p1-axis*.100+Vector((lateral*planes,0,0))]
                    # Monotone station order for the current280mm span.
                    widths=[.020,.034,.034,.023];depths=[.025,.045,.044,.018]
                else:
                    centers=[p0+axis*.067+Vector((lateral*planes,0,0)),p0.lerp(p1,.40)+Vector((lateral*planes,0,0)),p0.lerp(p1,.46)+Vector((lateral*planes,0,0)),p1-axis*.097+Vector((lateral*planes,0,0))]
                    widths=[.020,.022,.022,.020];depths=[.019,.038,.036,.018]
                rails[lateral]=centers
                change(prefix+f'primary load member {lateral}',owner,_profile(centers,widths,depths,True))
                for index,t in enumerate((.28,.72)):
                    c=centers[1] if index==0 else centers[2]
                    change(prefix+f'load channel collar {lateral} {t}',owner,_profile([c-axis*.009,c+axis*.009],[widths[index+1]+.002]*2,[depths[index+1]+.002]*2,True))
                ar=centers[1]-v*.025;br=centers[2]-v*.025
                change(prefix+f'rear return member {lateral}',owner,_profile([ar,ar.lerp(br,.5),br],[.014,.016,.014],[.015,.019,.015]))
                if kind=='thigh':
                    prox=p0+Vector((lateral*.055,0,0))+radial*.047
                    end=p1+Vector((lateral*planes,0,0))-radial*.081
                    change(prefix+f'proximal terminal gusset {lateral}',owner,_profile([prox,centers[0]],[.017,.020],[.018,.023]))
                    change(prefix+f'distal terminal gusset {lateral}',owner,_profile([end,centers[-1]],[.016,.023],[.012,.018]))
                    change(prefix+f'distal captive cheek {lateral}',owner,_ring(p1,lateral*planes,.074,.090,.018))
                    change(f'V28 {side} thigh proximal formed load cheek {lateral}',owner,_profile([prox,centers[1]],[.019,.027],[.020,.032]))
                else:
                    # Shin journal nests concentrically in thigh clevis, but
                    # its webs route inward before expanding into shin rails.
                    prox=p0+Vector((lateral*.145,0,0))+radial*.046
                    end=p1+Vector((lateral*planes,0,0))-radial*.083
                    change(prefix+f'proximal terminal gusset {lateral}',owner,_profile([prox,centers[0]],[.012,.020],[.010,.018]))
                    change(prefix+f'distal terminal gusset {lateral}',owner,_profile([end,centers[-1]],[.014,.020],[.011,.018]))
                    change(prefix+f'proximal journal {lateral}',owner,_ring(p0,lateral*.145,.028,.058,.020))
                    change(prefix+f'proximal retainer rim {lateral}',owner,_ring(p0,lateral*.160,.044,.060,.007))
                    change(prefix+f'distal captive cheek {lateral}',owner,_ring(p1,lateral*planes,.074,.092,.014))
                    for i in range(6):
                        a=2*math.pi*i/6;c=p0+Vector((lateral*.168,.052*math.cos(a),.052*math.sin(a)))
                        change(prefix+f'journal keeper bolt {lateral} {i}',owner,_shaft(c,.004,.0045))
            # Cross ties are confined inside the proximal bearing cylinder,
            # leaving the nested downstream planes unobstructed at full fold.
            for t,x in ((.28,-.027),(.72,.027)):
                change(prefix+f'transverse cross web {t}',owner,_shaft(p0+Vector((x,0,0)),.034,.032))
            c0=p0+axis*.026+v*.021;c1=p0+axis*.045+v*.021
            change(prefix+'limited anterior wear guard',owner,_profile([c0,c1],[.024,.025],[.006,.006]))
            if kind=='shin':change(prefix+'proximal captive axle',owner,_shaft(p0,.173,.027))
            contracts.append({'owner':owner,'jointCentersWorld':[list(p0),list(p1)],'memberPlanesNativeXOffsetM':[-planes,planes],'railStationsWorld':{str(k):[list(p) for p in c] for k,c in rails.items()},'nestedKneeThighClevisInnerRadiusM':.074,'nestedShinKneeJournalOuterRadiusM':.060,'ankleShinClevisInnerRadiusM':.074,'footRaceOuterRadiusM':.063,'singleRigidOwner':True})
        # The foot-owned race, receiver and metatarsal root form the third,
        # innermost load plane; toes, claws, floor patches and hallux unchanged.
        owner=side+'-foot';p0=bpy.data.objects[owner].matrix_world.translation.copy();p1=bpy.data.objects[side+'-toes'].matrix_world.translation.copy();axis=(p1-p0).normalized();u,v=_basis(p1-p0)
        change(f'{side} articulated bearing core.002',owner,_shaft(p0,.109,.046))
        for lateral in (-1,1):
            change(f'{side} open stepped bearing race {lateral}.002',owner,_ring(p0,lateral*.086,.046,.063,.014))
            change(f'{side} recessed axle cap {lateral}.002',owner,_shaft(p0+Vector((lateral*.112,0,0)),.003,.014))
            for i in range(4):
                a=2*math.pi*i/4+.45;c=p0+Vector((lateral*.099,.054*math.cos(a),.054*math.sin(a)))
                change(f'{side} bearing race pin {lateral} {i}.002',owner,_shaft(c,.0035,.005))
            name=f'{side} metatarsal passive rail'+('' if lateral==-1 else '.001')
            centers=[p0+axis*.067+Vector((lateral*.038,0,0)),p0.lerp(p1,.48)+Vector((lateral*.038,0,0)),p1-axis*.020+Vector((lateral*.045,0,0))]
            change(name,owner,_profile(centers,[.014,.018,.019],[.016,.021,.016],True))
        a=p0+axis*.082;b=p1-axis*.035
        change(f'{side.title()} metatarsus open passive truss',owner,_profile([a,a.lerp(b,.5),b],[.038,.041,.045],[.017,.021,.016],True))
        parts=[]
        for lateral in (-1,1):
            a=p0+axis*.030+Vector((lateral*.030,0,0));b=p0+axis*.082+Vector((lateral*.038,0,0))
            parts.append(_profile([a,b],[.011,.014],[.015,.018]))
        change(f'V21 {side} foot bearing receiver yoke',owner,_joined(parts))
    bpy.context.view_layer.update();assert rests=={o.name:_record(o) for o in bpy.data.objects if o.type=='EMPTY'};assert transforms=={o.name:_record(o) for o in bpy.data.objects}
    return {'region':'nested passive lower-limb structure','changed':changed,'changedMeshes':[x['name'] for x in changed],'changedFootOwnedMeshes':foot,'added':[],'removed':[],'structuralContract':contracts,'status':'Coarse03 interleaved member planes; actual discrete joint fit and visual review required','unchangedRigNodes':len(rests),'materialsOrEraTagsChanged':False,'limits':['Qualitative passive load structure, not load or engineering validation.','Named pivots and ground-contact toes/talons/hallux exact; explicitly declared foot-owned ankle/truss geometry revised.','No motion limits changed or pairs exempted.','Discrete actual poses cannot establish continuous movement clearance.']}
