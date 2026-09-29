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


def cheek_geometry(side):
    # A broad suborbital cheek return bridges the rear journal shoulder to the
    # deepened bill root; it stays fixed to head, separately from the jaw.
    rows=[(.132,-.350,1.680,.018),(.148,-.395,1.668,.030),
          (.135,-.460,1.664,.027),(.120,-.515,1.685,.022),
          (.101,-.552,1.704,.012)]
    along=48;across=8;n=(along+1)*(across+1);pts=[];faces=[]
    for skin in (0,1):
        for j in range(along+1):
            t=j/along;q=spline(rows,t);a=spline(rows,max(0,t-.002));b=spline(rows,min(1,t+.002))
            dy,dz=b.y-a.y,b.z-a.z;length=max(1e-8,math.hypot(dy,dz))
            for k in range(across+1):
                u=k/across;w=(2*u-1)*q[3]
                x=q.x+(.0018*math.sin(math.pi*u) if skin==0 else -.006)
                p=Vector((side*x,q.y-dz/length*w,q.z+dy/length*w));p.y=compact_y(p.y);pts.append(p)
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


def apply():
    nodes={o.name:([list(r) for r in o.matrix_world],o.parent.name if o.parent else None,dict(o.items())) for o in bpy.data.objects if o.type=='EMPTY'}
    changed=[];replaced=[];seats=[]
    # The complete upper-bill group uses one map, including its panel fixings,
    # root hood and proximal skins, so bill/head attachment is not disconnected.
    for obj in list(bpy.data.objects):
        if obj.type!='MESH' or not obj.parent:continue
        if obj.parent.name=='upper-bill':deform(obj,bill_point);changed.append(obj.name)
        elif obj.parent.name=='jaw':deform(obj,jaw_point);changed.append(obj.name)

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
        cheek=bpy.data.objects[f'Broad swept cheek band {side}'];verts,faces=cheek_geometry(side)
        install_cheek(cheek,verts,faces);changed.append(cheek.name);replaced.append(cheek.name)
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
            def bridge(p):
                q=p.copy();r=math.hypot(p.y-cy,p.z-cz);w=1-smooth((r-.069)/.025)
                q.x-=side*.010*w;nr=r-.0045*w;q.y=cy+(p.y-cy)*nr/r;q.z=cz+(p.z-cz)*nr/r;return q
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
      'construction':'Compact/deepen the entire bill root with a shared map, shorten its thick curved hook, and align the rigid jaw around unchanged journal articulation. Rebuild two broad finite suborbital cheek returns with reseated fixings; seat existing optics10mm inboard with a narrower retainer and supported bridges. Re-form the crown into tighter aft/down swept tapered guards, retaining leading fitting clearance returns.',
      'controllingReferences':['owner-resupplied whole-bird likeness target','July owner-preferred head identity ONLY'],
      'parameters':{'billForwardCompression':.15,'rootWidthGrowth':.18,'rootDepthGrowth':.16,'distalHookVerticalCompression':.14,'maximumJawForeRiseM':.008,'crownTipTransverseTaper':.28,'crownTipAftSweepM':.015,'crownTipDownSweepM':.010,'leadingTemporalTipUpReturnM':.004},
      'opticSeats':seats,'billContactNativeWorld':list(contact),'proposedBillContact':{'nativeWorldM':list(contact),'method':'minimum nativeY vertex of evaluated triangulated upper-bill surface, including wall/bevel modifiers; a linear triangle surface extremum occurs on its boundary vertex','evaluatedObject':contact_owner,'evaluatedTriangleIndex':contact_triangle,'unchangedMarker':'bill-contact node is preserved and now geometrically stale; update after region geometry checks only'},
      'preserved':['all52EMPTY names/parents/world rests/custom properties','all outside head/jaw/upper-bill/cranial-cover/builder-optics meshes','all existing materials and historical curves','existing owner/era tags, including Advanced-only optic eligibility','jaw rigid attachment and journal-root geometry'],
      'limits':['Neutral formed root and mouth interface need actual rest/open native review; jaw closure/penetration is not certified.','Changes are authored reconstruction; hidden cheek/root seating is proposed.','No rendering, export, runtime selection, material finishing, continuous clearance or owner acceptance.']}
