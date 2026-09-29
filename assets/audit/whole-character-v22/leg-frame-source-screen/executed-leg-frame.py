"""V22 formed passive limb members on frozen V21 Construction06.

Authored in native metres/Z-up/-Y-front, before the V22 proportion map.
Finite open-channel load members replace eight smooth rails on their measured
three-ring paths. Formed split guards reveal the original truss and journals.
No joints, foot surfaces, powered capability, or material definitions change.
"""
import bpy
import bmesh
from mathutils import Vector, Matrix

ERAS = 'maker,mechanic,builder'
OWNERS = ('left-thigh', 'left-shin', 'right-thigh', 'right-shin')
BASE_SHA256 = '79ad3e368e7b75edbbc758b1264a1ccaf34f284c6ca185ee8441875576a6f54c'
SECTION = {'thigh': (.026, .034, .008), 'shin': (.024, .030, .007)}


def signature(o):
    return (o.parent.name if o.parent else None,
            tuple(tuple(float(v) for v in r) for r in o.matrix_world),
            tuple((k, repr(o[k])) for k in sorted(o.keys())))


def mesh_signature(o):
    return (signature(o), tuple(tuple(v.co) for v in o.data.vertices),
            tuple(tuple(p.vertices) for p in o.data.polygons),
            tuple(m.name if m else None for m in o.data.materials))


def basis(direction):
    axis = direction.normalized()
    u = Vector((1, 0, 0)); u = (u-axis*u.dot(axis)).normalized()
    v = axis.cross(u).normalized()
    if v.y > 0: v.negate()
    return u, v


def install(name, owner, verts, faces, material, role, existing=None):
    obj = existing
    inverse = obj.matrix_world.inverted() if obj else owner.matrix_world.inverted()
    mesh = bpy.data.meshes.new(name+' formed mesh')
    mesh.from_pydata([inverse@Vector(p) for p in verts], [], faces)
    mesh.update()
    bm = bmesh.new(); bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges), name
    assert bm.calc_volume(signed=True) > 0, name
    bm.to_mesh(mesh); bm.free()
    if material: mesh.materials.append(material)
    if obj:
        obj.data = mesh
        for mod in list(obj.modifiers): obj.modifiers.remove(mod)
    else:
        obj = bpy.data.objects.new(name, mesh); bpy.context.scene.collection.objects.link(obj)
        obj.parent = owner; obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.matrix_basis = Matrix.Identity(4)
    for poly in mesh.polygons: poly.use_smooth = False
    bevel = obj.modifiers.new('V22 eased formed edges', 'BEVEL')
    bevel.width = .0012; bevel.segments = 2; bevel.limit_method = 'ANGLE'
    obj['region'] = 'leg-frame'; obj['surfaceRole'] = role
    obj['exteriorEras'] = ERAS; obj['constructionClass'] = 'inherited-passive'
    obj['proposal'] = True; obj['constructionOwner'] = owner.name
    obj['articulatesAcrossJoint'] = False
    return obj


def channel(centres, width, depth, wall):
    """One thick C section: rear web and paired flanges; front remains open."""
    verts=[]; faces=[]
    cross=((-1,-1),(1,-1),(1,1),(1-wall/width,1),
           (1-wall/width,-1+wall/depth),(-1+wall/width,-1+wall/depth),
           (-1+wall/width,1),(-1,1))
    for j,c in enumerate(centres):
        u,v = basis(centres[min(j+1,2)]-centres[max(j-1,0)])
        scale = (.78,1,.74)[j]
        for x,y in cross: verts.append(c+u*(x*width*scale)+v*(y*depth*scale))
    for j in range(2):
        for k in range(8):
            a=j*8+k; b=j*8+(k+1)%8
            faces.append((a,b,b+8,a+8))
    faces.extend((tuple(reversed(range(8))),tuple(range(16,24))))
    return verts,faces


def guard(p0, p1, side, kind):
    """Finite bowed half guard, with a formed side return, not a limb sleeve."""
    u,v=basis(p1-p0); verts=[]; faces=[]
    rows=((.27,.70),(.33,1),(.54,1),(.70,.78),(.74,.47))
    cols=(-1,-.65,.6,1)
    for layer in (0,1):
        for t,w in rows:
            for a in cols:
                x=side*(.040+a*.029*w)
                # Crest is forward; outside folds back toward the adjacent rail.
                depth=.058 + .008*(1-a*a) - .010*max(0,a)
                verts.append(p0.lerp(p1,t)+u*x+v*(depth-layer*.0055))
    n=len(rows)*len(cols)
    for j in range(len(rows)-1):
        for k in range(len(cols)-1):
            a=j*4+k; faces.extend(((a,a+4,a+5,a+1),(n+a+1,n+a+5,n+a+4,n+a)))
    boundary=list(range(4))+[j*4+3 for j in range(1,len(rows))]
    boundary += list(range(n-2,n-5,-1))+[j*4 for j in range(len(rows)-2,0,-1)]
    for i,a in enumerate(boundary):
        b=boundary[(i+1)%len(boundary)];faces.append((a,b,n+b,n+a))
    return verts,faces


def apply():
    bpy.context.view_layer.update()
    nodes={o.name:signature(o) for o in bpy.data.objects if o.type=='EMPTY'}
    outside={o.name:mesh_signature(o) for o in bpy.data.objects if o.type=='MESH' and (not o.parent or o.parent.name not in OWNERS)}
    changed=[];added=[];removed=[];paths=[]
    mat=bpy.data.materials['Neutral / frame']
    for side in ('left','right'):
        for kind,distal in (('thigh','shin'),('shin','foot')):
            owner=bpy.data.objects[side+'-'+kind]
            p0=owner.matrix_world.translation.copy();p1=bpy.data.objects[side+'-'+distal].matrix_world.translation.copy()
            suffixes=('', '.001') if kind=='thigh' else ('.002','.003')
            for suffix in suffixes:
                name=side+' tapered passive load rail'+suffix; obj=bpy.data.objects[name]
                world=[obj.matrix_world@v.co for v in obj.data.vertices]
                assert len(world)==36, (name,len(world))
                centres=[sum(world[j*12:(j+1)*12],Vector())/12 for j in range(3)]
                verts,faces=channel(centres,*SECTION[kind])
                obj=install(name,owner,verts,faces,mat,'frame',obj)
                obj['constructionDescription']='Three-station formed C-channel; measured old ring centres preserved, web and flanges replace round swollen bar.'
                changed.append(name); paths.append({'name':name,'owner':owner.name,'measuredWorldCentres':[list(c) for c in centres],'halfWidthHalfDepthWallM':list(SECTION[kind])})
            for half in (-1,1):
                name=f'V22 {side} {kind} formed anterior half-guard {half}'
                verts,faces=guard(p0,p1,half,kind)
                obj=install(name,owner,verts,faces,mat,'guard');added.append(name)
                obj['constructionDescription']='Bowed tapered finite half-guard with returned free edge; central machinery slit and round joint faces remain exposed.'
    obsolete=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name in OWNERS and (o.name.startswith('Limb sheath fixing') or o.name in ('V18 left split shin load web','V18 right split shin load web'))]
    for obj in obsolete:
        removed.append({'name':obj.name,'owner':obj.parent.name,'reason':'Obsolete smooth-sheath fixing island or old split guard, superseded by formed members/guards.'})
        bpy.data.objects.remove(obj,do_unlink=True)
    bpy.context.view_layer.update()
    assert nodes=={o.name:signature(o) for o in bpy.data.objects if o.type=='EMPTY'}
    assert all(mesh_signature(bpy.data.objects[n])==s for n,s in outside.items())
    return {'status':'proposed formed passive limb mass; awaiting whole-figure visual gate',
            'changed':changed,'added':added,'removed':removed,'sourceRailPaths':paths,
            'preservedOriginalNodes':len(nodes),'preservedOutsideMeshes':len(outside),
            'construction':'Eight open C-channel load members retain exact three-station source paths. Eight finite tapered half-guards replace old shin web and floating sheath fasteners; original trusses and round journals remain readable.',
            'classification':'All new/rebuilt surfaces inherited-passive frame/guard, eligible maker,mechanic,builder. No piston/actuator/sensor added.',
            'limits':['Static rest geometry proposal only.','No joint travel or whole-model clearance proven.','Existing retained truss/journal and ankle mating geometry remains unmodified.','Owner likeness acceptance pending.']}
