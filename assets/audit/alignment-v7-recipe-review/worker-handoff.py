"""Build a selective V7 native fork from frozen V6 and regional candidate04.

This script is intentionally not self-selecting: it creates a new model folder,
preserves editable guard modifiers in the native file, and batches only a
reopened export copy after native save. Run under Blender after reviewing this
recipe and confirming all pinned input hashes.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile

import bpy
import bmesh


ROOT = Path(__file__).resolve().parents[1]
V6_DIR = ROOT / "assets/models/uncaged-alignment-v6"
REGIONAL_DIR = ROOT / "assets/models/uncaged-alignment-v5-regional/candidate-04"
V6_BLEND = V6_DIR / "murderbird-alignment-v6.blend"
V6_GLB = V6_DIR / "murderbird-alignment-v6.glb"
V6_INVENTORY = V6_DIR / "alignment-inventory.json"
REGIONAL_BLEND = REGIONAL_DIR / "murderbird-v5-sixth-guard-talon-study.blend"
REGIONAL_GLB = REGIONAL_DIR / "murderbird-v5-sixth-guard-talon-study.glb"
REGIONAL_MANIFEST = REGIONAL_DIR / "manifest.json"
OUT_DIR = ROOT / "assets/models/uncaged-alignment-v7"
AUDIT_DIR = ROOT / "assets/audit/alignment-v7"

EXPECTED = {
    "v6_blend": "5a7a51941423dd0efcb48b9641b7a49597dad117e218ccb4e94f26315c5e9ded",
    "v6_glb": "ce35024adda89681a0f37e7018e2563a74af67cd06558a887222df87b78a87fe",
    "v6_inventory": "2cdef42ccc9e96059d23252513321a5936b5b36717bc6a5c6409246ca6d2ca3b",
    "regional_blend": "376718193b9859cf7e454a0e148dde420c74061e6cdfbec7dd84ae6a4d3c960b",
    "regional_glb": "829d416a9eb65226543ce619ffc37ce8f135f3f8869ffb291b65da2a5c664c67",
    "regional_manifest": "321fd2e01420e9fc06132822badedb79d2c6b0d27e26da0b8919ed434e4dc9ed",
}
ALL_ERAS = "maker,mechanic,builder"
MATRIX_TOLERANCE = 1e-8

REMOVE_GUARDS = {
    "left ankle sheath lap rib 0.27", "left ankle sheath lap rib 0.53", "left ankle sheath lap rib 0.78",
    "left articulated ankle sheath 0", "left articulated ankle sheath 1", "left articulated ankle sheath 2", "left articulated ankle sheath 3",
    "left tapered limb sheath left-shin 0", "left tapered limb sheath left-shin 1", "left tapered limb sheath left-shin 2",
    "left tapered limb sheath left-thigh 0", "left tapered limb sheath left-thigh 1", "left tapered limb sheath left-thigh 2",
    "right ankle sheath lap rib 0.27", "right ankle sheath lap rib 0.53", "right ankle sheath lap rib 0.78",
    "right articulated ankle sheath 0", "right articulated ankle sheath 1", "right articulated ankle sheath 2", "right articulated ankle sheath 3",
    "right tapered limb sheath right-shin 0", "right tapered limb sheath right-shin 1", "right tapered limb sheath right-shin 2",
    "right tapered limb sheath right-thigh 0", "right tapered limb sheath right-thigh 1", "right tapered limb sheath right-thigh 2",
}
ADD_GUARDS = {
    "left shaped thigh guard proximal": ("left-thigh", "leg"),
    "left shaped thigh guard distal-overlap": ("left-thigh", "leg"),
    "left shaped shin guard proximal": ("left-shin", "leg"),
    "left shaped shin guard distal-overlap": ("left-shin", "leg"),
    "left curved instep guard": ("left-foot", "foot"),
    "right shaped thigh guard proximal": ("right-thigh", "leg"),
    "right shaped thigh guard distal-overlap": ("right-thigh", "leg"),
    "right shaped shin guard proximal": ("right-shin", "leg"),
    "right shaped shin guard distal-overlap": ("right-shin", "leg"),
    "right curved instep guard": ("right-foot", "foot"),
}
TALONS = {
    f"{side} digit {digit} tapered claw sheath": f"{side}-digit-{digit}-distal"
    for side in ("left", "right") for digit in (1, 2, 3)
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def matrix_values(matrix):
    return [[float(matrix[r][c]) for c in range(4)] for r in range(4)]


def matrix_error(a, b):
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
                    value = [float(component) for component in value]
                except TypeError:
                    value = float(value) if isinstance(value, (int, float)) else str(value)
                inputs.append([socket.identifier, value])
            nodes.append({"name": node.name, "type": node.bl_idname,
                          "inputs": sorted(inputs, key=lambda item: item[0])})
        for link in material.node_tree.links:
            links.append([link.from_node.name, link.from_socket.name,
                          link.to_node.name, link.to_socket.name])
    payload = {
        "diffuseColor": [float(c) for c in material.diffuse_color],
        "metallic": float(material.metallic), "roughness": float(material.roughness),
        "useNodes": bool(material.use_nodes),
        "nodes": sorted(nodes, key=lambda item: item["name"]), "links": sorted(links),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def mesh_signature(obj):
    mesh = obj.data
    payload = {
        "verts": [tuple(round(float(c), 9) for c in vertex.co) for vertex in mesh.vertices],
        "edges": [tuple(edge.vertices) for edge in mesh.edges],
        "faces": [(tuple(poly.vertices), int(poly.material_index), bool(poly.use_smooth)) for poly in mesh.polygons],
        "materials": [material_signature(m) if m else None for m in mesh.materials],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def modifier_signature(obj):
    fields = {
        "SOLIDIFY": ("thickness", "offset", "use_rim", "use_even_offset", "use_quality_normals",
                     "material_offset", "material_offset_rim"),
        "BEVEL": ("width", "segments", "limit_method", "angle_limit", "offset_type", "profile",
                  "miter_outer", "affect", "harden_normals", "loop_slide", "clamp_overlap"),
        "WEIGHTED_NORMAL": ("keep_sharp", "weight", "thresh", "mode", "use_face_influence"),
    }
    records = []
    for modifier in obj.modifiers:
        require(modifier.type in fields, f"Unreviewed guard modifier type: {obj.name}/{modifier.type}")
        require(not (hasattr(modifier, "object") and modifier.object) and
                not (hasattr(modifier, "collection") and modifier.collection),
                f"Guard modifier has an external object/collection dependency: {obj.name}/{modifier.name}")
        values = {}
        for key in fields[modifier.type]:
            if not hasattr(modifier, key):
                continue
            value = getattr(modifier, key)
            if isinstance(value, (int, float, bool, str)):
                values[key] = value
            else:
                try:
                    values[key] = [float(component) for component in value]
                except TypeError:
                    values[key] = str(value)
        records.append({"name": modifier.name, "type": modifier.type,
                        "showViewport": modifier.show_viewport, "showRender": modifier.show_render,
                        "values": values})
    return records


def curve_signature(obj):
    curve = obj.data
    splines = []
    for spline in curve.splines:
        points = []
        collection = spline.bezier_points if spline.type == "BEZIER" else spline.points
        for point in collection:
            co = point.co
            points.append({"co": [round(float(v), 9) for v in co],
                           "radius": round(float(point.radius), 9),
                           "tilt": round(float(point.tilt), 9),
                           "handles": [[round(float(v), 9) for v in point.handle_left],
                                       [round(float(v), 9) for v in point.handle_right]] if spline.type == "BEZIER" else None})
        splines.append({"type": spline.type, "cyclic": bool(spline.use_cyclic_u), "points": points})
    payload = {"dimensions": curve.dimensions, "resolution": curve.resolution_u,
               "bevelDepth": float(curve.bevel_depth), "bevelResolution": curve.bevel_resolution,
               "splines": splines}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def id_properties(obj):
    return {key: repr(obj[key]) for key in obj.keys()}


def scene_snapshot():
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    def visibility(obj):
        return {"hideViewport": bool(obj.hide_viewport), "hideRender": bool(obj.hide_render),
                "hideSelect": bool(obj.hide_select), "hideInViewLayer": bool(obj.hide_get())}
    empties = {obj.name: {"parent": obj.parent.name if obj.parent else None,
                          "matrix": matrix_values(obj.matrix_world), "visibility": visibility(obj)}
               for obj in bpy.data.objects if obj.type == "EMPTY"}
    meshes, curves = {}, {}
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            meshes[obj.name] = {"parent": obj.parent.name if obj.parent else None,
                                "matrix": matrix_values(obj.matrix_world), "mesh": mesh_signature(obj),
                                "modifiers": modifier_signature(obj), "props": id_properties(obj),
                                "visibility": visibility(obj)}
        elif obj.type == "CURVE":
            curves[obj.name] = {"parent": obj.parent.name if obj.parent else None,
                                "matrix": matrix_values(obj.matrix_world), "curve": curve_signature(obj),
                                "props": id_properties(obj), "visibility": visibility(obj)}
    return {"empties": empties, "meshes": meshes, "curves": curves}


def copy_bound(source, destination, expected):
    require(source.is_file(), f"Missing pinned input: {source}")
    require(sha256(source) == expected, f"Pinned input SHA mismatch: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    require(not destination.exists(), f"Refusing to overwrite input snapshot: {destination}")
    shutil.copy2(source, destination)
    require(sha256(destination) == expected, f"Input snapshot hash mismatch: {destination}")


def capture_and_package_sources(package_path, regional_manifest):
    bpy.ops.wm.open_mainfile(filepath=str(REGIONAL_BLEND))
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    added_records = {item["name"]: item for item in regional_manifest["composition"]["addedGuards"]}
    talon_records = {item["name"]: item for item in regional_manifest["composition"]["addedTalons"]}
    require(set(added_records) == set(ADD_GUARDS), "Candidate04 guard names differ from the exact ten-name transfer contract")
    require(set(talon_records) == set(TALONS), "Candidate04 talon names differ from the exact six-name transfer contract")

    source_owner_matrices = {}
    package_objects = []
    for name, (owner_name, region) in ADD_GUARDS.items():
        source = bpy.data.objects.get(name)
        require(source is not None and source.type == "MESH", f"Candidate04 is missing guard mesh: {name}")
        require(source.parent is not None and source.parent.name == owner_name, f"Candidate04 guard owner mismatch: {name}")
        require(source.get("region") == region and source.get("surfaceRole") == "plate",
                f"Candidate04 guard semantic tags mismatch: {name}")
        require(source.get("exteriorEras", ALL_ERAS) == ALL_ERAS,
                f"Candidate04 guard era visibility mismatch: {name}")
        rec = added_records[name]
        require(rec["owner"] == owner_name and rec["region"] == region and rec["surfaceRole"] == "plate"
                and rec["eras"] == ALL_ERAS, f"Candidate04 guard manifest contract mismatch: {name}")
        owner_matrix = source.parent.matrix_world.copy()
        owner_record = source_owner_matrices.setdefault(owner_name, matrix_values(owner_matrix))
        require(matrix_error(owner_record, matrix_values(owner_matrix)) <= MATRIX_TOLERANCE,
                f"Candidate04 owner matrix changed between guard objects: {owner_name}")
        clone = source.copy()
        clone.data = source.data.copy()
        clone.name = "V7_TRANSFER_GUARD::" + name
        clone["v7TransferOwner"] = owner_name
        clone["v7SourceWorld"] = json.dumps(matrix_values(source.matrix_world))
        clone["v7SourceOwnerWorld"] = json.dumps(matrix_values(owner_matrix))
        clone.parent = None
        clone.matrix_world = source.matrix_world.copy()
        package_objects.append(clone)

    for name, expected_owner in TALONS.items():
        source = bpy.data.objects.get(name)
        require(source is not None and source.type == "MESH", f"Candidate04 is missing talon mesh: {name}")
        rec = talon_records[name]
        require(source.parent is not None and source.parent.name == expected_owner == rec["owner"],
                f"Candidate04 talon owner mismatch: {name}")
        require(source.get("region") == "foot" and source.get("surfaceRole") == "edge",
                f"Candidate04 talon semantic tags mismatch: {name}")
        require(source.get("exteriorEras", ALL_ERAS) == ALL_ERAS and rec["eras"] == ALL_ERAS,
                f"Candidate04 talon era visibility mismatch: {name}")
        owner_matrix = source.parent.matrix_world.copy()
        owner_record = source_owner_matrices.setdefault(expected_owner, matrix_values(owner_matrix))
        require(matrix_error(owner_record, matrix_values(owner_matrix)) <= MATRIX_TOLERANCE,
                f"Candidate04 owner matrix changed between talon objects: {expected_owner}")
        clone = source.copy()
        clone.data = source.data.copy()
        clone.name = "V7_TRANSFER_TALON::" + name
        clone["v7TransferOwner"] = expected_owner
        clone["v7SourceWorld"] = json.dumps(matrix_values(source.matrix_world))
        clone["v7SourceOwnerWorld"] = json.dumps(matrix_values(owner_matrix))
        clone.parent = None
        clone.matrix_world = source.matrix_world.copy()
        package_objects.append(clone)

    # Build a temporary, transfer-only library. Its objects have no source-owner
    # parents; only the explicitly copied geometry, modifier stacks, and their
    # material datablocks can enter the V7 scene.
    transfer_collection = bpy.data.collections.new("V7 transfer package")
    bpy.context.scene.collection.children.link(transfer_collection)
    for obj in package_objects:
        transfer_collection.objects.link(obj)
    keep = set(package_objects)
    for obj in list(bpy.data.objects):
        if obj not in keep:
            bpy.data.objects.remove(obj, do_unlink=True)
    for collection in list(bpy.data.collections):
        if collection != transfer_collection:
            bpy.data.collections.remove(collection)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(package_path))
    return source_owner_matrices


def load_transfer_package(package_path):
    with bpy.data.libraries.load(str(package_path), link=False) as (data_from, data_to):
        names = [name for name in data_from.objects if name.startswith("V7_TRANSFER_")]
        require(len(names) == 16, f"Transfer package should contain 16 objects, got {len(names)}")
        data_to.objects = names
    return [obj for obj in data_to.objects if obj is not None]


def material_map_for_guard(source_obj, base_materials_by_signature):
    mapped = []
    for source_material in source_obj.data.materials:
        if source_material is None:
            mapped.append(None)
            continue
        signature = material_signature(source_material)
        matches = [material for material in bpy.data.materials
                   if material.library is None and material_signature(material) == signature]
        if matches:
            mapped.append(sorted(matches, key=lambda item: item.name)[0])
        else:
            local = source_material.copy()
            require(local.library is None and material_signature(local) == signature,
                    f"Imported material did not retain source appearance: {source_material.name}")
            mapped.append(local)
    return mapped


def validate_and_apply_transfer(source_owner_matrices, package_path):
    before = scene_snapshot()
    base_empty_names = set(before["empties"])
    require(len(base_empty_names) == 51, f"Expected 51 V6 pivots, found {len(base_empty_names)}")
    require(len(before["meshes"]) == 703, f"Expected 703 V6 mesh objects, found {len(before['meshes'])}")
    require(set(REMOVE_GUARDS) <= set(before["meshes"]), "V6 does not contain all exact guard removal targets")
    require(set(TALONS) <= set(before["meshes"]), "V6 does not contain all six talon targets")
    require(not (set(ADD_GUARDS) & set(before["meshes"])), "V6 already contains an added-guard name")

    sources = load_transfer_package(package_path)
    source_by_name = {obj.name.split("::", 1)[1]: obj for obj in sources}
    base_owners = {obj.name: obj for obj in bpy.data.objects if obj.type == "EMPTY"}
    for owner, source_world in source_owner_matrices.items():
        target = base_owners.get(owner)
        require(target is not None, f"V6 target owner missing: {owner}")
        require(matrix_error(source_world, matrix_values(target.matrix_world)) <= MATRIX_TOLERANCE,
                f"Regional parent world matrix differs from V6 for owner {owner}")

    # The input V6 owner hierarchy and every relevant articulation pivot must
    # remain exactly the base V6 data; source-study transforms are never copied.
    for name, expected in ADD_GUARDS.items():
        source = source_by_name[name]
        owner_name, region = expected
        owner = base_owners[owner_name]
        require(source["v7TransferOwner"] == owner_name, f"Transfer owner tag mismatch: {name}")
        source_world = json.loads(source["v7SourceWorld"])
        imported_world = source.matrix_world.copy()
        source_modifiers = modifier_signature(source)
        destination = source.copy()
        destination.data = source.data.copy()
        destination.name = name
        destination.parent = owner
        destination.matrix_world = imported_world
        destination["region"] = region
        destination["surfaceRole"] = "plate"
        destination["exteriorEras"] = ALL_ERAS
        destination["constructionClass"] = "inherited-passive"
        destination["geometryStatus"] = "editable regional profile proposal"
        for slot_index, material in enumerate(material_map_for_guard(source, base_materials_by_signature)):
            destination.data.materials[slot_index] = material
        destination.pop("v7TransferOwner", None)
        destination.pop("v7SourceWorld", None)
        destination.pop("v7SourceOwnerWorld", None)
        bpy.context.scene.collection.objects.link(destination)
        require(destination.parent == owner and matrix_error(matrix_values(destination.matrix_world), source_world) <= MATRIX_TOLERANCE,
                f"Transferred guard world transform changed: {name}")
        require(modifier_signature(destination) == source_modifiers,
                f"Transferred guard modifier stack changed: {name}")

    for name, owner_name in TALONS.items():
        source = source_by_name[name]
        target = bpy.data.objects.get(name)
        require(target is not None and target.parent and target.parent.name == owner_name,
                f"V6 talon target/parent mismatch: {name}")
        require(source.get("v7TransferOwner") == owner_name, f"Transfer talon owner tag mismatch: {name}")
        require(matrix_error(matrix_values(target.parent.matrix_world), json.loads(source["v7SourceOwnerWorld"])) <= MATRIX_TOLERANCE,
                f"Source and target distal owner matrices differ: {name}")
        require(matrix_error(matrix_values(target.matrix_world), json.loads(source["v7SourceWorld"])) <= MATRIX_TOLERANCE,
                f"Source and target talon world transforms differ: {name}")
        before_materials = [material_signature(m) if m else None for m in target.data.materials]
        source_materials = [material_signature(m) if m else None for m in source.data.materials]
        require(before_materials == source_materials, f"Talon material mapping differs; mesh-only replacement unsafe: {name}")
        old_materials = list(target.data.materials)
        replacement = source.data.copy()
        replacement.materials.clear()
        for material in old_materials:
            replacement.materials.append(material)
        target.data = replacement
        require([material_signature(m) if m else None for m in target.data.materials] == before_materials,
                f"Talon replacement changed material equivalence: {name}")

    for name in REMOVE_GUARDS:
        obj = bpy.data.objects.get(name)
        require(obj is not None and obj.type == "MESH", f"Exact deletion target missing at apply: {name}")
        bpy.data.objects.remove(obj, do_unlink=True)

    for source in sources:
        bpy.data.objects.remove(source, do_unlink=True)

    after = scene_snapshot()
    require(set(after["empties"]) == base_empty_names, "V7 added or removed a V6 empty/pivot")
    require(after["empties"] == before["empties"], "V7 changed a V6 pivot parent or world matrix")
    require(set(after["curves"]) == set(before["curves"]), "V7 changed retained control-curve names")
    require(after["curves"] == before["curves"], "V7 changed retained control-curve signatures")
    expected_meshes = (set(before["meshes"]) - REMOVE_GUARDS) | set(ADD_GUARDS)
    require(set(after["meshes"]) == expected_meshes, "V7 mesh names differ outside the exact transfer allowlist")
    for name, signature in before["meshes"].items():
        if name in REMOVE_GUARDS or name in TALONS:
            continue
        require(after["meshes"][name] == signature, f"Unrelated V6 mesh changed: {name}")
    for name, owner_name in TALONS.items():
        before_target = before["meshes"][name]
        after_target = after["meshes"][name]
        require(before_target["parent"] == after_target["parent"] == owner_name and
                before_target["matrix"] == after_target["matrix"], f"Talons' V6 object transforms changed: {name}")
        require(before_target["mesh"] != after_target["mesh"], f"Talon mesh did not change: {name}")
    guard_modifier_signatures = {name: modifier_signature(bpy.data.objects[name]) for name in ADD_GUARDS}
    return before, after, guard_modifier_signatures


def export_from_reopened_native(blend_path, glb_path, expected_snapshot, expected_guard_modifiers):
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))
    require(not any(obj.library for obj in bpy.data.objects), "Saved native contains linked source objects")
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    require(scene_snapshot() == expected_snapshot, "Reopened native snapshot differs from exact pre-save V7 scene")
    for name, signature in expected_guard_modifiers.items():
        require(modifier_signature(bpy.data.objects[name]) == signature,
                f"Saved native guard modifier stack differs after reload: {name}")
    pivots_before = {obj.name: matrix_values(obj.matrix_world) for obj in bpy.data.objects if obj.type == "EMPTY"}
    expected_pivots = {name: record["matrix"] for name, record in expected_snapshot["empties"].items()}
    require(pivots_before == expected_pivots, "Saved native pivot matrices differ from pre-save V7")
    # Apply modifiers only in the reopened export copy. The editable .blend was
    # already saved with all ten guard stacks intact.
    for obj in list(bpy.context.scene.objects):
        if obj.type != "MESH":
            continue
        bpy.ops.object.select_all(action="DESELECT")
        obj.hide_set(False)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.convert(target="MESH")
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        degenerate = [face for face in bm.faces if face.calc_area() < 1e-12]
        if degenerate:
            bmesh.ops.delete(bm, geom=degenerate, context="FACES_ONLY")
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(obj.data)
        bm.free()
        for attr in list(obj.data.color_attributes):
            obj.data.color_attributes.remove(attr)
    groups = {}
    for obj in list(bpy.context.scene.objects):
        if obj.type != "MESH":
            continue
        key = (obj.parent, obj.get("exteriorEras", ALL_ERAS),
               obj.get("region", "back"), obj.get("surfaceRole", "frame"))
        groups.setdefault(key, []).append(obj)
    for (parent, eras, region, role), objects in groups.items():
        bpy.ops.object.select_all(action="DESELECT")
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        bpy.ops.object.join()
        merged = bpy.context.object
        merged.name = f"{parent.name}-{region}-{role}"
        merged["exteriorEras"] = eras
        merged["region"] = region
        merged["surfaceRole"] = role
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.context.scene.objects:
        if obj.type in {"MESH", "EMPTY"}:
            obj.select_set(True)
    pending = glb_path.with_name(".building-" + glb_path.name)
    bpy.ops.export_scene.gltf(filepath=str(pending), export_format="GLB", use_selection=True,
                              export_yup=True, export_apply=True, export_extras=True,
                              export_cameras=False, export_lights=False, export_animations=True,
                              export_animation_mode="ACTIONS", export_frame_range=True)
    require(pending.is_file(), "Blender did not produce the temporary V7 GLB")
    pending.replace(glb_path)
    require({obj.name: matrix_values(obj.matrix_world) for obj in bpy.data.objects if obj.type == "EMPTY"}
            == expected_pivots, "Export batching changed V7 pivots")


def main():
    for path in (V6_BLEND, V6_GLB, V6_INVENTORY, REGIONAL_BLEND, REGIONAL_GLB, REGIONAL_MANIFEST):
        require(path.is_file(), f"Missing V7 pinned input: {path}")
    for path, key in ((V6_BLEND, "v6_blend"), (V6_GLB, "v6_glb"), (V6_INVENTORY, "v6_inventory"),
                      (REGIONAL_BLEND, "regional_blend"), (REGIONAL_GLB, "regional_glb"),
                      (REGIONAL_MANIFEST, "regional_manifest")):
        require(sha256(path) == EXPECTED[key], f"V7 pinned input SHA mismatch: {path}")
    require(not OUT_DIR.exists(), f"Refusing to replace existing V7 model directory: {OUT_DIR}")
    require(not AUDIT_DIR.exists(), f"Refusing to replace existing V7 audit directory: {AUDIT_DIR}")

    v6_inventory = json.loads(V6_INVENTORY.read_text())
    require(len(v6_inventory["parts"]) == 703 and len(v6_inventory["pivots"]) == 51,
            "Pinned V6 inventory counts do not match frozen V6 identity")
    generated = {Path(item["path"]).name: item["sha256"] for item in v6_inventory["generatedFiles"]}
    require(generated.get(V6_BLEND.name) == EXPECTED["v6_blend"] and
            generated.get(V6_GLB.name) == EXPECTED["v6_glb"], "V6 inventory does not bind the frozen model files")
    regional_manifest = json.loads(REGIONAL_MANIFEST.read_text())
    require(regional_manifest["inputIdentity"]["base"]["blend"]["sha256"] == "fd5c8a21e8e7808fa94c9baa3499574bac3d0c1ed5a44573637286c359cea0e4",
            "Candidate04 does not bind the reviewed V5 sixth base")
    require(regional_manifest["nativeOutput"]["sha256"] == EXPECTED["regional_blend"] and
            regional_manifest["export"]["glb"]["sha256"] == EXPECTED["regional_glb"],
            "Candidate04 manifest does not bind its exact native and GLB outputs")
    require(len(regional_manifest["composition"]["replacedObjects"]) == 32 and
            len(regional_manifest["composition"]["addedGuards"]) == 10 and
            len(regional_manifest["composition"]["addedTalons"]) == 6,
            "Candidate04 manifest transfer counts differ from the pinned contract")
    replaced = regional_manifest["composition"]["replacedObjects"]
    require({item["name"] for item in replaced if item["replacement"] == "guard-study-06"} == REMOVE_GUARDS,
            "Candidate04 guard replacement names do not equal the exact 26-name allowlist")
    require({item["name"] for item in replaced if item["replacement"] == "talon-study-03"} == set(TALONS),
            "Candidate04 talon replacement names do not equal the exact six-name allowlist")
    v6_part_records = {item["name"]: item for item in v6_inventory["parts"]}
    for item in replaced:
        base_part = v6_part_records.get(item["name"])
        require(base_part is not None and base_part["parent"] == item["owner"],
                f"V6 inventory owner differs from candidate04 replacement contract: {item['name']}")
    for name, (owner, region) in ADD_GUARDS.items():
        record = next(item for item in regional_manifest["composition"]["addedGuards"] if item["name"] == name)
        require(record["owner"] == owner and record["region"] == region and
                record["surfaceRole"] == "plate" and record["eras"] == ALL_ERAS,
                f"Candidate04 added-guard metadata mismatch: {name}")

    # Snapshot exact input bytes before opening either authoring file.
    AUDIT_DIR.mkdir(parents=True, exist_ok=False)
    input_dir = AUDIT_DIR / "inputs"
    input_map = [
        (V6_BLEND, input_dir / "v6/murderbird-alignment-v6.blend", EXPECTED["v6_blend"]),
        (V6_GLB, input_dir / "v6/murderbird-alignment-v6.glb", EXPECTED["v6_glb"]),
        (V6_INVENTORY, input_dir / "v6/alignment-inventory.json", EXPECTED["v6_inventory"]),
        (REGIONAL_BLEND, input_dir / "regional-candidate-04/murderbird-v5-sixth-guard-talon-study.blend", EXPECTED["regional_blend"]),
        (REGIONAL_GLB, input_dir / "regional-candidate-04/murderbird-v5-sixth-guard-talon-study.glb", EXPECTED["regional_glb"]),
        (REGIONAL_MANIFEST, input_dir / "regional-candidate-04/manifest.json", EXPECTED["regional_manifest"]),
    ]
    for source, destination, expected in input_map:
        copy_bound(source, destination, expected)
    script_copy = AUDIT_DIR / "build-uncaged-alignment-v7.py"
    shutil.copy2(Path(__file__).resolve(), script_copy)

    OUT_DIR.mkdir(parents=True, exist_ok=False)
    out_blend = OUT_DIR / "murderbird-alignment-v7.blend"
    out_glb = OUT_DIR / "murderbird-alignment-v7.glb"
    inventory_path = OUT_DIR / "alignment-inventory.json"
    pending_blend = OUT_DIR / ".building-alignment-v7.blend"
    with tempfile.TemporaryDirectory(prefix="murderbird-v7-transfer-") as temp_dir:
        package_path = Path(temp_dir) / "regional-transfer-package.blend"
        source_owner_matrices = capture_and_package_sources(package_path, regional_manifest)
        bpy.ops.wm.open_mainfile(filepath=str(V6_BLEND))
        before, after, guard_modifier_signatures = validate_and_apply_transfer(source_owner_matrices, package_path)
        require(len(after["meshes"]) == 687 and len(after["curves"]) == len(before["curves"]),
                "V7 mesh/curve inventory counts do not match exact selective transfer")
        require(all(obj.library is None for obj in bpy.data.objects), "Linked source IDs remain in V7 scene")
        native_parts = [{"name": obj.name, "parent": obj.parent.name, "region": obj.get("region", "back"),
                         "role": obj.get("surfaceRole", "frame"), "eras": obj.get("exteriorEras", ALL_ERAS).split(","),
                         "class": obj.get("constructionClass", "inherited-passive"),
                         **({"geometryStatus": obj.get("geometryStatus")} if obj.get("geometryStatus") else {})}
                        for obj in bpy.data.objects if obj.type == "MESH"]
        native_pivots = [{"name": obj.name, "parent": obj.parent.name if obj.parent else None,
                          "local": list(obj.location), "world": list(obj.matrix_world.translation),
                          "scale": list(obj.scale)} for obj in bpy.data.objects if obj.type == "EMPTY"]
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=str(pending_blend))
        require(pending_blend.is_file(), "Native V7 save failed")
        pending_blend.replace(out_blend)

    # Export only from the just-saved editable native fork. Modifier conversion
    # and grouping therefore cannot erase the saved guard edit stacks.
    export_from_reopened_native(out_blend, out_glb, after, guard_modifier_signatures)
    require(sha256(V6_BLEND) == EXPECTED["v6_blend"] and sha256(V6_GLB) == EXPECTED["v6_glb"] and
            sha256(V6_INVENTORY) == EXPECTED["v6_inventory"] and
            sha256(REGIONAL_BLEND) == EXPECTED["regional_blend"] and sha256(REGIONAL_GLB) == EXPECTED["regional_glb"] and
            sha256(REGIONAL_MANIFEST) == EXPECTED["regional_manifest"], "An input changed during V7 build")

    v7_inventory = dict(v6_inventory)
    v7_inventory.update({
        "status": "neutral geometry proposal awaiting owner review",
        "startingRevision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "previousCandidate": {"path": "assets/models/uncaged-alignment-v6/murderbird-alignment-v6.glb", "sha256": EXPECTED["v6_glb"]},
        "base": {"path": str(V6_BLEND.relative_to(ROOT)), "sha256": EXPECTED["v6_blend"],
                 "glbPath": str(V6_GLB.relative_to(ROOT)), "glbSha256": EXPECTED["v6_glb"]},
        "scope": "Frozen V6 geometry, transforms, hierarchy, controls and pivots retained except exact 26 guard removals, ten editable guard additions, and six talon mesh-data replacements from bound regional candidate04.",
        "regionalTransfer": {
            "sourcePath": str(REGIONAL_BLEND.relative_to(ROOT)), "sourceSha256": EXPECTED["regional_blend"],
            "manifestPath": str(REGIONAL_MANIFEST.relative_to(ROOT)), "manifestSha256": EXPECTED["regional_manifest"],
            "guardRemovals": sorted(REMOVE_GUARDS), "guardAdditions": sorted(ADD_GUARDS),
            "talonMeshDataReplacements": sorted(TALONS),
            "inputSnapshots": [
                {"path": str(destination.relative_to(ROOT)), "bytes": destination.stat().st_size,
                 "sha256": sha256(destination)} for _, destination, _ in input_map
            ],
            "scriptSnapshot": {"path": str(script_copy.relative_to(ROOT)), "bytes": script_copy.stat().st_size,
                               "sha256": sha256(script_copy)},
            "retainedControlCurves": "Inherited V6 guides are preserved for reference; they do not regenerate the transferred guard meshes.",
            "editableGuardSource": "Transferred native guard mesh data and modifier stacks from regional candidate04; modifiers are applied only to the reopened export copy.",
        },
        "compatibilityChecks": {
            "sourceParentWorldMatricesCompared": True, "unrelatedNativeMeshAndCurveSignaturesPreserved": True,
            "all51PivotMatricesPreserved": True, "talonTransformsAndMaterialEquivalencePreserved": True,
            "guardModifierStacksPreservedInNative": True,
            "bounds": "Local native checks only; run the independent V7 exported-GLB parity validator and asset validator before treating export as verified.",
        },
        "parts": native_parts,
        "pivots": native_pivots,
        "generatedFiles": [],
    })
    v7_inventory.pop("inheritedHelperSources", None)
    v7_inventory["generatedFiles"] = [
        {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256(path)}
        for path in (out_blend, out_glb)
    ]
    with inventory_path.open("x") as stream:
        stream.write(json.dumps(v7_inventory, indent=2) + "\n")
    print("ALIGNMENT_V7_SAVED", len(v7_inventory["parts"]), "parts", len(v7_inventory["pivots"]),
          "pivots", sha256(out_glb))


if __name__ == "__main__":
    main()
