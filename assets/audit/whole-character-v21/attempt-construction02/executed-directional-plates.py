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


def _create_surface(name, owner, region, role, vertices, faces, outer_offset,
                    wall, layer, max_bulge, section=None):
    """Create a finite shell patch with explicit owner and era metadata."""
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(_mesh_material())
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = bpy.data.objects[owner]
    obj.matrix_parent_inverse = obj.parent.matrix_world.inverted()
    _orient_outward(obj, section if section is not None else 0.0)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    solidify = obj.modifiers.new("Finite formed wall", "SOLIDIFY")
    solidify.thickness = wall
    solidify.offset = -1.0
    solidify.use_even_offset = True
    bevel = obj.modifiers.new("Soft plate perimeter", "BEVEL")
    bevel.width = .0006
    bevel.segments = 2
    obj["region"] = region
    obj["surfaceRole"] = role
    obj["exteriorEras"] = ERAS
    obj["constructionClass"] = "proposed-passive"
    obj["authoringRole"] = "Finite formed breast door/backing shell; rigidly attached to breastplate owner"
    obj["geometryStatus"] = "V21 breast hierarchy proposal; clearance and likeness pending"
    obj["sourceEnvelope"] = "V21 attempt-envelope03 shared PROFILE"
    obj["outerOffsetMaxM"] = max_bulge
    obj["layer"] = layer
    return {"name": obj.name, "owner": owner, "region": region,
            "role": role, "eras": ERAS, "wallM": wall,
            "baseOuterOffsetM": outer_offset, "maxBulgeM": max_bulge,
            "layer": layer}


def _smoothstep(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def _shared_edges(angle):
    # This inner backing preserves the union of the old moving central and
    # bilateral guard boundaries while leaving no uncovered shell gaps.
    weight = _smoothstep((abs(angle) - .46) / .74)
    return 1.395 - .035 * weight, .890 + .005 * weight


def _add_backing():
    rows, columns = 56, 48
    verts = []
    faces = []
    for row in range(rows + 1):
        t = row / rows
        for column in range(columns + 1):
            angle = -1.20 + 2.40 * column / columns
            top, bottom = _shared_edges(angle)
            z = top + (bottom - top) * t
            verts.append(tuple(_surface_point(z, angle, -.002)))
    for row in range(rows):
        for column in range(columns):
            i = row * (columns + 1) + column
            faces.append((i, i + columns + 1, i + columns + 2, i + 1))
    return _create_surface("V21 recessed breast door backing", "breastplate",
                           "breast", "inner-backing", verts, faces,
                           -.002, .004, "recessed continuous door backing", 0.0)


def _add_plate(name, center, half_width, top, bottom, offset, wall,
               layer, crown=.001, lean=0.0, end_skew=0.0,
               rows=22, columns=14):
    if offset + crown > .0120001:
        raise ValueError("Breast plate exceeds 12 mm envelope relief: " + name)
    verts = []
    faces = []
    for row in range(rows + 1):
        t = row / rows
        roundness = math.sqrt(max(0.0, math.sin(math.pi * t)))
        taper = .68 + .32 * roundness
        row_center = center + lean * (t - .5) + end_skew * math.sin(math.pi * t)
        for column in range(columns + 1):
            u = 2 * column / columns - 1
            angle = row_center + half_width * taper * u
            z = top + (bottom - top) * t + .004 * (1-u*u) * math.sin(math.pi*t)
            radial = offset + crown * (1-u*u) * math.sin(math.pi*t)
            verts.append(tuple(_surface_point(z, angle, radial)))
    for row in range(rows):
        for column in range(columns):
            i = row * (columns + 1) + column
            faces.append((i, i + columns + 1, i + columns + 2, i + 1))
    return _create_surface(name, "breastplate", "breast", "plate",
                           verts, faces, offset, wall, layer,
                           offset + crown, center)


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
    added = [_add_backing()]

    # The continuous door backing closes the envelope. Fifteen shaped plates
    # sit above it in a staggered upper, load, and lower hierarchy. Course
    # overlap is deliberate; each lower course is radially outboard while its
    # inner face remains separated from the course behind it.
    added.append(_add_plate("V21 breast central load keel", 0.0, .215,
                            1.375, .915, .008, .0030, "central keel",
                            crown=.0030, lean=-.018, end_skew=.010))

    # Short upper transition plates taper the panel field toward the throat.
    upper_panels = (
        (-.43, .190, "right inner"), (.43, .190, "left inner"),
        (-.77, .120, "right shoulder"), (.77, .120, "left shoulder"),
        (-1.045, .120, "right outer"), (1.045, .120, "left outer"),
    )
    for center, width, label in upper_panels:
        added.append(_add_plate("V21 breast upper course " + label,
                                center, width, 1.360, 1.225,
                                .0025, .0015, "upper transition",
                                crown=.0005, lean=center*.035,
                                end_skew=-center*.012))

    # The middle course is longest across the chest load region.
    for center, width, label in ((-.47, .240, "right inboard"),
                                 (.47, .240, "left inboard"),
                                 (-.97, .200, "right access"),
                                 (.97, .200, "left access")):
        added.append(_add_plate("V21 breast load course " + label,
                                center, width, 1.285, 1.040,
                                .0060, .0015, "chest load",
                                crown=.0005, lean=-center*.025,
                                end_skew=center*.009))

    # Shorter lower plates close the taper without extending onto the hinge.
    for center, width, label in ((-.43, .220, "right inboard"),
                                 (.43, .220, "left inboard"),
                                 (-.91, .200, "right access"),
                                 (.91, .200, "left access")):
        added.append(_add_plate("V21 breast lower course " + label,
                                center, width, 1.070, .915,
                                .0105, .0015, "lower taper",
                                crown=.0005, lean=center*.020,
                                end_skew=-center*.008))

    bpy.context.view_layer.update()
    return {
        "status": "V21 directional breast plate proposal; visual and clearance review pending",
        "stagedOut": staged_out,
        "added": added,
        "changedPivots": {},
        "ownership": "The continuous recessed backing and all fifteen plates are separate breastplate-owned rigid meshes; no mesh bridges owners.",
        "construction": "A finite recessed backing covers the complete former central-and-flanking breast guard surface. Fifteen individually shaped finite plates sit above it in short upper transitions, long chest-load courses, and shorter lower taper courses. Their 20–60 mm vertical overlap is separated by deliberately stepped radial layers; maximum outer relief is 11 mm. Positive native X is anatomical left. The central load keel is long and distinct; paired access panels are staggered around it rather than arranged as a uniform grid. The existing fixed shoulder returns and breast-door hardware remain in place.",
        "preserved": ["all EMPTYs and rigid pivot matrices", "all load members and bearing geometry",
                      "all neck/cervical guards, head, wings, legs, feet, guides, materials, and source mesh objects outside the three listed breast guards"],
        "limits": ["Neck/cervical guards remain unchanged because the envelope03 articulation check found crossings; that region requires a separate joint repair before new plates.",
                   "The stepped overlapping courses are a geometry proposal; surface contact, detailed clearance, and owner acceptance remain unverified."]
    }
