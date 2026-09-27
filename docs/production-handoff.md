# MurderBird: Uncaged — local production handoff

**Status:** The local exhibit now implements an anchored, externally articulated Maker, a limited spring-driven Mechanic, and an Advanced encounter with pacing, visitor response, jump, shield thrust and grounded inspection. See the [three-era review](three-era-movement-review.md), [demonstration](../assets/audit/three-era-review/era-review.html), [requirements](uncaged-requirements.md) and [creative authority](creative-authority.md). Exact mechanisms and character acting remain proposed; owner likeness acceptance and publication are pending.

## Current source and runtime

- Authoring script: [`scripts/build-uncaged-presence-study.py`](../scripts/build-uncaged-presence-study.py)
- Editable Blender source: [`assets/models/uncaged-presence-study/murderbird-presence-study.blend`](../assets/models/uncaged-presence-study/murderbird-presence-study.blend)
- Browser GLB: [`assets/models/uncaged-presence-study/murderbird-presence-study.glb`](../assets/models/uncaged-presence-study/murderbird-presence-study.glb)
- Era capabilities and power-action controller: [`src/scene/era-controller.js`](../src/scene/era-controller.js), delegating the Advanced encounter to the retained [`presence-state.js`](../src/scene/presence-state.js)
- Separate procedural motion paths: [`src/scene/era-motion.js`](../src/scene/era-motion.js)
- Proposed runtime construction: [`src/scene/era-mechanisms.js`](../src/scene/era-mechanisms.js)
- Three.js exhibit: [`src/scene/presence-exhibit.js`](../src/scene/presence-exhibit.js)
- Current evidence: [three-era demonstration](../assets/audit/three-era-review/era-review.html), [report](three-era-movement-review.md), and [provenance](../provenance/three-era-runtime-2026-09-27.json)
- Preserved body source and earlier evidence: [Stage Two report](stage-two-encounter-review.md) and [model provenance](../provenance/uncaged-presence-study-2026-09-27.json)

The unchanged Blender source contains **2,038 mesh objects, 39 empties and no armature**. Its GLB contains **24 meshes, 63 nodes and 89,068 unique triangles**. The editable geometry is grouped into rigid body, head, shoulder/elbow, leg and toe assemblies. One short `attention-export-proof` head-rotation action exports as a glTF clip; the continuous encounter is procedural runtime motion, not an authored animation library or skinned character.

Legs use thigh → shin → ankle-pivot foot → toes groups. The runtime solves the two leg links to preserve world-space planted foot targets during travel and turns. The head can track a target; the Builder waits for alignment and planted support before committed contact. A dedicated upper-bill leading vertex is checked against the selected cylindrical cage bar. These are kinematic, tested constraints; they do not prove physical mass distribution, force transfer, collision response outside the tested bars, or engineering feasibility.

The owner’s raptor comparison informs speed, attention, and tension only. MurderBird keeps bird anatomy, a compact rear outline, hooked bill, bird feet, and flightless folded wings. The wings brace and shield with a short shoulder/elbow drive; do not add a dinosaur body, tail, or flight motion. Fictional heart and processing assemblies remain separate Builder additions; unseen internal layouts are reconstructions, not story facts.

## Review and known limits

The [three-era review](three-era-movement-review.md) describes current capture and validation results; Stage Two remains historical. It records passing pure-state tests, the actual GLB motion/integration checks, source/build validation, and local browser encounter/regression groups. Automated checks establish sampled kinematic and interaction behavior; they do not approve likeness, weight, acting, or final character art. The review capture uses local software and should be consulted for its hardware, browser, and viewport limits.

Owner likeness acceptance remains open. Captured views show improvement over the prior barrel-like form, while bill/cheek identity, neck transition, armor repetition and surface wear still need refinement. The runtime has no skinned armature and no finished authored motion library or claw-grip action. A toe-group lift during a step is not a claw strike. Maker remains anchored with five explicit external controls. Mechanic now has slow, finite spring-driven traversal without visitor awareness. Advanced has the responsive encounter plus controlled jump and planted shield thrust; it requires no ordinary winding or power recovery.

Human accessibility review, screen-reader testing, physical-phone/Safari/Firefox coverage, remote CI, clean-clone LFS retrieval, deployment, and publication approval remain unverified. The local build/allowlist receipt is not a remote deployment claim. Source models, captures, provenance and review pages stay out of `public/` and `dist/` except explicitly referenced approved runtime files.

## Reproduce and verify

Use the managed production worktree, not the independently active primary checkout. Blender 5.2 is the authoring target; regeneration overwrites the named `.blend` and `.glb`, so preserve any manual modeling work as a new version first.

```sh
npm ci
npm run build
node --test tests/*.test.mjs
node scripts/verify-era-motion.mjs
node scripts/verify-advanced-power-moves.mjs
python3 scripts/verify-era-assets.py
```

The browser capture and regression scripts use the already-installed Playwright entry point and a loopback preview; they add no application dependency:

```sh
PLAYWRIGHT_ENTRY="/Users/okh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs"
npm run dev -- --host 127.0.0.1 --port 5174
npm run preview -- --host 127.0.0.1 --port 4176
node scripts/capture-three-eras.mjs "$PLAYWRIGHT_ENTRY"
node scripts/verify-era-browser.mjs "$PLAYWRIGHT_ENTRY"
node scripts/verify-advanced-power-browser.mjs "$PLAYWRIGHT_ENTRY"
node scripts/verify-era-review.mjs "$PLAYWRIGHT_ENTRY"
```

Run the development server on **5174** and the production preview on **4176** in separate terminals; the capture/regression uses 5174 and the regression's production-build checks use 4176. The Playwright entry shown is the existing local QA installation, not a project dependency. On another host, set the quoted variable to that host's existing `playwright/index.mjs` entry point. Run GPU browser scripts sequentially. The verified local checks and exact receipts are in the [three-era review](three-era-movement-review.md). After a build, inspect every emitted `dist/` path and asset URL. A successful local build does not satisfy repository release rules or authorize publication.

## Preserved earlier studies

The earlier source, exports, and captures under `assets/models/uncaged-study/`, `assets/models/uncaged-mass-study/`, and `assets/models/uncaged-shield-study/` and their corresponding `assets/audit/uncaged-review/`, `uncaged-mass-review/`, and `uncaged-shield-review/` directories remain intact. Their prior review documents record historical status and tests at those checkpoints; do not treat their old model paths, test results, or limitations as the current Stage Two inventory. The Stage Two presence model is reused unchanged. Three-era motion and mechanisms are a new runtime derivative; the new geometry is not baked into that Blender/GLB pair.
