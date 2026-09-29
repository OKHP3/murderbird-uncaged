"""V34 broad shoulder/breast envelope study on the exact V33 composition.

An authoring-space reform of existing rigid pieces, not runtime deformation.
The high mantle rises toward the nape and wraps forward over the lateral
breast. Existing receiving edges and their support bows share one field.
Joint journals, anatomical-left stop, neck, feet and materials stay exact.
"""
import math
import bpy
from mathutils import Vector

OWNERS = {'body', 'breastplate', 'left-mantle', 'right-mantle',
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
        # More proximal height and forward wrap, not extra wingspan or a
        # longer trailing train. The low elbow and rear outline stay fixed.
        return p + Vector((-side*(.008+.052*inner_wrap)*weight*fixed, -.070*weight*fixed,
                           .142*weight*dome*fixed))

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
    bpy.context.view_layer.update()
    assert nodes == {o.name: tuple(tuple(r) for r in o.matrix_world)
                     for o in bpy.data.objects if o.type == 'EMPTY'}
    assert protected == {n: signature(bpy.data.objects[n]) for n in protected}
    return {'region': 'shoulder-breast-envelope', 'changedMeshes': changed,
            'changedNodes': [], 'protectedOutsideMeshesExact': len(protected),
            'reference': 'Owner whole-bird target; high rounded mantle receives neck and overlaps lateral breast. Hidden construction remains authored.',
            'construction': 'One shared rest-shape field reforms existing mantle skin, supporting bows and lateral breast receivers. Every mesh remains rigid on its original owner; no new material, hardware or runtime deformation.',
            'eraEligibility': 'Existing per-component tags retained unchanged; no powered hardware added.',
            'protected': 'All node rests, circular bearing geometry, anatomical-left stop, neck/head, and feet.',
            'limits': ['Broad proportion proposal awaiting matched visual review.',
                       'Reformed receiving edges require fresh clearance samples.',
                       'No exact dimensions inferred from the perspective artwork.']}
