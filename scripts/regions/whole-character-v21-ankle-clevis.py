"""V21 bounded ankle-clevis and foot-receiver proposal; in-memory only.

Call ``apply()`` on the opened V21 envelope03 native. The proposal keeps each
clevis on its shin side of the ankle joint and a separate receiver on the
foot side. It does not add capability, modify materials, or change the rig.
"""
import math

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree


ERAS = 'maker,mechanic,builder'
SIDES = (
    {'side': 'left', 'sign': 1, 'shin': 'left-shin', 'foot': 'left-foot',
     'shin_truss': 'Left shin open passive truss',
     'load_rails': ('left tapered passive load rail.002', 'left tapered passive load rail.003'),
     'bearing_core': 'left articulated bearing core.002',
     'metatarsal_rails': ('left metatarsal passive rail', 'left metatarsal passive rail.001'),
     'metatarsus_truss': 'Left metatarsus open passive truss',
     'legacy_yoke': 'V18 left ankle-to-foot-root yoke'},
    {'side': 'right', 'sign': -1, 'shin': 'right-shin', 'foot': 'right-foot',
     'shin_truss': 'Right shin open passive truss',
     'load_rails': ('right tapered passive load rail.002', 'right tapered passive load rail.003'),
     'bearing_core': 'right articulated bearing core.002',
     'metatarsal_rails': ('right metatarsal passive rail', 'right metatarsal passive rail.001'),
     'metatarsus_truss': 'Right metatarsus open passive truss',
     'legacy_yoke': 'V18 right ankle-to-foot-root yoke'},
)


def _world_vertices(obj):
    return [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]


def _nearest_surface(obj, target):
    """Return nearest point on raw mesh triangles transformed by matrix_world.

    This does not evaluate modifiers or dependency-graph geometry.
    """
    mesh = obj.data
    mesh.calc_loop_triangles()
    points = _world_vertices(obj)
    triangles = [tuple(triangle.vertices) for triangle in mesh.loop_triangles]
    tree = BVHTree.FromPolygons(points, triangles, all_triangles=True)
    point, _normal, _face, distance = tree.find_nearest(Vector(target))
    if point is None:
        raise ValueError(f'No raw triangle surface available for {obj.name}')
    return point.copy(), float(distance)


def _append_box_beam(verts, faces, start, end, width, depth):
    """Append one closed rectangular load web between world-space anchors."""
    axis = Vector(end) - Vector(start)
    if axis.length < 1e-5:
        raise ValueError('Clevis support web has coincident endpoints')
    axis.normalize()
    across = Vector((1, 0, 0))
    if abs(axis.dot(across)) > .92:
        across = Vector((0, 1, 0))
    across = (across - axis * axis.dot(across)).normalized()
    normal = axis.cross(across).normalized()
    base = len(verts)
    for point in (Vector(start), Vector(end)):
        for sa, sn in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            p = point + across * (sa * width * .5) + normal * (sn * depth * .5)
            verts.append(tuple(p))
    faces.extend([
        (base, base + 3, base + 2, base + 1),
        (base + 4, base + 5, base + 6, base + 7),
        (base, base + 1, base + 5, base + 4),
        (base + 1, base + 2, base + 6, base + 5),
        (base + 2, base + 3, base + 7, base + 6),
        (base + 3, base, base + 4, base + 7),
    ])


def _append_annular_clevis(verts, faces, center_x, center_y, center_z):
    """Append a finite, open-top annular cheek around the native-X axle."""
    x_half = .0045
    inner_r, outer_r = .068, .088
    segments = 40
    # The upper opening leaves the bearing/shaft approach visible. The long
    # lower arc captures the existing foot-owned race as a receiving journal.
    angles = [math.radians(50.0 - 280.0 * index / segments) for index in range(segments + 1)]
    base = len(verts)
    # Two x planes, with inner/outer radius vertices on each plane.
    for dx in (-x_half, x_half):
        for radius in (inner_r, outer_r):
            for angle in angles:
                y = center_y + radius * math.cos(angle)
                z = center_z + radius * math.sin(angle)
                verts.append((center_x + dx, y, z))
    stride = len(angles)
    inner_a = base
    outer_a = base + stride
    inner_b = base + stride * 2
    outer_b = base + stride * 3
    for i in range(segments):
        a, an = inner_a + i, inner_a + i + 1
        b, bn = outer_a + i, outer_a + i + 1
        c, cn = inner_b + i, inner_b + i + 1
        d, dn = outer_b + i, outer_b + i + 1
        faces.extend([
            (a, b, bn, an),       # first axial face
            (c, cn, dn, d),       # second axial face
            (a, an, cn, c),       # bearing-aperture wall
            (b, d, dn, bn),       # outside wall
        ])
    # Close only the two radial ends; the top opening remains intentional.
    faces.extend([
        (inner_a, inner_b, outer_b, outer_a),
        (inner_a + segments, outer_a + segments, outer_b + segments, inner_b + segments),
    ])
    return {
        'frontRoot': Vector(verts[outer_a]),
        'rearRoot': Vector(verts[outer_a + segments]),
        'innerRadiusM': inner_r,
        'outerRadiusM': outer_r,
    }


def _new_mesh(name, verts, faces, owner_name, material, role, description):
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    owner = bpy.data.objects[owner_name]
    obj.parent = owner
    obj.matrix_parent_inverse = owner.matrix_world.inverted()
    obj['region'] = 'leg' if owner_name.endswith(('-shin', '-foot')) else 'leg'
    obj['surfaceRole'] = role
    obj['exteriorEras'] = ERAS
    obj['constructionClass'] = 'inherited-passive'
    obj['proposal'] = True
    obj['authoringRole'] = description
    obj['geometryStatus'] = 'V21 ankle-clevis proposal; not visually or mechanically accepted'
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    return obj


def _pivot_signature():
    return {
        obj.name: {
            'parent': obj.parent.name if obj.parent else None,
            'world': tuple(round(float(obj.matrix_world[r][c]), 8) for r in range(4) for c in range(4)),
        }
        for obj in bpy.data.objects if obj.type == 'EMPTY'
    }


def apply():
    """Add paired shin clevises and foot-owned receiver yokes in memory only."""
    before_pivots = _pivot_signature()
    for side in SIDES:
        required = (side['shin'], side['foot'], side['shin_truss'], side['bearing_core'],
                    *side['load_rails'], *side['metatarsal_rails'], side['metatarsus_truss'], side['legacy_yoke'])
        assert all(name in bpy.data.objects for name in required), f"Missing {side['side']} interface objects"
        assert bpy.data.objects[side['shin_truss']].parent.name == side['shin']
        assert bpy.data.objects[side['bearing_core']].parent.name == side['foot']
        assert bpy.data.objects[side['metatarsus_truss']].parent.name == side['foot']
        assert bpy.data.objects[side['legacy_yoke']].parent.name == side['foot']
        for rail in side['load_rails']:
            assert bpy.data.objects[rail].parent.name == side['shin']
        for rail in side['metatarsal_rails']:
            assert bpy.data.objects[rail].parent.name == side['foot']

    staged_out = []
    created = []
    interfaces = []
    for side in SIDES:
        sign = side['sign']
        foot_pivot = bpy.data.objects[side['foot']]
        center = foot_pivot.matrix_world.translation.copy()
        center_x, center_y, center_z = center
        shin_rail = bpy.data.objects[side['shin_truss']]
        foot_core = bpy.data.objects[side['bearing_core']]
        metatarsus = bpy.data.objects[side['metatarsus_truss']]

        # Each shin-owned mesh carries two open C-cheeks around the existing
        # foot-owned axle. The radius leaves 2mm nominal radial clearance from
        # the foot race's documented 66mm outer silhouette.
        clevis_verts, clevis_faces, support_points = [], [], []
        for lateral in (-1, 1):
            cheek_x = center_x + lateral * .078
            ring = _append_annular_clevis(clevis_verts, clevis_faces, cheek_x, center_y, center_z)
            for end_name, ring_root in (('front', ring['frontRoot']), ('rear', ring['rearRoot'])):
                # Connect the open C ends to actual vertices of the retained
                # same-shin truss. Select by proximity; do not assume axes or
                # regenerate a rail with stale authoring coordinates.
                target = ring_root + Vector((lateral * .018, 0.0, .006))
                anchor, distance = _nearest_surface(shin_rail, target)
                assert distance < .075, f"{side['side']} {end_name} clevis cannot reach its shin truss ({distance:.4f}m)"
                _append_box_beam(clevis_verts, clevis_faces, ring_root, anchor, .014, .009)
                support_points.append({'cheekSide': lateral, 'end': end_name,
                                       'target': tuple(float(v) for v in target),
                                       'anchor': tuple(float(v) for v in anchor),
                                       'nearestDistanceM': distance})

        clevis_name = f"V21 {side['side']} ankle clevis fork"
        assert clevis_name not in bpy.data.objects
        clevis_material = shin_rail.data.materials[0]
        clevis = _new_mesh(clevis_name, clevis_verts, clevis_faces, side['shin'], clevis_material,
                           'bearing-frame',
                           'Shin-owned twin C-cheeks wrap the existing foot-owned ankle race; open aperture preserves articulation.')
        created.append(clevis.name)

        # Replace the small inherited foot-root strap with a visibly separate
        # foot-owned receiver pair from the bearing core into the retained
        # metatarsus truss. It never bridges to the shin-owned clevis.
        old_yoke = bpy.data.objects[side['legacy_yoke']]
        staged_out.append({'name': old_yoke.name, 'owner': side['foot'],
                           'reason': 'Replaced by the larger articulated foot-side receiver yoke; same owner and pivot.'})
        bpy.data.objects.remove(old_yoke, do_unlink=True)

        receiver_verts, receiver_faces, receiver_anchors = [], [], []
        foot_material = foot_core.data.materials[0]
        for lateral in (-1, 1):
            core_target = center + Vector((lateral * .030, 0.0, -.039))
            core_anchor, core_gap = _nearest_surface(foot_core, core_target)
            rail_name = side['metatarsus_truss']
            rail = bpy.data.objects[rail_name]
            rail_target = center + Vector((lateral * .050, -.060, -.095))
            rail_anchor, rail_gap = _nearest_surface(rail, rail_target)
            assert core_gap < .020 and rail_gap < .020, (
                f"{side['side']} foot receiver anchor mismatch: core {core_gap:.4f}m, rail {rail_gap:.4f}m")
            _append_box_beam(receiver_verts, receiver_faces, core_anchor, rail_anchor, .022, .010)
            receiver_anchors.append({'lateral': lateral, 'bearingCore': tuple(float(v) for v in core_anchor),
                                     'metatarsalRail': rail_name, 'railPoint': tuple(float(v) for v in rail_anchor),
                                     'coreSnapM': core_gap, 'railSnapM': rail_gap})
        receiver_name = f"V21 {side['side']} foot bearing receiver yoke"
        assert receiver_name not in bpy.data.objects
        receiver = _new_mesh(receiver_name, receiver_verts, receiver_faces, side['foot'], foot_material,
                             'frame',
                             'Foot-owned paired receiver webs connect the existing ankle core to the two metatarsal rails.')
        created.append(receiver.name)
        interfaces.append({'side': side['side'], 'ankleAxisNative': 'X',
                           'anklePivotWorld': tuple(float(v) for v in center),
                           'clevisRadialOpeningM': [.068, .088], 'nominalRaceOuterRadiusM': .066,
                           'shinRailSupportPoints': support_points,
                           'footReceiverSupportPoints': receiver_anchors,
                           'retainedFootBearingCore': side['bearing_core'],
                           'retainedFootRace': f"{side['side']} open stepped bearing race +/-",
                           'retainedShinLoadRails': list(side['load_rails'])})

    assert _pivot_signature() == before_pivots, 'Clevis proposal changed a pivot or parent'
    for name in created:
        obj = bpy.data.objects[name]
        assert obj.type == 'MESH' and len(obj.data.vertices) > 0 and len(obj.data.polygons) > 0
        assert all(math.isfinite(float(c)) for vertex in obj.data.vertices for c in vertex.co)
        assert obj['exteriorEras'] == ERAS and obj['constructionClass'] == 'inherited-passive' and obj['proposal']
    assert len(created) == 4 and len(staged_out) == 2
    return {
        'status': 'in-memory ankle clevis proposal; no visual or mechanical acceptance',
        'createdObjects': created,
        'stagedOutObjects': staged_out,
        'interfaces': interfaces,
        'preservedPivotCount': len(before_pivots),
        'preservedPivotSignatureExact': True,
        'preservedToeSurfaces': ['all meshes parented to left-toes and right-toes are untouched'],
        'allNewMeshesFinite': True,
        'allNewMeshesPassiveInAllEras': True,
        'limits': [
            'The C-cheeks and foot receiver webs are proposals; no collision, bearing-running, foot articulation, or visual acceptance check is performed here.',
            'The 2mm nominal race gap is derived from existing envelope bounds, not a measured tolerance or load-bearing bearing fit.',
            'Anchor points use nearest points on raw source-mesh triangles transformed by matrix_world; modifiers are not evaluated. Root should inspect actual attachment faces and nearby intersections after composition.',
            'No mesh spans the shin/foot articulation; foot receiver moves only with the existing foot pivot.',
        ],
    }
