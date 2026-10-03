# MurderBird basic shape study — revision 03

Status: new owner-directed contour pass, awaiting review.

Authority: owner supplied an orange torso trace and purple thigh/shank trace
over study 02, with the instruction "Next round adjustments." Original annotation
bytes are preserved in `owner-annotated-side.jpg`, SHA-256
`a182589242f3f7d7b171e4ba643713c54e8ec84e65aeee90c6dd24ecde6572d7`.
Source: attachment `1-Pasted-Image-1.jpg` in this chat, October 3, 2026. Creative
rights remain all rights reserved under NOTICE.md; no additional license inferred.

## Interpretation applied

- Orange: fuller continuous rear flank and lower belly, retaining a compact
  lower rear point. Preserve upper shoulder/head relationship.
- Purple: rounded proximal thigh tapering to the knee, a fuller shank, and
  a slightly forward/down knee. Its movement is a visual estimate from the trace,
  not a numeric instruction: -0.05 on the forward Y axis, -0.02 on Z.
- Preserve head, neck, hip/hock/ankle anchors, planted feet and all cameras
  from study 02. Earlier study files and detailed models remain untouched.

The owner trace supplies a visible profile, not exact 3D dimensions. Hidden
surfaces and front/top/rear widths remain proposals. No balance, fabrication
or engineering validity is claimed. No detailed model modification or reference
overlay is included in this checkpoint.

## Deliverables

`side-comparison.png` compares study 02 and study 03 with identical cameras,
scale and lighting. `review.html` provides assembly and isolated head, neck,
torso and legs in front/top/side/rear views. Each view is 384 × 384 pixels.
Part rows are enlarged independently; use assembly views for relative sizes.

`murderbird-basic-shapes.blend` is the editable geometry. `study.json` records
primitive parameters, cameras and assumptions; `manifest.json` records output
hashes. Reproduce with Blender:
`--background --python scripts/build-basic-shape-study.py -- --revision 03`,
then Python with Pillow: `scripts/layout-basic-shape-study.py --revision 03`.

Verification: rendered comparison visually inspected; head/neck isolated pixels
unchanged; foot geometry and fixed joint anchors checked against study 02;
gallery references resolve; original canon hash unchanged; generator syntax
checked. No exhibit runtime changes or public release. Next: owner notes.
