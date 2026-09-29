# V20 proportions02 early shape gate

Status: held for parent visual review. Not frozen for integration or accepted likeness. No GLB export, runtime review, expensive clearance checker, or engineering acceptance.

Pinned input: V19 attempt02 SHA `d98c46770101ad608fe2c50212a7b307ca66d5389f93ce7d43b79b9c7d41dded`.
Candidate native SHA `3bfd8381ef8910382da8642f3d076a62e066988d448d4ddc8556cdd2db897306`.

Actually viewed: owner whole-bird target `context/threads/assets/murderbird-owner-likeness-rejection-2026-09-28/2-Pasted-Image-2.jpg`; retained July head-only reference in earlier study; V19 before and V20 after side, neck, front and reference-angle clay images.

## Causal repair from attempt01

- The first head rise200mm doubled the draft100mm and stretched the cervical-root relationship. Candidate02 uses100mm rise and55mm forward translation. The constructed head meshes retain shape.
- The first mantle compounded body depth .88/.78 with another .78, yielding an undersized shoulder cap. Candidate02 maps the mantle directly: depth1.00, Z.94, rise60mm, radial width1.12, distal-width taper14%. Breast anterior depth becomes1.10 and rear .94; upper shoulder width remains approximately source size.
- The first toe/claw map interpolated every vertex Z through smooth knot intervals with endpoint clamping. That destroyed curved talons. Candidate02 translates the entire toe/phalanx/claw cluster from source toe root to new root, retaining its vertex Z. Toe bearing hardware retains explicit circular journal growth; the claw surfaces retain their shape. Proximal foot thickening uses only the foot owner's local lower-height fade, not toe/claw heights.
- Lower and upper cervical deltas now meet the head translation by sourceZ1.405. The lower guard root rises30mm and the upper throat100mm. Existing finite source courses remain instead of generating a stretched blank tube.

## Candid visual adjudication

The second candidate repairs the method regressions and retains stronger limb journals and sections. It does **not** resolve the main whole-bird recognition problem. The inherited cervical flank skirt still ends as a collar above the breast. The breast remains broad and rounded; mantle silhouette remains a broad plate-covered wedge rather than an exposed folded directional fan anchored at a substantial visible shoulder journal. Repeated small breast plates and thin ladder elements remain visible. These are construction relationships, not material defects.

## Evidence and interface

Eight matched clay images (four before/four after) were rendered. Save/reopen identity, retained52 rigid names/parents, retained744 source mesh identities, unchanged material definitions, and untouched V19 input hash were checked by the builder. All744 source mesh snapshots changed. Historical curves are mapped in the derivative, not asserted exact; historical binaries are retained. Source mesh thickness modifiers remain inherited and need renewed finite-wall and attachment checks after the shape gate.

Frozen executed module: `executed-proportions.py`; composer: `executed-composition.py`; serialized controls and52 old/new world/local matrices: `rig-shape-contract.json`. Public callable `map_point(owner, old_native_world_point)` uses native metres, Z up, negativeY front. `SOURCE_ROOT` may be supplied when loading the exact frozen module for socket metadata derivation. Native to browser point conversion is `(X,Z,-Y)`.

The editable authoring controls are Python profile tables plus native `body.proportionCageV20` JSON and a meridian curve. Geometry is baked as a rigid derivative; this is not an interactive lattice modifier. Bearing radial growth is explicit for limb/mantle joints. Body and cervical bearing surfaces still pass through their regional cage map; their circularity is not proven. No procedural attachment acceptance is claimed.
