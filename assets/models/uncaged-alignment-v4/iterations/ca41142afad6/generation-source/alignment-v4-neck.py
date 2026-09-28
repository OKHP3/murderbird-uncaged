"""Cervical armor proposal for the alignment-v4 build namespace.

Reuses the retained v3 neck envelope. Only cervical plate meshes and their
editable construction curves are replaced; neck frame, bearings, and pivots
remain inherited. Dimensions are authored interpretations, not metrology.
"""

_neck_sections = [
    (1.25, -.095, .205, .208), (1.325, -.15, .177, .19),
    (1.41, -.23, .147, .17), (1.48, -.283, .127, .148),
    (1.55, -.296, .12, .14), (1.60, -.276, .123, .143),
    (1.65, -.25, .121, .144),
]

# Replace exactly the former cervical armor surface; the inherited neck frame
# and bearing meshes are deliberately retained.
for _obj in list(bpy.data.objects):
    if (_obj.type == 'MESH' and _obj.get('region') == 'neck'
            and _obj.get('surfaceRole') == 'plate'):
        bpy.data.objects.remove(_obj, do_unlink=True)

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
            _vertices.append(envelope(_neck_sections, _z, _a, .004 + _bulge))

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
for _z, _cy, _rx, _ry in _neck_sections:
    control(f'Cervical section {_z:.3f}',
            [envelope(_neck_sections, _z, -1.8 + 3.6 * _k / 24)
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
            [envelope(_neck_sections, _z, _centre + _sweep * _t, .012)
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
                [envelope(_neck_sections, _z, _centre + _side * _sweep * _t, .010)
                 for _t, _z in ((0, _top), (.5, (_top + _bottom) / 2), (1, _bottom))],
                neck, 'hidden-lamina-profile')
