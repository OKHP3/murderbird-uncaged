"""Coherent V37 paired passive foot reconstruction from the V35 native.

Replaces fixed load members, separate guards and sheaths within their existing
rigid owners. Circular inherited pins/collars retain exact local geometry.
Only distal digit rests move; all foot/toe/proximal and ankle interfaces remain.
Authored construction proposal, not recovered engineering or owner acceptance.
"""
import math
import bpy
from mathutils import Vector, Matrix

SIDES = ('left', 'right')
DISTAL_SPAN = .78


def _matrix(m):
    return [round(float(m[r][c]), 10) for r in range(4) for c in range(4)]


def _sig(o):
    return (_matrix(o.matrix_world), [tuple(round(float(x), 9) for x in v.co) for v in o.data.vertices],
            [tuple(p.vertices) for p in o.data.polygons], [m.name if m else None for m in o.data.materials])


def _bounds(o):
    p = [o.matrix_world @ v.co for v in o.data.vertices]
    return [[min(v[k] for v in p), max(v[k] for v in p)] for k in range(3)]


def _centre(o):
    return Vector([(a+b)*.5 for a,b in _bounds(o)])


class Solid:
    """Closed stock volumes; overlapping same-part stock is fabricated together.

    No stock volumes from separately moving owners are combined. Internal stock
    self-intersection is disclosed; strict screen compares distinct mesh parts.
    """
    def __init__(self):
        self.v=[];self.f=[]
    def box(self, a, b, width, height):
        a,b=Vector(a),Vector(b);z=(b-a).normalized()
        x=Vector((1,0,0)); x=(x-z*x.dot(z)).normalized();y=z.cross(x).normalized()
        n=len(self.v)
        self.v.extend([tuple(p+x*dx*width*.5+y*dy*height*.5) for p in (a,b) for dx,dy in ((-1,-1),(1,-1),(1,1),(-1,1))])
        self.f.extend([tuple(n+i for i in face) for face in ((3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))])
    def annulus(self, centre, inner, outer, width, segments=40):
        c=Vector(centre);n=len(self.v)
        for x in (-width*.5,width*.5):
            for r in (inner,outer):
                for i in range(segments):
                    q=2*math.pi*i/segments
                    self.v.append(tuple(c+Vector((x,r*math.cos(q),r*math.sin(q)))))
        for i in range(segments):
            j=(i+1)%segments;N=segments
            self.f.extend([(n+i,n+j,n+N+j,n+N+i),(n+2*N+j,n+2*N+i,n+3*N+i,n+3*N+j),
                           (n+i,n+2*N+i,n+2*N+j,n+j),(n+N+j,n+3*N+j,n+3*N+i,n+N+i)])
    def sweep(self, centres, widths, heights, segments=12):
        n=len(self.v)
        for c,w,h in zip(centres,widths,heights):
            c=Vector(c)
            for i in range(segments):
                q=2*math.pi*i/segments
                self.v.append(tuple(c+Vector((math.cos(q)*w*.5,0,math.sin(q)*h*.5))))
        self.f.append(tuple(n+i for i in reversed(range(segments))))
        for k in range(len(centres)-1):
            for i in range(segments):
                j=(i+1)%segments;self.f.append((n+k*segments+i,n+k*segments+j,n+(k+1)*segments+j,n+(k+1)*segments+i))
        self.f.append(tuple(n+(len(centres)-1)*segments+i for i in range(segments)))


def _replace(o, solid, description):
    old=o.data;mesh=bpy.data.meshes.new(o.name+' v37 rebuilt native mesh')
    inv=o.matrix_world.inverted();mesh.from_pydata([inv@Vector(v) for v in solid.v],[],solid.f);mesh.update()
    for m in old.materials:mesh.materials.append(m)
    o.data=mesh
    # Winding for consistent normals, no destructive union or source mutation.
    import bmesh
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    o['constructionDescription']=description;o['geometryStatus']='V37 coherent passive foot reconstruction proposal'
    o['footAssemblyRevision']='whole-character-v37 attempt01';o['proposal']=True
    o['constructionClass']='inherited-passive';o['exteriorEras']='maker,mechanic,builder'


def apply():
    bpy.context.view_layer.update()
    owners={f'{s}-{part}' for s in SIDES for part in ('foot','toes')}
    owners.update(f'{s}-digit-{d}-{p}' for s in SIDES for d in range(1,4) for p in ('proximal','distal'))
    meshes={o.name:o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name in owners}
    before={n:_sig(o) for n,o in meshes.items()};bounds_before={s:[min(_bounds(o)[1][0] for o in meshes.values() if o.parent.name.startswith(s)),max(_bounds(o)[1][1] for o in meshes.values() if o.parent.name.startswith(s))] for s in SIDES}
    node_before={o.name:_matrix(o.matrix_world) for o in bpy.data.objects if o.type=='EMPTY'}
    bearing_local={n:(_sig(o)[1:]) for n,o in meshes.items() if o.get('surfaceRole')=='bearing' or 'articulated bearing core' in n}
    # Freeze actual flange centres before rests change (node translations are
    # offset from some V35 mesh axes). Every member is rebuilt from these centres.
    centres={o.parent.name:_centre(o) for o in meshes.values() if 'captive toe-bearing flanges' in o.name}
    moves=[];joins=[];endpoints=[]
    for side in SIDES:
        for d in range(1,4):
            pn=f'{side}-digit-{d}-proximal';dn=f'{side}-digit-{d}-distal'
            p=bpy.data.objects[pn];dst=bpy.data.objects[dn];old=dst.matrix_world.copy();target=old.copy()
            delta=(p.matrix_world.translation.y-old.translation.y)*(1-DISTAL_SPAN)
            target.translation.y+=delta;dst.matrix_world=target;bpy.context.view_layer.update()
            centres[dn].y+=delta
            moves.append({'name':dn,'oldWorldMatrix':_matrix(old),'newWorldMatrix':_matrix(dst.matrix_world),'worldDelta':[0,delta,0]})
            pc,dc=centres[pn],centres[dn]
            # The proximal fixed web terminates in an annular journal around
            # the distal pin. Pin radius <=27mm; journal bore 30mm; outer 39mm.
            # Axial 20mm journal lies between the inherited external collars.
            frame=next(o for o in meshes.values() if o.parent.name==pn and o.name.startswith('Digit inner link'))
            st=Solid();st.annulus(dc,.030,.039,.020)
            a=pc+Vector((0,-.040,-.003));b=dc+Vector((0,.033,.004))
            st.box(a,b,.025,.025)
            _replace(frame,st,'Fabricated proximal load web and fixed annular distal-pin receiving journal; inherited pin rotates separately in a proposed 3mm radial bore gap. Stock overlaps within this one fixed member are proposed fabrication, not validated union topology.')
            joins.append({'parts':[frame.name, next(o.name for o in meshes.values() if o.parent.name==pn and o.name.startswith('Toe hinge'))],
                          'type':'proposed fixed bearing-to-web fabrication seat','description':'Web begins 40mm forward of proximal axis, at the circular housing envelope; rest overlap if observed is separately reported, never a generic exclusion.'})
            # Separate proximal cap at the free midpoint between circular axes.
            guard=meshes[f'{side} digit {d} proximal dorsal guard'];g=Solid()
            mid=(pc+dc)*.5
            g.sweep([(mid.x,mid.y+.010,.092),(mid.x,mid.y,.099),(mid.x,mid.y-.010,.087)], [.034,.038,.032],[.008,.008,.008])
            _replace(guard,g,'Separate formed dorsal cap over the short proximal web; ends clear of circular bearing envelopes, retained proximal owner.')
            # Distal load link terminates in a stout talon socket, not an
            # affine-scaled original rail. Splay is from actual joint centres.
            direction=Vector((dc.x-pc.x,dc.y-pc.y,0)).normalized()
            length=.080 if d==2 else .068
            socket=dc+direction*(.045+length);socket.z=.051
            link=next(o for o in meshes.values() if o.parent.name==dn and o.name.startswith('Digit inner link'))
            st=Solid();st.box(dc+direction*.043+Vector((0,0,.002)),socket,.030,.025)
            _replace(link,st,'Short distal passive load bar and talon receiving socket, computed from relocated circular bearing centre and toe splay.')
            guard=meshes[f'{side} digit {d} distal dorsal guard'];g=Solid()
            gp=dc+direction*.055;gp.z=.077;ge=socket-direction*.018;ge.z=.077
            g.sweep([gp,ge],[.041,.043],[.008,.008])
            _replace(guard,g,'Independent dorsal guard over distal passive bar; rear lip clears inherited circular bearing.')
            talon=meshes[f'{side} digit {d} tapered claw sheath'];t=Solid()
            # Recurved dorsal ridge, broad root and hooked floorward tip.
            root=socket-direction*.007
            centres_t=[]
            for tpos,z in ((0,.067),(.018,.084),(.043,.077),(.063,.048),(.078,.013)):
                q=root+direction*tpos;q.z=z;centres_t.append(q)
            t.sweep(centres_t,[.050,.058,.051,.035,.006],[.039,.041,.035,.022,.008])
            _replace(talon,t,'Short stout curved talon: broad socket root, raised recurved dorsal ridge and hooked floorward terminal; retained independently moving distal owner.')
            joins.append({'parts':[link.name,talon.name],'type':'proposed fixed talon socket fabrication','description':'Broad talon root seats into distal load-bar socket on the same rigid owner; any strict witness remains visible and separately classified.'})
            endpoints.append({'digit':dn,'proximalAxis':list(pc),'distalAxis':list(dc),'journalInnerRadiusM':.030,'journalOuterRadiusM':.039,'journalAxialWidthM':.020,'socketWorldXYZ':list(socket),'talonTipWorldXYZ':list(centres_t[-1])})
        # Replace the complete lower foot-owned members together. Existing
        # ankle bearing/receiver is retained; no arch lift toward shin geometry.
        x=bpy.data.objects[f'{side}-foot'].matrix_world.translation.x
        rails=sorted([o for o in meshes.values() if o.parent.name==f'{side}-foot' and 'metatarsal passive rail' in o.name],key=lambda o:o.name)
        for o,sgn in zip(rails,(-1,1)):
            st=Solid();st.box((x+sgn*.046,.007,.211),(x+sgn*.046,-.091,.108),.024,.028)
            _replace(o,st,'Rebuilt stout metatarsal load rail between unchanged ankle bearing envelope and compact toe-root receiving channel; no raised arch.')
        channel=next(o for o in meshes.values() if o.parent.name==f'{side}-foot' and 'metatarsus open passive truss' in o.name)
        st=Solid()
        for sgn in (-1,1):st.box((x+sgn*.033,-.006,.190),(x+sgn*.033,-.094,.109),.019,.025)
        st.box((x-.052,-.091,.100),(x+.052,-.091,.100),.018,.024)
        _replace(channel,st,'Paired formed channel shoulders and toe-root crossmember around a central open service seam. Fixed stock within this one fabricated member; original receiver/bearing remains separately inspectable.')
        guard=meshes[f'{side} curved instep guard'];st=Solid()
        st.sweep([(x,-.038,.170),(x,-.070,.150),(x,-.100,.122)],[.065,.076,.083],[.009,.009,.009])
        _replace(guard,st,'Separate compact formed instep guard above the open receiving channel, below the unchanged ankle envelope; no arch raise.')
        hallux_link=meshes[f'{side} rear hallux load link v4'];hx=x+(.029 if side=='left' else -.029)
        st=Solid();st.box((hx,-.060,.046),(hx,.080,.046),.034,.026)
        _replace(hallux_link,st,'Compact rear hallux passive load bar under the foot channel, with its own fixed sheath socket; reconstructed as inherited passive support.')
        sheath=meshes[f'{side} rear hallux sheath v4'];st=Solid()
        st.sweep([(hx,.073,.049),(hx,.096,.062),(hx,.129,.058),(hx,.153,.033),(hx,.175,.006)],[.045,.053,.044,.028,.005],[.033,.035,.028,.016,.007])
        _replace(sheath,st,'Short recurved rear hallux sheath seated on compact rear load bar, preserving a distinct talon rather than an organic pad.')
        joins.append({'parts':[hallux_link.name,sheath.name],'type':'proposed fixed hallux socket fabrication','description':'Rear sheath root is received by load bar on the fixed foot owner; witnesses are recorded rather than exempted.'})
    bpy.context.view_layer.update()
    changed=[n for n,o in meshes.items() if _sig(o)!=before[n]]
    nodes=[o.name for o in bpy.data.objects if o.type=='EMPTY' and _matrix(o.matrix_world)!=node_before[o.name]]
    assert set(nodes)=={f'{s}-digit-{d}-distal' for s in SIDES for d in range(1,4)},nodes
    assert all(_sig(meshes[n])[1:]==v for n,v in bearing_local.items()),'Bearing-local geometry changed'
    bounds_after={s:[min(_bounds(o)[1][0] for o in meshes.values() if o.parent.name.startswith(s)),max(_bounds(o)[1][1] for o in meshes.values() if o.parent.name.startswith(s))] for s in SIDES}
    rows=[{'name':n,'owner':meshes[n].parent.name,'surfaceRole':meshes[n].get('surfaceRole'),'worldBounds':_bounds(meshes[n]),'worldPlacementChanged':_sig(meshes[n])[0]!=before[n][0],'localGeometryChanged':_sig(meshes[n])[1:]!=before[n][1:]} for n in changed]
    return {'region':'coherent paired compact mechanical foot assemblies','changedMeshes':changed,'changedFootMeshes':rows,'addedMeshes':[],'removedMeshes':[],'added':[],'removed':[],'changedNodes':nodes,
            'distalJointMoves':moves,'endpoints':endpoints,'proposedFabricationJoins':joins,
            'footEnvelope':{s:{'beforeYBoundsM':bounds_before[s],'afterYBoundsM':bounds_after[s],'foreAftReductionPercent':100*(1-(bounds_after[s][1]-bounds_after[s][0])/(bounds_before[s][1]-bounds_before[s][0]))} for s in SIDES},
            'invariants':{'bearingLocalMeshCountExact':len(bearing_local),'onlySixDistalRestTranslationsChanged':True,'ankleReceivingInterfaceUnchanged':True,'allPartsInheritedPassiveAllEras':True,'noUnrelatedNodesChanged':True},
            'rationale':'Rebuild frame, journals, guards, sockets and short curved talons together from actual bearing centres. Circular inherited bearings remain round; frame endpoints and separate guards are recomputed instead of affine compression.',
            'scopeLimitations':['Unapproved regional fabrication proposal; not measured source engineering, likeness acceptance, physics or publication.','Stock volumes within individual fixed fabricated members are closed but may overlap; no boolean-union or within-mesh self-intersection claim.','Distinct fixed-owner mesh joins remain in strict-screen evidence and are identified specifically as proposed fabrication; no generic same-owner exemptions.','Three discrete rest/scrape/landing states do not prove continuous clearance.']}
