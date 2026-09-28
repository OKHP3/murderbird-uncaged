# Alignment v3 editable candidate

This local correction preserves the reviewed v2 source and runtime unchanged. It retains the provisional body/neck/mantle proportions while refining the cheek, mandible, bill root, crown, regional plate boundaries, limb channels and digit covers. It is not an accepted exterior or a public release.

- `murderbird-alignment-v3.blend` contains 539 separately editable mesh pieces and 115 hidden profile/cross-section curves in **Editable region profile controls**. Reveal that collection and its objects to inspect the authored construction curves. They document the mesh-generation inputs; editing a saved curve does not automatically rebuild its adjacent mesh.
- `murderbird-alignment-v3.glb` is the neutral rigid browser derivative, batched only by rigid owner, era eligibility, region and material role. Native curves, cameras and authoring lights are excluded.
- `alignment-inventory.json` records exact hashes, editable pieces, profiles, local/world joint positions and scoped source references.
- Three `*-preview.png` files are fixed authoring views used by the illustrated fallback. They omit runtime-generated mechanisms.
- `iterations/rigid-envelope/` preserves the earlier v3 native/runtime candidate before further lamina and breast-shape refinement. The original v2 remains in its established directory.

## Rigid articulation contract

Blender uses metres, +X anatomical left, -Y forward and +Z up. Three.js uses `(X,Z,-Y)`. These are authored dimensions, not recovered measurements from the illustrations.

All inherited rest joint centres remain at their v2 world positions. The inherited nonuniform head scale `(1,1,1.2)` is baked into descendant rest offsets and vertices, and all exported scales are unity. This changes some local coordinates without moving the rest geometry. It prevents jaw shear under rotation. Use this inventory's coordinates rather than copying v2 local offsets.

The jaw and knee hinges rotate about local X. Positive jaw X opens downward; Maker range is 0 to 0.32 radians. The runtime derives approach distance from the actual upper-bill surface, keeps cervical pivots fixed, and solves contact against the chosen rail. Digit flexion is limited to lifted steps and restores the exact planted rest pose. It is not a purposeful supported gripping action.

The three eras retain their existing eligibility. The original left restriction and proposed later load strap remain distinct. V10 chronology and V12 historical motion scope are not newly approved by this geometry pass.

## Editing and generation

The generator reads the exact preserved v2 Blender source, normalizes inherited rest transforms, and authors region-specific boundaries and cross-sections. It refuses to overwrite recorded outputs whose bytes have changed. Save manual edits as a new native version before regeneration; never replace an edited scene with procedural output merely to satisfy a hash.

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/build-uncaged-alignment-v3.py
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/render-alignment-v3.py
python3 scripts/verify-alignment-v3-assets.py
```

Run these from the repository root. Full render generation refreshes the three explicit previews and their inventory hashes. The validator is read-only unless a v3 report path is supplied explicitly. [Review and evidence](../../../docs/alignment-v3-review.md) distinguish local technical checks from likeness, physical simulation and publication. Creative content remains all rights reserved under `NOTICE.md`.
