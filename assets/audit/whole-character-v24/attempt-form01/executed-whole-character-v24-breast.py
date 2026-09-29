"""V24 breast-only plate hierarchy proposal for the exact V23 Form03 native.

This replaces only the V23 breastplate-owned exterior courses and recessed
door. It retains the existing breast opening, hinge, frame, body returns,
neck, pivots, materials, and every other region. The whole-bird image guides
qualitative construction only; it is not a dimensioned source.
"""
from pathlib import Path
import hashlib
import math
import runpy

import bpy
import bmesh
from mathutils import Matrix, Vector


EXPECTED_NATIVE_SHA256 = "66b6ff8c17e468c0e1ab7874728a3aea889a5630fd25dafc3392d954a1343e62"
ALL_ERAS = "maker,mechanic,builder"
REGION = "breast"
PROFILE = ((.78,-.165,.125,.170),(.87,-.247,.139,.210),
 (.99,-.365,.128,.252),(1.12,-.425,.095,.280),
 (1.245,-.417,.038,.258),(1.335,-.382,-.035,.205),
 (1.410,-.352,-.106,.145),(1.48,-.379,-.160,.116),
 (1.555,-.428,-.213,.109),(1.635,-.446,-.256,.100))

# Reconstructed bands keep the existing V23 outer envelope and finite field.
# Course segmentation varies to make a broad sternum hierarchy and smaller
# flank armor, while each gap exposes a continuous recessed backing.
COURSES = (
    {"top": 1.354, "bottom": 1.274, "segments": ((-1.18,-.785),(-.777,-.405),(-.397,-.006),(.006,.397),(.405,.777),(.785,1.18)), "tip": .024, "flow": -.025, "offset": .0020},
    {"top": 1.262, "bottom": 1.171, "segments": ((-1.18,-.982),(-.974,-.696),(-.688,-.397),(-.389,-.006),(.006,.389),(.397,.688),(.696,.974),(.982,1.18)), "tip": .012, "flow": .020, "offset": .0024},
    {"top": 1.159, "bottom": 1.062, "segments": ((-1.18,-.792),(-.784,-.412),(-.404,-.006),(.006,.404),(.412,.784),(.792,1.18)), "tip": .032, "flow": -.015, "offset": .0028},
    {"top": 1.050, "bottom": .951, "segments": ((-1.18,-.944),(-.936,-.666),(-.658,-.372),(-.364,-.006),(.006,.364),(.372,.658),(.666,.936),(.944,1.18)), "tip": .017, "flow": .027, "offset": .0024},
    {"top": .939, "bottom": .844, "segments": ((-1.18,-.792),(-.784,-.405),(-.397,-.006),(.006,.397),(.405,.784),(.792,1.18)), "tip": .026, "flow": -.020, "offset": .0020},
)


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _pivot_snapshot():
    return {o.name: (o.parent.name if o.parent else None, o.matrix_world.copy())
            for o in bpy.data.objects if o.type == "EMPTY"}


def _matrices_equal(a, b, tolerance=1e-8):
    return all(abs(a[r][c] - b[r][c]) <= tolerance
               for r in range(4) for c in range(4))


def _mesh_signature(obj):
    digest = hashlib.sha256()
    digest.update((obj.parent.name if obj.parent else "").encode())
    digest.update(repr(tuple(tuple(round(obj.matrix_world[r][c], 12) for c in range(4))
                             for r in range(4))).encode())
    digest.update(repr(tuple(tuple(round(v.co[i], 12) for i in range(3))
                             for v in obj.data.vertices)).encode())
    digest.update(repr(tuple(tuple(poly.vertices) for poly in obj.data.polygons)).encode())
    digest.update(repr(tuple(mat.name if mat else None for mat in obj.data.materials)).encode())
    digest.update(repr(tuple(sorted((key, repr(value)) for key, value in obj.items()))).encode())
    return digest.hexdigest()


def _make_panel(name, top, bottom, start, end, course, column, owner, material,
                envelope_point, sample):
    rows, cols = 24, 28
    verts, faces = [], []
    mid = (start + end) * .5
    # Broad inner panels remain broad; each flank piece narrows with angle.
    flank = max(0.0, (abs(mid) - .32) / .86)
    end_taper = .020 + .014 * flank
    side = 1.0 if mid >= 0 else -1.0
    flow = course["flow"] * side
    for j in range(rows + 1):
        t = j / rows
        ease_t = t * t * (3.0 - 2.0 * t)
        for k in range(cols + 1):
            u = 2.0 * k / cols - 1.0
            # Different lower contours distinguish sternum guards from the
            # smaller flank guards without changing the common envelope.
            top_edge = top - end_taper * abs(u) ** 1.25 + side * .014 * u
            lower_edge = bottom - course["tip"] * (1.0 - u * u) ** 1.7 + side * .020 * u
            z = top_edge + (lower_edge - top_edge) * t
            z += .0025 * (1.0 - u * u) * math.sin(math.pi * t)
            angle = mid + ((end - start) * .5) * u + flow * (ease_t - .5)
            angle += .006 * math.sin(math.pi * t) * (1.0 - u * u) * (1 if column % 2 else -1)
            edge_fade = math.sin(math.pi * t) ** .55 * max(.02, math.sin(math.pi * k / cols)) ** .45
            radial = course["offset"] * edge_fade
            verts.append(tuple(envelope_point(z, angle, radial)))
    stride = cols + 1
    for j in range(rows):
        for k in range(cols):
            a = j * stride + k
            faces.append((a, a + stride, a + stride + 1, a + 1))

    inverse = owner.matrix_world.inverted()
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata([inverse @ Vector(v) for v in verts], [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = owner
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.data.materials.append(material)
    obj["region"] = REGION
    obj["surfaceRole"] = "plate"
    obj["exteriorEras"] = ALL_ERAS
    obj["constructionClass"] = "inherited-passive"
    obj["proposal"] = True
    obj["courseIndex"] = course["courseIndex"]
    obj["panelKind"] = "sternum" if flank < .08 else "lateral"
    obj["authoringRole"] = "formed breast armor panel seated over recessed continuous backing"
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    solid = obj.modifiers.new("V24 finite breast panel wall", "SOLIDIFY")
    solid.thickness = .0022
    solid.offset = -1.0
    solid.use_even_offset = True
    bevel = obj.modifiers.new("V24 eased panel edge", "BEVEL")
    bevel.width = .0006
    bevel.segments = 2
    bevel.limit_method = "ANGLE"
    return obj


def apply(envelope_helper=None):
    """Replace only the V23 breast door and its repeated exterior courses."""
    native = Path(bpy.data.filepath)
    assert native.is_file() and _sha256(native) == EXPECTED_NATIVE_SHA256, (
        "V24 breast module requires the pinned V23 Form03 native")
    root = Path(__file__).resolve().parents[2]
    helper_path = Path(envelope_helper) if envelope_helper else root / "scripts/regions/whole-character-v21-envelope.py"
    envelope = runpy.run_path(str(helper_path))
    envelope["PROFILE"] = PROFILE
    # runpy returns the module globals mapping, while function globals remain
    # attached to the executed module namespace. Update the actual functions
    # used by guard/envelope_point so every ray and surface uses V23's profile.
    for function_name in ("sample", "envelope_point", "guard"):
        envelope[function_name].__globals__["PROFILE"] = PROFILE
        assert tuple(envelope[function_name].__globals__["PROFILE"]) == PROFILE
    envelope_point = envelope["envelope_point"]
    sample = envelope["sample"]
    guard = envelope["guard"]

    owner = bpy.data.objects.get("breastplate")
    assert owner and owner.type == "EMPTY"
    pivot_before = _pivot_snapshot()
    materials_before = sorted(material.name for material in bpy.data.materials)
    plate_prefix = "V23 breast formed course "
    removed = sorted(o.name for o in bpy.data.objects if
                     o.type == "MESH" and o.parent == owner and
                     (o.name.startswith(plate_prefix) or o.name == "V23 recessed breast door"))
    # Current Form03 source has 46 repeated plates and one recessed door.
    expected_old = 47
    assert len(removed) == expected_old, f"Unexpected V23 breast replacement set: {len(removed)}"
    assert all("V23 breast formed course " in name or name == "V23 recessed breast door" for name in removed)
    plate_material = bpy.data.objects["V23 breast formed course 01 plate 01"].data.materials[0]
    assert plate_material is not None
    skin_material = plate_material
    retained_before = {o.name: _mesh_signature(o) for o in bpy.data.objects
                       if o.type == "MESH" and o.name not in removed}
    for name in removed:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    created = []
    backing = guard("V24 continuous recessed breast backing", 1.354, .840, 0, 1.17,
                    "breastplate", skin_material, off=-.006, wall=.004,
                    tip_depth=.010, edge_slope=0)
    backing["region"] = REGION
    backing["surfaceRole"] = "shell"
    backing["exteriorEras"] = ALL_ERAS
    backing["constructionClass"] = "inherited-passive"
    backing["proposal"] = True
    backing["authoringRole"] = "continuous recessed inner backing visible through panel seams"
    created.append(backing)

    for course_index, course in enumerate(COURSES, start=1):
        for panel_index, (start, end) in enumerate(course["segments"], start=1):
            name = f"V24 breast course {course_index:02} panel {panel_index:02}"
            obj = _make_panel(name, course["top"], course["bottom"], start, end,
                              {**course, "courseIndex": course_index},
                              panel_index, owner, skin_material,
                              envelope_point, sample)
            obj["lateralSpanRadians"] = end - start
            obj["courseTopM"] = course["top"]
            obj["courseBottomM"] = course["bottom"]
            created.append(obj)

    bpy.context.view_layer.update()
    assert len(created) == 35, f"Expected backing plus 34 shaped panels, got {len(created)}"
    assert all(obj.parent == owner for obj in created)
    assert all(obj.get("exteriorEras") == ALL_ERAS and
               obj.get("constructionClass") == "inherited-passive" and
               obj.get("proposal") is True for obj in created)
    assert sorted(material.name for material in bpy.data.materials) == materials_before
    retained_after = {o.name: _mesh_signature(o) for o in bpy.data.objects
                      if o.type == "MESH" and o.name not in {obj.name for obj in created}}
    assert retained_after == retained_before, "A non-target mesh, transform, material, or metadata changed"
    pivot_after = _pivot_snapshot()
    assert set(pivot_before) == set(pivot_after) and all(
        pivot_before[name][0] == pivot_after[name][0] and
        _matrices_equal(pivot_before[name][1], pivot_after[name][1]) for name in pivot_before), (
        "V24 breast module changed a pivot")
    for obj in created:
        for vertex in obj.data.vertices:
            assert all(math.isfinite(c) for c in vertex.co), f"Non-finite vertex in {obj.name}"
        evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            assert len(mesh.loop_triangles) > 0, f"No evaluated triangles in {obj.name}"
            assert all(math.isfinite(c) for vertex in mesh.vertices for c in vertex.co), (
                f"Non-finite evaluated geometry in {obj.name}")
        finally:
            evaluated.to_mesh_clear()

    return {
        "status": "V24 breast-only visual proposal; not selected or accepted",
        "sourceNativeSha256": EXPECTED_NATIVE_SHA256,
        "removedNames": removed,
        "createdNames": [obj.name for obj in created],
        "createdCount": len(created),
        "plateCount": len(created) - 1,
        "panelKinds": {"sternum": sum(obj.get("panelKind") == "sternum" for obj in created),
                       "lateral": sum(obj.get("panelKind") == "lateral" for obj in created)},
        "owner": "breastplate",
        "retainedMeshSignaturesExact": len(retained_before),
        "eligibility": {"eras": ALL_ERAS.split(","), "poweredOrSensing": False},
        "construction": "Five variable courses: broad sternum panels, smaller shaped lateral panels, and a continuous recessed backing. Open seams reveal backing; course boundaries are separated rather than stacked in accumulating radial layers.",
        "limits": ["Dimensions are qualitative reconstruction, not recovered from the perspective reference.",
                   "This module does not check opening motion, collision, or runtime integration.",
                   "The rest of the breast-to-neck junction remains outside this edit."],
    }
