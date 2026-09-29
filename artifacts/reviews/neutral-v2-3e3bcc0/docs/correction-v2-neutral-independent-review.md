# Correction v2 neutral candidate — independent visual review

**Review date:** 2026-09-27  
**Reviewed candidate:** [`murderbird-neutral-v2.glb`](../assets/models/uncaged-neutral-v2/murderbird-neutral-v2.glb), SHA-256 `48229ba5526ccd7a227db56d225ef88643eb6b3388eb07662452cc2c67636ac7` (6,038,136 bytes; 867 source pieces); editable source SHA-256 `64ea6d86504987357eb22c2e3c4036ec87da6432f15354f5d4a07d004fd6dec9`.  
**Scope:** independent visual review of F01–F04 against selected illustrations. This is a critique of the current neutral-model checkpoint, not a score, approval, or closure. Perspective source illustrations and authored model views are qualitative comparisons, not dimensional measurements.

## Evidence reviewed

I inspected the current `neutral-head.png`, `neutral-side-right.png`, `neutral-three-quarter.png`, and Builder, Maker, and Mechanic `*-reference-perspective.png` views in `assets/audit/neutral-v2/`. I compared the model views with the selected candidate 03 full-body illustration, July head image, and Maker-clean and Mechanic illustrations already recorded in the reference packet. The exact source scopes and digests are in [`correction-v2-reference-packet.md`](correction-v2-reference-packet.md) and [`reference-packet.json`](../assets/models/uncaged-neutral-v2/reference-packet.json).

The latest iteration improves the head outline: the crown has smaller courses and a segmented brow, the cervical span is shorter and more curved, and the bill is a narrower ridged hook with a compound surface. The breast-to-pelvis taper, broad folded mantle, inset optic, shortened leg span, and separated curved toes remain visible strengths. The per-era perspectives still show the same underlying repeated construction language; era styling does not resolve the neutral-shape findings. Root also reports that the uniform procedural courses and coarse leg construction remain insufficient for a visual twin. That is a production-method concern, not an independently measured source fact, and is consistent with the repeated regularity visible in the captures.

## F01–F04 findings

| Finding | Current disposition | What the captures support | Remaining discrepancy and evidence needed |
|---|---|---|---|
| **F01 · body/neck/silhouette** | **Open — partial progress** | The breast narrows toward the pelvis; the neck is shorter and bends more than in iteration D. The body retains a compact, grounded bird-like outline. | From the right-side view, the neck/head connection still reads as a stack of repeated plates around a narrow upright bridge, with a visible structural gap/transition beneath the head. The torso surface is densely and evenly coursed, so its silhouette reads as a plated barrel despite the improved taper. Compare matched side and three-quarter views with candidate 03 and Maker-clean; assess neck mass/curve, shoulder width, and breast depth as whole forms. Do not treat the shortened span alone as likeness closure. |
| **F02 · head/bill/crown/optic** | **Open — partial progress** | The bill now has a cleaner, narrowed hooked profile and visible longitudinal ridging; the crown is smaller and more segmented, with a brow course. The optic is distinct. | The side view still lacks a convincing cheek-to-mandible bridge: the lower cheek/jaw assembly looks layered and mechanical, with a narrow seam and open structural space under the optic, rather than a clear, unified cheek and lower-jaw mass. The upper bill remains smooth and regular compared with the illustrated deep convex hook. The optic ring projects prominently, and the crown courses remain uniform despite being smaller. Recheck side and three-quarter head shape against the July head reference and candidate 03, including open and closed jaw states. |
| **F03 · folded mantle** | **Open — shape progress, motion/ownership unverified** | The mantle reads as a broad folded wing with continuous coverage from the shoulder into the flank, closer to candidate 03’s compact near-side silhouette than the earlier disconnected panels. | Many small, similarly shaped plates repeat in highly regular courses across the mantle and body. The shoulder covering still reads as a separate rounded pod, and its moving-side plate ownership is not demonstrated by a static view. No reviewed image shows guard, right-side thrust, fold clearance, or the restricted anatomical-left travel. Review both sides in the required poses after the V10 chronology and pivot/contact inventory are resolved. |
| **F04 · limbs/feet/talons** | **Open — partial progress** | The stance remains grounded, the leg span is shorter, and the toes are separated with curved talons. | The side/full-body views still show coarse exposed struts and repeated flat shin plates between large drum-like knee and ankle joints. Toe links and claws repeat similar sizes and directions; the planted foot looks assembled from uniform segments. The captures do not establish grip, balance, contact stability, or foot-skating. Compare limb mass and foot spread against candidate 03 and Maker-clean, then inspect stance and movement contact in authored poses. |

## Overall judgment

This checkpoint is a meaningful improvement over iteration D in the head silhouette, neck length, crown segmentation, bill shaping, body taper, mantle coverage, and visible optic. The most consequential remaining visual gaps are the head/cheek/mandible transition, repeated uniform plate language, and coarse exposed limb construction. The model remains a procedural construction study; neither the updated neutral views nor per-era perspectives establish an era-specific visual twin. All four findings remain open.

This review inspected static authoring views only. It does not test mechanism, movement, contact, shoulder clearance, runtime behavior, illustrated fallback, or the owner’s intended likeness. V10 left-shoulder chronology remains pending in the reference packet. No score, acceptance, or closure is claimed.

## Validation record

| Check | Status | Evidence / limit |
|---|---|---|
| Candidate identity | **PASS** | Current GLB and editable-source digests and GLB byte count recorded above. |
| Visual reference review | **PASS, bounded** | Three neutral head/body views and three per-era perspective captures visually inspected; selected source illustrations compared within documented scopes. No metrology inferred. |
| F01–F04 closure | **NOT PASSED** | All findings remain open; visible progress and remaining discrepancies are recorded above. |
| Motion and interaction review | **NOT RUN** | No browser, GPU, continuous-motion, or contact review was performed by this reviewer. |
| Owner acceptance | **PENDING** | No owner likeness decision was part of this review. |

Iteration D’s earlier critique is preserved separately in the archived iteration-D record. This file documents the later candidate only. The next useful evidence is another matched-view neutral review after targeted head/neck and limb-form work, followed by movement and clearance views for F03/F04 after their dependencies are resolved.

## Frozen runtime-pose capture addendum

**Scope:** static screenshot review only, against the same frozen GLB `48229ba5526ccd7a227db56d225ef88643eb6b3388eb07662452cc2c67636ac7`. I inspected left/right and three-quarter Builder jump and thrust captures, Builder contact captures from head/left/right/three-quarter views, and Maker jaw-open/closed captures from head/left/right views. These snapshots do not show continuous acting, collision telemetry, or exhaustive clearance.

- **Jump:** The three-quarter captures read as an airborne crouch with the feet visibly clear of the floor. The folded legs and foot links look compact but remain a stack of exposed rigid segments. Since no landing/contact sequence is shown, these stills cannot establish limb support, balance, or safe landing.
- **Thrust:** The pose reads mostly upright and both feet appear planted in the reviewed side views. The near and far mantle remain folded, so the supplied stills do not clearly communicate a thrusting wing or show its excursion. Dark and brass-colored rods are visible beside/under the torso, but their attachment and clearance cannot be determined from these angles. Do not credit this as a demonstrated thrust cycle.
- **Contact:** The gold ring visible above the bill is the visitor/attention reticle at fixed `y=1.60`, not the contact target. Root’s source adjudication identifies the selected vertical rail as the contact target and reports a frozen-receipt bill/rail-centre hit at `[0, 1.20596357, 2.07900006]`, with tiny radial error and zero neck/skull translation error. The neutral cage is hidden in these captures, so the stills cannot independently show the rail or establish a rail hit/miss. The reticle remains a presentation ambiguity because it reads as a floating target near the bill. The stance appears floor-supported, but the stills do not prove stable contact or exclude transient clipping.
- **Maker jaw:** The open/closed head views show the jaw state change, but the lower jaw remains visually small and mechanically layered under the larger bill. The reviewed captures do not establish a clean contact path, collision-free sweep, or reliable stop across the full range.

These pose observations add concrete runtime-presentation concerns while leaving the neutral F01–F04 findings unchanged and open. They are not a continuous motion review, full collision audit, or acceptance result.
