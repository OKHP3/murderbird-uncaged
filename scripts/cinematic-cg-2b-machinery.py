"""CG2b exposed flank transmission and folded-wing bearings.

Runs after the CG2b body and wing modules. Adds separate editable UV meshes;
existing object geometry, transforms, visibility and material graphs are read-only.
Construction is a visual proposal inferred from the pinned composite, not engineering.
"""
import math
import bpy
from mathutils import Vector


def apply(scene, scaffold_path=None, era='builder'):
    if any(o.get('cg2bMachinery') for o in scene.objects):
        return {'module': 'cg2b-machinery', 'disposition': 'already applied; no duplicate construction'}
    if not any(o.get('cg2bBodyOwner') for o in scene.objects):
        raise RuntimeError('Apply the CG2b open-bay body before machinery')
    if not any(o.get('cg2bWing') for o in scene.objects):
        raise RuntimeError('Apply the CG2b folded wing before its root bearings')

    mats = {}
    for o in scene.objects:
        if o.type == 'MESH' and o.data.materials:
            mats.setdefault(o.get('surfaceRole'), o.data.materials[0])
    for m in bpy.data.materials:
        if m.get('cg2aEra') == era:
            role = {'armor': 'armor', 'steel': 'steel', 'bronze': 'rivet', 'machinery': 'inner'}.get(m.get('cg2aFamily'))
            if role:
                mats[role] = m
    for role, fallback in {'edge': 'steel', 'bearing': 'steel', 'shaft': 'steel', 'armor': 'plate'}.items():
        if role not in mats:
            mats[role] = mats.get(fallback, mats.get('inner'))
    coll = bpy.data.collections.new('CG2b exposed flank and wing-root machinery')
    scene.collection.children.link(coll)
    made = []
    counts = {}

    def mesh(name, verts, faces, uv, role='inner', region='body', side='left', smooth=True):
        d = bpy.data.meshes.new(name)
        d.from_pydata([tuple(v) for v in verts], [], faces)
        d.update()
        o = bpy.data.objects.new('CG2b ' + side + ' ' + name, d)
        coll.objects.link(o)
        o['cg1cRegion'] = region
        o['cg2bRegion'] = region
        o['cg2bMachinery'] = True
        o['machinerySide'] = side
        o['surfaceRole'] = role
        o['exteriorEras'] = 'maker,mechanic,builder'
        o['detailStatus'] = 'Pinned-canon visible construction proposal; no engineering claim'
        if mats.get(role):
            d.materials.append(mats[role])
        layer = d.uv_layers.new(name='CG2b separate machinery UV')
        for f in d.polygons:
            f.use_smooth = smooth
            for li in f.loop_indices:
                layer.data[li].uv = uv[d.loops[li].vertex_index]
        made.append(o)
        counts[role] = counts.get(role, 0) + 1
        return o

    def frame(axis):
        axis = Vector(axis).normalized()
        u = axis.cross(Vector((0, 0, 1)))
        if u.length < .01:
            u = axis.cross(Vector((0, 1, 0)))
        u.normalize()
        return axis, u, axis.cross(u).normalized()

    def tube(name, points, radius, role='inner', region='body', side='left', n=12, cap=True):
        points = [Vector(p) for p in points]
        verts = []; uv = []; faces = []
        length = sum((b-a).length for a, b in zip(points, points[1:]))
        travelled = 0
        for j, p in enumerate(points):
            if j:
                travelled += (p-points[j-1]).length
            axis = points[min(j+1, len(points)-1)] - points[max(0, j-1)]
            _, u, v = frame(axis)
            r = radius[j] if isinstance(radius, (list, tuple)) else radius
            for i in range(n):
                a = math.tau * i/n
                verts.append(p+r*(u*math.cos(a)+v*math.sin(a)))
                uv.append((i/n, travelled/max(length, .0001)))
        for j in range(len(points)-1):
            for i in range(n):
                faces.append((j*n+i, j*n+(i+1)%n, (j+1)*n+(i+1)%n, (j+1)*n+i))
        if cap:
            faces.extend([tuple(reversed(range(n))), tuple(range((len(points)-1)*n, len(points)*n))])
        o = mesh(name, verts, faces, uv, role, region, side)
        if cap:
            # Split the end-face normals: a machined pin is not a chrome ball.
            for f in o.data.polygons[-2:]:
                f.use_smooth = False
        return o

    def annulus(name, c, axis, outer, inner, depth, role='bearing', region='body', side='left', n=48, teeth=0):
        c = Vector(c); a, u, v = frame(axis)
        verts = []; uv = []
        # Real open centre and separate rims: no painted discs.
        for axial, base in ((-depth/2, outer), (depth/2, outer), (-depth/2, inner), (depth/2, inner)):
            for i in range(n):
                t = math.tau*i/n
                r = base
                if teeth and base == outer:
                    r *= 1.0 if i % 4 in (1, 2) else .90
                verts.append(c+a*axial+(u*math.cos(t)+v*math.sin(t))*r)
                uv.append((i/n, 0 if axial < 0 else 1))
        faces = []
        for i in range(n):
            j = (i+1)%n
            faces.extend([(i, j, n+j, n+i), (2*n+j, 2*n+i, 3*n+i, 3*n+j),
                          (j, i, 2*n+i, 2*n+j), (n+i, n+j, 3*n+j, 3*n+i)])
        o = mesh(name, verts, faces, uv, role, region, side)
        # Axial faces stay flat; only the circular inner/outer walls are smooth.
        for i, f in enumerate(o.data.polygons):
            if i % 4 in (2, 3):
                f.use_smooth = False
        return o

    def joint(name, p, axis, r, side, region='body'):
        p = Vector(p); axis = Vector(axis).normalized()
        tube(name+' pin', [p-axis*.010, p+axis*.012], r*.45, 'shaft', region, side, 16)
        annulus(name+' lug', p, axis, r, r*.47, .006, 'inner', region, side, 32)
        annulus(name+' cap rim', p+axis*.009, axis, r*.76, r*.48, .002, 'edge', region, side, 32)
        tube(name+' captive hex', [p+axis*.010, p+axis*.013], r*.31, 'rivet', region, side, 6)

    def piston(name, p, q, r, side):
        p = Vector(p); q = Vector(q); d = q-p; a = d.normalized()
        tube(name+' dark barrel', [p+d*.08, p+d*.54], r, 'inner', 'body', side, 16)
        tube(name+' burnished ram', [p+d*.47, p+d*.94], r*.48, 'shaft', 'body', side, 16)
        for j, t in enumerate((.10, .22, .49, .54)):
            annulus(name+' barrel collar '+str(j), p+d*t, a, r*1.18, r*.87, .004, 'bearing' if j in (0, 3) else 'inner', side=side, n=24)
        joint(name+' lower clevis', p, (1 if side=='right' else -1, 0, 0), r*1.1, side)
        joint(name+' upper clevis', q, (1 if side=='right' else -1, 0, 0), r*.90, side)
        # Two independent guard rails leave the shiny piston visible between them.
        _, u, v = frame(a)
        for j in (-1, 1):
            offset = u*r*1.3*j
            tube(name+' tie rod '+str(j), [p+d*.13+offset, p+d*.55+offset], r*.13, 'edge', 'body', side, 8)

    def spring(name, p, q, r, side, turns=7, region='body'):
        p = Vector(p); q = Vector(q); a, u, v = frame(q-p)
        pts = []
        for i in range(turns*12+1):
            t = i/(turns*12); theta = math.tau*turns*t
            pts.append(p+(q-p)*t+r*(u*math.cos(theta)+v*math.sin(theta)))
        tube(name, pts, .00125, 'inner', region, side, 8, False)

    # Match the body's authored profile without changing its source objects.
    profile = [(.735, .110, .182, .295, .300), (.840, .060, .219, .345, .355),
               (.960, .040, .244, .395, .355), (1.080, -.020, .247, .370, .335),
               (1.200, -.065, .232, .295, .285), (1.310, -.075, .197, .201, .205)]
    def bay(side, theta, z, inset=.022):
        z = max(.735, min(1.31, z))
        for p, q in zip(profile, profile[1:]):
            if p[0] <= z <= q[0]:
                t = (z-p[0])/(q[0]-p[0]); cy, rx, front, back = [p[i]*(1-t)+q[i]*t for i in range(1, 5)]
                break
        sign = 1 if side=='right' else -1
        depth = front if math.cos(theta) >= 0 else back
        return Vector((sign*(rx*math.sin(theta)-inset*math.sin(theta)), cy-depth*math.cos(theta)+inset*math.cos(theta), z))

    cavity_records = []
    for side in ('left', 'right'):
        sign = 1 if side == 'right' else -1
        axis = Vector((sign, 0, 0))
        # Recessed skeleton with deliberately unequal diagonals and open windows.
        for j, theta in enumerate((1.18, 1.37, 1.83, 2.00)):
            pts = [bay(side, theta+.07*math.sin(k*.55+j), .765+k*.041, .049) for k in range(13)]
            tube('deep longitudinal transmission rib '+str(j), pts, .007 if j%2 else .0055, 'inner', side=side)
        for j in range(5):
            z = .780+j*.086
            pts = [bay(side, 1.12+k*.083, z+.025*math.sin(k*.26+j), .038) for k in range(13)]
            tube('open curved cross rib '+str(j), pts, .0045, 'inner', side=side)
            for k in (0, 5, 12):
                joint('cross rib bracket '+str(j)+' '+str(k), pts[k], axis, .008, side)
        # Visible diagonal torque lines rather than a grid of generic gears.
        for j in range(3):
            pts = [bay(side, 1.32+k*.034+j*.155, .80+k*.031, .027+j*.006) for k in range(13)]
            tube('diagonal exposed torque shaft '+str(j), pts, .0043 if j else .0053, 'shaft', side=side)
            for k in (2, 6, 10):
                direction = (pts[k+1]-pts[k-1]).normalized()
                annulus('torque shaft collar '+str(j)+' '+str(k), pts[k], direction, .0075, .0045, .007, 'inner', side=side, n=24)

        # Two pistons at different depths. Inferred moving structure is visual only.
        piston('anterior slanted transmission', bay(side, 1.73, .795, .017), bay(side, 1.18, 1.190, .020), .014, side)
        piston('posterior shorter actuator', bay(side, 2.01, .808, .036), bay(side, 1.70, 1.094, .029), .0105, side)
        piston('visible front compression actuator', bay(side, 1.33, .824, .008), bay(side, 1.14, 1.159, .010), .0095, side)
        # Small guarded drive spindle remains visible through the lower opening.
        c = bay(side, 1.36, .938, .014)
        tube('transmission spindle', [c-axis*.090, c+axis*.012], .013, 'inner', side=side, n=24)
        for j, (dx, r, inner, role) in enumerate(((-.018, .053, .023, 'inner'), (-.006, .047, .024, 'bearing'),
                                                (.003, .042, .023, 'inner'), (.011, .034, .021, 'edge'))):
            annulus('stepped main drive bearing '+str(j), c+axis*dx, axis, r, inner, .004, role, side=side)
        annulus('irregular main drive gear rim', c-axis*.026, axis, .061, .046, .008, 'inner', side=side, n=64, teeth=16)
        # Six open spokes and distinct captive bolts. Empty sectors remain actual gaps.
        for j in range(6):
            a = math.tau*j/6+.16
            v = Vector((0, math.cos(a), math.sin(a)))
            tube('drive open spoke '+str(j), [c-axis*.027+v*.017, c-axis*.027+v*.048], .004, 'inner', side=side, n=10)
            p = c+axis*.016+v*.028
            tube('drive captive bolt '+str(j), [p, p+axis*.003], .003, 'rivet', side=side, n=6)
        tube('drive central hex shaft', [c-axis*.035, c+axis*.020], .010, 'shaft', side=side, n=8)
        # A single offset idler, mostly recessed; not repeated decorative cog rows.
        ic = bay(side, 1.76, .822, .025)
        annulus('low offset idler dark toothed rim', ic, axis, .027, .014, .008, 'inner', side=side, n=40, teeth=10)
        annulus('low offset idler washer', ic+axis*.007, axis, .018, .009, .003, 'bearing', side=side, n=32)
        tube('low idler axis', [ic-axis*.012, ic+axis*.012], .006, 'rivet', side=side, n=8)

        # Cables occupy the darkest depth plane; bundles curve into the shoulder.
        for j in range(7):
            theta = 1.43+j*.065
            pts = [bay(side, theta+.15*math.sin(k*.27+j*.3), .790+k*.037, .065+(j%3)*.004) for k in range(14)]
            tube('deep flex cable '+str(j), pts, .0026+(j%2)*.0005, 'inner', side=side, n=8)
            if j in (0, 3, 6):
                for k in (3, 8, 11):
                    annulus('cable crimp '+str(j)+' '+str(k), pts[k], pts[k+1]-pts[k-1], .0045, .0025, .007, 'rivet', side=side, n=16)
        spring('protected ribbed service hose', bay(side, 1.96, .862, .023), bay(side, 1.92, 1.170, .026), .006, side, 18)
        spring('front return spring', bay(side, 1.15, .861, .020), bay(side, 1.11, 1.080, .018), .008, side, 12)

        # Open triangular bracket layers touch the authored rims at discrete points.
        for j, z in enumerate((.858, 1.065, 1.220)):
            p = bay(side, 1.10, z, .012); q = bay(side, 1.98, z-.061, .031)
            r = bay(side, 1.50, z-.121, .038)
            for k, (a, b) in enumerate(((p, q), (p, r), (q, r))):
                tube('layered bay brace '+str(j)+' '+str(k), [a, b], .0047 if k else .006, 'inner' if k else 'steel', side=side, n=10)
            joint('bay brace anchor '+str(j), p, axis, .010, side)
        # A few scalloped bearing blocks break up long shafts without closing bays.
        for j in range(3):
            p = bay(side, 1.21, .910+j*.105, .019)
            annulus('front rib support bearing '+str(j), p, axis, .012, .0055, .010, 'inner', side=side, n=24)
            annulus('front rib support lip '+str(j), p+axis*.006, axis, .0094, .005, .002, 'edge', side=side, n=24)

        # High shoulder roots are unchanged. The visible cast cap protrudes only
        # at the front wing/breast split; a recessed shaft joins the root inside.
        root = Vector((sign*.195, -.045, 1.335))
        wc = Vector((sign*.296, -.190, 1.274))
        tube('wing root recessed link', [root, wc-axis*.018], .018, 'inner', 'wing', side, 20)
        for j, (dx, r, inner, role) in enumerate(((-.018, .037, .018, 'inner'), (-.008, .034, .019, 'bearing'),
                                                (.001, .029, .020, 'inner'), (.006, .025, .018, 'edge'))):
            annulus('wing-root layered cast bearing '+str(j), wc+axis*dx, axis, r, inner, .004, role, 'wing', side, 40)
        for j in range(5):
            a = math.tau*j/5+.4; v = Vector((0, math.cos(a), math.sin(a)))
            tube('wing-root open bearing spoke '+str(j), [wc-axis*.018+v*.009, wc-axis*.018+v*.026], .0028, 'inner', 'wing', side, 8)
            p = wc+axis*.009+v*.023
            tube('wing-root captive cap '+str(j), [p, p+axis*.003], .0027, 'rivet', 'wing', side, 6)
        tube('wing-root recessed flat hex axis', [wc-axis*.036, wc-axis*.017], .009, 'inner', 'wing', side, 8)
        cavity_records.append({'side': side, 'driveBearingCentre': list(c), 'wingRootAnchorUnchanged': list(root),
                                'visibleWingBearingCentre': list(wc), 'constructionDepth': 'Inset ribs/cables and open-spoke bearing stacks; no continuous side shell'})

    bounds = [[min((o.matrix_world@v.co)[i] for o in made for v in o.data.vertices),
               max((o.matrix_world@v.co)[i] for o in made for v in o.data.vertices)] for i in range(3)]
    return {'module': 'cg2b-machinery', 'era': era, 'newEditableMeshes': len(made), 'roles': counts,
            'newGeometryBoundsXYZ': bounds, 'cavities': cavity_records,
            'preservation': 'No existing object, geometry, UV, transform, visibility or material node was changed',
            'visualProposal': ['Layered exposed diagonal pistons and torque shafts', 'Sparse open-spoke gears with stacked bearings',
                               'Deep cable bundles, ribbed hoses and braces leave real recesses', 'Visible high wing-root cast bearing caps'],
            'limits': ['Machinery and unseen connections are CG inference, not engineering or exact source reconstruction',
                       'Inherited materials only; surface author owns subsequent regional maps', 'Artistic likeness remains subject to integrated owner review']}
