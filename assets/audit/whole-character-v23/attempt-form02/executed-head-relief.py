"""Second composed visual pass: fitted bill cells and narrower orbital rim.
Uses the frozen V23 head construction after its own bounded region study.
All changed parts are rigid; no material finish or texture changes.
"""
import bpy, math
from mathutils import Vector

def apply(headlib):
    install=headlib['install'];ribbon=headlib['ribbon'];bill_piece=headlib['bill_piece'];deform=headlib['deform']
    changed=[];added=[]
    sectors=[('Profiled upper bill blade 0',list(range(0,7))+list(range(18,31))+list(range(42,48))),
             ('V19 fitted proximal bill cheek plate right',list(range(7,18))),
             ('V19 fitted proximal bill cheek plate left',list(range(31,42)))]
    for name,indices in sectors:
        p,f,c=bill_piece(0,.322,indices);changed.append(install(name,p,f,.004,c))
        old=bpy.data.objects[name];n='V23 distal bill root cell '+name
        o=bpy.data.objects.new(n,old.data.copy());bpy.context.scene.collection.objects.link(o)
        o.parent=old.parent;o.matrix_parent_inverse=old.matrix_parent_inverse.copy();o.matrix_basis=old.matrix_basis.copy()
        for k in old.keys():o[k]=old[k]
        p,f,c=bill_piece(.333,.66,indices);install(n,p,f,.004,c);added.append(n)
    for side in (-1,1):
        # The receiving brow sits over the port. Its front foot descends into
        # the bill root; the back foot lands on the temporal journal plate.
        p,f=ribbon(side,[(.151,-.393,1.831,.018),(.160,-.446,1.835,.019),
            (.162,-.493,1.830,.017),(.151,-.543,1.808,.015),(.131,-.580,1.778,.014)])
        changed.append(install(f'Forged orbital brow {side}',p,f))
        p,f=ribbon(side,[(.141,-.411,1.725,.014),(.154,-.444,1.696,.018),
            (.151,-.491,1.678,.015),(.132,-.541,1.692,.016),(.108,-.590,1.719,.017)])
        changed.append(install(f'Broad swept cheek band {side}',p,f))
        # Seat the complete optic assembly together, retaining lens/housing
        # relationships. A modest outward shift makes the mechanical port read.
        for name in (f'Orbital passive retaining race {side}',f'Recessed orbital bearing {side}',
                     f'Seated passive optic housing {side}',f'Seated Advanced optic {side}'):
            o=bpy.data.objects[name];deform(o,lambda p:p+Vector((side*.009,0,0)));changed.append(name)
    # Crown curvature is still formed metal, but remove the inflated central
    # bulge that made its individual plates read as soft rolled tiles.
    for j in range(5):
        name=f'Rounded swept crown lamina {j}';o=bpy.data.objects[name]
        inv=o.matrix_world.inverted();o.data=o.data.copy()
        pts=[o.matrix_world@v.co for v in o.data.vertices];xmax=max(abs(p.x) for p in pts)
        for v,p in zip(o.data.vertices,pts):
            p.z-=.012*max(0,1-(p.x/max(xmax,1e-6))**2);v.co=inv@p
        o.data.update();changed.append(name)
    return {'changed':changed,'added':added,'construction':'Split bill into actual rigid cells; fitted narrow brow/cheek rim; complete optic seat9mm outward; flatter crown plate forming.',
            'limits':['Proposed fit; finite openings and joint motion require fresh review.','No color or texture improvement included.']}
