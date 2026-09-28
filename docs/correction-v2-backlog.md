# Correction v2 — accountable backlog

> Current continuation: the sixth v6 head/neck candidate and exact-model evidence are summarized in [alignment-v6-review.md](alignment-v6-review.md). The original v2 rows below remain a stage-history record; the continuation table at the end records later progress.

The frozen inspector assessed `4b1c726f5d9bbd1ba1048f89049a5b422001c506`, model `3ec668b0…baacdc5`. Its scores remain historical. This work starts from that commit on `codex/neutral-correction-v2`; the public release is not replaced. Source/reference ownership is in the [integration contract](correction-v2-integration-contract.md) and [feature packet](correction-v2-reference-packet.md). The current neutral model and generated parts/pivots are recorded in [its inventory](../assets/models/uncaged-neutral-v2/neutral-inventory.json).

No finding below is closed solely by implementation or an automated pass. The [neutral review](../assets/audit/neutral-v2/neutral-review.html) carries visible evidence. Stage B is a review gate before dependent surface finishing.

| ID / priority | Criteria / era / region | Baseline evidence and controlling source | Correction and owner / files | Dependencies and required retest | Current disposition |
|---|---|---|---|---|---|
| F01 P0 | V01 V02 V05 C01; all; breast/neck/silhouette | Inspector comparisons; candidate 03 common body, era stills | Supervisor: shaped taper, fuller bowed neck, integrated shoulder envelope; `scripts/build-uncaged-neutral-v2.py`, new native/export | Neutral bilateral/front/rear/three-quarter, matched perspective, dips/strike/return and owner review | Implemented neutral proposal; identity review OPEN |
| F02 P0 | V03 V04 V05; all; skull/bill/optic | Inspector head captures; July head only + candidate 03 | Supervisor: explicit convex hook/cutting edge, separate mandible, layered crown and optic aperture | Close views both sides, jaw open/closed, gaze/down, motion; no assumed approval from contact solve | Partial improvement; crown/cheek detail remains OPEN |
| F03 P0 | V06 C01 C03 C04; all; folded mantle | Inspector shoulder/rear captures; candidate 03 + flightless direction | Supervisor: broad wrap over actual shoulder/elbow, two rigid owners, compact lower contour | Folded/guard/thrust bilateral; left restriction; inspected moving overlap | Implemented neutral proposal; clearance/likeness OPEN |
| F04 P1 | V07 C04; all; legs/feet | Inspector foot captures; candidate 03/Maker/Mechanic | Supervisor: shorter leg span, hollow channel guards, varied toe lengths and hooked talons; independent digit pivots | Planted/step/turn/jump/landing, claw contact later; source support comparison | Partial improvement; fine joint/digit construction OPEN |
| F05 P1 | V08 C01 C03; all; regional plates | Inspector breast captures and selected stills | Supervisor; provisional rigid breast/neck/mantle/crown courses already define neutral envelope | Depends on owner Stage B review; density/edge/overlap hierarchy must be refined regionally | GATED: no finished exterior acceptance |
| F06 P1 | V09 C09; all; material history | Inspector neutral exhibit/material critique; era images | Supervisor; deliberately neutral solid PBR, no replacement atlas/noise or wear pass | Depends on corrected geometry; regional geometry-aware wear, three-era neutral/exhibit close-ups | GATED / NOT IMPLEMENTED |
| F07 P1 | B07 C03 C04; Advanced; claw | Inspector T09 absence; owner claw request | Supervisor; twelve independent proximal/distal digit nodes supplied; action still required | Limb/pivot agreement; actual target/support/recovery, normal/slow and interruptions | OPEN: separate toes are preparation, not a completed claw action |
| F08 P1 | B05 B08; Advanced; waiting persona | Frozen two 120s runs and repeated six-loop rhythm | Luna tooling worker; `src/scene/presence-state.js`, tests: authored varied intentions/routes/families/recovery | Stable controller integration; two new synchronized uncut 120s runs, event counts/intervals and human acting review | Controller integrated and unit-tested; existing shared cage-press choreography still limits visible action variety. Two fresh 120s runs and human acting review pending; OPEN |
| F09 P2 | I04 A02; Mechanic/Advanced (+Maker regression); inspection labels | Frozen open/exploded captures | Luna tooling worker + supervisor integration; `marker-layout.js`, `main.js`, `presence-exhibit.js`, `style.css` | Real browser all eras, 0/50/100%, default/orbit, 1440/390, keyboard/focus; human access remains separate | Corrected and visually checked; targeted retest passes 36 visible nonoverlapping desktop/narrow layouts and six keyboard checks. This supersedes the first narrow test that incorrectly accepted CSS-hidden, zero-size labels. |
| F10 P2 | D05 D02; global; stale validator | Historical `verify-exterior-assets.py` fixed 28-count/receipt write | Luna tooling worker; retired old entrypoint; explicit active source hashes + dynamic release inventory; `publication-boundary.mjs`, fixture/tests, current docs | Build current candidate, actual source/export hashes, safe unexpected-output negative fixture; preserve historical receipt | Targeted tests pass; current build/publication boundary passes locally; historical receipts unchanged |

## Gate and coverage rules

F01–F04 implementation does not make any era a visual twin. Each era requires its own likeness decision. F05/F06 remain dependent on the requested neutral review. V10's chronology and Maker/Mechanic V12 scope remain owner decisions in the packet. F07's named action and F08's recordings cannot be inferred from the new mesh or unit tests.

The PRD T01–T18 definitions and proposed 50/18/12/8/6/6 weights remain unchanged. No new full index is claimed during Stage B. Physical mobile/thermal, human screen reader, audible listening/loop review and continuous human acting acceptance remain unavailable/not performed here. A local built preview is not CI, live deployment or owner acceptance.

## V6 continuation — local neutral candidate

Model SHA-256 `ce35024adda89681a0f37e7018e2563a74af67cd06558a887222df87b78a87fe`; [current gallery](../assets/audit/alignment-v6/index.html). Original priorities, PRD criteria, reference scopes and acceptance policy remain unchanged. This table supersedes only stale progress statements, not the frozen inspector results.

| Finding | Current disposition | Evidence and remaining requirement |
|---|---|---|
| F01 | OPEN | V5 body retained; v6 adds a local jaw-clearance pocket while retaining the neck support and posterior contour. Neck layer hierarchy and whole-body likeness still need review. |
| F02 | OPEN | Larger seated primary optic, lowered fixed cheek and deeper mandible; sampled jaw/head, jaw/neck and optic crossings clear. Crown sweep experiments were rejected and the v5 roof restored. No defining-feature likeness pass. |
| F03 | OPEN | V5 mantle retained, with bounded v6 thrust and restricted-left travel evidence. Full reference-supported coverage and bilateral appearance remain review items. |
| F04 | OPEN | Inherited limbs remain selected; separate regional guard/talon work is not integrated or credited to v6. |
| F05 | GATED | Neutral regional covering exists; final hierarchy, overlap and edge refinement depend on structural review. |
| F06 | GATED | No material integration in this candidate. Separate surface experiments remain proposals. |
| F07 | IMPLEMENTED, bounded retest | Named articulated claw scrape is recorded on this model with contact and recovery; tests and telemetry do not certify force, complete collision freedom or artistic acceptance. |
| F08 | IMPLEMENTED, artistic review OPEN | Two fresh uncut 120-second no-input recordings and synchronized analysis are present. Alternate seed is an explicit development probe; continuous human acting acceptance remains outstanding. |
| F09 | PRIOR scoped evidence retained | Existing label/layout corrections unchanged. V6 captures cover open/exploded/reassembled states, not a new complete accessibility/device matrix. |
| F10 | TARGETED CHECKS PASS | Local build inventory/hash boundary and the isolated unexpected-output negative fixture pass. No fixed permanent output count replaces the retired assumption. No remote publication claimed. |

See the current review for versioned model/source identities, rejected iterations, finite test scopes, browser footage, and remaining owner decisions. No new per-era score or full acceptance index is asserted.
