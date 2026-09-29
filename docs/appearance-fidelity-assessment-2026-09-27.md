# MurderBird appearance fidelity — exterior assessment

September 27, 2026 · Assessment and production direction · Artistic acceptance remains open.

[Visual comparison](../artifacts/appearance-fidelity-2026-09-27/index.html) · [Evidence manifest](../artifacts/appearance-fidelity-2026-09-27/evidence.json) · [Timestamped video evidence](../artifacts/appearance-fidelity-2026-09-27/video-evidence/video-evidence-manifest.json)

## Assessment

The published exterior does not yet resemble the reference closely enough. It reads as a simplified mechanical assembly because too much of its appearance comes from a small set of broad shells, tubes, rings and repeated plates. The references resolve those same regions into a dense, coherent creature: curved armor, overlapping plate families, recessed mechanisms, substantial edge profiles and distinct metal surfaces. This is an artistic assessment supported by the comparisons below, not a numerical likeness measurement.

The owner's description of a skeleton missing its flesh and skin is apt as a production metaphor. For this mechanical character, the missing “flesh” is the shaped volume and layered construction around the working frame; the “skin” is its fitted metal exterior, local surface history and response to light. Biological flesh, feathers or a rubber covering would change the character. Simply hiding every mechanism would also lose the reference: its legs, cheek and shoulder intentionally reveal machinery, but with more integrated shape, depth and detail.

**Recommendation: build one convincing Advanced head, neck and shoulder exterior proof before multiplying surface work across the whole bird and three eras.** Use explicit, editable profile curves and region-specific control meshes. Keep procedural tools for repeatable placement, export and validation; do not ask another uniform plate generator to supply the character design.

## Which model this assessment concerns

| Evidence | Identity and limit |
| --- | --- |
| Public review | [Published gallery](https://okhp3.github.io/murderbird-uncaged/review/) inspected live. Page names publication revision `4b1c726f5d9bbd1ba1048f89049a5b422001c506`, while its comparison images and recording preserve exterior checkpoint `5016f7573319a9152f3592e1019ca5e556e52056`. These are different identities. |
| Published exterior source | `assets/models/uncaged-exterior-v1/murderbird-exterior-v1.glb`; SHA-256 `3ec668b0b9bbaf1cb546ec2e04b09030c5f45b0f0893adc5b7fe5aa57baacdc5`. Selected live-gallery media are checked against the publication manifest in this assessment's receipt. |
| Parallel structural candidate | Read-only comparison of neutral-v2 captures from `/Users/okh/.codex/worktrees/uncaged-production/murderbird-uncaged`, observed at `3e3bcc03dbf7635e06cc805cfcd29d31c2aabdc7`. Selected PNGs are preserved byte-for-byte in this assessment's `evidence/` directory. They are a local clay study, not the public gallery or a finished material pass. |
| Source authority | [Creative authority](creative-authority.md): candidate 03 for visible full-body identity; July reference for the head only; Maker-clean and Mechanic for scoped era appearance. Hidden surfaces and exact dimensions remain reconstructions. |

The newer neutral study improves breast/neck continuity, crown coverage, bill curvature and toe form. It should receive credit for those changes. Its white clay is intentional and cannot be scored as a failed final material. It still shows a large open cheek, a rail-like mandible, uniform plate courses and sparsely described leg surfaces. Its increased coverage does not by itself establish likeness.

## What creates the skeletal appearance

| Region | Firsthand visual finding | Exterior correction and success evidence |
| --- | --- | --- |
| Head and bill | Exterior-v1 has a smooth helmet, broad wedge bill and flat amber optic. Neutral-v2 improves the hook but still reads as a long curved bill mounted ahead of an optic cylinder; the cheek has a large through-opening and the lower jaw reads as a round rail. | Shape the convex bill root, brow, layered cheek and lower cutting profile together. Preserve the intentional mouth opening but bound it with substantial shaped parts. Recess the optic behind several distinct concentric surfaces. Sweep crown plates back from the brow. Compare the selected July head and candidate 03 at corresponding side/three-quarter views. |
| Neck | Large gaps, pipes and a collar interrupt the exterior-v1 head-to-breast contour. Neutral-v2 fills it with similarly sized scallops. | Build an overlapping cervical envelope with different throat, side and nape plates. It must retain the curve and deliberate mechanical windows, rather than becoming a seamless tube. Check the supplied head-turn extrema without moving the pivots. |
| Breast and belly | Exterior-v1's near-spherical trunk and a few horizontal bands dominate its identity. Neutral-v2 is closer in volume but rows still read as tiling. | Agree the exterior envelope with the structural work, then author broad curved breast plates that narrow, change orientation and transition into smaller lateral/ventral pieces. Do not swell every region; silhouette and taper matter more than blanket bulk. |
| Shoulder and folded wing | Separate shoulder/forewing bulges and conspicuous bearing windows divide the bird into parts. Reference mantle plates wrap into a compact, layered, flightless shield. | Establish a continuous resting contour across independently attached pieces. Use shorter shoulder coverts, a shaped cap, and longer tapered outer shield plates. Keep the elbow seam and motion clearance, with backing visible through only the intended openings. |
| Legs and feet | Long cylindrical members, drum joints and isolated toe-top panels resemble an exposed rig. The reference also exposes legs, but uses nested collars, shaped rails, fittings, segment armor and strong talon roots. | Shape nonfunctional exterior casing around the existing load-bearing members. Give ankle-to-toe transitions nested segments and differentiated talon sheaths. Avoid solid boots that erase machinery or hide weak proportions. Leave joint count, axes and contact trajectories to the parallel thread. |
| Surface history | Large uniform green-gray surfaces with sparse fasteners lack the reference's dark recesses, warm worn edges, broken patina and distinct replacement metal. | Author surface fields from actual plate boundaries, sheltered cavities and contact paths. Separate base metal, patina, polished wear, iron repairs and optics. Variation should explain construction and history, not add random noise. |

### A hierarchy of detail is missing

At thumbnail size, the head profile, neck curve, deep breast, mantle and foot stance must identify the bird. At ordinary viewing distance, plate overlap, edge thickness, cheek construction and joint housings must describe how it is made. Close inspection then reveals fastener seats, tool marks, pits and wear. The current asset has some tiny rivets while the larger identifying shapes remain simplified. Increasing small detail first spends resources without repairing that hierarchy.

The same simplification is visible in the Blender authoring render and the browser close-ups. Lighting contributes to presentation, but cannot explain or repair the entire gap.

## Technical findings: where resolution really matters

Direct GLB inspection and source review establish:

- The combined exterior contains **187,957 triangles across three variants**; the Advanced export contains **63,815**. The combined GLB has seven embedded 1024×1024 images and 22 materials. It is not an untextured wireframe, and total triangle count is not a likeness score.
- Each texture atlas is a 4×4 grid. A region or role reuses a **256×256 tile**, with object-normalized projection rather than an authored unique body unwrap. Detail scale varies between differently sized objects. Seven 1K files therefore do not imply seven unique 1K body regions.
- The normal map is procedural hammer/grain relief shared across roles. Deposit and polished-edge masks follow tile position, not the actual cavity/curvature of the assembled exterior. The code calls this a proposal, and the surface document acknowledges the limitation.
- The current ORM red channel is constant 1; exported materials have no `occlusionTexture`. This means there is no baked texture occlusion, not that all rendered shadows or occlusion are absent. Local cavity shading could help separation; it cannot supply missing geometry.
- Environment lighting already exists: RoomEnvironment plus hemisphere, key and fill. Software rendering can lower pixel ratio to 0.65, which may soften a browser image; it does not explain the same weak forms in the authoring render.
- Source leg guards intentionally cover only about 128–135 degrees, with flat-shaded segments; shoulder/elbow windows are also intentional. Some of the skeleton effect is a design choice made to expose construction.

Evidence: [surface pipeline](exterior-surface-pipeline.md); [atlas, materials and UV generator](../scripts/build-uncaged-exterior-v1.py), lines 60–143 and 185–192; [body generation](../scripts/exterior-body-regions.py), lines 403–458, 504–567 and 623–643; [head generation](../scripts/exterior-head-neck.py), lines 90–179; [browser lighting](../src/scene/presence-exhibit.js), lines 17–59. Exact inspected file hashes are in the receipt.

For a future bake, use shaped high-detail source geometry for major plates and bake smaller relief to a deliberate UV layout. glTF supports tangent normals, metallic/roughness and a separate occlusion input; the latter reads the red channel. Blender supports selected-to-active baking. Those capabilities fit the existing pipeline. [glTF material specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#materials), [Blender baking manual](https://docs.blender.org/manual/en/latest/render/cycles/baking.html).

Proposed material rules: keep silhouette edges and hero overlap thickness in geometry; bake subpixel relief; use local occlusion for fixed details rather than baking an articulated joint permanently shut; keep Maker/Mechanic optics dark; let Advanced lens depth and a restrained emission carry the eye. No new renderer or dependency is needed to begin this work.

Do not multiply every map to 4K. Current recorded limits are 18 MiB combined transfer and 48 MiB estimated decoded textures. First give the face and important plates useful UV area, share appropriate inherited surfaces, and measure the new export. Larger maps require an explicit measured budget decision, not an assumption of better art. The current Mechanic/Advanced aged map generation also offers a possible sharing opportunity; any savings must be measured in the actual export.

## What the videos add—and cannot establish

The packet contains six timestamped frame samples from each of four source clips: controlled First Choice pilot 03, legacy Maker, legacy Mechanic and legacy Heart. The source hashes, duration, sampling method, exact frame timestamps and individual frames are retained in the video manifest. This is a sampled appearance review, not continuous motion acceptance.

Across the inspected samples, the body is visually filled by overlapping shaped plates with dark intervening depth. Crowns, necks, breast and mantle use dense regional construction, while exposed machinery remains locally framed. First Choice's surface language supports the same exterior treatment seen in candidate 03. The selected controlled pilot is a 2D deformation of an opening raster, so it supplies no independent multi-view geometry. Its acceptance applies to that exact silent story-page use; it does not certify model geometry, attacks or a physical mechanism.

The legacy clips remain held/rejected for revised-film continuity. They can support bounded appearance observations, not override scoped selections. Heart's power housing changes in the sampled sequence; visible top/cap differences at 0, 5.5 and 7.958 seconds make copying its evolving internal topology unreliable. Generated stills and videos also do not settle unseen surfaces or form a consistent calibrated multi-view scan. Matching the recognizable, selected visual identity is achievable as a production objective; promising exact agreement with every conflicting frame would be false precision.

## Production order and interface with the parallel thread

| Step | Deliverable | Gate before extending the work |
| --- | --- | --- |
| 1. Reference lock | One feature board naming the authority for bill/brow/cheek, breast, mantle, leg casing and each era. Mark unknown rear and underside areas as reconstruction. | No excluded July body/train cues; no lit early optics; no conflicting video frame silently promoted to master. |
| 2. Hero exterior proof | New versioned Blender collection: Advanced head, neck and near shoulder; explicit control meshes, plate boundaries and a limited material sample. Keep an untouched structural input and existing parent names. | Neutral clay already has the recognizable brow/bill/cheek/crown and flowing neck/shoulder shape. Source-led detail replaces repeated generic patches. |
| 3. Complete regional shell | Breast/pelvis, far mantle, back, legs and feet; deliberate transitions and framed mechanism windows. | Front, side, rear and three-quarter views form one coherent bird. Any required frame/pivot change is returned as an interface issue to the parallel thread. |
| 4. Author surface history | UV layout, high-to-low detail bakes, material families, actual cavity/wear masks, separate lens construction. | Neutral light shows material separation; raking light reveals clean edges and intentional roughness; no tiled patina stripes or generic brushed-plastic response. |
| 5. Derive eras | Maker fabrication, inherited Mechanic aging/repairs, selective Advanced additions on the same identity. | Shared plate landmarks remain traceable. Repair chronology, heart/processing separation and era eligibility survive. |
| 6. Integrate and judge | Versioned GLB, updated model-derived fallback stills, matched source views, full turntable and representative supplied poses. | Likeness judgment plus asset/build/browser checks. Performance and deployment remain separate evidence. |

Appearance owns the surface envelope, plate layout, nonfunctional visible detailing, UVs, materials and appearance lighting. The parallel physiology/mechanics/kinesiology work owns structural proportions, articulation, drives, contacts and motion. The shared interface is a versioned structural baseline plus named rigid parents, pivots, exclusion/clearance envelopes, access-cover transforms and exact sampled poses. Exterior volume changes that demand different pivots must be identified explicitly rather than concealed in surface code.

It is useful to design the desired exterior silhouette now and test it against that interface. It is wasteful to finish every surface on geometry that is still being changed. The hero proof can establish visual quality while the frame is refined. Its eventual integration remains contingent on the verified pose/clearance envelope.

## Appearance acceptance

These are proposed review gates, not passed tests or replacements for the existing evaluation PRD:

1. **Recognition:** a plain clay thumbnail retains the selected bill/brow/crown, neck curve, breast depth and compact mantle. No texture or orange eye is needed to recognize the intended silhouette.
2. **Face:** a close-up has a constructed cheek/mandible and recessed optic; the bill appears integrated with the head. Compare visible reference landmarks from the same side. Do not demand an exact pixel overlay before camera/perspective alignment.
3. **Plate hierarchy:** crown, throat, breast, shoulder and folded wing have distinct plate shapes, scales and directions. No single scallop template dominates all regions.
4. **Depth:** major plate edges, seams and permanent recesses survive neutral light and camera rotation. Intentional negative spaces remain readable; accidental through-holes do not.
5. **Materials:** bronze/blackened frame/repair metal/working edges/lens can be distinguished in neutral light and under a moving highlight. Wear follows the construction. Cinematic darkness cannot be the only convincing view.
6. **Continuity:** turntable and supplied extreme poses preserve the exterior; overlaps do not visibly detach or expose unintended voids. Inspection closes back onto the same silhouette. The parallel thread validates the actual movement contract.
7. **Browser parity:** the exported Three.js model retains the authoring likeness and material response. Test real WebGL and model-derived fallback separately, and record actual image/canvas dimensions before diagnosing resolution.

Human artistic acceptance is still required. Counts, hashes and passing software tests certify their stated mechanics, never likeness.

## Scope and validation of this assessment

Created only this document and `artifacts/appearance-fidelity-2026-09-27/`: visual comparison, selected read-only evidence copies, frame samples and receipts. No model, runtime source, animation, source art, story, music, private archive, existing handoff or parallel worktree was edited. No commit, push, deployment or Replit publication is part of this assessment.

Validation results are recorded in the packet's `validation.json`: reference and local-link integrity, source hash preservation, selected public-media identity, report browser review, and build/output boundary checks. Checks of a future model, fresh exhibit WebGL/fallback behavior, continuous motion, device performance and final artistic acceptance are **NOT RUN** here. The next production unit is the head/neck/shoulder exterior proof described above, not a claim that this assessment has changed the model.

All MurderBird creative content remains all rights reserved under [NOTICE.md](../NOTICE.md). These local evidence derivatives are not added to `public/` or the release selection.
