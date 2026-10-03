# MurderBird basic shape study — revision 04

Status: owner-directed shoulder/wing attachment study, awaiting review.

Authority: owner asked to treat the hip as the balance point and focus on the
shoulders, specifically the stubby wing attachment to the top of the breast.
Green front/rear markup is preserved in `owner-annotated-shoulders.jpg`, SHA-256
`594f6d3e14b07363be9741b66886618f28f78ec334d6a74e60689614b7b78409`.
Source: `1-Pasted-Image-1.jpg` attachment in this chat, October 3, 2026.
Creative rights remain all rights reserved under NOTICE.md.

## Changes

- Widen the upper breast/shoulder shelf across the front and rear, following
  the green trace, while preserving the torso's side-profile sections and lower
  pointed rear contour.
- Add two short rounded folded wing stubs, rooted in the high breast and
  lying against the upper torso. These are ornamental shield masses, never
  flight surfaces. Green distinguishes the new geometry from the teal torso;
  it is a study color, not a material or era finish.
- Preserve the hip axis, all leg shapes and feet, head, neck and existing
  cameras from study 03. Add four isolated shoulder/wing views, labeled S1–S4.

## Visual balance assumption

Retain the hip axis at Y +0.105 / Z +0.865 as the shape study's visual anchor.
The front head/breast and lower rear body should read as counterweights around
it. Equal mass on either side alone does not establish balance: distance from
the hip also matters. This CG blockout does not assign physical mass, calculate
centre of mass or claim mechanical validity. New stub depth, hidden surfaces
and widths are visual proposals for owner review.

## Deliverables and reproduction

`shoulder-comparison.png` shows study 03/04 front and rear at identical framing.
`side-comparison.png` also uses matched assembly cameras and lighting.
`review.html` includes the four assembly views and head/neck/torso/legs plus
the four new shoulder/wing views. Every individual image is 384 × 384 pixels.
Part rows are enlarged separately; assembly views preserve relative scale.

Editable geometry: `murderbird-basic-shapes.blend`. Primitive parameters,
camera framing, balance assumptions: `study.json`. Output hashes: `manifest.json`.
Reproduce with Blender:
`--background --python scripts/build-basic-shape-study.py -- --revision 04`,
then Python with Pillow: `scripts/layout-basic-shape-study.py --revision 04`.

Verification: renders visually inspected; original head/neck/leg pixels and
shape parameters preserved; torso Y/Z/radius-Y sections preserved; all existing
cameras preserved; gallery references resolve; original canon hash unchanged;
generator syntax checked. No detailed-model modification, high-resolution
reference overlay, exhibit runtime change or public release. Next: owner notes.
