"""Cranial casting, formed coverings and open mandible for the retained04 Advanced bird.

Blender-native authoring. The sagittal drawing coordinates below are hand-laid guide
stations. Physical coordinates are in the retained scene's native space, with forward
along -Y. The reference photographs/illustrations are not texture inputs.
"""
from math import cos, pi, sin, sqrt
import bpy
import bmesh
from mathutils import Vector

EYE_U = 916.0
EYE_V = 114.0
EYE_Y = -0.2694
EYE_Z = 1.6956
UNIT_U = 0.00215
UNIT_V = 0.00202
STOCK = {}
CREATED = []
PINS = []


def point(u, v, x):
    return Vector((x, EYE_Y - (u - EYE_U) * UNIT_U, EYE_Z + (EYE_V - v) * UNIT_V))


def interpolate(rows, u):
    """Piecewise cubic Hermite with limited slope for monotonic guide channels."""
    if u <= rows[0][0]:
        return list(rows[0][1:])
    if u >= rows[-1][0]:
        return list(rows[-1][1:])
    i = next(k for k in range(len(rows) - 1) if rows[k][0] <= u <= rows[k + 1][0])
    a, b = rows[i:i + 2]
    p = rows[max(0, i - 1)]
    n = rows[min(len(rows) - 1, i + 2)]
    length = b[0] - a[0]
    t = (u - a[0]) / length
    values = []
    for k in range(1, len(a)):
        delta = (b[k] - a[k]) / length
        prev = (a[k] - p[k]) / (a[0] - p[0]) if i else delta
        nxt = (n[k] - b[k]) / (n[0] - b[0]) if b != n else delta
        m0 = 2 * prev * delta / (prev + delta) if prev * delta > 0 else 0.0
        m1 = 2 * nxt * delta / (nxt + delta) if nxt * delta > 0 else 0.0
        values.append((2*t**3-3*t*t+1)*a[k] + (t**3-2*t*t+t)*length*m0 +
                      (-2*t**3+3*t*t)*b[k] + (t**3-t*t)*length*m1)
    return values


def mesh_object(label, vertices, faces, family, assigned=None):
    mesh = bpy.data.meshes.new('FC head | ' + label)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new('FC head | ' + label, mesh)
    bpy.context.scene.collection.objects.link(obj)
    families = [family] if isinstance(family, str) else family
    for key in families:
        mesh.materials.append(STOCK[key])
    if assigned:
        for poly, idx in zip(mesh.polygons, assigned):
            poly.material_index = idx
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    uv = mesh.uv_layers.new(name='UVMap')
    for p in mesh.polygons:
        p.use_smooth = True
        direction = max(range(3), key=lambda i: abs(p.normal[i]))
        axes = ((1, 2), (0, 2), (1, 0))[direction]
        for li in p.loop_indices:
            xyz = mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv = (xyz[axes[0]] * 3.65 + .29, xyz[axes[1]] * 3.65 + .17)
    if hasattr(mesh, 'set_sharp_from_angle'):
        mesh.set_sharp_from_angle(angle=.91)
    obj['fc_region'] = 'head'
    obj['cg1cRegion'] = 'head'
    obj['cg2bRegion'] = 'head'
    obj['cg2bSurfaceFamily'] = families[0]
    obj['surfaceRole'] = families[0]
    CREATED.append(obj)
    return obj


def formed_panel(label, sample, family, length=18, width=8, rim='black-iron', thickness=.0022):
    """Form a cambered sheet with returned edge and a separate cut-edge material."""
    verts, faces, mats = [], [], []
    dims = (length + 1) * (width + 1)
    # Obtain surface normals from the drawn shell rather than extruding it on a world axis.
    for layer in (0, 1):
        for i in range(length+1):
            t = i / length
            for j in range(width+1):
                s = 2*j/width-1
                pos, normal = sample(t, s)
                verts.append(pos - normal * thickness * layer)
    idx = lambda i, j: i*(width+1)+j
    for i in range(length):
        for j in range(width):
            a, b = idx(i,j), idx(i+1,j)
            faces.extend([(a,b,b+1,a+1),(dims+a+1,dims+b+1,dims+b,dims+a)])
            mats.extend((0,1))
    boundary = [idx(0,j) for j in range(width+1)] + [idx(i,width) for i in range(1,length+1)]
    boundary += [idx(length,j) for j in reversed(range(width))] + [idx(i,0) for i in reversed(range(1,length))]
    for a,b in zip(boundary,boundary[1:]+boundary[:1]):
        faces.append((a,b,b+dims,a+dims))
        mats.append(1)
    return mesh_object(label,verts,faces,[family,rim],mats)


def volume(label, stations, ring, family, segments=36, steps=3):
    verts, faces = [], []
    samples = []
    for a,b in zip(stations[:-1],stations[1:]):
        samples.extend(a[0]+(b[0]-a[0])*i/steps for i in range(steps))
    samples.append(stations[-1][0])
    for u in samples:
        data = interpolate(stations,u)
        for j in range(segments):
            verts.append(ring(u,data,2*pi*j/segments))
    for i in range(len(samples)-1):
        for j in range(segments):
            a = i*segments+j
            b = i*segments+(j+1)%segments
            faces.append((a,b,b+segments,a+segments))
    faces.append(tuple(reversed(range(segments))))
    faces.append(tuple(range(len(verts)-segments,len(verts))))
    return mesh_object(label,verts,faces,family)


# Rear-to-front occipital bed. Its narrow orbital station leaves the optical units
# exposed. Small feather undersides and the landings behind each hinge have thickness.
BRAIN = [
    (730,111,125,.018),(741,85,153,.045),(758,64,173,.074),
    (781,49,188,.105),(806,43,187,.125),(832,36,175,.140),
    (858,40,161,.144),(882,50,151,.144),(901,59,151,.129),
    (921,68,153,.121),(941,80,151,.110),(959,99,152,.102),
    (974,118,160,.082),(984,138,168,.045),(988,156,162,.010),
]


def flank(u,v):
    top, bottom, width=interpolate(BRAIN,u)
    d=max(-1,min(1,(v-(top+bottom)/2)/((bottom-top)/2)))
    return width*max(0.0,1-d*d)**.45


def bed_ring(u,data,theta):
    top,bottom,span=data
    return point(u, (top+bottom)/2-(bottom-top)*cos(theta)/2, span*sin(theta))


# Same parent casting carries the brow and the upper bill. Courses overlap the
# casting by millimetres; their eccentric hems travel around the eye rather than
# forming a disconnected planar visor.
BROW=[
    (817,32,.036,47),(833,27,.058,48),(852,30,.101,59),
    (875,38,.141,74),(898,46,.164,82),(916,53,.171,83),
    (933,64,.168,91),(948,77,.151,107),(961,88,.133,114),
    (975,106,.104,122),(985,124,.077,137),
]


def arch_pos(u,s,offset=0.0):
    top,w,hem = interpolate(BROW,u)
    theta=abs(s)*1.18
    x=(1 if s>=0 else -1)*w*sin(theta)/sin(1.18)
    v=top+(hem-top)*(1-cos(theta))/(1-cos(1.18))
    outward=Vector(((1 if s>=0 else -1)*sin(theta),-.16,cos(theta))).normalized()
    return point(u+.8*s*s,v,x)+offset*outward, outward


def brow_course(label,start,end,slant0,slant1,offset,family,make_pins):
    def sample(t,s):
        edge=abs(s)**1.45
        u=(1-t)*(start+slant0*edge)+t*(end+slant1*edge)
        return arch_pos(u,s,offset+.0008*(1-s*s)*sin(pi*t))
    formed_panel(label,sample,family,20,18,'machined-steel',.0031)
    if make_pins:
        for t, s, radius in make_pins:
            p,n=sample(t,s)
            PINS.append((p,n,radius))


# A continuous hooked upper blade. Each section controls the inside cutting edge,
# outside ridge and transverse camber at its height. The front turns back behind
# its maximum projection as the tip descends.
BLADE=[
    (88,938,960,.074),(99,933,977,.089),(111,937,990,.104),
    (126,942,1001,.105),(142,945,1012,.100),(157,949,1020,.094),
    (171,959,1026,.085),(184,971,1028,.074),(200,981,1026,.061),
    (215,987,1020,.045),(228,988,1010,.032),(240,984,1000,.020),
    (250,979,987,.009),(258,973,974,.0012),
]


def bill_ring(v,data,theta):
    inner,outer,w=data
    # Flatten the flanks aft of the median keel and sharpen toward the cutting edge.
    f=(1+sin(theta))*.5
    u=inner+(outer-inner)*f
    cx=cos(theta)
    x=(1 if cx>=0 else -1)*w*abs(cx)**.87*(.78+.27*sin(pi*f))
    return point(u,v,x)


def blade_depth(u,v):
    inner,outer,w=interpolate(BLADE,v)
    f=min(.999,max(.001,(u-inner)/(outer-inner)))
    return w*(max(.0001,1-(2*f-1)**2))**(.87/2)*(.78+.27*sin(pi*f))


def side_panel(label,rows,side,family,thickness=.003,camber=.002,pins=(),curl=False):
    def sample(t,s):
        u=rows[0][0]+(rows[-1][0]-rows[0][0])*t
        top,bottom,outer,lean=interpolate(rows,u)
        q=(s+1)*.5
        v=top+(bottom-top)*q
        w=outer+lean*s+camber*(1-s*s)
        if curl and u>949:
            # The cheek curls into the blade's flank around its bore. The terminal
            # edge tucks under the blade, so the crossing has an actual landing.
            a=max(0,min(1,(u-949)/19))
            a=a*a*(3-2*a)
            tip=max(0,min(1,(u-965)/12))
            w=(1-a)*w+a*(blade_depth(u,v)+.0024-.0049*tip)
        return point(u,v,side*w), Vector((side,0,0))
    formed_panel(label,sample,family,26,6,'machined-steel',thickness)
    for t,s,radius in pins:
        p,n=sample(t,s)
        PINS.append((p,n,radius))



def orbital_fender(side, label, a0, a1, width, family, depth=.002):
    # Conical return from the relatively flat annular seat onto the domed casting.
    # Broken, tapered ends leave the intervening black throat and ring visible.
    def sample(t,s):
        angle=(a0+(a1-a0)*t)*pi/180
        q=(s+1)*.5
        taper=.17+.83*sin(pi*t)**.64
        inner=.0666+.0012*cos(2*angle)
        r=inner+q*(width*taper+.0015)
        u=EYE_U+r*cos(angle)/UNIT_U
        v=EYE_V+r*sin(angle)/UNIT_V
        margin=.1672
        underlying=max(.142,min(.158,flank(u,v)))
        x=margin*(1-q)+underlying*q+.0020*sin(pi*q)+depth
        return point(u,v,side*x),Vector((side,0,0))
    formed_panel(label,sample,family,30,8,'black-iron',.0029)


def poll_return():
    controls=[(748,71,.004,4),(763,58,.031,8),(782,46,.050,12),
              (802,37,.069,14),(820,31,.081,15),(834,30,.076,13),(845,36,.055,7)]
    def sample(t,s):
        u=748+97*t
        top,w,rise=interpolate(controls,u)
        n=Vector((s*.73,.12,.94-.32*abs(s))).normalized()
        return point(u+.7*s*s,top+rise*s*s,w*s),n
    formed_panel('swept sagittal poll return',sample,'head-armor',23,14,'black-iron',.0025)

def blade_lap(side,label,start,end,finish):
    # Three small upper bill lames seated on the same continuous blade. The diagonal
    # overlap is controlled across each side. The lower blade stays uninterrupted.
    def sample(t,s):
        v=start+(end-start)*t + (s*.5)*8*(.75+.25*t)
        inn,out,_=interpolate(BLADE,v)
        r=(s+1)*.5
        f=.075+.865*r
        u=inn+(out-inn)*f
        x=blade_depth(u,v)+.0018+.0015*sin(pi*t)*sin(pi*r)
        return point(u,v,side*x),Vector((side,0,0))
    formed_panel(label,sample,finish,12,14,'machined-steel',.0024)
    for t,s in ((.56,-.48),(.83,.2)):
        p,n=sample(t,s)
        PINS.append((p,n,.0034))


# Tapered, overlapping occipital feathers. Backward sweep and the direction of
# taper change from the high poll to the lower nape. The occiput is compact in plan.
LAMINAE=[
    (862,43,774,48,10.0,.000, .21),(844,48,751,65,12.0,.002, .42),
    (815,52,733,82,11.6,.003, .65),(800,61,722,100,11.2,.002, .83),
    (784,71,715,123,11.0,.001,1.0),
    (853,56,788,73,10.5,.002, .47),(830,67,760,91,13.0,.004,.79),
    (804,78,737,114,13.3,.005,.90),(786,85,725,141,12.8,.004,.98),
    (771,99,722,159,11.4,.003,1.00),
    (841,76,786,96,11.7,.005,.80),(816,90,763,120,12.7,.006,.98),
    (791,102,743,145,13.3,.006,1.00),(773,119,732,170,11.7,.004,1.00),
    (761,133,736,181,10.7,.003,.98),
    (808,116,773,156,12.7,.005,1.00),(790,126,761,174,12.1,.006,1.00),
    (773,142,749,188,11.1,.004,.95),
    (811,145,794,181,11.1,.003,.99),(793,156,775,197,10.8,.003,.96),
    (777,164,767,200,8.9,.002,.92),
]


def nape_leaf(side,index,guide):
    u0,v0,u1,v1,w,base,side_bias=guide
    du,dv=u1-u0,v1-v0
    distance=sqrt(du**2+dv**2)
    nx,ny=dv/distance,-du/distance
    def sample(t,s):
        width=w*(.24+.76*min(1,t/.19))*(1-.25*t)*max(.025,(1-t)**.48)
        sweep=2.2*sin(t*pi)*s
        u=u0+du*t+nx*(s*width+sweep)+.6*(side<0)*sin(pi*t)
        v=v0+dv*t+ny*s*width-3.8*sin(t*pi)
        # Tips outside the bony bed keep a little transverse body, so the feathers
        # still drape over a crown when viewed from its posterior.
        bone=flank(u,v)
        root=max(flank(u0,v0),.038)
        support=max(bone,root*(1-.48*t)*(.63+.21*side_bias))
        camber=.0037*(1-s*s)*sin(t*pi)+.0045*t*t
        x=side*(support + base + camber)
        n=Vector((side*.94,.17,.27)).normalized()
        return point(u,v,x),n
    formed_panel(('left' if side<0 else 'right')+f' occipital feather {index+1:02d}',
                 sample,'head-armor',15,8,'worn-bronze',.0018)
    if index%3!=1:
        p,n=sample(.53,.42 if index%2 else -.32)
        PINS.append((p,n,.0028))


def lathe(label,center,axis,rings,families,ids,segments=32):
    n=Vector(axis).normalized()
    helper=Vector((0,1,0)) if abs(n.y)<.88 else Vector((0,0,1))
    a=n.cross(helper).normalized()
    b=n.cross(a).normalized()
    vs,fs,ms=[],[],[]
    for rad,offset in rings:
        for j in range(segments):
            ang=j*2*pi/segments
            vs.append(center+n*offset+(a*cos(ang)+b*sin(ang))*rad)
    for i in range(len(rings)-1):
        for j in range(segments):
            a0=i*segments+j
            b0=i*segments+(j+1)%segments
            fs.append((a0,b0,b0+segments,a0+segments)); ms.append(ids[i])
    fs.extend((tuple(reversed(range(segments))),tuple(range(len(vs)-segments,len(vs)))))
    ms.extend((len(families)-1,len(families)-1))
    return mesh_object(label,vs,fs,families,ms)


def hardware():
    # Face, annular shoulder and dark driver in one rigid mesh for all small screws.
    vs,fs,ms=[],[],[]
    segments=12
    for center,axis,r in PINS:
        axis=Vector(axis).normalized()
        a=axis.cross(Vector((0,1,0))).normalized()
        b=axis.cross(a).normalized()
        base=len(vs)
        for radial,offset in ((1.12,-.22),(1.12,0),(.88,.16),(.62,.31),(.32,.30),(.23,-.02)):
            for j in range(segments):
                ang=2*pi*j/segments
                vs.append(center+(a*cos(ang)+b*sin(ang))*r*radial+axis*(r*offset))
        for i,idx in enumerate((2,2,0,1,2)):
            for j in range(segments):
                a0=base+i*segments+j
                b0=base+i*segments+(j+1)%segments
                fs.append((a0,b0,b0+segments,a0+segments)); ms.append(idx)
        fs.append(tuple(base+5*segments+j for j in range(segments))); ms.append(2)
        fs.append(tuple(base+j for j in reversed(range(segments)))); ms.append(2)
    return mesh_object('inset fastening cups',vs,fs,['machined-steel','worn-bronze','black-iron'],ms)


def born_journal(u,v,w,rad,side,label):
    center=point(u,v,side*w)
    r=rad
    lathe(label,center,(side,0,0),[(r*.98,-.011),(r,0),(r*.92,.0018),
          (r*.79,.0027),(r*.74,-.001),(r*.61,-.003),(r*.58,.0025),
          (r*.47,.004),(r*.26,.004),(r*.20,-.001)],
          ['machined-steel','worn-bronze','black-iron'],[2,0,1,1,2,2,0,0,2],36)


def apply_head():
    """Apply once to a writable scene opened from the specified retained04 source."""
    if any(o.name.startswith('FC head |') for o in bpy.context.scene.objects):
        raise ValueError('The new head is already present in this scene.')
    CREATED.clear()
    PINS.clear()
    # Select retained materials using visible head-family assignments at the base revision.
    material_examples={
        'head-armor':'CGH06 substantial swept plated mandible L',
        'machined-steel':'CGH18 formed distal hooked bill plate',
        'black-iron':'CGH06 nested dark jaw upper folded plate L',
        'worn-bronze':'CGH05 thin inset retaining lip L',
    }
    for key,name in material_examples.items():
        source=bpy.data.objects.get(name)
        if not source or not source.material_slots:
            raise ValueError('Expected retained04 source mesh '+name)
        STOCK[key]=source.material_slots[0].material
    old=[]
    for o in list(bpy.context.scene.objects):
        if o.type!='MESH' or o.hide_render or o.get('cg1cRegion')!='head':
            continue
        if o.name.startswith('CGO13') or o.name.startswith(('CGH05 integrated optical','CGH05 thin inset')):
            o.location.y+=EYE_Y-(-.2411)
            o['fc_region']='head'
            continue
        o.hide_render=True
        o.hide_viewport=True
        o.hide_set(True)
        o['fc_replaced']=True
        old.append(o.name)

    volume('dark orbital and occipital bed',BRAIN,bed_ring,'black-iron',48)
    poll_return()
    brow_course('frontal casting under the brow',818,980,5,4,-.0032,'black-iron',())
    brow_course('poll cap and flared back hem',817,860,7,7,.0007,'head-armor',
                ((.62,-.71,.0033),(.68,.69,.0034)))
    brow_course('upper saddle of brow',855,910,10,5,.0013,'head-armor',
                ((.28,-.78,.0042),(.78,-.71,.0031),(.29,.78,.0042),(.79,.68,.0031)))
    brow_course('forward orbital hood',907,951,5,10,.0018,'worn-bronze',
                ((.25,-.88,.0038),(.70,-.72,.0036),(.24,.88,.0038),(.71,.72,.0036)))
    brow_course('sloped nasal brow return',949,982,9,1,.0001,'machined-steel',
                ((.46,-.72,.0033),(.47,.72,.0033)))
    blade=volume('continuous deep hooked blade',BLADE,bill_ring,'machined-steel',48,4)

    # A transverse aperture opens the blade's lateral cheek panel. The cutter exists
    # only in this in-memory candidate and is removed as soon as the boolean is baked.
    v,u=151,984
    bpy.ops.mesh.primitive_cylinder_add(vertices=36,radius=.0132,depth=.38,
        location=point(u,v,0),rotation=(0,pi/2,0))
    tool=bpy.context.object
    bpy.context.view_layer.objects.active=blade
    mod=blade.modifiers.new('formed narial aperture','BOOLEAN')
    mod.operation='DIFFERENCE'
    mod.object=tool
    mod.solver='EXACT'
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(tool,do_unlink=True)

    lower_jaw=[
        (841,141,148,.119,-.001),(849,140,160,.133,.001),
        (870,149,174,.135,.002),(891,159,182,.120,.003),
        (914,171,190,.106,.002),(937,186,204,.083,.002),
        (953,203,218,.053,.001),(965,212,222,.027,0),(975,213,216,.008,0),
    ]
    zygoma=[
        (833,123,125,.133,0),(849,116,132,.149,.002),(861,122,143,.161,.002),
        (878,138,153,.166,.001),(898,145,162,.164,0),(918,148,165,.157,.001),
        (934,143,162,.149,.002),(945,135,158,.137,.002),(957,132,156,.124,.002),
        (968,133,153,.112,.002),(975,136,150,.107,0),(980,141,145,.100,0),
    ]
    jaw_lap=[
        (850,145,154,.139,.001),(861,149,160,.141,.002),(875,155,166,.134,.002),
        (893,161,175,.125,.002),(910,170,180,.113,.001),(923,181,185,.102,.001),
    ]
    cheek_cast=[
        (827,123,126,.115,0),(836,113,140,.128,0),(850,114,150,.131,0),
        (858,128,155,.134,0),(869,143,158,.126,0),(876,150,154,.116,0),
    ]
    for side in (-1,1):
        s='left' if side<0 else 'right'
        for i,g in enumerate(LAMINAE):
            nape_leaf(side,i,g)
        blade_lap(side,s+' nasal bridge outer course',103,119,'head-armor')
        blade_lap(side,s+' nasal bridge tip course',123,137,'machined-steel')
        orbital_fender(side,s+' orbital mounting crescent',123,253,.035,'head-armor',-.0012)
        orbital_fender(side,s+' upper orbital brow return',223,307,.019,'machined-steel',.0014)
        orbital_fender(side,s+' nasal orbital fender',-44,67,.029,'head-armor',-.0008)
        temporal=[(813,104,106,.137,0),(818,94,102,.144,0),(829,83,93,.147,.002),
                  (844,77,86,.148,.002),(854,75,85,.151,.001),(865,77,90,.155,.002),
                  (874,85,96,.155,.001),(882,90,100,.153,0),(889,89,94,.151,0)]
        side_panel(s+' stepped temporal casting',temporal,side,'machined-steel',.003,.003)
        side_panel(s+' temple hinge carrier',cheek_cast,side,'black-iron',.012,.004)
        side_panel(s+' orbital cheek return',zygoma,side,'head-armor',.0055,.003,
                   ((.15,.28,.0042),(.34,.47,.0039),(.58,.29,.0033)),curl=True)
        side_panel(s+' cast mandible spar',lower_jaw,side,'head-armor',.016,.004,
                   ((.17,.5,.0043),(.40,.17,.0033),(.66,.40,.0032)))
        side_panel(s+' lateral mandibular cover',jaw_lap,side,'machined-steel',.004,.0023,
                   ((.16,-.06,.003),(.71,.21,.0031)))
        # Dark subcutaneous receiving drums visible only through the exposed temple.
        born_journal(817,105,.136,.027,side,s+' posterior journal')
        born_journal(838,101,.143,.021,side,s+' offset temple idler')
        born_journal(851,139,.150,.020,side,s+' mandibular bush')
        # The narial cups are physically inset in the bore, with a dark central opening.
        p=point(u,v,side*(blade_depth(u,v)-.0060))
        lathe(s+' recessed nasal cup',p,(side,0,0),
              [(.0141,-.008),(.0136,0),(.0125,.001),(.0104,-.0004),(.0093,-.004),(.006,-.007)],
              ['machined-steel','black-iron'],[1,0,0,0,1],32)
    chin=[(915,182,182.6,.022),(930,190,197,.044),(948,204,216,.055),
          (959,211,220,.042),(969,214,221,.026),(977,213.7,215.3,.004)]
    volume('continuous upturned mandibular toe',chin,bed_ring,'black-iron',28,3)
    hardware()
    bpy.context.view_layer.update()
    return {'created':[o.name for o in CREATED], 'retired':old, 'optic_shift_m':EYE_Y+.2411}
