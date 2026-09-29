"""V34 substantial paired passive leg frame, current rests / native Z-up.

A qualitative construction proposal composed on V33 Form06. Existing rigid
owners, journal geometry, foot/claw geometry, metadata and materials remain.
No powered components, hidden parts, altered travel or engineering claims.
"""
import bpy,bmesh,math
from mathutils import Vector

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
    bpy.context.view_layer.update()
    assert rests=={o.name:_record(o) for o in bpy.data.objects if o.type=='EMPTY'}
    assert transforms=={o.name:_record(o) for o in bpy.data.objects},'Transforms or inherited metadata changed'
    return {'region':'lower-limb passive structural mass','changed':changed,'changedMeshes':[x['name'] for x in changed],'added':[],'removed':[],'structuralContract':contracts,'status':'One coarse inferred construction proposal; visual gate and movement fit remain pending','unchangedRigNodes':len(rests),'materialsOrEraTagsChanged':False,'limits':['Finite solids and exact rests do not prove load capacity.','Only neutral rest is previewed; articulated clearances are not established.','Foot/claw geometry and circular journals remain exact.','Section dimensions are qualitative construction choices, not measurements from art.']}
