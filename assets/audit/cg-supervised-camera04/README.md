# Camera04: camera accounts for only part of the alignment gap

[Review](review.html) · [Source landmarks](source-landmarks.png) · [Best overlay](best-overlay.png) · [Eight hypotheses](hypothesis-sheet.png) · [Exact receipts](receipt.json)

Frozen integration04 is unchanged. The declared-landmark compromise is **orthographic 35° from side, 16° elevation**. Weighted RMS falls from **80.40 to 72.22 pixels** (10.2%). This is a comparison proposal, not recovery of the source's physical camera or owner artistic acceptance. Elevation reaches the tested grid boundary; pose and camera remain entangled.

Thirteen manually declared source points cover crown, visible optic, bill hook, shoulder, breast, knees, hocks, ankles and plantar housing centers. Lower weights mark ambiguous breast and partly occluded far-side landmarks. Pixel coordinates, exact existing mesh/world correspondences, projected coordinates and every residual are in the receipt. July is excluded entirely; its body has no authority here. Hidden hips, far optic and overlapping toe tips are excluded from fitting; the complete foot silhouette remains in the crop gate.

| Hypothesis | Weighted RMS px | Knee separation px | Ankle separation px |
|---|---:|---:|---:|
| Declared source | — | 230 | 217 |
| Original canonical | 80.40 | 44 | 58 |
| Ortho 35° proposal | 72.22 | 83 | 109 |
| Ortho 50° | 73.27 | 112 | 146 |
| Ortho 80° | 94.80 | 143 | 186 |
| 65mm perspective at 35° | 72.49 | 79 | 101 |

The frontal hypothesis separates feet but loses the source's right-offset head and recognizable side profile. Perspective provides no score improvement. The proposed raster silhouette is 372px wide versus the approximately 476px source envelope; its height is 822px versus approximately 802px. Increasing scale cannot resolve this width deficit while preserving the complete bird.

**Inferred remaining geometry gaps:** the head optic and hooked bill remain left of the source positions; the bill reads vertically narrow, the lower head/cheek opening differs, the shield/body envelope remains too narrow, and the leg/foot centers remain substantially too close together. These observations do not authorize stance or geometry changes.

Use `camera(root_path)` from `scripts/cg-supervised-camera04.py` identically for before/candidate. It returns Blender location, Euler rotation, projection, orthographic scale, shifts, 65mm lens and exact 1280×853 resolution. The hypothesis sheet alone uses an identical display crop; full renders and overlay retain source aspect and entire bird.

| Claim | Tier | Evidence | Consequence if false | Next check |
|---|---|---|---|---|
| Input bytes and original payload preserved | Confirmed | Matching SHA256; 6,861 objects; unchanged material graphs | Invalid diagnostic | Integrator readback |
| Camera alone leaves large shape/stance gaps | Inferred | Overlay and residuals | Misassigned geometry work | Owner review |
| True source camera recovered | Unknown | No calibration or depth ground truth | False metrology | Additional matched source views |

Inputs: native SHA `5809c13d…bed254`; controlling owner-reissued JPG SHA `645d47c0…04114`; full hashes and paths in receipt. Reviewed shared goal at `251f2f0243181e97140179c2aff6eb057e165438`; checkout base `887da78`. Neutral clay/PBR renders, alpha-bound checks and preservation checks ran locally. No native save, runtime edit, build, deployment, remote synchronization or publication performed. Source pixels appear only in internal review diagrams, never textures. Creative content remains all rights reserved.
