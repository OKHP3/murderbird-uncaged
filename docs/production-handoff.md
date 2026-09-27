# MurderBird: Uncaged — local production handoff

**Status:** a reference-informed full-body prototype and local interactive slice are present in the managed worktree. See the [acceptance report](acceptance-report.md) for executed checks, artifact hashes, failures and limitations. Owner likeness review, visual acceptance, and any remote publication remain pending; remote publication is not authorized. See [working requirements](uncaged-requirements.md) and [creative authority](creative-authority.md).

## Source and outputs

- Authoring script: [`scripts/build-uncaged-study.py`](../scripts/build-uncaged-study.py)
- Editable Blender source: [`assets/models/uncaged-study/murderbird-study.blend`](../assets/models/uncaged-study/murderbird-study.blend)
- Browser export: [`assets/models/uncaged-study/murderbird-study.glb`](../assets/models/uncaged-study/murderbird-study.glb)
- Runtime loader and assembly contract: [`src/scene/exhibit.js`](../src/scene/exhibit.js)
- Encounter sequence: [`src/scene/encounter-state.js`](../src/scene/encounter-state.js); controls and copy: [`src/main.js`](../src/main.js)

The script is deterministic at the authoring level (fixed random seed), operates locally, creates new geometry, saves the editable `.blend`, then exports the GLB. It does not reconstruct certified hidden surfaces. The `.blend` keeps individual editable plates and fasteners. The GLB batches render meshes by named articulated assembly/material for browser delivery. It has no authored claw animation; scripted Three.js motion currently moves the bill/jaw/neck during the approach sequence.

The required root groups are `murderbird`, `body`, `neck`, `head`, `jaw`, `breastplate`, `cranial-cover`, `winding-drive`, `power-core`, `processing`, `industrial-repairs`, `builder-optics`, `left-mantle`, and `right-mantle`. The browser checks for the 13 named component groups from `body` through `right-mantle` before it accepts the model. Child mesh names describe proposed geometry such as the hooked upper bill, lower mandible, peened fasteners, shoulder repair, cavity, spring drive, ceramic cells, and processing lattice. The exact `export_scene.gltf` call and grouping pass are at the end of the script. The app's inspection view opens the breastplate and cranial cover, hides era-inapplicable systems, and offsets selected groups for the exploded view.

## Reproduction

Start in a clean, authorized local checkout of this branch. Do not use the independently active primary checkout. Node must satisfy the `package.json` engine range (`>=24 <27`); Blender 5.2 is the script's authoring target.

```sh
npm ci
npm run build
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/build-uncaged-study.py
npm run build
```

The Blender command overwrites both named study outputs. Preserve any local edits before regenerating. The second build checks the newly written runtime asset is resolved into Vite output; inspect `dist/` and confirm only intentionally referenced runtime content is present. The acceptance report records the commands actually run on this branch. For a machine where Blender is exposed on `PATH`, substitute its verified executable. No package additions or network services are required by the code path.

## Review gaps and status limits

- **Visual acceptance:** initial proportions required owner-requested rework; the revised study awaits owner acceptance. Compare the output at matching angles against the owner-preferred July head reference and lead-selected candidate 03. The 2.0 m value is a production convention, not an established story measurement. The owner likeness decision remains pending.
- **Claw animation:** claws are present as geometry; no animated talon action is implemented. The encounter sequence animates anticipation, bill/jaw, and a constrained neck slide to the visible rail. It is a scripted approximation, not collision physics.
- **Historical/technical claims:** winding, power, processing, and internal layout are proposed shapes. The script labels their provenance as illustrative; preserve the Maker and Mechanic uncertainty in copy.
- **Browser acceptance:** the app uses the existing Three.js `GLTFLoader`; it includes orbit/zoom, part focus, assembly separation, reassembly, era controls, optional sound, reduced motion, and an illustrated fallback. The acceptance report records passing local browser checks and their limits. Those checks do not establish human usability, screen-reader or physical-device acceptance.
- **Build/deployment:** the acceptance report establishes a successful local build and inspected output. Remote CI, LFS retrieval from a clean clone, Pages deployment and human release approval remain unverified. Follow the repository's release gates before publication.

The [asset capability audit](asset-capability-audit.md) and [production workflow](production-workflow.md) described the baseline inventory at commit `0d40329`, before this prototype existed. Their baseline findings should not be read as the current file inventory; their acceptance limitations remain relevant. Current work arrived through commits `3409121` and `6042b5d`, followed by recovered local prototype edits. The root agent moved this work into managed branch `codex/uncaged-production-review`; the latest primary `main` was not integrated here and has independent active work that must be preserved. Treat that cross-checkout history as coordination context, not proof of remote publication or synchronization.

## Repeat the local checks

`node --test tests/encounter-state.test.mjs` runs the dependency-free response-state checks. After building, `python3 scripts/verify-uncaged-assets.py` validates the real GLB, required nodes, local build allowlist and pointer absence. `scripts/verify-uncaged-browser.mjs` accepts the path to an already installed Playwright entry module; Playwright is QA tooling and is not added to the app. Start the loopback preview on port 5174 or set `UNCAGED_URL` to another loopback URL. The browser check writes review evidence outside the runtime bundle under `assets/audit/uncaged-review/`.

The native source currently contains 3,017 mesh objects, 13 component groups plus root and seven named landmarks. `bill-contact` and `anchor-*` move with authoring changes. Keep those landmarks rather than hard-coding a new contact offset in the browser. Before regenerating, save any manual modeling work as a new source version; the generator replaces its two named study outputs. The approximate two-metre convention must not be promoted into story canon.
