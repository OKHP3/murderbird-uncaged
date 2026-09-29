"""V34 broad shoulder/breast envelope study on the exact V33 composition.

An authoring-space reform of existing rigid pieces, not runtime deformation.
The high mantle rises toward the nape and wraps forward over the lateral
breast. Existing receiving edges and their support bows share one field.
Joint journals, anatomical-left stop, neck, feet and materials stay exact.
"""
import math
import bpy, bmesh
from mathutils import Vector, Matrix

OWNERS = {'left-mantle', 'right-mantle',
          'left-wing-shield', 'right-wing-shield'}


def ease(t):
    t = min(1.0, max(0.0, t))
    return t*t*(3.0-2.0*t)


def signature(o):
    return (o.parent.name if o.parent else None,
            tuple(tuple(r) for r in o.matrix_world),
            tuple(tuple(v.co) for v in o.data.vertices),
            tuple(tuple(p.vertices) for p in o.data.polygons))


def apply():
    bpy.context.view_layer.update()
    joints = [bpy.data.objects[n].matrix_world.translation.copy()
              for n in ('left-mantle', 'right-mantle', 'left-wing-shield',
                        'right-wing-shield')]
    nodes = {o.name: tuple(tuple(r) for r in o.matrix_world)
             for o in bpy.data.objects if o.type == 'EMPTY'}
    candidates = [o for o in bpy.data.objects
                  if o.type == 'MESH' and o.parent and o.parent.name in OWNERS
                  and o.get('surfaceRole') != 'bearing'
                  and 'travel stop' not in o.name
                  and 'oblique shoulder saddle' not in o.name
                  and 'shoulder journal bonnet' not in o.name
                  and 'swept upper wing load member' not in o.name
                  and not o.name.startswith(('V23 root ', 'V33 ',
                                             'V24 rising thoracic receiving cheek'))]
    names = {o.name for o in candidates}
    protected = {o.name: signature(o) for o in bpy.data.objects
                 if o.type == 'MESH' and o.name not in names}
    changed = []

    def shape(p, owner):
        # The center throat and actual journal seats are zero-displacement
        # islands. Coherent reform extends into both moving and fixed skins.
        side = 1 if p.x >= 0 else -1
        lateral = ease((abs(p.x)-.145)/.135)
        upper = ease((p.z-.970)/.290)
        seat = min(ease(((p-j).length-.074)/.070) for j in joints)
        weight = lateral*upper*seat
        # The preserved fixed receiving cheeks already rise above the old
        # mantle. Reform the outer crown into a dome, not an elevated flat
        # shelf or a second collar climbing behind the neck.
        dome = .25 + .75*math.exp(-((p.y-.035)/.170)**2)
        fixed = .30 if owner in {'body', 'breastplate'} else 1.0
        inner_wrap = ease((.430-abs(p.x))/.145)
        front_return = ease((-p.y-.105)/.080)*ease((p.z-1.145)/.080)
        # More proximal height and forward wrap, not extra wingspan or a
        # longer trailing train. The low elbow and rear outline stay fixed.
        return p + Vector((-side*(.008+.052*inner_wrap)*weight*fixed, -.070*weight*fixed,
                           (.142*dome-.075*front_return)*weight*fixed))

    for o in candidates:
        inv = o.matrix_world.inverted()
        before = [o.matrix_world@v.co for v in o.data.vertices]
        after = [shape(p, o.parent.name) for p in before]
        displacement = max((a-b).length for a,b in zip(after,before))
        if displacement < 1e-8:
            continue
        o.data = o.data.copy()
        for v,p in zip(o.data.vertices,after):
            v.co = inv@p
        o.data.update()
        assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
        o['v34EnvelopeProposal'] = 'Rigid authored shoulder/nape and lateral breast reform; original single owner retained'
        changed.append({'name': o.name, 'owner': o.parent.name,
                        'maximumVertexDisplacementM': displacement,
                        'beforeBounds': [[min(p[k] for p in before) for k in range(3)],
                                         [max(p[k] for p in before) for k in range(3)]],
                        'afterBounds': [[min(p[k] for p in after) for k in range(3)],
                                        [max(p[k] for p in after) for k in range(3)]]})
    # The elevated canopy needs its own rounded upper return. It terminates
    # beside the fixed receiver; it never bridges into the body owner.
    added=[]
    for label,side in [('left',1),('right',-1)]:
        owner=bpy.data.objects[label+'-mantle']
        backing=bpy.data.objects[f'{label} profiled mantle backing v4 {label}-mantle']
        edge=[backing.matrix_world@v.co for v in list(backing.data.vertices)[:25]]
        material=bpy.data.objects[f'V28 {label} canopy oblique course 1 plate 4'].data.materials[0]
        def point(u,t):
            k=min(23,int(u*24));a=u*24-k;p=edge[k].lerp(edge[k+1],a)
            inner=Vector((side*(.268+.004*math.sin(math.pi*u)),p.y,1.256+.014*math.sin(math.pi*u)))
            return p.lerp(inner,t)+Vector((0,0,.018*math.sin(math.pi*t)))
        # Three finite formed roof panels, deliberately separate from the
        # long directional side courses. A narrow seam separates each panel.
        for section in range(3):
            verts=[];faces=[];R=12;C=12
            u0=section/3+.003;u1=(section+1)/3-.003
            for j in range(R+1):
                t=.045+.955*j/R
                for k in range(C+1):
                    u=u0+(u1-u0)*k/C;verts.append(point(u,t))
            for j in range(R):
                for k in range(C):
                    a=j*(C+1)+k;faces.append((a,a+1,a+C+2,a+C+1))
            name=f'V34 {label} shoulder crown return {section+1}'
            mesh=bpy.data.meshes.new(name+' formed wall');mesh.from_pydata(verts,[],faces);mesh.materials.append(material);mesh.update()
            o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.parent=owner;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_world=Matrix.Identity(4)
            bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
            if mesh.polygons[len(mesh.polygons)//2].normal.z<0:
                bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
            for f in mesh.polygons:f.use_smooth=True
            q=o.modifiers.new('Finite 3 mm crown wall','SOLIDIFY');q.thickness=.003;q.offset=-1;q.use_even_offset=False
            o['surfaceRole']='guard';o['region']='mantle';o['exteriorEras']='maker,mechanic,builder';o['constructionClass']='proposed-passive';o['wallM']=.003
            o['authoringRole']='Rigid moving canopy upper return; terminates beside fixed receiver without bridging shoulder pivot'
            added.append(name)
    bpy.context.view_layer.update()
    assert nodes == {o.name: tuple(tuple(r) for r in o.matrix_world)
                     for o in bpy.data.objects if o.type == 'EMPTY'}
    assert protected == {n: signature(bpy.data.objects[n]) for n in protected}
    return {'region': 'rounded-shoulder-envelope', 'changedMeshes': changed,
            'addedMeshes': added, 'changedNodes': [], 'protectedOutsideMeshesExact': len(protected),
            'reference': 'Owner whole-bird target; high rounded mantle receives neck and overlaps lateral breast. Hidden construction remains authored.',
            'construction': 'One shared rest-shape field reforms the moving mantle skin and supporting bows. Fixed body and breast receivers remain exact. Every mesh remains rigid on its original owner; three formed roof return panels per side close the raised canopy edge; no powered hardware, new materials or runtime deformation.',
            'eraEligibility': 'Existing per-component tags retained unchanged; no powered hardware added.',
            'protected': 'All node rests, circular bearing geometry, anatomical-left stop, neck/head, and feet.',
            'limits': ['Broad proportion proposal awaiting matched visual review.',
                       'Reformed receiving edges require fresh clearance samples.',
                       'No exact dimensions inferred from the perspective artwork.']}
