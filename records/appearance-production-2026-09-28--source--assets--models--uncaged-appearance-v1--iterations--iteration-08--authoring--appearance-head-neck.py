"""Fitted head and cervical exterior replacement for alignment-v3.

Authored dimensions are visual reconstructions in metres (X lateral, -Y
forward, Z up). It replaces named exterior plates and adds fitted meshes; it
does not change the rig, pivots, bill contact geometry, or internal systems.
"""


def build(ctx):
    bpy = ctx['bpy']
    Vector = ctx['Vector']
    math = ctx['math']
    mat = ctx['mat']
    patch = ctx['patch']
    wm = ctx['wm']
    wr = ctx['wr']
    wt = ctx['wt']
    fastener = ctx['fastener']
    sample = ctx['sample']
    envelope = ctx['envelope']
    smooth_profile = ctx['smooth_profile']
    ALL = 'maker,mechanic,builder'

    head = bpy.data.objects['head']
    crown = bpy.data.objects['cranial-cover']
    neck = bpy.data.objects['neck']
    builder_optics = bpy.data.objects['builder-optics']
    bill = bpy.data.objects['upper-bill']
    jaw = bpy.data.objects['jaw']
    counts = {'head': 0, 'optic': 0, 'neck': 0}
    removed = []

    # Remove only the explicitly superseded exterior surfaces from the
    # in-memory alignment-v3 scene. Functional groups and internal assemblies
    # are not meshes with these names and are never touched.
    superseded_prefixes = (
        'Broad swept crown roof', 'Temporal swept blade',
        'Segmented supraorbital brow', 'Continuous temporal cheek arch',
        'Descending fixed cheek arm', 'Inset passive optic housing',
        'Recessed optic lip', 'Seated Advanced optic',
        'Central cervical shield', 'Lateral cervical guard',
        'Cervical side transition', 'Cervical rear quarter guard',
        'Profiled cranial backing', 'Temporal shaped backing',
        'Crown cap fixing', 'Temporal blade root pin',
    )
    for obj in list(bpy.data.objects):
        if (obj.type == 'MESH' and
                any(obj.name.startswith(prefix) for prefix in superseded_prefixes)):
            removed.append(obj.name)
            bpy.data.objects.remove(obj, do_unlink=True)

    def add(obj, region):
        counts[region] += 1
        return obj

    def fitted_patch(name, outline, project, parent, reg, role='plate',
                     thickness=.006, eras=ALL, sub=6):
        """Keep the curved face smooth; never bevel its tessellation edges.

        The shared helper uses angle-limited beveling (30 degrees by
        default), not an unrestricted bevel. On curved triangulated sheets,
        steep local tessellation edges may still qualify. Removing those
        modifiers here keeps curved face normals independent of edge finish;
        the Solidify wall supplies the small, crisp perimeter highlight.
        """
        obj = patch(name, outline, project, parent, reg, role,
                    thickness=thickness, eras=eras, sub=sub)
        for modifier in list(obj.modifiers):
            if modifier.type in {'BEVEL', 'WEIGHTED_NORMAL'}:
                obj.modifiers.remove(modifier)
        # YZ outlines project with opposite winding on the two head sides.
        # Give Solidify consistent outward normals before it makes inner walls.
        transform = parent.matrix_world
        rotation = transform.to_3x3()
        for face in obj.data.polygons:
            center = transform @ face.center
            normal = rotation @ face.normal
            if reg == 'neck':
                cy, _, _ = sample(cervical, center.z)
                outward = Vector((center.x, center.y - cy, 0))
            elif name.startswith('Rear cranial'):
                cy, _, _ = sample(skull, center.z)
                outward = Vector((center.x, center.y - cy, 0))
            else:
                outward = Vector((1 if center.x >= 0 else -1, 0, 0))
            if normal.dot(outward) < 0:
                face.flip()
            face.use_smooth = True
        obj.data.update()
        return obj

    def annular(name, x0, x1, outer_radius, inner_radius, parent, reg, role,
                eras=ALL, segments=48):
        """A true hollow, axially extruded ring around the lateral X axis."""
        vertices = []
        # Back/front outer loops, then front/back inner loops.
        for x, radius in [(x0, outer_radius), (x1, outer_radius),
                          (x1, inner_radius), (x0, inner_radius)]:
            for i in range(segments):
                angle = math.tau * i / segments
                vertices.append((x, eye_y + radius * math.cos(angle),
                                 eye_z + radius * math.sin(angle)))
        faces = []
        for layer in range(4):
            next_layer = (layer + 1) % 4
            for i in range(segments):
                j = (i + 1) % segments
                face = (layer * segments + i, layer * segments + j,
                        next_layer * segments + j, next_layer * segments + i)
                faces.append(tuple(reversed(face)) if x1 < x0 else face)
        return wm(name, vertices, faces, parent, reg, role, eras)

    def oval_collar(name, side, parent):
        vertices = []
        loops = [
            (side * .143, .066, .062), (side * .149, .066, .062),
            (side * .149, .059, .052), (side * .143, .059, .052),
        ]
        for x, ry, rz in loops:
            for i in range(64):
                angle = math.tau * i / 64
                vertices.append((x, eye_y + ry * math.cos(angle),
                                 eye_z + rz * math.sin(angle)))
        faces = []
        for layer in range(4):
            next_layer = (layer + 1) % 4
            for i in range(64):
                j = (i + 1) % 64
                face = (layer * 64 + i, layer * 64 + j,
                        next_layer * 64 + j, next_layer * 64 + i)
                faces.append(tuple(reversed(face)) if side < 0 else face)
        obj = wm(name, vertices, faces, parent, 'head', 'bearing', ALL)
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
        return obj

    # Alignment-v3 authored head envelope; it follows the retained skull and
    # keeps the July reference scoped to head identity alone.
    skull = [
        (1.575, -.15, .065, .10), (1.65, -.20, .123, .185),
        (1.74, -.25, .149, .22), (1.825, -.265, .153, .20),
        (1.915, -.24, .119, .175), (1.955, -.17, .025, .075),
    ]
    eye_y, eye_z = -.369, 1.786
    optic_clear_radius = .060

    def disc_intersects_polygon(points, radius=optic_clear_radius):
        """Return true when any point or edge enters the optic clear circle."""
        center = (eye_y, eye_z)
        inside = False
        for i, (x1, y1) in enumerate(points):
            x2, y2 = points[(i + 1) % len(points)]
            if ((y1 > center[1]) != (y2 > center[1]) and
                    center[0] < (x2 - x1) * (center[1] - y1) /
                    ((y2 - y1) or 1e-12) + x1):
                inside = not inside
            dx, dy = x2 - x1, y2 - y1
            denom = dx * dx + dy * dy
            t = 0 if denom == 0 else max(0, min(1,
                ((center[0] - x1) * dx + (center[1] - y1) * dy) / denom))
            px, py = x1 + t * dx, y1 + t * dy
            if (px - center[0]) ** 2 + (py - center[1]) ** 2 < radius ** 2:
                return True
        return inside

    # A formed inner cheek wall closes the unintended view-through behind the
    # cheek, while the separate perimeter defines the retained open mouth.
    backing = [
        (-.455, 1.758), (-.438, 1.789), (-.405, 1.785),
        (-.378, 1.757), (-.356, 1.715), (-.337, 1.669),
        (-.365, 1.638), (-.410, 1.648), (-.443, 1.692),
    ]
    for side in (-1, 1):
        # Recessed temporal backing replaces the old incompatible side shell.
        # Its front edge is behind the optic aperture; the upper edge sits
        # beneath the new scalp's lateral skirt.
        temporal_backing = [
            (-.300, 1.861), (-.265, 1.889), (-.182, 1.883),
            (-.095, 1.841), (-.023, 1.788), (.008, 1.731),
            (-.039, 1.654), (-.108, 1.607), (-.179, 1.618),
            (-.250, 1.687), (-.287, 1.762),
        ]
        def temporal_back_project(y, z, s=side):
            cy, rx, ry = sample(skull, z)
            q = (y - cy) / ry
            return (s * (rx * math.sqrt(max(.04, 1 - q*q)) - .003), y, z)
        add(fitted_patch(f'Continuous fitted temporal shadow shell {side}',
                         smooth_profile(temporal_backing, 3),
                         temporal_back_project, crown, 'head', 'recess',
                         thickness=.005, eras=ALL, sub=5), 'head')

        # Backing is deliberately recessed; the open jaw/throat remains visible.
        add(fitted_patch(
            f'Formed dark cheek backing {side}', backing,
            lambda y, z, s=side: (s * (.091 + .012 * max(0, z - 1.68)), y, z),
            head, 'head', 'inner', thickness=.009, eras=ALL, sub=5,
        ), 'head')

        # A formed annular orbital collar replaces the paddle and stays joined
        # to the cheek shell around the clear aperture.
        add(oval_collar('Formed orbital cheek collar', side, head), 'head')

        # A curved mounting cheek seats the socket rim into the skull instead
        # of leaving a complete disk perched beyond a thin oval collar. Its
        # real aperture is larger than the active lens and its inner retainer, and remains clear
        # through the entire thickness. Both sides have outward face winding.
        vertices, faces = [], []
        radial_steps, segments = 6, 64
        def mounting_point(angle, t, outward=0):
            dy, dz = math.cos(angle), math.sin(angle)
            outer_y = .094
            outer_z = .082 if dz > 0 else .093
            # This 46 mm clear opening masks the oversized passive washer,
            # while remaining comfortably outside the 20 mm ray samples.
            y = eye_y + dy*(.046 + (outer_y - .046)*t)
            z = eye_z + dz*(.046 + (outer_z - .046)*t)
            cy, rx, ry = sample(skull, z)
            q = (y - cy)/ry
            skull_x = max(.107, rx*math.sqrt(max(.04, 1 - q*q)) + .010)
            # Raised formed socket edge, with the lens seated 6 mm inside.
            x = .171*(1 - t) + (skull_x - .001)*t + outward
            return (side*x, y, z)
        for radial in range(radial_steps + 1):
            for index in range(segments):
                vertices.append(mounting_point(math.tau*index/segments,
                                               radial/radial_steps))
        for radial in range(radial_steps):
            for index in range(segments):
                nxt = (index + 1) % segments
                k, n = radial*segments + index, radial*segments + nxt
                face = (k, k + segments, n + segments, n)
                faces.append(face if side > 0 else tuple(reversed(face)))
        # Extrude along X explicitly: normal-offset Solidify would narrow
        # the aperture where this sloped face meets the inner boundary.
        front_count = len(vertices)
        front_faces = list(faces)
        vertices += [(x - side*.005, y, z) for x, y, z in vertices]
        faces += [tuple(front_count + index for index in reversed(face))
                  for face in front_faces]
        for radial in (0, radial_steps):
            for index in range(segments):
                nxt = (index + 1) % segments
                k, n = radial*segments + index, radial*segments + nxt
                rim = ((k, n, n + front_count, k + front_count)
                       if radial == 0 else
                       (k, k + front_count, n + front_count, n))
                faces.append(rim if side > 0 else tuple(reversed(rim)))
        mount = add(wm(f'Fitted orbital mounting cheek {side}', vertices,
                       faces, head, 'head', 'plate', ALL), 'head')
        for face in mount.data.polygons:
            face.use_smooth = face.index < 2*len(front_faces)

        # Small fabrication details are attached to this cheek's own formed
        # surface. None crosses the socket opening or changes the mouth edge.
        for index, angle in enumerate((.48, 2.51, 4.57)):
            p = mounting_point(angle, .76)
            add(fastener(f'Cheek recessed panel fixing {side} {index}', p,
                         (side, 0, 0), head, 'head', .0024, eras=ALL), 'head')
        for index, angles in enumerate(((.86, 1.02, 1.18),
                                        (3.63, 3.80, 3.97))):
            points = [mounting_point(angle, .80, .0004) for angle in angles]
            add(wt(f'Cheek fitted fabrication seam {side} {index}', points,
                   [.0006, .0008, .0006], head, 'head', 'recess',
                   eras=ALL, sides=8), 'head')

        # Passive socket is dark in Maker and Mechanic. The well is a recessed
        # dark cylinder; all surrounding rings are annular, leaving the center
        # open for depth and the era-specific Advanced lens.
        add(wr('Passive recessed optic well', (side * 0.1250, eye_y, eye_z),
               (side * 0.1350, eye_y, eye_z), .037, head, 'optic', 'recess',
               eras=ALL, sides=40), 'optic')
        for outer, inner, x0, x1, role, label in [
            (.060, .052, .135, .143, 'bearing', 'Outer optic seat'),
            (.053, .045, .144, .152, 'edge', 'Inner optic lip'),
            (.046, .038, .153, .160, 'bearing', 'Lens retaining ring'),
        ]:
            a, b = (side * x0, side * x1)
            add(annular(label, a, b, outer, inner,
                        head, 'optic', role, ALL), 'optic')
        # The lens is nested inside the retaining ring with visible depth. It
        # remains a child of the existing Advanced optics owner for inspection.
        add(wr('Advanced optic dark glass well', (side * 0.1250, eye_y, eye_z),
               (side * 0.1460, eye_y, eye_z), .037, builder_optics, 'optic',
               'inner', eras='builder', sides=40), 'optic')
        add(wr('Advanced seated amber lens', (side * 0.1450, eye_y, eye_z),
               (side * 0.1590, eye_y, eye_z), .035, builder_optics, 'optic',
               'optic', eras='builder', sides=40), 'optic')
        add(annular('Advanced amber lens bezel', side * 0.1570,
                    side * 0.1650, .040, .035, builder_optics,
                    'optic', 'edge', 'builder'), 'optic')
        add(wr('Advanced amber lens inner', (side * 0.1590, eye_y, eye_z),
               (side * 0.1650, eye_y, eye_z), .012, builder_optics, 'optic',
               'optic', eras='builder', sides=40), 'optic')

        # The iris is itself a lens surface (and therefore participates in
        # the optic ray test), with a restrained dark finish assigned by the
        # material module. A small amber center replaces the broad coin face.
        iris = add(annular('Advanced dark iris lens', side * 0.1600,
                           side * 0.1640, .033, .013, builder_optics,
                           'optic', 'optic', 'builder', segments=64), 'optic')
        iris['appearanceOpticSurface'] = 'dark-iris'
        for radius in (.0265, .0305):
            add(annular('Advanced fine concentric lens bezel', side * 0.1635,
                        side * 0.1650, radius + .00065, radius,
                        builder_optics, 'optic', 'edge', 'builder',
                        segments=64), 'optic')

        # One fitted brow band replaces the three floating paddles. Its
        # lower boundary sits above the optic clear circle; the side crown
        # surface below is continuous with the roof rather than planar at X.
        brow = [(-.447, 1.853), (-.408, 1.889), (-.351, 1.912),
                (-.292, 1.919), (-.241, 1.906), (-.264, 1.887),
                (-.329, 1.891), (-.385, 1.873), (-.419, 1.848)]
        def brow_project(y, z, s=side):
            cy, rx, ry = sample(skull, z)
            q = (y - cy) / ry
            return (s * (rx * math.sqrt(max(.04, 1 - q * q)) + .011), y, z)
        brow_outline = smooth_profile(brow, 3)
        assert not disc_intersects_polygon(brow_outline)
        add(fitted_patch(f'Fitted supraorbital band {side}', brow_outline,
                         brow_project, crown, 'head', 'plate',
                         thickness=.005, eras=ALL, sub=5), 'head')

        # Temporal scutes sweep back from the cheek instead of forming uniform
        # vertical tiles. Each course changes length and terminates in a taper.
        temporal_courses = [
            (1.856, [(-.251, .083), (-.180, .090), (-.109, .077)], .007),
            (1.781, [(-.282, .091), (-.208, .103), (-.134, .088)], .007),
            (1.703, [(-.297, .084), (-.224, .096), (-.151, .078)], .007),
            (1.630, [(-.277, .063), (-.209, .071)], .006),
        ]
        for row, (z, cells, lift) in enumerate(temporal_courses):
            for col, (y, length) in enumerate(cells):
                outline = [
                    (y - .031, z), (y + .030, z),
                    (y + .038, z - .024), (y + .048, z - length * .73),
                    (y + .019, z - length), (y - .027, z - .054),
                ]
                smoothed_outline = smooth_profile(outline, 3)
                if disc_intersects_polygon(smoothed_outline):
                    continue

                yc = y + .018
                zc = z - length * .49

                def side_profile(yy, zz, s=side, relief=lift,
                                 center_y=yc, center_z=zc, half_y=.065,
                                 half_z=length * .56, root_z=z, plate_length=length):
                    cy, rx, ry = sample(skull, zz)
                    q = (yy - cy) / max(.05, ry)
                    u = (yy - center_y) / half_y
                    v = (zz - center_z) / max(.025, half_z)
                    dome = .005 * max(0, 1 - u * u - v * v)
                    lap = .011 * max(0, min(1, (root_z - zz) / plate_length))
                    x = rx * math.sqrt(max(.04, 1 - q * q)) + relief + lap + dome
                    return (s * x, yy, zz)

                add(fitted_patch(
                    f'Swept temporal scute {side} {row} {col}',
                    smoothed_outline, side_profile,
                    crown, 'head', 'plate', thickness=.005,
                    eras=ALL, sub=3,
                ), 'head')
                add(wt(
                    f'Temporal scute warm edge {side} {row} {col}',
                    [side_profile(y + .038, z - .024),
                     side_profile(y + .048, z - length * .73),
                     side_profile(y + .019, z - length)],
                    [.0015, .0018, .0008], crown, 'head', 'edge', eras=ALL,
                    sides=8,
                ), 'head')

    # One smooth manufactured scalp surface, sampled as a regular quad grid.
    # Width/height/depth share the same envelope for backing and every cap;
    # no piecewise planar fans or mismatched historic shells remain beneath it.
    roof = [(-.454, 1.860, .067, .042), (-.370, 1.931, .127, .086),
            (-.272, 1.965, .150, .109), (-.161, 1.960, .143, .117),
            (-.049, 1.914, .102, .109), (.015, 1.852, .044, .079)]

    def roof_section(y):
        y = max(roof[0][0], min(roof[-1][0], y))
        for i in range(len(roof) - 1):
            a, b = roof[i], roof[i + 1]
            if a[0] <= y <= b[0]:
                distance = b[0] - a[0]
                t = (y - a[0]) / distance
                values = []
                for axis in (1, 2, 3):
                    slopes = [(right[axis] - left[axis]) /
                              (right[0] - left[0])
                              for left, right in zip(roof, roof[1:])]
                    def tangent(index):
                        if index == 0:
                            return slopes[0]
                        if index == len(roof) - 1:
                            return slopes[-1]
                        left, right = slopes[index - 1], slopes[index]
                        return 0 if left * right <= 0 else 2 * left * right / (left + right)
                    m0, m1 = tangent(i), tangent(i + 1)
                    values.append((2*t**3 - 3*t*t + 1)*a[axis] +
                                  (t**3 - 2*t*t + t)*distance*m0 +
                                  (-2*t**3 + 3*t*t)*b[axis] +
                                  (t**3 - t*t)*distance*m1)
                return values
        return roof[-1][1:]

    def scalp_point(y, angle, lift=0):
        crest, width, depth = roof_section(y)
        return (math.sin(angle)*(width + lift), y,
                crest - depth*(1 - math.cos(angle)) + lift*math.cos(angle))

    def scalp_grid(name, y0, y1, a0, a1, role, course=False,
                   rows=16, columns=14):
        vertices, faces = [], []
        for row in range(rows + 1):
            v = row / rows
            for col in range(columns + 1):
                u = col / columns
                # Narrow roots and a tapered, rounded trailing tip make each
                # cap a small swept scale while retaining regular quad rows.
                taper = 1 - .60*max(0, (v - .48)/.52)**1.4 if course else 1
                direction = 1 if a0 + a1 >= 0 else -1
                lateral_sweep = direction*.070*v*v if course else 0
                angle = (a0 + a1)/2 + (a1 - a0)*(u - .5)*taper + lateral_sweep
                sweep = (.009*math.sin(math.pi*u)**2 -
                         direction*.006*(2*u - 1)) if course else 0
                y = y0 + (y1 - y0)*v + sweep*v**3
                # Front roots are recessed beneath the preceding free edge.
                lift = .005 + .012*v*v if course else -.001
                vertices.append(scalp_point(y, angle, lift))
        stride = columns + 1
        for row in range(rows):
            for col in range(columns):
                k = row*stride + col
                faces.append((k, k + 1, k + stride + 1, k + stride))
        obj = add(wm(name, vertices, faces, crown, 'head', role, ALL), 'head')
        for face in obj.data.polygons:
            face.use_smooth = True
        wall = obj.modifiers.new('Fitted scalp wall', 'SOLIDIFY')
        wall.thickness = .0045 if course else .005
        wall.offset = -1
        return obj

    scalp_grid('Continuous fitted cranial shadow shell', -.454, .015,
               -math.pi/2, math.pi/2, 'recess', rows=48, columns=36)
    for row in range(7):
        course_root = -.451 + .064*row
        for lane in range(5):
            root_lag = [.006, .011, .001, .008, .003][(lane + row) % 5]
            y0 = course_root + root_lag
            span = (.067 if row == 6 else .085) + [.002, -.003, .004, 0, -.002][(2*lane + row) % 5]
            y1 = min(.006, y0 + span)
            stagger = .065 if row % 2 else -.025
            a0 = -1.55 + .62*lane + (stagger if lane else 0) + .010
            a1 = -1.55 + .62*(lane + 1) + (stagger if lane < 4 else 0) - .010
            scalp_grid(f'Formed swept crown scale {row} {lane}', y0, y1,
                       a0, a1, 'plate', course=True, rows=14, columns=10)

    # Rear center casing closes the strip between independently authored
    # side temporal courses. It shares their skull envelope and crown owner;
    # it ends above the neck and never bridges those moving assemblies.
    vertices, faces = [], []
    rows, columns = 24, 20
    for row in range(rows + 1):
        z = 1.616 + (1.885 - 1.616)*row/rows
        for col in range(columns + 1):
            angle = 2.52 + 1.243*col/columns
            vertices.append(envelope(skull, z, angle, -.001))
    stride = columns + 1
    for row in range(rows):
        for col in range(columns):
            k = row*stride + col
            faces.append((k, k + 1, k + stride + 1, k + stride))
    rear_shell = add(wm('Rear cranial fitted center backing', vertices,
                        faces, crown, 'head', 'recess', ALL), 'head')
    for face in rear_shell.data.polygons:
        face.use_smooth = True
    wall = rear_shell.modifiers.new('Rear cranial backing wall', 'SOLIDIFY')
    wall.thickness, wall.offset = .004, -1
    for row, (top, length) in enumerate([
        (1.879, .095), (1.807, .098), (1.733, .101), (1.659, .046),
    ]):
        center_angle = math.pi + (.025 if row % 2 else -.025)
        width = .56 if row < 2 else .49
        outline = [
            (center_angle - width, top), (center_angle + width, top),
            (center_angle + width*.92, top - length*.45),
            (center_angle + .07, top - length),
            (center_angle - width*.83, top - length*.73),
        ]
        project = lambda a, z, root=top, span=length: envelope(
            skull, z, a, .007 + .010*max(0, min(1, (root - z)/span))
        )
        add(fitted_patch(f'Rear cranial swept center scale {row}',
                         smooth_profile(outline, 2), project, crown,
                         'head', 'plate', thickness=.005, eras=ALL,
                         sub=5), 'head')

    # Restrained pins sit only at roots and plate junctions, not as random
    # surface noise. Passive construction is shared; replacement hardware is
    # reserved for Mechanic and Advanced.
    for side in (-1, 1):
        for y, z in [(-.329, 1.849), (-.251, 1.846), (-.367, 1.708)]:
            cy, rx, ry = sample(skull, z)
            q = (y - cy) / max(.05, ry)
            p = (side * (rx * math.sqrt(max(.12, 1 - q * q)) + .019), y, z)
            add(fastener('Temporal plate root pin', p, (side, 0, .12), crown,
                         'head', .0028, eras=ALL), 'head')
        add(wr('Mechanic cheek repair seam', (side * .145, -.410, 1.744),
               (side * .145, -.365, 1.704), .0022, head, 'head', 'repair',
               eras='mechanic,builder', sides=8), 'head')

    # Fine fitted seams make the retained upper bill read as assembled armor
    # without changing its silhouette or the preserved contact outline.
    bill_outer = [(-.421, 1.853), (-.493, 1.837), (-.571, 1.789),
                  (-.638, 1.716), (-.674, 1.634), (-.678, 1.560),
                  (-.657, 1.495), (-.622, 1.463)]
    bill_inner = [(-.420, 1.706), (-.482, 1.694), (-.538, 1.674),
                  (-.585, 1.643), (-.620, 1.602), (-.641, 1.554),
                  (-.642, 1.503), (-.622, 1.463)]
    bill_widths = [.071, .075, .067, .052, .037, .022, .010, .0008]

    def profile_at(points, t):
        position = max(0, min(len(points) - 1.000001, t * (len(points) - 1)))
        index = int(position)
        fraction = position - index
        return (points[index][0] + (points[index + 1][0] - points[index][0]) * fraction,
                points[index][1] + (points[index + 1][1] - points[index][1]) * fraction)

    def bill_seam_point(t, side, cross):
        oy, oz = profile_at(bill_outer, t)
        iy, iz = profile_at(bill_inner, t)
        width = profile_at([(i, value) for i, value in
                            enumerate(bill_widths)], t)[1]
        y = (oy + iy) / 2 + (oy - iy) / 2 * cross
        z = (oz + iz) / 2 + (oz - iz) / 2 * cross
        return (side * width * .84, y, z)

    for side in (-1, 1):
        for seam_index, cross in enumerate((.44, -.34)):
            points = [bill_seam_point(t, side, cross)
                      for t in (.14, .25, .37, .49, .61, .73, .82)]
            add(wt(f'Forged bill panel seam {side} {seam_index}', points,
                   [.0011, .0015, .0015, .0014, .0012, .0009, .0004],
                   bill, 'head', 'edge', eras=ALL, sides=8), 'head')

        inner_jaw_line = [
            (side * .054, -.354, 1.584), (side * .052, -.405, 1.582),
            (side * .043, -.458, 1.556), (side * .030, -.511, 1.532),
            (side * .018, -.560, 1.525),
        ]
        add(wt(f'Inner mandible joining seam {side}', inner_jaw_line,
               [.0014, .0017, .0017, .0013, .0006], jaw, 'head', 'edge',
               eras=ALL, sides=8), 'head')

    # Dark formed under-shell joins the inherited frame without hiding its
    # construction. It backs the plate courses and prevents accidental gaps.
    cervical = [
        (1.25, -.095, .205, .208), (1.325, -.15, .177, .19),
        (1.41, -.23, .147, .17), (1.48, -.283, .127, .148),
        (1.55, -.296, .12, .14), (1.60, -.276, .123, .143),
        (1.65, -.25, .121, .144),
    ]
    shell_vertices = []
    shell_faces = []
    z_steps, a_steps = 25, 65
    for zi in range(z_steps):
        z = 1.30 + (1.645 - 1.30) * zi / (z_steps - 1)
        for ai in range(a_steps):
            angle = -math.pi + math.tau * ai / (a_steps - 1)
            shell_vertices.append(envelope(cervical, z, angle, .002))
    for zi in range(z_steps - 1):
        for ai in range(a_steps - 1):
            p = zi * a_steps + ai
            shell_faces.append((p, p + 1, p + a_steps + 1, p + a_steps))
    under_shell = add(wm('Cervical formed shadow shell', shell_vertices,
                         shell_faces, neck, 'neck', 'recess', ALL), 'neck')
    for face in under_shell.data.polygons:
        face.use_smooth = True

    wall = under_shell.modifiers.new('Cervical inner liner wall', 'SOLIDIFY')
    wall.thickness = .004
    wall.offset = -1

    # Three different neck courses: front throat shields, articulated side
    # guards, and swept nape plates. Their boundaries overlap but retain dark
    # mechanical slots between courses.
    throat = [
        (1.645, .112, .62), (1.552, .137, .70),
        (1.443, .148, .79), (1.329, .111, .90),
    ]
    for row, (z, length, width) in enumerate(throat):
        outline = [
            (-width * .48, z), (width * .42, z + .004),
            (width * .50, z - .035), (width * .19, z - length),
            (-width * .18, z - length * .94), (-width * .51, z - .045),
        ]
        project = lambda a, zz: envelope(cervical, zz, a, .012)
        add(fitted_patch(f'Curved throat shield {row}', smooth_profile(outline, 2),
                  project, neck, 'neck', 'plate', thickness=.007,
                  eras=ALL, sub=5), 'neck')
        # A fine lower lip emphasizes actual plate depth; it follows the same
        # envelope and does not bridge the articulated gap below it.
        edge = [project(-width * .18, z - length * .94),
                project(0, z - length), project(width * .19, z - length)]
        add(wt(f'Throat shield warm edge {row}', edge,
               [.0011, .0018, .0008], neck, 'neck', 'edge', eras=ALL,
               sides=8), 'neck')

    side_rows = [
        (1.626, .096, .36), (1.532, .121, .40),
        (1.429, .133, .47), (1.318, .105, .53),
    ]
    for side in (-1, 1):
        for row, (z, length, spread) in enumerate(side_rows):
            angle = side * 1.04
            outline = [
                (angle - side * spread, z + .005),
                (angle + side * spread * .72, z),
                (angle + side * spread, z - length * .43),
                (angle + side * .18, z - length),
                (angle - side * spread * .78, z - length * .83),
            ]
            project = lambda a, zz: envelope(
                cervical, zz, a, .007 + .016 * max(0, (z - zz) / length)
            )
            add(fitted_patch(f'Swept lateral neck plate {side} {row}', outline,
                      project, neck, 'neck', 'plate', thickness=.006,
                      eras=ALL, sub=4), 'neck')

            # Side-to-nape transition closes the broad wire-backed slot
            # between the original lateral and rear courses. This stays on
            # the neck owner and follows exactly the shared cervical envelope.
            mid_angle = side*1.72
            mid = [
                (mid_angle - side*.34, z + .003),
                (mid_angle + side*.35, z),
                (mid_angle + side*.37, z - length*.45),
                (mid_angle + side*.10, z - length*.96),
                (mid_angle - side*.30, z - length*.78),
            ]
            mid_project = lambda a, zz, top=z, span=length: envelope(
                cervical, zz, a, .009 + .012*max(0, min(1, (top - zz)/span))
            )
            add(fitted_patch(f'Fitted cervical side nape transition {side} {row}',
                             smooth_profile(mid, 2), mid_project, neck,
                             'neck', 'plate', thickness=.005,
                             eras=ALL, sub=4), 'neck')

            rear_angle = side * 2.34
            rear = [
                (rear_angle - side * .32, z + .003),
                (rear_angle + side * .27, z - .005),
                (rear_angle + side * .30, z - length * .51),
                (rear_angle + side * .09, z - length * .92),
                (rear_angle - side * .30, z - length * .69),
            ]
            rear_project = lambda a, zz: envelope(
                cervical, zz, a, .008 + .014 * max(0, (z - zz) / length)
            )
            add(fitted_patch(f'Swept nape plate {side} {row}', rear,
                      rear_project, neck, 'neck', 'plate', thickness=.006,
                      eras=ALL, sub=4), 'neck')

    # Narrow center nape courses cover the remaining plain rear liner strip,
    # leaving only small construction seams against the established side rows.
    for row, (top, length, _) in enumerate(side_rows):
        center_angle = math.pi + (.035 if row % 2 else -.035)
        outline = [
            (center_angle - .49, top), (center_angle + .49, top + .003),
            (center_angle + .47, top - length*.42),
            (center_angle + .10, top - length*.98),
            (center_angle - .39, top - length*.79),
        ]
        project = lambda a, z, root=top, span=length: envelope(
            cervical, z, a, .010 + .012*max(0, min(1, (root - z)/span))
        )
        add(fitted_patch(f'Fitted cervical center nape scale {row}',
                         smooth_profile(outline, 2), project, neck,
                         'neck', 'plate', thickness=.005, eras=ALL,
                         sub=5), 'neck')

    return {
        'addedMeshes': dict(counts),
        'removedMeshes': removed,
        'notes': [
            'Head and crown additions attach to existing head or cranial-cover owners; throat plates attach to neck.',
            'Original bill, mandible, contact geometry, pivots and internal descendants are untouched.',
            'Passive eye wells remain dark in Maker and Mechanic; the optic role is Builder-only.',
            'The cheek backing closes the accidental rear aperture while the narrow orbital rib preserves the mouth opening.',
            'Scalp/temporal plates preserve the 60 mm optic exclusion; the fitted cheek has a 46 mm clear aperture around the fixed YZ eye center. Visibility requires rendered-ray verification.',
            'Continuous cranial backing and thirty-five tapered quad-grid scales share one smooth envelope; authored head/neck patches omit angle-limited bevel and weighted-normal modifiers.',
            'Rear skull and center nape courses follow their separate crown and neck owners; optic stack is seated 15 mm deeper without changing YZ centers, inside the formed cheek surround.',
            'Removed superseded mesh names: ' + ', '.join(removed),
        ],
    }
