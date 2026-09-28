# Correction v2 neutral candidate — independent visual review

**Review date:** 2026-09-27  
**Reviewed candidate:** [`murderbird-neutral-v2.glb`](../assets/models/uncaged-neutral-v2/murderbird-neutral-v2.glb), SHA-256 `85d0c44cd9fde244926eb9be9f32b64703b7731757f6ac32afc4ff1b6570c3b4`; editable source SHA-256 `065c7dd49a01b442d1931ef8de87dfbad2152f7b61afcd414dff1b527cb7e7c0`.  
**Scope:** visual review of F01–F04 against the selected references. This is an independent critique of one neutral-render checkpoint, not a score, approval, or closure. The source images are perspective illustrations and the neutral views are authored orthographic studio views; comparisons are qualitative, not dimensional measurements.

## Evidence reviewed

I inspected the neutral three-quarter, both side, front, rear, low and elevated views, plus the head, breast, mantle, and feet details under `assets/audit/neutral-v2/`. The referenced scene views use a neutral material and clean studio lighting. I also visually compared the result against candidate 03, the July head reference, Maker-clean and Mechanic stills. The exact feature scopes and source hashes are in [`correction-v2-reference-packet.md`](correction-v2-reference-packet.md) and [`reference-packet.json`](../assets/models/uncaged-neutral-v2/reference-packet.json).

The current neutral candidate shows useful shape progress. The breast now tapers more clearly toward the pelvis; the folded mantle is broader and more continuous around the shoulder; the optic opening exposes a distinct lens; the leg span is reduced; and the feet show curved separated talons. These changes are supported by the current images. They do not establish final likeness or solve the findings by themselves.

## F01–F04 findings

| Finding | Current disposition | What the captures support | Remaining visual discrepancy and evidence needed |
|---|---|---|---|
| **F01 · body/neck/silhouette** | **Open — partial progress** | The lower breast narrows into a more evident pelvis transition, and the upper torso reads heavier than the prior candidate. The neck has added curvature and layered coverage. | In the side views, the neck still reads as a tall, mostly upright column between the head and breast; the selected references show a shorter, stronger curved bridge. Breast plating remains evenly repeated across a rounded volume, so the deep breast can still read as a plated barrel rather than an organic-in-silhouette tapered bird torso. Recheck the side and three-quarter views against candidate 03 and Maker-clean after the next proportion pass. Include explicit judgments of breast taper, neck curve/mass, and shoulder width. |
| **F02 · head/bill/crown/optic** | **Open — partial progress** | The cut optic aperture now reveals a distinct inset lens; the head retains a deep hooked upper-bill outline and layered crown pieces. | The upper bill is still a broad smooth wedge with a thin, nearly closed lower-jaw seam. July and candidate 03 show a deeper convex bill surface and a readable cheek/mandible opening with distinct lower-jaw mass. The crown reads as a broad cap of large plates rather than the smaller swept segments that wrap around the cheek and optic. The optic is now visible, but its circular housing projects prominently from the head; check recession and how the crown/cheek frame it from side and three-quarter views. Recheck close-up, jaw-open/closed, and downward poses. |
| **F03 · folded mantle** | **Open — strong shape progress, incomplete evidence** | The shoulder covering is now broad, layered, and continuous enough to read as a folded armored wing around the ribs. This is closer to candidate 03’s compact near-side mantle than the previous disconnected-panel treatment. | The close-up still shows highly regular repeated rows and a large exposed round shoulder joint under the armor. In some views the mantle reads as a rounded pod attached to the torso; check that the full side silhouette remains compact and integrated rather than a circular shoulder mass. These are neutral poses only: the captures do not show guarding, right-side thrust, movement clearance, plate ownership, or the restricted anatomical-left travel. Keep F03 open until both sides are reviewed in folded, guard, and thrust poses with the repair chronology decided. |
| **F04 · limbs/feet/talons** | **Open — partial progress** | The stance remains grounded, toes are visibly separated, and curved talons are easier to read in the close-up. The reduced leg span helps body/leg balance. | Both side views still show long exposed mechanical struts and repeated flat shin plates between large cylindrical knee/ankle housings. The feet read as a nearly straight, flat row of toes; the talons are similar smooth hooks without much variation in length, direction, or hierarchy. Candidate 03 and Maker-clean support substantial load-bearing legs and broad grounded bird feet. Recheck upper-leg mass against the torso, toe spacing, claw silhouette and planted support in action poses. These stills cannot establish grip, balance, or foot-skating. |

## Overall judgment

This candidate is materially improved in torso taper, mantle coverage, optic visibility, leg span, and talon readability. The clearest remaining likeness gaps are the head’s bill/cheek/crown relationship and the long, column-like neck. Limb construction has better visible detailing but remains coarse and mechanically repetitive at full-body scale. The neutral images are enough to guide the next correction; they are not enough to close any F01–F04 finding or establish era-by-era visual-twin acceptance.

No owner likeness decision was supplied with this review. V10 left-shoulder chronology remains a separate pending choice in the reference packet. These static clay views do not test the Maker support/control arrangement, Mechanic travel, Advanced motion, restricted-side clearance, or illustrated fallback. No new runtime, deployment, or human-acceptance claim follows from viewing the authoring renders.

## Validation record

| Check | Status | Evidence / limit |
|---|---|---|
| Candidate identity | **PASS** | Current GLB and editable source digests recorded above. |
| Visual reference review | **PASS, bounded** | Selected full-body/head/era stills and the listed neutral views were visually inspected; no source metrology inferred. |
| F01–F04 closure | **NOT PASSED** | All four remain open; the table records partial visible progress and remaining evidence. |
| Motion and interaction review | **NOT RUN** | This was a neutral-render review, not a browser or continuous-motion session. |
| Owner acceptance | **PENDING** | No owner decision was part of the reviewed evidence. |

Next action: use these discrepancies to guide the next neutral shape pass, then compare fresh matched authoring views before adding era materials. Revisit the F03 repair and travel evidence after the V10 owner choice and pivot inventory are available.
