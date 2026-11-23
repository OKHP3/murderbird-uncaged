# First Choice motion

The final build runs the head, mantle, pedal and neck-reach adjustments on retained04 Advanced, then passes the corrected head pivot from `apply_reach()` to `apply_motion()`. The full call sequence is in `atelier/finish/build_candidate.py`. The source coordinate frame is Z-up and the bird faces −Y. The six empty nodes remain available for native editing, orbiting, GLB export and pose inspection.

| Pivot | Native rest origin (X, Y, Z) | Rigid children |
| --- | --- | --- |
| Ground | 0, 0, 0 | Legs, ankles, foot and talon assemblies |
| Stand | 0, 0, 0 | Pedestal, base, bolt and mounting eyes |
| Saddle | .025, −.438, .808 | Supported shoe, sleeve and cheeks |
| Torso | 0, .105, .865 | Breast, back, mantle and folded wings |
| Neck | 0, −.105, 1.300 | Assorted cervical parts |
| Head | 0, −.18937, 1.54059 | Cranial shell, bill, cheek, optics and crest |

The hinge and bearing locations are authored staging choices. Only the saddle moves on the stand. The four driven empties share an NLA track named `First Choice`. Export Blender's NLA tracks as glTF animations to obtain one clip. It lasts 10.5 seconds at 24 fps. The default scene pose is the first frame.

| Time | Event |
| --- | --- |
| 0–1.50 s | Seated, feet planted |
| After 1.50 s | Saddle gives around the fixed bolt |
| After 1.83 s | Torso rolls back from the loaded shoe, neck counters briefly |
| After 4.08 s | Head dips and turns toward the near mounting bolt |
| 6.90–8.04 s | Attention holds |
| 8.04–10.50 s | Head rises, shoe reseats and original pose returns |

The eight-second September 8 controlled study informed the initial timing. The recovery tail is newly authored so the local exhibit can return to rest. The story describes the adjustment before the next instruction, followed by inspection of the mounting bolt. The scene adds no operator cue. Neither a scoped film approval nor the mechanical plausibility of this visible motion establishes approval of the 3D character or physical construction.

The liner is fitted to the candidate's ventral keel using local underside samples and a seated profile. The fixed base lies in front of the feet. The derived model uses native formed parts and its own generic workshop-fixture materials. The historical opening, clip and visual references stay outside the runtime export.

`check_clearance.py` rebuilds the three edited regions and measures the moving liner against the ventral shell in native coordinates. `check_roundtrip.py` compares the six joint transforms of a supplied GLB with the native pose, then samples two local direction markers per joint. Use the scripts with Blender background mode. Both resolve their support files relative to this source directory; the clearance report is written beside the script.

## Frozen source and measured liner clearance

The motion module SHA-256 is `ed8c9121fef9d27b16f38ccb21f8ce214b070d859069524437bfdce362274a39`. The September 8 motion report and story excerpt supplied the action order. The scoped September 6 opening and September 8 clip were locally verified at SHA-256 `c12874d1898dbee7617df22acaf39165b4453c5a9282091274c37ad6070ad5f6` and `635f0e1552bac61699c03c8406157207f6230ea817bb1ecaeb3adbb3a7bf8613`. The artist inspected clip frames 0, 48, 96 and 160 and the complete opening composition.

The full nested-breast build was sampled at 965 positions on the evaluated liner surface for each of 253 frames. All 244,145 vertical rays reached the ventral shell with nonnegative separation. Measurements in native scene millimetres are listed as minimum, median and maximum. Local relief follows the unequal thickness of the three-dimensional shell hems.

| Pose | Minimum | Median | Maximum |
| --- | ---: | ---: | ---: |
| Seated, frame 0 | 0.60 | 0.77 | 4.28 |
| Initial give, frame 54 | 25.41 | 31.81 | 38.96 |
| Weight transfer, frame 73 | 32.43 | 38.45 | 44.48 |
| Bolt inspection, frame 155 | 30.09 | 36.37 | 42.48 |
| Reseated, frame 252 | 0.60 | 0.77 | 4.28 |

The check covers the sampled ventral shell/shoe interface. Small fit relief remains visible between the extremes of the cast surface. Animating these rigid groups conveys the story beat and does not simulate contact forces or demonstrate hidden-joint fit.
