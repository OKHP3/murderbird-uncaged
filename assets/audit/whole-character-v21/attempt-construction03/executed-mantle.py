"""V21 compact flightless mantle and forewing-shield construction proposal.

Apply to an already composed envelope03 scene. The existing owner-specific
backings, bearings, left repair stop, axes, and pivots remain in place. Only
the repeated broad covert/plume skins are replaced with finite shaped panels
sampled directly from their actual rigid-owner backing surfaces.
"""
import bpy
import bmesh
import math
from mathutils import Vector


ERAS = "maker,mechanic,builder"
GRID_COLUMNS = 37
OUTER_ROWS = 18
EXPECTED_SKIN_COUNTS = {
    "left-mantle": 25,
    "right-mantle": 25,
    "left-wing-shield": 17,
    "right-wing-shield": 17,
}


def _smooth(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def _world_point(backing, row, col):
    data = backing.data
    row = max(0.0, min(OUTER_ROWS - 1.0, row))
    col = max(0.0, min(GRID_COLUMNS - 1.0, col))
    r0 = int(math.floor(row))
    c0 = int(math.floor(col))
    r1 = min(OUTER_ROWS - 1, r0 + 1)
    c1 = min(GRID_COLUMNS - 1, c0 + 1)
    tr, tc = row - r0, col - c0

    def vertex(r, c):
        return backing.matrix_world @ data.vertices[r * GRID_COLUMNS + c].co

    a = vertex(r0, c0).lerp(vertex(r0, c1), tc)
    b = vertex(r1, c0).lerp(vertex(r1, c1), tc)
    return a.lerp(b, tr)


def _outward_normal(backing, row, col, point):
    eps = .25
    row_tangent = (_world_point(backing, row + eps, col)
                   - _world_point(backing, row - eps, col)).normalized()
    col_tangent = (_world_point(backing, row, col + eps)
                   - _world_point(backing, row, col - eps)).normalized()
    normal = col_tangent.cross(row_tangent).normalized()
    center = sum((_world_point(backing, row, c)
                  for c in range(GRID_COLUMNS)), Vector((0.0, 0.0, 0.0))) / GRID_COLUMNS
    radial = Vector((point.x - center.x, point.y - center.y, 0.0)).normalized()
    if normal.dot(radial) < 0:
        normal.negate()
    return normal


def _mesh_material(source):
    if source.data.materials:
        return source.data.materials[0]
    raise RuntimeError("Wing skin material is missing: " + source.name)


def _add_surface(name, owner, backing, region, role, row_start, row_end,
                 col_start, col_end, offset, wall, crown, layer,
                 row_sweep=0.0, col_sweep=0.0, rows=16, columns=12,
                 material=None):
    vertices = []
    faces = []
    center_col = (col_start + col_end) * .5
    for j in range(rows + 1):
        t = j / rows
        rounded = math.sqrt(max(0.0, math.sin(math.pi * t)))
        row = row_start + (row_end - row_start) * t + row_sweep * math.sin(math.pi*t)
        taper = .74 + .26 * rounded
        row_col_center = center_col + col_sweep * math.sin(math.pi*t)
        for k in range(columns + 1):
            u = 2.0 * k / columns - 1.0
            col = row_col_center + (col_end - col_start) * .5 * taper * u
            point = _world_point(backing, row, col)
            normal = _outward_normal(backing, row, col, point)
            bulge = crown * (1.0 - u*u) * math.sin(math.pi*t)
            vertices.append(tuple(point + normal * (offset + bulge)))
    for j in range(rows):
        for k in range(columns):
            i = j * (columns + 1) + k
            faces.append((i, i + columns + 1, i + columns + 2, i + 1))

    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(material or _mesh_material(backing))
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = bpy.data.objects[owner]
    obj.matrix_parent_inverse = obj.parent.matrix_world.inverted()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    sample = _world_point(backing, (row_start + row_end)*.5, center_col)
    normal = _outward_normal(backing, (row_start + row_end)*.5, center_col, sample)
    if bm.faces and bm.faces[len(bm.faces)//2].normal.dot(normal) < 0:
        bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    solidify = obj.modifiers.new("Finite formed wing plate wall", "SOLIDIFY")
    solidify.thickness = wall
    solidify.offset = -1.0
    solidify.use_even_offset = True
    bevel = obj.modifiers.new("Soft perimeter", "BEVEL")
    bevel.width = .0007
    bevel.segments = 2
    obj["region"] = region
    obj["surfaceRole"] = role
    obj["exteriorEras"] = ERAS
    obj["constructionClass"] = "proposed-passive"
    obj["authoringRole"] = "Finite formed flightless mantle/shield surface on one existing rigid owner"
    obj["geometryStatus"] = "V21 mantle construction proposal; clearance and likeness pending"
    obj["sourceBacking"] = backing.name
    obj["sourceGrid"] = [OUTER_ROWS, GRID_COLUMNS]
    obj["radialLayerM"] = offset
    obj["maximumCrownM"] = crown
    return {"name": name, "owner": owner, "region": region, "role": role,
            "eras": ERAS, "sourceBacking": backing.name,
            "sourceGridRows": [row_start, row_end],
            "sourceGridColumns": [col_start, col_end],
            "radialLayerM": offset, "wallM": wall,
            "maxOutwardM": offset + crown, "layer": layer}


def _skin_objects():
    targets = []
    counts = {name: 0 for name in EXPECTED_SKIN_COUNTS}
    for obj in list(bpy.data.objects):
        if obj.type != "MESH" or obj.parent is None:
            continue
        owner = obj.parent.name
        shoulder_skin = owner in ("left-mantle", "right-mantle") and " shoulder covert " in obj.name
        shield_skin = owner in ("left-wing-shield", "right-wing-shield") and " distal mantle plume " in obj.name
        if shoulder_skin or shield_skin:
            if obj.get("surfaceRole") != "plate":
                raise AssertionError("Unexpected mantle skin role: " + obj.name)
            targets.append(obj)
            counts[owner] += 1
    if counts != EXPECTED_SKIN_COUNTS:
        raise AssertionError("Unexpected source mantle skin inventory: " + repr(counts))
    return targets, counts


def apply():
    targets, source_counts = _skin_objects()
    empties_before = {o.name: (o.parent.name if o.parent else None,
                               o.matrix_world.copy())
                      for o in bpy.data.objects if o.type == "EMPTY"}
    materials_before = sorted(m.name for m in bpy.data.materials)
    shoulder_source = bpy.data.objects.get("left shoulder covert 1 3")
    if shoulder_source is None:
        raise RuntimeError("Expected shoulder covert source mesh is missing")
    shoulder_material = _mesh_material(shoulder_source)
    wing_source = bpy.data.objects.get("left distal mantle plume 0 3")
    if wing_source is None:
        raise RuntimeError("Expected distal shield source mesh is missing")
    wing_material = _mesh_material(wing_source)

    backings = {}
    for owner in EXPECTED_SKIN_COUNTS:
        suffix = "left-mantle" if owner == "left-mantle" else (
            "right-mantle" if owner == "right-mantle" else owner)
        backing = bpy.data.objects.get("left profiled mantle backing v4 " + suffix)
        if owner.startswith("right-"):
            backing = bpy.data.objects.get("right profiled mantle backing v4 " + suffix)
        if backing is None or backing.type != "MESH" or len(backing.data.vertices) != 1332:
            raise AssertionError("Expected actual V21 owner backing grid is missing: " + owner)
        if backing.parent is None or backing.parent.name != owner:
            raise AssertionError("Backing has unexpected rigid owner: " + owner)
        backings[owner] = backing

    staged_out = []
    for obj in targets:
        staged_out.append({"name": obj.name, "owner": obj.parent.name,
                           "region": obj.get("region"), "role": obj.get("surfaceRole")})
        bpy.data.objects.remove(obj, do_unlink=True)

    added = []
    # The compact shoulder mantle uses staggered, smaller shingles. Each row
    # is radially separated from the row behind it, while the source backing
    # remains continuous beneath narrow joints and deliberate openings.
    courses = (
        # The outside face clears its backing by more than the inward wall
        # thickness, so the first course cannot bury half its own section.
        ("upper", 2.0, 6.5, .0020, .0015, .0005,
         (9.5, 13.5, 17.8, 22.2, 26.5)),
        ("middle", 5.5, 10.0, .0040, .0015, .0005,
         (9.0, 13.2, 17.1, 21.4, 25.3, 29.0)),
        ("lower", 9.0, 13.5, .0070, .0015, .0005,
         (8.8, 12.7, 17.3, 21.0, 24.1, 27.2)),
        ("root", 12.5, 16.0, .0100, .0015, .0005,
         (10.0, 14.3, 18.4, 22.1, 25.5)),
    )
    for owner, side_label in (("left-mantle", "left"), ("right-mantle", "right")):
        backing = backings[owner]
        material = shoulder_material
        for course, row_start, row_end, offset, wall, crown, boundaries in courses:
            for index in range(len(boundaries) - 1):
                added.append(_add_surface(
                    "V21 " + side_label + " mantle " + course + " shingle " + str(index + 1),
                    owner, backing, "shoulder", "plate", row_start, row_end,
                    boundaries[index], boundaries[index + 1], offset, wall,
                    crown, "shoulder-" + course,
                    row_sweep=(index % 2 - .5) * .18,
                    col_sweep=(index % 2 - .5) * .22,
                    rows=14, columns=10, material=material))
        # A broad, rounded leading guard occupies only the leading angular
        # margin and stays on the mantle owner, away from the elbow child.
        added.append(_add_surface(
            "V21 " + side_label + " mantle leading guard", owner, backing,
            "shoulder", "guard", 2.0, 16.0, 4.8, 8.3,
            .0120, .0010, 0.0, "leading-edge-guard",
            row_sweep=.20, col_sweep=.12, rows=28, columns=12,
            material=material))

    # The elbow-owned shield is kept short and tapered beneath its native
    # shoulder/elbow pivot. It leaves the lower truss exposed rather than
    # extending an ornamental plume toward the ankle.
    shield_courses = (
        ("upper", 4.2, 6.7, .0020, .0015, .0005,
         (10.5, 15.5, 20.5, 26.0)),
        ("lower", 6.2, 8.8, .0060, .0015, .0005,
         (12.0, 17.8, 23.5, 27.0)),
    )
    for owner, side_label in (("left-wing-shield", "left"), ("right-wing-shield", "right")):
        backing = backings[owner]
        for course, row_start, row_end, offset, wall, crown, boundaries in shield_courses:
            for index in range(len(boundaries) - 1):
                added.append(_add_surface(
                    "V21 " + side_label + " forewing " + course + " shield " + str(index + 1),
                    owner, backing, "wing", "plate", row_start, row_end,
                    boundaries[index], boundaries[index + 1], offset, wall,
                    crown, "short-shield-" + course,
                    row_sweep=(index % 2 - .5) * .10,
                    col_sweep=(index % 2 - .5) * .16,
                    rows=12, columns=10, material=wing_material))
        added.append(_add_surface(
            "V21 " + side_label + " forewing leading guard", owner, backing,
            "wing", "guard", 5.3, 9.0, 5.6, 9.8,
            .0100, .0015, .0005, "forewing-leading-edge",
            row_sweep=.10, col_sweep=.12, rows=18, columns=12,
            material=wing_material))

    bpy.context.view_layer.update()
    empties_after = {o.name: (o.parent.name if o.parent else None,
                              o.matrix_world.copy())
                     for o in bpy.data.objects if o.type == "EMPTY"}
    assert set(empties_before) == set(empties_after)
    for name in empties_before:
        assert empties_before[name][0] == empties_after[name][0]
        assert all(abs(empties_before[name][1][r][c] - empties_after[name][1][r][c]) < 1e-9
                   for r in range(4) for c in range(4))
    assert materials_before == sorted(m.name for m in bpy.data.materials)
    assert all(entry["maxOutwardM"] <= .0120001 for entry in added)
    return {
        "status": "V21 compact flightless mantle/forewing construction proposal; visual and articulation clearance pending",
        "sourceSkinCounts": source_counts,
        "stagedOut": staged_out,
        "added": added,
        "changedPivots": {},
        "preserved": ["all EMPTY names, parents, and world matrices",
                      "left anatomical stop and repair bracket", "all shoulder/elbow bearings and load members",
                      "both profiled owner backing shells", "breast, neck, head, legs, feet, guides, and material definitions"],
        "construction": "Repeated broad coverts and distal plumes are replaced by staggered smaller mantle shingles, one finite leading guard per mantle owner, and short tapered shield courses with separate leading guards per elbow owner. Each new shell is sampled from its actual rigid-owner backing grid; no plate bridges shoulder and wing-shield owners. The elbow truss below the compact shield remains exposed.",
        "limits": ["Source grids provide an authoring surface, not proof of plate seating or cross-owner clearance.",
                   "The left repair stop and travel limits are preserved, but these new surfaces have not been checked through articulation.",
                   "All new parts are passive era geometry; this does not establish owner likeness acceptance."]
    }
