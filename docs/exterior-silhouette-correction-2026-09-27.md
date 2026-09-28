# Breast, neck, and folded-mantle geometry correction — 2026-09-27

**Status:** regenerated local review candidate; not owner-accepted final art and not published. This is a bounded geometry-only correction to the shared body, not a new reference decision or a claim of likeness approval.

## Scope and changes

Candidate 03 remains authoritative for the common full-body breast and folded-wing silhouette. Maker-clean and Mechanic remain scoped to fabrication and inherited aging/repair, respectively. Advanced is still the user-facing name for the `builder` export.

- **Breast:** reshaped the shared access-shell profile to fill the upper sternum and taper toward the waist. Twenty fitted overlap plates now follow five staggered courses instead of four regular courses. The rear shell and separate internal assemblies were not moved.
- **Visible neck:** widened and swept the existing cervical rails and overlapping shingles along a more legible S-curve. The four curved shell/frame shingles and diagonal link plates remain rigid parts on the existing neck assembly; no head or neck pivot was moved.
- **Shoulder-to-elbow mantle:** broadened the curved shoulder shells and replaced twenty short overlap leaves per shoulder with sixteen wider leaves in four rows. The bearing window remains open and each forewing shield remains a separate elbow assembly.

No head, bill, jaw, crown, optic, leg, foot, runtime, UI, controller, audio, fallback-image, release-manifest, or dependency changes were included. The one-sided repair restriction, flightless wings, era eligibility, and distinct power/processing roles remain unchanged.

## Visual record

Nine 800×800 Blender Cycles authoring renders use the regenerated model, the existing neutral-light setup, and 12 samples: front, side, and three-quarter views for Maker, Mechanic, and Advanced. The model retains its era-specific surface treatment in these views; they are not texture-free clay renders or measured reference drawings.

- [Nine-view contact sheet](../assets/audit/exterior-v1/geometry-correction-2026-09-27/silhouette-contact-sheet.jpg)
- Individual views: `maker-neutral-{front,side,three-quarter}.png`, `mechanic-neutral-{front,side,three-quarter}.png`, and `builder-neutral-{front,side,three-quarter}.png` in the same audit directory.
- [Advanced WebGL exhibit overview](../assets/audit/exterior-v1/geometry-correction-2026-09-27/builder-webgl-exhibit-overview.png) is a local headless Chromium software-render capture of the running Vite app, not a neutral likeness view or a hardware-performance test.

The managed app-preview screenshot browser could not create a WebGL context. Local Chromium with ANGLE/SwiftShader did render the 3D exhibit. The direct dev-server request for the combined GLB returned HTTP 200 and the same SHA-256 as the regenerated file. The full headed-browser screenshot suite was **not run** for this correction.

## Validation

| Claim | Tier | Evidence | Consequence if false | Next check |
|---|---|---|---|---|
| The change stayed within the three requested geometry regions. | Confirmed | Source diff is limited to breast/shoulder geometry in `scripts/exterior-body-regions.py` and cervical geometry in `scripts/exterior-head-neck.py`; no runtime or review-manifest edits. | Out-of-scope behavior or reference changes would be mixed into this candidate. | Recheck the scoped diff before any later integration. |
| Fourteen named contract nodes kept their previous transforms and parent names. | Confirmed | Parsed pre-correction and current combined GLBs; `body`, `neck`, `head`, `jaw`, `breastplate`, `cranial-cover`, both mantles, both wing shields, `power-core`, `processing`, `builder-optics`, and `bill-contact` had zero differences. | Runtime attachments, articulation, or inspection could be displaced. | Keep the existing motion and ownership checks when making later geometry edits. |
| The generated model set is internally consistent and serves from the dev app. | Confirmed | All 12 generated-file hashes match `assets/models/uncaged-exterior-v1/exterior-inventory.json`. The combined GLB is 16,870,136 bytes, SHA-256 `c41a7b10237373336bb585840295a1fea282ba17f13d5f0cebc68ba412be3c6a`; the same bytes were returned by the running dev server. | Review evidence could describe assets different from those served. | Recompute receipts after any regeneration; only package for release after review approval. |
| The targeted construction and motion contracts passed. | Confirmed | `construction-validation.json` 3/3; `motion-validation.json` 14/14; `structural-motion-validation.json` 4/4; `power-move-validation.json` 4/4; `mechanism-validation.json` 7/7; `source-placement-validation.json` passed for 48 current overlays at its 2 mm sampling tolerance. | A tested ownership, era, movement, or plate-placement contract could be broken. | Use these checks again after future geometry changes; they do not prove exhaustive collision freedom. |
| The correction improves the intended reference likeness. | Inferred | The new neutral views visibly show a fuller upper breast with a narrower lower profile, a curved neck, and broader layered mantle. These are visual observations, not owner evaluation. | Calling the result accepted would overstate what the evidence establishes. | Obtain the owner's direct comparison and decision. |
| The candidate has owner likeness acceptance or supervisor handoff. | Unknown | No acceptance or detailed inspector handoff is recorded in the current project evidence. | Treating the candidate as approved would be misleading. | Request and record explicit review of the nine neutral views. |
| A production/review package is ready. | Confirmed: no | `npm run build` completed Vite's production compilation, then `scripts/prepare-review-release.py` stopped on a source byte-size mismatch because `assets/review/exterior-v1-publication.json` still pins the previous combined model. The manifest was intentionally left unchanged; the package has not been advanced or published. | Publishing now would bypass the existing review boundary. | Do not change the public pin until a separately authorized review/package step. |

## Remaining boundary

The geometry is a proposal derived from perspective illustrations, not recovered dimensions. The owner still needs to judge the breast taper/panel rhythm, visible neck mass, and amount of mantle wrapping around the shoulder and elbow. Head/bill identity and lower-leg/foot construction remain separate unresolved likeness areas. The current static fallback images and public review manifest were not regenerated, by design; a non-WebGL fallback is not evidence of this correction.

The legacy asset audit still expects 28 `dist` files and observes 50 in the current Vite output. That count check is stale for the present bundle and was not changed as part of this geometry task. The available app-preview screenshot browser's WebGL failure is also not evidence that the running 3D scene is broken; the local software-render smoke is not evidence of target-device GPU performance.