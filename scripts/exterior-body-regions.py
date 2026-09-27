"""Inherited exterior regions for the structural MurderBird proposal.

Callable from the versioned Blender pipeline with ``build(ctx)``. Geometry is
intentionally regional and rigid: the selected images show surfaces and broad
silhouette cues, while hidden construction and exact fabrication remain proposals.
"""

import math


def build(ctx):
    bpy = ctx['bpy']
    Vector = ctx['Vector']
    mesh = ctx['mesh']
    rod = ctx['rod']
    tube = ctx['tube']
    loft = ctx['loft']
    plate = ctx['plate']
    under = ctx['under']
    delete_meshes = ctx['delete_meshes']
    mats = ctx['mats']

    bpy.context.view_layer.update()
    body = bpy.data.objects['body']
    chest = bpy.data.objects['breastplate']
    repair = bpy.data.objects['industrial-repairs']
    wings = {
        'left': (1, bpy.data.objects['left-mantle'], bpy.data.objects['left-wing-shield']),
        'right': (-1, bpy.data.objects['right-mantle'], bpy.data.objects['right-wing-shield']),
    }
    legs = {
        'left': (bpy.data.objects['left-thigh'], bpy.data.objects['left-shin'],
                 bpy.data.objects['left-foot'], bpy.data.objects['left-toes']),
        'right': (bpy.data.objects['right-thigh'], bpy.data.objects['right-shin'],
                  bpy.data.objects['right-foot'], bpy.data.objects['right-toes']),
    }
    created = []

    def mark(obj, region, role, eras='maker,mechanic,builder'):
        obj['region'] = region
        obj['surfaceRole'] = role
        obj['inherited'] = True
        obj['inheritedPart'] = 'structural-v1 body envelope'
        obj['exteriorEras'] = eras
        created.append(obj)
        return obj

    def smooth(obj):
        for face in obj.data.polygons:
            face.use_smooth = True
        return obj

    def localize(parent, points):
        inv = parent.matrix_world.inverted_safe()
        return [tuple(inv @ Vector(p)) for p in points]

    def world_rod(name, a, b, radius, parent, region, role='edge',
                  eras='maker,mechanic,builder'):
        la, lb = localize(parent, [a, b])
        obj = rod(name, la, lb, radius, mats[role], parent, 10)
        return mark(obj, region, role, eras)

    def custom_mesh(name, points, faces, parent, region, role, eras='maker,mechanic,builder'):
        obj = mesh(name, localize(parent, points), faces, mats[role], parent)
        return mark(obj, region, role, eras)

    def local_mesh(name, points, faces, parent, region, role,
                   eras='maker,mechanic,builder'):
        obj = mesh(name, points, faces, mats[role], parent)
        return mark(obj, region, role, eras)

    def world_elliptical_shell(name, profiles, start, span, parent, region='breast',
                               role='shell', thickness=.012, segments=36,
                               radial_offset=0.0, eras='maker,mechanic,builder'):
        """Closed, thin elliptical sector shell sampled in body/world coordinates."""
        outer = []
        inner = []
        for z, cy, rx, ry in profiles:
            orow = []
            irow = []
            for i in range(segments + 1):
                t = start + span * i / segments
                sn, cs = math.sin(t), math.cos(t)
                orow.append((sn * (rx + radial_offset),
                             cy - cs * (ry + radial_offset), z))
                irow.append((sn * max(.001, rx + radial_offset - thickness),
                             cy - cs * max(.001, ry + radial_offset - thickness), z))
            outer.append(orow)
            inner.append(irow)
        nr = len(profiles)
        stride = segments + 1
        pts = [p for row in outer for p in row] + [p for row in inner for p in row]
        faces = []
        layer = nr * stride
        for j in range(nr - 1):
            for i in range(segments):
                a = j * stride + i
                faces.append((a, a + 1, a + stride + 1, a + stride))
                b = layer + a
                faces.append((b + stride, b + stride + 1, b + 1, b))
        # Close the swept ends and both profile ends so Solidify is unnecessary.
        for j in range(nr - 1):
            for i in (0, segments):
                a = j * stride + i
                faces.append((a, a + stride, layer + a + stride, layer + a))
        for i in range(segments):
            a = i
            b = (nr - 1) * stride + i
            faces.append((a, a + 1, layer + a + 1, layer + a))
            faces.append((b, layer + b, layer + b + 1, b + 1))
        return smooth(custom_mesh(name, pts, faces, parent, region, role, eras))

    def add_panel_patch(name, profiles, z0, z1, a0, a1, parent, region='breast',
                        role='edge', lift=.008, eras='maker,mechanic,builder'):
        """A shallow, tapered, conforming panel over an elliptical shell sector."""
        rows, cols = 6, 6
        pts = []
        for layer in (0, 1):
            for j in range(rows + 1):
                z = z0 + (z1 - z0) * j / rows
                lo = profiles[0]
                hi = profiles[-1]
                for k in range(len(profiles) - 1):
                    if profiles[k][0] <= z <= profiles[k + 1][0]:
                        lo, hi = profiles[k], profiles[k + 1]
                        break
                f = 0 if hi[0] == lo[0] else (z - lo[0]) / (hi[0] - lo[0])
                cy = lo[1] + (hi[1] - lo[1]) * f
                rx = lo[2] + (hi[2] - lo[2]) * f
                ry = lo[3] + (hi[3] - lo[3]) * f
                taper = .92 + .08 * math.sin(math.pi * j / rows) ** .7
                for i in range(cols + 1):
                    amid = (a0 + a1) * .5
                    a = amid + (a0 + (a1 - a0) * i / cols - amid) * taper
                    pad = lift if layer == 0 else lift - .006
                    pts.append((math.sin(a) * (rx + pad),
                                cy - math.cos(a) * (ry + pad),
                                z))
        stride = cols + 1
        layer_size = (rows + 1) * stride
        faces = []
        for j in range(rows):
            for i in range(cols):
                k = j * stride + i
                faces.append((k, k + 1, k + stride + 1, k + stride))
                q = layer_size + k
                faces.append((q + stride, q + stride + 1, q + 1, q))
        perimeter = (list(range(stride))
                     + [j * stride + cols for j in range(1, rows + 1)]
                     + list(range(rows * stride + cols - 1, rows * stride - 1, -1))
                     + [j * stride for j in range(rows - 1, 0, -1)])
        for a, b in zip(perimeter, perimeter[1:] + perimeter[:1]):
            faces.append((a, b, b + layer_size, a + layer_size))
        obj = custom_mesh(name, pts, faces, parent, region, role, eras)
        # Keep the gently curved plate faces smooth, but leave the narrow
        # thickness walls crisp so the panel reads as fitted metal, not padding.
        for i, polygon in enumerate(obj.data.polygons):
            polygon.use_smooth = i < rows * cols * 2
        return obj

    def local_shell(name, profiles, parent, region, role='shell', start=-1.30,
                    span=2.60, thickness=.012, segments=20,
                    eras='maker,mechanic,builder', center_x=0,
                    smooth_faces=True):
        # Same closed sector generator in parent-local coordinates.
        outer, inner = [], []
        for z, cy, rx, ry in profiles:
            outer.append([(center_x + math.sin(start + span * i / segments) * rx,
                           cy - math.cos(start + span * i / segments) * ry, z)
                          for i in range(segments + 1)])
            inner.append([(center_x + math.sin(start + span * i / segments) * max(.001, rx - thickness),
                           cy - math.cos(start + span * i / segments) * max(.001, ry - thickness), z)
                          for i in range(segments + 1)])
        nr, stride = len(profiles), segments + 1
        pts = [p for row in outer for p in row] + [p for row in inner for p in row]
        layer = nr * stride
        faces = []
        for j in range(nr - 1):
            for i in range(segments):
                a = j * stride + i
                faces.extend([(a, a + 1, a + stride + 1, a + stride),
                              (layer + a + stride, layer + a + stride + 1,
                               layer + a + 1, layer + a)])
            for i in (0, segments):
                a = j * stride + i
                faces.append((a, a + stride, layer + a + stride, layer + a))
        for i in range(segments):
            a, b = i, (nr - 1) * stride + i
            faces.extend([(a, a + 1, layer + a + 1, layer + a),
                          (b, layer + b, layer + b + 1, b + 1)])
        obj = local_mesh(name, pts, faces, parent, region, role, eras)
        return smooth(obj) if smooth_faces else obj

    def local_extruded_polygon(name, outline, thickness, parent, region, role,
                               eras='maker,mechanic,builder', axis='y', center=0):
        """Tidy rigid shield from a 2D outline, extruded along local X or Y."""
        n = len(outline)
        pts = []
        for side in (-.5, .5):
            for a, b in outline:
                if axis == 'y':
                    pts.append((a, side * thickness, b))
                else:
                    pts.append((center + side * thickness, a, b))
        faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
        for i in range(n):
            faces.append((i, (i + 1) % n, (i + 1) % n + n, i + n))
        obj = local_mesh(name, pts, faces, parent, region, role, eras)
        bevel = ctx.get('bevel')
        if bevel:
            bevel(obj, .003)
        return obj

    def rounded_side_cap(name, side, parent, region='shoulder', role='shell',
                         center=(0, .045, -.05), radius_y=.12, radius_z=.085):
        """Curved outer-face shoulder cap outside the unchanged hinge axle."""
        cy, cz = center[1], center[2]
        rings = 5
        seg = 20
        outer = [(side * .135, cy, cz)]
        inner = [(side * .126, cy, cz)]
        for r in range(1, rings + 1):
            f = r / rings
            for i in range(seg):
                a = math.tau * i / seg
                y = cy + math.cos(a) * radius_y * f
                z = cz + math.sin(a) * radius_z * f
                dome = .020 * (1 - f * f)
                outer.append((side * (.112 + dome), y, z))
                inner.append((side * (.105 + dome), y, z))
        nouter = len(outer)
        pts = outer + inner
        faces = []
        for layer in (0, 1):
            base = layer * nouter
            first = base + 1
            for i in range(seg):
                tri = (base, first + i, first + (i + 1) % seg)
                faces.append(tri if layer == 0 else tuple(reversed(tri)))
            for ring_idx in range(1, rings):
                a0 = 1 + (ring_idx - 1) * seg
                a1 = 1 + ring_idx * seg
                for i in range(seg):
                    q = (i + 1) % seg
                    f = (base + a0 + i, base + a0 + q,
                         base + a1 + q, base + a1 + i)
                    faces.append(f if layer == 0 else tuple(reversed(f)))
        # Join rim and center thickness. The axle remains visible inside this cap.
        for i in range(seg):
            a = 1 + (rings - 1) * seg + i
            b = 1 + (rings - 1) * seg + (i + 1) % seg
            faces.append((a, b, b + nouter, a + nouter))
        obj = local_mesh(name, pts, faces, parent, region, role)
        return smooth(obj)

    def wing_shell_panel(name, outline, profiles, side, parent, role='shell',
                         center_x=0, layer_offset=0):
        """Tessellated raised panel projected onto the convex outward surface."""
        def cross_section(z):
            a, b = profiles[0], profiles[-1]
            for i in range(len(profiles) - 1):
                if profiles[i][0] <= z <= profiles[i + 1][0]:
                    a, b = profiles[i], profiles[i + 1]
                    break
            f = 0 if b[0] == a[0] else (z - a[0]) / (b[0] - a[0])
            cy = a[1] + (b[1] - a[1]) * f
            rx = a[2] + (b[2] - a[2]) * f
            ry = a[3] + (b[3] - a[3]) * f
            return cy, rx, ry
        zmin, zmax = profiles[0][0], profiles[-1][0]
        if any(z < zmin - .001 or z > zmax + .001 for _, z in outline):
            raise ValueError(name + ' extends beyond its projected shell profile')

        def project(y, z, outward):
            cy, rx, ry = cross_section(z)
            q = max(-.97, min(.97, (y - cy) / max(ry, .001)))
            x = center_x + side * (math.sqrt(max(.001, 1 - q * q)) * rx + outward)
            return (x, y, z)

        # A fan of small triangles is subdivided before projection. This makes
        # every interior vertex follow the convex shell instead of allowing a
        # flat n-gon chord to sink through the backing at its center.
        center = (sum(y for y, _ in outline) / len(outline),
                  sum(z for _, z in outline) / len(outline))
        outer_pts, inner_pts, outer_faces, inner_faces, wall_edges = [], [], [], [], []
        vertex_map = {}
        edge_subdivisions = 4
        for edge in range(len(outline)):
            a = center
            b = outline[edge]
            c = outline[(edge + 1) % len(outline)]
            index = {}
            for i in range(edge_subdivisions + 1):
                for j in range(edge_subdivisions + 1 - i):
                    wb, wc = i / edge_subdivisions, j / edge_subdivisions
                    wa = 1 - wb - wc
                    y = a[0] * wa + b[0] * wb + c[0] * wc
                    z = a[1] * wa + b[1] * wb + c[1] * wc
                    key = (round(y, 7), round(z, 7))
                    if key not in vertex_map:
                        vertex_map[key] = len(outer_pts)
                        outer_pts.append(project(y, z, .016 + layer_offset))
                        inner_pts.append(project(y, z, .013 + layer_offset))
                    index[(i, j)] = vertex_map[key]
            for i in range(edge_subdivisions):
                for j in range(edge_subdivisions - i):
                    tri = (index[(i, j)], index[(i + 1, j)], index[(i, j + 1)])
                    outer_faces.append(tri)
                    inner_faces.append(tri)
                    if i + j < edge_subdivisions - 1:
                        tri2 = (index[(i + 1, j)], index[(i + 1, j + 1)],
                                index[(i, j + 1)])
                        outer_faces.append(tri2)
                        inner_faces.append(tri2)
            # The B-C edge of each fan triangle is an actual panel boundary.
            rim = [index[(i, edge_subdivisions - i)]
                   for i in range(edge_subdivisions + 1)]
            for k in range(edge_subdivisions):
                wall_edges.append((rim[k], rim[k + 1]))

        core_count = len(outer_pts)
        pts = outer_pts + inner_pts
        faces = outer_faces + [tuple(core_count + k for k in reversed(face))
                               for face in inner_faces]
        for a, b in wall_edges:
            faces.append((a, b, core_count + b, core_count + a))
        first = outer_faces[0]
        normal = (Vector(pts[first[1]]) - Vector(pts[first[0]])).cross(
            Vector(pts[first[2]]) - Vector(pts[first[0]]))
        if normal.x * side < 0:
            faces = [tuple(reversed(face)) for face in faces]
        obj = local_mesh(name, pts, faces, parent, 'wing', role)
        for i, polygon in enumerate(obj.data.polygons):
            polygon.use_smooth = i < len(outer_faces) + len(inner_faces)
        bevel = ctx.get('bevel')
        if bevel:
            bevel(obj, .0015)
        return obj

    def mantle_leaf(name, profiles, side, parent, angle, top, length, layer):
        """A short swept armor leaf, sampled on the actual shoulder envelope."""
        def surface(theta, z, offset):
            a, b = profiles[0], profiles[-1]
            for lo, hi in zip(profiles, profiles[1:]):
                if lo[0] <= z <= hi[0]:
                    a,b=lo,hi;break
            f=(z-a[0])/(b[0]-a[0])
            cy,rx,ry=[a[k]+(b[k]-a[k])*f for k in (1,2,3)]
            return Vector((side*(.025+math.sin(theta)*(rx+offset)),
                           cy-math.cos(theta)*(ry+offset),z))
        rows,cols=4,4
        taper=[.72,1,.80,.40,.055]
        outside=.014+layer*.007
        pts=[]
        for offset in (outside,outside-.003):
            for j in range(rows+1):
                t=j/rows
                for i in range(cols+1):
                    theta=angle+.17*t+(i/cols-.5)*.56*taper[j]
                    pts.append(tuple(surface(theta,top-length*t,offset)))
        stride=cols+1;n=(rows+1)*stride;faces=[]
        for j in range(rows):
            for i in range(cols):
                k=j*stride+i
                faces.append((k,k+1,k+stride+1,k+stride))
                faces.append((n+k+stride,n+k+stride+1,n+k+1,n+k))
        wall_start=len(faces)
        perimeter=list(range(stride))+[j*stride+cols for j in range(1,rows+1)]+list(range(rows*stride+cols-1,rows*stride-1,-1))+[j*stride for j in range(rows-1,0,-1)]
        for a,b in zip(perimeter,perimeter[1:]+perimeter[:1]):faces.append((a,b,n+b,n+a))
        normal=(Vector(pts[1])-Vector(pts[0])).cross(Vector(pts[stride+1])-Vector(pts[0]))
        if normal.dot(Vector((side*math.sin(angle),-math.cos(angle),0)))<0:
            faces=[tuple(reversed(f)) for f in faces]
        obj=local_mesh(name,pts,faces,parent,'shoulder','shell')
        for index,p in enumerate(obj.data.polygons):p.use_smooth=index<wall_start
        for shift in (-.11,.11):
            theta=angle+shift
            p=surface(theta,top-.012,outside+.001)
            direction=Vector((side*math.sin(theta),-math.cos(theta),0)).normalized()
            fastener=rod(name+' peened pin',p-direction*.002,p+direction*.003,
                         .0035,mats['bearing'],parent,8)
            mark(fastener,'shoulder','bearing')
        return obj

    # Remove only the former exterior skins. Passive frames, hinges, rails,
    # bearings, wing links, leg pivots and inner assemblies stay in place.
    prefixes = (
        'Structural breast formed cover', 'Breast broad structural lamella',
        'Rear formed structural shell', 'Rear broad structural lamella',
        'Shoulder protective shell', 'Shoulder mantle scale',
        'Forewing shield backplate', 'Tucked forewing shield scale',
        'Folded forewing spar', 'Forewing return rail', 'Thigh overlapping guard',
    )
    delete_meshes(lambda o: o.name.startswith(prefixes))
    delete_meshes(lambda o: under(o, repair))
    # These two legacy thigh shells are uniform heavy tubes retained from the
    # presence blockout, not load-bearing rails. Remove only the exact mesh
    # objects; the thigh pivots and paired passive load rails remain untouched.
    delete_meshes(lambda o: o.type == 'MESH' and o.name in {'left thigh', 'right thigh'})
    bpy.context.view_layer.update()

    # Broad breast access shell: full breast volume, waist narrowing and a
    # rounded top into the shoulder bridge. The separate back stays passive.
    breast = [
        (.965, .025, .170, .205),
        (1.035, .008, .235, .285),
        (1.155, -.006, .305, .365),
        (1.285, -.004, .295, .365),
        (1.400, .012, .245, .305),
        (1.485, .035, .155, .215),
    ]
    world_elliptical_shell('Shaped breastplate access shell', breast,
                           -math.pi / 2, math.pi, chest, 'breast', 'shell', .014, 40)
    # Four staggered armor courses use irregularly offset fitted panels. Each
    # seam breaks against the course above/below, avoiding ruler-straight rows
    # while keeping the broad plate scale of the selected full-body reference.
    breast_bands = [
        (1.405, .125, [(-1.18, -.48, -.010), (-.54, .13, .018),
                       (.08, .72, -.012), (.66, 1.19, .010)]),
        (1.300, .150, [(-1.22, -.70, .018), (-.76, -.13, -.018),
                       (-.18, .48, .008), (.43, 1.20, -.006)]),
        (1.185, .160, [(-1.21, -.74, -.018), (-.80, -.16, .014),
                       (-.22, .43, -.010), (.37, 1.20, .020)]),
        (1.070, .150, [(-1.10, -.53, .015), (-.59, .06, -.014),
                       (.02, .67, .012), (.62, 1.10, -.008)]),
    ]
    plate_index = 0
    for band, (center_z, height, spans) in enumerate(breast_bands, 1):
        for column, (a0, a1, shift) in enumerate(spans, 1):
            plate_index += 1
            inset = .010 + .002 * ((band + column) % 3)
            lift = .011 + .002 * ((band * 2 + column) % 3)
            add_panel_patch('Breast fitted overlap plate ' + str(plate_index),
                            breast, center_z - height * .5 + shift + inset,
                            center_z + height * .5 + shift - inset, a0, a1,
                            chest, 'breast', 'shell', lift)

    def front_y(z, x):
        a, b = breast[0], breast[-1]
        for i in range(len(breast) - 1):
            if breast[i][0] <= z <= breast[i + 1][0]:
                a, b = breast[i], breast[i + 1]
                break
        f = 0 if b[0] == a[0] else (z - a[0]) / (b[0] - a[0])
        cy = a[1] + (b[1] - a[1]) * f
        rx = a[2] + (b[2] - a[2]) * f
        ry = a[3] + (b[3] - a[3]) * f
        q = min(.94, abs(x) / rx)
        return cy - ry * math.sqrt(1 - q * q)

    # Sparse service fasteners at panel margins; size remains subordinate to
    # armor breaks and they are actual rigid edge-role meshes.
    for z, xoff in ((1.085, .135), (1.245, .215), (1.345, .165)):
        for side in (-1, 1):
            x = side * xoff
            y = front_y(z, x)
            world_rod('Breast fitted panel peened fastener',
                      (x, y - .025, z), (x, y - .016, z), .006,
                      chest, 'breast', 'edge')

    # Closed posterior cover and a narrow spine guard. Keep the pelvis region
    # visibly narrower than the breast; do not turn it into another barrel.
    back_profiles = [
        (.930, .100, .185, .205), (1.035, .095, .248, .285),
        (1.165, .085, .290, .350), (1.305, .070, .268, .340),
        (1.415, .045, .205, .270), (1.475, .040, .135, .190),
    ]
    world_elliptical_shell('Dorsal and rump fitted armor', back_profiles,
                           math.pi / 2, math.pi, body, 'back', 'shell', .014, 36)
    # Compact flared hip caps finish the waist transition while staying above
    # the actual thigh rotation centers.
    pelvis_profiles = [
        (.875, .055, .145, .130), (.920, .045, .225, .180),
        (.975, .035, .238, .195), (1.015, .025, .195, .160),
    ]
    world_elliptical_shell('Pelvic saddle transition', pelvis_profiles,
                           -math.pi / 2, math.tau, body, 'pelvis', 'shell', .012, 32)

    # A shaped shoulder bridge rim closes the broad top opening while keeping
    # a deliberate neck clearance. It follows the existing neck root; no pivot
    # or neck transform is moved here.
    throat_rim = ctx['ring']('Breast-to-neck shoulder bridge rim',
                             (0, -.095, .565), .125, .018,
                             mats['shell'], body, 'Z', 48)
    throat_rim.scale = (1.12, 1.0, 1.0)
    mark(throat_rim, 'breast', 'shell')
    for side, label in ((1, 'left'), (-1, 'right')):
        # Small side windows leave the hip shaft visible; the armor ends above
        # the joint rather than bridging across the independent leg pivot.
        outline = [
            (side * .155, .995), (side * .238, 1.015), (side * .292, 1.075),
            (side * .276, 1.145), (side * .212, 1.178), (side * .170, 1.115),
        ]
        # Convert a world X/Z outline panel into body-local coordinates and
        # keep its front-facing depth shallow and inside the breast silhouette.
        pts = []
        for y in (-.112, -.096):
            pts.extend([(x, y, z - .90) for x, z in outline])
        faces = [tuple(reversed(range(len(outline)))), tuple(range(len(outline), 2 * len(outline)))]
        for i in range(len(outline)):
            faces.append((i, (i + 1) % len(outline), (i + 1) % len(outline) + len(outline), i + len(outline)))
        local_mesh(label.title() + ' hip transition guard', pts, faces,
                   body, 'pelvis', 'shell')

    # Compact, domed outer shoulder caps stay close to the inherited axle.
    # Forewing shells fold down and rearward from the unchanged elbow pivots.
    for label, (side, mantle, shield) in wings.items():
        rounded_side_cap(label.title() + ' curved shoulder mantle', side, mantle,
                         'shoulder', 'shell', center=(0, .025, -.025),
                         radius_y=.075, radius_z=.070)
        # Broad upper and lower mantle sheets wrap the outside and rear of the
        # shoulder drum. Separate pieces leave a deliberate window at the
        # bearing center; the forewing remains a second rigid assembly.
        shoulder_profiles = [
            (-.320, .060, .145, .165),
            (-.245, .055, .170, .190),
            (-.165, .045, .180, .195),
            (-.075, .030, .165, .175),
            (.055, .020, .140, .155),
            (.110, .010, .105, .180),
            (.130, .010, .002, .002),
        ]
        outside_half = 0 if side > 0 else math.pi
        local_shell(label.title() + ' upper shoulder mantle shell', [
                        (-.075, .030, .165, .175),
                        (.055, .020, .140, .155),
                        (.110, .010, .105, .180),
                        (.130, .010, .002, .002),
                    ], mantle, 'shoulder', 'shell', outside_half, math.pi,
                    .014, 20, center_x=side * .025)
        local_shell(label.title() + ' lower shoulder mantle shell', [
                        (-.320, .060, .145, .165),
                        (-.245, .055, .170, .190),
                        (-.165, .045, .180, .195),
                        (-.075, .030, .165, .175),
                    ], mantle, 'shoulder', 'shell', outside_half, math.pi,
                    .014, 20, center_x=side * .025)
        # Only the flightless mantle receives these compact directional leaves.
        # Their seven-millimetre layer steps clear the three-millimetre walls;
        # every leaf belongs to this shoulder, never to both sides of an elbow.
        for row,(top,length) in enumerate([(.112,.120),(.014,.130),(-.088,.130),(-.190,.125)]):
            for column,angle in enumerate([.32,.88,1.44,2.00,2.56]):
                mantle_leaf(label.title()+' upper-arm overlap '+str(row*5+column+1),
                            shoulder_profiles,side,mantle,angle,top,length,3-row)

        # Parent-local section centers follow the original elbow spar, but the
        # new armor tucks down/rearward rather than extending up and forward.
        shield_profiles = [
            (-.220, .165, .125, .145),
            (-.155, .130, .165, .180),
            (-.080, .080, .185, .200),
            (-.040, .045, .145, .165),
            (.045, -.015, .135, .150),
            (.105, -.050, .105, .125),
            (.145, -.070, .075, .095),
            (.160, -.070, .002, .002),
        ]
        # Keep the elbow's bearing face visible: lower and upper shells stop
        # on either side of the pivot, with the mantle above carrying the
        # silhouette into the shoulder.
        local_shell(label.title() + ' lower folded forewing shield',
                    shield_profiles[:4], shield, 'wing', 'shell',
                    outside_half, math.pi, .016, 20,
                    center_x=side * .035)
        local_shell(label.title() + ' upper folded forewing shield',
                    shield_profiles[4:], shield, 'wing', 'shell',
                    outside_half, math.pi, .014, 18,
                    center_x=side * .035)

        # Rebuild, rather than retain, the obsolete upward/front-facing spars.
        # These two passive members terminate at the same elbow assembly and
        # follow its compact downward/rearward armor envelope.
        tube(label.title() + ' tucked forewing load spar',
             [(0, -.006, .003), (-side * .035, .060, -.042),
              (-side * .050, .145, -.112), (-side * .042, .220, -.158)],
             [.034, .029, .024, .015], mats['frame'], shield, 10)
        tube(label.title() + ' tucked forewing return rail',
             [(side * .050, .006, -.004), (side * .026, .075, -.052),
              (side * .012, .158, -.120), (side * .018, .220, -.154)],
             [.015, .013, .010, .006], mats['bearing'], shield, 8)
        for o in list(shield.children):
            if o.name.startswith((label.title() + ' tucked forewing load spar',
                                  label.title() + ' tucked forewing return rail')):
                mark(o, 'wing', 'frame' if 'load spar' in o.name else 'bearing')

        # Broad upper and lower cover leaves shield the spars without closing
        # over the elbow bearing itself.
        for i, outline in enumerate([
            [(-.150, .145), (-.100, .155), (-.015, .120), (.020, .075),
             (.005, .045), (-.080, .065), (-.140, .095)],
            [(.015, -.045), (.075, -.035), (.195, -.075), (.275, -.130),
             (.235, -.175), (.110, -.145), (.005, -.105)],
        ], 1):
            wing_shell_panel(label.title() + ' curved forewing guard ' + str(i),
                             outline, shield_profiles, side, shield,
                             'edge' if i == 1 else 'shell',
                             center_x=side * .035, layer_offset=.030)

        # Six broad, overlapping mechanical-feather plates sweep down/rearward.
        # Their long axes and changing widths read as a folded wing, not a row
        # of tiny trim scales around the axle drum.
        vane_specs = [
            (-.045, -.155, .220, .090),
            (-.005, -.145, .230, .105),
            (.045, -.125, .170, .100),
            (.085, -.100, .175, .090),
            (.020, -.175, .200, .070),
            (.035, -.170, .220, .080),
        ]
        for i, (y0, z0, length, width) in enumerate(vane_specs, 1):
            outline = [
                (y0, z0 + width * .12),
                (y0 + length * .20, z0 + width * .62),
                (y0 + length * .72, z0 + width * .38),
                (y0 + length, z0 - width * .10),
                (y0 + length * .58, z0 - width * .58),
                (y0 + length * .12, z0 - width * .34),
            ]
            wing_shell_panel(label.title() + ' tapered trailing wing plate ' + str(i),
                             outline, shield_profiles, side, shield,
                             'shell' if i % 3 else 'edge',
                             center_x=side * .035, layer_offset=(6-i)*.004)

    # Rigid tapered leg guards follow the actual hip/knee/ankle parents.
    # Their open rear sectors leave load rails and bearings inspectable.
    for label, (thigh, shin, foot, toes) in legs.items():
        thigh_dz = shin.location.z
        thigh_slope = shin.location.y / thigh_dz if abs(thigh_dz) > 1e-5 else 0.0
        shin_dz = foot.location.z
        shin_slope = foot.location.y / shin_dz if abs(shin_dz) > 1e-5 else 0.0
        local_shell(label.title() + ' fitted thigh guard', [
            (-.292, thigh_slope * -.292, .040, .032),
            (-.240, thigh_slope * -.240, .046, .036),
            (-.105, thigh_slope * -.105, .050, .038),
            (-.035, thigh_slope * -.035, .042, .032),
        ], thigh, 'leg', 'shell', -1.12, 2.24, .008, 16,
                    smooth_faces=False)
        local_shell(label.title() + ' fitted shin guard', [
            (-.270, shin_slope * -.270, .032, .028),
            (-.222, shin_slope * -.222, .038, .032),
            (-.105, shin_slope * -.105, .042, .034),
            (-.030, shin_slope * -.030, .035, .028),
        ], shin, 'leg', 'shell', -1.18, 2.36, .007, 16,
                    smooth_faces=False)
        # A small plate over each toe keeps the compact mechanical bird foot
        # mass readable. Front talon tips remain uncovered and floor clear.
        for toe, x in enumerate((-.078, 0, .078), 1):
            o = plate(label.title() + ' toe sheath ' + str(toe),
                      (x, -.112, .050), .052 if toe != 2 else .058, .132,
                      mats['edge'], toes, (0, 0, 0))
            mark(o, 'foot', 'edge')

    # Refit the anatomical-left repair as a later replacement around the same
    # shoulder landmark. Parent eligibility keeps Maker free of later repairs.
    left_mantle = wings['left'][1]
    for z, shift in ((.115, -.015), (.055, .022)):
        a = (-.012, .045 + shift, z)
        b = (.125, .115 + shift, z - .035)
        o = rod('Left industrial shoulder replacement brace', a, b, .018,
                mats['repair'], repair, 10)
        mark(o, 'shoulder', 'repair', 'mechanic,builder')
        for i, (x, y, zz) in enumerate((a, b)):
            bolt = rod('Left repair peened bolt ' + str(i + 1),
                       (x, y - .014, zz), (x, y + .014, zz), .012,
                       mats['edge'], repair, 10)
            mark(bolt, 'shoulder', 'edge', 'mechanic,builder')
    # One quiet Builder-era service plate conforms to the outward shoulder
    # mantle instead of floating beyond its surface. Keep it below the pivot
    # center so it does not mask the bearing face.
    advanced = wing_shell_panel(
        'Left advanced shoulder service plate',
        [(-.005, -.115), (.018, -.055), (.073, -.040),
         (.098, -.082), (.048, -.135)],
        shoulder_profiles, 1, left_mantle, 'repair', center_x=.025)
    mark(advanced, 'shoulder', 'repair', 'builder')

    bpy.context.view_layer.update()
    return {
        'status': 'inherited regional exterior proposal; visual review pending',
        'references': {
            'candidate03': 'Full-body envelope, layered near wing, breast and floor-supported bird stance.',
            'makerClean': 'Ancient-era mass and folded ornamental wing treatment; illustration only.',
            'mechanic': 'Repair and support context; not a mechanism drawing.',
            'heart': 'Open chest/pale cylinder visual; no topology inferred.',
        },
        'regions': sorted({o.get('region') for o in created}),
        'createdObjects': len(created),
        'clearanceNotes': [
            'Shoulder shield begins outside the existing shoulder axle envelope.',
            'Forewing sector starts above the elbow pivot and leaves the pin ring exposed.',
            'Thigh and shin guards end short of the hip, knee, and ankle hinge planes.',
            'Toe sheaths stop behind the talon tips and do not define the ground contact plane.',
        ],
        'uncertainties': [
            'Armor seams, shell thickness, hidden backs and surface construction are proposed.',
            'The selected illustrations do not establish exact panel topology or fabrication.',
        ],
    }
