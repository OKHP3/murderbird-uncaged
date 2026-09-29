# V36 Form01 — useful face study, failed foot fit

The owner's likeness criticism remains valid. V36 improves the visible bill construction and opens a mechanical bay behind the optic. Its shorter feet look more compact at rest, but independent movement review found new toe-guard and ankle intersections. **V36 Form01 is rejected as an integrated correction. It is preserved for assessment and is not selected as the development default.** Three finished era exteriors and whole-character artistic acceptance remain incomplete.

[Reference / V35 / V36 comparison](../assets/audit/whole-character-v36/comparison.html) · [Interactive rejected study](../assets/audit/whole-character-v36/index.html) · [Regional construction record](whole-character-v36-construction-map.md).

The local full exhibit is `http://127.0.0.1:5183/?review-body=v36-form01`. The development default now points to V35, replacing the stale V32 selection; that remains an unapproved study. Production stays V9. Nothing in this correction has been pushed or deployed.

## Visible work and disposition

| Region | Actual change | Decision |
| --- | --- | --- |
| Face | Formed bill planes with real divisions, a faceted optic surround, open temporal bay showing inherited passive fittings, and a connected receiving yoke. Jaw lip, hinge and cervical seat remain. | Retain as a regional proposal. Broad goggle-like housing, blunt frontal bill and long rear leaves still differ from the references. Not owner accepted. |
| Feet | Fore-aft envelope shortened 21.58%; width and height unchanged. Six distal axes moved toward their proximal axes; 52 links, guards, talons and foot meshes revised. Bearing local geometry retained. | **Fit failed:** shifted distal hinges cross proximal guards. Raising the arch introduces landing interference with the shin receivers. Rest-shape improvement does not justify integration. |
| Shoulder | Separate receiver and sideguard trial tried to connect the shoulder to the torso. | **Rejected and excluded.** It introduced strict crossings in all four checked states. Next work must reconcile housing, receiver and outer envelope together. |
| Remaining body | V35 torso, neck, shoulders, leg housings and compact rear retained. | The shoulder mantle, breast/pelvis transition, lower-limb density and rear construction remain major likeness gaps. |

The reference is a perspective image. Model reductions are authored measurements, not recovered historical dimensions. The new Cycles neutral comparison uses identical camera, scale and white lighting for V35 and V36; material overrides exist only in the render session. Original native files are unchanged. Front, side, rear, three-quarter and neck Workbench views are also preserved.

## Exact preserved model

Workspace: `/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged`. Parent commit: `46c7c8a3be0264d3667616b3c685154def70a402`.

- [Editable Blender source](../assets/models/whole-character-v36/attempt-form01/murderbird-whole-character-v36.blend): SHA-256 `9b0072375fee116864954e882f5ed8ec023cf8d400783fb96947ce4c57bf151f`, 3,847,500 bytes.
- [Runtime GLB](../assets/models/whole-character-v36/attempt-form01/murderbird-whole-character-v36.glb): SHA-256 `565396fa9c43fb258821a8b18151b03032dd61ecfc004c59e39f5dffc3046263`, 13,928,164 bytes; 685 mesh objects, 54 rigid nodes, 543,388 triangles, eight exported materials.
- [Composition receipt](../assets/audit/whole-character-v36/attempt-form01/receipt.json): 58 existing meshes changed, 16 added, 12 superseded only in this derivative. Eight node translations change: six distal digits and two bill contact markers recalculated from actual geometry. All 46 other node rests, parents, unit bases and materials remain exact. Native save/reopen and finite-geometry checks pass.

Face final03 and compact feet attempt02 are the only composed regions. The failed shoulder study, face attempts01/02 and foot attempt01 remain preserved separately. No earlier source was overwritten. Later foot fit trials, if present, are separate regional studies and do not alter this model or its verdict.

## Validation results and limits

**FAIL — changed foot clearance.** The [independent screen](../assets/audit/whole-character-v36/attempt-form01/foot-motion-screen/summary.json) uses fresh actual-GLB matrices for each model and the same triangle-crossing kernel. New pair identities compared with V35 are:

| State | Between moving owners | Within one owner | Total introduced |
| --- | ---: | ---: | ---: |
| Rest | 4 | 6 | 10 |
| Claw scrape | 3 | 6 | 9 |
| Jump landing | 9 | 6 | 15 |

[Exact witnesses](../assets/audit/whole-character-v36/attempt-form01/foot-motion-screen/strict-foot-motion-screen.json) and [cause attribution](../assets/audit/whole-character-v36/attempt-form01/foot-motion-screen/cause-attribution.json) isolate the raised arch as the landing regression: V35 and V36 foot/shin matrices are identical in that pose. All 52 changed meshes are finite and closed, but that does not make their fit acceptable. Counts are intersecting pair identities, not penetration depth or independent defect counts. Three discrete states do not establish continuous clearance.

**FAIL — excluded shoulder trial.** The separate [four-state screen](../assets/audit/whole-character-v36/regional-studies/shoulder-receivers/attempt-02/shoulder-clearance/screen.json) reports 7 / 7 / 6 / 5 introduced pairs against a zero-pair V35 baseline in that bounded scope.

**PASS — bounded face construction.** Final03 retains the exact V35 temporal leaves after shortened replacements introduced eight same-owner crossings. The preserved face records report zero strict pairs in five jaw/two cap samples, seven neck states and 91 temporal rest pairs. This regional evidence transfers through the disjoint composition; it is not a fresh full-body clearance or art pass.

**PASS — export and attachments.** [Actual GLTFLoader roundtrip](../assets/audit/whole-character-v36/attempt-form01/export/actual-runtime-roundtrip/roundtrip-receipt.json) preserves all 739 native world matrices within 2.99e-8. [Full-era integration](../assets/audit/whole-character-v36/attempt-form01/era-integration/integration.json) checks 66 samples with no attachment failures or fit-risk flags, including five Maker controls, Mechanic movement, Advanced jump/thrust, inspection and era switching. The [source motion harness](../assets/audit/whole-character-v36/attempt-form01/motion/motion-validation.json) records nine passes and one procedural-tail partial; the full-era check covers that tail separately. These tests do not supersede the failed triangle-clearance screen. Motion is kinematic, not physical simulation.

**PASS — browser function.** Actual [jump](../assets/audit/whole-character-v36/attempt-form01/browser/advanced-jump.webm) and [thrust](../assets/audit/whole-character-v36/attempt-form01/browser/advanced-thrust.webm) recordings, state traces, era stills and extracted frames are preserved. The jump is a short vertical hop, not a traveling leap. Opening, separation and jaw movement restore all 740 loaded objects with zero transform drift and no missing objects in the [reassembly check](../assets/audit/whole-character-v36/attempt-form01/browser/inspection-reassembly.json). This checks identity and restoration, not all open-state intersections.

The full exhibit's deliberately retained V9 illustrated fallback appeared after forced context loss; Retry 3D restored the V36 GLB. The isolated review displays its actual V36 still and reload restores WebGL. The fallback is not presented as a render of the new candidate in the full exhibit.

**PASS — build boundary.** `npm ci`, `npm run build`, both publication-boundary tests and the full publication verifier passed. The [build receipt](../assets/audit/whole-character-v36/build/receipt.json) verifies all output hashes/lengths: 133 payload files, 134 including the manifest. V36/V35 source models, candidates, audits and private material are absent from the distribution. Existing optional fsevents and large-bundle notices remain. No remote CI or deployment is claimed.

The [performance sample](../assets/audit/whole-character-v36/attempt-form01/browser/performance.json) is a short 180-frame paused Advanced view at 856 × 648, pixel ratio 1, Apple M4 Max / ANGLE Metal: median 10 ms and 95th percentile 10.1 ms, 1,446 draw calls and 1,090,052 rendered triangles. It does not establish mobile, sustained motion or thermal performance. An earlier sample taken across a development reload is preserved as `performance-transition-trial.json` and excluded from that claim. Recorded video duration differs slightly from trace duration; extracted frames are illustrations, not timing metrology.

## Next bounded work and owner decisions

One foot fit revision may retain the compact footprint while restoring the unnecessary arch lift and shaping the guards around actual unchanged bearings. It must pass the same independent screen before another combined export is selected. Further shoulder work must change the whole receiving construction, not extend armor into unchanged oversized hardware.

Likeness work remains focused on the head's constructed profile, compact integrated shoulder mantle, breast-to-pelvis relationship, dense mechanical lower limbs and coherent rear. Finishing materials remains premature. The earlier bill/jaw direction question is still unanswered; no approval is inferred and no repeated prompt is needed to address these evident defects. Agent checks remain separate from owner artistic acceptance.
