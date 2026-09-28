# Independent review: V5 regional candidate 04

**Assessment: visually promising regional transfer; final likeness remains revision-required.** Candidate04 combines guard-study06 and talon-study03 on the V5 sixth base. This review covers fixed-camera native geometry only.

## Identity and evidence

- Native source: [`candidate-04/murderbird-v5-sixth-guard-talon-study.blend`](../assets/models/uncaged-alignment-v5-regional/candidate-04/murderbird-v5-sixth-guard-talon-study.blend), SHA-256 `376718193b9859cf7e454a0e148dde420c74061e6cdfbec7dd84ae6a4d3c960b`.
- Runtime GLB: [`candidate-04/murderbird-v5-sixth-guard-talon-study.glb`](../assets/models/uncaged-alignment-v5-regional/candidate-04/murderbird-v5-sixth-guard-talon-study.glb), SHA-256 `829d416a9eb65226543ce619ffc37ce8f135f3f8869ffb291b65da2a5c664c67`.
- Composition manifest: [`candidate-04/manifest.json`](../assets/models/uncaged-alignment-v5-regional/candidate-04/manifest.json), SHA-256 `321fd2e01420e9fc06132822badedb79d2c6b0d27e26da0b8919ed434e4dc9ed`.
- Base: V5 sixth GLB SHA-256 `1e7febcc03d9f8d1a644580c8422b124403cf4e5768aa01df747e3d9b6af9f1e`.
- Five base/candidate image pairs were inspected: `full-three-quarter`, `full-side`, `limbs-front`, `limbs-three-quarter`, and `feet-three-quarter`. Candidate render receipts are under [`candidate04/native-builder`](../assets/audit/alignment-v5-regional/candidate04/native-builder/), with corresponding `native-maker` and `native-mechanic` views. The base and candidate use the same renderer SHA (`88615d68b2f8fc753e5771cfeeb94295d5f5c12771d0eded464cb720b7edee0b`), camera locations, targets, and orthographic scales for these views. The separate Maker feet close-up and raised-foot images are vocabulary references, not camera-matched measurements.
- The direct GLB parity receipt is [`regional-export-parity-829d416a9eb6.json`](../assets/audit/alignment-v5-regional/export-parity-candidate04/regional-export-parity-829d416a9eb6.json). It passes 90/90 owner-era-region-role-material groups, 230,900 triangles and 116,693 unique world positions on both sides, all runtime meshes classified, and all 51 pivot world matrices unchanged (maximum component delta 0).

For the talon-specific refinement check, the candidate02 and candidate04 `feet-three-quarter.png` views share camera location `[-4,-6,1.1]`, target `[0,-0.17,0.16]`, orthographic scale `1.0`, and the same renderer. Candidate02's inspected image SHA-256 is `e77abd331617d45191def629e740e62fcbd8a57b46c0ad1ef58d940a5d237f01`; candidate04's is `6a26351d641fb87e4d7b555246502fd03bea6a4907013b64ab2dc085ef988447`. Their native/GLB identities are candidate02 `919c924055e35431cd3b2d7019349399e048b9d784c173a59c5066ee1f192702` / `8f8ec3290eba430d17af0f2f50fe24fa3ba318e783869d0e8ad08dcf87d7f1ee`, and candidate04 as listed above.

## Visual findings

The thigh and shin guards read more clearly as shaped overlapping armor than the base's largely cylindrical sleeves. The front and three-quarter views show tapered plate faces with the knee bearings left visible; the lower-leg edges now follow the limb instead of reading as a simple tube. The smooth instep cover is more restrained than the earlier visibly corrugated version, and its overall crown better approaches the Maker shell reference.

The feet remain the least resolved part. A direct same-camera comparison of candidate02 and candidate04 shows a visibly flatter dorsal contour on the six edited distal talon sheaths. The conspicuous rounded masses at their roots are the adjacent proximal digit links and knuckles, which this study intentionally leaves unchanged; flattening the six edited sheaths again would target the wrong region. The distal sheaths still transition from those rounded joints into relatively narrow shanks before their hooks, while the Maker reference has broader, flatter blade forms with a more continuous sweep. The foot-to-claw assembly therefore remains visually unresolved even though the edited distal surfaces have improved.

At whole-body scale, the guard revisions preserve the existing stance and body envelope. Their contribution is clearest in the close limb views and less prominent in the full-side view. I saw no obvious bilateral mismatch in the inspected neutral renders, but these images do not test posed deformation or contact.

## Transfer boundary

Candidate04 is a scoped source study, not an integration into the later head/neck candidate. Its transfer recipe names the exact 26 guard-study06 replacement surfaces, the ten new guard meshes, and six talon-study03 meshes; it retains the original rig/pivot contract. The direct GLB parity result supports that source/export mapping for this candidate only. It does not establish that a future head/neck composition has passed.

This is not final likeness approval, dimensional validation, collision clearance, mechanical certification, browser/runtime approval, or human acceptance. The candidate is worth preserving for a separately validated head/neck integration, with another focused foot-to-claw shape pass recommended.
