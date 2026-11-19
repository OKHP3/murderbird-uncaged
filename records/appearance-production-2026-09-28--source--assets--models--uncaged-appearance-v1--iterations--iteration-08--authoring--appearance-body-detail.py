"""Appearance-only body and limb fittings for the alignment-v3 proposal.

Called after alignment-v3 has been loaded. All new geometry is rigidly
parented to existing assembly empties; this module never edits the rig.
Dimensions are authored surface proposals, not source-image measurements.
"""

import math as _math


def build(ctx):
    bpy = ctx['bpy']
    Vector = ctx['Vector']
    math = ctx.get('math', _math)
    mat = ctx['mat']
    patch = ctx['patch']
    wm = ctx['wm']
    wr = ctx['wr']
    wt = ctx['wt']
    fastener = ctx['fastener']
    sample = ctx['sample']
    envelope = ctx['envelope']
    smooth_profile = ctx['smooth_profile']

    bpy.context.view_layer.update()
    objects = bpy.data.objects
    left_right = ((1, 'left'), (-1, 'right'))

    # These are the alignment-v3 world-space body sections. They let the
    # backing follow the existing envelope instead of filling its silhouette.
    body_sections = [
        (.68, .09, .11, .13), (.76, .075, .18, .20),
        (.88, .045, .255, .265), (1.02, .005, .305, .305),
        (1.16, -.04, .325, .305), (1.28, -.09, .282, .255),
        (1.37, -.125, .22, .205),
    ]

    # Replace the broad polygonal exterior fields in this derivative only.
    # The fitted envelope, rigid joints and retained inner construction stay.
    removed = []
    prefixes = ('Breast central field', 'Breast oblique field', 'Breast field fixing',
                'left graduated mantle plate', 'right graduated mantle plate',
                'Mantle plate root pin', 'left oblique shoulder saddle',
                'right oblique shoulder saddle', 'Dorsal lap')
    for obj in list(objects):
        if obj.type == 'MESH' and obj.name.startswith(prefixes):
            removed.append(obj.name)
            bpy.data.objects.remove(obj, do_unlink=True)

    def formed_plate(name, center, top, width, length, project, owner, region, index):
        # Rounded lower corners and an asymmetric short tip keep a formed
        # overlapping metal scale from reading as a flat hexagonal tile.
        a = center
        outline = [(a-width*.48,top), (a+width*.46,top+.002),
                   (a+width*.50,top-length*.40), (a+width*.40,top-length*.70),
                   (a+width*.22,top-length*.90), (a+width*.035,top-length),
                   (a-width*.21,top-length*.94), (a-width*.42,top-length*.72),
                   (a-width*.50,top-length*.40)]
        outline = smooth_profile(outline, 2)
        obj = patch(name, outline, project, owner, region, 'plate',
                    thickness=.0035, sub=2)
        # Finely rolled hem follows the exposed end only; rooted ends stay
        # under the next overlapping course. Detail comes from construction.
        hem = [project(x,z) for x,z in outline[5:16]]
        if len(hem)>1:
            wt(name+' rolled hem',hem,[.00065]*len(hem),owner,region,'edge',sides=6)

        def surface_normal(angle, z):
            # Use the authored projection itself so fasteners and the chased
            # line sit tangent to breast, dorsal, and wing surfaces alike.
            step = .0001
            da = Vector(project(angle+step,z))-Vector(project(angle-step,z))
            dz = Vector(project(angle,z+step))-Vector(project(angle,z-step))
            normal = da.cross(dz)
            if normal.length < 1e-10:
                return Vector((0, 0, 1))
            normal.normalize()
            point = Vector(project(angle,z))
            outward = Vector((point.x, point.y+.01, 0))
            if outward.length > 1e-8 and normal.dot(outward) < 0:
                normal.negate()
            return normal

        # Keep a pair of small headed fixings on the exposed lower course.
        # The short dark slot is a separate fine inlay, not a large bright rim.
        for side_index, lateral in enumerate((-.23,.23)):
            angle = a + width*lateral
            z = top-length*.70
            p = Vector(project(angle,z))
            normal = surface_normal(angle,z)
            fastener(name+f' seated lower fixing {side_index+1}',p,normal,
                     owner,region,r=.0025)
            across = Vector(project(angle+.0001,z))-Vector(project(angle-.0001,z))
            across.normalize()
            cap = p + normal*.003
            wt(name+f' fixing slot {side_index+1}',
               [cap-across*.0010,cap+across*.0010],
               [.00028,.00028],owner,region,'recess',sides=6)

        # Chase a fine inset groove just inside the visible rounded lower hem.
        # Pulling each point slightly toward the plate field keeps the line
        # clear of the rolled outer edge while following its authored curvature.
        groove_center_z = top-length*.48
        groove=[]
        for angle,z in outline[5:16]:
            inset_angle = angle+(a-angle)*.045
            inset_z = z+(groove_center_z-z)*.045
            point = Vector(project(inset_angle,inset_z))
            groove.append(point+surface_normal(inset_angle,inset_z)*.0005)
        if len(groove)>1:
            wt(name+' inset lower chased groove',groove,[.0008]*len(groove),
               owner,region,'recess',sides=6)
        return obj

    breast = objects['breastplate']
    for row in range(8):
        top = 1.367-row*.084
        count = 7 if row<5 else 5
        span = 2.97
        width = span/count*1.07
        for col in range(count):
            center = -span/2+span*(col+.5)/count+(.04 if row%2 else -.02)
            length = (.154 if row<5 else .130)*(1+.06*math.sin(col*2.1+row))
            ztop = top+.006*math.sin(col*1.3+row)
            length = min(length, ztop-.698) # retain a valid curved lower contour before Solidify
            def project(a,z,zt=ztop,l=length,c=center,w=width):
                t=max(0,min(1,(zt-z)/l))
                dome=.004*math.sin(math.pi*t)*max(0,1-((a-c)/(w*.6))**2)
                return envelope(body_sections,max(.685,z),a,.012+.016*t+dome)
            formed_plate(f'Fitted breast scale {row} {col}',center,ztop,width,length,
                         project,breast,'breast',row*count+col)

    # One dark fitted under-shell at each flank makes the plate gaps read as
    # intentional depth. The larger bronze fields remain the silhouette.
    breast = objects['breastplate']
    for side, label in left_right:
        outline = [
            (side * 1.02, .79), (side * 2.10, .78),
            (side * 2.24, .97), (side * 2.02, 1.19),
            (side * 1.57, 1.34), (side * 1.18, 1.28),
        ]
        if side < 0:
            outline.reverse()
        patch(
            f'{label} fitted flank shadow liner', outline,
            lambda angle, z: envelope(body_sections, z, angle, .003),
            breast, 'breast', 'recess', thickness=.003, sub=7,
        )

        # Three differently shaped transition pieces bridge the breast,
        # shoulder and rear flank. Their stagger and taper avoid a tiled row.
        transitions = [
            ([(.97, 1.285), (1.35, 1.34), (1.54, 1.23), (1.33, 1.12),
              (1.12, 1.16)], 'upper shoulder return', .029),
            ([(1.31, 1.12), (1.77, 1.18), (1.93, 1.02), (1.70, .91),
              (1.43, .96)], 'middle flank return', .026),
            ([(1.72, .91), (2.04, .96), (2.13, .82), (1.90, .765),
              (1.72, .80)], 'lower ventral return', .022),
        ]
        for outline, name, lift in transitions:
            mirrored = [(side * angle, z) for angle, z in outline]
            if side < 0:
                mirrored.reverse()
            patch(
                f'{label} {name}', mirrored,
                lambda angle, z, amount=lift: envelope(
                    body_sections, z, angle, amount),
                breast, 'breast', 'plate', thickness=.005, sub=5,
            )

        # A restrained forged seam traces only the outer breast transition.
        seam_points = [
            envelope(body_sections, z, side * a, .033)
            for a, z in ((1.08, 1.29), (1.29, 1.23), (1.43, 1.13),
                         (1.57, 1.00), (1.68, .88))
        ]
        wt(f'{label} breast return seam', seam_points,
           [.0032, .0038, .0035, .0030, .0022], breast,
           'breast', 'edge', sides=8)

    # Fitted dorsal courses continue the exterior language across the rear.
    # The historical flat laps are removed only in this derivative; their
    # rigid body owner and inner shell remain as the preserved foundation.
    body = objects['body']
    for row in range(7):
        top = 1.362-row*.094
        count=5 if row<5 else 4
        span=3.35
        width=span/count*1.06
        for col in range(count):
            center=math.pi-span/2+span*(col+.5)/count
            length=min(.145,top-.698)
            def project(a,z,zt=top,l=length):
                t=max(0,min(1,(zt-z)/l))
                return envelope(body_sections,z,a,.012+.016*t)
            formed_plate(f'Fitted dorsal scale {row} {col}',center,top,width,length,
                         project,body,'back',row*count+col)

    # Mantle perimeter caps and a few selected overlap seams refine the
    # folded shield without repeating a trim around every individual plate.
    wing_sections = [
        (.765, .29, .008, .02), (.81, .27, .035, .075),
        (.88, .245, .075, .16), (1.015, .17, .136, .235),
        (1.16, .095, .164, .266), (1.29, .035, .153, .228),
        (1.39, .02, .098, .155), (1.445, .025, .016, .055),
    ]

    def wing_point(side, angle, z, lift=0):
        cy, rx, ry = sample(wing_sections, z)
        return Vector((side * (.315 + math.cos(angle) * (rx + lift)),
                       cy + math.sin(angle) * (ry + lift), z))

    for side,label in left_right:
        upper=objects[f'{label}-mantle'];lower=objects[f'{label}-wing-shield']
        for row in range(10):
            top=1.423-row*.064
            count=8 if row<7 else 6
            width=2.95/count*1.11
            length=.105 if row<7 else .103
            owner=upper if top>1.10 else lower
            region='shoulder' if owner==upper else 'wing'
            for col in range(count):
                center=-1.47+2.94*(col+.5)/count+(.045 if row%2 else -.025)
                ztop=top+.004*math.sin(col*1.7+row)
                def project(a,z,zt=ztop,l=length,s=side,c=center,w=width):
                    t=max(0,min(1,(zt-z)/l))
                    sweep=.15*t
                    dome=.003*math.sin(math.pi*t)*max(0,1-((a-c)/(w*.6))**2)
                    return wing_point(s,a+sweep,max(.77,z),.009+.018*t+dome)
                formed_plate(f'{label} fitted mantle scale {row} {col}',center,ztop,width,length,
                             project,owner,region,row*count+col)

    for side,label in left_right:
        upper=objects[f'{label}-mantle'];lower=objects[f'{label}-wing-shield']
        for row in range(9):
            top=1.404-row*.067
            length=min(.106,top-.780)
            owner=upper if top>1.10 else lower
            region='shoulder' if owner==upper else 'wing'
            for col in range(2):
                center=1.62+col*.35
                def project(a,z,zt=top,l=length,s=side):
                    t=max(0,min(1,(zt-z)/l))
                    return wing_point(s,a,z,.010+.015*t)
                formed_plate(f'{label} trailing return scale {row} {col}',center,top,.39,length,
                             project,owner,region,row*2+col)

    for side, label in left_right:
        upper = objects[f'{label}-mantle']
        lower = objects[f'{label}-wing-shield']
        # Tapered border rails follow the fore and aft shield edges. The rail
        # changes owner with the existing shoulder/elbow split.
        for angles, name, role in ((-1.48, 'leading', 'edge'),
                                   (1.48, 'trailing', 'frame')):
            edge_angle = angles if side > 0 else -angles
            points = [wing_point(side, edge_angle, z, .016)
                      for z in (1.414, 1.34, 1.25, 1.15, 1.04, .93, .83)]
            upper_points = points[:4]
            lower_points = points[3:]
            wt(f'{label} mantle {name} formed rim upper', upper_points,
               [.0040, .0048, .0045, .0038], upper,
               'shoulder', role, sides=8)
            wt(f'{label} mantle {name} formed rim lower', lower_points,
               [.0038, .0042, .0035, .0025], lower,
               'wing', role, sides=8)

        # Select seam arcs across broad plates, leaving the smaller plates
        # unoutlined so the mantle keeps a varied, layered rhythm.
        seam_specs = [(1.356, upper, 'shoulder', 1.02, .015),
                      (1.136, upper, 'shoulder', .88, .016),
                      (.934, lower, 'wing', .72, .014)]
        if side > 0:
            # Leave the documented anatomical-left repair/stop landmark open.
            seam_specs = seam_specs[1:]
        for z, owner, region, span, lift in seam_specs:
            points = [wing_point(side, -span + 2 * span * i / 8,
                                 z + .008 * math.sin(math.pi * i / 8), lift)
                      for i in range(9)]
            wt(f'{label} mantle selected overlap seam {z:.3f}', points,
               [.0024, .0030, .0034, .0036, .0037,
                .0036, .0034, .0030, .0024], owner,
               region, 'edge', sides=8)

        # Root pins sit at staggered plate roots. Keep the anatomical-left
        # travel stop and repair bracket visible by leaving their pivot zone
        # and the industrial-repairs group untouched.
        pin_specs = ((1.385, -.88), (1.278, .52), (1.171, -.32),
                     (1.042, .76), (.925, -.58))
        for i, (z, angle) in enumerate(pin_specs):
            if side > 0 and i == 0:
                continue
            owner = upper if z > 1.10 else lower
            region = 'shoulder' if owner is upper else 'wing'
            point = wing_point(side, angle, z, .020)
            normal = Vector((side * math.cos(angle),
                             math.sin(angle), .34)).normalized()
            fastener(f'{label} mantle countersunk root pin {i + 1}',
                     point, normal, owner, region, r=.0038)

    # Nested, thin bearing skirts frame each real joint. They stay concentric
    # with the existing pivots and never replace or move the functional core.
    joint_specs = (
        ('hip', 'left-thigh', 'leg', .056),
        ('knee', 'left-shin', 'leg', .054),
        ('ankle', 'left-foot', 'foot', .046),
    )
    for side, label in left_right:
        for joint, owner_name, region, radius in joint_specs:
            owner = objects[owner_name.replace('left', label)]
            center = owner.matrix_world.translation.copy()
            axis = (owner.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()
            for sign in (-1, 1):
                base = center + axis * (sign * .043)
                wr(f'{label} {joint} outer bearing skirt',
                   base - axis * .006, base + axis * .006,
                   radius, owner, region, 'bearing', sides=28)
                lip = center + axis * (sign * .054)
                wr(f'{label} {joint} bright collar lip',
                   lip - axis * .0022, lip + axis * .0022,
                   radius * .91, owner, region, 'edge', sides=28)
                cap = center + axis * (sign * .060)
                wr(f'{label} {joint} inset seal ring',
                   cap - axis * .0015, cap + axis * .0015,
                   radius * .59, owner, region, 'recess', sides=24)

    # Fine contour strips follow existing leg guards. They are surface trim,
    # not extra load rails, and stop short of both bearing envelopes.
    for side, label in left_right:
        thigh = objects[f'{label}-thigh']
        shin = objects[f'{label}-shin']
        hip = thigh.matrix_world.translation.copy()
        knee = shin.matrix_world.translation.copy()
        ankle = objects[f'{label}-foot'].matrix_world.translation.copy()
        for name, a, b, owner, width in (
                ('thigh', hip, knee, thigh, .051),
                ('shin', knee, ankle, shin, .043)):
            axis = (b - a).normalized()
            front = Vector((0, -1, 0))
            front = (front - axis * front.dot(axis)).normalized()
            across = axis.cross(front).normalized()
            points = []
            for t in (.20, .36, .53, .70, .84):
                center = a.lerp(b, t)
                points.append(center + front * .044 + across * (side * width * .48))
            wt(f'{label} {name} narrow formed face trim', points,
               [.0030, .0038, .0040, .0036, .0024], owner,
               'leg', 'edge', sides=8)
            # Two offset fastener seats mark the ends of each guard course.
            for t, offset in ((.23, -.55), (.78, .50)):
                center = a.lerp(b, t) + front * .042 + across * (width * offset)
                fastener(f'{label} {name} guard seat', center,
                         front, owner, 'leg', r=.0035)

    # Toe-root ferrules surround, but do not replace, the articulated digit
    # cores. Their axes are read from the existing rigid attachment frames.
    for side, label in left_right:
        for digit in (1, 2, 3):
            owner = objects[f'{label}-digit-{digit}-proximal']
            center = owner.matrix_world.translation.copy()
            axis = (owner.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()
            radius = .035 if digit == 2 else .031
            for offset, scale, role in ((.0, 1.00, 'bearing'),
                                         (.010, .88, 'edge'),
                                         (-.010, .88, 'edge')):
                c = center + axis * offset
                wr(f'{label} digit {digit} root ferrule {offset:+.3f}',
                   c - axis * .002, c + axis * .002,
                   radius * scale, owner, 'foot', role, sides=20)

    # Short paired instep rails describe the ankle-to-toe transition while
    # staying above the sole and clear of toe contact surfaces.
    for side, label in left_right:
        owner = objects[f'{label}-foot']
        ankle = owner.matrix_world.translation.copy()
        toe_base = objects[f'{label}-toes'].matrix_world.translation.copy()
        direction = (toe_base - ankle).normalized()
        across = Vector((1, 0, 0))
        across = (across - direction * across.dot(direction)).normalized()
        up = across.cross(direction).normalized()
        if up.z < 0:
            up.negate()
        for sign in (-1, 1):
            points = []
            for t, lift in ((.18, .024), (.39, .030), (.61, .025), (.77, .016)):
                p = ankle.lerp(toe_base, t) + up * lift + across * (sign * .042)
                points.append(p)
            wt(f'{label} instep side reveal trim {sign:+d}', points,
               [.0024, .0032, .0030, .0018], owner,
               'foot', 'edge', sides=8)

    return {'removedExteriorMeshes':removed,
            'surfaceChange':'Rounded fitted breast and mantle courses, rolled exposed hems, nested joint fittings; rigid interface preserved.',
            'status':'Appearance reconstruction proposal; no new engineering authority.'}
