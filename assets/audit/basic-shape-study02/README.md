# MurderBird basic shape study — revision 02

Status: owner-requested head and torso adjustments, awaiting further notes.

Owner direction: soften the round node at the back of the head; elongate the
torso and draw it toward a point. The supplied red/yellow profile markup controls
these two changes. Its original bytes are preserved in `owner-annotated-side.jpg`,
SHA-256 `b0cdc156d262e5d5a6e92ac5ee0434ce2f76815243229a5a2cd5d8b5bb90bcb9`.
Source: attachment `1-Pasted-Image-1.jpg` in this chat, October 3, 2026. Creative
rights remain all rights reserved under NOTICE.md; no license is inferred from
the attachment. Prior study 01 remains preserved.

## Changes and interpretation

- Replace the rounded posterior skull contour with a continuous tapered crown
  and nape. The separate hooked bill remains preserved in the primitive study.
- Extend the torso down and backward into a narrow rounded point, following
  the drawn yellow contour. This is a diagonal elongation, not an overall
  enlargement of the bird or a change to its legs.
- Preserve neck, legs, feet and assembly cameras. Only the isolated torso
  framing expands to fit its new length without clipping.

`side-comparison.png` uses identical assembly camera, framing, lighting and
resolution before/after. `review.html` and the sheets provide front, top, side
and rear views of the complete bird and each part. All individual images remain
384 × 384 pixels. Hidden surfaces are proposals; exact percentages were not
specified by the owner, so the drawn contour governs this visual estimate.

Editable source: `murderbird-basic-shapes.blend`. Primitive parameters and
cameras: `study.json`. File hashes: `manifest.json`.

Reproduce using Blender:
`--background --python scripts/build-basic-shape-study.py -- --revision 02`,
then Python with Pillow: `scripts/layout-basic-shape-study.py --revision 02`.

Verification: renders visually inspected, gallery links resolved, original
canon hash checked, neck/leg isolated image pixels compared to study 01,
and generator syntax checked. This is a local shape study; no application
runtime change or public release. Neither overlays on the high-resolution art
nor modifications to the detailed 3D model are included. Next: owner notes.
