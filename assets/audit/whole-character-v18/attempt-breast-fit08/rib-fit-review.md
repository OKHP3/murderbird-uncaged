# V18 attempt breast-fit08: rib-only and joint-boundary review

Status: held regional proposal. It is not integrated into the application and does not have artistic acceptance.

The input is V17 attempt02 native SHA-256 `7d371907b279eb3d625e67164d84a78b2901a5cb6a79917def07f48ff8792d7b`; the candidate native is SHA-256 `a4f9ffd68067e14d5ff9e6abf8fc1d1c116d55692381d18673bfd4db5495147c`. The frozen composition receipt is [receipt.json](receipt.json). The matched neutral images are [breast close-up](after-breast.png) and [whole-bird three-quarter](after-reference-angle.png).

## Rib-only result

Only `Passive rib behind access cover.002` and `.003` changed in the body-owned breast/frame region. Each source tube has 492 vertices arranged as 41 ordered 12-vertex cross-section rings. The refit translates complete rings along Y, keeps rings with a vertex within 5 mm of either thoracic support rail fixed, and places the remaining anterior arc behind the evaluated access-shell back face with a 6 mm target offset. It does not clip individual tube vertices independently.

The candidate receipt records 17 and 18 translated rings, three rail-contact rings retained on each rib, maximum translation 6.47 mm and 19.43 mm, and maximum cross-section radius deviation below `0.00000006 m`. Because each ring is rigidly translated, its cross-section thickness/area is preserved to floating-point tolerance. The 19.43 mm shift on rib `.003` is substantial and remains a fit-review item.

The read-only triangle-crossing diagnostic replayed all 21 V17 runtime-module samples on both native files using the same strict noncoplanar edge-through-face kernel. In the scoped rib pairs, V17 has 132 strict pair/sample hits (38 shell-to-rib and 94 first-course-plate-to-rib); V18 has 12 (8 shell-to-rib and 4 first-course-plate-to-rib). The remaining V18 hits occur only during breast opening at 0.25, 0.5, 0.75, and 1.0, separation 0: both ribs cross the moving access shell at each sample, and the first-course left plate 4 crosses rib `.003`.

| Pair | Opening samples | X bounds | Y bounds | Z bounds |
|---|---|---:|---:|---:|
| Access shell / rib `.002` | 0.25, 0.5, 0.75, 1.0 | −0.3101…−0.2051 | −0.3346…−0.2123 | 1.0876…1.1216 |
| Access shell / rib `.003` | 0.25, 0.5, 0.75, 1.0 | −0.2895…−0.1854 | −0.3593…−0.2237 | 1.2158…1.2679 |
| First-course left plate 4 / rib `.003` | 0.25, 0.5, 0.75, 1.0 | −0.2823…−0.1920 | −0.3700…−0.2624 | 1.2407…1.2570 |

Root's coordinate review found the breastplate pivot at `(-0.305745, -0.359937, 1.27460)` lies inside the new shell planform (`X ±0.370`, `Y −0.456…+0.074`). The current vertical-axis swing carries the shell rearward into the body-fixed frame. The rib refit therefore improves rest fit but does not fix the access path. Do not treat those opening intersections as a reason to keep bending the ribs; this candidate is **REST-FIT ONLY / INSPECTION FAIL**. The next geometry/kinematics contract should preserve the closed shell and frame fit, then place a finite hinge at the outer lateral or rear shell boundary, or justify a translating hinge with explicit supports, before repeating a fresh pose sample. This report does not change pivots. The per-sample results and unchanged V17 baseline are in [candidate strict crossings](strict-crossings/strict-crossings.json) and [V17 strict baseline](strict-baseline-v17/strict-crossings.json).

## Neck/breast result

The neck-owned module changed only `Throat formed lamina 4`, `5`, and `6`; the nominated flank lamina 5/6 meshes were already inside the proposed radial envelope and remained unchanged. The module reshaped guard vertices outside a proposed 0.272 m central to 0.290 m outboard cylindrical envelope around the inherited neck pitch axis `(Y=-0.16981055, Z=1.2312945)`, with native X as its axis. This dimension is a reconstruction choice, not a reference measurement. The upper breast shell, first course, support frame, owners, 52 pivots, materials, and authoring curves remain as before.

The close-up still shows a dark neck/breast slit and hanging, tapered guard returns. Strict checks across the same 21 samples record 231 first-course/neck-guard pair-sample crossings, compared with 85 on V17. This profile did not establish an acceptable sliding interface. The entire neck module is held and must not be integrated. The next construction should rebuild a finite, coherent lower guard and breast-opening lip together around the existing pivot, rather than applying another surface clamp.

## Evidence limits

The pose packet is a fresh Node sample of the actual runtime modules, not browser captures. This is a discrete mesh-surface crossing check, not a continuous sweep, containment-depth test, strength assessment, or validation of a supported sliding bearing. The neutral Workbench images document geometry only; they do not show WebGL or certify likeness. V18 attempt01/02/03/04/05/06/07 are preserved as separate trials; none is promoted by this review.
