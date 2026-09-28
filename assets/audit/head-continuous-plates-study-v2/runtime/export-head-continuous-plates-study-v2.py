"""Export a held, hash-bound native head study through the reviewed V7 exporter."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import shutil
import struct

import bpy

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "assets/models/uncaged-head-continuous-plates-study-v2/murderbird-head-continuous-plates-v2.blend"
RECEIPT = ROOT / "assets/audit/head-continuous-plates-study-v2/receipt.json"
EXPORTER = ROOT / "scripts/build-uncaged-alignment-v7.py"
EXPECTED_NATIVE = "ad99e4c0df19870e78b0a38107499e285a1f2d8523dee2c7694ec277141d9807"
EXPECTED_RECEIPT = None  # Filled from the exact reviewed receipt bytes before export.
EXPECTED_EXPORTER = "39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a"
OUT_DIR = ROOT / "assets/models/uncaged-head-continuous-plates-study-v2/runtime"
AUDIT_DIR = ROOT / "assets/audit/head-continuous-plates-study-v2/runtime"
OUT_GLB = OUT_DIR / "murderbird-head-continuous-plates-study-v2.glb"


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def read_glb_json(path):
    data = path.read_bytes()
    require(data[:4] == b"glTF" and struct.unpack_from("<I", data, 4)[0] == 2,
            "Output is not a GLB 2.0 file")
    offset = 12
    while offset < len(data):
        length, kind = struct.unpack_from("<I4s", data, offset)
        offset += 8
        chunk = data[offset:offset + length]
        offset += length
        if kind == b"JSON":
            return json.loads(chunk.decode("utf-8").rstrip(" \t\r\n\0"))
    raise RuntimeError("GLB JSON chunk is missing")


def main():
    global EXPECTED_RECEIPT
    require(NATIVE.is_file() and RECEIPT.is_file() and EXPORTER.is_file(), "Missing pinned input")
    require(sha256(NATIVE) == EXPECTED_NATIVE, "V2 native hash differs from independently reviewed study")
    require(sha256(EXPORTER) == EXPECTED_EXPORTER, "Reviewed V7 exporter helper hash changed")
    EXPECTED_RECEIPT = sha256(RECEIPT)
    receipt = json.loads(RECEIPT.read_text())
    require(receipt["native"]["sha256"] == EXPECTED_NATIVE, "Study receipt does not bind the selected native")
    require(not OUT_DIR.exists() and not AUDIT_DIR.exists(), "Refusing to overwrite a runtime derivative or audit")
    OUT_DIR.mkdir(parents=True, exist_ok=False)
    AUDIT_DIR.mkdir(parents=True, exist_ok=False)
    script_copy = AUDIT_DIR / Path(__file__).name
    exporter_copy = AUDIT_DIR / EXPORTER.name
    shutil.copy2(Path(__file__).resolve(), script_copy)
    shutil.copy2(EXPORTER, exporter_copy)
    require(sha256(script_copy) == sha256(Path(__file__).resolve()), "Exporter snapshot differs")
    require(sha256(exporter_copy) == EXPECTED_EXPORTER, "Reviewed V7 helper snapshot differs")

    spec = importlib.util.spec_from_file_location("reviewed_v7_export", EXPORTER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    expected_snapshot = helper.scene_snapshot()
    pivots_before = {obj.name: helper.matrix_values(obj.matrix_world)
                     for obj in bpy.data.objects if obj.type == "EMPTY"}
    native_meshes = []
    native_curves = []
    modifier_inventory = {}
    material_inventory = {}
    batch_members = {}
    for obj in bpy.data.objects:
        if obj.type == "EMPTY":
            continue
        if obj.type == "CURVE":
            native_curves.append(obj.name)
            continue
        if obj.type != "MESH":
            continue
        eras = obj.get("exteriorEras", helper.ALL_ERAS)
        region = obj.get("region", "back")
        role = obj.get("surfaceRole", "frame")
        owner = obj.parent.name if obj.parent else None
        native_meshes.append({"name": obj.name, "parent": owner, "region": region,
                              "surfaceRole": role, "exteriorEras": eras.split(",")})
        modifier_inventory[obj.name] = helper.modifier_signature(obj)
        key = (owner, eras, region, role)
        batch_members.setdefault(key, []).append(obj.name)
        for material in obj.data.materials:
            if material:
                material_inventory[material.name] = helper.material_signature(material)
    require(len(native_meshes) == 687 and len(pivots_before) == 51,
            f"Unexpected V2 native object inventory: {len(native_meshes)} meshes / {len(pivots_before)} pivots")
    require(len(native_curves) == 462, f"Unexpected V2 native curve count: {len(native_curves)}")
    require(all(part["parent"] and part["exteriorEras"] and part["region"] and part["surfaceRole"]
                for part in native_meshes), "Unclassified native mesh cannot be batched under reviewed V7 rules")
    require(not OUT_GLB.exists(), "Refusing to replace an existing GLB")
    helper.export_from_reopened_native(NATIVE, OUT_GLB, expected_snapshot, {})
    pivots_after = {obj.name: helper.matrix_values(obj.matrix_world)
                    for obj in bpy.data.objects if obj.type == "EMPTY"}
    require(pivots_after == pivots_before, "Reviewed V7 export batching changed pivot world matrices")
    require(sha256(NATIVE) == EXPECTED_NATIVE and sha256(RECEIPT) == EXPECTED_RECEIPT,
            "Native study or its review receipt changed during export")

    gltf = read_glb_json(OUT_GLB)
    glb_nodes = gltf.get("nodes", [])
    glb_materials = [item.get("name") for item in gltf.get("materials", [])]
    glb_extras = [node.get("extras", {}) for node in glb_nodes]
    eras_summary = {}
    for item in native_meshes:
        for era in item["exteriorEras"]:
            eras_summary[era] = eras_summary.get(era, 0) + 1
    batches = [{"parent": key[0], "exteriorEras": key[1].split(","), "region": key[2],
                "surfaceRole": key[3], "members": sorted(names)}
               for key, names in sorted(batch_members.items(), key=lambda row: row[0])]
    manifest = {
        "capturedAtUtc": datetime.now(timezone.utc).isoformat(),
        "status": "separate diagnostic runtime derivative for structural screening; not selected in app; head study remains unaccepted",
        "inputs": {
            "native": {"path": str(NATIVE.relative_to(ROOT)), "sha256": EXPECTED_NATIVE, "bytes": NATIVE.stat().st_size},
            "studyReceipt": {"path": str(RECEIPT.relative_to(ROOT)), "sha256": EXPECTED_RECEIPT},
            "baseV7Native": {"path": receipt["base"]["path"], "sha256": receipt["base"]["sha256"]},
            "reviewedExporter": {"path": str(EXPORTER.relative_to(ROOT)), "sha256": EXPECTED_EXPORTER},
        },
        "exportScript": {"path": str(Path(__file__).resolve().relative_to(ROOT)),
                         "sha256": sha256(Path(__file__).resolve()),
                         "snapshotPath": str(script_copy.relative_to(ROOT)), "snapshotSha256": sha256(script_copy)},
        "reviewedExporterSnapshot": {"path": str(exporter_copy.relative_to(ROOT)), "sha256": sha256(exporter_copy)},
        "outputGlb": {"path": str(OUT_GLB.relative_to(ROOT)), "sha256": sha256(OUT_GLB), "bytes": OUT_GLB.stat().st_size},
        "blenderVersion": bpy.app.version_string,
        "nativeInventory": {"meshCount": len(native_meshes), "curveCount": len(native_curves),
                            "pivotCount": len(pivots_before), "meshes": native_meshes,
                            "curves": sorted(native_curves), "pivotWorldMatrices": pivots_before},
        "modifierStacksByNativeMesh": modifier_inventory,
        "materialSignaturesByName": material_inventory,
        "nativeEraEligibilityCounts": eras_summary,
        "batchContract": batches,
        "exportedGlbInventory": {"nodeCount": len(glb_nodes), "meshCount": len(gltf.get("meshes", [])),
                                 "materialCount": len(glb_materials), "materials": glb_materials,
                                 "nodesWithExtras": [{"name": n.get("name"), "extras": n.get("extras", {})}
                                                     for n in glb_nodes if n.get("extras")]},
        "summary": {"nativeMeshes": len(native_meshes), "nativeCurves": len(native_curves),
                    "nativePivots": len(pivots_before), "nativeMaterialsUsed": len(material_inventory),
                    "nativeBytesUnchanged": True, "pivotMatricesPreservedExactly": True,
                    "modifierEvaluationAndBatchingOnlyInReopenedExportCopy": True},
        "limits": ["This derivative is separate from app assets and changes no runtime URL or fallback.",
                   "The helper evaluates/converts modifiers in a reopened in-memory export copy; the editable native stays unchanged.",
                   "A GLB export and structural screenings do not establish artistic likeness, browser appearance, or acceptance."],
    }
    report = AUDIT_DIR / "runtime-derivative.json"
    with report.open("x") as stream:
        json.dump(manifest, stream, indent=2, sort_keys=True)
        stream.write("\n")
    require(sha256(NATIVE) == EXPECTED_NATIVE, "Native changed after derivative receipt")
    print(json.dumps({"status": manifest["status"], "glb": str(OUT_GLB.relative_to(ROOT)),
                      "sha256": manifest["outputGlb"]["sha256"], "bytes": manifest["outputGlb"]["bytes"],
                      "nativeMeshes": len(native_meshes), "curves": len(native_curves),
                      "pivots": len(pivots_before), "materials": len(material_inventory),
                      "batchGroups": len(batches)}, sort_keys=True))


if __name__ == "__main__":
    main()
