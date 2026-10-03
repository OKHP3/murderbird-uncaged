# Source and revised shape overlays

Owner requested starting superimposition of the high-resolution source images
against the revised model. This checkpoint compares **rounded shape study05**
with the locked full-bird canon and the July head-only reference. It does not
modify the detailed CG model or move into another milestone.

## Review

Open [review.html](review.html) through a local repository HTTP server.
The controls show source only, shapes only, an adjustable blend, and either
layer order. Close-ups reuse the full-bird registration; no body part is
independently resized to conceal a mismatch. July uses an independent head-only
registration; its body, large wings and stance do not control this comparison.

Static preview images are browser captures of the layered original source and
transparent model render. They are comparisons, not new character artwork.
The source binaries are not edited, resampled or replaced in the repository.

## Inputs and scope

- Full-bird canon: `assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg`, SHA-256 `645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114`.
- July head only: `context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png`, SHA-256 `47658dba6496f2c8594a40ad412a8bfaa087939e90044d1597329a27ca68d4e9`.
- Revised shape input: `assets/audit/basic-shape-study05/murderbird-basic-shapes.blend`, SHA-256 `8160533136d60061ae8486f0e309803e2da4b3d50d20982816b03f2f9ee376f7`.
- [registration.json](registration.json) records source dimensions, camera,
  model projection bounds, scope, input hash and preserved geometry signature.
- [murderbird-reference-overlay.blend](murderbird-reference-overlay.blend)
  preserves the geometry and adds estimated camera views with source image
  backgrounds. Source image paths are relative to the checkout.

## Registration and limitations

The original source cameras are unknown. The estimated view is approximately
side/three-quarter with a small downward angle. Uniform size is registered by
crown-to-sole height for the whole bird and crown-to-bill-tip for the July head.
Horizontal placement centres each entire silhouette. This is a reproducible
starting alignment, not a calibrated camera match. Pose differences, armour
thickness and visible talons affect the interpretation.

The comparison exposes remaining differences in the neck-to-breast transition,
the folded wing's lower extent, the rear torso contour, leg spread and foot
size. The July panel separates head and bill contours from body proportion.
Owner adjustment notes are the next step; no artistic acceptance is claimed.
There is no texture baking, UV transfer or invented rear/top imagery.

## Reproduction

Run from the repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --threads 4 --python scripts/render-basic-shape-reference-overlays.py
```

The review uses native HTML/SVG image layers. Save the full-page browser views
of `preview.html` and `head-preview.html` for the static comparison previews.

## Validation and handoff

- PASS: Blender renders both alpha layers and saves the editable scene.
- PASS: script asserts unchanged geometry and input model hash.
- PASS: both pinned source hashes checked before rendering.
- PASS: parser, whitespace and referenced-file checks.
- PASS: browser inspection of full bird and head comparisons; source-only,
  shapes-only and layer-order controls checked.
- WARN: estimated camera and different poses; owner likeness acceptance pending.
- NOT RUN: app build, runtime WebGL/fallback checks, CI and deployment; the
  checkpoint adds audit assets only and changes no application/runtime files.

Integrator: Codex. Working track: `codex/cinematic-vfx-milestone01b`.
Other systems must fetch the checkpoint revision before continuing; a branch
push alone does not prove they have received it. Next: owner contour notes,
then a separately reviewed shape revision before changing the detailed model.
