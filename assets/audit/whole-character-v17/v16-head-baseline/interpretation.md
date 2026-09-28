# V16 head/jaw clearance baseline

Input: `assets/models/whole-silhouette-v16/attempt-03/murderbird-whole-silhouette-v16.blend`, SHA-256 `3bd4b2e34d086fa15dbc9c06cdbcc0606b02430f9482f9d8d6877d39bec1318a`. The native was opened read-only by `executed-check.py`; successful Blender output is preserved in `blender.log`.

## Result

The checker found the same four strict non-coplanar crossing identities at every sampled jaw angle `0.00, 0.04, 0.08, 0.12, 0.16, 0.20, 0.24, 0.28, 0.32` radians (4 pairs per sample; 36 pair/sample observations). It screened 5 jaw-owned meshes against 117 meshes owned by head, upper-bill, cranial-cover, and builder-optics. Era-ineligible fixed meshes were retained conservatively.

| Pair | Strict crossing triangles (moving / fixed) | Reading |
|---|---:|---|
| `Forked forged mandible -1` ↔ `Coaxial mandible journal` | 40 / 11–13 | **Likely intended journal interface.** Matching side/name and localized bounds near the jaw pivot are consistent with a moving journal seated in its coaxial head-owned journal. The strict intersections are real triangle crossings; “likely intended” is a geometry-role interpretation, not proof of bearing fit or acceptable running clearance. |
| `Forked forged mandible 1` ↔ `Coaxial mandible journal.001` | 40 / 11–13 | **Likely intended mirrored journal interface**, subject to the same qualification. |
| `Mandible journal cap` ↔ `Broad swept cheek band -1` | 6–8 / 58 | **Localized probable cap-seat overlap.** Bounds remain near the same-side pivot region (approximately X −0.141 to −0.129, Y −0.355 to −0.305, Z 1.529 to 1.573 native units). The matching names and bilateral position suggest a retainer or cap seating into cheek structure. That is not established from the mesh names alone. |
| `Mandible journal cap.001` ↔ `Broad swept cheek band 1` | 6–9 / 58 | **Localized probable mirrored cap-seat overlap.** Bounds are near the opposite pivot (approximately X +0.129 to +0.141, Y −0.355 to −0.304, Z 1.522 to 1.573 native units). This is not a broad skull-surface crossing in the sampled result. |

The first pair's moving/fixed crossing-triangle bounds are localized around X −0.128 to −0.080, Y −0.370 to −0.328, Z 1.505 to 1.540; the mirrored pair occupies the corresponding positive-X region. Exact pair-specific triangle IDs, example vertex triples, and per-angle candidate counts are in `head-clearance.json`. No other strict crossing identity appears in the checker output, so this run did not expose a prominent unrelated jaw-to-head/bill/cover/optic surface crossing in its sampled scope.

## Limits

This is a nine-position sample from 0 to 0.32 radians using evaluated triangle surfaces and a strict non-coplanar edge-through-face kernel. Tangent/coplanar contact is excluded. The likely journal and cap seats remain strict crossings, not clearance passes. The screen does not test containment, continuous motion between samples, contact forces, physical simulation, or owner likeness. The output is an inherited V16 baseline, not evidence about later V17 geometry.
