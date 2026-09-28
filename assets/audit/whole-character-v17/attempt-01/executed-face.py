"""Add a compact passive orbital support assembly to a loaded V16 scene.

The lens, bearing, jaw, brow, cheek band and all motion pivots remain source
geometry. New meshes are one concentric retaining race and three formed
support bridges per side, all rigidly owned by the existing head pivot.
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
RACE_PROFILE = (
    (0.0575, 0.0010),
    (0.0585, 0.0040),
    (0.0605, 0.0060),
    (0.0685, 0.0060),
    (0.0700, 0.0040),
    (0.0710, 0.0010),
)


def _world_vertices(obj):
    return [obj.matrix_world @ vert.co for vert in obj.data.vertices]


def _aperture_center(plate):
    pts = [plate.matrix_world @ plate.data.vertices[segment * COLUMNS].co
           for segment in range(SEGMENTS)]
    return Vector((sum(p.y for p in pts) / SEGMENTS,
                   sum(p.z for p in pts) / SEGMENTS))


def _plate_surface_x(plate, side, center, angle, radius):
    """Interpolate the outward plate skin in angle and radial station."""
    seg_f = (angle % math.tau) * SEGMENTS / math.tau
    seg0 = int(math.floor(seg_f)) % SEGMENTS
    seg1 = (seg0 + 1) % SEGMENTS
    seg_t = seg_f - math.floor(seg_f)
    matrix = plate.matrix_world

    def sample(segment):
        # Skin zero is the outside face in the authored V16 annulus.
        row = [matrix @ plate.data.vertices[segment * COLUMNS + station].co
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


def apply():
    """Add passive orbital retention and support geometry to a loaded V16 scene."""
    head = bpy.data.objects.get('head')
    assert head and head.type == 'EMPTY', 'Expected existing head pivot'
    plate_material = bpy.data.materials.get('Neutral / plate')
    edge_material = bpy.data.materials.get('Neutral / edge')
    assert plate_material and edge_material, 'Expected inherited neutral materials'
    changed = []
    additions = []

    for side in SIDES:
        plate = bpy.data.objects.get(f'Forged orbital mounting plate {side}')
        assert plate and plate.type == 'MESH' and plate.parent == head
        assert len(plate.data.vertices) == 896 and len(plate.data.polygons) == 896
        assert all(len(poly.vertices) == 4 for poly in plate.data.polygons)
        center = _aperture_center(plate)
        race_verts, race_faces = _race_geometry(plate, side, center)
        race = _make_mesh_object(
            f'Orbital passive retaining race {side}', race_verts, race_faces,
            head, edge_material, 'bearing')
        additions.append(race.name)

        for number, angle in enumerate(BRIDGE_ANGLES, start=1):
            bridge_verts, bridge_faces = _bridge_geometry(plate, side, center, angle)
            bridge = _make_mesh_object(
                f'Orbital support bridge {side} {number}', bridge_verts, bridge_faces,
                head, plate_material, 'plate')
            additions.append(bridge.name)

    bpy.context.view_layer.update()
    return {
        'region': 'head',
        'changed': changed,
        'added': additions,
        'newPivots': [],
        'construction': 'One passive concentric retaining race and three tapered radial support bridges per orbital side. Bridges terminate near existing orbital rim fixings; the lower cheek/jaw sector stays open.',
        'materials': {'race': edge_material.name, 'bridges': plate_material.name},
        'eraEligibility': 'All additions are passive and tagged maker,mechanic,builder; no advanced-only sensor was added.',
        'preserved': ['both existing orbital plates and their geometry',
                      'both recessed bearings, housings, optics and advanced-only optic tags',
                      'all existing fixings, brow, cheek, bill and jaw meshes',
                      'all pivots, parent transforms and historical curves'],
        'limits': ['This is a geometric construction proposal; fit, collision, render quality and motion remain for integrated review.',
                   'New parts intentionally overlap the backing orbital plate and are not claimed to be physically validated.']
    }
