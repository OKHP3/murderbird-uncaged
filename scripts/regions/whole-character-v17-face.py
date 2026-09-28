"""Replace V16's blank orbital plate with an open passive support assembly.

The lens, bearing, jaw, brow, cheek band and all motion pivots remain source
geometry. Two segmented surrounds replace the broad plates. New races,
support bridges and secondary passive forms follow the existing head pivot.
Measurements are local construction choices, not recovered dimensions.
"""
import math

import bpy
import bmesh
from mathutils import Vector


SIDES = (-1, 1)
SEGMENTS = 64
COLUMNS = 7
SKIN_SIZE = SEGMENTS * COLUMNS
BRIDGE_ANGLES = (0.69, 1.58, 2.40)
SURROUND_ARCS = ((5.50, math.tau + 1.37), (1.45, 4.05))
PASSIVE_FORM_ANGLES = (0.96, 1.19)
RACE_PROFILE = (
    (0.0575, 0.0010),
    (0.0585, 0.0040),
    (0.0605, 0.0060),
    (0.0685, 0.0060),
    (0.0700, 0.0040),
    (0.0710, 0.0010),
)


def _aperture_center(plate):
    pts = [plate.matrix_world @ plate.data.vertices[segment * COLUMNS].co
           for segment in range(SEGMENTS)]
    return Vector((sum(p.y for p in pts) / SEGMENTS,
                   sum(p.z for p in pts) / SEGMENTS))


def _plate_surface_x(plate, side, center, angle, radius, skin=0):
    """Interpolate the outward plate skin in angle and radial station."""
    seg_f = (angle % math.tau) * SEGMENTS / math.tau
    seg0 = int(math.floor(seg_f)) % SEGMENTS
    seg1 = (seg0 + 1) % SEGMENTS
    seg_t = seg_f - math.floor(seg_f)
    matrix = plate.matrix_world

    def sample(segment):
        # Skin zero is the outside face in the authored V16 annulus.
        row = [matrix @ plate.data.vertices[skin * SKIN_SIZE + segment * COLUMNS + station].co
               for station in range(COLUMNS)]
        row_r = [math.hypot(p.y - center.x, p.z - center.y) for p in row]
        assert all(row_r[i + 1] > row_r[i] for i in range(COLUMNS - 1)), (
            f'{plate.name} radial stations are not ordered at segment {segment}')
        for i in range(COLUMNS - 1):
            if row_r[i] <= radius <= row_r[i + 1]:
                t = (radius - row_r[i]) / (row_r[i + 1] - row_r[i])
                return row[i].x * (1 - t) + row[i + 1].x * t
        if radius < row_r[0]:
            return row[0].x
        return row[-1].x

    x0, x1 = sample(seg0), sample(seg1)
    x = x0 * (1 - seg_t) + x1 * seg_t
    return x


def _replace_with_segmented_surround(plate, side, center):
    """Replace the blank annulus with two closed, tapered orbital arc plates."""
    matrix = plate.matrix_world.copy()
    inverse = matrix.inverted()
    vertices = []
    faces = []
    angle_step = math.tau / SEGMENTS
    radial_fractions = (0.0, 0.22, 0.40, 1.0)

    for start, end in SURROUND_ARCS:
        samples = max(12, math.ceil((end - start) / angle_step))
        rows = []
        for i in range(samples):
            angle = start + (i + 0.5) * (end - start) / samples
            outer_radius = _plate_outer_radius(plate, center, angle)
            edge_taper = min((angle - start) / 0.11, (end - angle) / 0.11, 1.0)
            edge_taper = max(0.0, min(1.0, edge_taper))
            edge_taper = edge_taper * edge_taper * (3.0 - 2.0 * edge_taper)
            radial_width = min(0.026, max(0.004, outer_radius - 0.076)) * edge_taper
            inner_radius = outer_radius - radial_width
            front = []
            back = []
            for fraction in radial_fractions:
                radius = inner_radius + radial_width * fraction
                front_x = _plate_surface_x(plate, side, center, angle, radius, 0) + side * (0.001 + 0.004 * math.sin(math.pi * fraction) ** 2)
                back_x = _plate_surface_x(plate, side, center, angle, radius, 1)
                y = center.x + radius * math.cos(angle)
                z = center.y + radius * math.sin(angle)
                front.append((front_x, y, z))
                back.append((back_x, y, z))
            rows.append((front, back))

        base = len(vertices)
        rows_n = len(rows)
        radial_n = len(radial_fractions)
        for skin in (0, 1):
            for front, back in rows:
                vertices.extend(front if skin == 0 else back)

        def idx(skin, angular, radial):
            return base + skin * rows_n * radial_n + angular * radial_n + radial

        for i in range(rows_n - 1):
            for j in range(radial_n - 1):
                faces.append((idx(0, i, j), idx(0, i + 1, j), idx(0, i + 1, j + 1), idx(0, i, j + 1)))
                faces.append((idx(1, i, j + 1), idx(1, i + 1, j + 1), idx(1, i + 1, j), idx(1, i, j)))
            for skin_edge in (0, 1):
                j = 0 if skin_edge == 0 else radial_n - 1
                faces.append((idx(0, i, j), idx(1, i, j), idx(1, i + 1, j), idx(0, i + 1, j)))
        for i in (0, rows_n - 1):
            for j in range(radial_n - 1):
                a, b = idx(0, i, j), idx(0, i, j + 1)
                c, d = idx(1, i, j + 1), idx(1, i, j)
                faces.append((a, b, c, d))

    old_mesh = plate.data
    mesh = bpy.data.meshes.new(plate.name + ' segmented V17 surround')
    mesh.from_pydata([inverse @ Vector(v) for v in vertices], [], faces)
    mesh.update()
    for material in old_mesh.materials:
        if material:
            mesh.materials.append(material)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    plate.data = mesh
    if not old_mesh.users:
        bpy.data.meshes.remove(old_mesh)
    return {'name': plate.name, 'vertices': len(mesh.vertices), 'faces': len(mesh.polygons),
            'closedArcPanels': 2, 'angularSpansRadians': [list(span) for span in SURROUND_ARCS]}


def _plate_outer_radius(plate, center, angle):
    seg_f = (angle % math.tau) * SEGMENTS / math.tau
    seg0 = int(math.floor(seg_f)) % SEGMENTS
    seg1 = (seg0 + 1) % SEGMENTS
    t = seg_f - math.floor(seg_f)
    matrix = plate.matrix_world
    p0 = matrix @ plate.data.vertices[seg0 * COLUMNS + COLUMNS - 1].co
    p1 = matrix @ plate.data.vertices[seg1 * COLUMNS + COLUMNS - 1].co
    r0 = math.hypot(p0.y - center.x, p0.z - center.y)
    r1 = math.hypot(p1.y - center.x, p1.z - center.y)
    return r0 * (1 - t) + r1 * t


def _surround_band(plate, center, angle):
    angle_u = angle if angle >= 5.50 else angle + math.tau if angle < 1.37 else angle
    span = next(((a, b) for a, b in SURROUND_ARCS if a <= angle_u <= b), None)
    if span is None:
        return None
    start, end = span
    taper = min((angle_u - start) / 0.11, (end - angle_u) / 0.11, 1.0)
    taper = max(0.0, min(1.0, taper))
    taper = taper * taper * (3.0 - 2.0 * taper)
    outer = _plate_outer_radius(plate, center, angle)
    width = min(0.026, max(0.004, outer - 0.076)) * taper
    return {'innerRadiusM': outer - width, 'outerRadiusM': outer, 'taper': taper}


def _make_mesh_object(name, world_verts, faces, head, material, role):
    assert bpy.data.objects.get(name) is None, f'Refusing to replace existing object {name}'
    inverse = head.matrix_world.inverted()
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata([inverse @ Vector(p) for p in world_verts], [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = head
    obj.matrix_parent_inverse.identity()
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)
    obj['region'] = 'head'
    obj['surfaceRole'] = role
    obj['exteriorEras'] = 'maker,mechanic,builder'
    obj['constructionClass'] = 'inherited-passive'
    obj['sourceRecipe'] = 'whole-character-v17-face-proposal'
    return obj


def _race_geometry(plate, side, center):
    verts = []
    faces = []
    segments = 96
    for segment in range(segments):
        angle = math.tau * segment / segments
        ydir, zdir = math.cos(angle), math.sin(angle)
        for radius, stand_off in RACE_PROFILE:
            base_x = _plate_surface_x(plate, side, center, angle, radius)
            x = base_x + side * stand_off
            verts.append((x, center.x + radius * ydir, center.y + radius * zdir))
    profile_count = len(RACE_PROFILE)
    for segment in range(segments):
        nxt = (segment + 1) % segments
        for station in range(profile_count):
            next_station = (station + 1) % profile_count
            a = segment * profile_count + station
            b = nxt * profile_count + station
            c = nxt * profile_count + next_station
            d = segment * profile_count + next_station
            faces.append((a, b, c, d))
    return verts, faces


def _bridge_geometry(plate, side, center, angle):
    segment = int(round((angle % math.tau) * SEGMENTS / math.tau)) % SEGMENTS
    outer = plate.matrix_world @ plate.data.vertices[segment * COLUMNS + COLUMNS - 1].co
    outer_radius = math.hypot(outer.y - center.x, outer.z - center.y)
    start_radius = 0.0700
    end_radius = outer_radius - 0.0080
    assert end_radius > start_radius + 0.015, f'No room for orbital bridge at angle {angle}'

    # Tapered forged web, broad at the rim attachment and narrowed as it meets
    # the collar. The lower cheek sector remains intentionally unbridged.
    rows = (
        (start_radius, 0.0042, 0.0055),
        (start_radius + 0.0060, 0.0072, 0.0065),
        (end_radius - 0.0160, 0.0062, 0.0060),
        (end_radius, 0.0048, 0.0045),
    )
    tangent = Vector((-math.sin(angle), math.cos(angle)))
    verts = []
    for radius, half_width, height in rows:
        surface_x = _plate_surface_x(plate, side, center, angle, radius)
        y = center.x + radius * math.cos(angle)
        z = center.y + radius * math.sin(angle)
        # Beveled trapezoid section: bottom embeds slightly into the backing
        # plate and the narrow crown stands proud as a formed structural rib.
        bottom_half = half_width * 1.35
        top_half = half_width * 0.78
        cross_section = (
            (surface_x + side * 0.0005, -bottom_half),
            (surface_x + side * 0.0005, bottom_half),
            (surface_x + side * height, top_half),
            (surface_x + side * height, -top_half),
        )
        for x, offset in cross_section:
            verts.append((x, y + tangent.x * offset, z + tangent.y * offset))

    faces = []
    for row in range(len(rows) - 1):
        for corner in range(4):
            a = row * 4 + corner
            b = row * 4 + (corner + 1) % 4
            faces.append((a, b, b + 4, a + 4))
    faces.extend([tuple(reversed((0, 1, 2, 3))), tuple(12 + i for i in range(4))])
    return verts, faces


def _passive_attachment_geometry(plate, side, center, angle, radius, coin_radius):
    """A blank, stepped passive attachment face; no optical function is implied."""
    segments = 40
    base_x = _plate_surface_x(plate, side, center, angle, radius)
    y0 = center.x + radius * math.cos(angle)
    z0 = center.y + radius * math.sin(angle)
    verts = []
    ring_specs = ((coin_radius, 0.0010), (coin_radius, 0.0040), (coin_radius * 0.72, 0.0060))
    for ring_radius, stand_off in ring_specs:
        for i in range(segments):
            a = math.tau * i / segments
            verts.append((base_x + side * stand_off,
                          y0 + ring_radius * math.cos(a),
                          z0 + ring_radius * math.sin(a)))
    back_center = len(verts)
    verts.append((base_x + side * 0.0010, y0, z0))
    face_center = len(verts)
    verts.append((base_x + side * 0.0060, y0, z0))
    faces = []
    for i in range(segments):
        nxt = (i + 1) % segments
        faces.append((i, nxt, segments + nxt, segments + i))
        faces.append((segments + i, segments + nxt, 2 * segments + nxt, 2 * segments + i))
        faces.append((back_center, nxt, i))
        faces.append((face_center, 2 * segments + i, 2 * segments + nxt))
    return verts, faces


def apply():
    """Replace the blank V16 orbit with an open passive face assembly."""
    head = bpy.data.objects.get('head')
    assert head and head.type == 'EMPTY', 'Expected existing head pivot'
    plate_material = bpy.data.materials.get('Neutral / plate')
    edge_material = bpy.data.materials.get('Neutral / edge')
    assert plate_material and edge_material, 'Expected inherited neutral materials'
    bearing_material = bpy.data.materials.get('Neutral / bearing')
    assert bearing_material, 'Expected inherited neutral bearing material'
    changed = []
    additions = []
    pin_seating = []
    surround_reports = []

    for side in SIDES:
        plate = bpy.data.objects.get(f'Forged orbital mounting plate {side}')
        assert plate and plate.type == 'MESH' and plate.parent == head
        assert len(plate.data.vertices) == 896 and len(plate.data.polygons) == 896
        assert all(len(poly.vertices) == 4 for poly in plate.data.polygons)
        center = _aperture_center(plate)
        race_verts, race_faces = _race_geometry(plate, side, center)
        bridge_records = []
        for number, angle in enumerate(BRIDGE_ANGLES, start=1):
            bridge_verts, bridge_faces = _bridge_geometry(plate, side, center, angle)
            bridge_records.append((number, bridge_verts, bridge_faces))

        passive_records = []
        for number, angle in enumerate(PASSIVE_FORM_ANGLES, start=1):
            outer_radius = _plate_outer_radius(plate, center, angle)
            radius = outer_radius - 0.012
            coin_radius = 0.010 if number == 1 else 0.009
            form_verts, form_faces = _passive_attachment_geometry(
                plate, side, center, angle, radius, coin_radius)
            passive_records.append((number, form_verts, form_faces))

        # The existing fixings remain on retained arc material. Their centers
        # and full radial extents are checked before replacing the backing mesh.
        for pin in sorted((o for o in bpy.data.objects if o.type == 'MESH' and
                           o.name.startswith(f'Orbital mounting fixing {side} ')), key=lambda o: o.name):
            points = [pin.matrix_world @ v.co for v in pin.data.vertices]
            pin_center = sum(points, Vector()) / len(points)
            angle = math.atan2(pin_center.z - center.y, pin_center.y - center.x) % math.tau
            angle_u = angle if angle >= 5.50 else angle + math.tau if angle < 1.37 else angle
            in_arc = any(a <= angle_u <= b for a, b in SURROUND_ARCS)
            band = _surround_band(plate, center, angle)
            assert band, f'No retained surround band under orbital fixing {pin.name}'
            radii = [math.hypot(p.y - center.x, p.z - center.y) for p in points]
            pin_radius = math.hypot(pin_center.y - center.x, pin_center.z - center.y)
            center_supported = band['innerRadiusM'] <= pin_radius <= band['outerRadiusM']
            pin_seating.append({'mesh': pin.name, 'angleRadians': angle,
                                'centerRadiusM': pin_radius, 'vertexRadiusRangeM': [min(radii), max(radii)],
                                'retainedArc': in_arc, 'panelBand': band,
                                'fixingCenterSupportedByArc': center_supported})
            assert in_arc and center_supported, f'Existing orbital fixing lacks retained arc support: {pin.name}'

        surround_reports.append(_replace_with_segmented_surround(plate, side, center))
        changed.append(plate.name)
        race = _make_mesh_object(
            f'Orbital passive retaining race {side}', race_verts, race_faces,
            head, edge_material, 'bearing')
        additions.append(race.name)
        for number, bridge_verts, bridge_faces in bridge_records:
            bridge = _make_mesh_object(
                f'Orbital support bridge {side} {number}', bridge_verts, bridge_faces,
                head, plate_material, 'plate')
            additions.append(bridge.name)
        for number, form_verts, form_faces in passive_records:
            form = _make_mesh_object(
                f'Passive orbital attachment form {side} {number}', form_verts, form_faces,
                head, bearing_material, 'plate')
            form['functionStatus'] = 'passive attachment form; specific function unknown'
            additions.append(form.name)

    bpy.context.view_layer.update()
    return {
        'region': 'head',
        'changed': changed,
        'added': additions,
        'newPivots': [],
        'construction': 'Each blank orbital annulus is replaced by two tapered finite-thickness upper/rear arc panels, leaving an open lower cheek/jaw sector. A compact concentric race and three support bridges per side form the primary optic surround; two round passive attachment forms sit behind/above the main optic.',
        'materials': {'races': edge_material.name, 'bridges': plate_material.name,
                      'secondaryForms': bearing_material.name},
        'eraEligibility': 'All additions are passive and tagged maker,mechanic,builder; secondary round forms have unknown function and are not labeled as sensors.',
        'retainedFixingSeating': pin_seating,
        'segmentedSurrounds': surround_reports,
        'preserved': ['both existing orbital plate object names, owners, material slots and tags; their blank annulus geometry is replaced',
                      'both recessed bearings, housings, optics and advanced-only optic tags',
                      'all existing fixings, brow, cheek, bill and jaw meshes',
                      'all pivots, parent transforms and historical curves'],
        'limits': ['This is a geometric construction proposal; fit, collision, render quality and motion remain for integrated review.',
                   'Support bridges intentionally overlap retained orbital arc panels and the race; their contact is not physically validated.',
                   'Secondary round forms are visual reconstructions with unknown function.']
    }
