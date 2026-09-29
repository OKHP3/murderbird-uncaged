"""V25 passive paired leg structure proposal, native Z-up / -Y front.

Apply to the exact V24 Form02 in memory. The four thigh/shin rigid owners
receive compact, substantial paired members and captive joint receivers.
Foot/toe geometry, every named rest and material definition remain exact.
This inferred construction is not a load, motion-clearance or likeness pass.
"""
import math
import bpy
import bmesh
from mathutils import Matrix, Vector

BASE_SHA256 = 'acb91013e0ca7cf98475e0d2ba6fb36d9c081c29c91b27e104bf7367d57f306d'
ERAS = 'maker,mechanic,builder'
OWNERS = ('left-thigh', 'left-shin', 'right-thigh', 'right-shin')


def _signature(o):
    return (o.parent.name if o.parent else None, tuple(tuple(r) for r in o.matrix_world),
            tuple(tuple(r) for r in o.matrix_local), tuple((k, repr(o[k])) for k in sorted(o.keys())))


def _mesh_signature(o):
    return (_signature(o), tuple(tuple(v.co) for v in o.data.vertices),
            tuple(tuple(p.vertices) for p in o.data.polygons), tuple(m.name if m else None for m in o.data.materials),
            tuple((m.name, m.type, repr(m.width) if m.type == 'BEVEL' else '') for m in o.modifiers))


def _basis(delta):
    axis = delta.normalized()
    across = Vector((1, 0, 0)) if abs(axis.x)<.9 else Vector((0,1,0))
    across = (across-axis*across.dot(axis)).normalized()
    front = axis.cross(across).normalized()
    if front.y > 0: front.negate()
    return across, front


def _member(a, b, width, depth, taper=(.88, 1, .88), channel=False):
    u, v = _basis(b-a)
    cross = ((-.68,-1),(.68,-1),(1,-.68),(1,.68),(.68,1),(-.68,1),(-1,.68),(-1,-.68))
    if channel:
        # Finite C-section, 9mm side flanges / 10mm rear web; the front
        # opening reveals depth instead of presenting one broad flat bar.
        cross=((-1,-1),(1,-1),(1,1),(.59,1),(.59,-.70),(-.59,-.70),(-.59,1),(-1,1))
    verts=[]; faces=[]
    for t, scale in zip((0,.5,1),taper):
        c=a.lerp(b,t)
        verts.extend(c+u*x*width*scale+v*y*depth*scale for x,y in cross)
    for j in range(2):
        for k in range(8):
            a0=j*8+k; a1=j*8+(k+1)%8
            faces.append((a0,a1,a1+8,a0+8))
    faces.extend((tuple(reversed(range(8))),tuple(range(16,24))))
    return verts,faces


def _ring(center, x_offset, inner, outer, thickness, opening=0):
    """Finite X-axis journal or clevis, defined concentrically at the rig pivot."""
    count=48; start=opening*.5; sweep=2*math.pi-opening
    steps=count+1 if opening else count
    angles=[start+sweep*i/count for i in range(steps)]
    verts=[];faces=[]
    for dx in (-thickness*.5,thickness*.5):
        for r in (inner,outer):
            verts.extend(center+Vector((x_offset+dx,r*math.cos(a),r*math.sin(a))) for a in angles)
    n=steps
    for i in range(count):
        j=(i+1)%n
        faces.extend(((i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),
                      (i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)))
    if opening:
        faces.extend(((0,n,3*n,2*n),(n-1,3*n-1,4*n-1,2*n-1)))
    return verts,faces


def _shaft(center, half_length, radius):
    n=32; verts=[]; faces=[]
    for dx in (-half_length,half_length):
        verts.extend(center+Vector((dx,radius*math.cos(2*math.pi*i/n),radius*math.sin(2*math.pi*i/n))) for i in range(n))
    for i in range(n): faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
    faces.extend((tuple(reversed(range(n))),tuple(range(n,2*n))))
    return verts,faces


def _install(name, owner, geometry, material, role, description):
    assert name not in bpy.data.objects
    # Synchronize evaluated rest transforms BEFORE converting world geometry.
    bpy.context.view_layer.update()
    inv=owner.matrix_world.inverted(); verts,faces=geometry
    mesh=bpy.data.meshes.new(name+' mesh')
    mesh.from_pydata([inv@Vector(p) for p in verts],[],faces);mesh.update()
    assert all(math.isfinite(c) for v in mesh.vertices for c in v.co), name
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges), name
    assert bm.calc_volume(signed=True)>1e-10, name
    bm.to_mesh(mesh);bm.free();mesh.materials.append(material)
    obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj)
    obj.parent=owner;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=Matrix.Identity(4)
    obj['region']='leg-structure';obj['surfaceRole']=role;obj['exteriorEras']=ERAS
    obj['constructionClass']='inherited-passive';obj['constructionOwner']=owner.name
    obj['proposal']=True;obj['articulatesAcrossJoint']=False
    obj['constructionDescription']=description
    obj['geometryStatus']='V25 inferred passive construction proposal; no engineering or owner acceptance'
    return obj


def apply():
    bpy.context.view_layer.update()
    rests={o.name:_signature(o) for o in bpy.data.objects if o.type=='EMPTY'}
    protected={o.name:_mesh_signature(o) for o in bpy.data.objects if o.type=='MESH' and (not o.parent or o.parent.name not in OWNERS)}
    frame=bpy.data.materials['Neutral / frame']; bearing=bpy.data.materials['Neutral / bearing'];edge=bpy.data.materials['Neutral / edge']
    removed=[];added=[];contracts=[]
    # These four owners carry only source passive frame/bearing/guard meshes.
    # Remove the old splayed flat rails, disc shells and isolated fixings;
    # foot-side receiving geometry remains protected, including its axle.
    for o in list(bpy.data.objects):
        if o.type=='MESH' and o.parent and o.parent.name in OWNERS:
            assert o.get('surfaceRole') in ('frame','bearing','edge','guard','bearing-frame'),o.name
            removed.append({'name':o.name,'owner':o.parent.name,'reason':'Replace sparse flat limb construction with joint-centered paired frame and captive journals.'})
            bpy.data.objects.remove(o,do_unlink=True)
    for side in ('left','right'):
        for kind,distal in (('thigh','shin'),('shin','foot')):
            owner=bpy.data.objects[f'{side}-{kind}']; next_owner=bpy.data.objects[f'{side}-{distal}']
            p0=owner.matrix_world.translation.copy();p1=next_owner.matrix_world.translation.copy()
            axis=(p1-p0).normalized(); u,v=_basis(p1-p0)
            gap=.055 if kind=='thigh' else .061
            radius=.055 if kind=='thigh' else .058
            def add(label,geometry,mat,role,description):
                obj=_install(f'V25 {side} {kind} {label}',owner,geometry,mat,role,description);added.append(obj.name);return obj
            # The existing foot-owned axle has a documented 66mm silhouette.
            # Distal shin cheeks therefore retain 68mm aperture / 2mm nominal
            # radial gap. It is a rest fit only, not swept clearance evidence.
            distal_inner=.068 if kind=='shin' else .057
            distal_outer=.084 if kind=='shin' else .075
            cheek_offset=.080 if kind=='shin' else .085
            for lateral in (-1,1):
                a=p0+u*(lateral*gap)+axis*.045
                b=p1+u*(lateral*gap)-axis*.056
                obj=add(f'primary load member {lateral}',_member(a,b,.022,.033,channel=True),frame,'frame','Substantial formed C-section passive member with finite flanges and rear web, paired around open service space; terminal sockets meet same-owner journal webs.')
                obj['jointCentersWorld']=[list(p0),list(p1)];obj['railEndpointWorld']=[list(a),list(b)]
                # Short webs overlap both member terminals and each journal's
                # outer wall. All pieces remain rigid on one segment owner.
                for label,c,anchor,r in (('proximal',p0,a,radius),('distal',p1,b,distal_outer)):
                    offset=gap if label=='proximal' else cheek_offset
                    # Ring axis is native X; choose a point inside its actual
                    # annular wall, not a splayed rail coordinate near it.
                    radial=Vector((0,axis.y,axis.z)).normalized()
                    seat=c+Vector((lateral*offset,0,0))+radial*(r*.82 if label=='proximal' else -r*.82)
                    seat_radius=Vector((0,seat.y-c.y,seat.z-c.z)).length
                    assert (distal_inner if label=='distal' else .028)<seat_radius<r
                    obj=add(f'{label} terminal gusset {lateral}',_member(seat,anchor,.023,.027,(1,1,1)),frame,'frame','Finite same-owner terminal web joining paired member to captive concentric journal; does not connect to adjacent rigid owner.')
                    obj['journalSeatWorld']=list(seat);obj['memberSeatWorld']=list(anchor)
                add(f'proximal journal {lateral}',_ring(p0,lateral*gap,.028,radius,.020),bearing,'bearing','Finite annular journal centered on the unchanged proximal rig pivot, paired at shaft shoulders.')
                add(f'distal captive cheek {lateral}',_ring(p1,lateral*cheek_offset,distal_inner,distal_outer,.015),bearing,'bearing-frame','Concentric captive clevis cheek on upstream segment; receiving shaft belongs to downstream owner. Aperture leaves the joint legible.')
                # Retaining rim and lock fasteners belong to this journal,
                # rather than floating detail or a fictitious drive system.
                x=lateral*(gap+.012)
                add(f'proximal retainer rim {lateral}',_ring(p0,x,radius-.014,radius+.002,.007),edge,'bearing','Stepped retaining lip on the same proximal journal shoulder; passive keeper only.')
                for index in range(6):
                    angle=2*math.pi*index/6
                    c=p0+Vector((x+lateral*.004,(radius-.006)*math.cos(angle),(radius-.006)*math.sin(angle)))
                    add(f'journal keeper bolt {lateral} {index}',_shaft(c,.004,.0045),bearing,'bearing','Captive axial keeper head seated through the same-owner retainer rim; passive fixing with no driven capability.')
                for t in (.28,.72):
                    c=p0.lerp(p1,t)+u*lateral*gap
                    add(f'load channel collar {lateral} {t}',_member(c-axis*.009,c+axis*.009,.026,.037,(1,1,1),channel=True),edge,'frame','Short finite formed clamp collar at the transverse web station; mechanically seated to same-owner primary channel.')
                # Additional rear member gives structural depth without an
                # invented actuator, piston or layer of concealing armor.
                ar=p0.lerp(p1,.24)+u*lateral*(gap-.008)-v*.039
                br=p0.lerp(p1,.77)+u*lateral*(gap-.008)-v*.039
                add(f'rear return member {lateral}',_member(ar,br,.010,.013),frame,'frame','Passive rear return rail, tied to the two fixed cross webs; no powered function.')
            add('proximal captive axle',_shaft(p0,gap+.008,.027),bearing,'bearing','Passive transverse axle rigid to the proximal owner; concentric journals expose its retained shaft line.')
            for t in (.28,.72):
                c=p0.lerp(p1,t)
                add(f'transverse cross web {t}',_member(c-u*gap,c+u*gap,.014,.038,(1,1,1)),frame,'frame','Short transverse load tie between the paired rigid members; open central bay remains visible.')
            # A selective narrow forward wear guard occupies only midspan;
            # its shoulders attach to cross webs, not to moving neighboring parts.
            c0=p0.lerp(p1,.32)+v*.042;c1=p0.lerp(p1,.67)+v*.042
            add('limited anterior wear guard',_member(c0,c1,.024,.005,(.78,1,.64)),edge,'guard','Narrow finite midspan wear guard; leaves both structural members and joint receivers exposed.')
            contracts.append({'owner':owner.name,'proximalJoint':owner.name,'distalJoint':next_owner.name,
                              'jointCentersWorld':[list(p0),list(p1)],'xAxisJournals':True,
                              'pairedMemberHalfWidthDepthM':[.022,.033],'formedChannelWallM':[.009,.010],'memberLateralOffsetsM':[-gap,gap],
                              'distalApertureRadiusM':distal_inner,'distalCheekRadiusM':distal_outer,
                              'distalCheekXOffsetM':cheek_offset,'kneeJournalToCheekNominalAxialGapM':.001 if kind=='thigh' else None,
                              'restOnlyFootRaceNominalRadialGapM':.002 if kind=='shin' else None,
                              'singleRigidOwner':True,'newDriveOrMotor':False})
    bpy.context.view_layer.update()
    assert rests=={o.name:_signature(o) for o in bpy.data.objects if o.type=='EMPTY'}
    assert all(_mesh_signature(bpy.data.objects[n])==s for n,s in protected.items())
    for n in added:
        o=bpy.data.objects[n];assert o.parent.name in OWNERS and o.scale==Vector((1,1,1))
    return {'status':'inferred passive construction proposal; whole-body review required','removed':removed,'added':added,'changed':[],
            'structuralContract':contracts,'checks':{'namedRestsExact':len(rests),'outsideLegAndAllFootMeshesExact':len(protected),
            'newClosedFinitePositiveSolids':len(added),'singleRigidOwners':True},
            'classification':'Passive structure eligible maker,mechanic,builder; no drive/sensor/motor added.',
            'limits':['Not a physics or load analysis.','Continuous joint travel and whole-model clearance not established.','Owner likeness acceptance pending.','Unseen construction inferred from qualitative owner reference.']}
