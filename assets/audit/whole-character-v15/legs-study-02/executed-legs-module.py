"""Passive, joint-local leg and foot construction proposal for V15 composition.

Call ``apply()`` after loading the pinned V14 native. Existing geometry and
all motion pivots remain untouched; this module only adds rigid, era-neutral
frame and bearing meshes parented to one existing joint each.
"""
from math import cos, pi, sin

import bpy
import bmesh
from mathutils import Matrix, Vector


ERAS = 'maker,mechanic,builder'
SEGMENTS = (
    ('left-thigh', 'left-shin', 'left', 'thigh', 'leg'),
    ('left-shin', 'left-foot', 'left', 'shin', 'leg'),
    ('left-foot', 'left-toes', 'left', 'metatarsus', 'foot'),
    ('right-thigh', 'right-shin', 'right', 'thigh', 'leg'),
    ('right-shin', 'right-foot', 'right', 'shin', 'leg'),
    ('right-foot', 'right-toes', 'right', 'metatarsus', 'foot'),
)


def _basis(direction):
    axis = direction.normalized()
    ref = Vector((0.0, 1.0, 0.0))
    across = ref - axis * ref.dot(axis)
    if across.length < 1e-6:
        ref = Vector((1.0, 0.0, 0.0))
        across = ref - axis * ref.dot(axis)
    across.normalize()
    width = axis.cross(across).normalized()
    return axis, width, across


def _box_beam(points, half_width, half_depth, vertices, faces):
    """Append a closed, beveled rectangular strut between two world points."""
    p0, p1 = Vector(points[0]), Vector(points[1])
    axis, u, v = _basis(p1 - p0)
    # Clipped corners make a legible formed member without a bevel modifier.
    cross = [
        (-.62, -1), (.62, -1), (1, -.62), (1, .62),
        (.62, 1), (-.62, 1), (-1, .62), (-1, -.62),
    ]
    start = len(vertices)
    for center in (p0, p1):
        for a, b in cross:
            vertices.append(center + u * (a * half_width) + v * (b * half_depth))
    faces.extend((start + i, start + (i + 1) % 8, start + 8 + (i + 1) % 8, start + 8 + i)
                 for i in range(8))
    faces.append(tuple(start + i for i in reversed(range(8))))
    faces.append(tuple(start + 8 + i for i in range(8)))


def _closed_torus_x(center, x, major_radius=.024, tube_radius=.004, major_steps=20, minor_steps=8,
                    vertices=None, faces=None):
    """Append a closed bearing flange, with its axis along the lateral X pin."""
    center = Vector(center)
    start = len(vertices)
    for i in range(major_steps):
        theta = 2 * pi * i / major_steps
        for j in range(minor_steps):
            phi = 2 * pi * j / minor_steps
            radial = major_radius + tube_radius * cos(phi)
            vertices.append(Vector((x + tube_radius * sin(phi),
                                    center.y + radial * cos(theta),
                                    center.z + radial * sin(theta))))
    for i in range(major_steps):
        ni = (i + 1) % major_steps
        for j in range(minor_steps):
            nj = (j + 1) % minor_steps
            faces.append((start + i * minor_steps + j,
                          start + ni * minor_steps + j,
                          start + ni * minor_steps + nj,
                          start + i * minor_steps + nj))


def _install_mesh(name, owner, vertices, faces, region, role, material):
    assert bpy.data.objects.get(name) is None, f'Refusing to replace existing object {name}'
    inverse = owner.matrix_world.inverted()
    local_vertices = [inverse @ Vector(vertex) for vertex in vertices]
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata(local_vertices, [], faces)
    if material:
        mesh.materials.append(material)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    for polygon in mesh.polygons:
        polygon.use_smooth = False
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = owner
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_basis = Matrix.Identity(4)
    obj['region'] = region
    obj['surfaceRole'] = role
    obj['exteriorEras'] = ERAS
    obj['constructionClass'] = 'passive-structural-hardware'
    obj['geometryStatus'] = 'editable V15 leg-region proposal'
    obj['constructionOwner'] = owner.name
    obj['eligibilityNote'] = 'Passive in Maker and Mechanic; remains exterior in Advanced without adding powered function.'
    return obj


def _segment_frame(owner, distal, side_name, side_sign, label, region, materials):
    p0 = owner.matrix_world.translation.copy()
    p1 = distal.matrix_world.translation.copy()
    delta = p1 - p0
    assert delta.length > .16, f'{label}: unexpectedly short rigid segment'
    axis, width, depth = _basis(delta)
    # Orient the paired rails to the anatomical outer/inner sides.
    if width.x * side_sign < 0:
        width.negate()
    depth = width.cross(axis).normalized()

    def center(t, lateral=0.0, fore_aft=0.0):
        return p0.lerp(p1, t) + width * lateral + depth * fore_aft

    vertices, faces = [], []
    # Two formed primary rails make the long limb load path visible on both
    # sides of each rigid segment while leaving its center open.
    for sign in (-1, 1):
        lateral = sign * .040
        a, b = center(.11, lateral), center(.89, lateral)
        _box_beam((a, b), .012, .014, vertices, faces)
        # Paired diagonal braces triangulate each rail pair without crossing a
        # joint. Their ends stay inside the bearings at either end.
        if sign < 0:
            p_a, p_b = center(.20, -.040, -.024), center(.48, .040, -.024)
            q_a, q_b = center(.52, .040, -.024), center(.80, -.040, -.024)
        else:
            p_a, p_b = center(.20, -.040, .024), center(.48, .040, .024)
            q_a, q_b = center(.52, .040, .024), center(.80, -.040, .024)
        _box_beam((p_a, p_b), .0065, .008, vertices, faces)
        _box_beam((q_a, q_b), .0065, .008, vertices, faces)
    # Three cross-ties turn the paired rails into an open framed assembly.
    for t in (.16, .50, .84):
        _box_beam((center(t, -.040), center(t, .040)), .008, .010, vertices, faces)
    frame_name = f'{side_name.title()} {label} open passive truss'
    frame = _install_mesh(frame_name, owner, vertices, faces, region, 'frame', materials['frame'])
    frame['constructionDescription'] = 'Twin closed-section load rails with triangulated braces and three transverse ties; all members move with one existing joint.'
    frame['articulatesAcrossJoint'] = False
    return frame


def _toe_bearing(owner, source_hinge, side, label, material):
    points = [source_hinge.matrix_world @ vertex.co for vertex in source_hinge.data.vertices]
    lo = [min(point[i] for point in points) for i in range(3)]
    hi = [max(point[i] for point in points) for i in range(3)]
    center = Vector(((lo[0] + hi[0]) * .5, (lo[1] + hi[1]) * .5, (lo[2] + hi[2]) * .5))
    vertices, faces = [], []
    # Paired captive flange rings reinforce the existing pin. The original
    # hinge, pivot, and claw-contact geometry are untouched.
    for x in (lo[0] + .006, hi[0] - .006):
        _closed_torus_x(center, x, vertices=vertices, faces=faces)
    name = f'{side.title()} {label} captive toe-bearing flanges'
    obj = _install_mesh(name, owner, vertices, faces, 'foot', 'bearing', material)
    obj['constructionDescription'] = 'Two passive annular collars seated around the existing toe hinge pin.'
    obj['existingHingeMesh'] = source_hinge.name
    obj['articulatesAcrossJoint'] = False
    return obj


def apply():
    """Replace obstructing leg armor with open passive trusses and toe flanges."""
    owners = {obj.name: obj for obj in bpy.data.objects if obj.type == 'EMPTY'}
    assert all(name in owners for segment in SEGMENTS for name in segment[:2])
    materials = {
        'frame': bpy.data.materials.get('Neutral / frame'),
        'bearing': bpy.data.materials.get('Neutral / bearing'),
    }
    assert all(materials.values()), 'Expected inherited neutral frame and bearing materials'
    # V14 thigh/shin guards occupy the same envelope as paired rails and
    # diagonal braces. Retire these exact panels in this candidate so the
    # load path reads as an open frame instead of braces punching through
    # intact armor. The pinned V14 source remains unchanged.
    replaced_guard_names = [
        f'{side} shaped {segment} guard {part}'
        for side in ('left', 'right')
        for segment in ('thigh', 'shin')
        for part in ('proximal', 'distal-overlap')
    ]
    retired = []
    for name in replaced_guard_names:
        obj = bpy.data.objects.get(name)
        assert obj and obj.type == 'MESH', f'Missing exact V14 guard target: {name}'
        assert obj.parent and obj.parent.name.startswith(name.split()[0] + '-')
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
        retired.append(name)

    changed, construction = [], []
    for proximal_name, distal_name, side_name, label, region in SEGMENTS:
        obj = _segment_frame(owners[proximal_name], owners[distal_name],
                             side_name, 1 if side_name == 'left' else -1,
                             label, region, materials)
        changed.append(obj.name)
        construction.append({
            'object': obj.name,
            'owner': proximal_name,
            'distalLandmark': distal_name,
            'region': region,
            'eras': ERAS,
            'function': 'passive paired rails, diagonal stiffeners and cross-ties; one-rigid-joint ownership',
        })

    hinges = sorted((obj for obj in bpy.data.objects
                     if obj.type == 'MESH' and obj.name.startswith('Toe hinge')),
                    key=lambda obj: obj.name)
    assert len(hinges) == 12, f'Expected all 12 inherited toe hinges, found {len(hinges)}'
    for hinge in hinges:
        owner = hinge.parent
        assert owner and owner.type == 'EMPTY' and 'digit-' in owner.name
        side_name = 'left' if owner.name.startswith('left-') else 'right'
        obj = _toe_bearing(owner, hinge, side_name, owner.name.replace(side_name + '-', ''), materials['bearing'])
        changed.append(obj.name)
        construction.append({
            'object': obj.name,
            'owner': owner.name,
            'existingHinge': hinge.name,
            'region': 'foot',
            'eras': ERAS,
            'function': 'passive paired bearing flanges; follows only the existing toe pivot',
        })

    return {
        'changedOrAddedObjects': changed,
        'replacedObjects': retired,
        'construction': construction,
        'eligibility': {
            'visibleEras': ERAS,
            'maker': 'Passive frame and bearings remain compatible with external/manual control.',
            'mechanic': 'Passive reinforcement only; existing wound-drive behavior remains unchanged.',
            'advanced': 'Passive frame only; no new powered or sensing function.',
            'notAdded': ['motors', 'powered actuators', 'cross-joint rigid rods', 'new pivots'],
        },
        'limits': [
            'Construction is a visual and attachment proposal, not a load, stress, or fatigue analysis.',
            'No exhaustive intersection or articulated-motion clearance sweep is performed by this module.',
            'All inherited leg, foot, toe and contact meshes are left unchanged.',
        ],
    }
