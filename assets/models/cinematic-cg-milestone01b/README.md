# Cinematic CG Milestone 1b study

Unapproved visual likeness attempt, created under the owner's 30,000-token / three-hour / three-worker ceiling. No engineering acceptance or runtime promotion.

Preserved input: `../whole-character-v38/hanging-breast01/attempt02/murderbird-v38-hanging-breast01-attempt02-rigid.glb`, SHA-256 `051477ffcf62a4e08a3f1968d6cec7fd7f8b0677661cd72dde6ad7bbd5514650`.

`murderbird-cg-1b-builder.blend` is the editable integrated study; hidden original alternatives remain for preservation. `murderbird-cg-1b-builder.glb` exports only visible candidate geometry with embedded base color, metallic/roughness and normal maps. `textures/` holds deterministic locally authored 2048px regional PBR maps; these are artistic proposals, not textures extracted from reference pixels. Maker and Mechanic map variants exist, but only Advanced has been integrated/rendered in this checkpoint. Other-era likeness and animation remain unverified.

Reproduce with Blender:

```sh
blender -b -t 8 --python scripts/build-cinematic-cg-milestone01b.py -- --final --attempt avian-stance01 --resolution 768
```

[Fixed-camera comparisons and interactive local preview](../../audit/cinematic-cg-milestone01b/review.html). Run a loopback HTTP server at repository root for the interactive preview; its Three.js imports use the existing installed dependencies. Opening as a local file may block the viewer. Comparison PNGs remain available independently.

Known failures: overly regular armor, rounded shield contour, angular head, muted worn-metal edges and crude joins. Final likeness requires owner artistic review. Original engineering archive and deployed V37 remain unchanged by this study.

Owner-reviewed proportion direction incorporated: torso cross-section -10%, vertical length +12%; neck length -15%, thickness +20%; head follows neck. Review remains pending. Earlier study assets are preserved in Git commit `ba72bc9012c5cccd61d420591203eb08200a2341`.

Latest avian correction: upper hip/thigh connection raised into the lower third of the torso; feet retained; lower rear torso extended into a compact counterweight mass. This is an appearance adjustment, not validated biomechanics.
