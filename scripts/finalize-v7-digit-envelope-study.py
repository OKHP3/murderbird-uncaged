"""Read-only finalizer for the already-generated V7 digit-envelope native study."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json

import bpy

ROOT = Path(__file__).resolve().parents[1]
RUN = "attempt-03"
SOURCE = ROOT / "assets/models/uncaged-alignment-v7/murderbird-alignment-v7.blend"
SOURCE_GLB = ROOT / "assets/models/uncaged-alignment-v7/murderbird-alignment-v7.glb"
SOURCE_INVENTORY = ROOT / "assets/models/uncaged-alignment-v7/alignment-inventory.json"
REFERENCE = ROOT / "assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png"
MODEL = ROOT / f"assets/models/uncaged-digit-envelope-study-v1/iterations/{RUN}/murderbird-uncaged-digit-envelope-study-v1.blend"
AUDIT = ROOT / f"assets/audit/digit-envelope-study-v1/iterations/{RUN}"
GENERATION = AUDIT / "study-v7-digit-envelope.py"
OUTPUT = AUDIT / "study-receipt.json"
EXPECTED_NATIVE = "a8fccaf024a096678415215029b34cae8270b348da2301b8872a34e72c75ed3f"
EXPECTED_GLB = "1c82874b86af6b493ac380536de6af72a30fafa3a4b0ebb3d8790f56ffc03018"
ORPHANS = ("Neutral / edge.001", "Neutral / plate.001")


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path, data):
    with path.open("x") as stream:
        json.dump(data, stream, indent=2, sort_keys=True)
        stream.write("\n")


def main():
    for path in (SOURCE, SOURCE_GLB, SOURCE_INVENTORY, REFERENCE, MODEL, GENERATION):
        require(path.is_file(), f"Missing bound input: {path}")
    require(sha256(SOURCE) == EXPECTED_NATIVE and sha256(SOURCE_GLB) == EXPECTED_GLB,
            "Frozen V7 source identity changed")
    require(not OUTPUT.exists(), f"Refusing to overwrite final receipt: {OUTPUT}")
    ns = {}
    spec = importlib.util.spec_from_file_location("executed_digit_study", GENERATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    ns = module.__dict__

    before_path = AUDIT / "snapshot-before-save.json"
    reload_path = AUDIT / "snapshot-after-reload.json"
    diff_path = AUDIT / "snapshot-reload-diff.json"
    before_snapshot = json.loads(before_path.read_text())
    reload_snapshot = json.loads(reload_path.read_text())
    require(before_snapshot == reload_snapshot and json.loads(diff_path.read_text()) == [],
            "Generation run did not record a clean saved/reloaded snapshot")

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    source_snapshot = module.snapshot()
    source_links = [obj for obj in bpy.data.objects if obj.type == "MESH" and obj.name.startswith(module.LINK_PREFIX)]
    require(len(source_links) == 12, "Frozen V7 input no longer has twelve Digit inner links")
    source_endpoints = {obj.name: module.endpoint_record(obj) for obj in source_links}

    bpy.ops.wm.open_mainfile(filepath=str(MODEL))
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    study_snapshot = module.snapshot()
    require(study_snapshot == before_snapshot,
            "Saved native differs from its recorded pre-save and post-reload snapshots")
    require(source_snapshot["empties"] == study_snapshot["empties"], "Pivot identities/world matrices changed")
    require(source_snapshot["curves"] == study_snapshot["curves"], "Source control curves changed")
    require(source_snapshot["materials"] == study_snapshot["materials"], "Material shader signatures changed")
    study_meshes = study_snapshot["meshes"]
    source_meshes = source_snapshot["meshes"]
    link_names = set(source_endpoints)
    new_names = sorted(set(study_meshes) - set(source_meshes))
    require(set(study_meshes) == set(source_meshes) | set(new_names), "Study mesh inventory lost source objects")
    require(len(new_names) == 12 and all("dorsal guard" in name for name in new_names),
            f"Unexpected added mesh allowlist: {new_names}")
    require(len(set(source_meshes) - set(study_meshes)) == 0, "Study deleted source mesh objects")
    for name, record in source_meshes.items():
        study_record = study_meshes[name]
        if name in link_names:
            for field in ("parent", "matrix", "props", "visibility"):
                require(study_record[field] == record[field], f"Digit link object state changed: {name}/{field}")
        else:
            require(study_record == record, f"Unchanged source mesh differs: {name}")

    links_report, guards_report = [], []
    for name, prior in source_endpoints.items():
        obj = bpy.data.objects[name]
        require(obj.parent.name == prior["owner"], f"Owner changed for link: {name}")
        require(module.max_matrix_delta(prior["objectWorldMatrix"], module.matrix_rows(obj.matrix_world)) <= module.MATRIX_TOLERANCE,
                f"World transform changed for link: {name}")
        module.retained_endpoint_membership(obj, prior)
        bounds = module.object_bounds(obj)
        require(all(abs(prior["bounds"][axis][i] - bounds[axis][i]) <= module.BOUND_TOLERANCE
                    for axis in ("min", "max") for i in range(3)), f"Local bounds/contact dimensions changed: {name}")
        links_report.append({"name": name, "owner": prior["owner"], "worldMatrix": prior["objectWorldMatrix"],
                             "retainedProximalVertices": 12, "retainedDistalVertices": 12, "bounds": bounds})
    for name in new_names:
        obj = bpy.data.objects[name]
        require(obj.parent is not None and obj.get("surfaceRole") == "plate" and obj.get("region") == "foot" and
                obj.get("exteriorEras") == "maker,mechanic,builder" and obj.get("constructionClass") == "inherited-passive",
                f"Guard ownership/era/surface metadata differs: {name}")
        guards_report.append({"name": name, "parent": obj.parent.name, "pairedLink": obj.get("pairedLink"),
                              "region": obj.get("region"), "surfaceRole": obj.get("surfaceRole"),
                              "eras": obj.get("exteriorEras"), "constructionClass": obj.get("constructionClass"),
                              "geometryStatus": obj.get("geometryStatus"), "vertices": len(obj.data.vertices),
                              "faces": len(obj.data.polygons)})
    require(len(links_report) == len(guards_report) == 12, "Guard/link object count differs")

    orphan_report = []
    for name in ORPHANS:
        source_material = source_snapshot["materials"].get(name)
        material = bpy.data.materials.get(name)
        require(source_material is not None and material is not None and material.use_fake_user,
                f"Source orphan material not retained: {name}")
        require(module.material_signature(material) == source_material, f"Orphan material shader changed: {name}")
        orphan_report.append({"name": name, "sourceUsers": 0, "sourceUseFakeUser": False,
                              "studyUseFakeUser": True, "shaderSignatureExact": True,
                              "shaderSignature": source_material})

    images = []
    for stem, camera in (("v7-before-three-quarter", [-4.0, -6.0, 0.6]),
                         ("v7-before-side", [-6.0, -0.1, 0.32]),
                         ("study-after-three-quarter", [-4.0, -6.0, 0.6]),
                         ("study-after-side", [-6.0, -0.1, 0.32])):
        path = AUDIT / f"{stem}.png"
        require(path.is_file(), f"Missing comparison still: {path}")
        images.append({"path": str(path.relative_to(ROOT)), "sha256": sha256(path),
                       "bytes": path.stat().st_size, "camera": camera,
                       "target": [0.0, -0.1, 0.31], "projection": "orthographic", "orthoScale": 0.98})

    require(sha256(SOURCE) == EXPECTED_NATIVE and sha256(SOURCE_GLB) == EXPECTED_GLB,
            "Frozen V7 source changed during finalization")
    receipt = {
        "capturedAtUtc": datetime.now(timezone.utc).isoformat(),
        "status": "native-only geometry proposal; not owner accepted",
        "execution": {"generationOutcome": "native save, reload checks, and four still renders completed; original process then exited during receipt serialization because Blender invalidated pre-reload Object references",
                      "finalization": "read-only Blender pass reopened exact source and study natives by path, recomputed source-versus-study inventory, pivots, curves, material signatures, links, and guard ownership; did not render or save either native"},
        "inputs": {"native": {"path": str(SOURCE.relative_to(ROOT)), "sha256": sha256(SOURCE), "bytes": SOURCE.stat().st_size},
                   "glb": {"path": str(SOURCE_GLB.relative_to(ROOT)), "sha256": sha256(SOURCE_GLB), "bytes": SOURCE_GLB.stat().st_size},
                   "inventory": {"path": str(SOURCE_INVENTORY.relative_to(ROOT)), "sha256": sha256(SOURCE_INVENTORY)},
                   "reference": {"path": str(REFERENCE.relative_to(ROOT)), "sha256": sha256(REFERENCE),
                                 "use": "Viewed candidate03 image as qualitative toe-construction reference, not dimensional metrology"}},
        "scripts": {"generation": {"path": str(GENERATION.relative_to(ROOT)), "sha256": sha256(GENERATION)},
                    "finalizer": {"path": str(Path(__file__).resolve().relative_to(ROOT)), "sha256": sha256(Path(__file__).resolve())}},
        "outputNative": {"path": str(MODEL.relative_to(ROOT)), "sha256": sha256(MODEL), "bytes": MODEL.stat().st_size},
        "blenderVersion": bpy.app.version_string,
        "changedLinkMeshes": sorted(link_names), "addedGuards": guards_report,
        "preservation": {"pivotCount": len(study_snapshot["empties"]), "allPivotMatricesExact": True,
                         "unmodifiedMeshCount": len(source_meshes) - len(link_names), "allUnmodifiedMeshesExact": True,
                         "controlCurvesExact": True, "shaderSignaturesExact": True,
                         "sourceOrphanMaterialMetadata": orphan_report,
                         "all12LinkObjectOwnersTransformsBoundsAndEndpointVerticesExact": True,
                         "allSixTalonsExact": True, "newGuardCount": len(guards_report)},
        "attachments": links_report,
        "comparisonStills": images,
        "scopeLimits": [
            "Separate native Blender geometry study only; no GLB, app/runtime selection, motion contact, or mechanical validation.",
            "End-ring vertices, object transforms and bounds were retained exactly; this does not prove load capacity or grasp performance.",
            "Dorsal guards use inherited passive classification and existing plate material; they add no powered hardware.",
            "Inherited V7 control curves do not regenerate these new guards.",
            "The proposal improves the large rounded link profile but remains visibly sparse relative to candidate03 coverings; F04 is not closed.",
        ],
    }
    write_new(OUTPUT, receipt)
    print("DIGIT_STUDY_RECEIPT_FINALIZED", json.dumps({"receipt": str(OUTPUT.relative_to(ROOT)),
          "modelSha256": receipt["outputNative"]["sha256"], "links": len(links_report), "guards": len(guards_report),
          "stills": len(images), "finalizerSha256": sha256(Path(__file__).resolve())}, sort_keys=True))


if __name__ == "__main__":
    main()
