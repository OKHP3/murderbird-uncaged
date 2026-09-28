"""Directional, shell-fitted breast armor proposal for whole-character V17.

Run ``apply()`` on a reopened V16 attempt-03 native before saving a new
candidate. This module replaces only the breastplate-owned V15 breast
exterior and its old access returns/anchors. It gently reshapes the upper
anterior profile of the breastplate-owned inner access shell, while keeping
the breast opening owner, body/frame structure, all pivots, and every other
region untouched.

The owner-provided whole-bird image and selected Maker/Mechanic/Candidate03
images guide qualitative construction only. Their perspective does not supply
recoverable dimensions. July's image is a head-only reference and does not
guide this breast proposal.
"""

from pathlib import Path
import hashlib
import math

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


EXPECTED_NATIVE_SHA256 = "3bd4b2e34d086fa15dbc9c06cdbcc0606b02430f9482f9d8d6877d39bec1318a"
ALL_ERAS = "maker,mechanic,builder"
REGION = "breast"
COURSE_COUNT = 8
COURSE_COUNTS = (4, 5, 6, 5, 6, 4, 5, 4)
COURSE_SPACING = .075
COURSE_HALF_LENGTH = .058
COURSE_LIFTS = (.006, .0055, .005, .0045, .004, .004, .0038, .0035)
COURSE_STAGGER = (-.025, .021, -.014, .029, -.021, .017, -.028, .008)
SURFACE_ROWS = 100
SURFACE_COLS = 14
PLATE_ALONG = 22
PLATE_ACROSS = 14

REFERENCE_HASHES = {
    "ownerWholeBird": {
        "path": "context/threads/assets/murderbird-owner-likeness-rejection-2026-09-28/2-Pasted-Image-2.jpg",
        "sha256": "2024330ac948bceb6a8e19d1467bc25882f57aca6d0abba2b072847f2439a8ce",
    },
    "candidate03": {
        "path": "assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png",
        "sha256": "538c51bcdbf5bfce95a0932fdbbb0f5868b446f4985346d15e6cacd32430e633",
    },
    "maker": {
        "path": "assets/img/library/murderbird-unified-maker-clean-candidate-2026-09-06.png",
        "sha256": "93966eb269ae9f8d8d00e05e913cbb23f7656204e6f3fdf7fd26e8a39ca0cbb9",
    },
    "mechanic": {
        "path": "assets/img/library/murderbird-unified-mechanic-candidate-2026-09-06.png",
        "sha256": "0bd7c79510be9eeef024f8861a7576b777a7f5de5710523e8d2ab039d03c65f9",
    },
}


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _scene_pivots():
    return {
        obj.name: (obj.parent.name if obj.parent else None, obj.matrix_world.copy())
        for obj in bpy.data.objects if obj.type == "EMPTY"
    }


def _matrices_equal(a, b, tolerance=1e-8):
    return all(abs(a[row][col] - b[row][col]) <= tolerance
               for row in range(4) for col in range(4))


def _smooth01(value):
    t = max(0.0, min(1.0, value))
    return t * t * (3.0 - 2.0 * t)


def _course_center(bounds, course):
    return bounds["max"][2] - .080 - COURSE_SPACING * course


def _course_half_length(course):
    return COURSE_HALF_LENGTH * (1.0 - .11 * (course % 3) / 2.0)


def _course_layout(course):
    count = COURSE_COUNTS[course]
    result = []
    for column in range(count):
        center = (column + .5) / count + COURSE_STAGGER[course]
        center = max(.09, min(.91, center))
        flank_scale = 1.0 - .24 * max(0.0, (center - .58) / .42)
        half_width = (.575 / count) * flank_scale
        result.append((center, half_width))
    return result


def _round_upper_shell(shell, bounds):
    """Ease the breast shell's top-front ledge into a rounded shoulder."""
    assert shell.data.users == 1, "Refusing to reshape shared breast-shell mesh data"
    inverse = shell.matrix_world.inverted()
    y_mid = (bounds["min"][1] + bounds["max"][1]) * .5
    front_depth = max(.05, y_mid - bounds["min"][1])
    z_start = bounds["max"][2] - .245
    z_span = bounds["max"][2] - z_start
    changed = 0
    for vertex in shell.data.vertices:
        point = shell.matrix_world @ vertex.co
        upper = _smooth01((point.z - z_start) / z_span)
        if upper <= 0.0:
            continue
        front = max(0.0, min(1.0, (y_mid - point.y) / front_depth))
        weight = upper * _smooth01(front / .72)
        if weight <= 0.0:
            continue
        # Recede and narrow only the upper anterior shell, with no transform
        # or pivot movement. This rounds the shelf without closing the throat.
        point.y += .020 * weight
        point.x *= 1.0 - .035 * weight
        point.z -= .008 * weight
        vertex.co = inverse @ point
        changed += 1
    shell.data.update()
    assert changed > 0, "Upper breast shell profile was not touched"
    return {"modifiedVertexCount": changed, "frontInsetMaxM": .020,
            "lateralTaperMaxFraction": .035, "upperEdgeDropMaxM": .008,
            "blendDepthM": .245}


def _evaluated_shell_tree(shell):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = shell.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
        triangles = [tuple(triangle.vertices) for triangle in mesh.loop_triangles]
        assert len(points) > 100 and len(triangles) > 100
        tree = BVHTree.FromPolygons(points, triangles, all_triangles=True, epsilon=0.0)
        bounds = {
            "min": [min(point[axis] for point in points) for axis in range(3)],
            "max": [max(point[axis] for point in points) for axis in range(3)],
        }
        return tree, bounds, len(points), len(triangles)
    finally:
        evaluated.to_mesh_clear()


def _surface_sampler(tree, bounds):
    front_ray = Vector((0.0, 1.0, 0.0))
    cache = {}

    def hit(x, z):
        location, normal, face_index, distance = tree.ray_cast(
            Vector((x, bounds["min"][1] - .75, z)), front_ray, 2.0)
        assert location is not None and normal is not None, (
            f"V16 Breast inner access shell ray missed at x={x:.4f}, z={z:.4f}")
        normal.normalize()
        if normal.y > 0:
            normal.negate()
        return location, normal, face_index, distance

    def half_width(z):
        key = round(max(bounds["min"][2], min(bounds["max"][2], z)), 5)
        if key in cache:
            return cache[key]
        # Measure the front shell's real section from this V16 native. Advance
        # outward until the ray leaves the surface, then bisect the last hit.
        assert hit(0.0, key)[0] is not None, f"Breast shell has no frontal center at z={key:.4f}"
        low, high = 0.0, min(.45, max(abs(bounds["min"][0]), abs(bounds["max"][0])) + .06)
        last_hit = 0.0
        found_miss = False
        for index in range(1, SURFACE_COLS + 1):
            sample = high * index / SURFACE_COLS
            location, _normal, _face, _distance = tree.ray_cast(
                Vector((sample, bounds["min"][1] - .75, key)), front_ray, 2.0)
            if location is None:
                high = sample
                found_miss = True
                break
            last_hit = sample
        if found_miss:
            low = last_hit
            for _ in range(9):
                middle = (low + high) * .5
                location, _normal, _face, _distance = tree.ray_cast(
                    Vector((middle, bounds["min"][1] - .75, key)), front_ray, 2.0)
                if location is None:
                    high = middle
                else:
                    low = middle
        else:
            low = last_hit
        assert low > .045, f"Measured breast shell half-width is implausible at z={key:.4f}: {low}"
        cache[key] = low
        return low

    return hit, half_width


def _create_mesh(name, world_vertices, faces, owner, material, role,
                 thickness, bevel_width=0.0):
    inverse = owner.matrix_world.inverted()
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata([inverse @ point for point in world_vertices], [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = owner
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.data.materials.append(material)
    obj["region"] = REGION
    obj["surfaceRole"] = role
    obj["exteriorEras"] = ALL_ERAS
    obj["constructionClass"] = "inherited-passive"
    obj["proposal"] = True
    if thickness:
        wall = obj.modifiers.new("V17 formed rigid wall", "SOLIDIFY")
        wall.thickness = thickness
        wall.offset = -1.0
        wall.use_even_offset = True
    if bevel_width:
        bevel = obj.modifiers.new("V17 softened formed edge", "BEVEL")
        bevel.width = bevel_width
        bevel.segments = 2
        bevel.limit_method = "ANGLE"
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    return obj


def _oriented_faces(vertices, faces, normals):
    score = 0.0
    for face in faces:
        a, b, c = (vertices[face[index]] for index in range(3))
        normal = normals[face[0]] + normals[face[1]] + normals[face[2]]
        if normal.length_squared:
            normal.normalize()
            score += (b - a).cross(c - a).dot(normal)
    return faces if score >= 0 else [tuple(reversed(face)) for face in faces]


def _plate_geometry(tree, bounds, hit, half_width, side, course, column,
                    center_fraction, half_width_fraction, count):
    center_z = _course_center(bounds, course)
    half_length = _course_half_length(course) * (1.0 - .16 * column / max(1, count - 1))
    runout = (.018 + .009 * ((course + column) % 2)) * (1.0 if (course + column) % 3 else -.55)
    sweep = (-1 if (course + column) % 2 else 1) * (.010 + .004 * (column % 2))
    base_lift = COURSE_LIFTS[course]
    vertices, normals, faces = [], [], []

    for along in range(PLATE_ALONG + 1):
        v = along / PLATE_ALONG
        longitudinal = 2.0 * v - 1.0
        # A broad shoulder narrows progressively to a rounded lower tip.
        # The asymmetric profile creates directional chevrons, not tiles.
        if v < .20:
            width_profile = .88 + .12 * _smooth01(v / .20)
        elif v < .63:
            width_profile = 1.0 - .08 * _smooth01((v - .30) / .33)
        else:
            tip_ratio = .115 + .035 * ((course + column) % 4)
            width_profile = .92 + (tip_ratio - .92) * _smooth01((v - .63) / .37)
        z_center = center_z - half_length * longitudinal
        for across in range(PLATE_ACROSS + 1):
            u = 2.0 * across / PLATE_ACROSS - 1.0
            z = z_center + .006 * (1.0 - u * u) * math.sin(math.pi * v)
            lateral = center_fraction + runout * longitudinal + sweep * math.sin(math.pi * v)
            lateral += u * half_width_fraction * width_profile
            lateral = max(.018, min(.988, lateral))
            x = side * lateral * half_width(z)
            location, normal, _face_index, _distance = hit(x, z)
            crown = .0020 * (1.0 - u * u) * math.sin(math.pi * v)
            alternating_lap = .0008 if (course + column) % 2 == 0 else 0.0
            vertices.append(location + normal * (base_lift + crown + alternating_lap))
            normals.append(normal)

    stride = PLATE_ACROSS + 1
    for along in range(PLATE_ALONG):
        for across in range(PLATE_ACROSS):
            index = along * stride + across
            faces.append((index, index + 1, index + stride + 1, index + stride))
    return vertices, _oriented_faces(vertices, faces, normals)


def _center_keel_geometry(hit, bounds, half_width, side):
    vertices, normals, faces = [], [], []
    steps = 64
    z_low = max(bounds["min"][2] + .085, .685)
    z_high = min(bounds["max"][2] - .045, 1.300)
    assert z_high > z_low + .25
    for index in range(steps + 1):
        t = index / steps
        z = z_low + (z_high - z_low) * t
        # A slim paired keel return borders an open service seam. It is a
        # passive moving breastplate part, not a latch or powered mechanism.
        x_center = side * (.0105 + .002 * math.sin(math.pi * t))
        for offset in (-.0022, .0022):
            x = x_center + offset
            location, normal, _face_index, _distance = hit(x, z)
            vertices.append(location + normal * .010)
            normals.append(normal)
    for index in range(steps):
        a = index * 2
        faces.append((a, a + 2, a + 3, a + 1))
    return vertices, _oriented_faces(vertices, faces, normals)


def _anchor_geometry(hit, half_width, owner):
    vertices, faces = [], []
    sides = 12
    course_names = []
    shell = bpy.data.objects["Breast inner access shell"]
    z_bounds = [shell.matrix_world @ vertex.co for vertex in shell.data.vertices]
    bounds_z = {"min": [0, 0, min(p.z for p in z_bounds)],
                "max": [0, 0, max(p.z for p in z_bounds)]}
    for course, count in enumerate(COURSE_COUNTS):
        layout = _course_layout(course)
        for column, (center_fraction, half_fraction) in enumerate(layout):
            half_length = _course_half_length(course) * (1.0 - .16 * column / max(1, count - 1))
            runout = (.018 + .009 * ((course + column) % 2)) * (1.0 if (course + column) % 3 else -.55)
            sweep = (-1 if (course + column) % 2 else 1) * (.010 + .004 * (column % 2))
            z = _course_center(bounds_z, course) + half_length * .42
            lateral_center = center_fraction + runout * (-.42) + sweep * math.sin(math.pi * .29)
            for side in (-1, 1):
                u = .44 if (course + column) % 2 == 0 else -.44
                for u in (u,):
                    lateral = max(.018, min(.988, lateral_center + u * half_fraction * .76))
                    x = side * lateral * half_width(z)
                    location, normal, _face_index, _distance = hit(x, z)
                    center = location + normal * (COURSE_LIFTS[course] + .0025)
                    axis_x = normal.cross(Vector((0.0, 0.0, 1.0)))
                    if axis_x.length_squared < 1e-8:
                        axis_x = normal.cross(Vector((0.0, 1.0, 0.0)))
                    axis_x.normalize()
                    axis_y = normal.cross(axis_x).normalized()
                    base = len(vertices)
                    for offset, radius in ((-.0012, .0040), (.0014, .0030)):
                        ring_center = center + normal * offset
                        for point in range(sides):
                            angle = math.tau * point / sides
                            vertices.append(ring_center + radius * (
                                axis_x * math.cos(angle) + axis_y * math.sin(angle)))
                    faces.append(tuple(base + point for point in range(sides - 1, -1, -1)))
                    faces.append(tuple(base + sides + point for point in range(sides)))
                    for point in range(sides):
                        nxt = (point + 1) % sides
                        faces.append((base + point, base + nxt,
                                      base + sides + nxt, base + sides + point))
                    course_names.append({"course": course + 1, "column": column + 1, "side": side})
    return vertices, faces, course_names


def apply():
    """Replace V16's broad plate field with fitted, directional lapped plates."""
    native_path = Path(bpy.data.filepath)
    assert native_path.is_file() and _sha256(native_path) == EXPECTED_NATIVE_SHA256, (
        "V17 breast module requires exact V16 attempt-03 native SHA")

    owner = bpy.data.objects.get("breastplate")
    shell = bpy.data.objects.get("Breast inner access shell")
    assert owner and owner.type == "EMPTY", "Breast opening owner is missing"
    assert shell and shell.parent == owner, "Continuous breast inner shell/owner is missing"
    materials = {
        "plate": bpy.data.materials.get("Neutral / plate"),
        "frame": bpy.data.materials.get("Neutral / frame"),
        "bearing": bpy.data.materials.get("Neutral / bearing"),
    }
    assert all(materials.values()), "Expected neutral plate/frame/bearing material definitions are missing"
    material_names_before = sorted(material.name for material in bpy.data.materials)
    pivots_before = _scene_pivots()

    _tree_before, bounds_before, _vertices_before, _triangles_before = _evaluated_shell_tree(shell)
    shell_rounding = _round_upper_shell(shell, bounds_before)
    # The inherited loft has a coarse change of slope across the upper
    # breast. Smooth its actual envelope before projection; smooth shading
    # alone would leave the fitted exterior plates following that shelf.
    rounding = shell.modifiers.new("V17 continuous breast envelope", "SUBSURF")
    rounding.subdivision_type = 'CATMULL_CLARK'
    rounding.levels = 2
    rounding.render_levels = 2
    shell_rounding["envelopeSubdivisionLevels"] = 2
    bpy.context.view_layer.update()
    tree, bounds, shell_vertex_count, shell_triangle_count = _evaluated_shell_tree(shell)
    hit, half_width = _surface_sampler(tree, bounds)
    # Fail early if the actual reopened shell cannot support the authored rows.
    course_centers = [_course_center(bounds, course) for course in range(COURSE_COUNT)]
    for z in course_centers:
        assert bounds["min"][2] < z < bounds["max"][2], f"Course outside actual V16 shell bounds: {z}"
        assert half_width(z) > .12, f"Actual shell section too narrow for breast course at z={z:.3f}"

    def is_retired_breast_exterior(obj):
        if obj.type != "MESH" or obj.parent != owner or obj.get("region") != REGION:
            return False
        if obj.get("surfaceRole") in {"plate", "bearing"}:
            return True
        return obj.name.startswith("V15 breast service-access return")

    retired_objects = sorted((obj for obj in bpy.data.objects if is_retired_breast_exterior(obj)), key=lambda obj: obj.name)
    retired_names = [obj.name for obj in retired_objects]
    assert len(retired_names) == 27, f"Unexpected V16 breast exterior replacement set: {len(retired_names)}"
    assert all(obj.parent == owner for obj in retired_objects)
    assert "Breast inner access shell" not in retired_names
    for obj in retired_objects:
        bpy.data.objects.remove(obj, do_unlink=True)

    created = []
    side_names = {-1: "left", 1: "right"}
    for course, count in enumerate(COURSE_COUNTS):
        layout = _course_layout(course)
        assert len(layout) == count
        for column, (center_fraction, half_fraction) in enumerate(layout):
            for side in (-1, 1):
                name = f"V17 breast directional lamina {course + 1} {column + 1} {side_names[side]}"
                vertices, faces = _plate_geometry(
                    tree, bounds, hit, half_width, side, course, column,
                    center_fraction, half_fraction, count)
                obj = _create_mesh(name, vertices, faces, owner, materials["plate"], "plate",
                                   thickness=.006, bevel_width=.0017)
                obj["course"] = f"directional-{course + 1}"
                obj["directionalSegment"] = f"swept-{column + 1}-of-{count}"
                obj["authoringRole"] = "curved overlapping exterior armor plate"
                obj["lateralRunoutFraction"] = float(
                    (.018 + .009 * ((course + column) % 2))
                    * (1.0 if (course + column) % 3 else -.55))
                created.append(obj)

    for side in (-1, 1):
        name = f"V17 breast center keel return {side_names[side]}"
        vertices, faces = _center_keel_geometry(hit, bounds, half_width, side)
        obj = _create_mesh(name, vertices, faces, owner, materials["frame"], "frame",
                           thickness=.004, bevel_width=.001)
        obj["authoringRole"] = "paired passive moving access-seam/keel return"
        created.append(obj)

    anchor_vertices, anchor_faces, anchors = _anchor_geometry(hit, half_width, owner)
    anchor_obj = _create_mesh("V17 breast captive overlap fasteners", anchor_vertices,
                              anchor_faces, owner, materials["bearing"], "bearing",
                              thickness=0.0)
    anchor_obj["anchorHeadCount"] = len(anchors)
    anchor_obj["authoringRole"] = "low-profile passive panel-lap fasteners"
    created.append(anchor_obj)

    bpy.context.view_layer.update()
    expected_plate_count = sum(COURSE_COUNTS) * 2
    expected_object_count = expected_plate_count + 3
    assert len(created) == expected_object_count, (
        f"Expected {expected_object_count} new V17 breast objects, got {len(created)}")
    assert all(obj.parent == owner for obj in created), "New breast parts must remain breastplate-owned"
    assert all(obj.get("exteriorEras") == ALL_ERAS
               and obj.get("constructionClass") == "inherited-passive"
               and obj.get("proposal") is True for obj in created)
    assert sorted(material.name for material in bpy.data.materials) == material_names_before, (
        "V17 module must not add or alter material definitions")
    pivots_after = _scene_pivots()
    assert set(pivots_before) == set(pivots_after) and all(
        pivots_before[name][0] == pivots_after[name][0]
        and _matrices_equal(pivots_before[name][1], pivots_after[name][1])
        for name in pivots_before), "Breast proposal changed a pivot or joint hierarchy"

    return {
        "status": "V17 curved breast exterior proposal; not a selected or accepted model",
        "sourceNative": {"path": native_path.as_posix(), "sha256": EXPECTED_NATIVE_SHA256},
        "authoringBasis": {
            "ownerTarget": REFERENCE_HASHES["ownerWholeBird"],
            "commonBodyDirection": REFERENCE_HASHES["candidate03"],
            "eraAppearanceGuides": [REFERENCE_HASHES["maker"], REFERENCE_HASHES["mechanic"]],
            "scopeDecision": "An eight-course directional chevron field, with four to six tapered plates per half-course and smaller outer plates, follows the Maker form cue. The upper anterior shell shelf is receded and tapered into a rounder shoulder before plate projection. Dimensions and hidden construction are rebuilt interpretations, not measured from perspective art. July head-only reference was not used for breast proportions.",
        },
        "replacedExistingNames": retired_names,
        "createdNames": [obj.name for obj in created],
        "createdCount": len(created),
        "plateCount": sum(obj.get("surfaceRole") == "plate" for obj in created),
        "keelReturnCount": sum(obj.get("surfaceRole") == "frame" for obj in created),
        "fastenerHeadCount": len(anchors),
        "owner": owner.name,
        "eligibility": {"eras": ALL_ERAS.split(","), "poweredOrSensing": False,
                        "allNewPartsMoveWithBreastOpeningGroup": True},
        "shellFit": {"source": shell.name, "boundsWorldXYZ": bounds,
                     "evaluatedVertices": shell_vertex_count,
                     "evaluatedTriangles": shell_triangle_count,
                     "upperShoulderRounding": shell_rounding,
                     "surfaceSampling": "front-directed rays against the actual evaluated V16 inner shell",
                     "plateStandOffByCourseM": list(COURSE_LIFTS),
                     "plateWallThicknessM": .006,
                     "courseCount": COURSE_COUNT,
                     "platesPerHalfCourse": list(COURSE_COUNTS),
                     "plateCourseCentersWorldZ": course_centers},
        "preserved": [
            "Breastplate opening pivot and parent hierarchy",
            "Breast inner access shell and body/frame construction",
            "All 52 pivots and parent/world matrices",
            "Existing material definitions and every non-target mesh",
            "Shared passive visibility in Maker, Mechanic, and Advanced",
            "Upper-neck geometry and its unresolved breast junction",
        ],
        "limits": [
            "No new native was saved or rendered by this module.",
            "No clearance, access motion, collision, or runtime test is claimed.",
            "This exterior proposal does not close the separately unresolved upper-neck junction.",
        ],
    }
