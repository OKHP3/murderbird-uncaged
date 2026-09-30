# V38 body and material integration checkpoint

Root integrates the final two-attempt body study with one regional material proposal on `codex/v38-material-contrast-01`. The input geometry checkpoint is `f82bc83b4f92e39649eab1b79cd6471512393ecc`; the integration tree before this note is `7732cbbdea365ab4430020808ab5886323491ad9`. Obtain the final checkpoint SHA from the branch tip after fetching. **This is a development review candidate. V37 remains the production selection; owner likeness acceptance is pending.**

Open the [local review page](../../assets/audit/whole-character-v38/body-finish01/review.html) through the development server, currently `http://127.0.0.1:5185/assets/audit/whole-character-v38/body-finish01/review.html`. It compares V37, the prior dark material study, the regional material study on unchanged V37, and the combined candidate. These comparison controls are development-only; no progression gallery is added to the visitor exhibit.

## Visible result and reference scope

The lower torso now continues more fully into the pelvis. Separate thigh-owned formed channels add load-bearing visual mass without moving the inherited joints. Crown, breast and shoulder plates have separate proposed PBR responses instead of sharing one armor response. Independent review found a visible body gain and a modest material separation gain. The largest remaining gap is mass distribution: the reference's compact, heavy body and fuller legs still contrast with the candidate's smaller plated body above long exposed struts. Smooth shoulder envelopes and simplified head construction also remain unresolved. No third geometry attempt was made in this checkpoint.

Whole-body contour follows the selected September [master candidate](../../assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png) and [owner-resupplied target](../../context/threads/assets/murderbird-owner-likeness-rejection-2026-09-28/2-Pasted-Image-2.jpg). Maker treatment follows the [clean Maker candidate](../../assets/img/library/murderbird-unified-maker-clean-candidate-2026-09-06.png); inherited aged/repair contrast follows the [Mechanic candidate](../../assets/img/library/murderbird-unified-mechanic-candidate-2026-09-06.png); restrained Advanced optic/interior context follows the [heart candidate](../../assets/img/library/murderbird-unified-heart-candidate-2026-09-06.png). The documented July choice controls the head only. This increment changes neither that head geometry nor the flightless wing direction. Perspective images establish visual intent, not exact dimensions or recovered construction. First Choice video and preserved story are unchanged sources, not certification of new geometry or jump behavior.

## Editable source and runtime derivative

| Combined output | SHA-256 |
| --- | --- |
| [Editable Blender source](../../assets/models/whole-character-v38/body-finish01/murderbird-v38-material-body-finish01.blend) | `a9ba1c424a84e7a8d50a5b0ccd80405a2808f8e36b986d88dfb3f0de228d96d8` |
| [Rigid runtime GLB](../../assets/models/whole-character-v38/body-finish01/murderbird-v38-material-body-finish01.glb) | `327725f8a1d8a3958ec7ecc2542ef943a85492f75c7eaf5c527c8c06c68cd596` |

The 12,277,984-byte GLB contains 600 meshes. Its geometry binary, nodes, attachment ownership and eligibility remain exact to body-study02. The [material receipt](../../assets/audit/whole-character-v38/body-finish01/receipt.json) records native save/reopen preservation, input/output hashes, material assignments and all profiles. Absolute input paths describe the executed Mac run; matching body-study02 binaries are also preserved on this branch. The write-once recipe refuses to overwrite an existing version. Its executed copy and the inherited base material recipe are frozen beside the receipt.

The regional-only contrast study preserves the V37 geometry and is a separate comparison artifact. It is not the combined checkpoint. Its executed recipe is frozen in its own audit directory.

## Construction, material and era map

| Region | Geometry and attachment | Material treatment | Era / inheritance |
| --- | --- | --- | --- |
| Lower breast and dorsal pelvis | 32 allowlisted original meshes revised; fixed body stock; sampled relief around moving thighs | Inherited plate/frame response | Original owners and era gates retained |
| Pelvis | Seven tapered return courses and two fixed load webs, all body-owned | Plate / frame | Nine new passive pieces eligible in all eras |
| Thighs | Six separate channel segments per thigh, rigidly attached to the corresponding thigh | Plate response; open functional spaces | Twelve new passive pieces eligible in all eras |
| Crown | Existing head-owned rigid plates | New `crown-plate` response | Maker warm metal; later restrained dark green metal; no head shaping |
| Breast | Existing rigid plate and liner attachments | New `breast-plate` response | Original era eligibility preserved |
| Shoulder | Existing shoulder envelope ownership | New `shoulder-plate` response | Restricted anatomical left articulation unchanged |
| Bill, neck, repairs, bearings, frame, feet, recesses, inner surfaces and edges | Existing geometry / attachment contracts | Inherited distinct roles | No newly added actuation, sensing or processing |
| Optic | Existing recessed assembly | Inherited gated optic profile | Dark early states; restrained Advanced treatment |

The full [regional assignment map](../../assets/audit/whole-character-v38/body-finish01/receipt.json) identifies 12 material roles and the source region/era of each assignment. Geometry remains rigid; no new skinned surfaces or flexible connections are introduced. This is a hybrid rigid-geometry and standard browser PBR material study with vertex colors retained. No UV maps, image textures, normal maps, relief, manufacturing marks or local wear were authored. Regional color/roughness/metallic factors are proposals, not measured alloys or painted photographic highlights. It does not satisfy the complete three-era exterior mandate yet.

## Checks completed and practical limits

- **PASS:** receipt-bound model hashes, native save/reopen preservation and geometry binary preservation for the material wrapper.
- **PASS, narrow clearance screen:** body-study02 reports zero introduced body/thigh actual-triangle overlap pair-samples at seven local-X thigh angles. See its [construction handoff](body-checkpoint-2026-09-29.md) for exact scope and preserved study01 failure. Continuous collision, containment, combined axes and physical loads are outside that screen.
- **PASS, bounded runtime integration:** [66 samples](../../assets/audit/whole-character-v38/body-finish01/era-integration/integration.json), zero declared failures or fit risks on the exact combined GLB. Actual GLTFLoader and existing era/motion/mechanism/inspection code cover five Maker controls, Mechanic route/turn samples, Advanced thrust/jump, all-era opening/separation/reset and era reset. This is kinematic evidence; the separate attention/strike envelope and continuous plate intersections are not certified by this run.
- **PASS:** actual browser WebGL loaded the combined GLB, with 9/10/12 eligible material profiles applied for Maker/Mechanic/Advanced and zero invalid profiles. Browser evidence includes all three neutral appearances, an actual Maker jaw control, Advanced opening, full separation, reassembly and exhibit lighting. Root visually reviewed the open/separated/reassembled captures; no claim of a full visual motion-envelope inspection follows from these static views.
- **PASS:** `npm ci`, `npm run build`, `git diff --check`, and `node scripts/verify-publication.mjs`. The production build includes the selected V37 model and approved media; neither candidate GLB is emitted. The known large Three.js chunk warning remains.
- **PASS, continuity only:** current illustrated fallback displayed in the browser. **NOT RUN:** new candidate fallback authoring; its displayed fixed captures remain V37 and do not prove candidate appearance.
- **WARN:** paused idle observation on Apple M4 Max, ANGLE Metal, 811 × 648 buffer, pixel ratio 1: 10 ms median / 12 ms P95 frame interval, 1,276 draw calls, 856,540 triangles. It is an initial short desktop observation, not a moving, mobile or stress benchmark. Frame-step intervals are excluded from performance claims.
- **NOT RUN:** candidate remote CI, Pages deployment, broad device testing and owner likeness acceptance. A branch push makes source available; it does not publish this model or synchronize another checkout by itself.

See [browser evidence](../../assets/audit/whole-character-v38/body-finish01/browser-evidence.json) for captures, conditions and exclusions. Camera presets match across comparison views, but iframe sizes differ and identical animation phase is not claimed. Initial unsettled/loading and requested-but-not-open captures are explicitly excluded from matched or inspection proof.

## Exchange and next action

Fetch `codex/v38-material-contrast-01`, record its exact SHA, and hydrate LFS before reviewing the native/GLB. Root will relay the verified pushed SHA to Replit. Replit is a development preview, **Free mode only**, with Power/Max declined. Its divergent local work at `c22c7e7` must remain preserved; acknowledgment of this branch is not permission to rebase/reset its main or retry managed completion.

The next bounded likeness increment should address the full-body mass distribution and head/shoulder construction against these matched views. Proposed geometry and surface values require owner artistic review before final exterior finishing or production selection. V37 deployment approval remains distinct from acceptance of this new candidate.
