# FINISH01 attempt02 pipeline diagnosis

2026-10-04, independent Builder read-only diagnostic. No producer artifacts, receiving native, Git state or runtime files were edited. All probes and outputs are disposable under `/tmp/cg-recursive-finish-pipeline-*`.

**Conclusion: no surviving attempt02 render-path defect was found.** Attempt01 had an evaluated material-binding failure; attempt02's DATA-bound exact mesh copies repair it. The current whole-image change is small and fails the worker's visual judgment, but further renderer repair is not indicated by these tests. No new artistic candidate or helper correction is recommended from this pipeline audit.

## Confirmed execution path

- Frozen `assets/audit/cg-recursive-finish01/executed-run-attempt02.py:16-18` applies BODY01, renders before, then applies FINISH01. Lines21-25 save and reopen the new attempt02 native before candidate rendering. The baseline therefore contains the same provisional BODY01 geometry.
- `scripts/cg-recursive-finish01.py:105-111` copies each successor mesh datablock exactly, uses DATA slots, and declares original render/layer hides. Lines97-99 bind the new color/ORM images and reduce normal strength; they do not remodel geometry.
- Architect `scripts/cg-recursive-delivery01.py:186-196` creates a separate scene and links visible render meshes; lines210-215 restore the serialized Cycles/view settings; lines248-261 explicitly set PBR override to None and render. Saved native's source view layer also has no material override.
- Fresh readback showed visible, camera-enabled brow, dorsal bill and BODY01 successor meshes; slot materials equal modifier-evaluated materials. The probe retained original graphs and never saved its in-memory changes.

## Decisive runtime evidence

1. Exact saved native SHA `f14ad88bcc79fb1fd8af1abb4a79e7a5558d8a6b7c946ea0f897c3026fb420f1` reopened in Blender 5.2.1. An in-memory solid-magenta emission diagnostic replaced 2,483 slots across 1,962 finish successor meshes. Through the exact helper, the visible shell rendered magenta. The selected brow's evaluated materials were magenta. This excludes a global visibility, helper material-override, or successor slot-binding obstruction for the tested Builder input. Images: `/tmp/cg-recursive-finish-pipeline-probe01/{normal,magenta}/canon-neutral.png`; report: same folder `report.json`.
2. A second fresh Blender process rendered the saved candidate at its original 640px / 6 samples through the same helper. It matches the frozen candidate to within 1 byte at 30 of 272,640 pixels; mean normalized RGB difference 1.438e-7. This excludes a stale saved-candidate render or materially different fresh renderer outcome. Image: `/tmp/cg-recursive-finish-pipeline-probe02/fresh/canon-neutral.png`; report: same folder `report.json`.
3. All 140 new successor color/ORM images are FILE sources whose packed bytes equal their external PNG bytes, and all 140 pixel arrays are finite. `/tmp/cg-recursive-finish-pipeline-texture-readback03.json` records every hash. Native binary remained unchanged after each probe.

## Actual scale and limits of the authored change

Frozen neutral before-to-candidate mean absolute RGBA8 difference is 1.0362007; normalized RGB difference is .00541804. Workshop RGBA8 difference is 1.2090146. The often-cited .00004 is not the measured neutral before-to-candidate RGB result for this frozen packet. This is a numerical correction, not an acceptance score.

Decoded source map colors were already dark. Head old scene-linear mean(.02661,.03475,.02826) becomes(.02292,.02771,.02251). Breast old(.02910,.03493,.02429) becomes(.02342,.02749,.02145). Brow old(.13061,.09569,.04512) becomes(.08469,.06504,.03219). Raw Blender image pixel means are sRGB-like file values; interpreting them as scene-linear would greatly overstate the darkening. Encoding/FILE metadata here is correct. The successor brow still has metallic mean .85766 and roughness .45406.

**Inference:** unchanged broad geometry and similar high-metal surface response under the same large white area rig explain why the brow remains pale and whole construction still reads similarly. This audit did not isolate individual light contributions, so reflection is not a separately proven sole cause. Texture work cannot reshape the broad hood, smooth bill or clean plate construction because its successor geometry is explicitly copied unchanged.

## Smallest safe correction and scope

The binding correction already exists in attempt02: exact independent successor mesh DATA slots (`cg-recursive-finish01.py:105-107`), replacing attempt01's shared mesh OBJECT overrides (`executed-attempt01.py:91-93`). Keep that method and require evaluated-material readback for future modules. No additional render helper correction is supported. Any further finish work should be decided as a new art proposal after source/whole-image review, not as a fix for supposedly hidden textures.

Only Builder attempt02 was independently probed. Maker/Mechanic, browser appearance, GLB rendering, app build, deployment, owner likeness acceptance and engineering were not verified. The worker's mechanical custody PASS is distinct from its visual FAIL (`assets/audit/cg-recursive-finish01/README.md:17-21`).

Absolute paths, exact pins and image/map metrics are in `/tmp/cg-recursive-finish-pipeline-metrics01.json`.
