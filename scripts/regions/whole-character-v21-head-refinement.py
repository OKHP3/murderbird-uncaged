"""Compact constructed head on a loaded V21 envelope scene.

July controls head identity only; the owner target controls recognition.
All dimensions and hidden connections are authored proposals. No rig edit,
render, export, material edit or surrounding-region deformation occurs here.
Native coordinates are metres, Z-up, -Y-front.
"""
import math
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ALLOWED_OWNERS={'head','jaw','upper-bill','cranial-cover','builder-optics'}


def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3.-2.*t)


def points(obj):
    return [obj.matrix_world@v.co for v in obj.data.vertices]


def deform(obj,fn):
    assert obj.type=='MESH' and obj.parent.name in ALLOWED_OWNERS
    old=points(obj);obj.data=obj.data.copy();obj.data.name=obj.name+' V21 refined'
    inv=obj.matrix_world.inverted()
    for v,p in zip(obj.data.vertices,old):v.co=inv@fn(p.copy())
    obj.data.update()


def translated(obj,delta):
    d=Vector(delta);deform(obj,lambda p:p+d)


def compact_y(y):
    f=max(0.,-y-.505)
    return y+.15*f*smooth(f/.045)


def bill_point(p):
    q=p.copy();forward=max(0.,-p.y-.505);root=(1-smooth((-p.y-.540)/.120))*smooth(forward/.020)
    q.y=compact_y(p.y)
    q.x*=1+.18*root
    q.z+=(p.z-1.720)*.16*root
    # Smooth affine shortening of the hook retains its thick curved sections;
    # no coordinate clamp flattens its tip or cutting edge.
    hook=smooth((-p.y-.610)/.100)
    q.z+=.14*max(0.,1.640-p.z)*hook
    return q


def jaw_point(p):
    q=p.copy();q.y=compact_y(p.y)
    q.z+=.008*smooth((-p.y-.480)/.170)
    return q


def spline(rows,t):
    u=max(0.,min(1.,t))*(len(rows)-1);i=min(int(u),len(rows)-2);v=u-i
    a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
    return Vector([.5*(2*b[k]+(-a[k]+c[k])*v+(2*a[k]-5*b[k]+4*c[k]-d[k])*v*v+(-a[k]+3*b[k]-3*c[k]+d[k])*v*v*v) for k in range(len(b))])


def cheek_geometry(side,rows=None):
    # A broad suborbital cheek return bridges the rear journal shoulder to the
    # deepened bill root; it stays fixed to head, separately from the jaw.
    rows=rows or [(.142,-.351,1.689,.019),(.158,-.398,1.680,.037),
          (.143,-.466,1.678,.033),(.122,-.528,1.697,.025),
          (.106,-.570,1.722,.015)]
    along=48;across=8;n=(along+1)*(across+1);pts=[];faces=[]
    for skin in (0,1):
        for j in range(along+1):
            t=j/along;q=spline(rows,t);a=spline(rows,max(0,t-.002));b=spline(rows,min(1,t+.002))
            dy,dz=b.y-a.y,b.z-a.z;length=max(1e-8,math.hypot(dy,dz))
            for k in range(across+1):
                u=k/across;w=(2*u-1)*q[3]
                x=q.x+(.0018*math.sin(math.pi*u) if skin==0 else -.006)
                p=Vector((side*x,q.y-dz/length*w,q.z+dy/length*w));pts.append(p)
    stride=across+1
    for j in range(along):
        for k in range(across):
            i=j*stride+k;faces.extend([(i,i+1,i+stride+1,i+stride),(n+i+stride,n+i+stride+1,n+i+1,n+i)])
        i=j*stride;l=i+stride;faces.append((i,l,n+l,n+i));i+=across;l+=across;faces.append((l,i,n+i,n+l))
    for k in range(across):
        faces.append((k+1,k,n+k,n+k+1));i=along*stride+k;faces.append((i,i+1,n+i+1,n+i))
    return pts,faces


def install_cheek(obj,pts,faces):
    old=obj.data;inv=obj.matrix_world.inverted();mesh=bpy.data.meshes.new(obj.name+' V21 deep cheek return')
    mesh.from_pydata([inv@p for p in pts],[],faces);mesh.update()
    for mat in old.materials:mesh.materials.append(mat)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
    bm.to_mesh(mesh);bm.free()
    for f in mesh.polygons:f.use_smooth=True
    obj.data=mesh


def install_sheet(obj,pts,faces,wall=.004,contract=0,section_centers=None):
    """Replace actual shell cells with a separate finite formed sheet."""
    ids=sorted({i for f in faces for i in f});index={i:j for j,i in enumerate(ids)}
    center=sum((pts[i] for i in ids),Vector())/len(ids);inv=obj.matrix_world.inverted()
    mesh=bpy.data.meshes.new(obj.name+' V21 formed shell')
    mesh.from_pydata([inv@(center+(pts[i]-center)*(1-contract)) for i in ids],[],[tuple(index[i] for i in f) for f in faces]);mesh.update()
    for mat in obj.data.materials:mesh.materials.append(mat)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    # Recalculation establishes winding consistency, but open components have
    # no volume sign. Orient each formed patch away from its loft centreline;
    # this also handles top/bottom patches whose mean X is zero.
    bm.verts.ensure_lookup_table();normal_matrix=obj.matrix_world.to_3x3().inverted().transposed()
    pending=set(bm.faces)
    while pending:
        seed=pending.pop();component={seed};queue=[seed]
        while queue:
            face=queue.pop()
            for edge in face.edges:
                for neighbor in edge.link_faces:
                    if neighbor in pending:pending.remove(neighbor);component.add(neighbor);queue.append(neighbor)
        score=0.
        for face in component:
            world_center=obj.matrix_world@face.calc_center_median()
            if section_centers is not None:
                receiving=sum((section_centers[ids[v.index]] for v in face.verts),Vector())/len(face.verts)
            else:receiving=Vector((0,world_center.y,world_center.z))
            score+=(normal_matrix@face.normal).normalized().dot(world_center-receiving)*face.calc_area()
        if score<0:bmesh.ops.reverse_faces(bm,faces=list(component))
    bm.to_mesh(mesh);bm.free();obj.data=mesh;obj.modifiers.clear()
    mod=obj.modifiers.new('Finite V21 bill formed wall','SOLIDIFY');mod.thickness=wall;mod.offset=-1;mod.use_even_offset=True
    mod=obj.modifiers.new('Finite formed free edge','BEVEL');mod.width=.0006;mod.segments=2
    for f in mesh.polygons:f.use_smooth=True


def bill_geometry(start,end):
    outer=[(-.505,1.818),(-.572,1.803),(-.635,1.748),(-.690,1.661),(-.706,1.568),(-.700,1.483),(-.675,1.441)]
    inner=[(-.505,1.647),(-.556,1.625),(-.601,1.596),(-.633,1.568),(-.651,1.531),(-.667,1.477),(-.675,1.437)]
    widths=[(.106,0),(.111,0),(.105,0),(.077,0),(.052,0),(.025,0),(.0012,0)]
    pts=[];faces=[];rows=42;segments=48
    for j in range(rows+1):
        t=start+(end-start)*j/rows;o=spline(outer,t);i=spline(inner,t);w=spline(widths,t)[0]
        for k in range(segments):
            a=math.tau*k/segments;cross=1-2*abs((a+math.pi)%math.tau-math.pi)/math.pi;s=math.sin(a)
            x=w*math.copysign(min(1,abs(s)*1.75),s)
            pts.append(Vector((x,(o.x+i.x)/2+(o.x-i.x)*cross/2,(o.y+i.y)/2+(o.y-i.y)*cross/2)))
    for j in range(rows):
        for k in range(segments):
            i=j*segments+k;l=j*segments+(k+1)%segments;faces.append((i,l,l+segments,i+segments))
    return pts,faces


def nasal_keel():
    rows=[(-.505,1.824,.048),(-.540,1.830,.053),(-.590,1.799,.043),(-.635,1.749,.030)]
    pts=[];faces=[];along=32;across=8;n=(along+1)*(across+1)
    for skin in (0,1):
        for j in range(along+1):
            q=spline(rows,j/along)
            for k in range(across+1):
                u=2*k/across-1;pts.append(Vector((q[2]*u,q[0],q[1]+.008*(1-u*u)-.005*skin)))
    for j in range(along):
        for k in range(across):
            i=j*9+k;faces.extend([(i,i+1,i+10,i+9),(n+i+9,n+i+10,n+i+1,n+i)])
        i=j*9;l=i+9;faces.append((i,l,n+l,n+i));i+=8;l+=8;faces.append((l,i,n+i,n+l))
    for k in range(across):
        faces.append((k+1,k,n+k,n+k+1));i=along*9+k;faces.append((i,i+1,n+i+1,n+i))
    return pts,faces


def rebuild_bill_and_jaw():
    rebuilt=[]
    pts,faces=bill_geometry(0,.540);groups={'cap':[],'right':[],'left':[]}
    for face in faces:
        k=face[0]%48;group='right' if 6<=k<18 else 'left' if 30<=k<42 else 'cap';groups[group].append(face)
    centers=[]
    for j in range(43):
        center=sum(pts[j*48:(j+1)*48],Vector())/48
        centers.extend([center]*48)
    install_sheet(bpy.data.objects['Profiled upper bill blade 0'],pts,groups['cap'],section_centers=centers);rebuilt.append('Profiled upper bill blade 0')
    for side in ('left','right'):
        name='V19 fitted proximal bill cheek plate '+side
        install_sheet(bpy.data.objects[name],pts,groups[side],contract=.006,section_centers=centers);rebuilt.append(name)
    pts,faces=bill_geometry(.548,1);faces.extend([tuple(reversed(range(48))),tuple(42*48+k for k in range(48))])
    obj=bpy.data.objects['Profiled upper bill blade 1'];install_cheek(obj,pts,faces);obj.modifiers.clear();rebuilt.append(obj.name)
    obj=bpy.data.objects['Overlapping nasal hood'];pts,faces=nasal_keel();install_cheek(obj,pts,faces);obj.modifiers.clear();rebuilt.append(obj.name)
    cere=[(.090,-.505,1.802,.018),(.113,-.545,1.755,.028),(.112,-.575,1.704,.025),(.104,-.595,1.668,.015)]
    jaw=[(.130,-.355,1.664,.016),(.124,-.398,1.631,.029),(.118,-.463,1.603,.034),(.098,-.526,1.588,.032),(.068,-.588,1.548,.024),(.047,-.623,1.541,.011)]
    for side in (-1,1):
        for name,rows in ((f'Cere root transition {side}',cere),(f'Forked forged mandible {side}',jaw)):
            obj=bpy.data.objects[name];pts,faces=cheek_geometry(side,rows);install_cheek(obj,pts,faces);obj.modifiers.clear();rebuilt.append(name)
    pts=[];faces=[];n=24
    for y,z,w,d in [(-.602,1.542,.055,.007),(-.623,1.541,.047,.008),(-.632,1.547,.041,.006)]:
        for k in range(n):
            a=math.tau*k/n;pts.append(Vector((w*math.cos(a),y,z+d*math.sin(a))))
    for j in range(2):
        for k in range(n):i=j*n+k;l=j*n+(k+1)%n;faces.append((i,l,l+n,i+n))
    faces.extend([tuple(reversed(range(n))),tuple(2*n+k for k in range(n))])
    obj=bpy.data.objects['Distal mandible bridge'];install_cheek(obj,pts,faces);obj.modifiers.clear();rebuilt.append(obj.name)
    return rebuilt


def support_tree(objects):
    vertices=[];faces=[];dg=bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        ev=obj.evaluated_get(dg);mesh=ev.to_mesh();base=len(vertices)
        vertices.extend(ev.matrix_world@v.co for v in mesh.vertices);faces.extend(tuple(base+i for i in p.vertices) for p in mesh.polygons);ev.to_mesh_clear()
    return BVHTree.FromPolygons(vertices,faces)


def crown_point(p):
    q=p.copy();rear=smooth((p.y+.430)/.150)
    q.x*=1-.09*rear
    # Seat the supporting shell closer to the crown, rather than raise a flap.
    q.z-=.005*rear*smooth((1.820-p.z)/.220)
    return q


def sweep_shingle(obj):
    old=points(obj);half=len(old)//2
    assert len(old)%2==0 and half%9==0,'Expected paired finite shingle skins'
    count=half//9;new=[crown_point(p) for p in old]
    leading=obj.name.startswith('Swept temporal lamina') and obj.name.endswith(' 0 0')
    for j in range(count):
        t=j/(count-1);weight=smooth((t-.30)/.70)
        mids=[(new[j*9+k]+new[half+j*9+k])*.5 for k in range(9)]
        center=sum(mids,Vector())/9;factor=1-.28*weight
        sweep=Vector((0,.015*weight,(.004 if leading else -.010)*weight))
        for k in range(9):
            a=j*9+k;b=half+a;wall=(new[a]-new[b])*.5
            mid=center+(mids[k]-center)*factor+sweep
            new[a]=mid+wall;new[b]=mid-wall
    inv=obj.matrix_world.inverted();obj.data=obj.data.copy();obj.data.name=obj.name+' V21 swept guard'
    for v,p in zip(obj.data.vertices,new):v.co=inv@p
    obj.data.update()


def relieve_brow_port(side):
    """Trim only the brow's lower free edge around the seated optic port."""
    race=bpy.data.objects[f'Orbital passive retaining race {side}'];racepts=points(race)
    center=sum(racepts,Vector())/len(racepts);radius=.064
    obj=bpy.data.objects[f'Forged orbital brow {side}'];old=points(obj);new=[p.copy() for p in old]
    # Each nine-vertex cross-section runs upper retained edge -> lower edge.
    # Stop the lower edge at its first circle entry. This creates a curved
    # receiving relief without lifting the upper brow or moving optic seats.
    for skin in (0,1):
        for j in range(49):
            base=skin*49*9+j*9;upper=old[base];lower=old[base+8]
            a=Vector((upper.y-center.y,upper.z-center.z));d=Vector((lower.y-upper.y,lower.z-upper.z))
            aa=d.dot(d);bb=2*a.dot(d);cc=a.dot(a)-radius*radius;discriminant=bb*bb-4*aa*cc
            if aa<=1e-12 or discriminant<=0 or cc<=0:continue
            entry=(-bb-math.sqrt(discriminant))/(2*aa)
            if not 0<entry<1:continue
            edge=upper+(lower-upper)*entry
            for k in range(1,9):
                q=upper+(edge-upper)*(k/8);q.x=old[base+k].x;new[base+k]=q
    inv=obj.matrix_world.inverted();obj.data=obj.data.copy()
    obj.data.name=obj.name+' V21 curved optic receiving edge'
    for vertex,p in zip(obj.data.vertices,new):vertex.co=inv@p
    obj.data.update()


def apply():
    nodes={o.name:([list(r) for r in o.matrix_world],o.parent.name if o.parent else None,dict(o.items())) for o in bpy.data.objects if o.type=='EMPTY'}
    changed=[];replaced=[];seats=[]
    # The complete upper-bill group uses one map, including its panel fixings,
    # root hood and proximal skins, so bill/head attachment is not disconnected.
    for obj in list(bpy.data.objects):
        if obj.type!='MESH' or not obj.parent:continue
        if obj.parent.name=='upper-bill':deform(obj,bill_point);changed.append(obj.name)
        elif obj.parent.name=='jaw':deform(obj,jaw_point);changed.append(obj.name)
    replaced.extend(rebuild_bill_and_jaw());changed.extend(replaced)

    # Reseat retained bill fixings onto the reconstructed actual shell, without
    # assigning a new historical function or making decorative duplicate pins.
    bill_support=support_tree([o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name=='upper-bill' and 'fixing' not in o.name.lower()])
    for obj in list(bpy.data.objects):
        if obj.type=='MESH' and obj.parent and obj.parent.name=='upper-bill' and 'fixing' in obj.name.lower():
            p=points(obj);center=sum(p,Vector())/len(p);target,normal,_,_=bill_support.find_nearest(center)
            translated(obj,target+normal*.0015-center)

    # Fixed orbital frame forward returns follow the same shortened root seam.
    for obj in list(bpy.data.objects):
        if obj.type=='MESH' and obj.parent and obj.parent.name=='head' and obj.name.startswith(('Forged orbital','Orbital mounting fixing')):
            def root_return(p):
                q=p.copy();q.y=compact_y(p.y)
                if obj.name.startswith('Forged orbital brow'):
                    w=smooth((-p.y-.390)/.160);q.z+=.007*w;q.x+=math.copysign(.004*w,p.x)
                return q
            deform(obj,root_return);changed.append(obj.name)
    for side in (-1,1):
        browrows=[(.154,-.335,1.847,.022),(.159,-.397,1.825,.027),(.150,-.458,1.800,.030),(.133,-.518,1.755,.027),(.108,-.575,1.715,.020)]
        bracketrows=[(.142,-.338,1.790,.018),(.155,-.359,1.755,.026),(.147,-.370,1.705,.023),(.132,-.375,1.670,.017)]
        structural=[]
        for name,rows in ((f'Forged orbital brow {side}',browrows),(f'Forged orbital mounting plate {side}',bracketrows)):
            obj=bpy.data.objects[name];verts,faces=cheek_geometry(side,rows);install_cheek(obj,verts,faces);obj.modifiers.clear()
            changed.append(name);replaced.append(name);structural.append((obj,verts))
        cheek=bpy.data.objects[f'Broad swept cheek band {side}'];verts,faces=cheek_geometry(side)
        install_cheek(cheek,verts,faces);cheek.modifiers.clear();changed.append(cheek.name);replaced.append(cheek.name)
        structural.append((cheek,verts))
        orbital_pins=sorted([o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(f'Orbital mounting fixing {side} ')],key=lambda o:o.name)
        fixing_targets=[structural[0][1][j*9+4] for j in (16,32)]+[structural[1][1][j*9+4] for j in (8,24,40)]
        for obj,target in zip(orbital_pins,fixing_targets):
            p=points(obj);center=sum(p,Vector())/len(p);translated(obj,target+Vector((side*.002,0,0))-center)
        pins=[]
        for obj in bpy.data.objects:
            if obj.type=='MESH' and obj.name.startswith('Recessed cheek fixing'):
                p=points(obj);center=sum(p,Vector())/len(p)
                if center.x*side>0:pins.append((center.y,obj,center))
        targets=[verts[j*9+4] for j in (8,24,40)]
        for (_,obj,center),target in zip(sorted(pins,key=lambda r:r[0]),sorted(targets,key=lambda p:p.y)):
            target=target+Vector((side*.002,0,0));translated(obj,target-center);changed.append(obj.name)

        race=bpy.data.objects[f'Orbital passive retaining race {side}'];p=points(race)
        cy=sum(q.y for q in p)/len(p);cz=sum(q.z for q in p)/len(p)
        def seated_race(p):
            q=p.copy();r=math.hypot(p.y-cy,p.z-cz);newr=.0575+(r-.0575)*.50
            q.x-=side*.010;q.y=cy+(p.y-cy)*newr/r;q.z=cz+(p.z-cz)*newr/r;return q
        deform(race,seated_race);changed.append(race.name)
        for name in (f'Recessed orbital bearing {side}',f'Seated passive optic housing {side}',f'Seated Advanced optic {side}'):
            obj=bpy.data.objects[name];translated(obj,(-side*.010,0,0));changed.append(name)
        for number in (1,2,3):
            obj=bpy.data.objects[f'Orbital support bridge {side} {number}']
            bridgepts=points(obj);outerpts=sorted(bridgepts,key=lambda p:math.hypot(p.y-cy,p.z-cz))[-len(bridgepts)//2:]
            outercenter=sum(outerpts,Vector())/len(outerpts)
            frame_support=support_tree([r[0] for r in structural]);target=frame_support.find_nearest(outercenter)[0];outerdelta=target-outercenter
            def bridge(p):
                q=p.copy();r=math.hypot(p.y-cy,p.z-cz);w=1-smooth((r-.069)/.025)
                q.x-=side*.010*w;nr=r-.0045*w;q.y=cy+(p.y-cy)*nr/r;q.z=cz+(p.z-cz)*nr/r
                q+=outerdelta*(1-w);return q
            deform(obj,bridge);changed.append(obj.name)
        seats.append({'side':side,'inboardTranslationM':.010,'retainingRaceWidthScale':.50,'opticCenterYZM':[cy,cz],'function':'existing optic assembly and passive seating; no added sensor'})

    # Crown guard roots, supporting shell and fixing seats move coherently.
    for obj in list(bpy.data.objects):
        if obj.type!='MESH' or not obj.parent or obj.parent.name!='cranial-cover':continue
        if obj.name.startswith(('Swept temporal lamina','Rounded swept crown lamina')):sweep_shingle(obj)
        elif 'pin' in obj.name.lower():
            p=points(obj);center=sum(p,Vector())/len(p);translated(obj,crown_point(center)-center)
        else:deform(obj,crown_point)
        changed.append(obj.name)
    # Last: retained fastener/bridge seats remain those of the broader brow.
    # Only its lower receiving edge changes in this local construction02.
    for side in (-1,1):relieve_brow_port(side)
    bpy.context.view_layer.update()
    assert nodes=={o.name:([list(r) for r in o.matrix_world],o.parent.name if o.parent else None,dict(o.items())) for o in bpy.data.objects if o.type=='EMPTY'},'Head refinement changed a rigid node'
    # An extremum of the evaluated triangle surface occurs on one of its
    # vertices. Include finite wall/bevel modifiers, not only authoring cages.
    dg=bpy.context.evaluated_depsgraph_get();contact=None;contact_owner=None;contact_triangle=None
    for obj in bpy.data.objects:
        if obj.type!='MESH' or not obj.parent or obj.parent.name!='upper-bill':continue
        ev=obj.evaluated_get(dg);mesh=ev.to_mesh();mesh.calc_loop_triangles()
        for tri in mesh.loop_triangles:
            for index in tri.vertices:
                p=ev.matrix_world@mesh.vertices[index].co
                if contact is None or p.y<contact.y:
                    contact=p.copy();contact_owner=obj.name;contact_triangle=tri.index
        ev.to_mesh_clear()
    return {'region':'head','status':'visible regional construction proposal; no likeness or motion acceptance',
      'changed':sorted(set(changed)),'added':[],'removed':[],'stagedOut':[],
      'replacedMeshData':replaced,'newPivots':[],'rigidOwners':sorted(ALLOWED_OWNERS),
      'construction':'Replace proximal bill cap/under-edge and two side skins with deep formed surfaces, plus a shorter thick distal hook and narrow dorsal nasal keel. Two formed cere shoulders continue the bill into a broad diagonal fixed brow, deep cheek and posterior load bracket; this replaces the circular orbital surround geometry rather than dressing its intact surface. Rebuild deep forked mandible side skins and closed tip bridge on unchanged jaw articulation. Reseat retained shell fixings and orbital support bridges onto actual new structural surfaces; seat existing optics10mm inboard. Re-form crown into tighter aft/down swept tapered guards, retaining leading fitting clearance returns.',
      'controllingReferences':['owner-resupplied whole-bird likeness target','July owner-preferred head identity ONLY'],
      'parameters':{'billRootOuterZM':1.818,'billRootInnerZM':1.647,'billMaximumHalfWidthM':.111,'billHookEndNativeYZM':[-.675,1.437],'proximalFormedWallM':.004,'proximalSideSeamContraction':.006,'nasalKeelWallM':.005,'browCheekMandibleWallM':.006,'browPortReceivingRadiusM':.064,'crownTipTransverseTaper':.28,'crownTipAftSweepM':.015,'crownTipDownSweepM':.010,'leadingTemporalTipUpReturnM':.004},
      'opticSeats':seats,'billContactNativeWorld':list(contact),'proposedBillContact':{'nativeWorldM':list(contact),'method':'minimum nativeY vertex of evaluated triangulated upper-bill surface, including wall/bevel modifiers; a linear triangle surface extremum occurs on its boundary vertex','evaluatedObject':contact_owner,'evaluatedTriangleIndex':contact_triangle,'unchangedMarker':'bill-contact node is preserved and now geometrically stale; update after region geometry checks only'},
      'preserved':['all52EMPTY names/parents/world rests/custom properties','all outside head/jaw/upper-bill/cranial-cover/builder-optics meshes','all existing materials and historical curves','existing owner/era tags, including Advanced-only optic eligibility','jaw rigid attachment and journal hardware'],
      'limits':['Neutral formed root and mouth interface need actual rest/open native review; jaw closure/penetration is not certified.','Changes are authored reconstruction; hidden cheek/root seating is proposed.','No rendering, export, runtime selection, material finishing, continuous clearance or owner acceptance.']}
