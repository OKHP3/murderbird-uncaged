# MurderBird: Uncaged — local production handoff

**Current stage: three exterior construction states v1, technically validated but not yet meeting the full artistic likeness criteria.** This continues the clean structural checkpoint `21ac417` in `/Users/okh/.codex/worktrees/uncaged-production/murderbird-uncaged`. The owner's subsequent exterior brief authorizes continued geometry and surfacing work; it does not retroactively approve the previous likeness study. The original evaluated checkpoint `2c22a50` and all historical production assets remain preserved. Nothing in this handoff is a publication claim.

## Current deliverables

- [Direction review gate](../assets/audit/exterior-v1/direction-gate.html): the current three-quarter and side beside Candidate 03; owner answer pending.
- [Exterior review](../assets/audit/exterior-v1/exterior-review.html): selected references, neutral authoring renders, browser views in two lighting setups, anatomical close-ups, inspection, extreme poses and matched clay before/after views.
- [Stage record and remaining decisions](exterior-stage-record.md), [regional material/attachment map](exterior-regional-map.md), and [surface production contract](exterior-surface-pipeline.md).
- [Versioned source and exports](../assets/models/uncaged-exterior-v1/README.md): editable Blender source, combined runtime GLB, three individual era GLBs, seven PBR maps and fixed fallback renders.
- [Component inheritance inventory](../assets/models/uncaged-exterior-v1/exterior-inventory.json): source hash, per-piece era, material role, regional assignment and rigid attachment.
- [Motion demonstration](../assets/audit/exterior-v1/exterior-motion-demonstration.mp4), [browser/performance receipt](../assets/audit/exterior-v1/browser-validation.json), [asset/build receipt](../assets/audit/exterior-v1/asset-validation.json), and [construction checks](../assets/audit/exterior-v1/construction-validation.json).

The application preserves Vite, Three.js, Web Audio and the existing three-era controls. Maker support and external controls, Mechanic spring/cam transmission, and Advanced distribution/actuation remain authored in `src/scene/era-mechanisms.js`; continuous articulation is in `era-motion.js`. These runtime mechanisms are not baked into the Blender or individual GLB review exports. The source and runtime derivative keep crown/breast covers, shoulder/elbow shields and leg/toe assemblies separate. No biological tissue or deforming metal skin was added.

## Authority and continuity

Candidate 03 controls the full-body identity. July controls the head only. Maker-clean informs the newly fabricated state before immersion; later material aging and repair belong to Mechanic and Advanced. Heart supports a pale, accessible chest power unit, with sensing and processing separate. First Choice supports restrained story-page continuity, not approval of jumps or attacks. Exact hidden construction, repairs, surface history and dimensions remain proposed.

MurderBird is flightless. Its compact wings balance, shield and perform a short tucked shoulder/elbow shove. The anatomical-left travel limit stays asymmetric. Advanced upgrades retain inherited plates and repairs. The original story snapshot remains unchanged, including its finite-power wording; the owner's abundant-power exhibit premise is recorded separately.

Movement is kinematic. Fixed attachments, foot targets, sampled contact and rendered pose review do not establish physical dynamics or an exhaustive continuous collision proof. Technical checks do not settle recognition, proportions, material history or acting quality.

## Reproduction and local boundary

Development: <http://127.0.0.1:5174/>. Local build preview: <http://127.0.0.1:4176/>. The review gallery is served only from the development tree, outside the runtime output. No provenance, source scene, historical archive or audit gallery belongs in `public/` or the shipped runtime.

```sh
npm ci
npm run build
node --test tests/*.test.mjs
node scripts/verify-era-motion.mjs
node scripts/verify-advanced-power-moves.mjs
node scripts/verify-structural-motion.mjs
node scripts/verify-structural-mechanisms.mjs
node scripts/verify-exterior-construction.mjs
python3 scripts/verify-exterior-assets.py
```

Motion checks load unchanged GLB geometry/transforms but remove image bindings from an in-memory copy because Node does not provide browser image decoding. Hardware-WebGL review separately checks the actual textured export. The validators default to the exterior version and new receipt directory; old receipts remain intact.

Use the already installed Playwright entry with `scripts/verify-exterior-browser.mjs`, then run the retained era/power browser regressions with `UNCAGED_AUDIT=assets/audit/exterior-v1/regression`. Run GPU-dependent browser jobs and render capture sequentially. Record motion with `scripts/capture-exterior-motion.mjs`, then encode its recording to the review MP4. Assemble the gallery with `scripts/build-exterior-review.py`, then check the built controls and gallery with `scripts/verify-exterior-review.mjs`. Run `scripts/verify-exterior-source.py` through Blender for the 56 overlay-placement samples and legacy-thigh exclusion.

The frozen combined GLB is 16,956,956 bytes, SHA-256 `3ec668b0b9bbaf1cb546ec2e04b09030c5f45b0f0893adc5b7fe5aa57baacdc5`. The stage record names the exact build assets and observations. Earlier exterior iteration A and rejected-pass diagnostics remain preserved.

Regeneration uses `scripts/build-uncaged-exterior-v1.py` in Blender and verifies both the historical structural source and previously generated output hashes. Preserve any manual changes under a new version before regenerating. `render-exterior-authoring.py` creates authoring and matched clay proofs without saving changes into the source scene.

Use the current dated receipts and stage record for the checks actually performed. Local validation does not prove remote CI, fresh remote LFS retrieval, deployment, phone performance or owner acceptance. The primary clone was used read-only for guidance and preserved source media; this work remains in the production worktree.
