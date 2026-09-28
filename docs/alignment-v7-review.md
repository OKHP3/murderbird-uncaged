# Alignment V7 — selective regional integration

**Local correction candidate; all three eras remain revision-required for artistic likeness.** This combines the sixth V6 head/neck and inherited body/mantle with the reviewed regional candidate04 limb guards and distal talons. It does not incorporate the separate bill-profile or toe-cover proposals. No finished material treatment, owner acceptance, push, merge or deployment is established here.

The local [review gallery](../assets/audit/alignment-v7/index.html) contains 42 neutral authoring views and seven fixed-camera V6/V7 pairs. Open it through the running local server at `http://127.0.0.1:5183/assets/audit/alignment-v7/index.html`. The local exhibit at port 5183 selects V7. The published site and historical `/review/` packet remain separate.

## Exact candidate

| Artifact | Identity |
| --- | --- |
| [Editable Blender source](../assets/models/uncaged-alignment-v7/murderbird-alignment-v7.blend) | `a8fccaf024a096678415215029b34cae8270b348da2301b8872a34e72c75ed3f`; 1,945,914 bytes |
| [Runtime GLB](../assets/models/uncaged-alignment-v7/murderbird-alignment-v7.glb) | `1c82874b86af6b493ac380536de6af72a30fafa3a4b0ebb3d8790f56ffc03018`; 4,426,968 bytes |
| [Construction inventory](../assets/models/uncaged-alignment-v7/alignment-inventory.json) | 687 editable mesh pieces, 462 retained control curves, 51 pivots; 90 exported mesh groups, 141 nodes, 230,900 triangles |
| V6 base | Native `5a7a51941423dd0efcb48b9641b7a49597dad117e218ccb4e94f26315c5e9ded`; runtime `ce35024adda89681a0f37e7018e2563a74af67cd06558a887222df87b78a87fe` |
| Regional candidate04 source | Native `376718193b9859cf7e454a0e148dde420c74061e6cdfbec7dd84ae6a4d3c960b`; runtime `829d416a9eb65226543ce619ffc37ce8f135f3f8869ffb291b65da2a5c664c67` |

The executed composer and exact input snapshots are under [`assets/audit/alignment-v7/`](../assets/audit/alignment-v7/). The unexecuted worker handoff was preserved separately after review found an undefined material-map variable and an incomplete material-selection restriction. Those were corrected before the first build. The native model was saved with guard modifiers intact, then reloaded and checked before modifiers were evaluated for export. Existing V6 control curves are retained guides; they do not regenerate the transferred guard profiles.

## Visible changes and remaining defects

The exact transfer removes 26 named cylindrical/ankle cover pieces, adds ten shaped overlapping thigh/shin/instep guards, and replaces only six distal talon mesh datasets. It preserves the other mesh/curve records and all pivot transforms. The original heel claws and axle caps remain; removing the ankle ribs intentionally reduces the foot-edge batch size. See the [regional transfer contract](alignment-regional-transfer.md).

The lead reviewed the combined three-quarter, feet and foot-side views against the V6 baseline and actual candidate03 reference. The guards now have shaped faces and more deliberate joint openings. Whole-body proportions remain unchanged. The feet still read as tubular articulated links with narrow hooked tips; the unchanged rounded digit roots remain a significant likeness gap. The side view also leaves substantial exposed rails. That exposure is not automatically incorrect, but its relation to the era-specific drives and the reference construction needs further work.

The head is exactly the V6 head. The small isolated bill-profile change was held because it did not resolve the constructed bill-root/brow/cheek hierarchy. An isolated toe-cover study was also held: added dorsal patches left the rounded roots dominant. Both editable proposals and their before/after evidence remain preserved. They are not claimed as improvements in V7.

Maker and Mechanic neutral fallback files have different PNG hashes but identical rendered pixels in the current closed view. The later shoulder repair is not visibly distinguishable there. These authoring stills therefore do not prove era differentiation; the browser adds the external controls, mechanical transmission and Advanced systems separately. Material and construction-state likeness remain open in each era.

## Technical evidence

- The [independent export comparison](../assets/audit/alignment-v7/export-comparison/export-comparison.json) passes all 90 material-tagged geometry groups and all 51 pivot parent/world-transform comparisons. Retained groups match V6; the 14 affected aggregate groups match regional candidate04. It compares triangle counts and bidirectional position clouds at 0.00001 m tolerance, not complete topology, normals or UVs. Native names/modifiers are checked by the separate composer.
- The [affected check suite](../assets/audit/alignment-v7/rig-suite/run-manifest.json) passes six rigid-motion validators (59 assertions) plus the sampled adjacent limb-plate diagnostic: four neighboring knee/ankle plate-owner pairs at seven actual controller poses, with zero proper surface-crossing candidates. Bearing/frame roles, same-owner overlap and continuous sweeps are excluded. The exact V7 GLB was supplied directly. The source hash set was unchanged during that run. Subsequent app edits select the V7 GLB and fallback paths and add a development-only current-review link; the tested motion/controller/inspection sources remain unchanged.
- `npm ci` completed with 17 packages and no reported vulnerabilities. `npm run build` and the active publication-boundary validator passed. The [local build receipt](../assets/audit/alignment-v7/local-build-validation.json) records 134 emitted paths and 16 exact model/folio/fallback source matches; this is a measured inventory, not a permanent count requirement. No V7 native sources, audit archive, private files or provenance trees were emitted. Two publication-boundary tests passed, including the unexpected private-file fixture. A first test invocation used the wrong directory and did not run; the correct `tests/publication-boundary.test.mjs` invocation passed.
- Actual WebGL on the Mac loaded 4,426,968 bytes with the exact V7 SHA above. The completed browser packet contains an 86.527-second normal-clock movement sequence, two no-input sequences of 120.033 and 122.022 video seconds, four directly captured action poses, and opening/separation/reassembly plus illustrated-fallback captures in all three eras. The alternate run uses an explicit development seed; small telemetry/video timing offsets are recorded. Evidence is under [`browser-1c82874b86af`](../assets/audit/alignment-v7/browser-1c82874b86af/). Static accelerated review poses are distinct from normal-clock recordings and performance measurements.

The build retains the existing large Three.js chunk warning. None of these checks establishes physical simulation, continuous/all-pairs collision freedom, physical mobile behavior, human screen-reader review, complete performance coverage or artistic acceptance.

## Finding status and next correction

| Finding | V7 state |
| --- | --- |
| F01 body/neck/silhouette | Inherited V6 proposal; reference likeness and owner acceptance open. |
| F02 head/bill/crown/optic | V6 retained exactly; bill-root/brow/cheek refinement needed. |
| F03 folded mantle | V6 retained; compact coverage and both-side likeness still open. |
| F04 limbs/feet/talons | Reviewed guards/talons integrated and technically checked; digit-root and foot-to-claw form remain open. |
| F05 regional plates | Shape work remains; no final exterior approval. |
| F06 materials/wear | Dependent finishing remains gated on neutral-structure review. |
| F07 articulated claw | Existing action retained; exact-model rig checks pass. The actual claw-contact frame and normal-clock sequence are captured; support/contact evidence remains kinematic and bounded. |
| F08 autonomous acting | Existing variation retained; two fresh V7 no-input recordings are saved with event logs. Continuous human acting judgment remains open. |
| F09 inspection labels | Existing layout retained; no new claim of complete T11–T13 coverage. |
| F10 validation scope | Active boundary validator accepts the explicit V7 contract; its negative fixture still passes. |

Continue with a constructed bill-root/brow proposal and a more coherent digit envelope, preserving the validated optic, jaw, neck and contact relationships. The [V10/V12 decision packet](correction-v2-reference-packet.md) remains pending. The complete neutral candidate still requires the owner's Stage B review before dependent material polish or release consideration.

The review gallery loads all three MP4 files and a short playback check decoded51frames while advancing1.393seconds. The390px DOM has no horizontal overflow. Its narrow PNG capture repeats part of the header inside the video area; the DOM contains only one header and the source video contains the exhibit. That capture/rendering issue remains unresolved and is not counted as a narrow-video visual pass.

The local exhibit now links directly to the current geometry gallery and labels the frozen older packet “Published review.” The development-only link is absent from the production bundle; no raw audit gallery was emitted. A subsequent install/build/boundary check passed, with its separate [receipt](../assets/audit/alignment-v7/local-build-navigation-validation.json) preserving the earlier build record.

The [independent telemetry readout](../assets/audit/alignment-v7/browser-1c82874b86af/telemetry-review.md) separates planned family labels from executed actions. In matched first-120-second windows, the default and alternate samples have seven and six family-label onsets; repeated route/family labels remain. These counts do not establish an acting pass. The scripted Mechanic stop completes its current cycle and reaches ready with14 reported steps; the envelope records actual bill contact and all three reassemblies.
