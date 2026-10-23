# Appearance integration contract

This is the handoff boundary between the appearance proposal on `codex/appearance-production` and the parallel structural-geometry work. It records an integration method, not an accepted model or permission to publish. See [appearance-production-review.md](appearance-production-review.md) for the iteration-by-iteration rejection record and current verification and remaining artistic limits.

## Frozen source and proposal status

The appearance builder starts from frozen alignment-v3 source at `assets/models/uncaged-alignment-v3/murderbird-alignment-v3.blend` (SHA-256 `6de7c16728ac2ac4926b9b0bd608d7eb5e03f702d3e1ef222db997c84fd7ff3a`, structural-baseline revision `3e6d340e616e79708d2a62ec9255fd997d14ea4f`). The paired GLB SHA-256 is `c4dc308f77399410368b82443a1b21b9113cfedb258aa055906b4f13c92dda21`. The builder checks its native-file hash before building; appearance iterations do not update this baseline. The alignment inventory records 51 pivot parent/local/world/scale entries and the bill-contact and joint contracts. Treat those recorded transforms, rigid owners, all twelve digit hinges, functional contact geometry, and motion systems as the v3 exterior interface.

Iterations 01–06 and 08 have `rework` decisions. Iteration 07 is a superseded historical local browser checkpoint. Iteration 09 is generated from iteration 08 with unchanged geometry/hierarchy digests; its asset, optic, kinematic, packing, and authoring-view receipts pass, and it is staged as a candidate for local review. The exact hashes, facts, and art-review limits are recorded in [appearance-production-review.md](appearance-production-review.md). Local desktop WebGL and illustrated-fallback validation passed for the exact selected candidate; physical-device and mobile WebGL performance remain untested. The art-review receipt says the candidate remains below exact illustrative-reference likeness; owner acceptance is pending and not inferred.

## Files and regional ownership

The build orchestration is `scripts/build-uncaged-appearance-v1.py`; its five appearance modules are:

- `scripts/appearance-head-neck.py` — head and neck exterior surfaces, fitted to their existing rigid owners.
- `scripts/appearance-body-detail.py` — breast/body, back, shoulder and mantle transitions.
- `scripts/appearance-limb-casing.py` — limb casings and foot/toe-root transitions, preserving digit owners and contact geometry.
- `scripts/appearance-bill-finish.py` — ray-seated surface fixings and joining lines on the retained bill and mandible.
- `scripts/appearance-materials.py` — appearance materials and surface response across the authored exterior.

The builder snapshots these authoring sources into each generated iteration. It records and checks existing empty parentage and local transforms before/after authoring, then assigns additions to existing rigid owners and propagates era eligibility. Keep all original source meshes, empties, pivot hierarchy, and motion/contact systems. Additions must use the existing regional tags (`breast`, `shoulder`, `wing`, `back`, `leg`, `foot`) and surface roles (`plate`, `bearing`, `frame`, `inner`, `edge`, `recess`, `repair`). The anatomical-left repair landmark must remain identifiable. Do not move or replace pivots, toe owners, or foot/toe contact geometry.

## Reference scope and retargeting

The reference manifest is `assets/models/uncaged-alignment-v3/alignment-inventory.json`. Candidate 03 (`assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png`) is the lead-selected full-body illustrative reference; it does not establish measured dimensions, far-side topology, left repair detail, internal construction, or owner final-art approval. The owner-preferred July image under `context/threads/assets/murderbird-camera-series-2026-09-05/` is head identity only; its support, lower-body proportions, plate train, scale, and wing/rear silhouette are excluded. Era illustrations inform visible surface state, not hidden controls or engineering. These images are rights-reserved references under `NOTICE.md`, not grants of reuse rights.

The parallel structural thread continues independently; this appearance checkpoint does not establish its latest state or acceptance. Before integrating a selected structural checkpoint, freeze its exact source revision, Blender hash, GLB hash, owner/pivot inventory, and passing export, kinematic, and browser evidence. Make a new appearance iteration from a copy of that checkpoint; leave the parallel worktree and all v3 appearance iterations unchanged. Reconcile the v4 owners, transforms, surfaces, clearance envelopes, and era tags first. Reuse only compatible appearance surfaces and materials. Inspect structural head/neck edits before considering `appearance-head-neck.py`; do not blindly duplicate or replace improved structural geometry. Apply `appearance-materials.py` only after its region/role/era mapping is checked against the new inventory, and port other modules selectively to the actual revised geometry.

## Required evidence after retargeting

Run the selected checkpoint's export/build and the applicable checks against the retargeted result. At minimum, retain evidence for:

- export and asset/interface integrity, including finite actual `POSITION` values and the 4 m coordinate guard: `scripts/verify-appearance-assets.py` (or its v4-aware equivalent);
- optic visibility: `scripts/verify-appearance-optic.py` (updated for the selected checkpoint if needed);
- kinematic alignment and preserved owner/pivot transforms using the alignment-v3 kinematic verifier or its v4 equivalent;
- rendered multi-angle/era evidence using `scripts/render-appearance-v1.py` or an updated renderer;
- browser/WebGL integration and fallback behavior in the exhibit.

Runtime staging is a separate step. `scripts/select-appearance-runtime.py --iteration <label>` requires passing bound technical receipts, era-specific three-quarter Blender stills, and an `art-review.json` explicitly marked `candidate-for-local-review` for the exact raw GLB hash. Staging writes a candidate inventory that still records owner acceptance as pending. Staging does not change application selectors or publish files.

The iteration audit under `assets/audit/appearance-v1/` is proposal evidence only. Iterations 01–06 and 08 are rework; iteration 07 is a preserved intermediate browser checkpoint; iteration 09 is selected in the local runtime with a passing browser receipt and remaining artistic gaps. Passing technical checks, generating renders, or staging a local candidate does not constitute artistic approval, owner acceptance, release readiness, publication, or a claim that the model is finished.
