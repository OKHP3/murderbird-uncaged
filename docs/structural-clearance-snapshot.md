# Structural clearance snapshot diagnostic

This offline tool uses the repaired triangle helper on an explicitly selected GLB, without importing application modules or promoting retained model/runtime integration. Existing models, historical receipts and private recovery archives are inputs to preserve, not files to rewrite. Code is MIT; creative assets retain their existing all-rights-reserved status.

## Run

From the repository root, create a **new private diagnostic directory** and supply every argument explicitly:

```sh
mkdir -p .local/diagnostics/snapshot-review-01
node scripts/verify-structural-clearance-snapshot.mjs \
  --model assets/models/whole-character-v37/attempt-release02/murderbird-whole-character-v37.glb \
  --sha256 4b7c3d248d69a038795b0a5c7b7742b8a5b77d0a9050b7e5afa32b544b0d4e25 \
  --era exported-label-only --pose exported-rest \
  --minimum-separation-m 0.002 \
  --output .local/diagnostics/snapshot-review-01/receipt.json
```

The example's 0.002 metres is a diagnostic proposal, **not an accepted engineering threshold**. Choose and record the threshold deliberately. The full input hash must match before GLB parsing. Texture bindings are removed only from an in-memory copy by the existing rigid-validation loader; source bytes remain unchanged. Run from the checkout being reviewed: receipts record checkout SHA, local origin/main tracking SHA (not live remote proof), tracked/untracked Git dirty state, absolute input path, input byte count/hash and creation time. During precommit development, `dirty: true` explicitly means the checkout SHA alone does not identify the uncommitted tool implementation. Retain the eventual PR revision alongside such development evidence.

Output requires an existing directory below Git-ignored `.local/`, outside `.local/archives/`. Ancestor symlinks, publication paths, missing directories, existing receipts and final symlinks are refused. Nothing is overwritten. The parent directory must remain under the operator's control during execution; this is not an adversarial concurrent-filesystem security boundary. Output can include private local paths and stays local. It is never a deployment payload.

## Coverage contract

Schema `murderbird-structural-clearance-snapshot/v1` always reports overall `PARTIAL`. Successful execution (exit 0) means a diagnostic was written; it is **not a clearance PASS**. Bad arguments, hash mismatch, input/parse or output errors exit nonzero.

| Area | Evidence and limit |
| --- | --- |
| Geometry | Ordinary static mesh triangles at exported resting transforms and exported visibility; units assumed metres. No runtime setup, animation, era selection or transform adjustment. Era/pose are labels only. |
| Static pairs | Nine: left/right toes, plus each toe set against both feet and both shins. Foot surfaces exclude descendant toes; shin surfaces exclude descendant feet. No centroid seam exclusion. |
| Contacts | All pairs returned by `measureSurfaceContacts`, with triangle/mesh identifiers and distances, retained in caller order. Duplicate geometry remains separate triangle pairs, not physical contact manifolds. Threshold and numeric tolerance semantics follow the [helper contract](triangle-clearance-contract.md). |
| Nearest summary | One nearest-distance result per measured pair; not a substitute for the full contact list. Its pair order is helper-defined. |
| Missing coverage | Missing/ambiguous groups, hidden ancestors, empty surfaces and unsupported skinned, instanced or morph geometry are `NOT RUN`. A dependent pair remains unknown, never clear. |
| Joint interpretation | Every measured pair is `UNCLASSIFIED`, including no observed contacts. Same-side join contacts may be intentional; no seam exemption or physical pass/fail decision is inferred. |
| Leg drives | Both toe/leg-drive checks `NOT RUN`: current main lacks the retained `getToeDriveSurface()` selection API. `getPart('drive')` is not substituted. |
| Time | `NOT RUN`: no sampled motion, no continuous sweeps, no impact times or interval certification. Full-model sweep cost remains unvalidated. No temporal uncertainties were evaluated. |
| Acceptance | Engineering not established; model/runtime integration held; whole-model likeness acceptance pending. No source likeness, load strength, device/WebGL appearance or production behavior claim. |

Only static triangle/BVH queries run. Contact inventories are not truncated; dense overlapping inputs may consume substantial time/memory. Start with the pinned reviewed models or small synthetic fixtures. This tool does not validate arbitrary malformed geometry, custom deformation or future model naming conventions. No hidden surfaces are enabled to improve coverage. There is no evidence of cross-host, Replit or Claude synchronization from running it.

## Regression evidence

`node --test tests/structural-clearance-snapshot.test.mjs` uses synthetic geometry: nine-pair selection, descendant exclusion, simultaneous contacts, unchanged transforms/visibility, missing/ambiguous/unsupported surfaces, labels/threshold validation, private-output boundaries, overwrite refusal and pre-parse hash rejection. These tests do not load creative model assets or establish motion integration. The independent helper suite covers its geometry and temporal algorithms; that does not add temporal coverage to this adapter.
