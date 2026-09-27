# MurderBird: Uncaged — local acceptance report

**Historical checkpoint at `519201b`.** This records the earlier proportion revision. The active model now follows the owner’s subsequent heavy-machine/predator direction; see [the current mass-study review](mass-study-review.md). Earlier assets and test receipts remain preserved.

**2026-09-27 · PARTIAL · revised proportions awaiting owner review.** The integrated local study demonstrates genuine 3D, a scripted cage response and reversible interior inspection. It does not yet establish the unmistakable MurderBird likeness or physical credibility required for finished character production. The owner rejected the first proportion direction with **“Rework the proportions first.”** The revised geometry is implemented; no subsequent owner acceptance is recorded.

This report is the current local verification record. It supersedes source-presence-only status in earlier handoff drafts. Technical checks, artistic acceptance, remote CI and publication are separate gates.

## Review the revision

- Local exhibit: `http://127.0.0.1:5174/`
- Side-by-side likeness review: `http://127.0.0.1:5174/assets/audit/uncaged-review/likeness-review.html`
- Production build preview used for checks: `http://127.0.0.1:4176/`
- Durable comparison: [review page](../assets/audit/uncaged-review/likeness-review.html), [current render](../assets/audit/uncaged-review/reference-angle-model.png), [previous proportions](../assets/audit/uncaged-review/proportions-before.png).

These URLs require the local preview processes. The comparison uses similar three-quarter views, not a calibrated camera reconstruction. The selected raster is a production reference, not approval of the new model.

The revision shortens and lowers the exposed legs, deepens and lowers the torso, compacts and broadens the neck, and adjusts the head profile. Named landmarks keep the bill contact and part labels attached to the revised geometry. The plates remain too regular; the cheek/neck transition, shoulder mass, repaired leg detail and aged surfaces still fall short of the reference. Hidden surfaces, joint topology and internals remain proposed reconstructions.

## Acceptance matrix

| Area / requirement | Local evidence | Status and boundary |
|---|---|---|
| Character identity · UCR-01–04 | Selected images and representative video frames inspected; exact source paths/hashes in [creative authority](creative-authority.md) and [provenance](../provenance/uncaged-study-2026-09-27.json); before/after comparison saved. | **Awaiting owner review.** Initial proportions required rework. Revised study is not finished or accepted art. |
| Genuine 3D · UCR-05 | Loaded self-contained GLB; orbit, elevation, zoom, reset and rear-view capture exercised in Chromium. | **Verified locally.** Model geometry is visible from changing viewpoints; no raster turntable supplies the 3D bird. |
| Component selection · UCR-06 | Six named regions, external text, focus controls and model landmarks are implemented. | **Implemented; partial visual verification.** Human inspection/readability and assistive-technology acceptance remain outstanding. |
| Editable source · UCR-07 | Blender source reopened with automatic script execution disabled; 3,017 mesh objects and 21 empties; GLB contract validates 13 component groups. | **Verified locally.** Editable source and runtime derivative are real binaries, not LFS pointers. Not a finished rig or engineered assembly. |
| Opening/interior · UCR-08 | Breastplate hinge and cranial cover expose geometry; separation to 100%, interrupted return, reassembly and era changes exercised. | **Verified locally as a study.** Interior geometry is illustrative; production layout and visual readability need refinement. |
| Cage/reaction · UCR-09–10 | Notice → warning → strike → contact → recover → cooldown → idle observed. Contact bill tip at z=1.079 m against the front boundary at z=1.100 m. | **Verified scripted contact; physical credibility partial.** Fixed front contact zone, not arbitrary 3D targeting or collision simulation. Feet stay planted. Animated claw action and a load-bearing production rig are missing. |
| Generations · UCR-11–13 | Three era controls and present/absent node checks; Mechanic winding assembly; Builder breast power separate from cranial processing. | **Verified visibility and transitions.** Shared schematic exterior and proposed mechanisms are not three finished historical models. Maker's unexplained drive remains uncertain. |
| State stability · UCR-08–10 | Twelve state tests plus browser checks for cancellation, repeated reach, inspection, era change, pause, reduced motion and interrupted reassembly. | **Verified for exercised cases.** Broader real-device testing remains. |
| Accessibility/audio · UCR-14 | Keyboard routes, pointer cancellation, 390×844 touch emulation, OS reduced motion, pause, readable text, no autoplay; opt-in theme and machinery sound controls exercised. | **Partial.** Automated behavior passes. No screen-reader audit, physical touch-device test, hearing/listening acceptance or human usability review. Existing sung theme retained. |
| Fallback · UCR-15 | Model failure, unavailable WebGL and actual context loss exercised separately; recognizable fixed illustration, labeled assembly schematic and text controls remain; retry restores 3D. | **Verified locally.** Fallback makes no claim of unrestricted 3D. |
| Performance | Transfer, scene geometry, frame-rate sample and available memory estimate recorded below. | **Partial / frame-rate target unmet in software rendering.** No hardware GPU or physical mobile benchmark. |
| Integrity/privacy · UCR-16 | `npm ci`, production build, real binary checks, all 26 emitted paths inspected, no LFS pointers or private/source/provenance records emitted. | **Verified local build boundary.** No app dependencies added. Historical sources and private archives preserved. |
| Release | Managed local worktree and local previews only. | **Not published.** Remote LFS retrieval, CI, deployment SHA, live acceptance and main-branch integration are unverified. Publication is not authorized by the prototype mandate. |

## Checks actually run

The flow under test was: load the exhibit → orbit and deliberately reach → observe contact/recovery → open and separate assemblies → switch eras → reassemble → exercise calm, keyboard/touch and failure recovery.

Browser plugin not available; the already bundled Playwright runtime was used without installing an application dependency. Desktop testing used Chromium **151.0.7922.34**, 1440×1080; mobile emulation used 390×844; fallback capture used 1280×960. The host is a Mac Studio, M4 Max, 36 GB RAM, macOS arm64. The browser reported **ANGLE / Vulkan SwiftShader**, a software renderer. The report's `softwareGL: false` means no explicit software-launch flag; it does not mean hardware rendering. The recorded `renderer` and `softwareRenderer` fields establish the actual renderer.

| Check | Result | Evidence |
|---|---|---|
| Dependency install and production build | Pass; 17 installed packages, zero reported vulnerabilities at install. Existing fsevents allowScripts warning and Vite >500 kB chunk warning retained. | Existing dependency lock unchanged; build file hashes in [asset validation](../assets/audit/uncaged-review/asset-validation.json). |
| State engine | **12/12 pass.** | `node --test tests/encounter-state.test.mjs` |
| Binary, assembly and build boundary | Pass; 13 assemblies, 34 nodes, 13 exported meshes; all 26 build paths allowed and actual binaries. | `python3 scripts/verify-uncaged-assets.py`; [JSON record](../assets/audit/uncaged-review/asset-validation.json). |
| Page identity / meaningful content / error overlay | Pass. | [Current browser record](../assets/audit/uncaged-review/browser-default.json), captured 05:39:58 UTC. |
| Interaction / responsive / fallback checks | **11/11 check groups pass.** | [Browser record](../assets/audit/uncaged-review/browser-default.json) and [repeatable harness](../scripts/verify-uncaged-browser.mjs). |
| Console health | Zero captured app errors; software GL ReadPixels stall warnings recorded. | Same browser record; warnings are not hidden. |
| Built-app smoke | **10/10 checks pass**, zero captured page errors: 3D, theme play/pause, sound on/off, context loss/retry and no-WebGL inspection. | [Production smoke](../assets/audit/uncaged-review/production-smoke.json), captured 05:42:47 UTC. |
| Visual evidence | Root inspected rendered exterior, exposed assemblies, mobile and illustrated fallback captures; independent worker review supplemented this. | [Exterior](../assets/audit/uncaged-review/reference-angle-model.png), [Builder interior](../assets/audit/uncaged-review/exploded-builder.png), [Mechanic interior](../assets/audit/uncaged-review/exploded-mechanic.png), [mobile](../assets/audit/uncaged-review/mobile-inspection.png), [fallback](../assets/audit/uncaged-review/illustrated-fallback.png). |

The older [initial browser record](../assets/audit/uncaged-review/prior/browser-native.json) predates the proportion correction and is retained as historical evidence only. Its filename is not evidence of hardware GPU rendering. The passing performance-sample check in the harness means measurements were captured, not that a frame-rate budget passed.

## Asset and performance measurements

Provisional local engineering targets are ≤5 MB for the GLB, ≤120,000 unique triangles, ≤250 kB gzip for the main JavaScript bundle, and ≥30 fps during interaction. These are starting budgets informed by this pipeline; representative physical-device measurements are still needed before treating them as production acceptance limits.

| Measurement | Observed value | Interpretation |
|---|---|---|
| Runtime model | 4,085,960 bytes; 94,604 unique triangles across all eras | Within provisional size/geometry targets. |
| Default visible scene | Approximately 91,010 triangles and 80 draw calls | Measured in default Builder view; changes with inspection/visibility. |
| Editable source | 1,727,906 bytes; native source bounding height 2.053 m, width 1.124 m | Approximate two-metre convention; source bounding boxes, not physical measurement or evaluated modifier extrema. |
| Main JavaScript | 672,611 bytes; build reports 173.30 kB gzip | Within provisional compressed target; Vite warns about uncompressed chunk size. |
| Frame-rate sample | **10.76 fps** across the captured desktop interaction run | Below the provisional 30 fps target in SwiftShader. Not proof of M4 GPU performance. |
| Model fetch | 859.5 ms; 4,086,260 transfer bytes including transport overhead | Loopback development server, not cold public-network loading. |
| Memory | Browser-reported JS heap estimate 24,500,000 bytes | Does not include total GPU/native allocations; not a peak-memory certification. |
| Whole build | 45,560,115 bytes, 26 files | Includes existing optional theme files (~36.8 MB). Build size is not initial page transfer; theme does not autoplay. |

Current GLB SHA-256: `074c493bba3bc36e7f9c0d1876a9d7dca7e818c9ea848345e60c7aa35094451b`.

Current Blender SHA-256: `9141384d713c0aed900325403665180ceaf96b233ce25e69726e7a68fb148700`.

The [asset validation record](../assets/audit/uncaged-review/asset-validation.json) enumerates every emitted path, size and hash. Runtime imports include only the GLB and selected reference WebP in addition to existing public assets. The `.blend`, authoring/QA scripts, audit captures, provenance, story snapshots and private sessions are outside `dist/`.

## Changed files and production decisions

- `scripts/build-uncaged-study.py` and `assets/models/uncaged-study/`: locally authored segmented mesh source and optimized runtime export. Native plate/fastener editability is retained; runtime batching stays within 13 named moving assemblies. Local Blender 5.2.1 LTS was verified as signed/notarized before use. No external asset upload or paid generation was used.
- `src/scene/exhibit.js`, `src/scene/encounter-state.js`, `src/main.js`: GLB loading, orbit/focus, enclosure, constrained response, era rules, reversible inspection and guarded UI state. The state module has no renderer dependency.
- `src/scene/fallback.js`, `src/style.css`, `src/fallback.css`: recognizable illustrated fallback, separate explanatory schematic, immediate exhibit layout, responsive controls and focus/reduced-motion support.
- `src/audio/soundscape.js`: corrected a stale explanatory comment. Existing theme integration and music assets remain intact.
- `tests/encounter-state.test.mjs`, `scripts/verify-uncaged-assets.py`, `scripts/verify-uncaged-browser.mjs`, `assets/audit/uncaged-review/`: state tests, reproducible local checks and review evidence.
- `README.md`, `docs/creative-authority.md`, `docs/asset-capability-audit.md`, `docs/production-workflow.md`, `docs/uncaged-requirements.md`, `docs/hotspot-map.md`, `docs/media-catalog.md`, `docs/production-handoff.md`, this report and `provenance/uncaged-study-2026-09-27.json`: scope, authority, source status, workflow comparison, acceptance and reproduction records.

The [workflow decision](production-workflow.md) compares local Blender, Adobe-assisted work and automated reconstruction using official sources. Installed Creative Cloud applications were distinguished from unverified Substance entitlements/credits. No new subscriptions, credits, application dependencies or uploads were used. Creative material remains all rights reserved; code retains the repository MIT license.

Current-session metadata verified the primary agent as `gpt-6-astra` with `ultra` effort. Bounded workers were requested using explicit `gpt-6-luna` / `high` controls where supported. The initial full-history worker has no independently exposed model execution receipt; its requested setting is not presented as independently verified execution. The root reviewed consequential outputs and owns acceptance.

## Worktree, remaining work and next gate

Work is preserved in the canonical repository's managed worktree at `/Users/okh/.codex/worktrees/uncaged-production/murderbird-uncaged`, branch `codex/uncaged-production-review`. Baseline inspection used `0d4032907ce55f328de10ba4978a5025988606ee`. Prototype commits `3409121` and `6042b5d` were recovered before further work. The primary checkout changed independently; its later `main` changes have not been merged here. This worktree is an isolated checkout of the same repository, not a competing creative archive.

Phase A evidence and Phase B local workflow proof are delivered. **Phase C remains open at likeness and physical-credibility acceptance.** Some Phase D technical features are implemented, but Phase D and final Phase E acceptance are incomplete.

1. Review the revised body/leg/head balance against both selected references. Resolve proportions before adding high-cost surface and animation work.
2. Refine the approved silhouette into irregular layered armor, continuous cheek/neck forms, substantial repaired legs and convincing handworked materials; author corresponding era variations without changing established narrative uncertainty.
3. Build and verify production joint travel, weight response and a claw/cage gesture. Retain cancellable state control and inspection safety.
4. Measure real GPU and physical mobile performance, optimize while preserving identity, and complete human accessibility/audio review.
5. Reconcile the independent primary branch, validate clean-clone LFS retrieval, rerun applicable checks, and obtain separate publication authorization before remote release.

No local check in this report is artistic acceptance or evidence of a successful live deployment.
