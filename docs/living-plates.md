# Living Plates

Added November 14, 2026 by owner direction, after the v1.0 closeout. Record: [provenance/living-plates-2026-11-14.json](../provenance/living-plates-2026-11-14.json).

## What it is

`public/plates/` presents four pinned reference images as look-around plates: the canon bird and the Maker, Mechanic and Advanced era scenes. A visitor drags to shift the viewpoint about five degrees each way and the background slides behind the bird. A depth survey view draws the estimated depth as contour lines. Iron Verdict plays only when the visitor starts it.

A tap on the plate, or the Provoke button, gets an answer in the manner of the era on show. The Maker's bird clacks once, as if a lever were pulled from outside. The Mechanic's bird slips three notches of its spring. The Advanced bird and the canon plate strike toward the visitor and the optic flares. The plate has no rig, so each answer is a camera move toward the head plus a short synthesized sound made in the browser at the moment of the tap. Visitors who ask for reduced motion get the status line, the flare and the sound without the camera move.

At rest each plate is its reference image. Nothing was modeled. One monocular depth estimate per image lifts it into a front layer and a back layer.

## What it is not

- It is not a 3D model. There is no orbit, no walk and no disassembly. The V37 exhibit keeps those.
- The provoke reaction does not move the bird. No jaw opens and no limb swings; the camera moves and the optic glow changes.
- It does not change the closeout status. Whole-bird likeness of the V37 and CG **models** stays **UNMET** and parked. The plates sidestep that question by showing the reference art itself.
- Background revealed behind a moving edge is mirrored from nearby texture. It is plausible, not recovered.
- The canon plate uses candidate 03, the higher-resolution sibling of the locked September 22 composite. The locked composite still controls full-bird canon.

## Files

| Path | Purpose |
|---|---|
| `public/plates/index.html` | The page. Self-contained; no build step. |
| `public/plates/img/*-front.webp` | Reference pixels. Alpha is zero only on the far side of occlusion edges. |
| `public/plates/img/*-back.webp` | Same image with foreground rims replaced by mirrored background. |
| `public/plates/img/*-depth.png` | 16-bit disparity packed in red (high byte) and green (low byte). Left half front, right half back. |
| `public/plates/vendor/three.min.js` | three.js r128, MIT, vendored so the page makes no script request to another host. |
| `scripts/build-living-plates.py` | Offline authoring tool that rebuilds the layers from the pinned images. Not part of the build or CI. |
| `scripts/assemble-plates-overlay.mjs`, `.github/workflows/publish-plates-overlay.yml` | Overlay publication, below. |

The plate images sit under `public/` and outside the Git LFS patterns, so they are ordinary Git blobs of about 2.8 MB in total. They add nothing to LFS storage or bandwidth.

## Publishing while the LFS budget is exhausted

The standard publication (`Validate build` with `publish_pages`) rebuilds the whole site and needs the LFS asset cache, which cannot be filled while the repository is over its LFS budget. Because `public/` is copied into every build, the plates will ship with any future standard publication automatically.

Until then, **Publish Living Plates overlay** adds the plates to the site that is already live:

1. It downloads every file named in the live `release.json`, and stops unless each one matches its recorded size and SHA-256 and the live revision equals `expected_base_revision`.
2. It copies `public/plates/` beside those files and writes `plates/overlay.json`, which names the base revision, the overlay revision and each plate file's hash.
3. It deploys that tree to GitHub Pages.

The exhibit, folio, CG viewer and `release.json` are republished unchanged. The run is manual, on `main` only, and requires `expected_revision` to equal the commit being published, the same gate the standard publication uses. It downloads nothing from Git LFS.

To run it: Actions, **Publish Living Plates overlay**, Run workflow on `main`, paste the current `main` commit SHA as `expected_revision`.

After an overlay publication the live site is the base release plus `plates/`. `release.json` still describes the base build only; `plates/overlay.json` describes the addition. A later standard publication replaces both with one ordinary build.

## Rebuilding the layers

```sh
pip install numpy pillow opencv-python-headless scipy onnxruntime huggingface_hub
python3 scripts/build-living-plates.py
```

The reference images must be hydrated from Git LFS first. Depth inference is not guaranteed bit-identical across machines, so rebuilt layers can differ slightly from the committed ones; update the provenance record if they are replaced.

## Verification status

Checked in headless Chromium with software rendering at phone and desktop sizes: all four plates, era switching, the depth survey, capture mode and the provoke reaction on each plate, with no script errors. Frame rate on real hardware was not measured, and the reaction sounds were not auditioned on real hardware. The Node test suite gives the same result before and after this change on an LFS-pointer checkout: 141 pass and 9 fail, the 9 needing hydrated model payloads. The CI asset plan is unchanged at 499 objects. `npm run build` and the publication verifiers were not run, because the authoring environment held LFS pointers only. No existing build input, verifier or test was modified; tracked files under `public/` are admitted by `scripts/verify-publication.mjs` as they are.
