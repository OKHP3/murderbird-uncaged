"""Build the rigid head and cervical exterior for the v1 three-era proposal.

Called by ``build-uncaged-exterior-v1.py`` after loading the preserved
structural-v1 rig.  The function changes mesh descendants only: the head,
neck, jaw, bill, optic, and contact landmark empties keep their authored
positions.  All dimensions are local Blender metres (Z up, forward -Y).

This is an interpretive mechanical construction, not evidence of anatomy or
an exact reconstruction of a reference image.
"""
import math


def build(ctx):
    from mathutils.geometry import tessellate_polygon

    bpy = ctx['bpy']
    Vector = ctx['Vector']
    Matrix = ctx['Matrix']
    mesh = ctx['mesh']
    bevel = ctx['bevel']
    rod = ctx['rod']
    ring = ctx['ring']
    tube = ctx['tube']
    plate = ctx['plate']
    loft = ctx['loft']
    delete_meshes = ctx['delete_meshes']
    under = ctx['under']
    mats = ctx['mats']

    head = bpy.data.objects['head']
    neck = bpy.data.objects['neck']
    jaw = bpy.data.objects['jaw']
    upper_bill = bpy.data.objects['upper-bill']
    optics = bpy.data.objects['builder-optics']
    cranial_cover = bpy.data.objects['cranial-cover']
    processing = bpy.data.objects['processing']

    # Clear the previous shell while preserving all rig empties and the
    # independent processing assembly.
    delete_meshes(lambda o: (under(o, head) or under(o, neck)) and not under(o, processing))

    def tagged_call(fn, *args, region, role, eras='maker,mechanic,builder', **kwargs):
        before = {o.as_pointer() for o in bpy.data.objects}
        result = fn(*args, **kwargs)
        for obj in bpy.data.objects:
            if obj.type != 'MESH' or obj.as_pointer() in before:
                continue
            lname = obj.name.lower()
            object_role = role
            if any(token in lname for token in ('rivet', 'fastener', 'edge', 'seam')):
                object_role = 'edge'
            elif any(token in lname for token in ('bearing', 'hinge', 'pin', 'retainer')):
                object_role = 'bearing'
            obj['region'] = region
            obj['surfaceRole'] = object_role
            obj['inherited'] = True
            obj['exteriorEras'] = eras
        if result is not None and result.type == 'MESH':
            result['region'] = region
            result['surfaceRole'] = role
            result['inherited'] = True
            result['exteriorEras'] = eras
        return result

    def mk_mesh(name, verts, faces, material, parent, *, region, role, eras='maker,mechanic,builder', edge=0):
        obj = tagged_call(mesh, name, verts, faces, material, parent, region=region, role=role, eras=eras)
        if edge:
            bevel(obj, edge)
        return obj

    def mk_rod(name, a, b, radius, material, parent, *, region, role, eras='maker,mechanic,builder', sides=12, end_radius=None):
        return tagged_call(rod, name, a, b, radius, material, parent, region=region, role=role, eras=eras, sides=sides, end_radius=end_radius)

    def mk_ring(name, center, radius, wire, material, parent, *, region, role, eras='maker,mechanic,builder', axis='X', segments=36):
        return tagged_call(ring, name, center, radius, wire, material, parent, region=region, role=role, eras=eras, axis=axis, segments=segments)

    def mk_tube(name, points, radii, material, parent, *, region, role, eras='maker,mechanic,builder', sides=10):
        return tagged_call(tube, name, points, radii, material, parent, region=region, role=role, eras=eras, sides=sides)

    def mk_plate(name, center, width, length, material, parent, *, region, role='shell', rotation=(0, 0, 0), eras='maker,mechanic,builder'):
        return tagged_call(plate, name, center, width, length, material, parent, region=region, role=role, eras=eras, rotation=rotation)

    def mk_loft(name, sections, material, parent, *, region, role='shell', segments=24, start=0, span=math.tau, thickness=.008, eras='maker,mechanic,builder'):
        return tagged_call(loft, name, sections, material, parent, region=region, role=role, eras=eras, segments=segments, start=start, span=span, thickness=thickness)

    # A single swept cranial hood hugs the curved crown and occiput. Shallow
    # surface patches are projected onto its measured loft rings below; this
    # avoids detached leaf-shaped plates while keeping visible panel breaks.
    crown_sections = [
        (-.008, .120, .046, .055), (.025, .103, .083, .113),
        (.065, .077, .132, .184), (.108, .055, .165, .222),
        (.151, .050, .165, .220), (.190, .062, .145, .187),
        (.215, .075, .137, .176), (.235, .090, .105, .150),
        (.246, .098, .056, .090), (.251, .101, .0015, .0015),
    ]
    mk_loft('Swept cranial hood', crown_sections, mats['frame'], cranial_cover, region='head', role='frame', thickness=.014)

    def interpolate_ring(z):
        for a, b in zip(crown_sections, crown_sections[1:]):
            if a[0] <= z <= b[0]:
                t = (z - a[0]) / (b[0] - a[0])
                return tuple(a[i] + (b[i] - a[i]) * t for i in range(1, 4))
        return crown_sections[0][1:] if z < crown_sections[0][0] else crown_sections[-1][1:]

    def crown_patch(name, side, angle_start, angle_end, z_values, drift=0.0, role='shell'):
        verts = []
        across = 10
        z_low, z_high = z_values[0], z_values[-1]
        for z in z_values:
            cy, rx, ry = interpolate_ring(z)
            row_t = (z - z_low) / max(z_high - z_low, 1e-6)
            center = (angle_start + angle_end) * .5 + drift * row_t
            taper = .64 + .36 * math.sin(math.pi * row_t)
            half_span = (angle_end - angle_start) * .5 * taper
            a0 = center - half_span
            a1 = center + half_span
            for j in range(across + 1):
                t = j / across
                angle = a0 + (a1 - a0) * t
                angle *= side
                # A fixed measured surface-normal lift makes the plate proud
                # without scaling it away from the underlying curved shell.
                base = Vector((math.sin(angle) * rx, cy - math.cos(angle) * ry, z))
                normal = Vector((math.sin(angle) / max(rx, .02),
                                 -math.cos(angle) / max(ry, .02), .35)).normalized()
                verts.append(tuple(base + normal * .008))
        faces = []
        for row in range(len(z_values) - 1):
            for col in range(across):
                a = row * (across + 1) + col
                quad = (a, a + 1, a + across + 2, a + across + 1)
                faces.append(quad if side > 0 else tuple(reversed(quad)))
        patch = mk_mesh(name, verts, faces, mats['shell'], cranial_cover, region='head', role=role, edge=.0015)
        solid = patch.modifiers.new('Cranial panel wall', 'SOLIDIFY')
        solid.thickness = .010

        def attach_fastener(z, angle):
            cy, rx, ry = interpolate_ring(z)
            a = angle * side
            point = Vector((math.sin(a) * rx, cy - math.cos(a) * ry, z))
            normal = Vector((math.sin(a) / max(rx, .02),
                             -math.cos(a) / max(ry, .02), .35)).normalized()
            point += normal * .008
            mk_rod(name + ' flush fastener', point - normal * .002, point + normal * .006,
                   .0045, mats['bearing'], cranial_cover, region='head', role='bearing', sides=10)

        attach_fastener(z_low + (z_high - z_low) * .16, angle_start + (angle_end-angle_start)*.5)
        attach_fastener(z_high - (z_high - z_low) * .16, angle_start + (angle_end-angle_start)*.5 + drift)
        return patch

    for side in (-1, 1):
        crown_patch('Cranial brow-to-crown swept plate', side, .16, .68, [.045, .075, .110, .148, .181], .94)
        crown_patch('Cranial temple-to-rear swept plate', side, .73, 1.28, [.060, .091, .127, .165, .198], .88)
        crown_patch('Cranial rear occipital swept plate', side, 1.42, 1.98, [.060, .093, .128, .164, .199, .222], .78)
        crown_patch('Cranial trailing overlap plate', side, 2.00, 2.42, [.065, .100, .138, .177, .210, .231], .55)
        crown_patch('Cranial high rear crown plate', side, .52, 2.54, [.174, .196, .218, .237, .246], .36)
    crown_patch('Cranial swept crest plate', 1, -.22, .22, [.048, .082, .120, .158, .198, .230, .246], .75)

    # A short formed brow bridge closes the hood around the upper bill root.
    mk_loft('Head brow bridge', [
        (.116, -.075, .102, .055), (.137, -.079, .116, .061),
        (.158, -.060, .104, .056), (.177, -.030, .077, .042),
    ], mats['shell'], cranial_cover, region='head', role='shell', thickness=.008)

    # Side rails and socket rims define a deliberately open cheek. Dark
    # recesses remain passive in all eras; only the lens belongs to Builder.
    for side in (-1, 1):
        eye = (side * .151, -.074, .105)
        mk_rod('Passive eye socket recess', (side * .126, eye[1], eye[2]), (side * .154, eye[1], eye[2]), .064, mats['dark'], head, region='optic', role='dark', sides=36)
        mk_ring('Passive eye bearing rim', (side * .158, eye[1], eye[2]), .067, .010, mats['bearing'], head, region='optic', role='bearing', segments=36)
        mk_ring('Passive inner socket lip', (side * .164, eye[1], eye[2]), .052, .0055, mats['edge'], head, region='optic', role='edge', segments=36)
        mk_rod('Builder amber sensor lens', (side * .159, eye[1], eye[2]), (side * .165, eye[1], eye[2]), .038, mats['optic'], optics, region='optic', role='optic', eras='builder', sides=32)
        mk_tube('Open cheek upper forged strut', [
            (side * .139, .034, .071), (side * .158, -.018, .035),
            (side * .151, -.093, .008), (side * .116, -.180, .028),
        ], [.026, .023, .021, .030], mats['shell'], head, region='head', role='shell', sides=10)
        mk_tube('Open cheek lower hinge fork', [
            (side * .111, .012, -.039), (side * .120, -.070, -.070),
            (side * .083, -.159, -.094), (side * .023, -.224, -.101),
        ], [.020, .021, .017, .009], mats['frame'], jaw, region='bill', role='frame', sides=10)
        mk_rod('Jaw hinge pin', (side * .105, -.010, -.047), (side * .160, -.010, -.047), .031, mats['bearing'], head, region='head', role='bearing', sides=24)
        mk_ring('Jaw hinge retainer', (side * .164, -.010, -.047), .033, .006, mats['edge'], head, region='head', role='edge', segments=24)

    # Deep hooked side profile, swept through variable lateral widths. This
    # gives the bill a real vertical convex section from the forehead above
    # the eye (z ~= .20) to the lower hook (z ~= -.19), rather than a shallow
    # horizontal tube. Its leading point remains at the existing landmark.
    # Each profile station is (local Y, local Z, half-width, convexity weight).
    profile = [
        (-.080, .078, .073, .14),
        (-.104, .126, .098, .23),
        (-.151, .140, .117, .34),
        (-.205, .119, .130, .47),
        (-.254, .083, .122, .53),
        (-.300, .038, .101, .58),
        (-.337, -.021, .075, .59),
        (-.367, -.076, .042, .49),
        (-.387, -.104, .006, .14),
        (-.380, -.155, .010, .12),
        (-.346, -.225, .002, .08),
        (-.325, -.176, .008, .10),
        (-.310, -.115, .018, .12),
        (-.294, -.075, .026, .08),
        (-.263, -.060, .061, .10),
        (-.215, -.035, .091, .13),
        (-.183, .030, .098, .19),
        (-.157, .064, .091, .18),
        (-.103, .060, .057, .12),
    ]
    lateral_slices = [-1.0, -.66, -.33, 0.0, .33, .66, 1.0]
    verts = []
    for lateral in lateral_slices:
        convex = 1.0 - lateral * lateral
        for y, z, half_width, weight in profile:
            # The negative-Y offset creates a gently crowned forged face.
            verts.append((lateral * half_width, y - .018 * convex * weight, z))
    count = len(profile)
    faces = []
    for layer in range(len(lateral_slices) - 1):
        base_a = layer * count
        base_b = (layer + 1) * count
        for i in range(count):
            j = (i + 1) % count
            faces.append((base_a + i, base_a + j, base_b + j, base_b + i))
    last = (len(lateral_slices) - 1) * count
    # Explicit triangle caps keep this concave profile filled in both Blender
    # and glTF, where a single non-convex ngon may be tessellated as an arc.
    outline = [Vector((y, z, 0.0)) for y, z, _w, _curve in profile]
    outline_index = {(round(p.x, 8), round(p.y, 8)): i for i, p in enumerate(outline)}
    cap_triangles = []
    for triangle in tessellate_polygon([outline]):
        # Blender versions have returned both source indices and copied
        # vectors from tessellate_polygon; accept either representation.
        ids = [int(p) if isinstance(p, int) else outline_index[(round(p.x, 8), round(p.y, 8))]
               for p in triangle]
        cap_triangles.append(ids)

    def edge_distance(y, z):
        best = float('inf')
        for k, current in enumerate(profile):
            nxt = profile[(k + 1) % len(profile)]
            dy, dz = nxt[0] - current[0], nxt[1] - current[1]
            denom = dy * dy + dz * dz
            t = 0.0 if denom <= 1e-12 else max(0.0, min(1.0, ((y-current[0])*dy + (z-current[1])*dz)/denom))
            py, pz = current[0] + t * dy, current[1] + t * dz
            best = min(best, math.hypot(y - py, z - pz))
        return best

    # Subdivide each triangulated cap with shared barycentric samples and a
    # single smooth distance-based bow. This keeps the bill convex without
    # independent raised triangle centers that read as spikes.
    cap_subdivisions = 4
    for side, layer in [(-1, 0), (1, len(lateral_slices) - 1)]:
        base = layer * count
        point_cache = {}

        def cap_point(weights, ids):
            y = sum(profile[idx][0] * weight for idx, weight in zip(ids, weights))
            z = sum(profile[idx][1] * weight for idx, weight in zip(ids, weights))
            width = sum(profile[idx][2] * weight for idx, weight in zip(ids, weights))
            key = (round(y, 8), round(z, 8))
            if key in point_cache:
                return point_cache[key]
            dist = edge_distance(y, z)
            ratio = min(dist / .075, 1.0)
            bulge = .012 * ratio * (2.0 - ratio)
            idx = len(verts)
            verts.append((side * (width + bulge), y, z))
            point_cache[key] = idx
            return idx

        for ids in cap_triangles:
            grid = {}
            for i in range(cap_subdivisions + 1):
                for j in range(cap_subdivisions + 1 - i):
                    w1, w2 = i / cap_subdivisions, j / cap_subdivisions
                    weights = (1.0 - w1 - w2, w1, w2)
                    if i == 0 and j == 0:
                        grid[(i, j)] = base + ids[0]
                    elif i == cap_subdivisions and j == 0:
                        grid[(i, j)] = base + ids[1]
                    elif i == 0 and j == cap_subdivisions:
                        grid[(i, j)] = base + ids[2]
                    else:
                        grid[(i, j)] = cap_point(weights, ids)
            for i in range(cap_subdivisions):
                for j in range(cap_subdivisions - i):
                    first = (grid[(i, j)], grid[(i + 1, j)], grid[(i, j + 1)])
                    faces.append(tuple(reversed(first)) if side < 0 else first)
                    if i + j < cap_subdivisions - 1:
                        second = (grid[(i + 1, j)], grid[(i + 1, j + 1)], grid[(i, j + 1)])
                        faces.append(tuple(reversed(second)) if side < 0 else second)
    upper = mk_mesh('Upper bill deep convex forged hook', verts, faces, mats['bill'], upper_bill, region='bill', role='bill', edge=.002)
    for face in upper.data.polygons:
        face.use_smooth = True

    # Bind the contact landmark to the central foremost vertex of the actual
    # upper-bill mesh. It now follows the same articulated parent transforms.
    contact = bpy.data.objects['bill-contact']
    contact.parent = upper_bill
    contact.matrix_parent_inverse = Matrix.Identity(4)
    contact.location = (0.0, -.387 - .018 * .14, -.104)

    # A raised central ridge follows the broad bill surface. Side seam rails
    # sit on the actual profile edge instead of floating inside the side cap.
    mk_tube('Bill central forged keel', [
        (0, -.123, .125), (0, -.194, .114), (0, -.257, .077),
        (0, -.309, .032), (0, -.354, -.051), (0, -.383, -.099),
    ], [.006, .007, .007, .006, .0035, .0015], mats['frame'], upper_bill, region='bill', role='frame', sides=8)

    def side_profile_point(index, side, offset=.002):
        y, z, width, _curve = profile[index]
        return (side * (width + offset), y, z)

    for side in (-1, 1):
        for title, indices in [('brow cheek division', [1, 2, 3]),
                               ('hook cheek division', [8, 9, 10, 11]),
                               ('inner bill seam', [13, 14, 15, 16])]:
            pts = [side_profile_point(i, side, .002) for i in indices]
            mk_tube('Bill formed ' + title, pts, [.0025] * len(pts), mats['frame'], upper_bill,
                    region='bill', role='frame', sides=6)
        for index in (2, 4, 14, 16):
            p = side_profile_point(index, side, .002)
            base = p[0] - side * .004
            end = p[0] + side * .004
            mk_rod('Bill seated cheek fastener', (base, p[1], p[2]), (end, p[1], p[2]),
                   .0045, mats['bearing'], upper_bill, region='bill', role='bearing', sides=8)

    # A separate lower cutting jaw leaves a clear, dark negative-space gap to
    # the upper bill. It is attached to the authored jaw pivot.
    lower_verts = [
        (-.102, -.070, -.066), (.102, -.070, -.066),
        (.075, -.177, -.095), (-.075, -.177, -.095),
        (.014, -.263, -.104), (-.014, -.263, -.104),
        (-.060, -.127, -.080), (.060, -.127, -.080),
    ]
    # Bring the fixed lower plate up beneath the upper hook without changing
    # its articulated jaw pivot; the rear cheek remains open for inspection.
    lower_verts = [(x, y, z + .035) for x, y, z in lower_verts]
    lower_faces = [(0, 1, 7, 6), (6, 7, 2, 3), (3, 2, 4, 5), (0, 6, 3), (1, 2, 7), (3, 5, 4)]
    lower = mk_mesh('Lower jaw open forged cutting plate', lower_verts, lower_faces, mats['frame'], jaw, region='bill', role='frame', edge=.004)
    solid = lower.modifiers.new('Lower jaw forged wall thickness', 'SOLIDIFY')
    solid.thickness = .018

    # A short cheek backing closes the rear of the oversized triangular void
    # while preserving a clear forward mandible opening.
    for side in (-1, 1):
        cheek_verts = [
            (side * .101, -.018, .031), (side * .142, -.060, .028),
            (side * .146, -.112, -.008), (side * .124, -.159, -.042),
            (side * .086, -.126, -.065), (side * .080, -.060, -.052),
        ]
        cheek = mk_mesh('Open cheek rear backing plate', cheek_verts,
                        [(0, 1, 2, 3, 4, 5)], mats['shell'], head,
                        region='head', role='shell', edge=.003)
        cheek_solid = cheek.modifiers.new('Cheek plate wall', 'SOLIDIFY')
        cheek_solid.thickness = .010

    # Compact S-curved neck frame. Three tapered elliptical shells wrap the
    # front and sides, following the curved centerline and leaving small
    # service gaps at each hinge instead of presenting bare fork rails.
    for side in (-1, 1):
        mk_tube('Cervical load-bearing side rail', [
            (side * .061, .012, .028), (side * .079, -.055, .124),
            (side * .071, -.140, .232), (side * .059, -.185, .335),
            (side * .047, -.198, .423),
        ], [.020, .023, .022, .020, .017], mats['frame'], neck, region='neck', role='frame', sides=12)
        mk_rod('Cervical lower cross-pin', (side * .050, .012, .025), (side * .091, .012, .025), .050, mats['bearing'], neck, region='neck', role='bearing', sides=24)
        mk_ring('Cervical lower bearing race', (side * .096, .012, .025), .044, .007, mats['edge'], neck, region='neck', role='edge', segments=24)
        mk_rod('Cervical upper cross-pin', (side * .035, -.198, .423), (side * .073, -.198, .423), .041, mats['bearing'], neck, region='neck', role='bearing', sides=24)
        mk_ring('Cervical upper bearing race', (side * .077, -.198, .423), .035, .006, mats['edge'], neck, region='neck', role='edge', segments=24)

    # Segment cross-rings follow the S-shaped axis; overlapping axial spans
    # keep the external form continuous while leaving the base service wedge.
    mk_loft('Cervical lower curved shingle', [
        (-.018, .016, .081, .081), (.002, .010, .102, .096),
        (.047, -.006, .120, .109), (.105, -.055, .128, .113),
        (.151, -.090, .116, .106), (.174, -.102, .094, .087),
    ], mats['shell'], neck, region='neck', role='shell', thickness=.014,
       segments=28, start=-math.pi / 2 + .40, span=math.tau - .80)
    mk_loft('Cervical middle curved shingle', [
        (.148, -.088, .085, .079), (.165, -.102, .108, .101),
        (.211, -.135, .123, .113), (.259, -.162, .114, .106),
        (.286, -.180, .093, .085),
    ], mats['shell'], neck, region='neck', role='shell', thickness=.014, segments=28)
    mk_loft('Cervical middle upper overlap shingle', [
        (.264, -.170, .078, .073), (.279, -.182, .100, .092),
        (.317, -.194, .109, .098), (.350, -.199, .100, .091),
        (.369, -.199, .080, .073),
    ], mats['frame'], neck, region='neck', role='frame', thickness=.012, segments=28)
    mk_loft('Cervical upper curved shingle', [
        (.346, -.198, .073, .071), (.361, -.199, .094, .087),
        (.388, -.200, .102, .092), (.414, -.200, .092, .084),
        (.429, -.200, .073, .068),
    ], mats['shell'], neck, region='neck', role='shell', thickness=.013, segments=28)

    # A short skull-attached socket overlaps the neck shingle across the top
    # hinge. Because it follows the head transform, the joint remains visibly
    # assembled as the neck and skull articulate independently.
    mk_loft('Skull cervical socket collar', [
        (-.090, .000, .073, .076), (-.078, .000, .095, .096),
        (-.043, .000, .100, .099), (-.018, .000, .084, .087),
        (.002, .000, .073, .077),
    ], mats['bearing'], head, region='head', role='bearing', thickness=.012, segments=28)

    # Short oblique plates overlap the smooth cervical shells and follow the
    # S-curve upward. They remain on the neck rig, stop before the skull joint,
    # and avoid the negative-X lower service aperture.
    neck_rings = [
        (-.018, .016, .081, .081), (.002, .010, .102, .096),
        (.047, -.006, .120, .109), (.105, -.055, .128, .113),
        (.151, -.090, .116, .106), (.174, -.102, .094, .087),
        (.211, -.135, .123, .113), (.259, -.162, .114, .106),
        (.286, -.180, .093, .085), (.317, -.194, .109, .098),
        (.350, -.199, .100, .091), (.369, -.199, .080, .073),
        (.388, -.200, .102, .092), (.414, -.200, .092, .084),
        (.429, -.200, .073, .068),
    ]

    def neck_ring_at(z):
        for a, b in zip(neck_rings, neck_rings[1:]):
            if a[0] <= z <= b[0]:
                t = (z - a[0]) / (b[0] - a[0])
                return tuple(a[i] + (b[i] - a[i]) * t for i in range(1, 4))
        return neck_rings[0][1:] if z < neck_rings[0][0] else neck_rings[-1][1:]

    def cervical_panel(name, side, z_values, start_angle, end_angle, drift):
        across = 6
        verts = []
        z0, z1 = z_values[0], z_values[-1]
        for z in z_values:
            cy, rx, ry = neck_ring_at(z)
            trow = (z - z0) / max(z1 - z0, 1e-6)
            center = (start_angle + end_angle) * .5 + drift * trow
            half = (end_angle - start_angle) * .5 * (.62 + .38 * math.sin(math.pi * trow))
            for col in range(across + 1):
                angle = (center - half + 2 * half * col / across) * side
                verts.append((math.sin(angle) * rx * 1.055,
                              cy - math.cos(angle) * ry * 1.055,
                              z + .002))
        faces = []
        for row in range(len(z_values) - 1):
            for col in range(across):
                a = row * (across + 1) + col
                quad = (a, a + 1, a + across + 2, a + across + 1)
                faces.append(quad if side > 0 else tuple(reversed(quad)))
        panel = mk_mesh(name, verts, faces, mats['shell'], neck,
                        region='neck', role='shell', edge=.0015)
        wall = panel.modifiers.new('Cervical link plate wall', 'SOLIDIFY')
        wall.thickness = .008
        z = (z0 + z1) * .5
        cy, rx, ry = neck_ring_at(z)
        angle = (start_angle + end_angle) * .5 + drift * .5
        angle *= side
        p = Vector((math.sin(angle) * rx * 1.055,
                    cy - math.cos(angle) * ry * 1.055,
                    z + .002))
        n = Vector((math.sin(angle) / max(rx, .02),
                    -math.cos(angle) / max(ry, .02), .2)).normalized()
        mk_rod(name + ' service fastener', p - n * .002, p + n * .005,
               .004, mats['bearing'], neck, region='neck', role='bearing', sides=8)

    for side in (-1, 1):
        cervical_panel('Cervical lower diagonal link plate', side,
                       [.018, .050, .083, .118, .153, .170], .15, .76, .30)
        cervical_panel('Cervical middle diagonal link plate', side,
                       [.145, .176, .210, .248, .279, .292], .23, .86, .34)
        cervical_panel('Cervical upper diagonal link plate', side,
                       [.272, .300, .335, .370, .399, .412], .20, .82, .28)

    # Three exposed restraint links follow the cervical curve. They are short
    # and local to the neck assembly, not a continuous flexible hose.
    for idx, (y, z, radius) in enumerate([(-.006, .050, .023), (-.078, .160, .025), (-.173, .305, .021)]):
        mk_ring(f'Cervical restraint bearing link {idx + 1}', (0, y, z), radius, .005, mats['bearing'], neck, region='neck', role='bearing', axis='Y', segments=20)

    # Group metadata allows downstream era/material transforms to recognize
    # the passive shells while leaving powered sensing explicitly Builder-only.
    for group, region, eras in [(head, 'head', 'maker,mechanic,builder'), (cranial_cover, 'head', 'maker,mechanic,builder'), (neck, 'neck', 'maker,mechanic,builder'), (jaw, 'bill', 'maker,mechanic,builder'), (upper_bill, 'bill', 'maker,mechanic,builder'), (optics, 'optic', 'builder')]:
        group['region'] = region
        group['inherited'] = group is not optics
        group['exteriorEras'] = eras

    return {
        'headNeck': {
            'status': 'interpretive rigid exterior proposal',
            'pivotsChanged': False,
            'billContactLandmarkChanged': True,
            'contactEnvelope': {'billLocalTip': (0.0, -.38952, -.104), 'profileStations': len(profile), 'verticalRange': (min(p[1] for p in profile), max(p[1] for p in profile))},
            'designChoices': ['deep convex hooked bill', 'open cheek and mandible gap', 'curved hood panels', 'segmented cervical guards with a negative-X base service aperture'],
        }
    }
