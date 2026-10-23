# Appearance production review

This local production record summarizes appearance iterations 01–09 on branch `codex/appearance-production`. Iteration 09 is selected by the local application as a candidate pending owner acceptance. Its local build and publication boundary checks pass; local browser review was completed, with the formal browser receipt linked below. This is not an owner acceptance record, a reference-parity claim, or a deployment decision.

The initial [appearance fidelity assessment](appearance-fidelity-assessment-2026-09-27.md) and its visual/video evidence are preserved here byte-for-byte from the canonical main clone. Its September 27 inspection identifies the public gallery and source checkpoint observed then; it is historical evidence rather than a claim about a later deployment.

The [local comparison workshop](http://localhost:5187/assets/audit/appearance-v1/index.html) includes era/view comparisons, the geometry turntable, exact GLB downloads, and browser evidence. The [interactive candidate](http://localhost:5187/?review=appearance) runs from this worktree. To reopen after the development server stops, run `npm run dev -- --host 127.0.0.1 --port 5187` here. The public `/review/` remains the earlier published gallery. The [delivery validation](../assets/audit/appearance-v1/iteration-09/delivery-validation.json) records final local checks and limitations. All production iterations and native files remain preserved locally; this work is uncommitted and unpublished.

## Iteration decisions

| Iteration | Review evidence | Decision and concrete findings |
| --- | --- | --- |
| 01 | [art-review.json](../assets/audit/appearance-v1/iteration-01/art-review.json) | `rework`. Flat oversized plates, excessive clean gold, a flat optic, and crown/cheek/neck overlays that collide or disappear under other surfaces. Do not adopt as final exterior. |
| 02 | [art-review.json](../assets/audit/appearance-v1/iteration-02/art-review.json) | `rework`. Temporal plates occlude the optic; crown gap and coplanar caps create voids/artifacts; legs and plates remain too soft and uniform. Do not adopt as final exterior. |
| 03 | [art-review.json](../assets/audit/appearance-v1/iteration-03/art-review.json) | `rework`. The 84 sampled optic rays are clear, but cheek seating is weak; crown creases, intersections, and detached edges remain; roughness/metallic variation clouds bill and cheek; likeness remains below selected references. |
| 04 | [art-review.json](../assets/audit/appearance-v1/iteration-04/art-review.json) | `rework`. Crown continuity, optic backing, finish control, and body coverage improve. Crown caps still read as a helmet; a rear neck slot exposes frame; the optic reads as a gold coin; breast and wing courses are too alike. |
| 05 | [art-review.json](../assets/audit/appearance-v1/iteration-05/art-review.json) | `rework`. Lower breast scales `7 0–4` produced Solidify spikes, with the largest radius reported above 116 km. The prior finite-coordinate check was inadequate. The review explicitly says never select this candidate and calls for a 4 m coordinate guard plus bounded plate projection. |
| 06 | [art-review.json](../assets/audit/appearance-v1/iteration-06/art-review.json) | `rework`; not selected for runtime. The spike and coordinate guard are reported corrected, and front/three-quarter crown, iris, and neck casing are coherent. Rear dorsal laps remain faceted; inner trailing wings are plain; rear neck/skull strips remain exposed. |
| 07 | [art-review.json](../assets/audit/appearance-v1/iteration-07/art-review.json) and [browser checkpoint](../assets/audit/appearance-v1/iteration-07/browser/browser-checkpoint.json) | Historical `candidate-for-local-review`, superseded by later work. Actual desktop IAB WebGL exposed overly gold Maker finish, regular-looking crown courses, and missing visible fabrication hardware, prompting follow-on detail work. The checkpoint recorded local separation/reassembly, not reference likeness or mobile performance. |
| 08 | [art-review.json](../assets/audit/appearance-v1/iteration-08/art-review.json) | `rework`. Lower fasteners, seams, darker Maker finish, recessed optic and staggered crown improve construction. Broad panels/form remain simpler than references; finish looks uniform at normal scale; name-based material routing gives bill fixings/ports/edge details the bill material; fasteners may read as dotted trim; frozen v3 contours/proportions still need structural reconciliation. |
| 09 | [art-review.json](../assets/audit/appearance-v1/iteration-09/art-review.json) | `candidate-for-local-review` for the exact raw GLB hash. The review reports improved era finish and metadata-first bill hardware roles, no new major clipping in reviewed head/three-quarter views, and unchanged iteration-08 geometry/hierarchy. Still below exact illustrative likeness: broad head/cheek surfaces, large jaw-to-neck pocket, regular crown/torso courses, warm bill seams, repeated tiny fasteners, sharp plate transitions, and unresolved frozen-v3 proportions. Owner acceptance remains pending. |

The review files do not request or infer owner acceptance. Technical checks such as export validation, ray visibility, or kinematic samples establish only their stated properties; they do not override rework decisions or prove reference likeness.

## Geometry and surface ownership

The appearance sequence authors against frozen alignment-v3 source [murderbird-alignment-v3.blend](../assets/models/uncaged-alignment-v3/murderbird-alignment-v3.blend), SHA-256 `6de7c16728ac2ac4926b9b0bd608d7eb5e03f702d3e1ef222db997c84fd7ff3a`; the paired runtime GLB is `c4dc308f77399410368b82443a1b21b9113cfedb258aa055906b4f13c92dda21`. The appearance builder records structural baseline revision `3e6d340e616e79708d2a62ec9255fd997d14ea4f`. The v3 [alignment inventory](../assets/models/uncaged-alignment-v3/alignment-inventory.json) is the interface source: 51 pivot records with parent, local/world position and scale, plus controls, limits, bill-contact landmark, and joint contract. Its jaw contract specifies positive-X opening downward; local coordinates are not presumed equal to v2.

Five local modules are composed by `scripts/build-uncaged-appearance-v1.py`:

- `scripts/appearance-head-neck.py` authors crown, cheek/orbital, bill-adjacent exterior, and cervical plates onto the existing head, cranial-cover, and neck owners. The bill contact surface, internal descendants, and pivots stay intact.
- `scripts/appearance-body-detail.py` shapes breast/body, shoulder/mantle and wing transitions, bearing surrounds, and selected ankle/toe-root surface details on their existing owners.
- `scripts/appearance-limb-casing.py` builds segmented fitted limb guards and foot/toe-root transitions around retained links, bearings, digit owners, and contact geometry.
- `scripts/appearance-bill-finish.py` seats authored ports, fixings, and joining lines onto the existing upper bill and mandible surfaces, retaining their owners and contact geometry.
- `scripts/appearance-materials.py` assigns role/era PBR materials and UVs without changing geometry, hierarchy, or era visibility. The current proposal uses three 1024² base-color atlases (Maker, Mechanic, Advanced), two roughness/metallic atlases, one shared tangent-normal atlas, and three Advanced head-hero maps. Topology-derived `COLOR_0` tints supply restrained edge wear. Occlusion red is constant 1; there is no AO bake or assembly-cavity bake. These are authored procedural materials, not scans or measured alloy/corrosion data.

All added surfaces follow the existing rigid owners and era tags. Preserve all 51 baseline pivot parent/local transforms, all twelve independently owned digit hinges, bill/foot/toe contact surfaces, motion systems, original source pieces, and the identifiable anatomical-left repair landmark. Appearance must fit around the functional structure rather than move it to hide surface conflicts.

## Parallel geometry handoff

The structural-geometry thread remains independently owned; this note makes no claim about its latest checkpoint or acceptance. Before a future integration, select and freeze a verified structural checkpoint with exact revision, native/GLB hashes, owner and pivot inventory, and passing export, kinematic, and browser evidence. Leave its worktree and checkpoint untouched. Start a new appearance iteration from a copy in this worktree; compare owner names, transforms, clearances, region boundaries, and era tags before porting surfaces. Apply `appearance-materials.py` only after checking its role/era map against that checkpoint. Do not blindly overlay crown/head/neck surfaces or rebuild structural casing where improved geometry already exists. Keep all v3-based appearance iterations preserved as provenance.

The current guide is [appearance-integration-contract.md](appearance-integration-contract.md). A future retargeted candidate still needs its own asset/geometry guard, optic, kinematic, render, and browser evidence. Neither a verified frame nor a passing code check supplies owner artistic acceptance.

## Historical browser checkpoint — iteration 07

Iteration 07 remains preserved under its model, audit, and runtime-inventory paths. Its [art review](../assets/audit/appearance-v1/iteration-07/art-review.json) was `candidate-for-local-review`, not owner acceptance, and did not claim exact reference parity. Its [browser checkpoint](../assets/audit/appearance-v1/iteration-07/browser/browser-checkpoint.json) bound the packed model and recorded a local CUA/IAB WebGL session on ANGLE Metal / Apple M4 Max at 856×648; separation, inspection-open, and reassembly were observed. Recorded desktop frame data is hardware-specific and is not a mobile performance claim. Visual follow-up on that checkpoint identified too-gold Maker finish, overly regular crown, and missing visible fasteners; iteration 08 proceeded to address the gaps. This checkpoint is historical and superseded by later appearance work, not a current-runtime or publication claim.

## Iteration 08 — verified technical receipts, art rework

The exact identities in [appearance inventory](../assets/models/uncaged-appearance-v1/iterations/iteration-08/appearance-inventory.json) are:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Native Blender source | 18,725,370 | `ea6c9a235106810e8056401467a13863fdbb0a215589375321101d5894b53c33` |
| Raw GLB | 61,031,756 | `85549ff0b1bc20b4f0208f5239b66e09639bba83ae52559a1d4bb38631c3e162` |
| Packed GLB | 32,321,628 | `0165e98c3359f4e88ad049c035848ab74cc5cfa5db2bb87481b0412491e37499` |

[Asset validation](../assets/audit/appearance-v1/iteration-08/asset-validation.json) passed with 423 meshes, 427 primitives, 979,112 triangles, 40 materials, 120 textures and 9 images. Its position guard checked 427 accessors / 841,079 values; maximum absolute component was 0.6200000047683716 m against 4 m. All 37 required rigid owners retained parent/local transforms, including all 12 digit hinges. [Optic visibility](../assets/audit/appearance-v1/iteration-08/optic-visibility.json) passed 84/84 rays, and [kinematic alignment](../assets/audit/appearance-v1/iteration-08/kinematic-alignment.json) passed 4/4 checks. The [packing receipt](../assets/audit/appearance-v1/iteration-08/packing.json) verifies byte-exact buffer-view slices and unchanged semantic JSON, and records 28,709,996 bytes saved.

These technical passes do not change the `rework` decision in [art-review.json](../assets/audit/appearance-v1/iteration-08/art-review.json). It records better fabrication detail, a darker Maker surface, recessed optic, and varied crown stagger; it still identifies overly simple broad form, near-uniform finish, metadata-routing errors on bill fixings/ports/edges, fasteners that can read as dotted trim, and unresolved frozen-v3 jaw/bill and neck/shoulder proportions. No iteration-08 runtime inventory or browser-review receipt is recorded here. Owner acceptance remains pending and not inferred.

## Iteration 09 — technical checks passed, local browser review complete

Iteration 09 was generated by `scripts/refinish-appearance-iteration.py` from iteration 08. It replaces nine packed image maps and reapplies hardware material roles from metadata. The recorded geometry/hierarchy digest is identical before and after (`cffe167c0fc6d74f9c0f21ca947c96455cbf2eecb7a56637eefc56399b53bff5`); the source inventory records `geometryAndHierarchyUnchanged: true`.

The [appearance inventory](../assets/models/uncaged-appearance-v1/iterations/iteration-09/appearance-inventory.json) and [asset validation](../assets/audit/appearance-v1/iteration-09/asset-validation.json) bind these files:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Native Blender source | 19,097,642 | `5f56c9dec0bc0deb26e42235ece063f62184a80b8721ce07669f6c0d11b03ae7` |
| Raw GLB | 61,021,248 | `bace5c9cbce078ba636f7fa87be2b7fcafe57d2f47a3cc8f265646e87adcbe89` |
| Packed GLB | 32,319,544 | `157c91ca39bb893a74a003ebc15fdc4710bc686eb16437144f41ae83f2ee708f` |

Asset validation passed: 423 meshes, 427 primitives, 979,112 triangles, 46 materials, 138 textures, 9 embedded images, 37 rigid owners with unchanged parent/local transforms, and all 12 digit hinges. Its position guard checked 427 accessors and 840,845 values; maximum absolute component was 0.6200000047683716 m against the 4 m limit. [Optic visibility](../assets/audit/appearance-v1/iteration-09/optic-visibility.json) passed all 84 samples. [Kinematic alignment](../assets/audit/appearance-v1/iteration-09/kinematic-alignment.json) passed 4/4 checks. The [packing receipt](../assets/audit/appearance-v1/iteration-09/packing.json) proves buffer-view slices byte-exact and semantic JSON unchanged, with 28,701,572 bytes saved. [Authoring views](../assets/audit/appearance-v1/iteration-09/authoring-views.json) records 10 Cycles/GPU views at 48 samples.

The [runtime inventory](../assets/models/uncaged-appearance-v1/runtime/iteration-09/runtime-inventory.json) records this as a candidate pending owner acceptance. `src/scene/presence-exhibit.js` selects its packed GLB; the fallback selects one iteration-09 still per era. The local headed-browser review confirmed real WebGL in all three eras, separation/reassembly behavior, and illustrated fallback behavior. The [browser-validation receipt](../assets/audit/appearance-v1/iteration-09/browser/browser-validation.json) binds the exact raw and packed GLB hashes and six diagnostic/image pairs. The reassembled desktop observation recorded 100 fps median on Apple M4 Max at a 856×648 canvas, DPR 1. A 390×844 illustrated-fallback check showed no horizontal overflow and a clearly labeled assembly diagram; mobile WebGL and physical-device performance were not tested. Both local exhibit tabs reported no console warnings or errors. This evidence is local to this worktree and is not deployment or owner art acceptance.

The local test run passed 44/44 tests. `npm run build` and the publication gate passed: the built `dist/` contains 134 files and 16 exact pinned runtime/folio assets; the DEV-only appearance review helper is absent from the build. These facts are recorded in `.local/publication/build-validation.json` and `scripts/verify-publication.mjs`. The local publication gate does not indicate that anything was deployed.

The Builder turntable is complete: [turntable metadata](../assets/audit/appearance-v1/iteration-09/turntable-builder/turntable-metadata.json) records 96 Cycles/GPU frames at 1080×1080 and 24 fps; the encoded movie is 4 seconds. This remains visual evidence, not acceptance. Iteration 09's [art review](../assets/audit/appearance-v1/iteration-09/art-review.json) says the candidate remains below exact illustrative-reference likeness and explicitly implies no publication or owner art acceptance. Structural-v4 reconciliation remains a separate integration gate.

All MurderBird creative material remains rights reserved under `NOTICE.md`. This record establishes no model acceptance, release approval, or publication.
