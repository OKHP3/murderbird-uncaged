# V18 — regional construction and honest progress review

**HELD: visible improvement over the rejected V10, still below the MurderBird target and still failing important surface clearances.** This pass continues `36e8af79009f9d48573198f6c7c750d493e1cd52` on `codex/review-regression-v4`, worktree `/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged`. It preserves the existing application. Local development still defaults to V16; the production selection remains V9. No new publication occurred.

[Local matched review and actual export](http://127.0.0.1:5183/assets/audit/whole-character-v18/index.html) · [Explicit V18 runtime](http://127.0.0.1:5183/?review-body=v18-01&review-seed=927). These require the local server on this Mac. The gallery starts with the owner-rejected V10 rerendered using the exact V18 camera, scale and neutral light. The target illustration is separately labeled as a perspective reference, enlarged/cropped for readability with its complete original linked. Its camera is not claimed to match.

## Exact model and preservation

Editable [V18 attempt01 native](../assets/models/whole-character-v18/attempt-01/murderbird-whole-character-v18.blend): SHA-256 `696515decad31608600d0e3f753fcf7cb8ecf3e8a5283dd7d69266edd39e37ab`, 2,679,497 bytes. [Runtime derivative](../assets/models/whole-character-v18/attempt-01/murderbird-whole-character-v18.glb): SHA-256 `b59bf9dee1ff681c53b21aedfb1505c1fb944890d673a07b3e3b148fd95babf8`, 10,675,336 bytes.

The [composition receipt](../assets/audit/whole-character-v18/attempt-01/receipt.json) freezes all four regional modules and the composer. It records 29 changed existing meshes, four additions, no removals, 684 exact unrelated meshes, all 52 rigid nodes/parents/transforms and 462 guides preserved, identical materials, and an exact save/reopen check. The composer also rejects overlapping module edits. The [export receipt](../assets/audit/whole-character-v18/attempt-01/export/export-receipt.json) verifies the native stayed unchanged and all 52 nodes survived export. Historical assets and unsuccessful drafts remain intact. Neither guides nor rigid-node checks establish functional cables or physical simulation.

## What changed and what remains wrong

| Region | Integrated construction | Evidence and remaining failure |
| --- | --- | --- |
| Orbital surround / crown | Orbital04: narrower retaining races, visible paired passive fittings and a finite leading crown underlap. 16 existing meshes change. | All 16 changed subjects clear neighboring head/crown/bill/jaw/optic owners in 21 regional pose samples. Twelve prior scoped crossing identities disappear. Whole-head form remains too smooth and sparse; this is no likeness approval. |
| Breast frame | Ring-preserving fit of two retained ribs to the rounded V17 shell. Rail contact rings and tube cross sections stay intact. | Closed/action fits improve. The access shell and a top plate still cross fixed ribs at four opening levels. The hinge/envelope must be redesigned together. |
| Lower neck | Reconstruction01 replaces seven lower guard sheets/backing relationships and eases the adjacent throat edge; nine existing meshes change. | The hanging cup is removed. Five scoped pairs still cross at rest, two with Maker neck control and 22 at Advanced contact. The collar and curved transition remain visually unresolved. Reconstruction02 exposes a void and is excluded. |
| Lower legs | Leg06 replaces two open metatarsal trusses with tapered ported channels and adds four passive shin/yoke parts. | No scoped different-owner strict crossings in 27 regional poses, including six claw phases. Thirty-two fixed same-owner crossing identities still need construction adjudication. Joint housings and feet remain too light/simple. |
| Wings, pelvis, toes and rear | Existing compact flightless assemblies, left restriction, rigid pivots and compact rear remain. | No claim of newly achieved reference likeness or full clearances. Thickened shanks do not establish heavier feet or adequate drive density. |

[Independent whole-character review](../assets/audit/whole-character-v18/attempt-01/independent-review.md) identifies substantial remaining shape gaps: broad egg-like breast, oversized repetitive plate forms, a column-like neck, simplified bill/optic and sparse limbs. The gray finish is deliberate for shape review. Material polish would not fix those defects. [Supervisor decisions](../assets/audit/whole-character-v18/supervisor-disposition.md) retain the failed alternatives and why they were rejected.

## Regional construction, materials and inheritance

The [V16 regional contract](whole-silhouette-v16-regions.md) and [V17 construction record](whole-character-v17-regions.md) remain the baseline for unchanged regions. V18 changes are specified in [orbital fit](whole-character-v18-orbital-fit.md), [breast/frame fit](whole-character-v18-breast-fit.md), [neck reconstruction](whole-character-v18-neck-reconstruction.md) and [leg envelope](whole-character-v18-leg-envelope.md), including exact component identities, rigid owners, finite surfaces, clearance failures, references and reconstructed details.

| Construction | Reference scope / attachment | Maker | Mechanic | Advanced |
| --- | --- | --- | --- | --- |
| Head fittings and crown underlap | July head only and owner target; rigid `head` and `cranial-cover` attachments; crown opens independently | Inherited passive machinery, dark optic | Same inherited passive hardware, no new sensing | Same fittings; existing restrained optic/sensing eligibility retained |
| Breast ribs and panel | Selected Maker construction / common body; ribs fixed to `body`, access plates to `breastplate` | Passive support and external-control access | Inherited support around existing transmission | Inherited support around existing protected supply/distribution |
| Neck guards and backing | Common-body/owner target, July restricted to head; `neck`/`cervical-upper` rigid overlapping sheets | Outside-operated articulation | Existing restricted mechanical drive | Existing coordinated actuation; contact fit still fails |
| Shin webs, foot channels and yokes | Owner target and selected full-body lineage; separate shin/foot owners with ports and end relief | Passive load members only | Inherited passive members; repair/drive hardware remains distinct | Same inherited members around existing actuation |

No new powered component, sensor or biological tissue is introduced by these modules. New shapes and small fitting functions remain reconstruction proposals, not recovered historical facts. All eight material definitions are inherited. The derivative has no image textures or UV coordinates; geometry supplies edges, overlaps and openings, with existing glTF material/vertex response. [Pipeline inventory](../assets/audit/whole-character-v18/attempt-01/surface-pipeline.json). This is a deliberate neutral construction pipeline, not evidence that it can yet deliver the requested finished materials. Three era-specific finish and repair-history treatments remain gated by the structure/likeness review.

## Verification and limits

[Exact-export bounded checks](../assets/audit/whole-character-v18/attempt-01/check-summary-v2.json) pass: kinematics 4/4, inspection matrix restoration 1/1, Advanced power moves 4/4 and claw contact 32/32. A fresh 21-pose packet, SHA `5df577436747042d5ba56e33f0dcc8cc0401e07ff423844a27dcc5756f646a30`, drives [eight native movement illustrations](../assets/audit/whole-character-v18/attempt-01/motion-renders/render-02/pose-render-manifest.json). These show all-era selected controls/actions and opening, omit procedural browser hardware and are not a video or collision simulation.

[Actual browser evidence](../assets/audit/whole-character-v18/attempt-01/browser/summary.json) confirms hardware WebGL served the exact V18 hash. All five Maker controls, Mechanic stepped phases, opening/separation/reassembly and a strike trace were exercised. Jump was UI-triggered and sampled at normal speed; thrust was successfully requested through the public development action hook and sampled at normal speed after an earlier UI trace failed to capture it. The strike trace reaches the controller contact state, but its motion-level contact flag remains false; those are distinct observations. Returned runtime and gallery warning/error lists were empty. Main fallback remains a verified V9 illustration, explicitly disclosed; gallery fixed mode uses the V18 native image.

A short independent sample of 360 frame intervals on Apple M4 Max at 856×648, pixel ratio 1, recorded 10.0 ms median and 11.2 ms p95 across 3.60 seconds, with 354 draw calls and 953,748 triangles. This is a short desktop watch/pace sample, not sustained or mobile performance evidence. Temporary browser samplers were cleared by reload.

The first native pose render had thin floor-directed lines. A second write-once render hides all 462 historical guide curves, but some lines remain; their cause is unresolved. These lines are not credited as functional cables. Both render runs remain preserved; no actual mesh was hidden to conceal a motion defect.

Regional strict checks bind their own exact regional natives and the unchanged V17 pose matrices; they are not mislabeled as checks against the final combined GLB. The combined export has a fresh runtime packet and browser verification. Known neck, breast-opening and fixed leg-fit defects remain acceptance failures. No continuous sweep, containment, load/strength, full mechanism endpoint reconciliation, physical mobile test or human acting acceptance is established.

`npm ci`, `npm run build` and the publication boundary check passed. [Build inventory](../assets/audit/whole-character-v18/attempt-01/build/summary.json) contains 134 intended emitted files and the exact source hashes; V18 native/study files and private archives are excluded. The optional `fsevents` script and existing large bundle warnings remain. This is a local modified-tree build, not remote CI or deployment.

## Next structural correction and owner decisions

The current side-opening breast pivot lies inside the wider shell planform. Correct that hinge and its physical supports together with a finite, flared lower-neck underlap that reaches into the cavity. Preserve the improved head/leg regions, and reassess the whole bird before a finish pass. Do not use further arbitrary surface clamps, treat old pivots as approved, or count repeated checks as visual progress.

The owner’s whole-character approval, reconstructed detail decisions and three exterior-state approval remain outstanding. No owner permission is needed merely to repair these demonstrated structural defects. The supplied rejection remains controlling; this checkpoint does not claim to have met the final brief.
