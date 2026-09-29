"""V35 head-to-trunk proportion study, baked into rigid authored geometry.

The head envelope grows about its retained cervical bearing. The bill/cheek
design is not changed or accepted by this operation. Neck-end shafts and
receiving seats remain exact; their cranial load bows transition to the larger
head. No runtime node scale or stretched metal animation is introduced.
"""
import math
import bpy
from mathutils import Vector

FACTOR = 1.16
FIXED = {'V21 head captive shaft', 'V23 cervical 4 captive pin',
         'V31 cranial load bow shaft seat -1',
         'V31 cranial load bow shaft seat 1'}


def ease(t):
    t = min(1.0, max(0.0, t))
    return t*t*(3-2*t)


def apply():
    bpy.context.view_layer.update()
    head = bpy.data.objects['head']
    pivot = head.matrix_world.translation.copy()
    descendants = list(head.children_recursive)
    meshes = [o for o in descendants if o.type == 'MESH']
    original = {o.name: [o.matrix_world@v.co for v in o.data.vertices]
                for o in meshes}
    empties = [o for o in descendants if o.type == 'EMPTY']
    matrices = {o.name: o.matrix_world.copy() for o in empties}

    def depth(o):
        count = 0
        while o.parent:
            count += 1
            o = o.parent
        return count

    moved = []
    for o in sorted(empties, key=depth):
        old = matrices[o.name]
        new = old.copy()
        new.translation = pivot+(old.translation-pivot)*FACTOR
        o.matrix_world = new
        bpy.context.view_layer.update()
        if (old.translation-new.translation).length > 1e-8:
            moved.append({'name': o.name, 'before': list(old.translation),
                          'after': list(new.translation)})

    changes = []
    for o in meshes:
        if o.name in FIXED:
            continue
        source = original[o.name]
        target = []
        for p in source:
            # Preserve the load bows' root attachment, not an arbitrary
            # scaled bearing bore. Upper frame shares the head reform.
            weight = ease((p.z-pivot.z-.016)/.080) if (
                'passive cranial load bow' in o.name) else 1.0
            target.append(p+(p-pivot)*(FACTOR-1)*weight)
        inv = o.matrix_world.inverted()
        o.data = o.data.copy()
        for v, p in zip(o.data.vertices, target):
            v.co = inv@p
        o.data.update()
        assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
        o['v35HeadPresence'] = 'Baked head envelope proportion proposal; fixed cervical bearing retained'
        changes.append({'name': o.name, 'owner': o.parent.name,
                        'maximumVertexDisplacementM': max(
                            (a-b).length for a,b in zip(source,target))})

    bpy.context.view_layer.update()
    for name in FIXED:
        o = bpy.data.objects[name]
        assert max((o.matrix_world@v.co-p).length for v,p in
                   zip(o.data.vertices,original[name])) < 1e-7
    return {'region': 'head-to-trunk proportion study',
            'status': 'Unaccepted visual proportion proposal',
            'factor': FACTOR, 'pivotNative': list(pivot),
            'changedMeshes': changes, 'changedNodes': moved,
            'fixedBearingMeshes': sorted(FIXED), 'added': [], 'removed': [],
            'materialsChanged': False,
            'limits': ['Perspective references motivate apparent proportion, not recovered dimensions.',
                       'Bill/jaw shape direction remains unapproved.',
                       'Head/jaw/neck clearance and actual contact must be rechecked.',
                       'Existing hidden processing layout remains a proposal.']}
