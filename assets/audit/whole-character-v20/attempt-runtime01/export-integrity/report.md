# Runtime01 export warning investigation

Result: a real inherited modifier defect, not a harmless warning and not uniquely introduced by the V20 cage. Read-only investigation; no model or source was changed or exported by these scripts.

The warning names the retained **mesh datablock**, `V17 breast directional lamina 1 1 left mesh`. The actual exported object is the72-part `breastplate-breast-plate` group. The defective source members are **`V17 breast directional lamina 3 1 left` and `...right`**.

All744 raw editable meshes validate without repairs in pinned V19, proportions02 and runtime01. Exactly these two source members need validation after modifier evaluation in all three. Each source has345vertices/308faces, two exact/near-exact collapsed edges and two duplicate positions. Their6mm Solidify alone stays finite, closed and positive-volume. Adding the1.7mm two-segment angle-limited Bevel creates one NaN vertex per side. The evaluated bevel mesh remains topologically closed, but its volume is nonfinite; topology alone cannot validate its solid.

| Stage | V19 | proportions02/runtime01 |
| --- | --- | --- |
| Raw validation repairs |0|0|
| Evaluated validation repairs |2 source meshes|2 source meshes|
| After export conversion/face cleanup |same2 meshes|same2 meshes|
| Joined validation repair |one breast group/two NaN coordinates|one breast group/two NaN coordinates|
| Joined group vertices/faces |70710/70470|70714/70488|
| Joined boundary/wire edges after cleanup |164/116|134/104|
| Group near-zero triangles before→after validation (area≤1e-14m²) |34→42|45→53|

The export helper deletes faces with area<1e-12m² before joining, but NaN area does not satisfy that comparison. The installed glTF exporter subsequently calls Mesh.validate, which changes each NaN coordinate to the group-local origin. The warning therefore accompanies a geometry substitution, not just a label.

Existing runtime01 GLB has two origin vertices and10 incident triangles in the breast group. Its longest incident edge is361.31mm (already336.74mm in V19). The runtime origin in native coordinates is(-.305745,-.377337,1.407909); intended neighboring seam geometry lies nearX±.00603,Y-.42405,Z1.23138. This produces long triangle excursions from the tiny seam feature. Finite exported numbers are not source-surface parity.

Existing GLBs both have111meshes/113primitives, no out-of-range indices, no nonfinite position/normal values, and no zero-length normals. V19 has551392triangles/124 near-zero triangles; runtime01 has551484/131. Runtime01's53 breast near-zero triangles compare with42 in V19; both retain74 in `upper-bill-head-plate` and4 in `cervical-upper-neck-bearing`. The V19-only4 in `neck-neck-bearing` disappear in runtime01, explaining the net+7. Degenerate counts are threshold diagnostics, not independent failure scores.

The remaining joined boundary/wire edges and position-welded exported multiplicities are documented in the JSON. Approximate welding can merge coincident independent pieces; no manifold, collision, motion or engineering acceptance follows from buffer validity.

Files: native-stages-summary.json and three stage packets; lamina-modifier-cause.json/log for modifier-prefix isolation and witnesses; both glb-integrity.json packets; repaired-origin.json and exported-origin-triangles.json; exact executed investigation scripts/logs. Native and GLB hashes stayed unchanged. Raw stage JSON uses NaN to represent nonfinite volumes; the narrative explicitly treats them as invalid, not positive finite solids.

Recommended narrowly scoped correction: remove the two inherited coincident-tip degeneracies in each editable lamina before the retained Solidify/Bevel stack, then regenerate a new derivative and verify evaluated geometry and export. Do not silently accept exporter origin substitution or blanket-delete affected identity geometry.
