# MurderBird correction — independent regression and visual review

This is a local, partial assessment from the delegated correction program. The neutral v4 geometry and appearance candidates are still being revised in their own worktrees. No new candidate is owner-accepted or published by this work.

## What was corrected

Commit `b523c3a` preserves the explanatory caption when an illustrated preview fails to load. Previously, inspection, separation, resize, or a same-era refresh could replace the error caption while leaving the image hidden. Switching to a different era now clears the failed-image state and allows that preview to load normally.

Commit `4c95de4` extracts the active exported-model inspection transforms into a small shared function. This keeps the existing offsets and ordering while allowing the actual production transform code to be exercised against the exported model. It does not redesign the inspection mechanism or certify collision freedom.

## Candidate identities and ownership

The QA checkout is `/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged`, branch `codex/review-regression-v4`, based on `3e6d340e616e79708d2a62ec9255fd997d14ea4f`. The `v4` in the QA folder and script names identifies this correction workstream; most regression evidence here deliberately uses the frozen **alignment-v3 model**:

- Model: `assets/models/uncaged-alignment-v3/murderbird-alignment-v3.glb`.
- SHA-256: `c4dc308f77399410368b82443a1b21b9113cfedb258aa055906b4f13c92dda21`.
- Size: 3,370,292 bytes.
- Tested browser preview: `http://127.0.0.1:5183/`; controlled failure fixture: `http://127.0.0.1:5184/`. These temporary test processes and their test tab were stopped after the checks; saved evidence remains available below.

The production geometry worktree owns v4 geometry and motion. The appearance worktree owns regional surface proposals. Their source files and models were not overwritten by these QA changes. The fallback fix and inspection extraction were integrated there as `7e35a80` and `698c049`, respectively. Uncommitted owner work in the primary clone remains intact.

## Evidence that ran

| Check | Observed result | Boundary |
| --- | --- | --- |
| Node unit suite | 54 tests passed after fallback and telemetry changes. | Unit behavior, not visual acceptance. |
| Actual-model interruption checks | Four check groups passed: five inspection cycles per era, two ten-input reach batches, 12 era/action interruption combinations, jump/thrust pause and inspection recovery. | Advanced connector disengagement/restoration is exercised; Maker and Mechanic connectors are ineligible. Connector restoration is distinct from exterior restoration. A retained-rig controller reset during an airborne jump is an explicitly non-gating API diagnostic; it is not the public app reset path. |
| Shared exterior inspection transforms | Five cycles per era; 6/6/8 eligible owners moved locally and in world space, and all 21 mapped descendant mesh world matrices restored exactly. | Fixed exported rest pose. Era eligibility is mirrored fixture setup, not a test of the browser's era-switch wiring. No collision or vertex deformation certification. |
| Two fresh accelerated acting traces | 120 simulated seconds per seed; 1,201 samples per run; five cage-test episodes in each. | These are actual-GLB kinematics, not two uncut browser videos or continuous human acting review. |
| Model loading and fallback image | First two model requests failed; public retries restored an actual 3D canvas. A missing Maker preview retained its explanation through inspection and 75% separation; Mechanic artwork loaded after switching eras. The story/media folio remained reachable. | Controlled local failure fixture, not a deployed-site test. |
| Graphics loss | Two native WebGL context-loss cycles returned to labeled illustrated mode and recovered through public Retry 3D. | Single desktop in-app browser. |
| WebGL unavailable | An unavailable WebGL context on retry retained useful illustrated content and explanatory status; restoring the original context method allowed recovery. | Startup injection was unsupported and was not executed. The tested failure occurred during retry. |
| Theme media failure | A blocked full-song fetch showed a retry message. After unblocking, Play loaded the 2:27 song and advanced its clock; Pause stopped it. | Playback was muted. No audible quality or loop-seam acceptance. |
| Extracted inspection UI | Public Open, 100% separation, and Reassemble moved actual plates and restored `open=0`, `separation=0`, with encounter controls and movement returning. | One Advanced browser cycle; full model-transform proof is a separate check. |
| Build and delivery boundary | Captured build, publication inventory validation, and theme release validation passed on the QA baseline. The build emitted 134 files and 16 declared runtime assets. | `npm ci` completed earlier in the session; its terminal output was not preserved in this packet and installation was not repeated. Counts are observations, not permanent release assumptions. No remote CI or deployment was performed. |

The graphics renderer reported `ANGLE (Apple, ANGLE Metal Renderer: Apple M4 Max, Unspecified Version)`, with software rendering false. The browser viewport was 1280 × 720. The captured performance fields are short rolling statistics only; they do not satisfy sustained desktop or physical-mobile performance evaluation.

Detailed records:

- [Receipt index and superseded-trial dispositions](../assets/audit/regression-v4/evidence-index.json).
- [Final unit/build/publication-boundary/theme validation with captured command outputs](../assets/audit/regression-v4/validation-final/validation-receipt.json).
- [Reviewed connector/interruption receipt](../assets/audit/regression-v4/reviewed/interruption-validation.json).
- [Shared exterior restoration receipt](../assets/audit/regression-v4/inspection-pose-final-v3/inspection-pose-validation.json).
- [Reviewed baseline acting trace](../assets/audit/regression-v4/baseline-acting-envelope-reviewed.json).
- [Initial model/image browser receipt](../assets/audit/regression-v4/recovery-browser-receipt.json).
- [Graphics and media browser observations](../assets/audit/regression-v4/browser-fault-observations.json).
- [Browser source intervals and artifact hashes](../assets/audit/regression-v4/browser-evidence-binding.json).
- [Actual separated exterior](../assets/audit/regression-v4/browser-inspection-helper-separated.png) and [reassembled exterior](../assets/audit/regression-v4/browser-inspection-helper-reassembled.png).

`scripts/verify-recovery-v4.mjs` is a reusable browser harness that has been reviewed and syntax-checked, but was **not executed** in this work. The browser evidence above came from direct Codex browser controls and the supported developer capability. All temporary WebGL overrides and network blocks were removed, and playback was stopped.

## Visual correction review

The reviewed model, SHA-256 `038aa7eeb56304cb8ead1b28aee23467cfa1a3bdc760b4847966d46ae985fb19`, has smooth claw surfaces and continuous breast edges in the inspected views. It still requires head and regional plate revision. This packet makes no evidence claim for earlier geometry iterations.

The [hash-bound review](../assets/audit/regression-v4/geometry-review-038aa7eeb563.json) compares actual binaries with the July head-only reference and candidate 03 common-body reference. Exact inspected render copies are preserved here:

- [Head](../assets/audit/regression-v4/reviewed-models/038aa7eeb563/alignment-head.png): daylight above the eye, exposed crossbars, detached socket treatment, and horizontal cheek ribbons still disrupt the constructed face. Passing jaw-clearance samples does not settle these shape defects.
- [Whole body](../assets/audit/regression-v4/reviewed-models/038aa7eeb563/alignment-three-quarter.png): body continuity has improved, while coarse plate hierarchy and neck coverage remain under review.
- [Feet](../assets/audit/regression-v4/reviewed-models/038aa7eeb563/alignment-feet.png): faceting is improved; bulbous talon bases and abrupt socket transitions need further hard-surface refinement.

These are agent judgments from static neutral authoring views. They do not constitute per-era scoring, continuous collision inspection, or owner acceptance. The reviewed image hashes are frozen; later images in the production worktree may differ.

Two later hash-bound reviews preserve the subsequent progress and unresolved defects:

- [Independent review of `f937647d5bb0`](../assets/audit/regression-v4/geometry-review-f937647d5bb0.json): the optic is better seated; bill/jaw mass, torso taper and mantle integration still require correction. This reviewer identifies the mantle issue as shape and integration rather than insufficient total coverage.
- [Supervisor review of `bcfb03ef96c6`](../assets/audit/regression-v4/geometry-review-bcfb03ef96c6.json): the fitted orbital plate remains an improvement. The long smooth hook, thin lateral mandible, forward neck/collar intrusion and broad gaps between regional armor courses remain visible. Exact [head](../assets/audit/regression-v4/reviewed-models/bcfb03ef96c6/alignment-head.png) and [three-quarter](../assets/audit/regression-v4/reviewed-models/bcfb03ef96c6/alignment-three-quarter.png) images are preserved.
- [Front, side and rear follow-up for the same model](../assets/audit/regression-v4/geometry-envelope-review-bcfb03ef96c6.json): the side view clarifies the separated cheek/throat layers and straight mantle band; the rear still has unresolved broad panel fields. The record includes bounded source-level hypotheses and their attribution limits.

The acting analyzer distinguishes planned family labels, executed cage actions, rendered claw phases and renderer-reported claw contact. Its fixtures cover canceled approaches and legacy v3 telemetry.

## Independent v4 motion diagnostic

A later [source freeze and condensed result](../assets/audit/regression-v4/current-v4-diagnostic-7833be03d361-summary.json) records an independent run against model `bcfb03ef96c6b64f3bf18caca7851d7b3bd5808d196c55e334ecda1e1ca04299` and production working-tree snapshot `7833be03d361216ad3665eef0b7759341f29f2de860bc1e4eea1c39977843d75`. All 35 selected production source/helper/package/model file hashes matched before, during and after copying. The snapshot includes uncommitted production source at HEAD `698c049`; it is not a released build. No source adaptation was needed.

| Seed | Executed actions over 120 simulated seconds | Renderer contact intervals |
| --- | --- | --- |
| 927 | Rail press 2; claw scrape 1; edge probe 2; seam rattle 1. | Cage 7; claw proximity 1. |
| 20260928 | Claw scrape 2; seam rattle 2; edge probe 1; rail press 1. | Cage 8; claw proximity 2. |

Both accelerated actual-rig runs completed without analyzer warnings. All three claw episodes observed lift, contact, scrape, release and recovery. This supports a bounded improvement over the v3 action sequence. It does not establish visible acting quality, physical contact, force, collision clearance or two uninterrupted browser recordings. The raw trace's `baseCommit` names QA ancestry because the temporary snapshot resides inside that checkout; the companion source-freeze manifest supplies the actual production HEAD and source identities.

## Open findings and next integration gate

F01–F06 remain open for visual integration and review. F07's new claw action and F08's revised acting are being implemented in the production worktree and require fresh evidence against the final exported geometry. The baseline traces exposed the same family sequence under both seeds: edge probe, rail press, seam rattle, edge probe, rail press. Distinct labels and passing state tests cannot close F08. Existing F09 label and F10 publication-boundary checks remain useful bounded evidence; neither supplies missing artistic acceptance.

The next independent integration review must exercise motion interruption, actual shell restoration, neutral and exhibit-light views, and two uncut no-input browser recordings against the final corrected geometry/runtime identity. The v4 diagnostic above adds bounded claw/action telemetry; it does not replace those reviews. Regional appearance proposals must be reconciled onto that one geometry rather than shipped as a competing bird.

V10 repair chronology and V12 historical movement scope remain the documented concrete owner decisions. Physical touch-device work, human screen-reader review, continuous acting review, audible listening, sustained performance, and any future publication verification remain separate tasks. No full score or passing gate is claimed here.

## Superseded evidence

The initial `assets/audit/regression-v4/interruption-validation.json` overstated exterior inspection coverage: its fixture exercised mechanisms but did not move the exported shell. It is preserved as a rejected draft and must not be cited as full shell-restoration evidence. The intermediate `regression-v4-run2` and `regression-v4-final` receipts narrow that scope but still refer to the legacy `exhibit.js` rather than active `presence-exhibit.js`. The reviewed receipt linked above corrects that reference and records non-finite API diagnostics explicitly. Historical receipts are retained without alteration.

The captured Vite stderr has one original trailing space; it is retained byte-for-byte to preserve its recorded hash. Whitespace checking passes for the rest of the committed QA change when this captured log is excluded.
