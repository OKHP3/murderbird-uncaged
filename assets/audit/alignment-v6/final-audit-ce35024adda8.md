# Independent closeout audit — v6 sixth candidate

Audit date: 2026-09-28 UTC. Read-only review except for this uniquely named note. No suite was rerun.

## Findings

No material source-selection, preservation, scope, or publication-boundary defect was found in the reviewed sixth-candidate closeout.

The active exhibit selects `assets/models/uncaged-alignment-v6/murderbird-alignment-v6.glb`; the fallback selects the v6 Maker, Mechanic and Builder preview paths. `main.js` continues to load the existing presence exhibit. The only tracked code diffs in this checkout are those v6 asset-path selections and the publication verifier's default/allowlist update to accept v6. No tracked motion, material, or interaction implementation change appeared in the diff.

The current GLB SHA-256 is `ce35024adda89681a0f37e7018e2563a74af67cd06558a887222df87b78a87fe`; the editable source SHA-256 is `5a7a51941423dd0efcb48b9641b7a49597dad117e218ccb4e94f26315c5e9ded`. Both match the v6 inventory. All 12 inventory-generated files exist with declared byte counts and hashes. The current asset-validation, jaw/head + jaw/neck + optic receipts, six-validator suite and browser evidence all name this same model SHA where applicable. The 17 current runtime/test/package source hashes captured before the six-validator suite still match the checkout at this audit.

The local build-boundary receipt is for the same model and reports 133 emitted files / 16 exact media assets. I compared the receipt to the actual `dist/` tree: all 133 paths match, with no missing or unlisted files. No audit tree, Blender source, generation source, provenance, private-session or archive-named file appears in `dist/`. `git diff --check` is clean. This establishes the current local build boundary only; it does not establish remote CI, deployment, or owner approval.

The review document consistently labels this as a neutral proposal, keeps likeness revision required, records the third/fourth clearance failures and sixth passing sampled checks, and states the limits of collision, motion and browser evidence. It does not claim physical simulation, learned AI, deployment, or artistic acceptance. Its separate contact-gated strike recording is present in the current evidence manifest with completed sequence metadata; the earlier warning-only scripted sequence remains accurately described as approach/retreat evidence.

## Limits

This was a bounded source, hash, receipt, documentation and built-file audit. It did not rerun the build or validators, inspect every rendered frame, or conduct artistic/owner review. The gallery metadata was in the process of being updated during this assignment and is not adjudicated here as final. Nothing in this audit promotes the candidate beyond the review status recorded in its inventory.
