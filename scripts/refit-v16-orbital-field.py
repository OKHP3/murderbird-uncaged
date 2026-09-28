"""Refit the V16 blank orbital field around its unchanged circular optic seat.

Call apply() after the V16 whole-silhouette composition has mapped the meshes
and before saving. This is one rest-geometry proposal, not a final surface,
clearance, era-material, or likeness acceptance.
"""
import math
import bpy
from mathutils import Vector

SEGMENTS = 64
COLUMNS = 7
SKIN_VERTICES = SEGMENTS * COLUMNS
PLATE_NAMES = ('Forged orbital mounting plate -1', 'Forged orbital mounting plate 1')


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _angular_distance(a, b):
    return abs((a - b + math.pi) % math.tau - math.pi)


def _edge_scale(angle):
    # Keep the forehead/rear return broad enough to sit under the existing
    # brow, while opening the lower-front cheek sector toward its machinery.
    lower_front = math.exp(-0.5 * (_angular_distance(angle, 4.48) / 0.72) ** 2)
    return 0.74 - 0.20 * lower_front


def _optic_center_yz(plate):
    # The innermost authored loop is the actual aperture contour. Its mean is
    # retained as the invariant center for the circular bearing/optic seat.
    pts = [plate.matrix_world @ plate.data.vertices[k * COLUMNS].co for k in range(SEGMENTS)]
    return Vector((sum(p.y for p in pts) / SEGMENTS, sum(p.z for p in pts) / SEGMENTS))


def _visible_side_skin(side):
    # The two skins are offset across X; choose the outward skin for pin seating.
    return 0 if side < 0 else 1


def _move_mesh_translation(obj, delta):
    inverse = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        vertex.co = inverse @ (world + delta)
    obj.data.update()


def apply():
    """Narrow the existing annular plates and move their existing rim fixings."""
    edited_plates = []
    fixing_edits = []
    for side in (-1, 1):
        plate = bpy.data.objects.get(f'Forged orbital mounting plate {side}')
        assert plate and plate.type == 'MESH' and plate.parent and plate.parent.name == 'head'
        assert len(plate.data.vertices) == 2 * SKIN_VERTICES and len(plate.data.polygons) == 896
        assert all(len(poly.vertices) == 4 for poly in plate.data.polygons), 'Expected intact quad-strip annulus'
        matrix = plate.matrix_world.copy()
        center_yz = _optic_center_yz(plate)
        center_x = sum((matrix @ plate.data.vertices[k * COLUMNS].co).x for k in range(SEGMENTS)) / SEGMENTS

        # Freeze each fixing's original stand-off from the visible outer rim;
        # after reprofiling, retain that offset at the new corresponding edge.
        fixings = sorted((o for o in bpy.data.objects if o.type == 'MESH' and
                          o.name.startswith(f'Orbital mounting fixing {side} ')), key=lambda o: o.name)
        assert len(fixings) == 5, f'Expected five inherited orbital fixings for side {side}'
        pin_records = []
        outward_skin = _visible_side_skin(side)
        for fixing in fixings:
            old_points = [fixing.matrix_world @ v.co for v in fixing.data.vertices]
            old_center = sum(old_points, Vector()) / len(old_points)
            angle = math.atan2(old_center.z - center_yz.y, old_center.y - center_yz.x) % math.tau
            segment = int(round(angle / math.tau * SEGMENTS)) % SEGMENTS
            rim_index = outward_skin * SKIN_VERTICES + segment * COLUMNS + (COLUMNS - 1)
            old_rim = matrix @ plate.data.vertices[rim_index].co
            pin_records.append((fixing, angle, old_rim.copy()))

        original = [plate.matrix_world @ v.co for v in plate.data.vertices]
        original_radii = {}
        for segment in range(SEGMENTS):
            samples = []
            for station in range(COLUMNS):
                point = original[segment * COLUMNS + station]
                samples.append(math.hypot(point.y - center_yz.x, point.z - center_yz.y))
            original_radii[segment] = samples
        max_delta = 0.0
        for index, vertex in enumerate(plate.data.vertices):
            skin = index // SKIN_VERTICES
            within_skin = index % SKIN_VERTICES
            segment = within_skin // COLUMNS
            station = within_skin % COLUMNS
            if station < 2:
                continue  # aperture and first seat land remain bit-for-bit fixed
            angle = math.tau * segment / SEGMENTS
            t = _smooth((station - 1.0) / (COLUMNS - 2.0))
            radii = original_radii[segment]
            outer_radius = radii[1] + (radii[-1] - radii[1]) * _edge_scale(angle)
            target_radius = radii[1] + (outer_radius - radii[1]) * t
            point = original[index].copy()
            original_radius = math.hypot(point.y - center_yz.x, point.z - center_yz.y)
            radial_scale = target_radius / original_radius
            point.y = center_yz.x + (point.y - center_yz.x) * radial_scale
            point.z = center_yz.y + (point.z - center_yz.y) * radial_scale
            max_delta = max(max_delta, (point - original[index]).length)
            vertex.co = matrix.inverted() @ point
        plate.data.update()

        for fixing, angle, old_rim in pin_records:
            segment = int(round(angle / math.tau * SEGMENTS)) % SEGMENTS
            rim_index = outward_skin * SKIN_VERTICES + segment * COLUMNS + (COLUMNS - 1)
            new_rim = matrix @ plate.data.vertices[rim_index].co
            delta = new_rim - old_rim
            _move_mesh_translation(fixing, delta)
            fixing_edits.append({'mesh': fixing.name, 'angleRadians': angle,
                                 'translationWorld': list(delta),
                                 'retainedShapeAndOwner': True})
        edited_plates.append({'mesh': plate.name, 'vertices': len(plate.data.vertices),
            'topology': 'preserved 64-segment x 7-station closed quad annulus, two skins',
            'unchangedStations': [0, 1], 'maximumVertexDisplacementM': max_delta,
            'edgeScaleRange': [0.54, 0.74],
            'radialConstruction': 'Stations 2-6 interpolate monotonically from the unchanged station 1 radius to a contracted outer radius; X separation of the two skins is preserved.'})

    bpy.context.view_layer.update()
    return {
        'region': 'orbital-field-refit',
        'changedMeshes': sorted(PLATE_NAMES + tuple(o['mesh'] for o in fixing_edits)),
        'newMeshes': [],
        'method': 'Reprofile only the existing outer orbital-plate stations in YZ around the unchanged aperture loops; taper lower-front sector further to reveal existing cheek machinery; translate existing rim fixings to the new edge while retaining their geometry.',
        'editedPlates': edited_plates,
        'movedExistingFixings': fixing_edits,
        'preserved': ['optic-bearing aperture and inner two stations', 'optic and housing meshes',
                      'brow and cheek-band meshes', 'object names, owners, materials and era tags',
                      'all pivots, parent links, and historical curves'],
        'limits': ['Outer profile factors are qualitative construction choices, not recovered source dimensions.',
                   'No render, surface fit, collision, or motion validation is performed by this module.'],
    }
