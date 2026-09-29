"""Constructed proximal bill shell and a closer neutral mandible.

Second V19 proposal. July is head-only authority; the current owner target
supports a narrower neutral gape. Dimensions are authored reconstruction.
All pieces are rigid. No texture, optic change or contact landmark movement.
"""
import math
import bpy, bmesh
from mathutils import Vector


def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)


def install_surface(obj, points, faces, materials, wall):
    inv=obj.matrix_world.inverted()
    used=sorted({i for face in faces for i in face});remap={old:i for i,old in enumerate(used)}
    mesh=bpy.data.meshes.new(obj.name+' V19 formed shell')
    mesh.from_pydata([inv@points[i] for i in used],[],[tuple(remap[i] for i in face) for face in faces]);mesh.update()
    for m in materials:mesh.materials.append(m)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    # The authored circular sections have outer winding; orient side sheets
    # toward their side when their average normal has a clear lateral sign.
    avg=Vector((0,0,0))
    for f in mesh.polygons:avg+=obj.matrix_world.to_3x3()@f.normal
    mean_x=sum(points[i].x for i in used)/len(used)
    if abs(mean_x)>.035 and avg.x*mean_x<0:
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    old=obj.data;obj.data=mesh
    if old and not old.users:bpy.data.meshes.remove(old)
    obj.modifiers.clear();mod=obj.modifiers.new('Finite formed bill wall','SOLIDIFY');mod.thickness=wall;mod.offset=-1;mod.use_even_offset=True
    mod=obj.modifiers.new('Forged panel edge radius','BEVEL');mod.width=.0008;mod.segments=2
    for f in mesh.polygons:f.use_smooth=True


def split_proximal_bill():
    obj=bpy.data.objects['Profiled upper bill blade 0'];owner=obj.parent
    assert len(obj.data.vertices)==43*48 and owner.name=='upper-bill'
    pts=[obj.matrix_world@v.co for v in obj.data.vertices]
    mats=list(obj.data.materials)
    groups={'body':[], 'left':[], 'right':[]}
    for j in range(42):
        for k in range(48):
            group='body'
            # Curved, swept side seams. The dorsal cap and cutting under-edge
            # remain the original shell; side skins replace those face cells.
            sidek=k if k<24 else k-24
            if 6<=sidek<18:
                v=(sidek-6+.5)/12
                begin=4+int(4*(1-v)**2)
                end=39-int(7*v*v)
                if begin<=j<end:group='right' if k<24 else 'left'
            groups[group].append((j*48+k,(j+1)*48+k,(j+1)*48+(k+1)%48,j*48+(k+1)%48))
    install_surface(obj,pts,groups['body'],mats,.004)
    records=[]
    for side in ('left','right'):
        name=f'V19 fitted proximal bill cheek plate {side}'
        mesh=bpy.data.meshes.new(name+' placeholder');panel=bpy.data.objects.new(name,mesh)
        bpy.context.scene.collection.objects.link(panel);panel.parent=owner;panel.matrix_world=owner.matrix_world.copy()
        panel['exteriorEras']='maker,mechanic,builder';panel['region']='head';panel['surfaceRole']='passive formed bill shell'
        panel['constructionDescription']='Finite side skin replaces the proximal bill side faces; seam reveals panel thickness, not a decorative plate on top of an intact bill.'
        ids={i for face in groups[side] for i in face}
        # A narrow manufactured separation is created in the panel geometry;
        # the cap and retained under-edge are not stretched across it.
        center=sum((pts[i] for i in ids),Vector())/len(ids)
        localpts=[p.copy() for p in pts]
        for i in ids:
            p=pts[i];q=center+(p-center)*.988
            # Very slight convex rise, tapered by the perimeter contraction.
            q.x+=.0015 if side=='right' else -.0015
            localpts[i]=q
        install_surface(panel,localpts,groups[side],mats,.004)
        records.append({'name':name,'faces':len(groups[side]),'wallM':.004,'seamContraction':.012})
    return records


def raise_mandible():
    changed=[];maxmove=0
    for side in (-1,1):
        obj=bpy.data.objects[f'Forked forged mandible {side}'];inv=obj.matrix_world.inverted()
        assert len(obj.data.vertices)==882
        for v in obj.data.vertices:
            t=((v.index%(49*9))//9)/48
            # Leave the journal seat and distal return exact. Lift the broad
            # hanging middle into a much narrower resting cheek opening.
            weight=smooth((t-.08)/.30)*(1-smooth((t-.66)/.34))
            move=.045*weight;p=obj.matrix_world@v.co;p.z+=move;v.co=inv@p;maxmove=max(maxmove,move)
        obj.data.update();changed.append(obj.name)
    return changed,maxmove


def apply():
    panels=split_proximal_bill();changed,maxmove=raise_mandible();bpy.context.view_layer.update()
    return {'region':'head','changed':['Profiled upper bill blade 0']+changed,'added':[p['name'] for p in panels],
      'construction':'Replace broad proximal bill side surfaces with two fitted 4mm formed panels under retained dorsal cap and cutting edge. Raise middle mandible 45mm maximum while retaining journal seat and distal endpoint to reduce the smile-shaped neutral gape.',
      'controllingReference':'Owner-preferred July head only; owner-resupplied target for neutral mouth relationship. Exact dimensions and plate divisions are proposed.',
      'plates':panels,'maximumMandibleRiseM':maxmove,'eraEligibility':'passive inherited surfaces in all three eras; no sensing or power additions',
      'preserved':['all node transforms and parents','bill-contact landmark','orbital04 construction','all materials and unrelated meshes'],
      'limits':['Segmented surfaces have narrow exposed seams and require sampled jaw clearance and close visual inspection.','Static rest fit does not establish contact, motion or whole-character artistic acceptance.']}
