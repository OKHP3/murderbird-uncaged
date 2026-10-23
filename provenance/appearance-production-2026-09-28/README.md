# Appearance production historical handoff

This directory reconciles the September 27–28 appearance thread's retained source and evidence into the canonical repository. It is an archive of a **below-likeness, owner-unaccepted candidate**, not the current model, a runtime selection, or a release approval. Current authority is [goal.md](../../goal.md); its cinematic CG track supersedes the old v3-based sequence and mechanics-first ordering.

The [closeout handoff](../../docs/handoffs/appearance-thread-closeout-2026-10-22.md) records the retirement of this superseded study and the existing CG backlog that retains its unmet visual goal. Preserving and integrating this record does not claim that the model looks like the source pictures and videos.

## What was preserved

- Source snapshot `7da906d1f59bbcb75c533354cdbcc145ccb690f2`, parent `3e6d340e616e79708d2a62ec9255fd997d14ea4f`.
- [Manifest](manifest.json): all 492 changed paths, Git blob and actual payload identities, plus comparison with main `2f0d919cb89aedc6a00575e686e81baa3bd2d27e`. Of these, 37 assessment paths already matched main, 451 production paths were absent, and four historical runtime files differed.
- [Frozen selection](canonical-selection.json): byte-exact historical production documents, authoring and verification scripts, iteration-08/09 frozen authoring sources, and iteration-09 technical/art/browser/delivery receipts. These copies are retained under `source/` with their original relative paths. They are not active application tooling.
- [Preservation verification](preservation-verification.json): dedicated bundle and scoped LFS archive hashes. All 317 LFS paths resolve to 309 distinct payloads totaling 1,224,824,170 bytes. All archived payloads passed SHA-256 and size verification on October 22.
- Full nine-iteration model, image, gallery and video evidence remains in the local recovery package described in [restore instructions](restore.md). This repository record does not claim those bulk binaries were uploaded to GitHub.

Historical Markdown links and localhost URLs inside `source/` describe the original snapshot layout and session. They are deliberately unchanged; they need the restored snapshot to resolve. Statements such as “selected by the local application” refer only to that September worktree. Its original `.local/publication/build-validation.json` was ignored and is absent from the snapshot; retained delivery evidence summarizes that historical build but does not recover every ignored QA file.

## Reuse boundary

Do not execute relocated scripts or replay the four archived runtime changes against current main. The scripts derive paths from their original repository layout. A safe restoration proves byte custody, not deterministic regeneration or compatibility with today's CG model.

Iteration 09 depends on iteration 08: native SHA-256 `ea6c9a235106810e8056401467a13863fdbb0a215589375321101d5894b53c33`, inventory `b0f5eaf91e588a9d2986a09b4f861d3d1bb9660227af6088d054cdd7bb197ef6`, and six frozen authoring scripts. Iteration 09 freezes only the material and refinishing scripts. The material `assign()` path clears color attributes, replaces UVs/material slots and face assignments; the refinishing wrapper joins, renames and unhides meshes. Geometry/hierarchy parity alone does not cover those changes. A future material port requires the current checkpoint's explicit role mapping and independent validation; no Stage C port is claimed here.

All MurderBird creative material remains all rights reserved under [NOTICE.md](../../NOTICE.md). Code licensing remains as recorded by the repository. Nothing in this archive changes creative status or grants publication authority.
