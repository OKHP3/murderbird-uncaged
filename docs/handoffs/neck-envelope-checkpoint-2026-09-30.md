# Neck envelope checkpoint — 2026-09-30

**Both attempts are frozen and held. No candidate is construction-approved or selected for production.** Study01 modestly covers the exposed shaft but makes a stronger stiff cuff and fails every sampled pose. Final study02 uses varied tapered upper ends and preserves the lower neck, but adds one strict rear-course crossing in the Maker pose. No third attempt or hidden repair was made. Root owns visual selection, runtime review and integration.

## Authority, input and scope

Clean new checkout `/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged` was fetched and verified at exact GitHub `0726e99b4c6728a73b320346eae7f7d0f8e0f90b`, then switched to `codex/v38-neck-envelope-01`. Actual master03 and selected Mechanic binaries were viewed; they control the compact, strong curved mechanical neck joining head to deep breast. July remains head-only. No July body/wing cues, historical held V18/V19 geometry, hanging strips or breast-lip recession were imported.

Both studies independently start from crown-fit02 native SHA256 `11af51be40c3a725daaeb4c7697640e3bb388d575733f1d620f630e172149137`, matching GLB `7b5efb08d497035f98153a14143b41470e7c4234c60dcacf341916aea18d94ea`. Only those tracked LFS binaries were hydrated from hash-verified root files; their working-tree entries remain unstaged/excluded. Historical/old worker trees are untouched.

Actual baseline `neck-inventory.json` records62 neck meshes, evaluated bounds, modifiers, materials and the unchanged four-course chain. Native pivot origins in metres are neck `(0,-.188,1.215)`, mid-a `(0,-.229,1.2735)`, mid-b `(0,-.270,1.3281)`, upper `(0,-.321,1.3827)` and head `(0,-.3226,1.423884)`. Source top guard bounds reach aboutZ1.46, leaving a visible shaft below the skull. These are actual model measurements, not dimensions inferred from illustrations.

Study01 explicitly changes40 existing `V23 cervical {1..4} directional guard {1..10}` meshes. It broadens the curved envelope and raises the upper course;1173 other objects have exact snapshots. Its upper course reads as a flat raised cuff in author/root review. Its zero root deformation field is an authored fade; exact unchanged vertex-bit preservation inside those40 changed meshes is not asserted. All unrelated geometry, matrices and materials remain exact.

Study02 starts again from original crown-fit02. Its only geometry allowlist is ten existing `V23 cervical 4 directional guard {1..10}` meshes; original lower three courses and1203 other objects remain exact. Each replaces its complete upper-guard mesh with the original399-vertex outer grid connectivity,399 paired inner vertices and explicit edge walls. Tapered tips retain72% of the source end width, have diagonal/sloped boundaries and varied short extensions. Actual authored outer displacement is at most36.090122mm. This is a finite reconstruction proposal, not a measured fabrication design or a compliant skin.

All studies preserve exact pivots, owner matrices, head/bill/contact extrema, jaw, crown/cheek/optic seat, cervical load links/bearings, breast aperture/root receiving structure, shoulders/wings, body/legs/feet, repair landmark and era gates. No attachment incompatibility was demonstrated and no pivot was changed. No objects were added/deleted, and no guide or soft body was introduced.

## Final construction and era map

All ten study02 objects remain separate rigid parts on `cervical-upper`, which stays under `cervical-mid-b`; they do not bridge to head or breast. Their roles remain `plate` / `inherited-passive`, material `V38 contrast / plate`, eligibility maker/mechanic/builder. Source standardPBR records and eraFinishes profiles remain exact; no new power, sensing or earlier-era optic illumination is introduced.

| Existing upper guard | Authored tip extension | Finite paired stock | Owner / era role |
|---|---:|---:|---|
| 1 |25mm|3.5mm|cervical-upper; inherited passive, all3eras|
| 2 |35mm|3.5mm|same|
| 3 |26mm|3.5mm|same|
| 4 |33mm|3.5mm|same|
| 5 |23mm|3.5mm|same|
| 6 |16mm|3.5mm|same|
| 7 |12mm|3.5mm|same|
| 8 |8mm|3.5mm|same|
| 9 |18mm|3.5mm|same|
| 10 |5mm|3.5mm|same|

Paired outer/inner section distances are3.5mm within2e-7m; closed edge-manifold topology and positive volume passed. The plates are finite rigid geometry, with no stretch. Paired-stock checks do not establish normal manufacturing thickness, tolerances, loads or engineering suitability. Exact before/after mesh signatures and full attachment/era records are in each receipt.

## Checks and visible evidence

PASS: native finite topology/positive volume, native save/reopen snapshots, undeclared-object/material preservation, exported node names and rigid parents, exact source standardPBR/eraFinishes records. Actual GLTFLoader→applyEraFinishes passed40 modified guards for01 and ten for02 across all3eras, preserving visibility and actual shared profile references.

FAIL: unchanged `scripts/validate-neck-guard-envelope.py` actual evaluated triangle edge-through-face screen, using1e-7m plane epsilon and1e-6 barycentric/edge margins, seven declared rigid poses. It includes40 guard meshes versus adjacent owners; same-owner contacts are excluded. It is not continuous-sweep, containment, tolerance or full collision certification.

| Pose | Original baseline | Study01 | Study02 |
|---|---:|---:|---:|
| Rest |0|4|0|
| Maker neck/jaw |0|8|1|
| Attention |0|4|0|
| Contact neck |0|7|0|
| Thrust neck |0|4|0|
| Yaw minus |0|5|0|
| Yaw plus |0|6|0|

Study01 persistent crossings hit exact V33 throat-cheek plates from upper rear guard10; other pose failures reach adjacent posterior guards, scapular receiving plates and breast guards. Study02 eliminates those observed interfaces but adds the exact Maker witness `V23 cervical 3 directional guard 10` versus modified `V23 cervical 4 directional guard 10`. That lower guard is protected baseline geometry. Full triangle witnesses are frozen in each candidate screen; the original seven-pose zero result is retained. No aggregate PASS conceals this residual.

Both studies have matched1200×1200 whole-bird three-quarter/profile and neck profile/three-quarter/front neutral views. Study02 also has read-only matched whole-bird rear and neck rear supplements, plus rest/Maker/contact authored native pose glances from the checker. Those glances are not captured browser playback. Broader whole-bird likeness gain remains modest and owner acceptance is open.

NOT RUN here: runtime/app changes, actual browser contact/Maker/inspection, illustrated fallback, full build/publication boundary, full tests, CI/deployment or owner acceptance. Root performs its own actual runtime/build evidence separately. No commit or push was performed in this worker.

## Frozen models and reproduction

Study01 native `assets/models/whole-character-v38/neck-study01/murderbird-v38-neck-study01.blend`: SHA256 `7c70a00bb287ab528bd7b483880894dfcd383a6606872d314daf0fec40d5485e`.

Study01 rigid GLB `murderbird-v38-neck-study01-rigid.glb`: SHA256 `baf4d01fff7ad152edd5d021f24f491ca2457d7f1195d5524e77d58b46f94479`.

Study02 native `assets/models/whole-character-v38/neck-study02/murderbird-v38-neck-study02.blend`: SHA256 `f3482b83014f420fcfbfe5ddab89282d5dc397952a2c36c6e932c572885fc4e1`.

Study02 rigid GLB `murderbird-v38-neck-study02-rigid.glb`: SHA256 `c11eb6aa2372d5581c5f15df95ad4cc64ebcd73fd5611370212ca47f9671e744`.

Study01 recursive freeze-manifest has23 entries, SHA256 `abf70b7ee85c1457643596dd793e5eb598c540c80a17c970f524be02821f9da8`. Study02 has30 entries, SHA256 `32064687abb5b3b0b54a4c94be09a23e0fe62ace88d475998e97f0e51de2e63a`. Both include native/GLB, images, checks, executed source copies and receipts; they exclude themselves and this handoff. All53 entries were verified after freeze. Both model/audit sets are write-once, including the failed01 evidence.

Current top-level source recipe builds02 from original crown-fit02. Fresh reproduction from repository root with actual pinned inputs and no existing output directories: `/Applications/Blender.app/Contents/MacOS/Blender -b --python scripts/build-v38-neck-envelope.py`. It refuses existing native/GLB/receipt/candidate files. Initial inventory mode (`-- --inventory-only`) is optional; its explicitly preserved baseline can precede one candidate build. No native models or media are overwritten. For01 reproduction, copy01 frozen executed-builder.py/executed-region.py back to their original two script locations in a fresh checkout. Executed audit copies derive ROOT from the original recipe location and are not directly runnable from the audit directory.

Reference reads use the machine-specific canonical root `/Volumes/OKH-Local/04_GitHub_Mirrors/murderbird-uncaged`; exact actual paths/hashes are recorded in receipt.inputs.viewedReferences. The checker arguments are `--model NATIVE --sha SHA --output NEWDIR` (optional `--render`). The read-only rear supplement arguments are baseline native, candidate native and audit directory; it refuses existing media. Actual parser check arguments are GLB, era-finish.js, existing Three.js directory and new JSON output; it used root checkout dependencies without installation.

Owned paths: the two new neck recipe files, new model/audit neck-study01 and neck-study02 trees, and this handoff. The two tracked crown-fit02 input hydration entries stay excluded. Final status is HELD for one Maker interface and incomplete visible reconciliation. Root decides checkpoint integration; no further modeling is authorized here.
