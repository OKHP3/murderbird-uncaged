# MurderBird basic shape study

Status: new proposed geometry, awaiting owner adjustment notes. This does not
promote Milestone 1b or authorize edits to its detailed model.

The owner requested front, top, side and rear views of head, neck, torso and
legs, using simple rounded polygons. `review.html` shows all sixteen isolated
part views plus four assembly views. Each render is 384 × 384 pixels. Part rows
are enlarged independently; assembly views share one scale. Top views point
forward upward; side views face right. View IDs H1–H4, N1–N4, T1–T4 and L1–L4
identify cells for notes. A1–A4 identify assembly views.

## Authority and assumptions

Reference: `assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg`,
SHA-256 `645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114`.
The shapes are visual estimates from that owner-selected image and the owner's
flightless-bird directions. They are not measurements recovered from the image,
nor a simplification extracted from the existing detailed asset. Hidden surfaces
and unseen projections remain proposals. Neck and leg segments are deliberately
simplified; no physical mass distribution or balance is validated.

This study omits wings, plates, surface materials, optics and machinery so the
four requested regions can be adjusted clearly. Creative material remains all
rights reserved under the repository NOTICE. The engineering archive, detailed
CG model, and original images are preserved.

## Editable source and reproduction

`murderbird-basic-shapes.blend` stores the same geometry used for every view.
`study.json` records its primitive parameters, axes, framing and assumptions.
`manifest.json` records output hashes.

Run Blender with `--background --python scripts/build-basic-shape-study.py -- --revision 01`,
then run `scripts/layout-basic-shape-study.py --revision 01` using Python with Pillow.
The source generators live at the repository root's `scripts/` directory.

## Next step

Wait for owner notes; revise this study first. Overlay accepted shapes onto
the high-resolution references afterward, labeling perspective registration
and inferred geometry. Adjust the detailed 3D model only after that review.
No exhibit runtime changes or publication are included in this checkpoint.
