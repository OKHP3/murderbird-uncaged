"""Formed breast armor for the whole-character V15 proposal.

Breast appearance follows the owner's resupplied whole-body target and
Candidate03; neither is treated as dimensional evidence. The July image's
scope is head-only and contributes no breast/body proportions. This module
replaces only breastplate-owned exterior breast plates and their
old field fixings. The breast opening pivot, continuous inner access shell,
body structure, repair landmarks, and every other owner remain untouched.

Call apply() after loading the pinned V14 scene in Blender. All new parts are
rigidly attached to the existing breastplate owner and shared by all eras.
"""

import math
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


ALL_ERAS = "maker,mechanic,builder"
BODY_SECTIONS = [
    (.68, .09, .11, .13),
    (.76, .075, .18, .20),
    (.88, .045, .255, .265),
    (1.02, .005, .305, .305),
    (1.16, -.04, .325, .305),
    (1.28, -.09, .282, .255),
    (1.37, -.125, .22, .205),
]

# Each course is broken into two or three shaped shells per flank. The field
# nearly covers the measured shell; narrow lap seams and a center service joint
# preserve access without leaving broad areas as unfinished skin.
# Values are authoring proposals in metres/radians.
PANELS = [
    # course, segment, inner/outer angle, top inner/outer, bottom inner/outer,
    # sweep, shell stand-off, wall
    ("upper", "sternal", .018, .72, 1.308, 1.300, 1.222, 1.230, -.030, .026, .012),
    ("upper", "outer",   .66, 1.40, 1.296, 1.292, 1.230, 1.204,  .052, .019, .012),
    ("high", "sternal", .018, .49, 1.228, 1.213, 1.091, 1.080,  .030, .020, .012),
    ("high", "middle",  .42, .98, 1.218, 1.226, 1.100, 1.128, -.058, .027, .013),
    ("high", "outer",   .91, 1.39, 1.224, 1.208, 1.116, 1.101,  .067, .018, .012),
    ("middle", "sternal", .018, .48, 1.108, 1.121, .958, .952, -.042, .026, .013),
    ("middle", "swept",   .41, .96, 1.116, 1.094, .978, .990,  .078, .019, .012),
    ("middle", "outer",   .89, 1.39, 1.102, 1.123, .985, .997, -.052, .025, .012),
    ("lower", "sternal", .025, .53, .975, .986, .811, .802,  .022, .021, .013),
    ("lower", "outer",   .46, 1.39, .986, .999, .835, .842, -.064, .026, .012),
    ("ventral", "sternal", .035, .51, .829, .843, .681, .687, -.040, .027, .012),
    ("ventral", "outer",   .44, 1.32, .840, .856, .719, .726,  .073, .019, .012),
]

_BREAST_SHELL_TREE = None


def _sample(z):
    z = max(BODY_SECTIONS[0][0], min(BODY_SECTIONS[-1][0], z))
    for a, b in zip(BODY_SECTIONS, BODY_SECTIONS[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return tuple(a[i] + (b[i] - a[i]) * t for i in range(1, 4))
    return BODY_SECTIONS[-1][1:]


def _envelope(z, angle, lift=0.0):
    _, rx, _ = _sample(z)
    x = math.sin(angle) * rx
    origin = Vector((x, -1.0, z))
    location, normal, _index, _distance = _BREAST_SHELL_TREE.ray_cast(
        origin, Vector((0, 1, 0)), 2.0)
    assert location is not None, f"V14 inner breast shell projection missed at x={x:.4f}, z={z:.4f}"
    normal.normalize()
    front = Vector((0, -1, 0))
    if normal.dot(front) < 0:
        normal.negate()
    return location + normal * lift


def _world_points_for_band(spec, side, nu=28, nv=8):
    _, _, a0, a1, ti, to, bi, bo, sweep, lift, _ = spec
    vertices = []
    for i in range(nu + 1):
        u = i / nu
        angle_mag = a0 + (a1 - a0) * u + sweep * math.sin(math.pi * u)
        top = ti + (to - ti) * u + .003 * math.sin(math.pi * u)
        bottom = bi + (bo - bi) * u - .009 * math.sin(math.pi * u)
        for j in range(nv + 1):
            v = j / nv
            z = top * (1 - v) + bottom * v
            crown = .0075 * math.sin(math.pi * u) * math.sin(math.pi * v)
            edge_rake = .018 if spec[1] in {"sternal", "middle"} else -.014
            angle_at_v = angle_mag + edge_rake * (v - .5)
            vertices.append(_envelope(z, side * angle_at_v,
                                      lift + crown))

    faces = []
    for i in range(nu):
        for j in range(nv):
            a = i * (nv + 1) + j
            quad = (a, a + nv + 1, a + nv + 2, a + 1)
            faces.append(quad)

    # Orient the skin outward before adding its inward wall.
    score = 0.0
    for face in faces:
        p, q, r = (vertices[face[k]] for k in range(3))
        c = (p + q + r) / 3
        z = c.z
        _, rx, _ = _sample(z)
        angle = math.asin(max(-1.0, min(1.0, c.x / max(rx, .01))))
        outward = Vector((math.sin(angle), -math.cos(angle), 0))
        score += (q - p).cross(r - p).dot(outward)
    if score < 0:
        faces = [tuple(reversed(face)) for face in faces]
    return vertices, faces


def _surface_point(spec, side, u, v):
    _, _, a0, a1, ti, to, bi, bo, sweep, lift, _ = spec
    angle_mag = a0 + (a1 - a0) * u + sweep * math.sin(math.pi * u)
    top = ti + (to - ti) * u + .003 * math.sin(math.pi * u)
    bottom = bi + (bo - bi) * u - .009 * math.sin(math.pi * u)
    z = top * (1 - v) + bottom * v
    crown = .0075 * math.sin(math.pi * u) * math.sin(math.pi * v)
    edge_rake = .018 if spec[1] in {"sternal", "middle"} else -.014
    angle_at_v = angle_mag + edge_rake * (v - .5)
    return _envelope(z, side * angle_at_v, lift + crown)


def _make_mesh(name, world_vertices, faces, owner, material, region,
               role, thickness=0.0, bevel_width=0.0):
    inv = owner.matrix_world.inverted()
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata([inv @ Vector(v) for v in world_vertices], [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = owner
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.data.materials.append(material)
    obj["region"] = region
    obj["surfaceRole"] = role
    obj["exteriorEras"] = ALL_ERAS
    obj["constructionClass"] = "inherited-passive"
    obj["proposal"] = True
    if thickness:
        solid = obj.modifiers.new("Inward formed wall", "SOLIDIFY")
        solid.thickness = thickness
        solid.offset = -1.0
    if bevel_width:
        bevel = obj.modifiers.new("Rolled plate edge", "BEVEL")
        bevel.width = bevel_width
        bevel.segments = 2
        bevel.limit_method = "ANGLE"
    for poly in mesh.polygons:
        poly.use_smooth = True
    return obj


def _access_return(owner, material, side):
    # A shallow continuous lip frames the narrow center service seam. It sits
    # below the plate faces and does not close the opening or add an actuator.
    vertices, faces = [], []
    n = 32
    for i in range(n + 1):
        t = i / n
        z = .692 + .602 * t
        for j in range(2):
            angle = side * (.008 + j * .012)
            vertices.append(_envelope(z, angle, .015))
    for i in range(n):
        face = (i * 2, (i + 1) * 2, (i + 1) * 2 + 1, i * 2 + 1)
        faces.append(face if side < 0 else tuple(reversed(face)))
    return _make_mesh(f"V15 breast service-access return {side:+d}",
                      vertices, faces, owner, material, "breast", "frame",
                      thickness=.005, bevel_width=.0015)


def _fasteners(owner, material):
    vertices, faces = [], []
    sides = 10
    for index, spec in enumerate(PANELS):
        for side in (-1, 1):
            # Captive anchors follow the inner mount and swept outer lap.
            # Offsets vary by plate so the fasteners align to actual panel ends.
            inset = (.12, .17, .22)[index % 3]
            outer = (.84, .89, .93)[index % 3]
            upper_v = (.18, .24, .31)[index % 3]
            lower_v = (.72, .79, .84)[index % 3]
            for u, v in ((inset, upper_v), (outer, lower_v)):
                p = _surface_point(spec, side, u, v)
                x = p.x
                _, n, _index, _distance = _BREAST_SHELL_TREE.ray_cast(
                    Vector((x, -1.0, p.z)), Vector((0, 1, 0)), 2.0)
                n.normalize()
                if n.y > 0:
                    n.negate()
                axis_x = n.cross(Vector((0, 0, 1))).normalized()
                axis_y = n.cross(axis_x).normalized()
                start = len(vertices)
                for depth, radius in ((-.001, .0058), (.0018, .0044)):
                    center = p + n * depth
                    for k in range(sides):
                        a = math.tau * k / sides
                        vertices.append(center + radius *
                                        (axis_x * math.cos(a) + axis_y * math.sin(a)))
                faces.append(tuple(start + k for k in range(sides - 1, -1, -1)))
                faces.append(tuple(start + sides + k for k in range(sides)))
                for k in range(sides):
                    q = (k + 1) % sides
                    faces.append((start + k, start + q,
                                  start + sides + q, start + sides + k))
    obj = _make_mesh("V15 breast panel lap anchors", vertices, faces,
                      owner, material, "breast", "bearing")
    obj["anchorHeadCount"] = len(PANELS) * 2 * 2
    return obj


def apply():
    """Replace only the old breastplate exterior field; return scope evidence."""
    owner = bpy.data.objects.get("breastplate")
    assert owner and owner.type == "EMPTY", "V14 breast opening owner is missing"
    plate_mat = bpy.data.materials.get("Neutral / plate")
    frame_mat = bpy.data.materials.get("Neutral / frame")
    bearing_mat = bpy.data.materials.get("Neutral / bearing")
    assert plate_mat and frame_mat and bearing_mat, "V14 neutral construction materials are missing"

    global _BREAST_SHELL_TREE
    shell = bpy.data.objects.get("Breast inner access shell")
    assert shell and shell.parent == owner, "V14 continuous breast envelope is missing"
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = shell.evaluated_get(depsgraph)
    evaluated_mesh = evaluated.to_mesh()
    try:
        evaluated_mesh.calc_loop_triangles()
        shell_points = [evaluated.matrix_world @ vertex.co for vertex in evaluated_mesh.vertices]
        shell_faces = [tuple(tri.vertices) for tri in evaluated_mesh.loop_triangles]
        _BREAST_SHELL_TREE = BVHTree.FromPolygons(
            shell_points, shell_faces, all_triangles=True, epsilon=0.0)
    finally:
        evaluated.to_mesh_clear()

    def is_breast_exterior(obj):
        return (obj.type == "MESH" and obj.parent == owner
                and obj.get("region") == "breast"
                and obj.get("surfaceRole") in {"plate", "bearing"})

    replaced = sorted(obj.name for obj in bpy.data.objects if is_breast_exterior(obj))
    assert len(replaced) == 129, f"Unexpected V14 breast replacement set: {len(replaced)} meshes"
    assert "Breast inner access shell" in bpy.data.objects
    assert bpy.data.objects["Breast inner access shell"].parent == owner

    for name in replaced:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    created = []
    side_names = {-1: "left", 1: "right"}
    for spec in PANELS:
        course, segment = spec[:2]
        for side in (-1, 1):
            verts, faces = _world_points_for_band(spec, side)
            obj = _make_mesh(f"V15 breast {course} {segment} plate {side_names[side]}",
                             verts, faces, owner, plate_mat, "breast", "plate",
                             thickness=spec[-1], bevel_width=.0035)
            obj["course"] = course
            obj["directionalSegment"] = segment
            obj["sweptCourseRadians"] = float(spec[8] * side)
            created.append(obj)

    for side in (-1, 1):
        created.append(_access_return(owner, frame_mat, side))
    created.append(_fasteners(owner, bearing_mat))
    bpy.context.view_layer.update()

    assert all(obj.parent == owner for obj in created)
    assert all(obj.get("exteriorEras") == ALL_ERAS
               and obj.get("constructionClass") == "inherited-passive"
               for obj in created)
    retained_landmarks = sorted(
        obj.name for obj in bpy.data.objects
        if obj.type == "MESH" and obj.parent
        and obj.parent.name == "industrial-repairs"
        and obj.get("surfaceRole") == "repair")

    return {
        "changedExisting": [],
        "removedExisting": replaced,
        "createdObjects": created,
        "createdNames": [obj.name for obj in created],
        "region": "breast",
        "owner": "breastplate",
        "eligibility": {
            "eras": ALL_ERAS.split(","),
            "constructionClass": "inherited-passive",
            "poweredOrSensing": False,
            "allPartsMoveWithExistingBreastOpeningGroup": True,
        },
        "retainedRepairLandmarks": retained_landmarks,
        "preserved": [
            "breastplate pivot and parent hierarchy",
            "continuous Breast inner access shell",
            "body frame, rails, ribs, power core and processing assemblies",
            "industrial repair landmarks and all other regional meshes",
            "all existing guide curves",
        ],
        "authoringNote": "Owner-resupplied whole-body target and Candidate03 guide breast appearance; all dimensions and hidden construction are reconstructed proposals. July reference scope is head-only and no July breast/body proportions are used. Twenty-four softened, staggered plates are ray-projected to the evaluated V14 inner-shell envelope with finite outward stand-off, narrow service seams, and lap overlaps; only actual lateral frame margins remain exposed.",
    }
