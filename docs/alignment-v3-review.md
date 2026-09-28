# MurderBird alignment v3 — geometry and articulation review

**A new local candidate is implemented; final likeness remains revision-required.** The owner authorized the next geometry and kinesiological alignment pass after Stage B, retaining the body/neck/mantle proportions provisionally. This pass supplies new editable geometry, corrects concrete joint/contact defects and preserves the v2 review. It does not claim perfect alignment, physical simulation, final surfaces, a full PRD score or publication.

## Exact candidate

- Worktree: `/Users/okh/.codex/worktrees/uncaged-production/murderbird-uncaged`.
- Branch: `codex/neutral-correction-v2`; implementation begins at `3e3bcc03dbf7635e06cc805cfcd29d31c2aabdc7`.
- [Runtime GLB](../assets/models/uncaged-alignment-v3/murderbird-alignment-v3.glb): **3,370,292 bytes**, SHA-256 **`c4dc308f77399410368b82443a1b21b9113cfedb258aa055906b4f13c92dda21`**.
- [Editable Blender source](../assets/models/uncaged-alignment-v3/murderbird-alignment-v3.blend): **2,577,802 bytes**, SHA-256 **`6de7c16728ac2ac4926b9b0bd608d7eb5e03f702d3e1ef222db997c84fd7ff3a`**.
- **539 editable mesh pieces, 115 profile/cross-section curves, 157 exported nodes, 163,129 exported triangles** before runtime mechanisms and shadows.
- [Inventory and profile coordinates](../assets/models/uncaged-alignment-v3/alignment-inventory.json), [editing guide](../assets/models/uncaged-alignment-v3/README.md), [independent visual critique](alignment-v3-independent-review.md).
- [Local gallery](http://127.0.0.1:5177/assets/audit/alignment-v3/alignment-review.html), [local WebGL exhibit](http://127.0.0.1:5177/), built preview on `http://127.0.0.1:4177/`. These are loopback previews, not deployed URLs.

## Geometry changes

The generator opens the preserved v2 Blender source instead of reconstructing the rig from an earlier generic model. The new version contains explicit profile boundaries and cross-sections, neutral materials and separately owned rigid meshes. Native curves document the construction inputs; they are not live modifiers that automatically regenerate geometry after manual editing.

| Region | Implemented change | Remaining review issue |
| --- | --- | --- |
| Cheek, optic and bill root | Continuous irregular socket surround, a descending cheek arm, recessed optic housing and shaped cere transitions replace the floating ring and small bridge. | The flat cheek arm and cap-to-bill transition still differ from the illustrated construction. |
| Mandible and bill | A curved crescent mandible and shaped lower keel replace the thin fork. Its journal is concentric with the actual jaw pivot. The upper bill has independently authored dorsal/cutting profiles and breadth sections. | Cheek opening, lower-jaw contour and regional mass still need owner likeness judgment. |
| Crown and neck | Closed roof pieces, segmented brow and swept laminae with exposed-edge relief; fuller lateral/rear-quarter cervical guards. | Crown rows, cap gaps and exposed neck structure remain visibly more regular/coarse than the sources. |
| Breast and mantle | A narrow central breast field and staggered lateral subfields, variable overlap, profiled folded mantle backing and a shoulder-to-distal plate hierarchy. | Horizontal plate rhythm, smooth gutters and the rounded mantle envelope remain open likeness findings. |
| Legs and feet | Crowned, tapered channels with returned flanges, smaller coaxial bearings, a curved instep and individually owned digit covers. | Joint drums and talon bases remain coarse. Separate digits are not proof of a purposeful supported grip. |

All three era configurations use this inherited neutral structure. The existing runtime supplies era-specific external controls, transmission or Advanced systems. The native file does not claim to contain those runtime-generated mechanisms. Source illustrations remain unwarped; the July reference controls the head only, and unseen construction remains proposed.

## Kinematic defects corrected

1. **Reversed jaw opening.** The prior negative-X rotation lifted a forward jaw vertex toward the upper bill. Positive-X rotation now opens the jaw downward about the actual transverse pivot. Maker's maximum is 0.32 radians. The runtime and its geometric assertions now agree on that direction.
2. **Jaw shear from inherited scale.** V2's head scale was `(1,1,1.2)` in Blender. Rotating its child jaw beneath that nonuniform scale changed world-space lengths and angles. The new native source bakes the scale into descendant rest offsets and vertex coordinates. All rest world joint centres are preserved, and the recorded vertex-bake error is zero at the script's precision. Exported node scales are unity; 33 jaw-angle samples check unit, orthogonal world bases.
3. **Knee rotation outside its hinge axis.** The old shortest-arc solve introduced sideways shin rotation. The new solver retains the actual exported link offsets and constrains each knee to local X while the hip orients the chain. Supported feet retain their world-space targets.
4. **Inactive digits.** All twelve proximal/distal digit hinges now flex during raised steps, with flexion limited by actual foot elevation. Planting restores each recorded rest rotation exactly. Low Mechanic steps receive less flexion than higher Advanced steps.
5. **Contact approach tied to older bill dimensions.** The new bill was approximately 14 mm short of the rail at the old approach goal. The runtime now calibrates the approach from the loaded upper-bill triangle surface and bounded cervical articulation. The contact solve keeps neck/skull translations fixed and uses the selected vertical rail; the gold attention ring is not the contact target.

The [kinematic receipt](../assets/audit/alignment-v3/kinematic-validation-receipt.json) binds the model, controller/solver source hashes and individual reports. The [jaw sweep](../assets/audit/alignment-v3/jaw-sweep.json) samples 33 poses against fixed cheek, bill and crown triangles, excluding the stated coaxial bearing envelope. It detects proper triangle crossings only: it is not a continuous, containment, coplanar-contact or whole-body collision certificate.

## Verification

| Check | Result and scope |
| --- | --- |
| Dependencies and build | `npm ci` and `npm run build` pass with the existing lockfile. No dependency added. Vite retains its large Three.js chunk warning; npm reports an unapproved optional `fsevents` install script. |
| Unit tests | **44/44 pass**, including transverse hinge geometry and model-derived approach feedback. |
| Asset integrity | Native/runtime/previews match inventory; all v2 generated hashes remain unchanged; 13 distinct source/provenance paths, including the v2 source, exist and match hashes. Rigid ownership, unit scales, finite geometry and era exclusions pass. |
| Kinematic alignment | **4/4** actual-model checks: downward jaw movement, rigid world bases, raised-foot/digit recovery, bilateral planted support. |
| Era/structural/power/mechanisms | **14/14**, **4/4**, **4/4**, **7/7** respectively on the exact current GLB. These are each script's declared sample bounds. |
| Jaw sweep | No proper crossings detected in **33** sampled angles outside the documented journal exclusion; other collision questions remain open. |
| Headed browser | **7/7 grouped checks**, **101 captures**, current served-model hash verified, three eras, desktop/narrow controls, keyboard samples, inspection and all three illustrated fallback hashes. No recorded app errors. |
| Build boundary | Actual emitted paths and hashes pass the active publication-boundary validator. **134 files** were observed, not made an acceptance constant. Native sources, profile curves, provenance, v3 comparison evidence and private archives are not copied into `dist/`. The historical allowlisted assessment gallery remains historical. |

Browser environment: Chromium 151.0.7922.34, native Apple M4 Max/ANGLE Metal, loopback without network throttling, analytics stubbed. Desktop viewport is 1440×1000 and the narrow viewport is 390×844. Layout receipts now include viewer bounds and scroll position. Short rolling performance samples do not establish sustained desktop, physical mobile, thermal or constrained-network performance.

[Paused live evidence](../assets/audit/alignment-v3/frozen-extrema.json) contains **six poses, 20 screenshots and 18 keyboard marker activations**. The animation state is frozen before bilateral view changes. Jaw opening, jump, thrust and rail contact are bounded pose samples, not continuous clearance evidence.

The [silent normal-speed demonstration](../assets/audit/alignment-v3/alignment-motion-demonstration.mp4) exercises all five Maker levers, inspection and reassembly, Mechanic traversal/turning/stopping, Advanced pacing, jump, thrust, selected-rail contact/recovery and separate power/processing inspection. Its measured sequence is **115.133 seconds**; both the original WebM and MP4 contain **2,909 frames at 25 fps, 116.36 seconds including setup**. No audio was enabled. The [motion receipt](../assets/audit/alignment-v3/motion-demonstration.json) records the served GLB hash, visible performance-clock events, samples and media hashes. The transcode retains the complete original interval without cuts or resizing. Root inspected selected video frames and live frozen views; this is not complete continuous human acting review. The sequence does not replace the two required fresh 120-second no-input runs.

The recorded application footage retains the older “Neutral structure correction v2” footer. A subsequent copy-only correction changes the current exhibit footer to “Geometry and articulation are under review”; model and motion code are unchanged. The final build and a focused browser check cover that text change. Original footage is preserved unaltered.

## Preservation, scope and remaining acceptance

The reviewed v2 GLB remains `48229ba5…`, and its native source remains `64ea6d86…`; its gallery, receipts, earlier iterations, source artwork, story, audio and videos are unchanged. The intermediate v3 `9a979911…` native/runtime and its evidence are retained under the matching `iterations/rigid-envelope/` directories. The first v3 profile images and contact-failure diagnostics are also retained with their original identities.

Active changes are the new model/evidence trees, geometry/render/capture/validation scripts, the model and fallback imports, `era-motion.js`, `presence-state.js`, the new transverse-leg solver, targeted tests and the current exhibit's review footer. Two existing motion validator assertions change with the corrected jaw sign; their historical receipts remain untouched. The main clone's owner work under `docs/handoffs/` and `artifacts/reviews/` is untouched.

F01–F04 remain open for likeness and comprehensive clearance. F05/F06 finishing remains gated. Digit flexion improves articulation but does not close F07's named supported claw action. F08's distinct action choreography and two complete no-input recordings remain outstanding. The existing PRD definitions and weights are unchanged, including full reference-video, route, interruption/restoration, human accessibility, physical-device, audio and sustained-performance evaluation. V10 chronology and V12 historical motion targeting remain proposed as documented in the preserved source packet.

No push, merge, deployment, Replit publication, new public release, owner likeness acceptance or full passing score is claimed.
