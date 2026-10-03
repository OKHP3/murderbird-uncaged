# MurderBird basic shape study — revision 05

Status: owner-requested larger folded wings, awaiting shape review.

Owner direction: increase wing size by about 25%. Original green-marked
assembly is preserved at `owner-annotated-wings.jpg`, SHA-256
`97bee601b4ad3c2a959015fadd9e1a36b22a5abae177305c75866012684580b0`.
Source: `1-Pasted-Image-1.jpg` attachment in this chat, October 3, 2026.
Creative rights remain all rights reserved under NOTICE.md.

## Change and interpretation

Scale each existing folded wing form by 1.25 in all three linear dimensions,
about its fixed upper-breast root: left (-0.195, -0.045, 1.335), right
(+0.195, -0.045, 1.335). This is a linear-size interpretation, not a 25%
surface-area, volume or mass change. Keep the forms folded and ornamental;
no flight surfaces or arm-like extensions.

Head, neck, torso, hips, legs, feet and cameras remain identical to study 04.
Prior study files and the detailed CG models are preserved. Green highlights
the study wing shapes; it is not a final surface or material decision.

Prior design direction remains: the mechanical lower rear body may house a
dense power source, motor and transmission as a visual counterweight to the
head. Such components are proposals, not built or physically validated here.

## Deliverables and reproduction

`side-comparison.png` compares studies 04 and 05 with identical assembly
framing and lighting. `shoulder-comparison.png` compares matched front/rear
views. `review.html` includes all four assembly views and isolated head, neck,
torso, shoulders/wings and legs. Individual views are 384 × 384 pixels.
Part rows are enlarged independently; assembly views preserve relative scale.

Editable scene: `murderbird-basic-shapes.blend`; parameters/cameras: `study.json`;
output hashes: `manifest.json`.

Reproduce using Blender:
`--background --python scripts/build-basic-shape-study.py -- --revision 05`,
then Python with Pillow: `scripts/layout-basic-shape-study.py --revision 05`.

Verification: matched renders inspected; non-wing isolated pixels and geometry
preserved; wing linear scaling and fixed roots checked; gallery links resolve;
original canon hash unchanged; generators parse. No detailed-model edit,
high-resolution reference overlay, exhibit runtime change or public release.
Next: owner notes on wing proportions.
