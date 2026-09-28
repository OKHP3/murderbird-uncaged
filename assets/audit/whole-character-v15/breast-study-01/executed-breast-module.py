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

# Each band is a single broad formed shell with a deliberately swept course.
# The nonuniform spans and alternating sweep leave a central access seam and
# exposed lateral load rails. Values are authoring proposals in metres/radians.
BANDS = [
    # id, inner/outer angle, inner/outer top, inner/outer bottom, sweep, lift, wall
    ("upper",   .20, 1.09, 1.365, 1.325, 1.248, 1.222, -.025, .024, .012),
    ("high",    .17, 1.23, 1.257, 1.226, 1.105, 1.104,  .052, .018, .012),
    ("middle",  .22, 1.20, 1.119, 1.132,  .965,  .984, -.085, .023, .013),
    ("lower",   .28, 1.11,  .977, 1.004,  .815,  .842,  .040, .018, .013),
    ("ventral", .35,  .94,  .831,  .858,  .704,  .744, -.045, .022, .012),
]


def _sample(z):
    z = max(BODY_SECTIONS[0][0], min(BODY_SECTIONS[-1][0], z))
    for a, b in zip(BODY_SECTIONS, BODY_SECTIONS[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return tuple(a[i] + (b[i] - a[i]) * t for i in range(1, 4))
    return BODY_SECTIONS[-1][1:]


def _envelope(z, angle, lift=0.0):
    cy, rx, ry = _sample(z)
    return Vector((math.sin(angle) * (rx + lift),
                   cy - math.cos(angle) * (ry + lift), z))


def _world_points_for_band(spec, side, nu=28, nv=8):
    _, a0, a1, ti, to, bi, bo, sweep, lift, _ = spec
    vertices = []
    for i in range(nu + 1):
        u = i / nu
        angle_mag = a0 + (a1 - a0) * u + sweep * math.sin(math.pi * u)
        top = ti + (to - ti) * u + .006 * math.sin(math.pi * u)
        bottom = bi + (bo - bi) * u - .004 * math.sin(math.pi * u)
        for j in range(nv + 1):
            v = j / nv
            z = top * (1 - v) + bottom * v
            crown = .0035 * math.sin(math.pi * u) * math.sin(math.pi * v)
            vertices.append(_envelope(z, side * angle_mag,
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
        cy, rx, ry = _sample(z)
        outward = Vector((c.x / max(rx, .01),
                          (c.y - cy) / max(ry, .01), 0))
        score += (q - p).cross(r - p).dot(outward)
    if score < 0:
        faces = [tuple(reversed(face)) for face in faces]
    return vertices, faces


def _surface_point(spec, side, u, v):
    _, a0, a1, ti, to, bi, bo, sweep, lift, _ = spec
    angle_mag = a0 + (a1 - a0) * u + sweep * math.sin(math.pi * u)
    top = ti + (to - ti) * u + .006 * math.sin(math.pi * u)
    bottom = bi + (bo - bi) * u - .004 * math.sin(math.pi * u)
    z = top * (1 - v) + bottom * v
    crown = .0035 * math.sin(math.pi * u) * math.sin(math.pi * v)
    return _envelope(z, side * angle_mag, lift + crown)


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
        z = .735 + .605 * t
        for j in range(2):
            angle = side * (.157 + (j * 2 - 1) * .018)
            vertices.append(_envelope(z, angle, .015))
    for i in range(n):
        face = (i * 2, (i + 1) * 2, (i + 1) * 2 + 1, i * 2 + 1)
        faces.append(face if side < 0 else tuple(reversed(face)))
    return _make_mesh(f"V15 breast service-access return {side:+d}",
                      vertices, faces, owner, material, "breast", "frame",
                      thickness=.007, bevel_width=.001)


def _fasteners(owner, material):
    vertices, faces = [], []
    sides = 10
    for spec in BANDS:
        for side in (-1, 1):
            # One inner anchor and one swept outer anchor make each band read
            # as a mounted plate rather than a repeated field of scales.
            for u, v in ((.10, .20), (.88, .78)):
                p = _surface_point(spec, side, u, v)
                n = Vector((math.sin(side * (spec[1] + (spec[2] - spec[1]) * u)),
                            -math.cos(side * (spec[1] + (spec[2] - spec[1]) * u)),
                            .06)).normalized()
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
    return _make_mesh("V15 breast band captive fasteners", vertices, faces,
                      owner, material, "breast", "bearing")


def apply():
    """Replace only the old breastplate exterior field; return scope evidence."""
    owner = bpy.data.objects.get("breastplate")
    assert owner and owner.type == "EMPTY", "V14 breast opening owner is missing"
    plate_mat = bpy.data.materials.get("Neutral / plate")
    frame_mat = bpy.data.materials.get("Neutral / frame")
    bearing_mat = bpy.data.materials.get("Neutral / bearing")
    assert plate_mat and frame_mat and bearing_mat, "V14 neutral construction materials are missing"

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
    for spec in BANDS:
        key = spec[0]
        for side in (-1, 1):
            verts, faces = _world_points_for_band(spec, side)
            obj = _make_mesh(f"V15 breast formed band {side_names[side]} {key}",
                             verts, faces, owner, plate_mat, "breast", "plate",
                             thickness=spec[-1], bevel_width=.002)
            obj["sweptCourseRadians"] = float(spec[7] * side)
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
        "authoringNote": "Owner-resupplied whole-body target and Candidate03 guide breast appearance; all dimensions and hidden construction are reconstructed proposals. July reference scope is head-only and no July breast/body proportions are used.",
    }
