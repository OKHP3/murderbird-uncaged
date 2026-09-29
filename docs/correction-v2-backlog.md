# Correction v2 — accountable backlog

> Current continuation: [V33 Form06](whole-character-v33-checkpoint.md) revises the orbital/cheek and crown construction and removes the sampled neck, crown and leaf self-crossings. The full bird still fails the owner likeness target. The next substantial correction is the breast-to-shoulder envelope and supporting stance; more small head detail is insufficient. DEV defaults to V32, with V33 available by explicit review route; production still selects V9. The V32 jaw/bill direction remains pending owner review. No finishing acceptance or publication. Earlier entries retain their historical scope.

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

## V8 and isolated correction continuation — September 28, 2026

The selected V8 runtime remains `c8c30cc46059…`, with native `b12c442e2f51…`. The paired bill/mandible candidate is native `7ba7c996fbcf…`, diagnostic GLB `ad7391eede50…`, locally preserved in commit `10372e2`; it is available in its separate WebGL head viewer. Optional two-stage neck runtime support is committed at `5209bd4`, but V8 still uses its original single neck joint. None of these local records establish a new deployment or an accepted visual twin.

| Finding | Current disposition | Latest bounded evidence and next requirement |
|---|---|---|
| F01 | OPEN | Two-stage neck maintains fixed attachments in the affected runtime checks. Attempt14 clears the intermediate joint in21 sampled poses but remains held for same-owner backing penetration, breast contacts and collar-like appearance. No replacement selected; resolve the exterior contour, drive mounting and breast access together. |
| F02 | OPEN; regional improvement | V8 incorporates continuous head V2. The isolated paired bill/mandible candidate deepens the formed blade and shortens the lower jaw, with unchanged hinge and outer contact profile.33 jaw samples,9 runtime jaw/neck samples,4 structural checks and independent native/export comparison pass. Its four root pins are buried inside the bill, not floating. The broader orbital saddle improves construction but its41-position opening sweep reveals plate crossings; held seam/ownership studies are linked in the [local gallery](../assets/audit/orbital-saddle-study-v4/index.html). |
| F03 | OPEN | V8 incorporates shoulder attempt02 and reseated pins, retaining compact shields and restricted anatomical-left motion. Normal-clock thrust and inspection are recorded; the shoulder still reads as a separate pod and needs a stronger body transition. |
| F04 | OPEN | V8 incorporates digit attempt03. Grounding and contact checks do not establish reference-level toe, ankle or exposed-drive construction; neutral limb appearance remains sparse. |
| F05 | GATED | Regional coverage is still provisional. Neck, breast and orbital seams require structural resolution before exterior finishing. |
| F06 | GATED | No new material-history integration. Maker and Mechanic neutral native views still fail to communicate sufficiently distinct visible repairs; shared geometry and occlusion must be resolved before a finish pass. |
| F07 | IMPLEMENTED; visual acceptance OPEN | V8's86.589-second actual-browser sequence includes claw action, contact and recovery, plus jump and thrust. This is a kinematic movement demonstration, not force simulation or exhaustive clearance. |
| F08 | IMPLEMENTED; whole encounter review OPEN | Earlier V6 two120-second recordings retain their exact historical scope. The V8 recording is shorter and does not replace a complete new no-input cage-cycle assessment. |
| F09 | PRIOR scoped evidence retained | V8 has static and recorded open/exploded/reassembled views. The optional two-stage neck's21-pose diagnostic reveals a proposed upper actuator crossing the access panel. Both a101-sample panel-only staged-slide proposal and a101-sample opposite-side-anchor proposal fail and are not integrated. These findings do not invalidate the separate historical label-layout checks or establish an inspection pass for new geometry. |
| F10 | TARGETED CHECKS PASS | Build at `10372e2` emitted134 files, with16 exact selected-model/folio/fallback assets. Experimental head/neck natives, diagnostic GLBs and audit trees were excluded. [Receipt](../assets/audit/paired-bill-mandible-study-v2/integration-build-v1/receipt.json). No remote CI or publication claimed. |

The whole-candidate neutral owner gate remains ahead of finishing and publication. V10 repair chronology and V12 historical movement scope remain the same owner decisions; no story wording or reference approval scope has been silently changed.

## V9 bounded integration

V9 adopts the verified bill derivative `f5c0f5ad99ac…` into the local whole-bird exhibit. Five mesh geometries and four fixing positions differ from V8; other 690 meshes and all 51 pivots remain unchanged. The seven affected checks, build and publication boundary pass. The gallery supplies 42 new neutral views and 18 matched comparisons; the actual browser response carries the same GLB hash.

F02 now includes the deeper bill, shorter mandible and reseated root fixings in the selected candidate. Its brow/optic fit and whole-head likeness remain OPEN. F01, F03 and F04 remain OPEN; separate neck and lower-leg workers are implementing bounded candidates. F05/F06 remain GATED on the whole-bird structural review. F07/F08 keep prior recording scope and require final-candidate encounter review. F09 retains earlier layout evidence plus bounded new inspection checks. F10 passes the current local boundary with version9 enabled; no new deployment is claimed. The [V9 review](alignment-v9-review.md) identifies exact files, checks and remaining decisions.


## V17 held checkpoint and V18 correction assignments

This checkpoint supersedes stale active-work statements above. It does not close the frozen inspector findings or replace their scores. V17 native is `7d371907b279eb3d625e67164d84a78b2901a5cb6a79917def07f48ff8792d7b`; GLB is `52980d9578d985737dfe7595515be494d9b1bcfa2dc17d960f18ac6f6fe6049e`. [Matched views, runtime and failed clearance](../assets/audit/whole-character-v17/index.html) establish the actual current discrepancy.

| Finding | Current disposition | Accountable next correction / verification |
| --- | --- | --- |
| F01 | OPEN; breast form improved, upper junction fails clearance | Breast/frame worker fits retained ribs and first-course armor to the rounded envelope. Supervisor compares full front/side/rear/reference views before integration; curved neck and body balance remain explicit visual criteria. |
| F02 | OPEN; eye surround improved, new fittings intersect crown | Orbital worker reseats/constructs the passive fittings and directly implicated crown surfaces. July controls head only. Supervisor reviews clustered machinery, cheek identity and moving cover clearance; a plain gray optic disk is not sufficient. |
| F03 | OPEN; compact shields and left restriction retained | No V18 wing shape change assigned. Recheck breast/shoulder fit and bilateral guard/thrust after regional composition; current wing seams are not accepted merely because they articulate. |
| F04 | OPEN; lower limbs remain sparse | Leg worker strengthens selective passive guarding, frame webs and ankle transition while retaining all toe/contact pivots. Supervisor compares stance and leg close-ups, then checks step/turn/jump and adjacent owner clearance. |
| F05 | PARTIAL / FINISH GATED | V17 has 78 tapered breast plates and separate head construction, but repeated cadence and sampled intersections remain. V18 fit repairs must retain purposeful supporting structure, thickness and inspection identity. |
| F06 | GATED / NOT INTEGRATED | All current V17/V18 construction proposals remain neutral. Three era-specific material history and finish acceptance have not been achieved. |
| F07 | IMPLEMENTED; candidate visual/contact acceptance OPEN | V17 exact-export claw checks pass 32/32 within their bounded kinematic scope. Geometry changes need affected retest; this does not replace reviewed normal/slow live articulated action. |
| F08 | IMPLEMENTED; final-candidate acting review OPEN | Earlier two 120-second recordings remain historical. V17 has normal-time jump/thrust evidence and a short watch/pace timing sample; neither constitutes the required new two-minute no-input review. |
| F09 | PRIOR LABEL EVIDENCE RETAINED; exterior inspection FAIL | V17 restores eligible mesh matrices, but strict samples reveal breast/body and head/crown intersections during inspection. No full inspection success is claimed for V17; V18 must address actual surfaces. |
| F10 | LOCAL TARGETED PASS | V17 build and dynamic publication boundary pass with 134 emitted files. The count is an observed result, not a new permanent assertion. V17 studies and natives remain outside distribution; no new remote release is claimed. |

V18 worker ownership is limited to the three new `scripts/regions/whole-character-v18-*.py` modules, their versioned regional model/audit directories and regional notes. Supervisor owns composition, application routing, integrated evidence and the whole-character decision. All 52 existing rigid node transforms, material definitions and historical guides are invariant in this specific fit pass; that compatibility constraint is not an approval of their visual proportions. If unchanged proportions still fail the reference after composition, continue structural correction before finishing.


## V18 combined checkpoint — assignments completed, acceptance open

The regional assignments above are complete for this checkpoint. [V18 attempt01](whole-character-v18-checkpoint.md) integrates orbital04, ring-preserving rib fit, neck reconstruction01 and leg06. Failed neck-lap drafts and reconstruction02 are excluded. Exact native/export and validation are in the checkpoint; no frozen score is revised.

- F01 remains OPEN: hanging cup reduced, but egg-like torso/collar and lower-neck contact fail. Next is a coherent deeper finite underlap, not another arbitrary clamp.
- F02 remains OPEN: fitted passive eye cluster improves and scoped crown collisions are removed. Bill, cheek and larger plate forms still miss the target.
- F03 remains OPEN: wings/left restriction are preserved, without new wing likeness acceptance.
- F04 remains OPEN: formed leg channels improve presence and clear the scoped moving neighbors; 32 fixed same-owner fits and sparse joints/feet remain.
- F05 remains PARTIAL and F06 GATED: no finished three-era exterior/material-history pass.
- F07/F08 retain bounded implementation evidence; final-candidate acting and owner review remain OPEN.
- F09 remains FAIL for exterior inspection: the opening shell crosses ribs despite correct matrix restoration. The old hinge lies inside the new shell planform and needs a structural correction with fresh samples.
- F10 has a fresh local build/boundary pass, with 134 emitted files, studies excluded and no new publication. This does not accept the artwork.

The changed work remains preserved in one worktree. The next integration must explicitly scope any necessary hinge/pivot change; retaining 52 pivots is not a permanent creative requirement.

## V22 checkpoint — September 29, 2026

This updates the current work state without changing historical receipts or inspector scores. See [V22 construction checkpoint](whole-character-v22-checkpoint.md) and the local comparison gallery at `http://127.0.0.1:5183/assets/audit/whole-character-v22/index.html`.

| Finding | Current evidence and disposition |
| --- | --- |
| F01 | OPEN. Frame04 changes torso/neck/leg proportions; Cassette06 restores neck coverage but has cuff-like joints, a lateral gap and moving surface crossings. Neither is an accepted foundation. |
| F02 | OPEN. Visible head geometry is retained during this scoped pass; the characteristic bill/head relationship still needs correction. |
| F03 | OPEN. Shoulder roots tuck inward in Frame04; the neck/breast/mantle envelope remains visually disconnected. Restricted left-side rig is preserved. |
| F04 | OPEN. Formed leg channels and tapered guards replace swollen rails. Feet and round bearings remain exact. No V22 dynamic support/landing claim. |
| F05/F06 | GATED. No finished regional surfacing or new era materials applied over unresolved geometry. |
| F07/F08 | Prior bounded implementation evidence retained. Thirteen targeted runtime regressions pass on retained V21 plus optional receiver fixtures. V22 has no browser derivative or final-candidate acting review. |
| F09 | Prior label evidence retained; V22 exterior inspection, separation and reassembly remain NOT VERIFIED. |
| F10 | Current local modified-tree build and dynamic publication boundary PASS. No V22 models/studies are in distribution. No remote CI/deployment claim. |

Likeness remains below target in all three eras. No new numeric visual score or owner acceptance is inferred from these checks.

## V23 coordinated form checkpoint

Form03 (`66b6ff8c…343e62`) implements a connected curved throat, tapered opening breast, four short neck links, rebuilt bill/mandible and arched inner mantle caps. A local GLB comparison now exists; V22 and every V23 attempt remain preserved. Independent visual review finds improvement, not acceptance. Mask-like face, weak shoulder-to-breast transition, repetitive breast plates, inherited limb gaps, new guard intersections and stale full-exhibit mechanism sockets remain open. See `docs/whole-character-v23-checkpoint.md` and `assets/audit/whole-character-v23/index.html`. Do not promote the local neck demonstration to full era behavior or publication evidence.

### V24 local checkpoint (2026-09-29)

V24 Form02 is an unaccepted construction proposal, continued from V23 Form03. It revises head/bill/jaw, breast plate sizes, and shoulder receivers/crown; a live-browser defect in two new head receivers was caught and corrected in a preserved second native/export. Exact native is `acb91013e0ca7cf98475e0d2ba6fb36d9c081c29c91b27e104bf7367d57f306d`; exact GLB is `940bccff25acbe37747ee8c462a59e8a63d4338482715e63740f27953aebc81b`. See `docs/whole-character-v24-checkpoint.md` and local `assets/audit/whole-character-v24/index.html`.

Independent visual verdict remains HOLD: head presence versus torso, sparse leg construction, repetitive plates, shoulder shelf and unresolved finite-wall neck crossings. Next begin with a coarse whole-body proportion/leg-construction correction, then pivot-centered neck terminal laps. Do not spend another pass on finish over this silhouette. Full new-model era hardware and movement integration remains unfinished. Nothing from this checkpoint was pushed or deployed.


### V25 local checkpoint (2026-09-29)

V25 Form01 enlarges the whole head coherently, tapers the lower breast and replaces sparse thigh/shin rails with paired formed structure. Native `b1b9cc88…8911f6`; GLB `45067ebb…0cf78a`. Independent visual verdict remains HOLD for chest form, facial construction, repetitive crown/plate hierarchy and unresolved neck coverage clearance. Experimental neck-lap changes are preserved and excluded after worsening contact-pose crossings.

The actual new-model controller diagnostic exposed off-center planted-foot slip; a bounded support-reach correction now passes the actual V25 journey and affected V9/V21 checks. Current diagnostic: nine passes, one partial (physical Maker tail not loaded). Full era machinery, continuous plate clearance and likeness remain open. [V25 checkpoint](whole-character-v25-checkpoint.md) separates the source/native/export, initial failures, corrections, browser demonstrations and remaining decisions. F01–F04 are OPEN; F05 partial/F06 gated; F07–F09 retain scoped evidence without final-candidate acceptance; F10 has the current local boundary pass. No new publication.

### V26 selected head checkpoint (2026-09-29)

V26 Form01 integrates only the shorter fuller bill, tucked jaw and provisional optic surround. The new planar crown and both neck experiments are rejected and preserved; original V25 crown/neck remain. A new jaw path interference was detected and repaired before integration. Five sampled poses retain only two inherited mandible/journal pair identities; their running fit and continuous clearance are unproven.

Native `f897b331…b65564`; GLB `5e9b9acd…a1b9d3`. Independent actual export parity and new-model motion diagnostic pass their bounded checks (nine passes, one partial for absent physical Maker tail). Browser recording, neutral views, inspection, fallback and stated-condition timing are preserved. [V26 checkpoint](whole-character-v26-checkpoint.md) records exact identities, selective integration and the remaining mask-like face/crown/neck/breast problems. F01–F04 remain OPEN, F05 partial/F06 gated, and artistic acceptance remains HOLD. No application model promotion or new publication.

### V27 curved cranial checkpoint (2026-09-29)

Form01 replaces planar crown fins with actual curved swept plates and separates fixed lateral receivers from the opening dorsal cap. A targeted forehead fit reduces the floating roof opening; small side gaps, smooth foreplate and plain optic facade remain. Local selected study only; owner likeness rejection still applies. Native `3014ae31…e66ceb`; GLB `971b28eb…74f63b`. Five scoped cap poses show zero strict pairs; this does not establish continuous clearance or art acceptance.

The three-guard sliding neck study is excluded after finite hardware and neighboring plate crossings. The lower-torso widening is excluded because its visual improvement is marginal. A wing-terminal taper is also excluded after introducing articulated liner/mantle crossings. All are preserved. [V27 checkpoint](whole-character-v27-checkpoint.md) records the exact source/native/export, regional ownership, actual WebGL/movement/inspection/fallback evidence and remaining defects. Nine diagnostic motion passes and one partial do not close F01–F04; F05 remains partial and F06 gated. No main-exhibit promotion or publication.

## V28 whole-form checkpoint — September 29, 2026

[V28 Form02](whole-character-v28-checkpoint.md) combines a larger lower-seated head, shorter curved rigid neck with fitted guards, fuller torso/pelvic/thigh support, compact canopy over an independent short shield, and shorter curved talons. Geometry and affected head/neck pivots were authored together; current joint locations were not treated as approved anatomy. Actual browser review caught sparse wing coverage and prompted Form02's fuller lap coverage.

F01–F04 remain OPEN: direction improves, but tall stance, generic breast bands, facial/neck construction and shoulder integration remain deficient. Finite crossing screens FAIL (neck 5–17 pairs; wing 52/54/57 across folded/guard/shove, including new coverage conflicts). F05 remains PARTIAL and F06 GATED. F07/F08 preserve nine controller passes/one partial and a new actual 14.70s canvas recording; no new full two-minute acting acceptance. F09 restores all 617 objects and source visibility correctly but does not pass exterior clearance. F10 local build/export/WebGL/fallback checks pass; production remains V9 with no new deployment. Early owner direction check is pending. No artistic score or acceptance is inferred from test results.

## V29 bounded fit checkpoint — September 29, 2026

[Fit01](whole-character-v29-checkpoint.md) retains only the fitted passive breast hinge and nested short-wing interfaces. Exact composition removes six hinge crossing identities at five openings; wing pairs improve52/54/57→38/38/37 with zero edited-interface pairs in three poses. Remaining contacts are failures, not inherited exemptions. Both root neck experiments are preserved and excluded after visual or interference regression; original neck counts5/17/5/9/6/4/4 remain.

All54 rest nodes and94 foot/toe meshes are exact. Native04040543…c63e7; GLBd6e5d4b9…53f6a. Browser export, six motion samples, inspection restoration of619objects, fallback and local build boundary are checked; no main-model promotion or publication. Overall likeness still fails the intended outcome. F01–F04OPEN, F05PARTIAL/F06GATED. Next visible work must address the head/breast/stance relationship, not treat another fit-only increment as fulfillment of the owner rejection.

## V30 whole-form check-in — September 29, 2026

[Form02](whole-character-v30-checkpoint.md) combines a continuous tapered breast, shorter authored structural supports, and a head experiment. The breast/support direction is provisionally retained; the shortened head is unsuccessful (blunt hook, straight jaw and mask-like face). Do not use its passing bounded motion checks as permission to finish or promote it. The extra-crouch experiment and earlier head/body fit failures are preserved and excluded.

Native `207e32fe…95e275`; GLB `bd08e5d1…b3a512`. Actual exact-composition breast/hinge/new-neighbor screens have zero introduced identities; inherited body/wing witnesses remain38/37, neck remainsFAIL2/15/2/7/4/1/1, jaw retains two inherited journal pairs. Controller checks9PASS/1PARTIAL, actual WebGL/inspection615-object restoration/fallback/local-build checks pass only their bounded scopes. The full new-model era machinery and finished exteriors are still absent. F01–F04OPEN, F05PARTIAL/F06GATED, F07–F09bounded; F10local only. All three era visual outcomes remain unaccepted.

Publication clarification: earlier “production remains V9” statements describe this branch's local build selection, not the live site. Fresh read-only verification binds live Pages to exteriorV1 at assessment revision `4b1c726`, model SHA `3ec668b0…baacdc5`; remote main was `2b3e284`. New studies are local and were not pushed or deployed.

The present patch-level process has reached diminishing returns. Next work must reconstruct the deep hook, curved mandible/cheek opening and integrated eye as one source-aligned head/neck form within an editable whole-body scene. No additional owner brief is needed to identify that failure. No fit-only checkpoint closes the likeness rejection.
# V31 check-in — held, not completion

2026-09-29: [V31 checkpoint](whole-character-v31-checkpoint.md) records the reconstructed head and complete era-mechanism attachment work. Actual controls/inspection/export checks pass within their stated scope, but likeness remains below the owner reference and the broad neck screen introduces two strike-pose collisions. F01–F04 OPEN, F05 PARTIAL, F06 GATED; F07–F09 bounded evidence only; F10 local only. Three finished exteriors and owner acceptance are not delivered. No publication. Do not count this fit checkpoint as resolving the owner's Squidward rejection.


## V32 — shape progress, owner direction pending

The formed lower bill and matched upper cutting profile replace the bar-like V31 jaw. Separate brow/cheek and tapered crown courses remain proposals. Exact head screens have zero witnesses in five jaw/two cap samples; broader neck counts2/14/2/7/4/1/1 still fail, all inherited after the two V31 introductions were removed. Full era integration, actual WebGL/inspection/fallback and local build have bounded evidence in the [V32 checkpoint](whole-character-v32-checkpoint.md). F01–F04 OPEN, F05 PARTIAL, F06 GATED; no owner artistic approval and no release.
