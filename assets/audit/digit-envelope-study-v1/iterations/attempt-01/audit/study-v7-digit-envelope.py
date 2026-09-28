"""Create a native-only V7 digit-envelope study and matched clay views.

Only the twelve Digit inner link mesh datasets change. Twelve separate dorsal
guards are added, one under each proximal/distal owner. The frozen V7 source is
never saved over and no GLB/runtime output is made.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import shutil
import subprocess

import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/models/uncaged-alignment-v7/murderbird-alignment-v7.blend"
SOURCE_GLB = ROOT / "assets/models/uncaged-alignment-v7/murderbird-alignment-v7.glb"
SOURCE_INVENTORY = ROOT / "assets/models/uncaged-alignment-v7/alignment-inventory.json"
REFERENCE = ROOT / "assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png"
MODEL_DIR = ROOT / "assets/models/uncaged-digit-envelope-study-v1"
AUDIT_DIR = ROOT / "assets/audit/digit-envelope-study-v1"
EXPECTED = {
    "native": "a8fccaf024a096678415215029b34cae8270b348da2301b8872a34e72c75ed3f",
    "glb": "1c82874b86af6b493ac380536de6af72a30fafa3a4b0ebb3d8790f56ffc03018",
}
LINK_PREFIX = "Digit inner link"
ALL_ERAS = "maker,mechanic,builder"
MATRIX_TOLERANCE = 1e-8
BOUND_TOLERANCE = 1e-7
THREE_QUARTER = (-4.0, -6.0, 0.6)
SIDE = (-6.0, -0.1, 0.32)
TARGET = (0.0, -0.1, 0.31)
ORTHO_SCALE = 0.98


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix_rows(matrix):
    return [[float(matrix[r][c]) for c in range(4)] for r in range(4)]


def max_matrix_delta(a, b):
    return max(abs(float(a[r][c]) - float(b[r][c])) for r in range(4) for c in range(4))


def material_signature(material):
    nodes, links = [], []
    if material.use_nodes and material.node_tree:
        for node in material.node_tree.nodes:
            inputs = []
            for socket in node.inputs:
                if not socket.enabled or not hasattr(socket, "default_value"):
                    continue
                value = socket.default_value
                try:
                    value = [float(v) for v in value]
                except TypeError:
                    value = float(value) if isinstance(value, (int, float)) else str(value)
                inputs.append([socket.identifier, value])
            nodes.append({"name": node.name, "type": node.bl_idname,
                          "inputs": sorted(inputs, key=lambda item: item[0])})
        links = sorted([link.from_node.name, link.from_socket.name,
                        link.to_node.name, link.to_socket.name]
                       for link in material.node_tree.links)
    payload = {"diffuseColor": [float(v) for v in material.diffuse_color],
               "metallic": float(material.metallic), "roughness": float(material.roughness),
               "useNodes": bool(material.use_nodes),
               "nodes": sorted(nodes, key=lambda item: item["name"]), "links": links}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def mesh_signature(obj):
    mesh = obj.data
    data = {
        "vertices": [tuple(round(float(c), 9) for c in v.co) for v in mesh.vertices],
        "edges": [tuple(e.vertices) for e in mesh.edges],
        "polygons": [(tuple(p.vertices), int(p.material_index), bool(p.use_smooth)) for p in mesh.polygons],
        "materials": [material_signature(m) if m else None for m in mesh.materials],
    }
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def object_props(obj):
    return {key: repr(obj[key]) for key in obj.keys()}


def visibility(obj):
    return {"hideViewport": bool(obj.hide_viewport), "hideRender": bool(obj.hide_render),
            "hideSelect": bool(obj.hide_select), "hideInViewLayer": bool(obj.hide_get())}


def snapshot():
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    empties, meshes, curves = {}, {}, {}
    for obj in bpy.data.objects:
        if obj.type == "EMPTY":
            empties[obj.name] = {"parent": obj.parent.name if obj.parent else None,
                                 "matrix": matrix_rows(obj.matrix_world), "visibility": visibility(obj)}
        elif obj.type == "MESH":
            meshes[obj.name] = {"parent": obj.parent.name if obj.parent else None,
                                "matrix": matrix_rows(obj.matrix_world), "mesh": mesh_signature(obj),
                                "props": object_props(obj), "visibility": visibility(obj)}
        elif obj.type == "CURVE":
            spline_records = []
            for spline in obj.data.splines:
                points = []
                collection = spline.bezier_points if spline.type == "BEZIER" else spline.points
                for point in collection:
                    record = {"co": [round(float(c), 9) for c in point.co],
                              "radius": round(float(point.radius), 9), "tilt": round(float(point.tilt), 9)}
                    if spline.type == "BEZIER":
                        record["handles"] = [[round(float(c), 9) for c in point.handle_left],
                                              [round(float(c), 9) for c in point.handle_right]]
                        record["handleTypes"] = [point.handle_left_type, point.handle_right_type]
                    points.append(record)
                spline_records.append({"type": spline.type, "cyclic": bool(spline.use_cyclic_u),
                                       "resolution": spline.resolution_u, "points": points})
            curves[obj.name] = {"parent": obj.parent.name if obj.parent else None,
                                "matrix": matrix_rows(obj.matrix_world),
                                "dataName": obj.data.name,
                                "dataDigest": hashlib.sha256(repr((obj.data.dimensions, obj.data.resolution_u,
                                                                  obj.data.bevel_depth, obj.data.bevel_resolution,
                                                                  obj.data.bevel_mode, spline_records)).encode()).hexdigest(),
                                "props": object_props(obj), "visibility": visibility(obj)}
    materials = {material.name: material_signature(material) for material in bpy.data.materials}
    return {"empties": empties, "meshes": meshes, "curves": curves, "materials": materials}


def object_bounds(obj):
    points = [Vector(v.co) for v in obj.data.vertices]
    return {"min": [min(p[i] for p in points) for i in range(3)],
            "max": [max(p[i] for p in points) for i in range(3)]}


def endpoint_rings(obj):
    points = [Vector(v.co) for v in obj.data.vertices]
    require(len(points) == 24 and len(obj.data.polygons) == 14,
            f"Unexpected source digit-link topology; refusing guessed remesh: {obj.name}")
    ordered_y = sorted(p.y for p in points)
    gaps = [(ordered_y[i + 1] - ordered_y[i], i) for i in range(len(ordered_y) - 1)]
    _, split = max(gaps)
    require(split == 11, f"Expected two twelve-vertex attachment rings: {obj.name}")
    distal = [p for p in points if p.y <= ordered_y[split] + 1e-8]
    proximal = [p for p in points if p.y >= ordered_y[split + 1] - 1e-8]
    require(len(distal) == len(proximal) == 12, f"Digit link attachment ring count differs: {obj.name}")

    def sort_ring(ring):
        cx = sum(p.x for p in ring) / len(ring)
        cz = sum(p.z for p in ring) / len(ring)
        return sorted(ring, key=lambda p: math.atan2(p.z - cz, p.x - cx))

    return sort_ring(proximal), sort_ring(distal)


def endpoint_record(obj):
    proximal, distal = endpoint_rings(obj)
    world = obj.matrix_world.copy()
    return {
        "owner": obj.parent.name,
        "objectWorldMatrix": matrix_rows(world),
        "proximalRingWorld": sorted([tuple(round(c, 9) for c in (world @ p)) for p in proximal]),
        "distalRingWorld": sorted([tuple(round(c, 9) for c in (world @ p)) for p in distal]),
        "bounds": object_bounds(obj),
    }


def retained_endpoint_membership(obj, prior):
    current = {(round(float(v.co.x), 9), round(float(v.co.y), 9), round(float(v.co.z), 9))
               for v in obj.data.vertices}
    for key in ("proximalRingWorld", "distalRingWorld"):
        # Prior world coordinates are mapped back to this object's local frame.
        inverse = obj.matrix_world.inverted()
        expected = {tuple(round(float(c), 9) for c in (inverse @ Vector(point))) for point in prior[key]}
        require(len(expected) == 12 and expected.issubset(current),
                f"Digit link lost/repositioned an original attachment ring vertex: {obj.name}/{key}")


def check_closed_mesh(mesh, label):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    try:
        require(all(edge.is_manifold for edge in bm.edges), f"Non-manifold/crossed boundary in {label}")
        require(abs(bm.calc_volume(signed=True)) > 1e-10, f"Zero-volume or inverted collapsed mesh: {label}")
    finally:
        bm.free()


def super_sign(value, exponent):
    return math.copysign(abs(value) ** exponent, value)


def ring_center_and_radius(ring):
    cx = sum(p.x for p in ring) / len(ring)
    cy = sum(p.y for p in ring) / len(ring)
    cz = sum(p.z for p in ring) / len(ring)
    rx = max(abs(p.x - cx) for p in ring)
    rz = max(abs(p.z - cz) for p in ring)
    return (cx, cy, cz, rx, rz)


def segment_profile(obj):
    proximal, distal = endpoint_rings(obj)
    a = ring_center_and_radius(proximal)
    b = ring_center_and_radius(distal)
    angle_start = math.atan2(proximal[0].z - a[2], proximal[0].x - a[0])
    return proximal, distal, a, b, angle_start


def make_digit_link_mesh(obj, profile):
    proximal, distal, a, b, angle_start = profile
    # Original attachment rings stay byte-position-identical. Between them,
    # the link waist is tapered and faceted with six sampled cross-sections.
    factors = [(0.0, 1.0), (0.12, 0.91), (0.30, 0.80), (0.50, 0.77),
               (0.70, 0.80), (0.88, 0.91), (1.0, 1.0)]
    rings = [proximal]
    for t, factor in factors[1:-1]:
        cx = a[0] + (b[0] - a[0]) * t
        cy = a[1] + (b[1] - a[1]) * t
        cz = a[2] + (b[2] - a[2]) * t
        rx = (a[3] + (b[3] - a[3]) * t) * factor
        rz = (a[4] + (b[4] - a[4]) * t) * factor
        ring = []
        for i in range(12):
            angle = angle_start + 2 * math.pi * i / 12
            sx = super_sign(math.cos(angle), 0.72)
            sz = super_sign(math.sin(angle), 0.72)
            ring.append(Vector((cx + rx * sx, cy, cz + rz * sz)))
        rings.append(ring)
    rings.append(distal)
    # Corresponding vertices must preserve angular order across every ring;
    # matching endpoints by coordinates alone would allow a half-twist.
    centers = []
    for ring in rings:
        centers.append((sum(p.x for p in ring) / len(ring), sum(p.z for p in ring) / len(ring)))
    ring_angles = [[math.atan2(p.z - cz, p.x - cx) for p in ring]
                   for ring, (cx, cz) in zip(rings, centers)]
    for ring_index, angles in enumerate(ring_angles):
        unwrapped = [angles[0]]
        for angle in angles[1:]:
            while angle <= unwrapped[-1]:
                angle += 2 * math.pi
            unwrapped.append(angle)
        require(all(0 < (unwrapped[i + 1] - unwrapped[i]) < math.pi / 2 for i in range(11)) and
                2 * math.pi - (unwrapped[-1] - unwrapped[0]) < math.pi / 2,
                f"Ring vertex angular order is inconsistent in {obj.name}/ring{ring_index}")
    for ring_index in range(len(rings) - 1):
        differences = [abs(ring_angles[ring_index + 1][i] - ring_angles[ring_index][i]) for i in range(12)]
        differences = [min(d % (2 * math.pi), 2 * math.pi - (d % (2 * math.pi))) for d in differences]
        require(max(differences) < math.pi / 3,
                f"Corresponding link-ring indices twist/cross: {obj.name}/span{ring_index}")
    vertices = [tuple(p) for ring in rings for p in ring]
    faces = [tuple(reversed(range(12))), tuple((len(rings) - 1) * 12 + i for i in range(12))]
    for r in range(len(rings) - 1):
        for i in range(12):
            j = (i + 1) % 12
            faces.append((r * 12 + i, r * 12 + j, (r + 1) * 12 + j, (r + 1) * 12 + i))
    mesh = bpy.data.meshes.new(obj.name + " | tapered faceted study data")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    for material in obj.data.materials:
        mesh.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = False
    check_closed_mesh(mesh, obj.name)
    return mesh


def link_profile(profile, t):
    _, _, a, b, _ = profile
    factors = [(0.0, 1.0), (0.12, 0.91), (0.30, 0.80), (0.50, 0.77),
               (0.70, 0.80), (0.88, 0.91), (1.0, 1.0)]
    for (ta, fa), (tb, fb) in zip(factors, factors[1:]):
        if ta <= t <= tb:
            q = (t - ta) / (tb - ta)
            factor = fa + (fb - fa) * q
            break
    else:
        factor = 1.0
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3)) + (
        (a[3] + (b[3] - a[3]) * t) * factor,
        (a[4] + (b[4] - a[4]) * t) * factor)


def make_dorsal_guard(owner, link, profile, material):
    # A closed 5.5 mm-thick crown per segment, sunk 4 mm and standing 1.5 mm
    # proud. The two end gaps leave the existing hinge visible.
    stations = [0.18, 0.34, 0.50, 0.66, 0.82]
    angles = [-1.00, -0.66, -0.33, 0.0, 0.33, 0.66, 1.00]
    vertices, faces = [], []
    for offset in (0.0015, -0.004):
        for t in stations:
            cx, cy, cz, rx, rz = link_profile(profile, t)
            for angle in angles:
                sx = super_sign(math.sin(angle), 0.72)
                cz_factor = super_sign(math.cos(angle), 0.72)
                dx, dz = rx * sx, rz * cz_factor
                length = math.sqrt(dx * dx + dz * dz)
                scale = (length + offset) / length
                vertices.append((cx + dx * scale, cy, cz + dz * scale))
    row = len(angles)
    layer_size = len(stations) * row
    # Outer skin, inner skin, and closed perimeter walls.
    for s in range(len(stations) - 1):
        for a in range(row - 1):
            i = s * row + a
            faces.append((i, i + 1, i + row + 1, i + row))
            j = layer_size + i
            faces.append((j, j + row, j + row + 1, j + 1))
    perimeter = []
    perimeter.extend(range(row))
    perimeter.extend(s * row + row - 1 for s in range(1, len(stations)))
    perimeter.extend((len(stations) - 1) * row + a for a in range(row - 2, -1, -1))
    perimeter.extend(s * row for s in range(len(stations) - 2, 0, -1))
    for p, i in enumerate(perimeter):
        j = perimeter[(p + 1) % len(perimeter)]
        faces.append((i, j, layer_size + j, layer_size + i))
    mesh = bpy.data.meshes.new(link.name + " dorsal guard study data")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    check_closed_mesh(mesh, link.name + " dorsal guard")
    side, _, digit, joint = owner.name.split("-")
    obj = bpy.data.objects.new(f"{side} digit {digit} {joint} dorsal guard", mesh)
    obj.parent = owner
    obj.matrix_parent_inverse = link.matrix_parent_inverse.copy()
    obj.matrix_basis = link.matrix_basis.copy()
    obj.data.materials.append(material)
    obj["region"] = "foot"
    obj["surfaceRole"] = "plate"
    obj["exteriorEras"] = ALL_ERAS
    obj["constructionClass"] = "inherited-passive"
    obj["geometryStatus"] = "native digit-envelope study proposal"
    obj["pairedLink"] = link.name
    return obj


def configure_clay_views(scene):
    old_camera = scene.camera
    shading = scene.display.shading
    old_state = {
        "engine": scene.render.engine, "resolution_x": scene.render.resolution_x,
        "resolution_y": scene.render.resolution_y, "resolution_percentage": scene.render.resolution_percentage,
        "file_format": scene.render.image_settings.file_format,
        "film_transparent": scene.render.film_transparent,
        "world_color": tuple(scene.world.color) if scene.world else None,
        "light": shading.light, "studio_light": shading.studio_light, "color_type": shading.color_type,
        "show_shadows": shading.show_shadows, "show_cavity": shading.show_cavity,
        "cavity_type": shading.cavity_type, "ridge": shading.curvature_ridge_factor,
        "valley": shading.curvature_valley_factor, "background_type": shading.background_type,
    }
    scene.render.engine = "BLENDER_WORKBENCH"
    shading = scene.display.shading
    shading.light = "STUDIO"
    shading.studio_light = "paint.sl"
    shading.color_type = "MATERIAL"
    shading.show_shadows = True
    shading.show_cavity = True
    shading.cavity_type = "BOTH"
    shading.curvature_ridge_factor = 1.15
    shading.curvature_valley_factor = 1.1
    shading.background_type = "WORLD"
    scene.world.color = (0.12, 0.13, 0.14)
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    camera_data = bpy.data.cameras.new("Temporary digit envelope comparison camera")
    camera = bpy.data.objects.new("Temporary digit envelope comparison camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = ORTHO_SCALE
    return camera, old_state, old_camera


def restore_render_state(scene, camera, old_state, old_camera):
    scene.camera = old_camera
    camera_data = camera.data
    bpy.data.objects.remove(camera, do_unlink=True)
    bpy.data.cameras.remove(camera_data)
    scene.render.engine = old_state["engine"]
    scene.render.resolution_x = old_state["resolution_x"]
    scene.render.resolution_y = old_state["resolution_y"]
    scene.render.resolution_percentage = old_state["resolution_percentage"]
    scene.render.image_settings.file_format = old_state["file_format"]
    scene.render.film_transparent = old_state["film_transparent"]
    if scene.world and old_state["world_color"] is not None:
        scene.world.color = old_state["world_color"]
    shading = scene.display.shading
    shading.light = old_state["light"]
    shading.studio_light = old_state["studio_light"]
    shading.color_type = old_state["color_type"]
    shading.show_shadows = old_state["show_shadows"]
    shading.show_cavity = old_state["show_cavity"]
    shading.cavity_type = old_state["cavity_type"]
    shading.curvature_ridge_factor = old_state["ridge"]
    shading.curvature_valley_factor = old_state["valley"]
    shading.background_type = old_state["background_type"]


def render_pair(scene, camera, out_dir, prefix):
    images = []
    for name, position in (("three-quarter", THREE_QUARTER), ("side", SIDE)):
        camera.location = position
        camera.rotation_euler = (Vector(TARGET) - camera.location).to_track_quat("-Z", "Y").to_euler()
        path = out_dir / f"{prefix}-{name}.png"
        require(not path.exists(), f"Refusing to overwrite comparison image: {path}")
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        images.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
                       "sha256": sha256(path), "camera": list(position), "target": list(TARGET),
                       "projection": "orthographic", "orthoScale": ORTHO_SCALE})
    return images


def main():
    for path in (SOURCE, SOURCE_GLB, SOURCE_INVENTORY, REFERENCE):
        require(path.is_file(), f"Missing digit study input: {path}")
    require(sha256(SOURCE) == EXPECTED["native"] and sha256(SOURCE_GLB) == EXPECTED["glb"],
            "V7 source identity differs from the frozen study input")
    require(not MODEL_DIR.exists(), f"Refusing to overwrite digit study model folder: {MODEL_DIR}")
    require(not AUDIT_DIR.exists(), f"Refusing to overwrite digit study audit folder: {AUDIT_DIR}")
    v7_inventory = json.loads(SOURCE_INVENTORY.read_text())
    require(len(v7_inventory["pivots"]) == 51 and len(v7_inventory["parts"]) == 687,
            "V7 inventory does not match frozen source identity")
    reference_sha = sha256(REFERENCE)

    MODEL_DIR.mkdir(parents=True, exist_ok=False)
    AUDIT_DIR.mkdir(parents=True, exist_ok=False)
    script_snapshot = AUDIT_DIR / "study-v7-digit-envelope.py"
    shutil.copy2(Path(__file__).resolve(), script_snapshot)
    require(sha256(script_snapshot) == sha256(Path(__file__).resolve()), "Study script snapshot changed while copied")

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    scene.frame_set(1)
    bpy.context.view_layer.update()
    before = snapshot()
    require(len(before["empties"]) == 51 and len(before["meshes"]) == 687,
            "V7 native scene counts differ from the pinned inventory")
    links = [obj for obj in bpy.data.objects if obj.type == "MESH" and obj.name.startswith(LINK_PREFIX)]
    require(len(links) == 12 and len({obj.name for obj in links}) == 12,
            "Expected exactly twelve existing digit inner-link meshes")
    link_names = {obj.name for obj in links}
    require({obj.parent.name for obj in links} == {
        f"{side}-digit-{digit}-{joint}" for side in ("left", "right")
        for digit in (1, 2, 3) for joint in ("proximal", "distal")},
        "Digit inner-link owner set differs from six proximal/distal digit pairs")
    for obj in links:
        require(len(obj.data.uv_layers) == 0 and len(obj.data.color_attributes) == 0 and
                obj.data.shape_keys is None, f"Unexpected source attributes on link mesh; needs bespoke preservation: {obj.name}")
    attachment_records = {obj.name: endpoint_record(obj) for obj in links}
    other_before_images = []
    camera, old_render_state, old_camera = configure_clay_views(scene)
    before_images = render_pair(scene, camera, AUDIT_DIR, "v7-before")
    restore_render_state(scene, camera, old_render_state, old_camera)

    plate_material = bpy.data.materials.get("Neutral / plate")
    require(plate_material is not None, "Frozen V7 neutral plate material is missing")
    modified = {}
    added = []
    link_by_owner = {}
    source_profiles = {link.name: segment_profile(link) for link in links}
    for link in links:
        link_by_owner[link.parent.name] = link
        profile = source_profiles[link.name]
        new_data = make_digit_link_mesh(link, profile)
        old_data = link.data
        link.data = new_data
        bpy.data.meshes.remove(old_data)
        modified[link.name] = link
        guard = make_dorsal_guard(link.parent, link, profile, plate_material)
        scene.collection.objects.link(guard)
        added.append(guard)

    bpy.context.view_layer.update()
    after = snapshot()
    require(after["empties"] == before["empties"], "Digit study changed or reparented a pivot")
    require(after["curves"] == before["curves"], "Digit study changed control curves")
    require(after["materials"] == before["materials"], "Digit study created or changed a source material")
    require(set(after["meshes"]) == set(before["meshes"]) | {obj.name for obj in added},
            "Digit study added/deleted objects outside the exact guard allowlist")
    require(set(modified) == link_names, "Digit study modified objects outside the twelve-link allowlist")
    for name, record in before["meshes"].items():
        if name in modified:
            current = after["meshes"][name]
            for field in ("parent", "matrix", "props", "visibility"):
                require(current[field] == record[field], f"Digit link object state changed beyond mesh data: {name}/{field}")
            continue
        require(after["meshes"][name] == record, f"Unchanged source mesh differs: {name}")
    require(all(after["meshes"][obj.name]["parent"] == obj.parent.name for obj in added),
            "Added dorsal guard owner mapping differs")
    require(len(added) == 12, "Expected one closed dorsal guard per proximal/distal digit owner")
    talons = {name: before["meshes"][name]["mesh"] for name in before["meshes"]
              if name.endswith("tapered claw sheath")}
    require(talons and all(after["meshes"][name]["mesh"] == signature for name, signature in talons.items()),
            "A talon mesh changed during digit-envelope study")

    attachment_after = {}
    for name, prior in attachment_records.items():
        obj = bpy.data.objects[name]
        require(prior["owner"] == obj.parent.name and
                max_matrix_delta(prior["objectWorldMatrix"], matrix_rows(obj.matrix_world)) <= MATRIX_TOLERANCE,
                f"Digit link transform/owner changed: {name}")
        retained_endpoint_membership(obj, prior)
        current_bounds = object_bounds(obj)
        require(all(abs(prior["bounds"][axis][i] - current_bounds[axis][i]) <= BOUND_TOLERANCE
                    for axis in ("min", "max") for i in range(3)),
                f"Digit link bounding/contact dimensions changed: {name}")
        attachment_after[name] = {"owner": obj.parent.name, "objectWorldMatrix": matrix_rows(obj.matrix_world),
                                  "retainedOriginalEndpointVertices": {"proximal": 12, "distal": 12},
                                  "bounds": current_bounds}

    native_path = MODEL_DIR / "murderbird-uncaged-digit-envelope-study-v1.blend"
    pending = MODEL_DIR / ".building-digit-envelope-study-v1.blend"
    require(not native_path.exists() and not pending.exists(), "Refusing to replace a prior digit study output")
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(pending))
    require(pending.is_file(), "Native digit study save failed")
    pending.replace(native_path)
    bpy.ops.wm.open_mainfile(filepath=str(native_path))
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    after_reload = snapshot()
    require(after_reload == after, "Saved and reloaded digit study differs from the pre-save snapshot")
    for name, prior in attachment_records.items():
        current_obj = bpy.data.objects[name]
        require(current_obj.parent.name == prior["owner"] and
                max_matrix_delta(matrix_rows(current_obj.matrix_world), prior["objectWorldMatrix"]) <= MATRIX_TOLERANCE,
                f"Reload changed an attachment transform: {name}")
        retained_endpoint_membership(current_obj, prior)
    scene = bpy.context.scene
    camera, old_render_state, old_camera = configure_clay_views(scene)
    after_images = render_pair(scene, camera, AUDIT_DIR, "study-after")
    restore_render_state(scene, camera, old_render_state, old_camera)

    require(sha256(SOURCE) == EXPECTED["native"] and sha256(SOURCE_GLB) == EXPECTED["glb"],
            "Frozen V7 source changed during the study")
    record = {
        "capturedAtUtc": datetime.now(timezone.utc).isoformat(),
        "status": "native-only geometry proposal; not owner accepted",
        "source": {"native": {"path": str(SOURCE.relative_to(ROOT)), "sha256": EXPECTED["native"], "bytes": SOURCE.stat().st_size},
                   "glb": {"path": str(SOURCE_GLB.relative_to(ROOT)), "sha256": EXPECTED["glb"], "bytes": SOURCE_GLB.stat().st_size},
                   "inventorySha256": sha256(SOURCE_INVENTORY)},
        "reference": {"path": str(REFERENCE.relative_to(ROOT)), "sha256": reference_sha,
                      "use": "Viewed candidate03 image for toe construction language: segmented dorsal armor over separate articulated toe links; not dimensional metrology."},
        "studyScript": {"path": str(script_snapshot.relative_to(ROOT)), "sha256": sha256(script_snapshot)},
        "outputNative": {"path": str(native_path.relative_to(ROOT)), "bytes": native_path.stat().st_size,
                         "sha256": sha256(native_path)},
        "blenderVersion": bpy.app.version_string,
        "changedLinkMeshes": sorted(link_names),
        "addedGuards": [{"name": obj.name, "parent": obj.parent.name, "pairedLink": obj["pairedLink"],
                         "region": obj["region"], "surfaceRole": obj["surfaceRole"], "eras": obj["exteriorEras"],
                         "constructionClass": obj["constructionClass"], "geometryStatus": obj["geometryStatus"],
                         "vertices": len(obj.data.vertices), "faces": len(obj.data.polygons)}
                        for obj in sorted([bpy.data.objects[g.name] for g in added], key=lambda item: item.name)],
        "preservation": {
            "pivotCount": len(after["empties"]), "allPivotsAndWorldMatricesUnchanged": after["empties"] == before["empties"],
            "unmodifiedMeshCount": len(before["meshes"]) - len(modified),
            "allUnmodifiedMeshesExact": all(after["meshes"][name] == before["meshes"][name]
                                             for name in before["meshes"] if name not in modified),
            "controlCurvesExact": after["curves"] == before["curves"],
            "materialsExact": after["materials"] == before["materials"],
            "all12ExistingAttachmentRingsAndBoundsExact": True,
            "allSixTalonsExact": True,
            "newGuardCount": len(added),
        },
        "attachments": attachment_records,
        "rendering": {"engine": "Blender Workbench neutral-material clay", "resolution": [1400, 1000],
                      "cameraTarget": list(TARGET), "orthoScale": ORTHO_SCALE,
                      "views": {"before": before_images, "after": after_images}},
        "scopeLimits": [
            "Separate native Blender geometry study only; no GLB, app/runtime selection, motion contact, or mechanical validation.",
            "End-ring world positions and object bounds were retained exactly; the study does not prove load capacity or grasp performance.",
            "Dorsal guards use inherited passive classification and existing plate material; they add no powered hardware.",
            "Control curves and all other source objects/materials/pivots are preserved; inherited V7 curves do not regenerate these new guards.",
        ],
    }
    with (AUDIT_DIR / "study-receipt.json").open("x") as stream:
        json.dump(record, stream, indent=2)
        stream.write("\n")
    print("DIGIT_ENVELOPE_STUDY_SAVED", json.dumps({"nativeSha256": record["outputNative"]["sha256"],
                                                    "changed": len(link_names), "guards": len(added),
                                                    "beforeImages": len(before_images), "afterImages": len(after_images)}, sort_keys=True))


if __name__ == "__main__":
    main()
