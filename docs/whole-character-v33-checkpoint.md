# V33 Form06 — local construction review proposal

2026-09-29. **Whole-body likeness still fails; no owner acceptance or finished exterior is established.** Form06 refines the neck receivers, orbital construction and swept crown on exact V32 Form01. The V32 bill/mandible direction remains unchanged and its owner decision is pending. These are authored mechanical proposals guided by the owner whole-bird target and the July head-only reference; unmatched reference cameras do not establish dimensions.

Use the [local review page](../assets/audit/whole-character-v33/index.html) and the explicit complete-exhibit route `?review-body=v33-form06`. The local development default remains V32. This checkpoint does not publish, change production selection or claim deployment.

## Three regional changes and inheritance

| Region | Construction and ownership | Frozen executed source SHA-256 |
| --- | --- | --- |
| Neck receiving underlaps | Thirty existing guards on the first three cervical owners are formed inward behind sampled adjacent rigid shells. Two body-fixed thoracic cheeks receive the root pitch/yaw envelope. The fourth course, frame, shafts, four-joint rests and motion law remain exact. The finite receiving walls retain the curved guard direction; this is passive relative movement, not neck stretch or a new actuator. | `de8f3854b3e631be5829505cb51836816e22d9166cf07e7f6cc6e4513b807f18` |
| Orbital/cheek construction | Nine fixed brow/cheek/bearing/hood meshes are replaced by thirty head-owned finite plates: diagonal brow lands, asymmetric lower cheek, a thin retaining lip and staggered throat receiving plates. The actual retained lens, cup, passive floor, eye centre, jaw and bill stay exact. Two stationary cheek bores receive the unchanged rotating jaw axles rather than exempting solid penetration. | `7efee457369d725ef6cf51ef9e07fa4ddd675664ed158963a270beb32912a311` |
| Crown and temporal flow | Thirty-one V32 cap/temporal plates are replaced by twenty-nine opening-cap leaves and fourteen fixed temporal leaves. Shorter staggered aft sweep exposes the retained fittings. Actual seats/separations replace crossing laps; the cap remains independently opening. Final leaves use a **2.5 mm radial-section wall** whose normal thickness varies with local slope. It is not constant normal thickness. | `998eb52afb79fcd0ff19bc9ffaf5bf6eedaf7d910533d7c83edf843e25d643e3` |

All additions are passive inherited construction in Maker, Mechanic and Advanced (`builder`). Existing Advanced-only sensing/processing remains Advanced-only; the earlier-era optic floor remains passive and dark. No new materials, textures, finish, dependencies or era capabilities were introduced. All 54 rigid node records and all 94 foot/toe mesh records remain exact. Body, wings, legs, feet, bill and jaw retain the prior V32 regional scope and limitations.

## Exact Form06 evidence

- [Native source](../assets/models/whole-character-v33/attempt-form06/murderbird-whole-character-v33.blend): SHA-256 `5fdfe66693db848fcf624b28484c3eaba220a8d7f389248390a4f21a571d108d`, 3,333,698 bytes. The [composition receipt](../assets/audit/whole-character-v33/attempt-form06/receipt.json) records 624 finite meshes, exact materials, save/reopen, 54 unchanged nodes and 94 exact foot/toe meshes.
- [GLB derivative](../assets/models/whole-character-v33/attempt-form06/murderbird-whole-character-v33.glb): SHA-256 `7430fd397ad44e066e4f9197b023ba2f0f239451e12cb256ba34de8d9d4148ad`, 12,732,280 bytes. The [export receipt](../assets/audit/whole-character-v33/attempt-form06/export/export-receipt.json) records 624 meshes, 54 rigid owners, 678 nodes, 500,928 triangles and eight materials. Names, parenting, extras, material assignments and finite accessors pass; the native is unchanged. Three authoring curves are excluded, with no exported cameras, lights or animation tracks.
- Fresh exact-native [jaw/cap screen](../assets/audit/whole-character-v33/attempt-form06/head-views/screen.json): zero strict crossings at jaw 0/.08/.16/.24/.32 radians and cap 0/+0.08 m. It dynamically includes all 140 head-subtree meshes.
- Fresh [same-owner leaf screen](../assets/audit/whole-character-v33/attempt-form06/head-views/same-owner-leaf-screen.json): zero strict crossings across 406 distinct crown-leaf pairs and 91 temporal-leaf pairs at rest.
- Fresh [self-triangle screen](../assets/audit/whole-character-v33/attempt-form06/head-views/leaf-self-triangle-screen.json): all 43 crown/temporal meshes have zero strict nonadjacent triangle crossings. Shared-vertex triangle pairs are excluded.

These checks reuse the frozen evaluated edge-through-face kernel: 1e-7 m plane epsilon and 1e-6 edge/barycentric margins. They exclude coplanar, tangent and containment cases and do not establish continuous swept clearance, physical guidance, strength or artistic likeness.

## Preserved failures and remaining gate

Form01's original crown failed the same-owner screen: eighteen crown and two temporal crossing identities. Form05 still had two crown-leaf crossing identities, and all 43 leaf meshes together had **1,789 strict nonadjacent self-crossing triangle pairs**. Their natives, sources, renders and witnesses remain preserved. Passing jaw/cap samples did not make those leaves valid.

Form06 removes the transverse tip bulge and replaces the numerically unstable surface-normal-offset wall construction with a common nested radial section. Its zero same-owner/self counts are fresh Form06 evidence, not reassigned Form05 results. See the [independent composition review](../assets/audit/whole-character-v33/attempt-form06/head-views/composition-review.json) and [closed head](../assets/audit/whole-character-v33/attempt-form06/head-views/closed-head.png).

The face still has a conspicuous round optic on broad plain cheek fields; the crown remains ribbon-like, with a visible under-cap opening. The head front remains dominated by the retained bill triangle, and throat/neck boundaries remain coarse. The full bird is still an unaccepted silhouette and the three finished era exteriors remain incomplete.

## Runtime and browser evidence

The exact Form06 [neck screen](../assets/audit/whole-character-v33/attempt-form06/neck-screen/manifest.json) has zero strict crossings in all seven sampled poses. The corresponding V32 counts were 2/14/2/7/4/1/1. This is a meaningful interference correction, but the visible mechanical opening below the head remains; it is not proof of complete moving coverage.

The actual-GLB [roundtrip](../assets/audit/whole-character-v33/attempt-form06/export/actual-runtime-roundtrip/roundtrip-receipt.json) verifies 624 meshes, 438,213 vertices and 678 world matrices, with maximum matrix difference 2.98e-8. The [motion receipt](../assets/audit/whole-character-v33/attempt-form06/motion/motion-validation.json) records nine passes, zero failures and one explicit procedural-tail exclusion across 5,124 frames and 1,045 geometry samples. The separate [full-era integration](../assets/audit/whole-character-v33/attempt-form06/era-integration/manifest.json) covers the procedural controls and tail: 66 samples, zero alignment failures or declared endpoint-gap flags. All five Maker controls move actual geometry. Advanced-only source machinery remains absent in Maker and Mechanic.

Fresh [browser checks](../assets/audit/whole-character-v33/attempt-form06/browser/browser-check.json) loaded this derivative and exercised six representative motion poses. [Inspection and reset](../assets/audit/whole-character-v33/attempt-form06/browser/inspection-check.json) restore all 679 loaded objects with zero transform difference. These are sampled kinematic and identity checks, not physical simulation or a full-body collision certificate.

The [43-second actual exhibit recording](../assets/audit/whole-character-v33/attempt-form06/browser/full-era-mechanisms.webm) demonstrates five Maker controls, Mechanic stepping, Advanced jump, shield thrust, strike and recovery. Its [timed segment record](../assets/audit/whole-character-v33/attempt-form06/browser/full-era-recording.json) reports no capture failure. [Neutral](../assets/audit/whole-character-v33/attempt-form06/browser/integrated-head-neutral.png) and [exhibit lighting](../assets/audit/whole-character-v33/attempt-form06/browser/integrated-head-exhibit.png) are actual browser captures of the same paused view, not final material renders. The deep pose still exposes the throat support opening.

The local isolated viewer successfully showed the Form06 still after forced context loss and recovered real 3D after reload. The full exhibit's separately checked illustrated fallback deliberately remains **V9**, identified in the route banner; Retry 3D restored Form06. Neither fallback is evidence of WebGL rendering. The pre-fallback full-exhibit warning/error log was empty.

Measured on Apple M4 Max, ANGLE Metal, device pixel ratio 1, visible Codex browser: the full exhibit at a paused Advanced head view with neutral lighting, 856×648 buffer, sampled 180 frames with median 10.0 ms and P95 10.4 ms; 1,085 draw calls and 938,244 triangles. The isolated viewer's closed neutral rest view at 1056×690 sampled 180 frames with median 10.0 ms and P95 11.3 ms; 625 draw calls and 500,928 triangles. These short desktop samples are not mobile or worst-case performance acceptance.

## Local build and next correction

`npm ci`, `npm run build` and both publication-boundary tests completed successfully. The [build receipt](../assets/audit/whole-character-v33/build/receipt.json) verifies all 133 declared payload files against bytes and hashes, with 134 physical files including the manifest. Production still packages V9; no V33 model, native, audit, private archive or source file enters the distribution. The npm optional `fsevents` script notice and large-bundle warning remain recorded. This is a local modified-tree build on parent `e881ed246628b22d85b7713b68b200bd17b54996`; no remote CI or deployment is claimed.

Next, compare and reshape the breast-to-shoulder envelope and the apparent load path from pelvis through legs and feet. The current smooth egg-shaped breast, thin shoulder shield and sparse leg connections still make the body look light beside the owner target. Head/crown mass relative to the body also needs comparison; simply enlarging the already dominant bill would not address it. These are visual judgments from perspective references, not recovered dimensions. Existing pivots are compatibility facts, not approved proportions: move them when a demonstrated silhouette or attachment correction requires it, then revalidate the affected motion.

The pending V32 jaw/bill direction question remains unchanged. No response has been inferred, and no finishing or whole-character artistic acceptance is claimed. Earlier Form05 receipts remain attached to that rejected geometry. The [V32 checkpoint](whole-character-v32-checkpoint.md) records the preceding scope.
