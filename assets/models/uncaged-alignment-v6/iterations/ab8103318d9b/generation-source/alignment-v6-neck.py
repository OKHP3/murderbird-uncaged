"""Cervical jaw-clearance proposal for the alignment-v6 build namespace.

Reconstructs the upper guard envelope to leave a real mandible sweep pocket.
A local forward clearance pocket accommodates the deeper v6 jaw at full opening.
The passive forks, bearings and pivots remain inherited. The forward inner
guard and matching exterior plates use the same revised envelope. Dimensions are authored interpretations, not metrology.
"""

_neck_sections = [
    (1.25, -.095, .205, .208), (1.325, -.15, .177, .19),
    (1.41, -.23, .147, .17), (1.48, -.283, .127, .148),
    (1.55, -.253, .109, .107), (1.60, -.218, .088, .086),
    (1.65, -.200, .082, .082),
]
_neck_control_sections = list(_neck_sections)


def _round_cervical_profile(knots):
    """Interpolate the envelope without changing its authored control stations.

    Cubic slopes round the former straight-sided V. Clamping each scalar to
    its adjacent stations prevents an unreviewed bulge beyond those stations.
    """
    def slope(i, field):
        a, b = max(0, i-1), min(len(knots)-1, i+1)
        return (knots[b][field]-knots[a][field])/(knots[b][0]-knots[a][0])
    result = []
    for i in range(len(knots)-1):
        a, b = knots[i], knots[i+1]
        dz = b[0]-a[0]
        for step in range(5):
            t = step/5
            values = [a[0]+dz*t]
            for field in range(1, 4):
                value = ((2*t**3-3*t**2+1)*a[field] +
                         (t**3-2*t**2+t)*dz*slope(i,field) +
                         (-2*t**3+3*t**2)*b[field] +
                         (t**3-t**2)*dz*slope(i+1,field))
                values.append(max(min(a[field],b[field]), min(max(a[field],b[field]),value)))
            result.append(tuple(values))
    return result+[knots[-1]]


_neck_sections = _round_cervical_profile(_neck_sections)

# The deeper v6 mandible crosses the lower edge of the second throat lamina
# at full opening. Recess only this forward and anterolateral sweep pocket; posterior/nape
# contours, bearing positions and load-bearing forks retain the v5 envelope.
# These are reconstruction dimensions, not measurements from the references.
_pocket_stations = [(1.36,0.0),(1.41,.008),(1.465,.035),
                    (1.505,.030),(1.55,.012),(1.585,.008),(1.62,0.0)]
_lateral_pocket_stations = [(1.43,0.0),(1.48,.010),(1.505,.029),
                            (1.55,.030),(1.58,.024),(1.615,0.0)]
def _jaw_clearance_pocket(point):
    p = Vector(point)
    cy, rx, ry = sample(_neck_sections, p.z)
    a = math.atan2(p.x/max(rx,.001), -(p.y-cy)/max(ry,.001))
    depth = sample(_pocket_stations,p.z)[0]
    p.y += depth * max(0.0,math.cos(a))**4
    # A turned open mandible also sweeps beside the upper throat. A shallow
    # anterolateral bearing recess tapers out before the nape and lower neck.
    radial = sample(_lateral_pocket_stations,p.z)[0]
    lateral_fade = max(0.0,min(1.0,(1.60-abs(a))/.30))
    radial *= math.exp(-((abs(a)-.98)/.40)**2) * lateral_fade**2*(3-2*lateral_fade)
    p.x -= radial*math.sin(a)
    p.y += radial*math.cos(a)
    return p

def _cervical_envelope(sections,z,a,offset=0):
    return _jaw_clearance_pocket(envelope(sections,z,a,offset))

# Replace matching forward inner guard as well as external armor: reducing
# only the plates would conceal the same interference beneath them. The
# load-bearing forks, bearings and their attachment transforms are untouched.
for _obj in list(bpy.data.objects):
    if (_obj.type == 'MESH' and _obj.get('region') == 'neck'
            and (_obj.get('surfaceRole') == 'plate'
                 or _obj.name == 'Cervical articulated inner guards')):
        bpy.data.objects.remove(_obj, do_unlink=True)

_inner_guard = shell('Cervical articulated inner guards', _neck_sections, neck, 'neck',
                     -.98, .98, 'frame', offset=-.010)
bpy.context.view_layer.update()
_guard_inverse = _inner_guard.matrix_world.inverted()
for _v in _inner_guard.data.vertices:
    _v.co = _guard_inverse @ _jaw_clearance_pocket(_inner_guard.matrix_world @ _v.co)


# The v3 cross-section curves describe the retired shields. Remove only curves
# parented directly to the neck and their matching manifest records.
for _obj in list(bpy.data.objects):
    if _obj.type == 'CURVE' and _obj.parent == neck:
        bpy.data.objects.remove(_obj, do_unlink=True)
control_records[:] = [r for r in control_records if r.get('owner') != neck.name]


def _neck_grid_plate(name, top, bottom, centre, half_span, owner,
                     sweep=0.0, crown=.012, edge_lift=.003):
    """One monotonic, curved quad skin with a solidified rigid plate wall.

    A shared angular/vertical grid preserves the anatomical cross-section.
    The taper, mild root sweep, and different end heights make each lamina a
    distinct formed piece instead of a square tile.
    """
    _across, _along = 12, 8
    _vertices, _faces = [], []
    for _j in range(_along + 1):
        _t = _j / _along
        for _k in range(_across + 1):
            _u = _k / _across
            _q = 2 * _u - 1
            _edge = abs(_q)
            # Slightly bowed upper edge; the lower contour varies by plate and
            # remains monotonic in height across each regular row.
            _top_z = top + .006 * (1 - _q * _q) - .003 * _q
            _tip_z = bottom + .013 * (1 - _q * _q) + .009 * _q
            _z = _top_z + (_tip_z - _top_z) * _t
            _a = centre + sweep * _t + half_span * _q * (1 - .08 * _t)
            _edge_falloff = max(0.0, 1 - _edge * _edge)
            _bulge = crown * _edge_falloff + edge_lift * _t
            _vertices.append(_cervical_envelope(_neck_sections, _z, _a, .004 + _bulge))

    _stride = _across + 1
    for _j in range(_along):
        for _k in range(_across):
            _i = _j * _stride + _k
            # top-to-bottom then increasing angle: outward on the front
            _faces.append((_i, _i + _stride, _i + _stride + 1, _i + 1))

    # Orient the open surface explicitly before solidify. The front and side
    # samples together avoid relying on angular reflection assumptions.
    _score = 0.0
    for _face in _faces:
        _a, _b, _c = [Vector(_vertices[_i]) for _i in _face[:3]]
        _mid = (_a + _b + _c) / 3
        _cy, _rx, _ry = sample(_neck_sections, _mid.z)
        _angle = math.atan2(_mid.x / max(_rx, .001),
                            -(_mid.y - _cy) / max(_ry, .001))
        _radial = Vector((math.sin(_angle), -math.cos(_angle), 0))
        _score += (_b - _a).cross(_c - _a).dot(_radial)
    if _score < 0:
        _faces = [tuple(reversed(_face)) for _face in _faces]

    _mesh = wm(name, _vertices, _faces, owner, 'neck', 'plate')
    _wall = _mesh.modifiers.new('Formed rigid lamina wall', 'SOLIDIFY')
    _wall.thickness = .006
    _wall.offset = -1
    for _face in _mesh.data.polygons:
        _face.use_smooth = True
    return _mesh


# Keep the cross-section evidence inspectable in the native proposal.
for _z, _cy, _rx, _ry in _neck_control_sections:
    control(f'Cervical section {_z:.3f}',
            [_cervical_envelope(_neck_sections, _z, -1.8 + 3.6 * _k / 24)
             for _k in range(25)], neck, 'cross-section')

# Six overlapping central throat plates. Unequal spans, end shapes, roots, and
# alternating sweeps make a formed cascade while staying inside the v3 shell.
_throat = [
    (1.638, 1.548, -.015, .58, -.035, .018),
    (1.566, 1.474,  .035, .62,  .025, .020),
    (1.492, 1.397, -.025, .67, -.018, .021),
    (1.414, 1.321,  .045, .72,  .032, .019),
    (1.339, 1.259, -.010, .69, -.028, .017),
    (1.286, 1.247,  .035, .58,  .018, .014),
]
for _i, (_top, _bottom, _centre, _span, _sweep, _crown) in enumerate(_throat):
    _neck_grid_plate(f'Throat formed lamina {_i + 1}', _top, _bottom,
                     _centre, _span, neck, _sweep, _crown)
    control(f'Throat lamina { _i + 1 } section edges',
            [_cervical_envelope(_neck_sections, _z, _centre + _sweep * _t, .012)
             for _t, _z in ((0, _top), (.5, (_top + _bottom) / 2), (1, _bottom))],
            neck, 'hidden-lamina-profile')

# Paired lateral guards transition into smaller rear-quarter/nape laminae.
# They bridge the uncovered long strut runs without widening the silhouette.
_side_rows = [
    (1.615, 1.465, 1.08, .35, .025),
    (1.485, 1.337, 1.23, .38, -.025),
    (1.354, 1.250, 1.36, .34, .035),
    (1.605, 1.455, 2.12, .36, -.020),
    (1.472, 1.322, 2.20, .39, .028),
    (1.340, 1.252, 2.28, .35, -.030),
]
for _i, (_top, _bottom, _angle, _span, _sweep) in enumerate(_side_rows):
    for _side in (-1, 1):
        _centre = _side * _angle
        _neck_grid_plate(f'Cervical flank lamina {_side} {_i + 1}',
                         _top, _bottom, _centre, _span, neck,
                         _side * _sweep, .010, .002)
        control(f'Cervical flank { _side } {_i + 1 } profile',
                [_cervical_envelope(_neck_sections, _z, _centre + _side * _sweep * _t, .010)
                 for _t, _z in ((0, _top), (.5, (_top + _bottom) / 2), (1, _bottom))],
                neck, 'hidden-lamina-profile')
