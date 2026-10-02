# LEGO MurderBird: 14-inch model reference review

Reviewed October 1, 2026. The owner requests an affordable, manually articulated Technic and conventional-brick MurderBird, approximately 14 inches tall. Assuming a full-size height of 84 inches, the target is exactly **1:6**, or **35.56 cm** from feet to crown, excluding a support. The assumed full-size height comes from the owner; the exported models do not establish it.

## Recent sources and selection

The main checkout at `fac4337d9f5128d3a6d720601fc5d2c197461fb8` contains V37. Newer V38 material resides in the linked checkout `/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged`, branch `codex/v38-hanging-breast-integration01`, reviewed at `a06c243d4cd3c764c3bacb876c2bf149c566fa25`. Sources were inspected without editing them.

| Saved checkpoint | Finding relevant to LEGO | Recorded status |
| --- | --- | --- |
| V37 production, September 29 | Complete articulated baseline, compact shoulders and rebuilt feet. Useful for comparing the whole silhouette. | Owner authorized deployment; final likeness and physical engineering remain open. |
| V38 facial-fit01 attempt02, October 1 | Smaller recessed optic, open cheek and repaired local facial crossings. Useful head reference; brow still reads as a band. | Retained development candidate, not final owner acceptance. |
| V38 hanging-breast01 attempt02, October 1 | Twenty-two formed hanging shields replace thirty-three rectangular breast tiles. Diagonal layers and free tips provide a useful starting point for removable brick armor. | Visible development gain, **FIT HOLD**: support, overlaps and motion clearance unproven. |
| V38 optic-seat01 attempt02, October 1 | Clearer upper orbital surround, but crowded lower cheek and little whole-bird improvement. | **HOLD**, source review only; not integrated. Being newer does not make it the preferred complete reference. |

Use hanging-breast attempt02 as a provisional whole-body proportion reference, with facial-fit attempt02 informing the head. Master03 remains the controlling breast/body artwork; the July reference is head-only. The LEGO interpretation must return to that artwork for likeness rather than copying every unresolved study feature.

## Measured proportions

Measurements use the exported GLB position vertices with the complete node hierarchy applied in world space, then normalize the vertical extent to the chosen height. They describe the saved assembled pose and include all exported era components. They are not a visibility-filtered single-era inventory, motion envelope, engineering dimensions or LEGO construction tolerances. Regional boxes overlap and must not be added together.

| Envelope | At 35 cm height | At 14 inches / 35.56 cm height |
| --- | --- | --- |
| V38 complete bird, width × depth × height | 19.0 × 22.8 × 35.0 cm | **19.3 × 23.2 × 35.56 cm** |
| Head including bill, width × depth × height | 6.4 × 10.9 × 8.6 cm | 6.5 × 11.1 × 8.7 cm |
| Neck group, width × depth × height | 5.7 × 8.2 × 6.4 cm | 5.8 × 8.3 × 6.5 cm |
| Torso and remaining equipment, width × depth × height | 13.5 × 12.5 × 12.6 cm | 13.7 × 12.7 × 12.8 cm |
| Both wing groups, width × depth × height | 15.1 × 11.0 × 10.0 cm | 15.4 × 11.2 × 10.2 cm |
| Legs and feet together, width × depth × height | 19.0 × 12.0 × 13.6 cm | 19.3 × 12.2 × 13.8 cm |

For comparison, V37 at 35 cm measures approximately 18.3 cm wide by 20.4 cm deep. V38's hanging-breast and optic-seat exports share the measured whole-body extent. Their 625 mesh nodes and 54 nonmesh transform nodes are digital organization, not LEGO piece counts or a requirement for 54 physical joints.

## Construction assessment

**Inferred:** this size is worth prototyping for a manually poseable model. Removing onboard power allows the torso volume to serve the frame and joints. The current evidence does not prove that the requested likeness, articulation and budget can all be met.

- Preserve the hooked bill, recessed optic, curved armored neck, compact layered wing guards, hanging breast shields, substantial legs and long talons. These features carry more likeness than reproducing every small plate or exposed cable.
- Concentrate articulation at head turn, one or two neck pitch joints, jaw, wing roots, hips and knees. The roughly 6.5 cm neck envelope is the tightest packaging challenge: simplify its armor segmentation and limit movement as needed to leave space for load-bearing joints.
- Keep the head hollow and the bill light. Its forward reach increases the load on the neck and the tendency to tip. Test the head/neck assembly under its finished weight before completing the bird.
- Build a braced torso and leg frame with removable armor. Use the breast study's layered visual rhythm; twenty-two digital shields need not become twenty-two independently moving LEGO elements.
- Prioritize feet that carry weight and knees that hold poses. Fixed or grouped toe construction is a reasonable first version. Do not transfer the digital model's compact foot joints as evidence of physical strength or clearance.
- Retain a removable support until loaded standing and posing are demonstrated. Check breast/hip, wing/torso and neck/head clearances in the actual proposed poses.

The brief's 1,200–1,800-piece range remains an unpriced planning proposal. This review establishes neither a parts total nor a dollar estimate. The next useful unit is a brick prototype of the characteristic head and loaded neck at this scale, followed by a leg/foot load test and a priced inventory.

## Evidence and limits

Inspected editable-source records, exported geometry and whole-bird/head/breast images. No model, exhibit code, release asset or linked worktree was changed. No physical LEGO assembly or continuous digital motion validation was performed. App build/tests were not needed for this documentation-only review.

- [V37 production record](production-v37.md).
- [V38 facial-fit handoff at the reviewed revision](https://github.com/OKHP3/murderbird-uncaged/blob/a06c243d4cd3c764c3bacb876c2bf149c566fa25/assets/audit/whole-character-v38/facial-fit-integration01/handoff.md).
- [V38 hanging-breast handoff at the reviewed revision](https://github.com/OKHP3/murderbird-uncaged/blob/a06c243d4cd3c764c3bacb876c2bf149c566fa25/assets/audit/whole-character-v38/hanging-breast-integration01/handoff.md).
- [V38 optic-seat disposition at the reviewed revision](https://github.com/OKHP3/murderbird-uncaged/blob/a06c243d4cd3c764c3bacb876c2bf149c566fa25/assets/audit/whole-character-v38/optic-seat01/attempt02/root-disposition.json).

The revision links identify locally inspected Git content; remote availability was not independently checked for this review. Measured GLB SHA-256 values:

| Export | SHA-256 |
| --- | --- |
| V37 attempt-release02 | `4b7c3d248d69a038795b0a5c7b7742b8a5b77d0a9050b7e5afa32b544b0d4e25` |
| V38 hanging-breast01 attempt02 | `051477ffcf62a4e08a3f1968d6cec7fd7f8b0677661cd72dde6ad7bbd5514650` |
| V38 optic-seat01 attempt02 | `fec7d89772a29bc106f129e5a3628d452d41cbf98e7e54b45082ff30db437633` |

Creative material remains all rights reserved under [NOTICE.md](../NOTICE.md). This local review records a proposed physical interpretation, not a new production release or final likeness acceptance.
