"""V21 directional breast plate study for the shared envelope.

Apply to an already composed envelope03 scene. This module changes no EMPTY,
transform, guide, material, or mechanism. It replaces only the broad moving
breast skin guards and fits finite passive plates to the same shared PROFILE.
Neck/cervical geometry is deliberately untouched pending joint clearance repair.
"""
import bpy
import bmesh
import math
from mathutils import Vector


PROFILE = ((.80, -.175, .130, .205), (.88, -.235, .160, .240),
           (1.00, -.370, .150, .285), (1.16, -.445, .120, .285),
           (1.30, -.420, .050, .255), (1.40, -.385, -.095, .170),
           (1.48, -.360, -.155, .120), (1.56, -.385, -.175, .105),
           (1.63, -.400, -.170, .110))
ERAS = "maker,mechanic,builder"


def _sample(z, column):
    xs = [row[0] for row in PROFILE]
    ys = [row[column] for row in PROFILE]
    if z <= xs[0]:
        return ys[0]
    if z >= xs[-1]:
        return ys[-1]
    h = [b - a for a, b in zip(xs, xs[1:])]
    slopes = [(b - a) / width for a, b, width in zip(ys, ys[1:], h)]
    tangents = [slopes[0]]
    for index in range(1, len(xs) - 1):
        if slopes[index - 1] * slopes[index] <= 0:
            tangents.append(0.0)
        else:
            w1 = 2 * h[index] + h[index - 1]
            w2 = h[index] + 2 * h[index - 1]
            tangents.append((w1 + w2) / (w1 / slopes[index - 1]
                                          + w2 / slopes[index]))
    tangents.append(slopes[-1])
    for index in range(len(xs) - 1):
        if xs[index] <= z <= xs[index + 1]:
            t = (z - xs[index]) / h[index]
            return ((2*t**3 - 3*t**2 + 1) * ys[index]
                    + (t**3 - 2*t**2 + t) * h[index] * tangents[index]
                    + (-2*t**3 + 3*t**2) * ys[index + 1]
                    + (t**3 - t**2) * h[index] * tangents[index + 1])
    raise AssertionError("profile interpolation did not select a segment")


def _surface_point(z, angle, radial_offset):
    front, rear, width = (_sample(z, column) for column in (1, 2, 3))
    center_y = (front + rear) * .5
    radius_y = (rear - front) * .5
    return Vector(((width + radial_offset) * math.sin(angle),
                   center_y - (radius_y + radial_offset) * math.cos(angle),
                   z))


def _mesh_material():
    for name in ("V21 breast central opening keel",
                 "V21 lower swept throat keel",
                 "V21 upper swept throat keel"):
        obj = bpy.data.objects.get(name)
        if obj and obj.type == "MESH" and obj.data.materials:
            return obj.data.materials[0]
    raise RuntimeError("Envelope03 skin material is unavailable")


def _orient_outward(obj, angle):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    if bm.faces:
        face = bm.faces[len(bm.faces) // 2]
        radial = Vector((math.sin(angle), -math.cos(angle), 0.0))
        if face.normal.dot(radial) < 0:
            bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()


def _smoothstep(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


ANGULAR_BOUNDARIES = (-1.20, -.68, -.22, .22, .68, 1.20)
BOUNDARY_SWEEPS = (0.0, .040, -.022, .026, -.034, 0.0)
BREAST_SEAM_M = .0025


def _boundary(index, progress):
    return ANGULAR_BOUNDARIES[index] + BOUNDARY_SWEEPS[index] * math.sin(math.pi * progress)


def _seam_inset(z, angle):
    front, rear, width = (_sample(z, column) for column in (1, 2, 3))
    radius_y = (rear - front) * .5
    arc_scale = math.sqrt((width * math.cos(angle)) ** 2
                          + (radius_y * math.sin(angle)) ** 2)
    return (BREAST_SEAM_M * .5) / max(arc_scale, .05)


def _shared_edges(angle):
    # Preserve the original central guard's longer free edge and the side
    # guards' shorter shared perimeter as one continuous envelope contour.
    outer_weight = _smoothstep((abs(angle) - .46) / (.74))
    return 1.395 - .035 * outer_weight, .890 + .005 * outer_weight


def _add_section(name, section, offset, wall, relief=0.0,
                 rows=48, columns=16):
    """Tile a curved angular sector of the original guard surface."""
    verts = []
    faces = []
    for row in range(rows + 1):
        t = row / rows
        smooth = math.sin(math.pi * t)
        for column in range(columns + 1):
            u = 2 * column / columns - 1
            left = _boundary(section, t)
            right = _boundary(section + 1, t)
            angle = left + (right - left) * (u + 1) * .5
            top, bottom = _shared_edges(angle)
            z = top + (bottom - top) * t + relief * (1 - u*u) * smooth
            if section > 0:
                angle += _seam_inset(z, left) * (1 - u) * .5
            if section < len(ANGULAR_BOUNDARIES) - 2:
                angle -= _seam_inset(z, right) * (1 + u) * .5
            verts.append(tuple(_surface_point(z, angle, offset)))
    for row in range(rows):
        for column in range(columns):
            i = row * (columns + 1) + column
            faces.append((i, i + columns + 1, i + columns + 2, i + 1))

    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.materials.append(_mesh_material())
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = bpy.data.objects["breastplate"]
    obj.matrix_parent_inverse = obj.parent.matrix_world.inverted()
    _orient_outward(obj, (ANGULAR_BOUNDARIES[section]
                          + ANGULAR_BOUNDARIES[section + 1]) * .5)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    solidify = obj.modifiers.new("Finite formed plate wall", "SOLIDIFY")
    solidify.thickness = wall
    solidify.offset = -1.0
    solidify.use_even_offset = True
    bevel = obj.modifiers.new("Soft formed perimeter", "BEVEL")
    bevel.width = .0008
    bevel.segments = 2
    obj["region"] = "breast"
    obj["surfaceRole"] = "plate"
    obj["exteriorEras"] = ERAS
    obj["constructionClass"] = "proposed-passive"
    obj["authoringRole"] = "Directional finite-thickness envelope plate; rigidly attached to one source owner"
    obj["geometryStatus"] = "V21 directional construction proposal; clearance and likeness pending"
    obj["sourceEnvelope"] = "V21 attempt-envelope03 shared PROFILE"
    return {"name": obj.name, "owner": "breastplate", "region": "breast",
            "role": "plate", "eras": ERAS, "wallM": wall,
            "outerOffsetM": offset, "angularSection": [section, section + 1],
            "nominalBoundsRad": [ANGULAR_BOUNDARIES[section],
                                 ANGULAR_BOUNDARIES[section + 1]],
            "seamWidthM": BREAST_SEAM_M,
            "sharedTopBottomContour": True}


def _remove_surface_guards():
    names = (
        "V21 breast central opening keel",
        "V21 anterior breast guard -1", "V21 anterior breast guard 1",
    )
    removed = []
    for name in names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise RuntimeError("Expected envelope03 guard is missing: " + name)
        if obj.type != "MESH" or obj.parent is None:
            raise AssertionError("Unexpected guard object: " + name)
        removed.append({"name": name, "owner": obj.parent.name,
                        "region": obj.get("region"), "role": obj.get("surfaceRole")})
        bpy.data.objects.remove(obj, do_unlink=True)
    return removed


def apply():
    """Replace only broad front guards with owner-isolated directional plates."""
    staged_out = _remove_surface_guards()
    added = []

    # Five continuous longitudinal sections tile the removed three guards.
    # Curved, unequal seams and shallow course relief make the center keel
    # read as the load-bearing plate while retaining full outer-span coverage.
    added.append(_add_section("V21 directional breast outer access right", 0,
                              .004, .0045, relief=.003))
    added.append(_add_section("V21 directional breast inner flank right", 1,
                              .006, .0045, relief=.005))
    added.append(_add_section("V21 directional breast central keel", 2,
                              .010, .0050, relief=.008))
    added.append(_add_section("V21 directional breast inner flank left", 3,
                              .006, .0045, relief=.004))
    added.append(_add_section("V21 directional breast outer access left", 4,
                              .004, .0045, relief=.006))

    bpy.context.view_layer.update()
    return {
        "status": "V21 directional breast plate proposal; visual and clearance review pending",
        "stagedOut": staged_out,
        "added": added,
        "changedPivots": {},
        "ownership": "Every new plate is one breastplate-owned rigid mesh; no mesh bridges owners.",
        "construction": "Five contiguous angular sections cover the original breast guard envelope from -1.2 to +1.2 radians. Curved shared top/bottom contours preserve the original perimeter; curved unequal longitudinal seams have a nominal 2.5 mm tangent gap. Positive native X is anatomical left. A more pronounced central keel and shallower flanking relief create hierarchy without leaving uncovered gaps. Each plate has a finite inward-solidified wall. Existing fixed shoulder returns remain in place.",
        "preserved": ["all EMPTYs and rigid pivot matrices", "all load members and bearing geometry",
                      "all neck/cervical guards, head, wings, legs, feet, guides, materials, and source mesh objects outside the three listed breast guards"],
        "limits": ["Neck/cervical guards remain unchanged because the envelope03 articulation check found crossings; that region requires a separate joint repair before new plates.",
                   "Local ownership tags indicate passive era eligibility, not mechanical validation or owner acceptance."]
    }
