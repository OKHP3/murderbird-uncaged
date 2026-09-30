#!/usr/bin/env python3
"""Create a bounded V37 material study with native and GLB era profiles.

Run with Blender:
  blender -b --python scripts/build-v37-mechanical-finish.py -- \
    --native-source assets/models/whole-character-v37/attempt-release02/murderbird-whole-character-v37.blend \
    --glb-source assets/models/whole-character-v37/attempt-release02/murderbird-whole-character-v37.glb \
    --output-directory assets/models/whole-character-v37/finish-study01

The native file stays editable. The GLB keeps standard PBR defaults for the
Advanced era and stores all era responses in material extras. The runtime can
select a profile from GLTFLoader material.userData. Geometry stays in the
original BIN chunk. Existing mesh records receive only material index changes;
mesh records and node mesh references stay in their original positions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

import bpy


SOURCE_ROLES = {
    "Neutral / frame": "frame",
    "Neutral / plate": "plate",
    "Neutral / repair": "repair",
    "Neutral / bearing": "bearing",
    "Neutral / optic": "optic",
    "Neutral / inner": "inner",
    "Neutral / recess": "recess",
    "Neutral / edge": "edge",
}
ERAS = ("maker", "mechanic", "builder")
GLB_HEADER = struct.Struct("<4sII")
CHUNK_HEADER = struct.Struct("<II")
JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942

# Values are linear RGB, standard glTF metallic-roughness material values.
# The Builder values are the GLB defaults. No texture, aging noise, transmission,
# alpha, shader-only feature, or unbounded optic glow is used.
FINISHES = {
    "shell": {
        "maker":    {"baseColorFactor": [0.115, 0.066, 0.030, 1.0], "metallicFactor": 0.78, "roughnessFactor": 0.48},
        "mechanic": {"baseColorFactor": [0.026, 0.067, 0.053, 1.0], "metallicFactor": 0.74, "roughnessFactor": 0.53},
        "builder":  {"baseColorFactor": [0.026, 0.067, 0.053, 1.0], "metallicFactor": 0.74, "roughnessFactor": 0.53},
    },
    "bill": {
        "maker":    {"baseColorFactor": [0.145, 0.084, 0.040, 1.0], "metallicFactor": 0.76, "roughnessFactor": 0.43},
        "mechanic": {"baseColorFactor": [0.042, 0.078, 0.057, 1.0], "metallicFactor": 0.75, "roughnessFactor": 0.48},
        "builder":  {"baseColorFactor": [0.042, 0.078, 0.057, 1.0], "metallicFactor": 0.75, "roughnessFactor": 0.48},
    },
    "frame": {
        "maker":    {"baseColorFactor": [0.030, 0.037, 0.040, 1.0], "metallicFactor": 0.84, "roughnessFactor": 0.59},
        "mechanic": {"baseColorFactor": [0.027, 0.038, 0.038, 1.0], "metallicFactor": 0.84, "roughnessFactor": 0.60},
        "builder":  {"baseColorFactor": [0.027, 0.038, 0.038, 1.0], "metallicFactor": 0.84, "roughnessFactor": 0.60},
    },
    "bearing": {
        "maker":    {"baseColorFactor": [0.105, 0.068, 0.033, 1.0], "metallicFactor": 0.82, "roughnessFactor": 0.40},
        "mechanic": {"baseColorFactor": [0.105, 0.073, 0.036, 1.0], "metallicFactor": 0.82, "roughnessFactor": 0.42},
        "builder":  {"baseColorFactor": [0.105, 0.073, 0.036, 1.0], "metallicFactor": 0.82, "roughnessFactor": 0.42},
    },
    "edge": {
        "maker":    {"baseColorFactor": [0.205, 0.126, 0.051, 1.0], "metallicFactor": 0.78, "roughnessFactor": 0.38},
        "mechanic": {"baseColorFactor": [0.135, 0.105, 0.053, 1.0], "metallicFactor": 0.79, "roughnessFactor": 0.41},
        "builder":  {"baseColorFactor": [0.135, 0.105, 0.053, 1.0], "metallicFactor": 0.79, "roughnessFactor": 0.41},
    },
    "repair": {
        "mechanic": {"baseColorFactor": [0.230, 0.126, 0.050, 1.0], "metallicFactor": 0.72, "roughnessFactor": 0.46},
        "builder":  {"baseColorFactor": [0.230, 0.126, 0.050, 1.0], "metallicFactor": 0.72, "roughnessFactor": 0.46},
    },
    "inner": {
        "builder":  {"baseColorFactor": [0.105, 0.097, 0.075, 1.0], "metallicFactor": 0.25, "roughnessFactor": 0.67},
    },
    "recess": {
        "maker":    {"baseColorFactor": [0.010, 0.014, 0.016, 1.0], "metallicFactor": 0.16, "roughnessFactor": 0.78},
        "mechanic": {"baseColorFactor": [0.010, 0.014, 0.016, 1.0], "metallicFactor": 0.16, "roughnessFactor": 0.78},
        "builder":  {"baseColorFactor": [0.010, 0.014, 0.016, 1.0], "metallicFactor": 0.16, "roughnessFactor": 0.78},
    },
    "optic": {
        "builder":  {"baseColorFactor": [0.095, 0.031, 0.007, 1.0], "metallicFactor": 0.20, "roughnessFactor": 0.35,
                      "emissiveFactor": [0.0084, 0.00216, 0.00024]},
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def args_after_double_dash():
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-source", required=True, type=Path)
    parser.add_argument("--glb-source", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    return parser.parse_args(values)


def tags_for(obj):
    return {k: obj.get(k) for k in ("region", "surfaceRole", "exteriorEras")}


def era_set(value):
    return {part.strip().lower() for part in value.split(",")} & set(ERAS) if isinstance(value, str) else set()


def mapped_role(source_material, object_name, region):
    role = SOURCE_ROLES.get(source_material)
    n = object_name.lower().replace("_", "-")
    if role == "plate" and region in {"head", "head-reconstruction"} and any(
        token in n for token in ("bill", "beak", "jaw", "mandible")
    ):
        return "bill"
    return role


def mat_name(role):
    return "V37 finish / " + ("shared shell" if role == "plate" else role)


def finish_key(role):
    return "shell" if role == "plate" else role


def blender_color(material, profiles):
    # The selected editable default is Advanced/Builder. Era-specific profiles
    # remain attached as Blender ID properties for the runtime integrator.
    p = profiles.get("builder") or profiles.get("mechanic") or profiles.get("maker")
    c = p["baseColorFactor"]
    material.diffuse_color = tuple(c)
    material.metallic = p["metallicFactor"]
    material.roughness = p["roughnessFactor"]
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = material.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = tuple(c)
    bsdf.inputs["Metallic"].default_value = p["metallicFactor"]
    bsdf.inputs["Roughness"].default_value = p["roughnessFactor"]
    e = p.get("emissiveFactor", [0.0, 0.0, 0.0])
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*e, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 1.0
    elif "Emission" in bsdf.inputs:
        bsdf.inputs["Emission"].default_value = (*e, 1.0)
    material["eraFinishes"] = json.dumps(profiles, separators=(",", ":"), sort_keys=True)
    material["finishStudy"] = "v37-mechanical-finish-study01"


def native_snapshot():
    result = {}
    for obj in bpy.data.objects:
        row = {
            "type": obj.type,
            "parent": obj.parent.name if obj.parent else None,
            "matrixLocal": [list(v) for v in obj.matrix_local],
            "matrixWorld": [list(v) for v in obj.matrix_world],
            "visibility": [bool(obj.hide_viewport), bool(obj.hide_render), bool(obj.hide_get())],
            "tags": tags_for(obj),
        }
        if obj.type == "MESH":
            mesh = obj.data
            data = bytearray(struct.pack("<III", len(mesh.vertices), len(mesh.edges), len(mesh.polygons)))
            for v in mesh.vertices:
                data.extend(struct.pack("<3f", *v.co))
            for edge in mesh.edges:
                data.extend(struct.pack("<2I", *edge.vertices))
            for poly in mesh.polygons:
                data.extend(struct.pack("<I", len(poly.vertices)))
                data.extend(struct.pack("<" + "I" * len(poly.vertices), *poly.vertices))
                data.extend(struct.pack("<I", poly.material_index))
            row["geometrySHA256"] = sha(bytes(data))
            row["counts"] = [len(mesh.vertices), len(mesh.edges), len(mesh.polygons)]
        result[obj.name] = row
    return result


def glb_read(path):
    raw = path.read_bytes()
    magic, version, size = GLB_HEADER.unpack_from(raw)
    if magic != b"glTF" or version != 2 or size != len(raw):
        raise ValueError(f"Invalid GLB 2 file: {path}")
    chunks, offset = [], GLB_HEADER.size
    while offset < len(raw):
        length, kind = CHUNK_HEADER.unpack_from(raw, offset)
        offset += CHUNK_HEADER.size
        payload = raw[offset:offset + length]
        if len(payload) != length:
            raise ValueError("Truncated GLB chunk")
        chunks.append((kind, payload))
        offset += length
    if not chunks or chunks[0][0] != JSON_CHUNK or not any(k == BIN_CHUNK for k, _ in chunks):
        raise ValueError("GLB JSON/BIN chunks missing")
    return raw, chunks, json.loads(chunks[0][1].decode("utf-8"))


def set_material_profiles():
    assignments, role_rows, unmapped = {}, Counter(), []
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        tg = tags_for(obj)
        eras = era_set(tg.get("exteriorEras"))
        if not eras:
            continue
        region = str(tg.get("region") or "")
        for index, slot in enumerate(obj.material_slots):
            old = slot.material
            if old is None:
                continue
            role = mapped_role(old.name, obj.name, region)
            profiles = FINISHES.get(finish_key(role), {}) if role else {}
            profiles = {era: profiles[era] for era in ERAS if era in eras and era in profiles}
            if not profiles:
                unmapped.append({"object": obj.name, "material": old.name, "region": region, "eras": sorted(eras)})
                continue
            name = mat_name(role)
            material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
            blender_color(material, profiles)
            slot.material = material
            assignments[(obj.name, index)] = {"sourceMaterial": old.name, "material": name, "role": role}
            role_rows[(tg.get("exteriorEras"), region, str(tg.get("surfaceRole") or ""), role, old.name)] += 1
    if unmapped:
        raise ValueError(f"Unmapped tagged native material slots: {unmapped[:12]}")
    if not assignments:
        raise ValueError("No tagged exterior material assignments found")
    return assignments, role_rows


def patch_glb(source_path, output_path, native_assignments):
    raw, chunks, doc = glb_read(source_path)
    original = json.loads(json.dumps(doc))
    old_materials = original.get("materials", [])
    assignment_by_pair = {
        (object_name, value["sourceMaterial"]): value["material"]
        for (object_name, _slot), value in native_assignments.items()
    }
    material_profiles = {}
    role_counts = Counter()
    node_mesh_signatures = {}
    for ni, node in enumerate(original["nodes"]):
        if "mesh" not in node:
            continue
        extras = node.get("extras", {})
        eras = era_set(extras.get("exteriorEras"))
        if not eras:
            continue
        region = str(extras.get("region") or "")
        surface_role = str(extras.get("surfaceRole") or "")
        signature = []
        for primitive in original["meshes"][node["mesh"]].get("primitives", []):
            mi = primitive.get("material")
            old = old_materials[mi].get("name") if mi is not None else None
            name = assignment_by_pair.get((node.get("name"), old))
            if not name:
                raise ValueError(f"No native material mapping for tagged GLB node {node.get('name')} / {old}")
            role = mapped_role(old, node.get("name", ""), region)
            key = finish_key(role)
            profiles = {era: FINISHES[key][era] for era in ERAS if era in eras and era in FINISHES[key]}
            if set(profiles) != eras:
                raise ValueError(f"Profile eligibility mismatch on {node.get('name')}: {eras} vs {set(profiles)}")
            material_profiles[name] = {"role": role, "profiles": profiles, "doubleSided": bool(old_materials[mi].get("doubleSided", False))}
            role_counts[(extras.get("exteriorEras"), region, surface_role, role, old)] += 1
            signature.append(name)
        node_mesh_signatures[ni] = (node["mesh"], tuple(signature))

    profile_index = {}
    for name, record in material_profiles.items():
        profile_index[name] = len(doc.setdefault("materials", []))
        default = record["profiles"].get("builder") or record["profiles"].get("mechanic") or record["profiles"].get("maker")
        doc["materials"].append({
            "name": name,
            "pbrMetallicRoughness": {
                "baseColorFactor": default["baseColorFactor"],
                "metallicFactor": default["metallicFactor"],
                "roughnessFactor": default["roughnessFactor"],
            },
            "emissiveFactor": default.get("emissiveFactor", [0.0, 0.0, 0.0]),
            "alphaMode": "OPAQUE",
            "doubleSided": record["doubleSided"],
            "extras": {
                "finishStudy": "v37-mechanical-finish-study01",
                "materialRole": record["role"],
                "eraFinishes": record["profiles"],
            },
        })
    source_mesh_count = len(original["meshes"])
    mesh_signatures = {}
    for ni, (source_mesh_index, signature) in node_mesh_signatures.items():
        previous = mesh_signatures.setdefault(source_mesh_index, signature)
        if previous != signature:
            raise ValueError(f"Shared mesh {source_mesh_index} needs incompatible material assignments; preserve source and scope separately")
        for pi, name in enumerate(signature):
            doc["meshes"][source_mesh_index]["primitives"][pi]["material"] = profile_index[name]
    # Material records and primitive material indices are the complete JSON
    # change allowlist; compare every other field rather than infer preservation.
    restored = json.loads(json.dumps(doc))
    restored["materials"] = original["materials"]
    for mi, mesh in enumerate(restored["meshes"]):
        for pi, primitive in enumerate(mesh.get("primitives", [])):
            source_primitive = original["meshes"][mi]["primitives"][pi]
            if "material" in source_primitive:
                primitive["material"] = source_primitive["material"]
            else:
                primitive.pop("material", None)
    if restored != original:
        raise ValueError("GLB JSON changed outside the material record/index allowlist")

    payload = json.dumps(doc, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    payload += b" " * ((4 - len(payload) % 4) % 4)
    output = bytearray(GLB_HEADER.pack(b"glTF", 2, 0))
    for kind, data in chunks:
        output.extend(CHUNK_HEADER.pack(len(payload) if kind == JSON_CHUNK else len(data), kind))
        output.extend(payload if kind == JSON_CHUNK else data)
    struct.pack_into("<I", output, 8, len(output))
    output_path.write_bytes(output)
    _, output_chunks, outdoc = glb_read(output_path)
    source_bin = next(data for kind, data in chunks if kind == BIN_CHUNK)
    output_bin = next(data for kind, data in output_chunks if kind == BIN_CHUNK)
    if source_bin != output_bin:
        raise ValueError("GLB BIN chunk changed")
    if len(outdoc["materials"]) != len(old_materials) + len(material_profiles):
        raise ValueError("Unexpected GLB material count")
    return {
        "sourceSha256": sha(raw), "outputSha256": sha(bytes(output)),
        "sourceBytes": len(raw), "outputBytes": len(output),
        "binChunkByteIdentical": True, "binChunkSha256": sha(source_bin),
        "sourceMaterialCount": len(old_materials), "outputMaterialCount": len(outdoc["materials"]),
        "sourceMeshCount": source_mesh_count, "outputMeshCount": len(outdoc["meshes"]),
        "nodeMeshReferencesUnchanged": outdoc["nodes"] == original["nodes"],
        "jsonOnlyMaterialRecordsAndPrimitiveMaterialIndicesChanged": True,
        "materialNamesAdded": list(material_profiles), "nodesWithOverrides": len(node_mesh_signatures),
        "roleRegionEraCounts": [
            {"exteriorEras": k[0], "region": k[1], "surfaceRole": k[2], "mappedRole": k[3], "sourceMaterial": k[4], "primitiveCount": v}
            for k, v in sorted(role_counts.items(), key=lambda x: tuple(str(i) for i in x[0]))
        ],
    }


def main():
    args = args_after_double_dash()
    native_source = args.native_source.resolve()
    glb_source = args.glb_source.resolve()
    out_dir = args.output_directory.resolve()
    if not native_source.is_file() or not glb_source.is_file():
        raise FileNotFoundError("Both --native-source and --glb-source must exist")
    native_out = out_dir / "murderbird-v37-mechanical-finish-study01.blend"
    glb_out = out_dir / "murderbird-v37-mechanical-finish-study01.glb"
    repo_root = Path(__file__).resolve().parents[1]
    audit = repo_root / "assets/audit/whole-character-v37/finish-study01"
    receipt_path = audit / "receipt.json"
    existing = [str(path) for path in (native_out, glb_out, receipt_path) if path.exists()]
    if existing:
        raise FileExistsError(f"Write-once study outputs already exist; preserve and scope a new study before rerunning: {existing}")
    out_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(native_source))
    before = native_snapshot()
    assignments, role_rows = set_material_profiles()
    after = native_snapshot()
    if set(before) != set(after):
        raise ValueError("Native object set changed")
    for name, old in before.items():
        new = after[name]
        for key in ("type", "parent", "matrixLocal", "matrixWorld", "visibility", "tags", "geometrySHA256", "counts"):
            if key in old and old[key] != new.get(key):
                raise ValueError(f"Native preservation failure: {name}.{key}")
    bpy.ops.wm.save_as_mainfile(filepath=str(native_out), check_existing=False)
    glb_info = patch_glb(glb_source, glb_out, assignments)

    new_mats = {}
    for name, material in bpy.data.materials.items():
        if material.get("finishStudy") == "v37-mechanical-finish-study01":
            new_mats[name] = json.loads(material["eraFinishes"])
    receipt = {
        "status": "bounded readability study; proposal only; no likeness or owner acceptance",
        "inputs": {
            "native": {"path": str(native_source), "sha256": sha(native_source.read_bytes()), "bytes": native_source.stat().st_size},
            "glb": {"path": str(glb_source), "sha256": glb_info["sourceSha256"], "bytes": glb_info["sourceBytes"]},
        },
        "outputs": {
            "native": {"path": str(native_out), "sha256": sha(native_out.read_bytes()), "bytes": native_out.stat().st_size},
            "glb": {"path": str(glb_out), **glb_info},
        },
        "preservation": {
            "nativeObjectCount": len(before), "nativeMeshCount": sum(v["type"] == "MESH" for v in before.values()),
            "nativeGeometryAndMaterialIndexDataUnchanged": True,
            "nativeOwnersTransformsVisibilityAndEligibilityTagsUnchanged": True,
            "nativeMaterialSlotResponsesChanged": len(assignments),
            "glbBinChunkByteIdentical": True,
            "glbAccessorsUnchanged": True,
            "glbOriginalSourceMeshesRetained": True,
            "glbMeshRecordCountUnchanged": glb_info["sourceMeshCount"] == glb_info["outputMeshCount"],
            "glbNodesAndMeshReferencesUnchanged": glb_info["nodeMeshReferencesUnchanged"],
            "sourceMaterialsRetained": True,
            "onlyNewMaterialRecordsAndPrimitiveMaterialIndicesDifferInGLBJSON": glb_info["jsonOnlyMaterialRecordsAndPrimitiveMaterialIndicesChanged"],
        },
        "references": {
            "makerClean": "assets/img/webp/murderbird-unified-maker-clean-2026-09-06-960.webp",
            "mechanic": "assets/img/webp/murderbird-unified-mechanic-2026-09-06-960.webp",
            "advanced": "Inherited shell interpretation documented by docs/exterior-surface-pipeline.md and docs/exterior-regional-map.md; Builder is the runtime era key for Advanced.",
        },
        "materialProfiles": new_mats,
        "nativeRoleRegionEraSlotCounts": [
            {"exteriorEras": k[0], "region": k[1], "surfaceRole": k[2], "mappedRole": k[3], "sourceMaterial": k[4], "slotCount": v}
            for k, v in sorted(role_rows.items(), key=lambda x: tuple(str(i) for i in x[0]))
        ],
        "mappingContract": {
            "selection": "For each tagged mesh material slot, combine exteriorEras, region, surfaceRole, object name (to distinguish bill/jaw), and the existing Neutral material primitive role. Apply only matching profile eras.",
            "runtime": "GLB material.extras.eraFinishes profiles are standard metallic-roughness factors; GLTFLoader exposes extras through material.userData. Default PBR fields are Advanced/Builder. Runtime integration may select maker, mechanic, or builder profile without geometry duplication.",
            "alpha": "Every generated profile baseColorFactor alpha is 1; materials remain opaque.",
        },
        "limitations": [
            "No texture or wear noise is added. Mechanic and Advanced inherit the darker teal-bronze response; visible later repair contrast is limited to existing era-eligible repair primitives.",
            "Optic emission is limited to the existing Builder optic aperture role. No power-core or reactor glow is included.",
            "No geometry, object owners, transforms, pivots, visibility tags, lighting, or machinery eligibility changed.",
            "Material readability study only; silhouette/likeness, clearances, runtime integration, release, deployment, and owner acceptance remain unevaluated.",
        ],
    }
    audit.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"nativeSha256": receipt["outputs"]["native"]["sha256"], "glbSha256": glb_info["outputSha256"], "receipt": str(receipt_path)}, indent=2))


if __name__ == "__main__":
    main()
