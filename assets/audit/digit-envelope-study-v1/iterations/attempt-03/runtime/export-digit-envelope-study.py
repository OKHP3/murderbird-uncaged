"""Export a runtime derivative from the preserved native digit-envelope study.

The native study is opened and hashed read-only. Only the reopened export copy is
modifier-evaluated and batched using the reviewed V7 parent/era/region/role rule.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import shutil

import bpy

ROOT = Path(__file__).resolve().parents[1]
RUN = "attempt-03"
BASE = ROOT / "assets"
V7_NATIVE = BASE / "models/uncaged-alignment-v7/murderbird-alignment-v7.blend"
V7_GLB = BASE / "models/uncaged-alignment-v7/murderbird-alignment-v7.glb"
STUDY_NATIVE = BASE / f"models/uncaged-digit-envelope-study-v1/iterations/{RUN}/murderbird-uncaged-digit-envelope-study-v1.blend"
STUDY_RECEIPT = BASE / f"audit/digit-envelope-study-v1/iterations/{RUN}/study-receipt.json"
EXPORTER = BASE / "audit/alignment-v7/build-uncaged-alignment-v7.py"
OUT_DIR = BASE / f"models/uncaged-digit-envelope-study-v1/iterations/{RUN}/runtime"
AUDIT_DIR = BASE / f"audit/digit-envelope-study-v1/iterations/{RUN}/runtime"
OUT_GLB = OUT_DIR / "murderbird-digit-envelope-study-v1.glb"
EXPECTED_NATIVE = "5d8d101f4eee4d3bb86bae57d8de41b4aa2b9a8399d6962c91505f60bedfde54"
EXPECTED_V7_NATIVE = "a8fccaf024a096678415215029b34cae8270b348da2301b8872a34e72c75ed3f"
EXPECTED_V7_GLB = "1c82874b86af6b493ac380536de6af72a30fafa3a4b0ebb3d8790f56ffc03018"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def matrix_rows(matrix):
    return [[float(matrix[r][c]) for c in range(4)] for r in range(4)]


def main():
    for path in (V7_NATIVE, V7_GLB, STUDY_NATIVE, STUDY_RECEIPT, EXPORTER):
        require(path.is_file(), f"Missing bound input: {path}")
    require(sha256(V7_NATIVE) == EXPECTED_V7_NATIVE and sha256(V7_GLB) == EXPECTED_V7_GLB,
            "Frozen V7 source identity changed")
    require(sha256(STUDY_NATIVE) == EXPECTED_NATIVE, "Digit study native hash differs from the reviewed proposal")
    receipt = json.loads(STUDY_RECEIPT.read_text())
    require(receipt["outputNative"]["sha256"] == EXPECTED_NATIVE, "Digit study receipt does not bind the expected native")
    require(not OUT_DIR.exists() and not AUDIT_DIR.exists(), "Refusing to overwrite an existing runtime derivative or audit")
    OUT_DIR.mkdir(parents=True, exist_ok=False)
    AUDIT_DIR.mkdir(parents=True, exist_ok=False)
    script_copy = AUDIT_DIR / Path(__file__).name
    shutil.copy2(Path(__file__).resolve(), script_copy)
    require(sha256(script_copy) == sha256(Path(__file__).resolve()), "Exporter script snapshot differs")

    # Import only the existing V7 reviewed export function. Its unrelated build
    # entry point is never called; all file identities and output paths here are
    # specific to the separate digit-study derivative.
    spec = importlib.util.spec_from_file_location("v7_export_rules", EXPORTER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    bpy.ops.wm.open_mainfile(filepath=str(STUDY_NATIVE))
    scene = bpy.context.scene
    scene.frame_set(1)
    bpy.context.view_layer.update()
    expected_snapshot = module.scene_snapshot()
    pivots_before = {obj.name: matrix_rows(obj.matrix_world) for obj in bpy.data.objects if obj.type == "EMPTY"}
    native_objects = {"empties": [], "meshes": [], "curves": []}
    batches = {}
    for obj in bpy.data.objects:
        if obj.type == "EMPTY":
            native_objects["empties"].append(obj.name)
        elif obj.type == "CURVE":
            native_objects["curves"].append(obj.name)
        elif obj.type == "MESH":
            native_objects["meshes"].append(obj.name)
            owner = obj.parent.name if obj.parent else None
            key = (owner, obj.get("exteriorEras", module.ALL_ERAS),
                   obj.get("region", "back"), obj.get("surfaceRole", "frame"))
            batches.setdefault(key, []).append(obj.name)
    require(len(pivots_before) == 51, f"Unexpected native pivot count: {len(pivots_before)}")
    require(len(native_objects["meshes"]) == 699, f"Unexpected native mesh count: {len(native_objects['meshes'])}")
    study_guards = [name for name in native_objects["meshes"] if "dorsal guard" in name]
    require(len(study_guards) == 12, f"Expected twelve study guard meshes; got {len(study_guards)}")
    require(all(key[0] and key[1] and key[2] and key[3] for key in batches),
            "Unclassified or unparented mesh cannot be batched under V7 rules")

    require(not OUT_GLB.exists(), "Refusing to overwrite runtime GLB")
    module.export_from_reopened_native(STUDY_NATIVE, OUT_GLB, expected_snapshot, {})
    pivots_after = {obj.name: matrix_rows(obj.matrix_world) for obj in bpy.data.objects if obj.type == "EMPTY"}
    require(pivots_after == pivots_before, "V7 batching/export changed a native pivot world matrix")
    require(sha256(STUDY_NATIVE) == EXPECTED_NATIVE, "The native study changed during export")
    glb_sha = sha256(OUT_GLB)
    manifest = {
        "capturedAtUtc": datetime.now(timezone.utc).isoformat(),
        "status": "runtime derivative for motion and geometric screening only; not selected in app",
        "inputs": {
            "studyNative": {"path": str(STUDY_NATIVE.relative_to(ROOT)), "sha256": EXPECTED_NATIVE,
                            "bytes": STUDY_NATIVE.stat().st_size},
            "studyReceipt": {"path": str(STUDY_RECEIPT.relative_to(ROOT)), "sha256": sha256(STUDY_RECEIPT)},
            "v7Native": {"path": str(V7_NATIVE.relative_to(ROOT)), "sha256": EXPECTED_V7_NATIVE},
            "v7RuntimeGlb": {"path": str(V7_GLB.relative_to(ROOT)), "sha256": EXPECTED_V7_GLB},
            "reviewedExportSource": {"path": str(EXPORTER.relative_to(ROOT)), "sha256": sha256(EXPORTER)},
        },
        "exportScript": {"executedPath": str(Path(__file__).resolve().relative_to(ROOT)),
                         "sha256": sha256(Path(__file__).resolve()),
                         "snapshotPath": str(script_copy.relative_to(ROOT)), "snapshotSha256": sha256(script_copy)},
        "outputGlb": {"path": str(OUT_GLB.relative_to(ROOT)), "sha256": glb_sha, "bytes": OUT_GLB.stat().st_size},
        "blenderVersion": bpy.app.version_string,
        "method": "Called existing V7 export_from_reopened_native on a reopened copy of the digit-study native; modifier evaluation/conversion and object batching occurred only in that unsaved export copy.",
        "nativeInventory": {key: sorted(names) for key, names in native_objects.items()},
        "batchContract": [{"parent": key[0], "exteriorEras": key[1], "region": key[2],
                           "surfaceRole": key[3], "objectNames": sorted(names)}
                          for key, names in sorted(batches.items(), key=lambda item: item[0])],
        "pivotWorldMatrices": pivots_before,
        "summary": {"nativeMeshObjects": len(native_objects["meshes"]), "studyGuardMeshes": len(study_guards),
                    "batchCount": len(batches), "pivotCount": len(pivots_before),
                    "nativeBytesUnchanged": True, "batchingPivotMatricesExact": True},
        "limits": [
            "This GLB is a separate diagnostic derivative; no application URL, fallback, runtime source or release inventory was changed.",
            "The exporter applies/converts modifiers in a reopened in-memory copy; the native study stays editable and byte-identical.",
            "Animation, claw contact, geometric clearance and viewer rendering are evaluated separately; this export receipt alone is not evidence for them.",
        ],
    }
    output = AUDIT_DIR / "runtime-derivative.json"
    with output.open("x") as stream:
        json.dump(manifest, stream, indent=2, sort_keys=True)
        stream.write("\n")
    require(sha256(STUDY_NATIVE) == EXPECTED_NATIVE, "Native changed after derivative receipt generation")
    print("DIGIT_STUDY_RUNTIME_EXPORTED", json.dumps({"glb": str(OUT_GLB.relative_to(ROOT)),
          "sha256": glb_sha, "bytes": OUT_GLB.stat().st_size, "nativeMeshes": len(native_objects['meshes']),
          "pivots": len(pivots_before), "batches": len(batches)}, sort_keys=True))


if __name__ == "__main__":
    main()
