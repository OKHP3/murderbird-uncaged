"""Fitted limb and foot armor for the alignment-v3 appearance proposal.

Every surface is a rigid child of an existing moving assembly. The module
adds dorsal/forward armor while leaving the load-bearing links, bearing axes,
toe articulation and planted contact geometry intact.
"""

import math as _math


def build(ctx):
    bpy = ctx['bpy']
    Vector = ctx['Vector']
    math = ctx.get('math', _math)
    wm = ctx['wm']
    wt = ctx['wt']
    fastener = ctx['fastener']
    objects = bpy.data.objects
    bpy.context.view_layer.update()

    created = []
    estimated_top_triangles = 0
    estimated_finished_triangles = 0

    def smooth_shell(name, vertices, faces, owner, region, role='plate',
                     thickness=.006, bevel_width=.0018):
        nonlocal estimated_top_triangles, estimated_finished_triangles
        obj = wm(name, vertices, faces, owner, region, role)
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
        solid = obj.modifiers.new('Fitted armor return', 'SOLIDIFY')
        solid.thickness = thickness
        solid.offset = -1
        bevel = obj.modifiers.new('Soft forged edge', 'BEVEL')
        bevel.width = bevel_width
        bevel.segments = 2
        created.append(obj)
        top = sum(max(0, len(face) - 2) for face in faces)
        estimated_top_triangles += top
        # Solidify adds a reversed inner surface and perimeter walls. The
        # fourfold figure is a conservative rough allowance for those walls
        # plus the later two-segment bevel; exact counts come from export.
        estimated_finished_triangles += top * 4
        return obj

    def track_primitive(obj):
        nonlocal estimated_top_triangles, estimated_finished_triangles
        created.append(obj)
        triangles = sum(max(0, len(poly.vertices) - 2) for poly in obj.data.polygons)
        estimated_top_triangles += triangles
        estimated_finished_triangles += triangles
        return obj

    def tapered_guard(name, start, end, owner, region, *, half_width,
                      half_depth, t0, t1, front, across, rows=7, columns=16,
                      arc=1.19, central_gap=0, thickness=.007):
        """Crowned, open-sided plate formed around a real rigid link axis."""
        if central_gap:
            half_columns = columns // 2
            angles = ([-arc + (arc - central_gap) * k / half_columns
                       for k in range(half_columns + 1)]
                      + [central_gap + (arc - central_gap) * k / half_columns
                         for k in range(half_columns + 1)])
        else:
            angles = [-arc + 2 * arc * k / columns for k in range(columns + 1)]
        verts = []
        for j in range(rows):
            u = j / (rows - 1)
            t = t0 + (t1 - t0) * u
            # Fine taper at both ends and a broad shoulder through the middle.
            fullness = .79 + .21 * math.sin(math.pi * u) ** .55
            center = start.lerp(end, t)
            for angle in angles:
                p = (center
                     + across * (math.sin(angle) * half_width * fullness)
                     + front * (math.cos(angle) * half_depth * fullness))
                verts.append(tuple(p))
        faces = []
        stride = len(angles)
        for j in range(rows - 1):
            for k in range(len(angles) - 1):
                if central_gap and k == columns // 2:
                    continue
                a = j * stride + k
                faces.append((a, a + 1, a + stride + 1, a + stride))
        return smooth_shell(name, verts, faces, owner, region,
                            thickness=thickness, bevel_width=.0022)

    def segmented_side_guard(name, start, end, owner, region, *, width, depth,
                             front, across, side, courses):
        """Two formed cheek plates wrap the outer edge of a retained link rail."""
        rows, columns = 4, 3
        verts, faces = [], []
        stride = columns + 1
        for course, (t0, t1) in enumerate(courses):
            base = len(verts)
            for j in range(rows):
                u = j / (rows - 1)
                t = t0 + (t1 - t0) * u
                fullness = .76 + .24 * math.sin(math.pi * u)
                center = start.lerp(end, t)
                angle_center = side * 1.35
                for k in range(columns + 1):
                    angle = angle_center + (k / columns - .5) * .30
                    p = (center
                         + across * (math.sin(angle) * width * fullness)
                         + front * (math.cos(angle) * depth * fullness)
                         + front * .004)
                    verts.append(tuple(p))
            for j in range(rows - 1):
                for k in range(columns):
                    a = base + j * stride + k
                    faces.append((a, a + 1, a + stride + 1, a + stride))
        return smooth_shell(name, verts, faces, owner, region,
                            thickness=.0045, bevel_width=.0018)

    def channel_points(start, end, front, across, depth, t_values):
        return [start.lerp(end, t) + front * (depth * .65)
                + across * 0 for t in t_values]

    def interrupted_tie(name, start, end, owner, region, front, across,
                        width, depth, t, arc, gap, side):
        points = []
        for i in range(7):
            angle = side * (gap + (arc - gap) * i / 6)
            points.append(start.lerp(end, t)
                          + across * (math.sin(angle) * width)
                          + front * (math.cos(angle) * depth + .0025))
        return wt(name, points, [.0022, .0027, .0030, .0031,
                                 .0030, .0027, .0022], owner,
                  region, 'edge', sides=6)

    # Hip and knee are fixed assembly pivots in the loaded alignment source.
    # The casing starts and ends well clear of the existing concentric skirts.
    limb_specs = (
        ('thigh', 'leg', .089, .066, ((.15, .47), (.535, .86))),
        ('shin', 'leg', .076, .056, ((.12, .44), (.51, .83))),
    )
    for label in ('left', 'right'):
        thigh = objects[f'{label}-thigh']
        shin = objects[f'{label}-shin']
        foot = objects[f'{label}-foot']
        hip = thigh.matrix_world.translation.copy()
        knee = shin.matrix_world.translation.copy()
        ankle = foot.matrix_world.translation.copy()

        for link_name, region, width, depth, courses in limb_specs:
            if link_name == 'thigh':
                a, b, owner = hip, knee, thigh
            else:
                a, b, owner = knee, ankle, shin
            axis = (b - a).normalized()
            forward = Vector((0, -1, 0))
            forward = (forward - axis * forward.dot(axis)).normalized()
            across = axis.cross(forward).normalized()
            forward = across.cross(axis).normalized()
            if forward.y > 0:
                across.negate()
                forward = across.cross(axis).normalized()

            # Two non-identical courses leave a narrow dark break between
            # them and reveal the original rods along both sides.
            for course, (t0, t1) in enumerate(courses):
                taper = 1.0 if course == 0 else .91
                tapered_guard(
                    f'{label} {link_name} fitted crown {course + 1}',
                    a, b, owner, region,
                    half_width=width * taper,
                    half_depth=depth * (1.0 if course == 0 else .94),
                    t0=t0, t1=t1, front=forward, across=across,
                    rows=7, columns=16, arc=1.18, central_gap=.17,
                )

                # A pair of compact, flush seats anchors each armor course.
                for edge in (-1, 1):
                    t = t0 + (t1 - t0) * (.13 if edge < 0 else .87)
                    angle = edge * .88
                    point = (a.lerp(b, t)
                             + across * (math.sin(angle) * width * taper)
                             + forward * (math.cos(angle) * depth * .98))
                    track_primitive(fastener(
                        f'{label} {link_name} crown seat {course + 1} {edge:+d}',
                        point, forward, owner, region, r=.0036))

                # Interrupted narrow ribs bind each course without bridging
                # the central opening or covering the dark actuator channel.
                tie_t = (t0 + t1) * .5
                tie_course = 0 if link_name == 'thigh' else 1
                if course == tie_course:
                    for side_sign in (-1, 1):
                        track_primitive(interrupted_tie(
                            f'{label} {link_name} formed tie {course + 1} {side_sign:+d}',
                            a, b, owner, region, forward, across,
                            width * taper, depth * (1.0 if course == 0 else .94),
                            tie_t, 1.18, .17, side_sign))

            # A recessed load rail remains visible in the slot between both
            # crown halves. It follows the link but leaves each bearing face
            # and the larger joint skirt exposed.
            rail_points = channel_points(a, b, forward, across, depth,
                                         (.16, .29, .43, .58, .72, .84))
            track_primitive(wt(
                f'{label} {link_name} central exposed load rail', rail_points,
                [.0055, .0075, .0085, .0085, .0070, .0055],
                owner, region, 'frame', sides=8))

            # Segmented cheek guards flank each original side load member.
            # Their short courses leave long open portions of the mechanism.
            for side_sign in (-1, 1):
                segmented_side_guard(
                    f'{label} {link_name} formed side guard {side_sign:+d}',
                    a, b, owner, region, width=width * 1.02,
                    depth=depth * .40, front=forward, across=across,
                    side=side_sign, courses=((.19, .38), (.62, .81)),
                )

            # Dark narrow reveals run along the uncovered side channels. They
            # frame rather than hide the retained mechanical rails.
            for side in (-1, 1):
                points = []
                for t in (.12, .29, .47, .65, .84, .92):
                    center = a.lerp(b, t)
                    points.append(center
                                  + across * (side * width * 1.02)
                                  + forward * (depth * .34))
                track_primitive(wt(
                    f'{label} {link_name} exposed dark channel {side:+d}',
                    points, [.0060, .0075, .008, .008, .007, .0055],
                    owner, region, 'frame', sides=8))

        # Two small radial screws on each existing joint face add scale and
        # purpose to the inherited skirts without enlarging their silhouette.
        for joint, owner, region, radius in (
                ('hip', thigh, 'leg', .056),
                ('knee', shin, 'leg', .054),
                ('ankle', foot, 'foot', .046)):
            center = owner.matrix_world.translation.copy()
            axis = (owner.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()
            radial_up = Vector((0, 0, 1))
            radial_up = (radial_up - axis * radial_up.dot(axis)).normalized()
            if radial_up.length < .5:
                radial_up = Vector((0, 1, 0))
                radial_up = (radial_up - axis * radial_up.dot(axis)).normalized()
            radial_side = axis.cross(radial_up).normalized()
            for face_side in (-1, 1):
                face_center = center + axis * (face_side * .0617)
                for angle in (.40, 2.50, 4.60):
                    radial = radial_up * math.cos(angle) + radial_side * math.sin(angle)
                    point = face_center + radial * (radius * .52)
                    track_primitive(fastener(
                        f'{label} {joint} radial face screw {face_side:+d} {angle:.2f}',
                        point, axis * face_side, owner, region, r=.0022))

    # The dorsal foot bridge joins the ankle armor to the toe roots. It does
    # not wrap under the foot, move the toe assembly, or cover the contact sole.
    for label in ('left', 'right'):
        foot = objects[f'{label}-foot']
        ankle = foot.matrix_world.translation.copy()
        toe_pivot = objects[f'{label}-toes'].matrix_world.translation.copy()
        axis = (toe_pivot - ankle).normalized()
        up = Vector((0, 0, 1))
        up = (up - axis * up.dot(axis)).normalized()
        across = axis.cross(up).normalized()
        if up.z < 0:
            up.negate()
            across.negate()

        deck_width = .079
        deck_depth = .041
        rows, cols = 7, 18
        verts = []
        for j in range(rows):
            u = j / (rows - 1)
            t = .12 + .62 * u
            fullness = .66 + .34 * math.sin(math.pi * u) ** .55
            center = ankle.lerp(toe_pivot, t) + up * .023
            for k in range(cols + 1):
                angle = -1.19 + 2.38 * k / cols
                p = (center + across * (math.sin(angle) * deck_width * fullness)
                     + up * (math.cos(angle) * deck_depth * fullness))
                verts.append(tuple(p))
        faces = []
        stride = cols + 1
        for j in range(rows - 1):
            for k in range(cols):
                a = j * stride + k
                faces.append((a, a + 1, a + stride + 1, a + stride))
        smooth_shell(f'{label} dorsal foot bridge', verts, faces, foot, 'foot',
                     thickness=.006, bevel_width=.0024)

        # Each proximal toe receives a short shaped knuckle cover. A smaller
        # cap shields only the base of the distal segment; claw/contact tips
        # remain uncovered and each original toe owner remains independent.
        for digit in (1, 2, 3):
            proximal = objects[f'{label}-digit-{digit}-proximal']
            distal = objects[f'{label}-digit-{digit}-distal']
            root = proximal.matrix_world.translation.copy()
            hinge = distal.matrix_world.translation.copy()
            direction = (hinge - root).normalized()
            dorsal = Vector((0, 0, 1))
            dorsal = (dorsal - direction * dorsal.dot(direction)).normalized()
            lateral = direction.cross(dorsal).normalized()
            if dorsal.z < 0:
                dorsal.negate()
                lateral.negate()
            length = (hinge - root).length
            width = .031 if digit == 2 else .028
            depth = .020 if digit == 2 else .018
            tapered_guard(
                f'{label} digit {digit} proximal knuckle plate',
                root, hinge, proximal, 'foot',
                half_width=width, half_depth=depth,
                t0=.10, t1=.79, front=dorsal, across=lateral,
                rows=5, columns=10, arc=1.02, thickness=.0045,
            )

            # Limit the terminal cover to the first 35 mm beyond its real
            # hinge so it cannot reach the talon tip or planted contact area.
            tip = hinge + direction * min(.035, max(.024, length * .27))
            tapered_guard(
                f'{label} digit {digit} distal root cap',
                hinge, tip, distal, 'foot',
                half_width=width * .73, half_depth=depth * .72,
                t0=.03, t1=.86, front=dorsal, across=lateral,
                rows=4, columns=10, arc=.98, thickness=.0038,
            )

    return {
        'removedNames': [],
        'addedNames': [obj.name for obj in created],
        'meshCount': len(created),
        'estimatedTopSurfaceTriangles': estimated_top_triangles,
        'estimatedFinishedTrianglesPerEra': estimated_finished_triangles,
        'limits': 'Triangle estimate excludes bevel tessellation and is not measured export output.',
    }
