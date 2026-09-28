# MurderBird alignment v5 — local candidate review

**Local neutral-geometry candidate; owner review remains pending; declared asset checks pass.** This is not approved, deployed, or a final likeness. Current runtime model: [GLB](../assets/models/uncaged-alignment-v5/murderbird-alignment-v5.glb), SHA-256 `1e7febcc03d9f8d1a644580c8422b124403cf4e5768aa01df747e3d9b6af9f1e` (4,385,348 bytes). Editable native file: [BLEND](../assets/models/uncaged-alignment-v5/murderbird-alignment-v5.blend), SHA-256 `fd5c8a21e8e7808fa94c9baa3499574bac3d0c1ed5a44573637286c359cea0e4` (2,094,769 bytes). Both match [the inventory](../assets/models/uncaged-alignment-v5/alignment-inventory.json) and the image manifest.

The preserved v3 source and v4 geometry are the construction base. V5 revises breast courses and shoulder/wing cover, reconstructs the lower-jaw hinge and fork, and reshapes the upper cervical guard pocket. Neutral colors, the separate Advanced processing parts and optics, and other rest pivots are inherited. The current authored set contains 703 editable mesh pieces and 462 profile curves; the GLB contains 231,704 triangles, 90 meshes, and 141 nodes.

## Regional construction and eligibility

| Region | V5 construction change | Rigid owner / era eligibility |
|---|---|---|
| Lower jaw | Reconstructed cheek-level hinge at Blender world `[0, -0.300, 1.704]`; forked mandible is built around the revised pivot. The earlier `[0, -0.345, 1.590]` hinge and its geometry were already jaw-owned. The earlier impression that this meant the jaw had the wrong owner was a mistaken visual diagnosis by the reviewer, not a change in ownership. | Jaw remains a separate rigid child of head; Maker, Mechanic, Builder. This is an authored interpretation, not measured source metrology. |
| Breast | Existing courses are lengthened and overlap adjusted to reduce bare gaps; original body silhouette envelope is retained. | Breastplate/body rigid ownership; inherited passive pieces eligible in all three eras. Advanced power-core parts remain Builder-only. |
| Shoulder / wing | Mantle coverts and distal guards are revised as staggered, narrower overlapping courses; upper mantle and lower wing shield remain separate rigid assemblies. | Left/right mantle and wing-shield owners; inherited passive pieces eligible in all three eras. Later repair brace remains Mechanic/Builder only. |
| Neck | Replaced cervical outer plates and forward inner guard profile with a rounded pocket between fixed stations; inherited load-bearing fork and bearings remain. | Neck owner; passive parts eligible in all three eras. |
| Head | Fixed v4 bill, skull and orbital construction otherwise retained around the reconstructed jaw. | Cranial/bill/jaw pieces remain separate rigid owners, all eras. The 24 processing parts and two optics are separate Advanced-system owners and Builder-only. |

Legs, feet, individual digit owners, remaining joints, neutral materials, and their era eligibility are inherited from v3/v4. No full surfaces, textures, measured dimensions, purposeful claw grip, or physical simulation are established by this candidate.

## Before and after

- **Jaw hinge and clearance:** the v4 jaw-head sweep passed. The first v5 attempt to raise the jaw hinge caused clearance failures against fixed cheek and processing meshes. The current cheek-level hinge and forked mandible revise the attachment placement while retaining the existing separate jaw rigid owner; ownership was never the defect. The source image constrains head identity only and supplies no hinge dimensions.
- **Jaw sweep:** the current diagnostic reports no proper triangle crossings over 33 sampled opening angles against fixed head-descendant meshes. See [jaw sweep receipt](../assets/audit/alignment-v5/rig-1e7febcc03d9/jaw-head-sweep/jaw-sweep.json). It does not prove continuous clearance, coplanar contact, containment, forces, or clearance against every moving part.
- **Neck / inner frame:** the former forward V-shaped guard and hidden inner guard crowded the reconstructed jaw. The current sixth-pose structural diagnostic reports no sampled crossings in 27 discrete jaw/pitch/yaw poses between selected neck plates/frames and the jaw. See [jaw/neck receipt](../assets/audit/alignment-v5/rig-1e7febcc03d9/jaw-neck-structure.json). Pair filtering and pose sampling limits are recorded in that receipt; this is not whole-body collision certification.
- **Mantle and breast:** earlier iterations showed a broad straight mantle stripe, an exposed recess/backing region between overlapping courses, and gaps between breast courses. These were surface-coverage readings, not a claim of a topological hole. V5 changes the course profiles and stagger/overlap to reduce those defects while keeping the established compact envelope. The matched neutral [mantle](../assets/audit/alignment-v5/alignment-mantle.png), [breast](../assets/audit/alignment-v5/alignment-breast.png), [side](../assets/audit/alignment-v5/alignment-side-right.png), and [three-quarter](../assets/audit/alignment-v5/alignment-three-quarter.png) views are bound to the current model and source hashes in [authoring-views.json](../assets/audit/alignment-v5/authoring-views.json). These are authoring renders, not artistic acceptance evidence.

The [asset-validation receipt](../assets/audit/alignment-v5/asset-validation-1e7febcc03d9.json) is passed for its declared checks and exact model hash. It records 703 native parts, 231,704 triangles, 90 exported meshes, and 141 nodes; it explicitly excludes artistic likeness and final-surface approval. The [six-validator run manifest](../assets/audit/alignment-v5/rig-1e7febcc03d9/run-manifest.json) records 59 passed assertions, jaw-head sweep at 0/33 crossing poses, expanded jaw/neck check at 0/27, and the exact model/source identities. The [five export-contract fixtures](../assets/audit/alignment-v5/export-contract-tests.log) passed. The [build-boundary receipt](../assets/audit/alignment-v5/build-boundary-1e7febcc03d9.json) passed with 133 emitted files and 16 exact approved runtime media assets. The [27 neutral authoring renders](../assets/audit/alignment-v5/authoring-views.json) are hash-bound to the GLB and native source. Bounded browser results are recorded below. Earlier generated candidates and receipts remain preserved under the matching [model iterations](../assets/models/uncaged-alignment-v5/iterations/) and [audit iterations](../assets/audit/alignment-v5/iterations/); their results do not transfer to the current model.

## Reference scope and remaining decisions

The [July owner-selected reference](../context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png) governs the head only. [Candidate 03](../assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png) guides the proposed shared neck/body direction. Both source hashes and declared scopes are recorded in the inventory. These perspective illustrations do not provide exact art metrology or establish hidden construction.

Remaining artistic decisions include further head refinement; lower-jaw rail and shell continuity; angular layering of the neck guards; and wing coverage. Legs and feet are inherited and still need likeness review. Full-surface construction remains future work. The Maker and Mechanic references describe era appearance; later repair geometry remains a proposal under the recorded chronology, not an owner-approved mechanism. Complete browser evaluation and owner acceptance remain outstanding; no remote CI or deployment is claimed here.

The app source in this QA checkout points at the v5 GLB and preview images. The production v4 worktree remains untouched; a local source URL is not a deployed release.

## Browser checkpoint

The [local gallery](../assets/audit/alignment-v5/index.html) collects the candidate comparisons and motion recordings. The live QA exhibit is `http://127.0.0.1:5183/`, based on commit `b6c0c17aed5873955f439edb573f6d2f1e6690e1` plus this local v5 change. The loaded browser GLB was fetched and hashed inside the page: its bytes match `1e7febcc03d9…`, rather than merely matching a filename. [Browser evidence and limits](../assets/audit/alignment-v5/browser-1e7febcc03d9/evidence-manifest.json) bind the captures, telemetry, scripts and recordings.

All five Maker controls were exercised separately. The Mechanic stepped and stopped at a cycle boundary. Advanced jump, thrust and bill contact were captured; all three eras opened, separated and returned to open/separation values of zero. Their current fallback images loaded after era transitions. No browser console errors were recorded. Static extrema used the existing development time-step hook to settle or reach poses; these are distinct from normal-speed evidence.

The silent [115-second canvas recording](../assets/audit/alignment-v5/browser-1e7febcc03d9/motion-normal-speed.mp4) uses the normal application clock and captures Maker controls, Mechanic motion, Advanced jump/thrust and inspection. Its fixed schedule attempted claw, reach and retreat while their controls were unavailable. Those failed dispatches remain in the receipt and are not passes. The separate [20-second claw recording](../assets/audit/alignment-v5/browser-1e7febcc03d9/claw-normal-speed.mp4) waits for the actual control and records approach, lift, contact, scrape, release and recovery. Both retain original WebM files and synchronized telemetry. Neither replaces complete interruption testing, two uncut autonomous runs, or continuous human acting review.

Observed conditions: Codex in-app browser using Apple M4 Max hardware through ANGLE Metal, 1280×720 viewport, 856×648 render buffer, DPR 1, loopback without network throttling. A short rolling sample reported 10 ms median / 11.2 ms p95 frame time, 316 draw calls and 468,124 rendered triangles including extra render passes. This is not sustained, thermal, physical-mobile, or constrained-network performance certification. Audio remained off. No new audio quality claim is made.

Rejected stale-paint/cropped captures, the premature inspection image and a clipped contact close-up remain identified in the manifest. They are excluded from the gallery's review evidence. The corrected centered contact view is separate. Reassembly state and the rigid-matrix tests establish bounded restoration; they do not prove continuous all-pair clearance.

## Finding state after this checkpoint

| Finding | Current assessment |
|---|---|
| F01 body/neck | Open. Upper-neck sweep clearance improved; angular guards and exposed transitions still need likeness work. |
| F02 head | Open. Reconstructed hinge clears sampled head/neck poses; rail-like mandible, broad orbital surround and bill construction remain weak. |
| F03 mantle | Open. Denser overlapping courses reduce straight gaps; exposed elbow/rear backing and full moving overlap remain unresolved. |
| F04 limbs/feet | Open. Existing digits/contact behavior preserved; parallel limb guard correction is not integrated into this model. |
| F05 regional plates | Open. Local breast/mantle changes are implemented; full regional hierarchy remains incomplete. |
| F06 materials | Gated. This is a neutral study; parallel appearance work is separate and not geometry approval. |
| F07 claw | Bounded technical evidence retained and current browser action recorded. Full support/visual/interruption acceptance remains open. |
| F08 acting | Existing revised acting retained. This demonstration is scripted; fresh v5 two-minute no-input runs and human judgment remain outstanding. |
| F09 labels | Era inspection views remain readable in sampled desktop views. Full orbit/narrow/keyboard coverage is not newly established here. |
| F10 release tooling | Current version-aware local boundary validator passes without replacing the historical count with another permanent count. No deployment claim. |

Maker, Mechanic and Advanced each remain **revision required** for likeness. No new aggregate score, complete PRD pass or owner acceptance is asserted. Surrounding circular head details in the reference are not automatically secondary sensors: roles beyond the principal optic remain uncertain, and earlier eras must not acquire Advanced sensing through shared geometry.

The integration audit found that the neutral Maker and Mechanic fallback PNGs are byte-identical in their current authored view. Their labels and controls correctly switch, but this is not evidence of visible era differentiation. The later repair and future materials must be made readable in the finished fallback. A preserved predecessor neck script remains alongside current generation snapshots and is explicitly excluded from the active recipe; it is not shipped in the website build.

The application's existing “Review evidence” navigation and the emitted `review/` package retain the previously published, explicitly frozen assessment. They are historical evidence, not the v5 gallery or a current score. Use the local v5 gallery linked above for this checkpoint. The boundary log also includes that older packet's separate verification; the current runtime model identity is in the v5 build-boundary JSON.
