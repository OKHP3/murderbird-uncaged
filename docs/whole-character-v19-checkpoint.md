# V19 — fitted bill, front access door and held likeness review

**HELD: useful construction changes, still below the required MurderBird likeness.** This continues local commit `4f182a8f6958bdccd206973a0d437d4067da06b8` on `codex/review-regression-v4`, worktree `/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged`. No material finish or artistic acceptance is claimed. Development default remains V16; production remains V9. This candidate has not been published.

[Local comparison gallery](http://127.0.0.1:5183/assets/audit/whole-character-v19/index.html) · [Explicit V19 attempt02 runtime](http://127.0.0.1:5183/?review-body=v19-02&review-seed=927). Both require this Mac's local server. The gallery leads with the actual owner target and exported model, then matched V18/V19 cameras. Display enlargement is not calibrated reference-image alignment.

## Exact deliverable

Editable [attempt02 native](../assets/models/whole-character-v19/attempt-02/murderbird-whole-character-v19.blend): SHA-256 `d98c46770101ad608fe2c50212a7b307ca66d5389f93ce7d43b79b9c7d41dded`, 2,788,800 bytes.

[Runtime derivative](../assets/models/whole-character-v19/attempt-02/murderbird-whole-character-v19.glb): SHA-256 `b3a59adf99a167276155895c6d0fe8f714e6676d36a5b28313c621ec5410a9c2`, 12,004,088 bytes.

The [composition receipt](../assets/audit/whole-character-v19/attempt-02/receipt.json) freezes head03 and torso05 regional sources and the composer. It records 114 changed mesh geometries, 27 added meshes, no removed meshes, 603 exact unchanged mesh records, all 462 historical guides and material definitions exact, and an exact save/reopen check. Of 52 rigid nodes, only the breastplate pivot and its opening metadata change; the other 51 remain exact. The [export receipt](../assets/audit/whole-character-v19/attempt-02/export/export-receipt.json) verifies that the native stays unchanged and all 52 rigid nodes survive.

## Visible discrepancy and construction record

| Region | V18 defect / V19 change | Current disposition |
| --- | --- | --- |
| Bill and jaw | A broad uninterrupted bill and hanging mandible produced a long smiling opening. Two finite 4 mm skins now replace proximal bill side faces under the retained cap and cutting edge. The middle mandible rises by up to 45 mm, fading to unchanged hinge and distal seats. | Narrower gape and more coherent plate seams; broad smooth bill/cheek integration still lacks the reference's identity. The bill-contact marker is unchanged. |
| Breast envelope | The rounded front is tapered and recessed into a reshaped underlying frame. A narrow lateral blend caused padded bulges in torso04; torso05 broadens the blend and restores monotonic sampled sections. | Bulges are removed. Repetitive large plates and the neck collar remain visually unresolved. |
| Access construction | The old moving breastplate was an entire wrapped ellipsoidal shell. Side-hinge and early bottom-hinge attempts drove rear portions through fixed structure. Torso05 separates a front door from body-owned side/rear liner and places a supported horizontal bottom axis below its seam. | The cover itself clears the liner and ribs at all four sampled nonzero openings. Shaft-stock and lower return intersections remain; no full mechanism clearance claim. |
| Neck | Lower guards extend deeper into the breast cavity with finite overlapping walls and a gentler front contour. | Neck-to-breast flow still reads as an abrupt collar. Maker and Advanced action samples retain substantial crossing identities. |
| Wings, legs and rear | V18 compact flightless wings, restricted anatomical-left movement, strengthened lower-leg pieces and compact rear are preserved. | The folded mantle still reads too much like a broad plate blanket, while limbs/feet look too slight for the body. Unchanged does not mean approved. |

[Independent combined-model review](../assets/audit/whole-character-v19/attempt-02/independent-review.md) keeps the same whole-character failures open. The head does not need an arbitrary wholesale resize; it needs bill/cheek construction, and the body needs stronger curved neck and limb/shoulder mass relationships. All three eras remain below the required likeness outcome. No updated numerical visual score is invented from these qualitative views.

## Regional attachment, materials and era eligibility

The [V16 regional contract](whole-silhouette-v16-regions.md), [V17 construction record](whole-character-v17-regions.md) and V18 region records remain the baseline for unchanged areas. [V19 torso/neck details](whole-character-v19-torso-neck.md) contain exact component assignments, geometry, preserved rest transforms, finite-wall checks, failed attempts and missing clearance. The head module is frozen in the composition receipt.

| Region / reference | Rigid attachment and movement | Maker / Mechanic / Advanced inheritance | Clearance and inspection |
| --- | --- | --- | --- |
| Bill skins; July head only, owner target for neutral gape | `upper-bill`; 4 mm rigid sheets, no deformation or sensor additions | Passive inherited skins in all three; existing optic eligibility unchanged | Separate constructed panels under cap/edge; no new jaw sweep pair identities in the regional nine-angle check |
| Mandible; same scoped head sources | `jaw`; middle shape changed, existing pivot/seat retained | Passive frame moved by existing era-specific control/drive | Existing journal/cap crossings remain; not accepted running fits |
| Breast/frame; selected Maker construction, common-body and current owner target | Shared torso envelope deformation; fixed liner/plates on `body`, opening front on `breastplate` | Passive structure in all three around existing external controls, transmission, or Advanced hardware | Native local X / browser local X, +1.1 radians opening; separate front/fixed walls retain 4 mm thickness and a 6 mm seam |
| Lower neck; common body and current target | `neck` / `cervical-upper`; finite rigid overlaps and backing | Outside-operated / mechanically driven / coordinated actuation from inherited era systems | New surfaces still cross surrounding structures in reviewed action poses |
| Access supports and axle; proposed unseen construction | Fixed bearings/seats on `body`, axle and finite returns on `breastplate` | Passive inherited hinge construction; no early-era powered hardware | Missing shaft passages and below-axis keel returns remain explicit design defects |

Authored dimensions, rear reconstruction, hidden supports and exact mechanisms are proposals, not recovered historical facts. Original story and sources are unchanged. No biological tissue is introduced. No metal armor is stretched at runtime.

The [GLB inventory](../assets/audit/whole-character-v19/attempt-02/surface-pipeline.json) reports eight materials, zero images/textures/UV sets and zero skinned joints. The export groups rigid surfaces by common owner/role/era; four new exported groups represent additions across 27 new editable source objects. Independently opening assemblies retain separate rigid nodes. Per-era static exported triangles are 550,000 Maker, 550,068 Mechanic and 551,392 Advanced, before procedural browser hardware and render passes. This neutral geometry pipeline is not evidence that the three requested finished exterior treatments are complete.

## Verification and failures

Fresh exact-export checks pass: kinematics 4/4, inspection restoration 1/1, Advanced power moves 4/4 and claw contact 32/32. The inspection check exercises five open/separation/reassembly cycles in each era and now uses declared hinge metadata; historical V9 also passes with its original untagged side hinge. These establish bounded motion and matrix restoration, not collision-free surfaces.

A fresh [21-pose packet](../assets/audit/whole-character-v19/attempt-02/runtime-poses/pose-snapshot.json), SHA `311b1305f36ad4bb94bef041ac122f8f7dd5c4ad4b11c708aff2a8ab652999af`, binds the exact combined GLB. [Eight native pose illustrations](../assets/audit/whole-character-v19/attempt-02/motion-renders/pose-render-manifest.json) show Maker jaw/shield, Mechanic turn, Advanced contact/recovery/jump/thrust and inspection. They omit procedural browser hardware and are not a motion recording or physical simulation.

The [combined native/GLB clearance check](../assets/audit/whole-character-v19/inspection-tooling/attempt-02/clearance/breast-opening.json) confirms the new X/+1.1 hinge matrices within maximum error 1.19e-7 across all 52 rigid nodes. Five discrete opening levels contain 18/7/9/9/11 strict crossing pairs. The previous cover-versus-liner/rib obstruction is absent at nonzero openings. Seven recurring pairs involve the moving shaft and fixed liner, lower lamina fragments and seat boxes; four additional full-open pairs involve lower keel returns. Counts are interface identities, not independent design failures. Intended mating or lap overlaps are not automatically valid clearance.

Maker neck-control and Advanced contact samples retain 33 and 40 strict neck/neighbor crossing pairs. These are fresh combined-model findings, not the earlier torso04 counts of 38/45. The head and body changes affect targets even though several neck guard meshes are unchanged. No continuous sweep, containment, load/strength, all-linkage endpoint or artistic acceptance is established.

Head03's independent nine-angle jaw check preserves the same four inherited journal/cap crossing identities, with no new/resolved pairs. Both new bill skins are closed and consistently wound. Torso05's 51 checked finite pieces are closed and have positive volume; partition-tip slivers from torso04 are gone. Fastener ownership counts match 68 moving and 10 fixed whole islands. These construction checks do not override the action failures.

A controlled same-model/pose/light test isolated the prior thin floor-directed lines to Workbench cast shadows. New pose illustrations disable cast shadows explicitly; actual character meshes remain visible. The [shadow diagnostic](../assets/audit/whole-character-v19/render-shadow-diagnostic/assessment.md) is not geometry-clearance evidence.

`npm ci`, the final local build and publication-boundary check passed. [Final build receipt](../assets/audit/whole-character-v19/attempt-02/build/receipt.json) and [complete dist inventory](../assets/audit/whole-character-v19/attempt-02/build/inventory.json) record 134 intended outputs; V19 native/studies/private archives are excluded. The optional fsevents-script and existing bundle-size warnings remain. This is local verification, not remote CI or deployment.

## Actual browser review

[Browser evidence](../assets/audit/whole-character-v19/attempt-02/browser/summary.json) verifies hardware WebGL fetched the exact 12,004,088-byte V19 GLB and expected hash. Opening, 100% separation and reassembly reached their requested states. All five Maker sliders were exercised together; the exact-export checks separately cover individual articulations. A short Mechanic run sampled load/release/settle/dwell. Advanced jump was UI-triggered; a fresh shield thrust was accepted through the public development action hook after a development reload interrupted the earlier UI trace. Both were passively sampled at normal speed. These samples are not the required full long-form acting assessment.

A short independent 360-frame-interval measurement on Apple M4 Max, canvas 856×648 at pixel ratio 1, covered 3.602 seconds during the jump. Median was 10.0 ms; p95 was 11.0 ms. This is not sustained performance, physical-mobile, thermal or constrained-network evidence. Returned runtime/gallery warning/error lists were empty.

The main illustrated view loaded its existing V9 image and disclosed that version. The gallery's fixed V19 image loaded through its DOM click handler; automated pointer activation did not work in this session, so pointer usability is not credited as verified. Both runtime and gallery were restored to their normal V19 review states. All temporary sampling timers were cleared by navigation. [Final side-by-side capture](../assets/audit/whole-character-v19/attempt-02/browser/comparison-final.png).

## Finding status and next correction

| Finding | Status after V19 |
| --- | --- |
| F01 body/neck/silhouette | Open. Breast taper improves, curved neck transition remains wrong. |
| F02 head/bill/crown/optic | Open. Jaw and actual bill segmentation improve, identity still below target. |
| F03 folded mantle | Open, preserved but still visually too blanket-like. |
| F04 limbs/feet/talons | Open, inherited local strengthening insufficient for target mass. |
| F05 regional plates | Open; construction additions do not settle regional plate hierarchy. |
| F06 materials/wear | Gated by structure/likeness; no finish pass. |
| F07 articulated claw | Existing bounded checks pass on this export; full visual action acceptance remains open. |
| F08 varied acting | Existing behavior preserved; no new full two-minute acting reassessment claimed. |
| F09 labels | Existing controls preserved; complete layout/accessibility matrix not repeated here. |
| F10 validation scope | Current allowlist-based publication check passes; no new closure beyond prior tooling evidence. |

The procedural local adjustments have produced useful parts but have not converged to the requested visual twin. The next geometry work must address larger head-to-neck-to-breast and shoulder-to-limb relationships using explicit reference landmarks and an editable whole-body control cage in Blender. Current pivot positions are implementation data, not approved anatomy. Preserve movement interfaces while revising any necessary frame/pivot locations together, then rederive contacts and supporting external mechanisms. Do not spend another pass merely fitting small collars around the same unresolved silhouette.

The remaining access correction is concrete: authored finite shaft passages or saddles through the fixed stock, sized to the existing 8 mm bearing bores around the 6 mm shaft, plus reshaped lower keel underlaps that remain above the axis through opening. Removing unclosed faces would be insufficient. These are proposals for the next construction revision.

Owner artistic acceptance of the whole neutral character, repair chronology/topology and scoped Maker/Mechanic motion interpretation remain outstanding. This checkpoint does not ask the owner to waive known defects. Correcting them is already authorized; finished era materials and publication of a new candidate remain subject to the governing review gate.
