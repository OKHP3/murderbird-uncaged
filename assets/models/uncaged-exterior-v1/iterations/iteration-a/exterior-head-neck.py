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
                # Slightly proud of the hood so panel edges catch light; the
                # curvature follows each corresponding ellipsoid cross-ring.
                scale = 1.042
                verts.append((math.sin(angle) * rx * scale,
                              cy - math.cos(angle) * ry * scale,
                              z + .003))
        faces = []
        for row in range(len(z_values) - 1):
            for col in range(across):
                a = row * (across + 1) + col
                faces.append((a, a + 1, a + across + 2, a + across + 1))
        patch = mk_mesh(name, verts, faces, mats['shell'], cranial_cover, region='head', role=role, edge=.0015)
        solid = patch.modifiers.new('Cranial panel wall', 'SOLIDIFY')
        solid.thickness = .007

        def attach_fastener(z, angle):
            cy, rx, ry = interpolate_ring(z)
            a = angle * side
            point = Vector((math.sin(a) * rx * 1.042,
                            cy - math.cos(a) * ry * 1.042,
                            z + .003))
            normal = Vector((math.sin(a) / max(rx, .02),
                             -math.cos(a) / max(ry, .02),
                             .24)).normalized()
            mk_rod(name + ' flush fastener', point - normal * .002, point + normal * .006,
                   .0045, mats['bearing'], cranial_cover, region='head', role='bearing', sides=10)

        attach_fastener(z_low + (z_high - z_low) * .16, angle_start + (angle_end-angle_start)*.5)
        attach_fastener(z_high - (z_high - z_low) * .16, angle_start + (angle_end-angle_start)*.5 + drift)
        return patch

    for side in (-1, 1):
        crown_patch('Cranial forward swept plate', side, .16, .68, [.045, .075, .110, .148, .181], .78)
        crown_patch('Cranial middle swept plate', side, .73, 1.28, [.060, .091, .127, .165, .198], .68)
        crown_patch('Cranial rear swept plate', side, 1.42, 1.98, [.084, .117, .151, .184, .211], .57)
        crown_patch('Cranial trailing overlap plate', side, 2.00, 2.42, [.075, .110, .148, .187, .216], .34)
    crown_patch('Cranial swept crest plate', 1, -.22, .22, [.058, .091, .126, .164, .202, .229], .58)

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
        (-.365, -.112, .018, .17),
        (-.337, -.129, .025, .19),
        (-.310, -.143, .018, .13),
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
    for triangle in tessellate_polygon([outline]):
        # Blender versions have returned both source indices and copied
        # vectors from tessellate_polygon; accept either representation.
        ids = [int(p) if isinstance(p, int) else outline_index[(round(p.x, 8), round(p.y, 8))]
               for p in triangle]
        faces.append(tuple(reversed(ids)))
        faces.append(tuple(last + i for i in ids))
    upper = mk_mesh('Upper bill deep convex forged hook', verts, faces, mats['bill'], upper_bill, region='bill', role='bill', edge=.002)
    for face in upper.data.polygons:
        face.use_smooth = True

    # Bind the contact landmark to the central foremost vertex of the actual
    # upper-bill mesh. It now follows the same articulated parent transforms.
    contact = bpy.data.objects['bill-contact']
    contact.parent = upper_bill
    contact.matrix_parent_inverse = Matrix.Identity(4)
    contact.location = (0.0, -.387 - .018 * .14, -.104)

    # A raised central ridge and restrained side seams reinforce a single
    # manufactured volume. These are designed divisions, not scratch marks.
    mk_tube('Bill central forged keel', [
        (0, -.123, .125), (0, -.194, .114), (0, -.257, .077),
        (0, -.309, .032), (0, -.354, -.051), (0, -.383, -.099),
    ], [.008, .010, .010, .008, .0045, .0015], mats['edge'], upper_bill, region='bill', role='edge', sides=8)
    for side in (-1, 1):
        # Three short formed seams break the broad side into forged cheek
        # planes without drawing continuous decorative scratches.
        mk_tube('Bill brow cheek seam', [
            (side * .086, -.126, .126), (side * .101, -.157, .124), (side * .111, -.186, .112),
        ], [.0035, .0035, .003], mats['bearing'], upper_bill, region='bill', role='bearing', sides=6)
        mk_tube('Bill middle cheek seam', [
            (side * .111, -.207, .105), (side * .108, -.237, .084), (side * .100, -.264, .063),
        ], [.0035, .0035, .003], mats['bearing'], upper_bill, region='bill', role='bearing', sides=6)
        mk_tube('Bill lower hook seam', [
            (side * .085, -.300, .038), (side * .067, -.326, -.008), (side * .045, -.349, -.052),
        ], [.003, .0028, .002], mats['bearing'], upper_bill, region='bill', role='bearing', sides=6)
        for y, z, x in [(-.151, .119, .108), (-.240, .082, .114)]:
            mk_rod('Bill cheek plate fastener', (side * x, y, z), (side * (x + .010), y, z),
                   .006, mats['bearing'], upper_bill, region='bill', role='bearing', sides=10)

    # A separate lower cutting jaw leaves a clear, dark negative-space gap to
    # the upper bill. It is attached to the authored jaw pivot.
    lower_verts = [
        (-.102, -.070, -.066), (.102, -.070, -.066),
        (.075, -.177, -.095), (-.075, -.177, -.095),
        (.014, -.263, -.104), (-.014, -.263, -.104),
        (-.060, -.127, -.080), (.060, -.127, -.080),
    ]
    lower_faces = [(0, 1, 7, 6), (6, 7, 2, 3), (3, 2, 4, 5), (0, 6, 3), (1, 2, 7), (3, 5, 4)]
    lower = mk_mesh('Lower jaw open forged cutting plate', lower_verts, lower_faces, mats['frame'], jaw, region='bill', role='frame', edge=.004)
    solid = lower.modifiers.new('Lower jaw forged wall thickness', 'SOLIDIFY')
    solid.thickness = .018

    # Compact S-curved neck frame. Three tapered elliptical shells wrap the
    # front and sides, following the curved centerline and leaving small
    # service gaps at each hinge instead of presenting bare fork rails.
    for side in (-1, 1):
        mk_tube('Cervical load-bearing side rail', [
            (side * .061, .012, .028), (side * .079, -.044, .124),
            (side * .071, -.119, .232), (side * .059, -.164, .335),
            (side * .047, -.198, .423),
        ], [.020, .023, .022, .020, .017], mats['frame'], neck, region='neck', role='frame', sides=12)
        mk_rod('Cervical lower cross-pin', (side * .050, .012, .025), (side * .091, .012, .025), .050, mats['bearing'], neck, region='neck', role='bearing', sides=24)
        mk_ring('Cervical lower bearing race', (side * .096, .012, .025), .044, .007, mats['edge'], neck, region='neck', role='edge', segments=24)
        mk_rod('Cervical upper cross-pin', (side * .035, -.198, .423), (side * .073, -.198, .423), .041, mats['bearing'], neck, region='neck', role='bearing', sides=24)
        mk_ring('Cervical upper bearing race', (side * .077, -.198, .423), .035, .006, mats['edge'], neck, region='neck', role='edge', segments=24)

    # Segment cross-rings follow the S-shaped axis; overlapping axial spans
    # keep the external form continuous while leaving the base service wedge.
    mk_loft('Cervical lower curved shingle', [
        (-.018, .016, .077, .078), (.002, .012, .097, .091),
        (.047, -.002, .111, .101), (.105, -.040, .116, .104),
        (.151, -.070, .105, .098), (.174, -.080, .084, .081),
    ], mats['shell'], neck, region='neck', role='shell', thickness=.014,
       segments=28, start=-math.pi / 2 + .40, span=math.tau - .80)
    mk_loft('Cervical middle curved shingle', [
        (.148, -.068, .077, .074), (.165, -.081, .100, .095),
        (.211, -.110, .111, .102), (.259, -.136, .102, .096),
        (.286, -.151, .083, .079),
    ], mats['shell'], neck, region='neck', role='shell', thickness=.014, segments=28)
    mk_loft('Cervical middle upper overlap shingle', [
        (.264, -.140, .070, .068), (.279, -.148, .090, .084),
        (.317, -.165, .101, .092), (.350, -.180, .094, .086),
        (.369, -.187, .076, .071),
    ], mats['frame'], neck, region='neck', role='frame', thickness=.012, segments=28)
    mk_loft('Cervical upper curved shingle', [
        (.346, -.179, .070, .068), (.361, -.185, .088, .083),
        (.388, -.196, .097, .089), (.414, -.199, .089, .082),
        (.429, -.200, .070, .066),
    ], mats['shell'], neck, region='neck', role='shell', thickness=.013, segments=28)

    # A short skull-attached socket overlaps the neck shingle across the top
    # hinge. Because it follows the head transform, the joint remains visibly
    # assembled as the neck and skull articulate independently.
    mk_loft('Skull cervical socket collar', [
        (-.090, .000, .073, .076), (-.078, .000, .095, .096),
        (-.043, .000, .100, .099), (-.018, .000, .084, .087),
        (.002, .000, .073, .077),
    ], mats['bearing'], head, region='head', role='bearing', thickness=.012, segments=28)

    # Three exposed restraint links follow the cervical curve. They are short
    # and local to the neck assembly, not a continuous flexible hose.
    for idx, (y, z, radius) in enumerate([(.018, .050, .023), (-.055, .160, .025), (-.145, .305, .021)]):
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
            'contactEnvelope': {'billLocalTip': (0.0, -.38952, -.104), 'profileStations': len(profile), 'verticalRange': (-.143, .140)},
            'designChoices': ['deep convex hooked bill', 'open cheek and mandible gap', 'curved hood panels', 'segmented cervical guards with a negative-X base service aperture'],
        }
    }
