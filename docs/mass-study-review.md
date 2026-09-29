# MurderBird — strength and posture review

**Preserved checkpoint at `882268b`.** The next derivative implements the owner's flightless balance/shielding and shoulder/elbow clarification. See [the current shield-study review](shield-study-review.md); this report and its evidence remain historical.

**2026-09-27 · PARTIAL · new owner direction implemented as a local study; likeness acceptance pending.**

**Historical status clarification (2026-09-27):** The release row below records this study's status at that checkpoint. The owner subsequently authorized publication of the current assessment exhibit, selected review derivative, and source/evidence package; see the [publication review](publication-review-2026-09-27.md). This does not accept the study's likeness or grant broader asset rights.

The owner clarified a combination of exposed Terminator machinery, B2 super battle droid strength and bulk, and Jurassic Park raptor speed and ferocity, in bird form. The [direction record](mechanical-predator-direction.md) preserves the exact instruction, its interpretation and evidence tiers. The resulting study emphasizes a broad shoulder frame, a deep trunk, substantial leg mechanisms and a compact structural neck. It remains rough character work, not finished production art.

## Review links

- [Current comparison](../assets/audit/uncaged-mass-review/likeness-review.html): selected MurderBird raster, actual new 3D render, and preserved previous study.
- Local comparison URL: `http://127.0.0.1:5174/assets/audit/uncaged-mass-review/likeness-review.html`
- Local interactive exhibit: `http://127.0.0.1:5174/`
- [Editable source](../assets/models/uncaged-mass-study/murderbird-mass-study.blend), [runtime GLB](../assets/models/uncaged-mass-study/murderbird-mass-study.glb), [authoring script](../scripts/build-uncaged-mass-study.py), [provenance and hashes](../provenance/uncaged-mass-study-2026-09-27.json).

Local URLs require the running preview. These are approximate three-quarter view comparisons; the source camera is unknown.

## Changes and interpretation

The new derivative widens and deepens the torso, strengthens the shoulder yoke, thigh/shin mechanisms and joint housings, compacts the neck, recesses the optic and darkens the bill. Closed, overlapping armor replaces the bright outlined cells of the previous study. A second local refinement tapers the lower mantles, exposes the overlap at each plate edge and shortens the toes so the added bulk reads less like a static barrel.

The strike phase is now **0.18 seconds**, following the existing readable warning; pause, reduced motion and inspection retain their cancellation behavior. This is a faster scripted head/neck response, not a finished locomotion performance or proof of raptor-like speed. Feet remain fixed and no claw strike is implemented.

The heavier head exposed a contact defect in the previous tip-only rule. The scene now uses the actual leading head geometry to place the surface against the bar, within the existing bounded cervical slide. The final sampled contact is at **z=1.079 m**, against the bar surface at **1.100 − 0.021 m**. The browser check also verifies sampled head surfaces throughout the response remain inside the front plane. This is an illustrative rigid mechanism and planar constraint, not general collision physics or validated joint engineering.

The earlier source, export and comparison under `uncaged-study/` and `uncaged-review/` remain intact. Runtime imports explicitly use the new GLB. The selected source images were hash-checked again in the canonical primary checkout and were not modified. No new dependencies, asset uploads, purchases or publication occurred.

## Validation

The tested journey was: load → orbit/elevate/zoom/reset → deliberate reach → warning/strike/contact/recovery → open/separate → change eras → interrupted reassembly → keyboard/touch/reduced motion → model failure and retry. The actual built app separately exercised audio controls, WebGL context loss and unavailable-WebGL fallback.

Browser plugin not available; already bundled Playwright was used. Desktop: **Chromium 151.0.7922.34, 1440×1080**; touch emulation: **390×844**; fallback: **1280×960**. Host: Mac Studio M4 Max, 36 GB, macOS arm64. Chromium reports **SwiftShader software rendering**, not hardware GPU use. The report's `softwareGL: false` is the requested launch flag; the actual renderer fields establish software rendering.

| Check | Status | Evidence / boundary |
|---|---|---|
| Existing dependency installation | **PASS** | `npm ci`; 17 packages, zero reported vulnerabilities at install. Existing fsevents allowScripts warning remains. |
| Production build | **PASS** | `npm run build`; existing >500 kB uncompressed JavaScript warning remains. |
| State engine | **PASS · 12 tests** | `node --test tests/encounter-state.test.mjs`, after strike-duration change. |
| Native source | **PASS** | Reopened with automatic script execution disabled; 1,838 mesh objects and 21 empties. [Native receipt](../assets/audit/uncaged-mass-review/native-source.json). |
| Binary/export/build boundary | **PASS** | Actual self-contained GLB, 13 required component groups; all 26 emitted paths inspected, no LFS pointers or private/source/provenance files. [Asset receipt](../assets/audit/uncaged-mass-review/asset-validation.json). |
| Page identity / meaningful content / no framework overlay | **PASS** | [Current browser receipt](../assets/audit/uncaged-mass-review/browser-default.json). |
| Interaction, era state, keyboard, touch emulation, reduced motion and model retry | **PASS · 11 browser check groups total** | Same receipt; group count includes page identity, performance sampling and console health. |
| Console health | **PASS with renderer warnings** | Zero captured application errors; ReadPixels stalls from software rendering recorded. |
| Production smoke | **PASS · 10 checks** | [Built-app receipt](../assets/audit/uncaged-mass-review/production-smoke.json): 3D, theme play/pause, sound on/off, context loss/retry, no-WebGL fallback/inspection. |
| Visual inspection | **WARN** | Root inspected exterior, opened assembly, mobile and fallback. Comparative worker feedback identified excessive barrel-like mass; mantle/plate/toe refinement followed. The final head/neck transition, armor rhythm, wear and predatory movement remain unfinished. |
| Performance target | **FAIL in software-renderer test** | 11.20 fps sample versus provisional 30 fps target. Hardware GPU and physical-mobile performance **NOT RUN**. |
| Owner likeness / human accessibility / final audio review | **NOT ACCEPTED / NOT RUN** | No owner acceptance of this derivative; no screen-reader or human listening certification. |
| Remote CI / LFS clean-clone retrieval / deployment | **NOT RUN** | Work remains local. Independent primary-branch work is not integrated; publication is not authorized. |

The [initial failed contact check](../assets/audit/uncaged-mass-review/contact-before-fix.json) is retained. It is superseded by the passing current browser receipt, not suppressed. The response screenshot is named `reaction.png`: asynchronous capture may land in recovery after the contact measurement, so it is not claimed as an exact contact freeze-frame. Earlier `uncaged-review` receipts apply to the prior model only.

## Final local measurements

| Measurement | Result | Limit |
|---|---|---|
| Runtime GLB | **3,600,600 bytes; 95,004 unique triangles** | Within provisional 5 MB / 120,000-triangle budgets. |
| Visible default scene | **91,410 triangles; 82 draw calls** | Varies with state and visible era systems. |
| Main JavaScript | **672,688 bytes; 173.36 kB gzip** | Within provisional 250 kB compressed budget; Vite's uncompressed warning remains. |
| Model fetch | **820.3 ms**, 3,600,900 transfer bytes | Loopback development fetch, not public-network loading. |
| Frame rate / memory | **11.20 fps; 24.5 MB browser-reported JS heap** | Software-rendered interaction sample; no peak GPU/native-memory or real-device claim. |
| Native source bounds | **2.053 m tall × 1.414 m wide × 1.720 m deep** | Native object bounding boxes, not evaluated-modifier extrema or a story measurement. |
| Complete build | **45,074,832 bytes; 26 files** | Includes unchanged optional music and public assets; not initial page transfer. |

The asset receipt contains exact hashes for every emitted path. New review captures, source `.blend`, authoring script and provenance remain outside the website build. The original study is also excluded because the app no longer imports it.

## Handoff and next action

Changed scope: a new model generator and its two outputs; explicit model import and contact constraint in `src/scene/exhibit.js`; strike duration in `src/scene/encounter-state.js`; study label in `src/main.js`; validation output paths; new evidence/provenance; updated authority, requirements, catalog and handoff links. Existing theme assets, story snapshots and the illustrated reference remain unchanged.

Work is in `/Users/okh/.codex/worktrees/uncaged-production/murderbird-uncaged`, branch `codex/uncaged-production-review`, continuing local checkpoint `519201b`. This managed worktree belongs to the canonical repository. The independently active primary checkout was not edited.

Use the [handoff](production-handoff.md) to reproduce the source and runtime export. Review the mass/stance comparison next: does it convey a powerful mechanical bird that could move suddenly, while retaining MurderBird's identity? Resolve that visual direction before high-cost material finishing and the production joint/locomotion/claw rig. Technical success here does not close the original Phase C likeness gate or the broader production mandate.
