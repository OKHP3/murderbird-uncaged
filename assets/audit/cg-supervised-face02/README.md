# Face and throat checkpoint — two attempts, stop for integration review

Input: `assets/models/cg-supervised01/attempt01/murderbird-supervised-builder.blend` at `8efb5ba11eaa208d802ee876516648b1b08b79d1`, already containing supervised head/neck and compact shoulder modules. Shared goal read at `251f2f0243181e97140179c2aff6eb057e165438`; current architect authorization read from `codex/cg-superintendent-20261004:goal.md`.

## Integration

Load the untouched attempt01 native, then call `scripts/cg-supervised-face02.py` → `apply(scene, root_path=None, era='builder')`. Supported eras: maker, mechanic, builder. Apply once after head-neck01 and shoulder01. No earlier geometry is deleted or modified. New geometry is tagged `cgSupervisedFace02`; superseded meshes are hidden and tagged `cgFace02Superseded`. Receiving materials are reused; optical materials are copied to enforce era emission canon.

The 144 editable added meshes form a sinuous diagonal eye-to-billroot bridge, cheek hinge and curved aperture, shorter descending mandible, tapered crown clusters, and linked throat-to-upper-breast plates. No shoulder, wing, leg, or foot mesh was edited. The new throat plates and side rails are tagged region `neck`, including their upper-breast extension. This intentionally coupled region may need integrator material routing.

## Visible assessment — inferred, owner acceptance unknown

The cheek now has a recognizable curved structural bridge, and the lower jaw bends downward instead of forming the original horizontal spear. Crown volume remains swept and its courses have shorter, finer tips. Whole-bird identity gain is limited: the upper bill remains an oversized smooth shell, the new throat still reads too much like a regular segmented duct, and cheek hardware density and construction do not match the pinned source. The throat is the weakest part of this proposal and needs independent review before retaining it. No third attempt was made.

If the integrator rejects only the throat, hide `CGF02 linked throat breast lamella*` and `CGF02 throat to breast side rail*`, then restore the original `CGH01 curved cervical leaf*` and `CG supervised breast throat course*` objects listed in `receipt.json`. The source-side restoration is reversible and does not require regenerating cheek or crown geometry.

## Evidence and checks

- PASS: original input SHA unchanged; all 6,114 receiving mesh geometry, topology, UVs and world transforms unchanged; all recorded empty anchors unchanged. See `receipt.json`.
- PASS: exact full-bird JPEG and July head reference hashes match shared pins. July body/wing/stance was excluded.
- PASS: module imports and runs in Blender 5.2.1 for all three eras. Maker and Mechanic amber emission strengths are zero; Advanced retains 0.85 core / 0.18 coils. See `era-check.json`.
- PASS: before/after images rendered using the root's frozen camera transforms and neutral-light profile, 800px, 16 Cycles samples. `attempt01-*` preserves the first design attempt; `after-*` is the second/final attempt.
- NOT RUN: native/browser export, browser material parity, WebGL/fallback, app build, remote CI or deployment. These remain integrator scope; no app or runtime references changed.
- UNKNOWN: owner artistic acceptance; unseen-side construction is inferred.

`render-check.py` reproduces evidence from the exact input. Input native and original mesh data remain intact. No native duplicate is saved by the worker; root integration creates the next versioned native.
