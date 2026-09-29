"""One formed-bill profile proposal on the loaded combined V18 scene.

The July image controls head identity only. Coordinates below are local
surface relief choices fitted to the existing bill meshes, not measurements
read from the perspective reference. Owners, pivots, contact marker, materials,
and era rules remain inherited.
"""
import math
import bpy
import bmesh
from mathutils import Vector


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _world_vertices(obj):
    return [obj.matrix_world @ v.co for v in obj.data.vertices]


def _interp_ring(points, station, angle_index, stations=43, ring=48):
    """Bilinearly sample the preserved generated bill shell grid."""
    a0 = int(math.floor(station)); a1 = min(stations - 1, a0 + 1)
    at = station - a0
    b0 = int(math.floor(angle_index)); b1 = min(ring - 1, b0 + 1)
    bt = angle_index - b0
    def sample(j, k):
        return points[j * ring + (k % ring)]
    p00, p10 = sample(a0, b0), sample(a0, b1)
    p01, p11 = sample(a1, b0), sample(a1, b1)
    return ((p00 * (1-bt) + p10 * bt) * (1-at) +
            (p01 * (1-bt) + p11 * bt) * at)


def _add_side_panel(source, side, zone, j0, j1):
    owner = source.parent
    assert owner and owner.name == 'upper-bill'
    src = _world_vertices(source)
    assert len(src) == 43 * 48, (source.name, len(src))
    k0, k1 = (8, 16) if side > 0 else (32, 40)
    longitudinal, transverse = 25, 9
    outer, back = [], []
    for i in range(longitudinal + 1):
        u = i / longitudinal
        station = j0 + (j1-j0) * u
        end_taper = math.sin(math.pi*u) ** 0.42
        for k in range(transverse + 1):
            v = k / transverse
            angle = k0 + (k1-k0)*v
            p = _interp_ring(src, station, angle)
            relief = 0.002 + 0.006 * (math.sin(math.pi*v) ** 0.8) * end_taper
            outer.append(p + Vector((side * relief, 0, 0)))
            back.append(p + Vector((side * 0.0007, 0, 0)))
    count = len(outer)
    verts = outer + back
    faces = []
    stride = transverse + 1
    def front(i, k): return i*stride+k
    def rear(i, k): return count+i*stride+k
    for i in range(longitudinal):
        for k in range(transverse):
            a,b,c,d=front(i,k),front(i+1,k),front(i+1,k+1),front(i,k+1)
            faces.append((a,b,c,d))
            faces.append((rear(i,k+1),rear(i+1,k+1),rear(i+1,k),rear(i,k)))
        faces.extend([
            (front(i,0),rear(i,0),rear(i+1,0),front(i+1,0)),
            (front(i,transverse),front(i+1,transverse),rear(i+1,transverse),rear(i,transverse))])
    for k in range(transverse):
        faces.extend([
            (front(0,k+1),rear(0,k+1),rear(0,k),front(0,k)),
            (front(longitudinal,k),rear(longitudinal,k),rear(longitudinal,k+1),front(longitudinal,k+1))])
    name = f'Formed upper bill side panel {side} {zone}'
    assert bpy.data.objects.get(name) is None
    inv = owner.matrix_world.inverted()
    mesh = bpy.data.meshes.new(name + ' relief shell')
    mesh.from_pydata([inv @ p for p in verts], [], faces); mesh.update()
    for mat in source.data.materials:
        if mat: mesh.materials.append(mat)
    bm = bmesh.new(); bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces)); bm.to_mesh(mesh); bm.free()
    obj = bpy.data.objects.new(name, mesh); bpy.context.scene.collection.objects.link(obj)
    obj.parent = owner; obj.matrix_parent_inverse.identity(); obj.matrix_world = owner.matrix_world.copy()
    obj['exteriorEras'] = 'maker,mechanic,builder'
    obj['region'] = 'head'
    obj['surfaceRole'] = 'formed passive bill side plate'
    obj['constructionDescription'] = 'Finite-thickness shallow formed side plate fitted to the existing upper-bill shell; two courses clarify the dorsal cap and hooked distal blade while leaving the cheek/mandible opening exposed.'
    return {'name': name, 'owner': owner.name, 'vertices': len(mesh.vertices),
            'sourceShell': source.name, 'profileStationRange': [j0, j1],
            'sideAngleSamples': [k0, k1], 'maxReliefM': 0.008,
            'fit': 'sampled from the existing upper-bill shell grid; small intentional lap over source surface'}


def _raise_forward_mandible():
    changed = []
    for side in (-1, 1):
        obj = bpy.data.objects[f'Forked forged mandible {side}']
        assert len(obj.data.vertices) == 2 * 49 * 9
        inverse = obj.matrix_world.inverted()
        for index, vertex in enumerate(obj.data.vertices):
            row = (index % (49 * 9)) // 9
            t = row / 48
            # Gently lift the forward third into the upper hook's concave
            # underside. Both the hinge and distal contact endpoint stay put.
            weight = _smooth((t - 0.56) / 0.17) * (1 - _smooth((t - 0.90) / 0.10))
            p = obj.matrix_world @ vertex.co
            p.z += 0.008 * weight
            vertex.co = inverse @ p
        obj.data.update(); changed.append(obj.name)
    return changed


def apply():
    for name in ('Profiled upper bill blade 0', 'Profiled upper bill blade 1',
                 'Forked forged mandible -1', 'Forked forged mandible 1',
                 'Distal mandible bridge', 'Broad swept cheek band -1', 'Broad swept cheek band 1'):
        assert bpy.data.objects.get(name), f'Missing pinned V18 head mesh: {name}'
    panels = []
    for side in (-1, 1):
        for zone, name, span in (
            ('root', 'Profiled upper bill blade 0', (4, 38)),
            ('hook', 'Profiled upper bill blade 1', (3, 37)),
        ):
            panels.append(_add_side_panel(bpy.data.objects[name], side, zone, *span))
    changed = _raise_forward_mandible()
    bpy.context.view_layer.update()
    return {
        'region': 'head',
        'changed': changed,
        'added': [p['name'] for p in panels],
        'newPivots': [],
        'construction': 'Two fitted side-panel courses per side clarify the formed upper-bill root and distal hook. A small forward-third mandible lift narrows the neutral cheek/gape slit while keeping its hinge and distal row fixed.',
        'controllingReference': 'July head-only identity reference; owner target controls whole-character recognition.',
        'panelFit': panels,
        'eraEligibility': 'All new panels are passive and available in Maker, Mechanic, and Builder eras; no powered/sensing role added.',
        'preserved': ['all upper-bill, jaw, and head owners','all 52 articulation pivots and transforms','existing bill-contact marker and source materials','all orbital geometry, crown geometry, and historical guides'],
        'limits': ['Panels intentionally lap the upper-bill shell; local intersection and jaw motion need integrated review.', 'Perspective illustration does not establish dimensions or hidden construction.', 'No likeness or clearance acceptance is implied.']
    }
