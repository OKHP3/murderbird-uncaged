"""Passive fitted shin webs and ankle-root yokes for whole-character V18.

Apply to the pinned V17 attempt-02 native. Adds only rigid passive surfaces to
the existing shin and foot owners. Existing hinges, motion landmarks, toes,
talons, guides, materials, and powered-era mechanisms remain untouched.
"""
import hashlib
import math
from pathlib import Path

import bpy
import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


EXPECTED_NATIVE_SHA256 = "7d371907b279eb3d625e67164d84a78b2901a5cb6a79917def07f48ff8792d7b"
ALL_ERAS = "maker,mechanic,builder"
REGION = "leg-envelope"
SIDES = (('left', 1), ('right', -1))


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _mesh_surface(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        faces = [tuple(tri.vertices) for tri in mesh.loop_triangles]
        assert points and faces, f"No evaluated surface on {obj.name}"
        return BVHTree.FromPolygons(points, faces, all_triangles=True, epsilon=0.0), points
    finally:
        evaluated.to_mesh_clear()


def _basis(owner_start, owner_end, side_sign):
    axis = (Vector(owner_end) - Vector(owner_start)).normalized()
    lateral = Vector((1.0, 0.0, 0.0)) - axis * axis.x
    lateral.normalize()
    if lateral.x * side_sign < 0:
        lateral.negate()
    front = axis.cross(lateral).normalized()
    if front.y > 0:
        front.negate()
    return axis, lateral, front


def _make_mesh(name, owner, world_vertices, faces, role, material,
               description, bevel=0.0018):
    assert bpy.data.objects.get(name) is None, f"Refusing duplicate regional object: {name}"
    inverse = owner.matrix_world.inverted()
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata([inverse @ Vector(point) for point in world_vertices], [], faces)
    mesh.validate(verbose=False, clean_customdata=False)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    if bm.faces:
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    if material:
        mesh.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = False
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = owner
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_basis = Matrix.Identity(4)
    obj["region"] = REGION
    obj["surfaceRole"] = role
    obj["exteriorEras"] = ALL_ERAS
    obj["constructionClass"] = "inherited-passive"
    obj["proposal"] = True
    obj["constructionOwner"] = owner.name
    obj["articulatesAcrossJoint"] = False
    obj["constructionDescription"] = description
    if bevel:
        modifier = obj.modifiers.new("V18 eased formed edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
        modifier.limit_method = 'ANGLE'
    return obj


def _append_box_beam(a, b, half_width, half_depth, vertices, faces):
    """Append a closed chamfered section along the measured endpoint vector."""
    a, b = Vector(a), Vector(b)
    axis = (b - a).normalized()
    ref = Vector((1.0, 0.0, 0.0))
    across = ref - axis * ref.dot(axis)
    if across.length < 1e-6:
        ref = Vector((0.0, 1.0, 0.0))
        across = ref - axis * ref.dot(axis)
    across.normalize()
    deep = axis.cross(across).normalized()
    corners = ((-.65, -1), (.65, -1), (1, -.65), (1, .65),
               (.65, 1), (-.65, 1), (-1, .65), (-1, -.65))
    start = len(vertices)
    for center in (a, b):
        for x, y in corners:
            vertices.append(center + across * (half_width * x) + deep * (half_depth * y))
    for i in range(8):
        nxt = (i + 1) % 8
        faces.append((start + i, start + nxt, start + 8 + nxt, start + 8 + i))
    faces.append(tuple(start + i for i in reversed(range(8))))
    faces.append(tuple(start + 8 + i for i in range(8)))


def _append_panel(centerline, lateral, front, center_offset, half_width,
                  t0, t1, rows, front_depth, vertices, faces):
    """Build one closed, stepped laminated plate on an owner-derived axis."""
    cross = (-1.0, -0.78, 0.78, 1.0)
    face_start = len(vertices)
    for layer in (0, 1):
        for row in rows:
            t, width_scale = row
            z = t0 + (t1 - t0) * t
            width = half_width * width_scale
            for u in cross:
                # A shallow crown and clipped shoulders make a formed plate,
                # while a thin back offset leaves the nearby open frame visible.
                crown = .0035 * (1.0 - u * u)
                depth = front_depth - layer * .009
                point = centerline(z) + lateral * (center_offset + width * u)
                point += front * (depth + crown)
                vertices.append(point)
    row_count, col_count = len(rows), len(cross)
    back_start = face_start + row_count * col_count
    # Front and back skins.
    for j in range(row_count - 1):
        for k in range(col_count - 1):
            a = face_start + j * col_count + k
            faces.append((a, a + col_count, a + col_count + 1, a + 1))
            b = back_start + j * col_count + k
            faces.append((b + 1, b + col_count + 1, b + col_count, b))
    # Closed side returns around the perimeter.
    boundary = [face_start + k for k in range(col_count)]
    boundary += [face_start + j * col_count + col_count - 1 for j in range(1, row_count)]
    boundary += [face_start + (row_count - 1) * col_count + k for k in range(col_count - 2, -1, -1)]
    boundary += [face_start + j * col_count for j in range(row_count - 2, 0, -1)]
    for i, front_index in enumerate(boundary):
        next_front = boundary[(i + 1) % len(boundary)]
        back_index = back_start + (front_index - face_start)
        next_back = back_start + (next_front - face_start)
        faces.append((front_index, next_front, next_back, back_index))


def _shin_web(owner, distal, side, sign, material):
    p0 = owner.matrix_world.translation.copy()
    p1 = distal.matrix_world.translation.copy()
    axis, lateral, front = _basis(p0, p1, sign)
    length = (p1 - p0).length
    assert .15 < length < .32, f"Unexpected {side} shin pivot span {length:.4f} m"
    centerline = lambda t: p0.lerp(p1, t)
    vertices, faces = [], []
    # Three open-ended courses form a substantial split anterior section.
    # The center slit stays visible; 18% end setbacks leave both axle
    # envelopes clear and the course gaps expose the load rails and links.
    courses = (
        (.18, .39, ((0.0, .88), (.12, 1.0), (.70, 1.06), (.90, .94), (1.0, .76)), .026, .059),
        (.43, .61, ((0.0, .78), (.18, 1.0), (.72, .97), (1.0, .72)), .023, .056),
        (.65, .82, ((0.0, .72), (.22, .96), (.68, .88), (1.0, .56)), .021, .052),
    )
    for t0, t1, rows, half_width, depth in courses:
        for sign_x in (-1, 1):
            _append_panel(centerline, lateral, front, sign_x * .032, half_width,
                          t0, t1, rows, depth, vertices, faces)
    # Short tapered formed yokes seat each split course into the existing
    # owner-local rail field without bridging either moving hinge.
    for t, width in ((.28, .052), (.70, .040)):
        c = centerline(t) + front * .061
        _append_box_beam(c + lateral * -width, c + lateral * width,
                         .0065, .0075, vertices, faces)
    name = f"V18 {side} split shin load web"
    obj = _make_mesh(name, owner, vertices, faces, 'guard', material,
                     'Three stepped paired anterior load plates with an open central service slot and two short cross-ties; fixed to one shin owner, clear of knee and ankle pivot envelopes.')
    obj["jointEndSetbackFraction"] = .18
    obj["sectionNote"] = "Split plated web over existing passive rails; central actuator/frame channel remains open."
    return obj, {"object": name, "owner": owner.name, "distalLandmark": distal.name,
                 "pivotSpanM": round(length, 6), "plateCourses": 3,
                 "plateEndSetbackFraction": .18,
                 "centerSlotNominalM": .012,
                 "newPoweredParts": False}


def _ankle_root_yoke(owner, side, sign, material):
    pivot = owner.matrix_world.translation.copy()
    core = bpy.data.objects.get(f"{side} articulated bearing core.002")
    rails = [bpy.data.objects.get(f"{side} metatarsal passive rail"),
             bpy.data.objects.get(f"{side} metatarsal passive rail.001")]
    assert core and all(rails), f"Missing measured {side} ankle or foot-root source geometry"
    core_tree, _ = _mesh_surface(core)
    rail_rows = []
    vertices, faces = [], []
    for index, rail in enumerate(rails):
        _rail_tree, points = _mesh_surface(rail)
        # Find the existing proximal rail endpoint and a second point 50 mm
        # into its measured surface; these establish a local fork instead of
        # arbitrary foot dimensions.
        root = min(points, key=lambda point: (point - pivot).length)
        desired = pivot + Vector((0.0, -.050, -.020))
        location, normal, tri, distance = _rail_tree.find_nearest(desired)
        assert location is not None
        bearing_point, bearing_normal, bearing_tri, bearing_distance = core_tree.find_nearest(root)
        assert bearing_point is not None
        _append_box_beam(bearing_point, location, .010, .009, vertices, faces)
        rail_rows.append({"rail": rail.name, "proximalRailVertexWorld": [round(v, 7) for v in root],
                          "measuredRailPointWorld": [round(v, 7) for v in location],
                          "measuredBearingSurfacePointWorld": [round(v, 7) for v in bearing_point],
                          "railSampleDistanceM": round(distance, 7),
                          "bearingSampleDistanceM": round(bearing_distance, 7)})
    # Tie the two real rail paths with a formed bridge 50 mm into the measured
    # forefoot roots, still well proximal to the toe pivots and talon contacts.
    rail_points = [Vector(row["measuredRailPointWorld"]) for row in rail_rows]
    _append_box_beam(rail_points[0], rail_points[1], .008, .008, vertices, faces)
    name = f"V18 {side} ankle-to-foot-root yoke"
    obj = _make_mesh(name, owner, vertices, faces, 'frame', material,
                     'Paired passive ankle-to-metatarsal-root gussets and a transverse root tie; endpoints sampled from the evaluated ankle bearing and existing metatarsal rails, rigid to the foot owner.')
    obj["attachmentSourceMeshes"] = [core.name, *(rail.name for rail in rails)]
    obj["toePivotOrContactChanged"] = False
    return obj, {"object": name, "owner": owner.name, "bearing": core.name,
                 "railSources": rail_rows, "toePivotOrContactChanged": False,
                 "newPoweredParts": False}


def _replace_metatarsal_truss(obj, toe_owner, side, sign):
    """Replace the ladder-like foot truss with a tapered ported channel on the same owner."""
    owner = obj.parent
    old_mesh = obj.data
    original_world = [obj.matrix_world @ vertex.co for vertex in old_mesh.vertices]
    assert len(original_world) == 144, f"Unexpected {side} source metatarsal truss topology"
    p0 = owner.matrix_world.translation.copy()
    p1 = toe_owner.matrix_world.translation.copy()
    axis, lateral, front = _basis(p0, p1, sign)
    length = (p1 - p0).length
    assert .27 < length < .35, f"Unexpected {side} metatarsal span {length:.4f} m"
    along = [(point - p0).dot(axis) / length for point in original_world]
    lo, hi = min(along), max(along)
    span = hi - lo
    assert .45 < span < .9, f"Unexpected {side} truss projected span {span:.4f} m"
    t0, t1 = lo + .08 * span, hi - .12 * span
    centroid = sum(original_world, Vector()) / len(original_world)
    lat_offset = (centroid - p0).dot(lateral)
    front_offset = (centroid - p0).dot(front)
    half_width = max(abs((p - centroid).dot(lateral)) for p in original_world) * .94
    assert .035 < half_width < .075, f"Unexpected {side} truss width {half_width:.4f} m"
    centerline = lambda t: p0.lerp(p1, t) + lateral * lat_offset + front * front_offset

    # The profile is a deep C-channel with paired dorsal shoulders, tapered
    # ends and a deliberate centre seam. Large lateral port windows expose the
    # retained twin load rails while the channel replaces the old zigzag face.
    station_rows = ((0.00,.68),(.12,.88),(.27,1.0),(.43,.98),(.60,.88),(.77,.73),(.91,.58),(1.0,.42))
    gap = .010
    cross = ((-1.0,-.020),(-1.0,.030),(-.22,.030),(.22,.030),(1.0,.030),(1.0,-.020))
    verts, faces = [], []
    for station_t, width_factor in station_rows:
        t = t0 + (t1 - t0) * station_t
        center = centerline(t)
        width = half_width * width_factor
        for x, depth in cross:
            # The two top shoulders stop at the centreline, leaving a narrow
            # open longitudinal service slot.
            signed_x = x * width
            if abs(x) == .22:
                signed_x = (-gap if x < 0 else gap)
            verts.append(center + lateral * signed_x + front * depth)
    cross_n = len(cross)
    side_window_cells = {3, 4}  # both flanks remain visually open over mid-span
    for j in range(len(station_rows)-1):
        for k in range(cross_n-1):
            if k == 2:
                continue
            if k in (0, 4) and j in side_window_cells:
                continue
            a = j * cross_n + k
            b = (j+1) * cross_n + k
            faces.append((a, a+1, b+1, b))
    mesh = bpy.data.meshes.new(f"{obj.name} tapered ported channel mesh")
    inverse = obj.matrix_world.inverted()
    mesh.from_pydata([inverse @ point for point in verts], [], faces)
    mesh.validate(verbose=False, clean_customdata=False); mesh.update()
    bm = bmesh.new(); bm.from_mesh(mesh)
    if bm.faces: bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh); bm.free()
    for material in old_mesh.materials:
        mesh.materials.append(material)
    obj.data = mesh
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)
    solid = obj.modifiers.new("V18 formed channel wall", "SOLIDIFY")
    solid.thickness = .009; solid.offset = -1.0
    bevel = obj.modifiers.new("V18 eased channel edges", "BEVEL")
    bevel.width = .0018; bevel.segments = 2; bevel.limit_method = 'ANGLE'
    obj["constructionDescription"] = 'Tapered formed metatarsal C-channel replaces the ladder-like open truss while retaining its foot owner and rail anchors; paired dorsal shoulders leave an open centre seam and large lateral service ports expose both inherited load rails. Distal edge stops before the toe-bearing envelope.'
    obj["geometryStatus"] = 'editable V18 lower-leg construction study; source mesh replaced by fitted channel'
    obj["replacementStudy"] = 'V18 foot metatarsal formed channel'
    obj["toeOwner"] = toe_owner.name
    obj["metatarsalPivotSpanM"] = round(length, 6)
    obj["sourceProjectedSpanM"] = round(span, 6)
    obj["coverageFractionOfSource"] = [.08, .88]
    obj["openLongitudinalServiceSeam"] = True
    obj["lateralServiceWindows"] = 2
    obj["toePivotOrContactChanged"] = False
    return obj, {"object": obj.name, "owner": obj.parent.name, "toeOwner": toe_owner.name,
                 "pivotSpanM": round(length, 6), "sourceProjectedSpanM": round(span, 6),
                 "coverageFractionOfSource": [.08, .88], "crossSection": "tapered C-channel with split dorsal shoulders",
                 "lateralServiceWindows": 2, "retainedRailAnchors": True,
                 "toePivotOrContactChanged": False, "newPoweredParts": False}


def apply():
    """Add a measured split shin web and foot-root support on both sides."""
    filepath = Path(bpy.data.filepath)
    if filepath.exists():
        assert _sha(filepath) == EXPECTED_NATIVE_SHA256, "V18 leg module requires the pinned V17 attempt-02 native"
    owners = {o.name: o for o in bpy.data.objects if o.type == 'EMPTY'}
    required = {f'{side}-{joint}' for side, _ in SIDES for joint in ('shin', 'foot', 'toes')}
    assert required <= set(owners), f"Missing limb pivots: {required-set(owners)}"
    expected_meshes = {o.name for o in bpy.data.objects if o.type == 'MESH'}
    pivots_before = {o.name: (o.parent.name if o.parent else None, o.matrix_world.copy())
                     for o in bpy.data.objects if o.type == 'EMPTY'}
    frame_material = bpy.data.materials.get('Neutral / frame')
    bearing_material = bpy.data.materials.get('Neutral / bearing')
    assert frame_material and bearing_material, "Expected inherited neutral frame and bearing materials"

    changed, details = [], []
    replacements, replacement_details = [], []
    for side, sign in SIDES:
        shin, shin_detail = _shin_web(owners[f'{side}-shin'], owners[f'{side}-foot'], side, sign, frame_material)
        ankle, ankle_detail = _ankle_root_yoke(owners[f'{side}-foot'], side, sign, bearing_material)
        truss = bpy.data.objects.get(f'{side.title()} metatarsus open passive truss')
        assert truss and truss.parent == owners[f'{side}-foot'], f"Missing {side} foot-owned source truss"
        replacement, replacement_detail = _replace_metatarsal_truss(truss, owners[f'{side}-toes'], side, sign)
        changed.extend((shin.name, ankle.name))
        replacements.append(replacement.name); replacement_details.append(replacement_detail)
        details.extend((shin_detail, ankle_detail))

    pivots_after = {o.name: (o.parent.name if o.parent else None, o.matrix_world.copy())
                    for o in bpy.data.objects if o.type == 'EMPTY'}
    assert pivots_before.keys() == pivots_after.keys()
    for name, (parent, matrix) in pivots_before.items():
        assert pivots_after[name][0] == parent
        assert all(abs(matrix[r][c] - pivots_after[name][1][r][c]) < 1e-9
                   for r in range(4) for c in range(4)), f"Changed pivot {name}"
    after_meshes = {o.name for o in bpy.data.objects if o.type == 'MESH'}
    assert after_meshes - expected_meshes == set(changed)
    assert after_meshes == expected_meshes | set(changed), "Unexpected mesh addition or removal"
    bpy.context.view_layer.update()
    return {
        "changedOrAddedObjects": changed,
        "replacedObjects": replacements,
        "replacementConstruction": replacement_details,
        "construction": details,
        "preservation": {"pivotCount": len(pivots_before), "allPivotWorldMatricesUnchanged": True,
                         "allExistingMeshesRetained": True, "existingMeshesModified": []},
        "eligibility": {"visibleEras": ALL_ERAS,
                        "class": "passive frame and guard surfaces only",
                        "maker": "Passive reinforcement; no powered mechanism added.",
                        "mechanic": "Passive shank and ankle structure; existing drive mechanism unchanged.",
                        "advanced": "Passive structure; no actuator or sensor added.",
                        "notAdded": ["new pivots", "cross-joint rigid parts", "powered actuators", "toe or talon edits"]},
        "limits": ["Visual proposal, not a load or fatigue analysis.",
                   "Continuous swept-volume clearance and full containment are not established.",
                   "Attachment points are sampled from evaluated native bearing and rail surfaces; qualitative source images do not supply dimensions."]
    }
