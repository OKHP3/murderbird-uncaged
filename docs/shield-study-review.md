# MurderBird — flightless wing study

**2026-09-27 · PARTIAL · functional wing revision implemented; artistic and motion acceptance pending.**

The owner clarified that MurderBird is flightless and uses its wings for balance and shielding, like a running back tucking in and using shoulder and elbow to push off and shove. The [direction record](flightless-wing-direction.md) preserves that instruction. Active requirements now describe functional shielding wings. Earlier ornamental-only wording is retained as historical context where appropriate, with an explicit current-direction addendum; story sources are unchanged.

## Inspect the revision

- [Wing comparison](../assets/audit/uncaged-shield-review/likeness-review.html): guarded rest, response capture and preserved earlier one-piece mantle study.
- Local comparison: `http://127.0.0.1:5174/assets/audit/uncaged-shield-review/likeness-review.html`
- Local exhibit: `http://127.0.0.1:5174/`. Select **Wings · balance & shielding**, then use **Reach toward bars** to see the short asymmetric response. Open inspection to examine the separate assemblies.
- [Editable Blender source](../assets/models/uncaged-shield-study/murderbird-shield-study.blend), [runtime export](../assets/models/uncaged-shield-study/murderbird-shield-study.glb), [authoring script](../scripts/build-uncaged-shield-study.py), [provenance and hashes](../provenance/uncaged-shield-study-2026-09-27.json).

Local URLs require the running preview processes. The screenshot labeled `reaction.png` may show recovery because capture is asynchronous; it is not presented as an exact impact freeze-frame.

## What changed

The one-piece mantles have become separate upper-wing/shoulder and elbow/forewing assemblies. A short load link joins the shoulder to a visible elbow axle; folded armor follows the forewing over the flank and ribs. Both shields remain compact. The right side leads the drive, and the repaired left shoulder has smaller travel. The opposite pose suggests counterbalance; actual center of mass and force are not calculated.

The existing response sequence now tucks the wings during warning, adds a short shoulder/elbow drive alongside the beak snap, and returns them to rest. There is no lift, takeoff, hovering or flapping animation. The beak still supplies the explicit front-bar contact; the wing gesture remains within the cage and is not claimed as a simulated wing impact.

The app has a seventh readable component entry, **Wings · balance & shielding**, with a model landmark and focus control. The same explanation remains available in the illustrated fallback; its canvas marker is hidden there. Inspection, pause and reduced motion suppress the wing drive. Separate shields remain editable and separate further in the exploded view.

## Local validation

The tested flow was load → inspect wing explanation → orbit/reset → reach and observe asymmetric shoulder/elbow motion → open/separate → change eras/reassemble → keyboard/touch/reduced motion → model failure/retry. Built-app smoke separately checked WebGL context loss, no-WebGL fallback and existing optional audio controls.

Browser plugin not available; already bundled Playwright was used without a new application dependency. Chromium **151.0.7922.34** ran on the existing Mac Studio M4 Max, 36 GB, macOS arm64, at **1440×1080**, **390×844** touch emulation and **1280×960** fallback. The actual renderer was **SwiftShader software rendering**. The launch flag `softwareGL: false` in the report does not establish hardware rendering.

| Check | Status | Evidence and boundary |
|---|---|---|
| Dependency install and build | **PASS** | `npm ci` and `npm run build`. No dependency/lock change. Existing fsevents allowScripts and >500 kB JavaScript warnings remain. |
| Native source editability | **PASS** | Blender source reopened with auto-execution disabled: **1,912 mesh objects, 24 empties**. [Native receipt](../assets/audit/uncaged-shield-review/native-source.json). |
| Assembly contract | **PASS** | **15 named component groups**; each elbow/shield is a child of its corresponding shoulder. Loader and asset validator both enforce this relationship. [Asset receipt](../assets/audit/uncaged-shield-review/asset-validation.json). |
| Page identity / meaningful content / no overlay | **PASS** | [Current browser receipt](../assets/audit/uncaged-shield-review/browser-default.json). |
| Wing limits and cage clearance | **PASS for sampled response** | Larger right drive, limited repaired-left travel; sampled wing bounds stay inside side/front planes. This does not certify all self-collision, joint engineering or force transfer. |
| Inspection and reduced motion | **PASS** | Measured wing drive angles return to zero; reach/inspection cancellation and reassembly remain functional. |
| Browser journey | **PASS · 11 check groups** | Includes wing copy, era visibility, keyboard/touch, no autoplay, model failure/retry and fallback marker handling. Same receipt. |
| Console health | **PASS with renderer warnings** | Zero captured application errors; software-renderer ReadPixels stall warnings retained. |
| Built-app smoke | **PASS · 10 checks** | [Production receipt](../assets/audit/uncaged-shield-review/production-smoke.json): 3D, optional theme/sound controls, context loss/retry and no-WebGL inspection. |
| Earlier state-engine unit suite | **NOT RERUN in this revision** | `encounter-state.js` is unchanged; the preceding checkpoint records its 12 passing tests. This revision exercises the new rendered wing behavior directly. |
| Visual review | **WARN** | Root inspected neutral, response, exploded and mobile inspection renders. Jointed guards are present and fit the inspection views, but finished likeness, handworked materials and full-body weight transfer remain unaccepted. |
| Performance | **FAIL against provisional 30 fps target in software rendering** | **10.62 fps** sample; hardware GPU and physical mobile measurements **NOT RUN**. |
| Owner acceptance / human accessibility / real force and balance | **NOT ACCEPTED / NOT RUN** | Intent is confirmed; artistic quality, engineering and human usability are separate gates. |
| Remote CI / clean-clone LFS / publication | **NOT RUN** | Local branch only; no upload, push or deployment. Independent primary checkout remains untouched. |

At the sampled contact phase, shoulder X rotations were **+0.065 rad left / −0.23 rad right**; elbow X rotations were **0.18 rad left / 0.40 rad right**. Their magnitudes are approximately **3.7° / 13.2°** and **10.3° / 22.9°**, respectively. These are authored exhibit limits, not researched anatomical specifications. Wing surfaces stayed within roughly **±0.803 m** laterally, with forward extent below **0.672 m**. The beak/head leading surface remained at **1.079 m** against the front bar surface at **1.100 − 0.021 m**.

## Delivery measurements and preservation

The self-contained GLB is **3,747,052 bytes** with **99,516 unique triangles** across all eras. The default visible scene measured **95,922 triangles and 92 draw calls**. Main JavaScript is **673,966 bytes / 173.75 kB gzip**. The loopback model fetch measured **815.5 ms**, and the browser-reported JavaScript heap estimate was **23.1 MB**; these are not WAN, GPU-memory or peak-memory measurements.

All **26 build paths**, totaling **45,222,562 bytes**, were checked. The total includes unchanged optional music and existing public assets. There are no LFS pointers, native source files, audit captures, provenance or private archives in the build. The asset receipt lists every emitted path and hash. Earlier `uncaged-study` and `uncaged-mass-study` binaries, generators and evidence are preserved separately.

Changed scope: new shield generator and `.blend`/`.glb`; model loading, elbow hierarchy, asymmetric pose and marker in `src/scene/exhibit.js`; component explanation/status copy in `src/main.js`; marker cleanup in `src/scene/fallback.js`; focused validation scripts; direction, requirements, handoff, catalog and provenance records. No story, music, historical image or private archive was changed.

Work remains in `/Users/okh/.codex/worktrees/uncaged-production/murderbird-uncaged`, branch `codex/uncaged-production-review`, continuing `882268b`. See the [production handoff](production-handoff.md) to regenerate the new derivative. The next review is whether the tucked wing silhouette and short elbow drive read as shielding and close-contact strength. Full-body bracing, turning balance, locomotion, claw action and final character fidelity remain production work; the original likeness gate is still open.
