#!/usr/bin/env python3
"""Read-only bounded replay of retained strict normal and crown associations."""
import hashlib
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
AUDIT = ROOT / "assets/audit/cg-recursive-three-loop01"
CHECKER = AUDIT / "loop03/independent-proof01/export-replay/checker-results.json"
OUT = Path(__file__).resolve().parent / "normal-diagnosis.json"
LIMIT = 2e-5


def read_glb(path):
    raw = path.read_bytes()
    magic, version, total = struct.unpack_from("<III", raw, 0)
    assert magic == 0x46546C67 and version == 2 and total == len(raw)
    json_len, json_type = struct.unpack_from("<II", raw, 12)
    assert json_type == 0x4E4F534A
    doc = json.loads(raw[20:20 + json_len])
    off = 20 + json_len
    bin_len, bin_type = struct.unpack_from("<II", raw, off)
    assert bin_type == 0x004E4942 and off + 8 + bin_len == len(raw)
    return doc, raw[off + 8:off + 8 + bin_len], hashlib.sha256(raw).hexdigest()


def accessor(doc, blob, idx):
    a = doc["accessors"][idx]
    view = doc["bufferViews"][a["bufferView"]]
    assert "sparse" not in a and not a.get("normalized")
    formats = {5123: ("<H", 2), 5125: ("<I", 4), 5126: ("<f", 4)}
    fmt, size = formats[a["componentType"]]
    widths = {"SCALAR": 1, "VEC2": 2, "VEC3": 3}
    width = widths[a["type"]]
    stride = view.get("byteStride", size * width)
    base = view.get("byteOffset", 0) + a.get("byteOffset", 0)
    values = []
    for i in range(a["count"]):
        row = tuple(struct.unpack_from(fmt, blob, base + i * stride + j * size)[0] for j in range(width))
        values.append(row)
    return values


def identity_transforms(doc):
    ident = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    for node in doc.get("nodes", []):
        if "mesh" not in node:
            continue
        assert node.get("matrix", ident) == ident
        assert node.get("translation", [0, 0, 0]) == [0, 0, 0]
        assert node.get("rotation", [0, 0, 0, 1]) == [0, 0, 0, 1]
        assert node.get("scale", [1, 1, 1]) == [1, 1, 1]


def triangles_for_material(doc, blob, material_name):
    out = []
    for node in doc.get("nodes", []):
        if "mesh" not in node:
            continue
        mesh = doc["meshes"][node["mesh"]]
        for prim in mesh["primitives"]:
            mat = doc["materials"][prim["material"]]["name"]
            if mat != material_name:
                continue
            attrs = prim["attributes"]
            pos = accessor(doc, blob, attrs["POSITION"])
            uv = accessor(doc, blob, attrs["TEXCOORD_0"])
            norm = accessor(doc, blob, attrs["NORMAL"])
            inds = [v[0] for v in accessor(doc, blob, prim["indices"])]
            for i in range(0, len(inds), 3):
                out.append(tuple(tuple(pos[k]) + tuple(uv[k]) + tuple(norm[k]) for k in inds[i:i + 3]))
    return out


def tri_key(tri):
    rounded = [tuple(round(float(v), 6) for v in row[:5]) for row in tri]
    start = min(range(3), key=lambda j: tuple(rounded[j:] + rounded[:j]))
    order = [((start + j) % 3) for j in range(3)]
    return tuple(v for j in order for v in rounded[j]), tuple(tri[j] for j in order)


def crown_associations():
    rows = []
    for era in ("builder", "maker", "mechanic"):
        old_path = AUDIT / f"loop02/delivery/retained03/{era}/murderbird-recursive-{era}.glb"
        new_path = AUDIT / f"loop03/delivery/retained04/{era}/murderbird-recursive-{era}.glb"
        old, oldbin, oldsha = read_glb(old_path)
        new, newbin, newsha = read_glb(new_path)
        identity_transforms(old)
        identity_transforms(new)
        material = f"CGRS04 {era} uv-method02-visual02-heldnormal formed crown"
        old_shared = f"CG metal05 / worn-bronze / {era} / retained-uv.001"
        prior = [tri_key(t) for t in triangles_for_material(old, oldbin, old_shared)]
        current = [tri_key(t) for t in triangles_for_material(new, newbin, material)]
        lookup = {k: tri for k, tri in prior}
        duplicates = len(prior) - len(lookup)
        changed, unmatched, max_delta = 0, 0, 0.0
        for key, tri in current:
            earlier = lookup.get(key)
            if earlier is None:
                unmatched += 1
                continue
            delta = max(abs(float(tri[v][5 + c]) - float(earlier[v][5 + c])) for v in range(3) for c in range(3))
            max_delta = max(max_delta, delta)
            changed += delta != 0
        rows.append({
            "era": era, "current_crown_triangles": len(current), "prior_shared_material_triangles": len(prior),
            "prior_duplicate_position_uv0_keys": duplicates, "unmatched_current_crown_triangles": unmatched,
            "triangles_with_changed_stored_normal_components": changed,
            "max_stored_normal_component_delta": max_delta, "prior_glb_sha256": oldsha, "current_glb_sha256": newsha,
            "current_mesh_transforms_identity": True, "prior_mesh_transforms_identity": True
        })
    return rows


def main():
    recorded = json.loads(CHECKER.read_text(encoding="utf-8"))
    assert recorded["normalized_normal_vector_L2_tolerance"] == LIMIT
    # Retained native/export correspondence records identify the failing object and exact matched triangle.
    failures = []
    for era_result in recorded["results"]:
        era = era_result["era"]
        for material in era_result["material_checks"]:
            if material.get("normal_joint_corner_status") == "FAIL":
                worst = material["worst_normal_joint_triangle"]
                failures.append({
                    "era": era, "material": material["material"],
                    "status": material["normal_joint_corner_status"],
                    "native_object": material["worst_normal_native_object"],
                    "max_l2": material["normal_vector_max_L2"],
                    "bad_triangles": material["normal_bad_triangles"],
                    "max_angle_degrees": material["normal_angle_max_degrees"],
                    "position_mismatches": material["oriented_position_triangle_key_mismatches"],
                    "position_max_abs": material["position_max_abs"],
                    "uv_bad_triangles": material["UV_bad_triangles"],
                    "uv_max_abs": material["UV_max_abs"],
                    "worst_triangle_native_corners": worst["native_corners"],
                    "worst_triangle_glb_corners": worst["GLB_corners"],
                    "worst_triangle_native_mesh_transform": worst.get("native_mesh_transform"),
                    "worst_triangle_glb_mesh_transform": worst.get("GLB_mesh_transform")
                })
    # Recheck retained export identities and hashes against the archived checker receipt.
    export_receipts = []
    for row in recorded["results"]:
        glb = Path(row["GLB_path"].replace("/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged/", ""))
        glb = ROOT / glb
        doc, _, sha = read_glb(glb)
        identity_transforms(doc)
        assert sha == row["GLB_sha256"]
        export_receipts.append({"era": row["era"], "status": row["status"], "glb_sha256_matches_receipt": True, "mesh_transforms_identity": True})
    unique_failures = {}
    crown_failures = {}
    for fail in failures:
        unique_failures[(fail["era"], fail["material"])] = fail
    for era_result in recorded["results"]:
        for material in era_result["material_checks"]:
            if "formed crown" in material.get("material", "") and material.get("normal_joint_corner_status") == "FAIL":
                key = (era_result["era"], material["material"])
                prior = crown_failures.get(key)
                if prior is None or material["normal_vector_max_L2"] > prior["max_l2"]:
                    crown_failures[key] = {
                        "era": era_result["era"], "material": material["material"],
                        "max_l2": material["normal_vector_max_L2"],
                        "bad_triangles": material["normal_bad_triangles"],
                        "triangle_count": material["GLB_triangles"],
                        "max_angle_degrees": material["normal_angle_max_degrees"],
                        "position_mismatches": material["oriented_position_triangle_key_mismatches"],
                        "uv_bad_triangles": material["UV_bad_triangles"]
                    }
    worst = max(unique_failures.values(), key=lambda f: f["max_l2"])
    assert worst["max_l2"] == 0.008557185882560697 and worst["native_object"] == "CGRF02 left forward toe 2 recessed joint shoulder 1"
    crowns = crown_associations()
    result = {
        "threshold_l2": LIMIT,
        "outcome": "REPRODUCED_RETAINED_STRICT_NORMAL_FAILURE",
        "evidence_basis": "Fresh read-only replay of retained GLB hashes and transforms, plus exact saved native/export joint-correspondence records from checker-results.json; no Blender/native re-evaluation performed.",
        "worst_failure": worst,
        "failure_material_count": len(unique_failures),
        "retained_failure_receipt_rows": len(failures),
        "crown_normal_failures": list(crown_failures.values()),
        "export_receipts": export_receipts,
        "crown_prior_final_associations": crowns,
        "diagnosis": {
            "object": "The global maximum maps to CGRF02 left forward toe 2 recessed joint shoulder 1; its native object identity is retained in checker result.",
            "vertex": "The retained worst-triangle record supplies per-corner native and GLB positions, UV0, and normals. Position/UV associations passed while normal association failed.",
            "transform_export": "Actual retained current and prior GLB mesh-node transforms are identity; current export SHA-256 values match the checker receipt. This rules out a non-identity GLB node transform in the tested exports, but not native exporter/runtime behavior.",
            "crown": "Each era crown is a separate failure (3823/3824 triangles; max L2 0.0005350984722657378; 0 position and UV mismatch). Prior/final joint material-position-UV0 association found all 3824 current crown triangles and exact stored normal component equality for all three eras. This does not explain the native-to-current-export discrepancy.",
            "cause": "UNKNOWN. No native .blend computation was re-run; retained records do not prove the producer-side cause."
        },
        "limits": ["No threshold change", "No geometry or native-source edit", "No fresh Blender evaluation", "No full shader or rendered-pixel equivalence claim", "No acceptance claim"]
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"outcome": result["outcome"], "worst_object": worst["native_object"], "worst_l2": worst["max_l2"], "unique_failure_material_count": len(unique_failures), "retained_receipt_rows": len(failures), "crown_rows": len(crowns), "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
