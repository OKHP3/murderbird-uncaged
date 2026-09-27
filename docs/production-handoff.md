# MurderBird: Uncaged — local production handoff

**Current checkpoint: structural reconciliation v1, at the early visual review gate.** The three-era controls remain, and the app loads a new versioned neutral structural study. Owner likeness acceptance is **pending**. The independent reference review still flags bill depth/curvature, a boxy crown, a tall/straight neck and repetitive breast layering. This checkpoint must not be described as a finished recognizable character or an approved exterior.

The evaluated starting point was `2c22a50d8e8f39982992cd3ce1ada5b098c5a34e`, verified clean in `/Users/okh/.codex/worktrees/uncaged-production/murderbird-uncaged`. The independently active primary clone was used read-only for selected hash-verified preserved media and repository skill guidance. Work continues in the production worktree. No publication or remote synchronization is claimed.

## Current deliverables

- [Early neutral likeness review](../assets/audit/structural-reconciliation-v1/likeness-review.html): identical-camera before/after front, side, three-quarter, rear reconstruction and head detail; selected references remain separately labelled perspective artwork.
- [Reference audit](structural-reference-audit.md), [regional construction contract](structural-construction-contract.md), [era eligibility matrix](structural-era-eligibility.md), and [checks / remaining decisions](structural-reconciliation-review.md).
- [Continuous 1:54 motion demonstration](../assets/audit/structural-reconciliation-v1/structural-motion-demonstration.mp4), [final preview receipt](../assets/audit/structural-reconciliation-v1/final-preview-validation.json), and [version provenance ledger](../provenance/structural-reconciliation-v1-2026-09-27.json).
- Editable source: [`assets/models/uncaged-structure-v1/murderbird-structure-v1.blend`](../assets/models/uncaged-structure-v1/murderbird-structure-v1.blend).
- Runtime derivative: [`assets/models/uncaged-structure-v1/murderbird-structure-v1.glb`](../assets/models/uncaged-structure-v1/murderbird-structure-v1.glb).
- Authoring: [`scripts/build-uncaged-structure-v1.py`](../scripts/build-uncaged-structure-v1.py); named pivots and removed shared powered components: [construction inventory](../assets/models/uncaged-structure-v1/construction-inventory.json).
- Runtime: `src/scene/era-controller.js`, `era-motion.js`, `era-mechanisms.js`, `presence-exhibit.js`; `presence-state.js` retains the Advanced encounter state logic with the corrected closer approach position.

The editable source preserves **1,276 separate mesh objects** and rigid named groups. The current GLB contains **23 meshes, 62 nodes, 63,468 indexed unique triangles, no skins**, and one `attention-export-proof` clip. Continuous motion remains procedural. Runtime-only Maker support/controls, Mechanic spring/cam drive, Advanced distribution/actuators, and short tail remain editable in `era-mechanisms.js`; they are not baked into the Blender/GLB pair. Regeneration verifies the historical source hash and writes only the new version path. Preserve any subsequent manual source edits as another version before regeneration.

## Structural decisions and constraints

The bill is now physically divided into formed panels, the cheek/mandible is open geometry, the cervical load frame has fixed base and skull attachments, and the shoulder assemblies sit lower. The breast/rear envelope is rebuilt around a tapered pelvic frame. Eighteen shared actuator/piston/hydraulic/take-off meshes were removed, and the unused duplicate winding-drive meshes were removed while retaining the interface empty. Passive structural rails remain common; motion sources are era-specific. The left repair bracket follows its corrected shoulder pivot, and restricted travel remains asymmetric.

MurderBird remains a flightless mechanical bird. Wings balance, shield and deliver a tucked short shoulder/elbow shove. No dinosaur tail, long hanging wing train, humanoid hand, biological tissue, or flight action was added. July controls the head only; candidate 03 controls the selected whole-body identity. Original story files remain unchanged, including finite-energy wording that differs from the owner's Advanced exhibit premise.

Movement is kinematic. Fixed attachments, bounded rotation, foot targets and contact sampling do not establish physical simulation, collision-free continuous dynamics, feasible load ratings, or artistic acceptance. The updated review records exactly which sampled checks ran and their limits.

## Local review and verification

Development: <http://127.0.0.1:5174/>. Local build preview: <http://127.0.0.1:4176/>. The review HTML is a development-served audit artifact, excluded from `dist/`. Review and proof media, source Blender files, provenance and source archives remain outside `public/` and the shipped runtime allowlist.

```sh
npm ci
npm run build
node --test tests/*.test.mjs
node scripts/verify-era-motion.mjs
node scripts/verify-advanced-power-moves.mjs
node scripts/verify-structural-motion.mjs
node scripts/verify-structural-mechanisms.mjs
python3 scripts/verify-structure-assets.py
```

The two retained motion validators now default to the active structural model and the new audit directory. `UNCAGED_MODEL` and `UNCAGED_AUDIT` can select explicit alternatives. Existing historical receipts were not overwritten. Browser validators use the already installed Playwright module; no application dependency was added. Run browser/render capture jobs sequentially on the local GPU:

```sh
PLAYWRIGHT_ENTRY="/Users/okh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs"
node scripts/verify-era-browser.mjs "$PLAYWRIGHT_ENTRY"
node scripts/verify-advanced-power-browser.mjs "$PLAYWRIGHT_ENTRY"
node scripts/capture-structure-motion.mjs "$PLAYWRIGHT_ENTRY"
node scripts/verify-structure-review.mjs "$PLAYWRIGHT_ENTRY"
```

The explicit local build validator checks 26 intended runtime files and source-to-build GLB identity. A successful local build does not prove remote CI, clean-clone LFS retrieval, deployment, or human accessibility/art review. Refer to the current receipts rather than this reproduction list to know what actually passed.

## Next decision

The owner was shown the neutral matched views and asked whether to refine this direction or rework head/bill or body/neck proportions. That early gate is pending. Do not treat silence, a completed motion demonstration, or passing tests as approval. Continue structural corrections from the owner's response before detailed surfacing. Preserve the v1 review so later before/after claims remain inspectable.

The previous presence-study source/export and [three-era review](three-era-movement-review.md) remain the preserved `2c22a50` checkpoint. Earlier study, mass, shield and Stage Two files remain intact and retain their dated status.
