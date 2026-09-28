"""Regional breast, mantle and limb geometry for the alignment-v4 proposal.

Executed by the v4 orchestrator in a namespace containing the preserved v3
scene and geometry helpers. Dimensions are authored interpretations in metres,
not recovered source measurements. This module never changes rig empties.
"""

# Remove only the prior exterior meshes owned by these regions. Rigid digit
# nodes and all other objects, including every empty, remain in place.
_old_parts = []
for _obj in list(bpy.data.objects):
    if _obj.type != 'MESH':
        continue
    if (under(_obj, bpy.data.objects['processing'])
            or under(_obj, bpy.data.objects['power-core'])):
        continue
    _region = _obj.get('region', '')
    _role = _obj.get('surfaceRole', '')
    _name = _obj.name.lower()
    _replace = (_region == 'breast' and _role in {'plate', 'bearing'})
    _replace |= _region in {'shoulder', 'wing', 'leg'}
    _replace |= (_region == 'foot' and (
        'instep' in _name or 'knuckle' in _name or 'talon' in _name
        or 'hallux' in _name
    ))
    if _replace:
        bpy.data.objects.remove(_obj, do_unlink=True)


def _plate(name, outline, project, owner, region, thickness=.007, sub=4):
    """Curved overlapping shell plate with a slightly rolled exposed edge."""
    # Keep boundaries as the authored simple polygon. Catmull smoothing can
    # overshoot concave feather tips and self-intersect; the projected surface
    # and smooth polygon normals provide the curvature without moving edges.
    vertices, faces = polygon_surface(outline, project, sub)
    # Reflection in the angular coordinate reverses winding. Orient the open
    # sheet outward BEFORE solidifying it, so mirrored plate walls do not grow
    # through their neighbors or acquire inverted edge bevels.
    score = 0.0
    for ids in faces:
        aa, bb, cc = [Vector(vertices[i]) for i in ids[:3]]
        centre = (aa+bb+cc)/3
        if region == 'breast':
            cy, _, _ = sample(_body_sections, centre.z)
            outward = Vector((centre.x, centre.y-cy, 0))
        else:
            cy, _, _ = sample(_wing_sections, centre.z)
            side = 1 if owner.name.startswith('left') else -1
            outward = Vector((centre.x-side*.315, centre.y-cy, 0))
        score += (bb-aa).cross(cc-aa).dot(outward)
    if score < 0: faces = [tuple(reversed(face)) for face in faces]
    _mesh = wm(name, vertices, faces, owner, region, 'plate')
    solid = _mesh.modifiers.new('Outward rigid plate wall', 'SOLIDIFY')
    solid.thickness = thickness
    solid.offset = -1
    # The native face grid already defines the edge. Beveling every projected
    # triangulation crease can create artificial slivers on tight curvature.
    for face in _mesh.data.polygons: face.use_smooth = True
    control(name+' boundary', [project(_a,_b) for _a,_b in outline], owner,
            'regional-plate-profile', True)
    return _mesh


def _annular_race(name, centre, x0, x1, outer_radius, inner_radius, owner, region):
    """Closed stepped bearing ring whose center remains visibly open/recessed."""
    _n = 40
    _vertices = []
    for _x, _radius in ((x0,outer_radius),(x0,inner_radius),
                        (x1,outer_radius),(x1,inner_radius)):
        for _k in range(_n):
            _a = math.tau*_k/_n
            _vertices.append(Vector((_x, centre.y+math.cos(_a)*_radius,
                                     centre.z+math.sin(_a)*_radius)))
    _faces = []
    for _k in range(_n):
        _next = (_k+1)%_n
        _faces.extend([
            (_k,_next,_n+_next,_n+_k),
            (2*_n+_k,3*_n+_k,3*_n+_next,2*_n+_next),
            (_k,2*_n+_k,2*_n+_next,_next),
            (_n+_k,_n+_next,3*_n+_next,3*_n+_k),
        ])
    _ring = wm(name,_vertices,_faces,owner,region,'bearing')
    for _poly in _ring.data.polygons:
        _poly.use_smooth = True
    return _ring


# Breast keeps the exact v3 body_sections envelope. Long central keel plates and
# narrower oblique flank scales now overlap in both the vertical and lateral
# directions, and stand proud as curved shells rather than flat pentagons.
_body_sections = [(.68,.09,.11,.13),(.76,.075,.18,.20),(.88,.045,.255,.265),
                  (1.02,.005,.305,.305),(1.16,-.04,.325,.305),
                  (1.28,-.09,.282,.255),(1.37,-.125,.22,.205)]
_breast_rows = [
    # top, length, lateral half-span, sweep, crown
    (1.365, .158, 1.02, -.045, .024),
    (1.246, .184, 1.26, -.030, .029),
    (1.105, .190, 1.39,  .012, .031),
    (.961,  .170, 1.34,  .052, .028),
    (.829,  .138, 1.12,  .075, .022),
    (.739,  .090,  .78,  .060, .017),
]
for _row, (_top, _length, _span, _sweep, _crown) in enumerate(_breast_rows):
    # The keel plate is deliberately narrow and long; separate paired plates
    # feather across it. Angular limits correspond to about +/- .17 m at the
    # widest body section, retaining the established outer silhouette.
    _keel = [(-.23, _top), (.21, _top + .006), (.25, _top - _length*.34),
             (.09 + _sweep, _top - _length*.80), (-.025 + _sweep, _top - _length),
             (-.23, _top - _length*.64)]

    def _breast_surface(_a, _z, _top=_top, _length=_length, _crown=_crown):
        _f = max(0.0, min(1.0, (_top - _z) / max(_length, .001)))
        _c = math.cos(max(-1.45, min(1.45, _a)))
        # The raised center tapers smoothly into the body at the plate margins.
        return envelope(_body_sections, max(.681, _z), _a,
                        .010 + .48*_crown * max(0.0, _c)**1.4 + .005*_f)

    _plate(f'Breast keel overlapping lamina { _row }', _keel,
           _breast_surface, breast, 'breast', .009)
    for _pin, _pin_angle in enumerate((-.115,.115)):
        fastener(f'Breast keel root fixing {_row} {_pin}',
                 _breast_surface(_pin_angle,_top-.022),
                 (math.sin(_pin_angle),-math.cos(_pin_angle),.16),
                 breast,'breast',.0028)
    for _side in (-1, 1):
        # Three unequal feather-like plates per side. They interleave around the
        # keel and expose pointed lower margins rather than a uniform grid.
        for _col, (_centre, _width, _len_gain, _lift) in enumerate([
            (.43, .52, .88, .010), (.88, .54, 1.04, .013), (1.31, .53, .76, .011),
        ]):
            # Build every plate in the same positive-angle winding. Reflection
            # belongs in the projector; mirroring only the tip points reverses
            # the polygon ordering and creates crossed splines on one flank.
            _a = _centre
            _w = _width * (1.04 if _row in (1, 2, 3) else .88)
            _len = _length * _len_gain
            _stagger = (-.026, .012, -.010)[_col]
            _top2 = _top + _stagger + _lift*(_row%2)
            _column_sweep = (-.105, .018, .125)[_col]
            _tip = _a + _column_sweep + _sweep*.35
            _outline = [
                (_a-_w*.48, _top2), (_a-_w*.13, _top2+.009),
                (_a+_w*.37, _top2+.002), (_a+_w*.51, _top2-_len*.26),
                (_tip+_w*.12, _top2-_len*.71),
                (_tip-_w*.12, _top2-_len),
                (_a-_w*.31, _top2-_len*.79), (_a-_w*.51, _top2-_len*.36),
            ]

            def _side_surface(_aa, _zz, _top2=_top2, _len=_len,
                              _lift=_lift, _w=_w, _a=_a):
                _f = max(0.0, min(1.0, (_top2-_zz)/max(_len, .001)))
                _q = max(0.0, 1.0-abs(_aa-_a)/max(_w*.56, .001))
                _angle = _side * _aa
                _c = math.cos(max(-1.5, min(1.5, _angle)))
                return envelope(_body_sections, max(.681, _zz), _angle,
                                .008 + .007*_c + .45*_lift*_q + .005*_f)

            _plate(f'Breast lateral feather {_side} {_row} {_col}',
                   _outline, _side_surface, breast, 'breast', .007)
            for _pin, _local_angle in enumerate((-.20,.20)):
                _pin_angle = _side * (_a + _local_angle*_w)
                fastener(f'Breast field root fixing {_side} {_row} {_col} {_pin}',
                         _side_surface(_a+_local_angle*_w,_top2-.022),
                         (math.sin(_pin_angle),-math.cos(_pin_angle),.14),
                         breast,'breast',.0028)


# Mantle: retain the v3 z/cy profile and compact folded envelope, slightly
# reduce the smooth backing depth, then give the shoulder small overlapping
# coverts that transition into a few long, swept distal flank plates.
_wing_sections = [
    (.705,.30,.010,.030), (.765,.29,.016,.045), (.81,.27,.032,.071), (.88,.245,.067,.148),
    (1.015,.17,.123,.215), (1.16,.095,.145,.244),
    (1.29,.035,.139,.216), (1.39,.02,.091,.149), (1.445,.025,.016,.055),
]

def _wing_point(_side, _a, _z, _lift=0.0):
    _cy, _rx, _ry = sample(_wing_sections, _z)
    return Vector((_side*(.315+math.cos(_a)*(_rx+_lift)),
                   _cy+math.sin(_a)*(_ry+_lift), _z))


def _loft_mantle_blade(name, owner, region, side, root_a, root_z,
                       length, half_width, sweep, layer=0.0):
    """Smooth regular quad loft with a monotonic, finite-width feather tip."""
    _longitudinal, _across = 14, 12
    _vertices, _faces = [], []
    _profiles = []
    for _i in range(_longitudinal+1):
        _t = _i/_longitudinal
        _turn = _t*_t*(3.0-2.0*_t)
        _centre_a = root_a+sweep*_turn
        _z = root_z-length*_t
        # Width closes continuously but leaves a small roundable terminal edge.
        _width_scale = max(.035,(1.0-.55*_t)*(1.0-_t)**.42)
        _section = []
        for _j in range(_across+1):
            _u = -1.0+2.0*_j/_across
            _a = _centre_a+_u*half_width*_width_scale
            _camber = .008*(1.0-_u*_u)*math.sin(math.pi*_t)
            _point = _wing_point(side,_a,_z,.014+layer+_camber)
            _vertices.append(_point)
            _section.append(_point)
        _profiles.append(_section)
    for _i in range(_longitudinal):
        for _j in range(_across):
            _k = _i*(_across+1)+_j
            _faces.append((_k,_k+1,_k+_across+2,_k+_across+1))

    # Reflecting the width coordinate changes face winding on one side. Orient
    # every quad sheet toward the shell normal before its thickness is added.
    _score = 0.0
    for _face in _faces:
        _p0,_p1,_p2 = [Vector(_vertices[_q]) for _q in _face[:3]]
        _mid = (_p0+_p1+_p2)/3
        _cy,_,_ = sample(_wing_sections,_mid.z)
        _outward = Vector((_mid.x-side*.315,_mid.y-_cy,0))
        _score += (_p1-_p0).cross(_p2-_p0).dot(_outward)
    if _score < 0:
        _faces = [tuple(reversed(_face)) for _face in _faces]
    _mesh = wm(name,_vertices,_faces,owner,region,'plate')
    _solid = _mesh.modifiers.new('Outward mantle plate wall','SOLIDIFY')
    _solid.thickness=.006
    _solid.offset=-1
    for _face in _mesh.data.polygons:
        _face.use_smooth=True

    _boundary = list(_profiles[0]) + [_profile[-1] for _profile in _profiles[1:]]
    _boundary += list(reversed(_profiles[-1][:-1]))
    _boundary += [_profiles[_i][0] for _i in range(_longitudinal-1,-1,-1)]
    control(name+' boundary',_boundary,owner,'regional-plate-profile',True)
    for _i in (0,_longitudinal//2,_longitudinal):
        control(f'{name} loft section {_i}',_profiles[_i],owner,'cross-section')
    return _mesh

for _side, _label in ((1, 'left'), (-1, 'right')):
    _upper = bpy.data.objects[f'{_label}-mantle']
    _lower = bpy.data.objects[f'{_label}-wing-shield']
    for _top, _bottom, _owner in ((1.444, 1.065, _upper), (1.10, .705, _lower)):
        _vertices, _faces = [], []
        _n = 36
        for _j in range(18):
            _z = _top + (_bottom-_top)*_j/17
            for _k in range(_n+1):
                _vertices.append(_wing_point(_side, -math.pi+math.tau*_k/_n,
                                              _z, -.015))
        for _j in range(17):
            for _k in range(_n):
                _i = _j*(_n+1)+_k
                _faces.append((_i, _i+1, _i+_n+2, _i+_n+1))
        _back = wm(f'{_label} profiled mantle backing v4 {_owner.name}',
                   _vertices, _faces, _owner,
                   'shoulder' if _owner == _upper else 'wing', 'frame')
        _solid = _back.modifiers.new('Mantle inner wall', 'SOLIDIFY')
        _solid.thickness = .005
        for _face in _back.data.polygons:
            _face.use_smooth = True

    # Small, curved coverts clustered over the shoulder cap.
    _covert_rows = [
        (1.410, .105, 5, 1.08), (1.337, .120, 5, 1.10),
        (1.253, .140, 4, 1.08),
    ]
    for _r, (_z, _length, _count, _width_scale) in enumerate(_covert_rows):
        for _c in range(_count):
            _a = -1.16 + 2.32*(_c+.5)/_count
            _width = _width_scale * (2.32/_count)
            _drift = (.055,.12,.035,.095,-.035)[_c] + .012*_r
            _loft_mantle_blade(f'{_label} shoulder covert {_r} {_c}',
                               _upper,'shoulder',_side,_a,_z,_length,
                               _width*.49,_drift,.002*_r)
            fastener('Shoulder covert root pin',
                     _wing_point(_side, _a, _z-.012, .014),
                     (_side, 0, .15), _upper, 'shoulder', .0028)

    # Two overlapping rows of elongated distal plates replace the many regular
    # pod courses. Their roots tuck under the row above and their tips sweep
    # down and aft, producing a visible feather train within the same envelope.
    _distal_rows = [
        (1.150, .310, 3, 1.18, _lower), (.900, .194, 3, 1.22, _lower),
    ]
    for _r, (_z, _length, _count, _span, _owner) in enumerate(_distal_rows):
        for _c in range(_count):
            _a = -1.18 + 2.36*(_c+.5)/_count
            _width = _span * (2.36/_count) * 1.18
            _sweep = (.20,.36,.13)[_c] + .035*_r
            _region = 'shoulder' if _owner == _upper else 'wing'
            _loft_mantle_blade(f'{_label} distal mantle plume {_r} {_c}',
                               _owner,_region,_side,_a,_z,_length,
                               _width*.49,_sweep,.006+.004*_r)
            fastener('Distal mantle root pin',
                     _wing_point(_side, _a, _z-.013, .022+.004*_r),
                     (_side,0,.15), _owner, _region, .003)

    # Oblique saddle ties the near-side folded shell into the cervical field.
    _saddle = [(-1.28,1.348),(-.78,1.402),(-.28,1.434),(.27,1.434),
               (.58,1.398),(.32,1.379),(-.25,1.406),(-.94,1.347)]
    _plate(f'{_label} oblique shoulder saddle v4', _saddle,
           lambda _a,_z: _wing_point(_side,_a,_z,.018),
           _upper, 'shoulder', .008)

    _a = _upper.matrix_world.translation.copy()
    _b = _lower.matrix_world.translation.copy()
    # Coaxial journals remain centered on the established rigid shoulder axes.
    wr(f'{_label} shouldered shoulder journal', _a-Vector((.027,0,0)),
       _a+Vector((.033,0,0)), .041, _upper, 'shoulder', 'bearing', sides=32)
    for _dx, _radius, _width in ((-.044,.049,.009),(-.033,.044,.004),
                                  (.033,.044,.004),(.044,.049,.009)):
        wr(f'{_label} stepped shoulder race {_dx}',
           _a+Vector((_dx,0,0)), _a+Vector((_dx+_width,0,0)),
           _radius, _upper, 'shoulder', 'bearing', sides=32)
    wt(f'{_label} swept upper wing load member',
       [_a, _a.lerp(_b,.45)+Vector((0,.014,.012)), _b],
       [.023,.022,.024], _upper, 'shoulder')
    wr(f'{_label} coaxial elbow journal', _b-Vector((.011,0,0)),
       _b+Vector((.011,0,0)), .033, _lower, 'wing', 'bearing', sides=32)
    for _dx in (-.015,.011):
        wr(f'{_label} stepped elbow race {_dx}', _b+Vector((_dx,0,0)),
           _b+Vector((_dx+.004,0,0)), .039, _lower, 'wing', 'bearing', sides=28)

    if _side == 1:
        wr('Original anatomical-left travel stop v4',
           _a+Vector((.007,-.063,-.010)), _a+Vector((.044,-.063,-.010)),
           .016, _upper, 'shoulder', 'frame')
        wt('Proposed later left bearing strap v4',
           [_a+Vector((.035,-.02,.055)), _a+Vector((.043,-.035,0)),
            _a+Vector((.028,-.015,-.070))], [.011,.012,.011],
           bpy.data.objects['industrial-repairs'], 'shoulder', 'repair',
           'mechanic,builder')


# Legs retain all hip/knee/ankle empty pivots and separate thigh/shin/foot
# ownership. Tapered shell guards bridge the plain rails; bearings receive
# stepped concentric races while their clear transverse axes remain exposed.
for _side, _label in ((1, 'left'), (-1, 'right')):
    _thigh = bpy.data.objects[f'{_label}-thigh']
    _shin = bpy.data.objects[f'{_label}-shin']
    _foot = bpy.data.objects[f'{_label}-foot']
    _hip = _thigh.matrix_world.translation.copy()
    _knee = _shin.matrix_world.translation.copy()
    _ankle = _foot.matrix_world.translation.copy()

    for _centre, _owner, _radius in ((_hip,_thigh,.046), (_knee,_shin,.044),
                                      (_ankle,_foot,.035)):
        wr(f'{_label} articulated bearing core',
           _centre-Vector((.034,0,0)), _centre+Vector((.034,0,0)),
           _radius, _owner, 'leg' if _owner != _foot else 'foot',
           'frame', sides=32)
        # Alternating radii and recessed inner races form a stepped bearing
        # stack instead of a single unbroken drum.
        for _sgn in (-1,1):
            _base = _centre.x + _sgn*.034
            _end = _base + _sgn*.008
            _region = 'leg' if _owner != _foot else 'foot'
            _x0,_x1 = sorted((_base,_end))
            _annular_race(f'{_label} open stepped bearing race {_sgn}',
                          _centre,_x0,_x1,_radius*1.20,_radius*.79,
                          _owner,_region)
            # The small axle cap is set back inside the annulus; four pins sit
            # on the raised race face and make the ring legible in profile.
            _cap0 = _base+_sgn*.001
            _cap1 = _base+_sgn*.004
            wr(f'{_label} recessed axle cap {_sgn}',
               Vector((_cap0,_centre.y,_centre.z)),
               Vector((_cap1,_centre.y,_centre.z)), _radius*.27,
               _owner,_region,'edge',sides=24)
            _face_x = _end
            for _pin_index in range(4):
                _a = math.tau*_pin_index/4 + math.pi/4
                _p = Vector((_face_x,
                             _centre.y+math.cos(_a)*_radius*.99,
                             _centre.z+math.sin(_a)*_radius*.99))
                fastener(f'{_label} bearing race pin {_sgn} {_pin_index}',
                         _p,(_sgn,0,0),_owner,_region,.0035)

    for _a, _b, _owner, _width in ((_hip,_knee,_thigh,.051),
                                    (_knee,_ankle,_shin,.043)):
        _axis = (_b-_a).normalized()
        _front = Vector((0,-1,0))
        _front = (_front-_axis*_front.dot(_axis)).normalized()
        _across = _axis.cross(_front).normalized()
        for _sign in (-1,1):
            wt(f'{_label} tapered passive load rail',
               [_a.lerp(_b,.13)+_across*_sign*_width,
                _a.lerp(_b,.50)+_across*_sign*_width*.80,
                _b.lerp(_a,.14)+_across*_sign*_width*.68],
               [.017,.015,.013], _owner, 'leg', 'frame')
        for _piece, (_start,_end,_w0,_w1) in enumerate(
            ((.12,.39,1.10,.91),(.35,.66,.97,.80),(.62,.88,.84,.62))):
            _vertices, _faces = [], []
            _n = 14
            for _j in range(7):
                _t = _j/6
                _p = _a.lerp(_b,_start+(_end-_start)*_t)
                _w = _width*(_w0+(_w1-_w0)*_t)
                for _k in range(_n+1):
                    _ang = -1.78+3.56*_k/_n
                    _vertices.append(_p+_across*(math.sin(_ang)*_w)
                                     +_front*(.014+math.cos(_ang)*(.029-.004*_t)))
            for _j in range(6):
                for _k in range(_n):
                    _i = _j*(_n+1)+_k
                    _faces.append((_i,_i+1,_i+_n+2,_i+_n+1))
            _guard = wm(f'{_label} tapered limb sheath {_owner.name} {_piece}',
                        _vertices,_faces,_owner,'leg','plate')
            _solid = _guard.modifiers.new('Returned sheath wall','SOLIDIFY')
            _solid.thickness = .006
            _edge = _guard.modifiers.new('Soft returned edge','BEVEL')
            _edge.width=.0018; _edge.segments=2
            _guard.modifiers.new('Weighted sheath normals','WEIGHTED_NORMAL')
            for _poly in _guard.data.polygons:
                _poly.use_smooth = True
            for _sign in (-1,1):
                fastener('Limb sheath fixing',
                         _a.lerp(_b,_start+.05)+_across*_sign*_width*.62+_front*.039,
                         _front,_owner,'leg',.003)

    # Four separately rooted ankle/instep sheaths follow the curved foot line.
    # Neighboring segments overlap by a small amount; their center ridge and
    # returned edges articulate with the existing foot link.
    _path = [(_ankle.y-.025,_ankle.z-.027),(-.041,.159),
             (-.096,.104),(-.142,.076)]
    _widths = [.044,.047,.053,.058]
    _sections = [0,.27,.53,.78,1]
    for _piece in range(4):
        _t0 = max(0.0,_sections[_piece]-.035)
        _t1 = min(1.0,_sections[_piece+1]+.035)
        _shell_lift = .004 + .002*(_piece%2)
        _vertices, _faces = [], []
        _n = 16
        for _j in range(6):
            _t = _t0+(_t1-_t0)*_j/5
            _seg = min(2,int(_t*3))
            _local = _t*3-_seg
            _cy = _path[_seg][0]+(_path[_seg+1][0]-_path[_seg][0])*_local
            _cz = _path[_seg][1]+(_path[_seg+1][1]-_path[_seg][1])*_local
            _width = _widths[_seg]+(_widths[_seg+1]-_widths[_seg])*_local
            for _k in range(_n+1):
                _ang = -1.46+2.92*_k/_n
                _vertices.append((_ankle.x+math.sin(_ang)*_width,
                                  _cy-(.024+_shell_lift)*math.cos(_ang),
                                  _cz+(.034+_shell_lift)*math.cos(_ang)))
        for _j in range(5):
            for _k in range(_n):
                _i = _j*(_n+1)+_k
                _faces.append((_i,_i+1,_i+_n+2,_i+_n+1))
        _sheath = wm(f'{_label} articulated ankle sheath {_piece}',
                     _vertices,_faces,_foot,'foot','plate')
        _solid = _sheath.modifiers.new('Ankle sheath return','SOLIDIFY')
        _solid.thickness=.006
        _edge = _sheath.modifiers.new('Sheath plate edge','BEVEL')
        _edge.width=.0014; _edge.segments=2
        _sheath.modifiers.new('Weighted sheath normals','WEIGHTED_NORMAL')
        for _poly in _sheath.data.polygons:
            _poly.use_smooth=True
    # Fine transverse lap ribs make the four overlapping sheath plates read as
    # separate pieces in profile while leaving the ankle hinge unobstructed.
    for _t in (.27,.53,.78):
        _seg = min(2,int(_t*3)); _local = _t*3-_seg
        _cy = _path[_seg][0]+(_path[_seg+1][0]-_path[_seg][0])*_local
        _cz = _path[_seg][1]+(_path[_seg+1][1]-_path[_seg][1])*_local
        _width = _widths[_seg]+(_widths[_seg+1]-_widths[_seg])*_local
        _rib_pts = [Vector((_ankle.x+math.sin(-1.42+2.84*_k/16)*_width,
                            _cy-.031*math.cos(-1.42+2.84*_k/16),
                            _cz+.041*math.cos(-1.42+2.84*_k/16)))
                    for _k in range(17)]
        wt(f'{_label} ankle sheath lap rib {_t}', _rib_pts, [.0025]*17,
           _foot, 'foot', 'edge', sides=8)

    # Rebuild the four front talons around the exact prior terminal points.
    # A full base taper replaces the oversized round roots; a flattened oval
    # section reads as a forged claw sheath while retaining the old tip pose.
    _spreads = [-.083,0,.09]
    _lengths = [.235,.28,.215]
    _claw_lengths = [.090,.113,.077]
    for _digit in (1,2,3):
        _distal = bpy.data.objects[f'{_label}-digit-{_digit}-distal']
        _root = Vector((_ankle.x+_spreads[_digit-1]*.70,-.13,.058))
        _end = Vector((_ankle.x+_spreads[_digit-1]*1.45,
                       -.13-_lengths[_digit-1],.039))
        _hook = [
            _end+Vector((0,.020,.025)),
            _end+Vector((_spreads[_digit-1]*.08,-_claw_lengths[_digit-1]*.30,.047)),
            _end+Vector((_spreads[_digit-1]*.12,-_claw_lengths[_digit-1]*.73,.024)),
            _end+Vector((_spreads[_digit-1]*.15,-_claw_lengths[_digit-1],-.032)),
        ]
        _vertices, _faces = [], []
        _n = 16
        _radii = [.028,.027,.025,.022,.019,.014,.009,.004,.0017]
        for _j in range(17):
            _t = _j/16
            _p = Vector(curve(_hook, _t))
            _fi = _t*(len(_radii)-1)
            _ri = min(len(_radii)-2,int(_fi))
            _r = _radii[_ri]+(_radii[_ri+1]-_radii[_ri])*(_fi-_ri)
            # Axis follows the sweep in Y/Z; the cross-section stays broad
            # side-to-side and slightly flattened vertically.
            _prev = Vector(curve(_hook,max(0,_t-.01)))
            _next = Vector(curve(_hook,min(1,_t+.01)))
            _tan = (_next-_prev).normalized()
            _normal = Vector((0,-_tan.z,_tan.y)).normalized()
            for _k in range(_n):
                _ang = math.tau*_k/_n
                _vertices.append(_p+Vector((math.cos(_ang)*_r,0,0))
                    +_normal*(math.sin(_ang)*_r*.74))
        for _j in range(16):
            for _k in range(_n):
                _i = _j*_n+_k; _nextk = _j*_n+(_k+1)%_n
                _faces.append((_i,_nextk,_nextk+_n,_i+_n))
        _faces.append(tuple(range(_n-1,-1,-1)))
        _faces.append(tuple(16*_n+_k for _k in range(_n)))
        _claw = wm(f'{_label} digit {_digit} tapered claw sheath',
           _vertices,_faces,_distal,'foot','edge')
        for _face in _claw.data.polygons: _face.use_smooth = True

    # Substantial rear toe remains attached to the foot with a tapered shell.
    _hallux_root = Vector((_ankle.x,.014,.058))
    _tarsus_base = Vector((_ankle.x,-.13,.068))
    wt(f'{_label} rear hallux load link v4',
       [_tarsus_base,_hallux_root], [.042,.035], _foot,'foot','frame')
    wt(f'{_label} rear hallux sheath v4',
       [_hallux_root,Vector((_ankle.x+_side*.046,.08,.039)),
        Vector((_ankle.x+_side*.065,.115,.008))], [.022,.015,.0017],
       _foot,'foot','edge', sides=16)
