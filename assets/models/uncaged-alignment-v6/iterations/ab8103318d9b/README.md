# Alignment v6 head and neck study

This is an editable neutral construction proposal. The [inventory](alignment-inventory.json) identifies the current [Blender source](murderbird-alignment-v6.blend), [GLB](murderbird-alignment-v6.glb), exact executed recipe bytes, rigid part owners, era eligibility and source-reference scopes. It is not approved exterior art or a deployed release.

V6 refines the primary optic aperture, orbital mounting field, brow, fixed cheek, lower mandible curve, crown sweep, and localized neck clearance. The reconstructed v5 jaw hinge is unchanged. V5 body, breast and compact articulated mantle remain inherited; legs and digits remain the prior implementation while a separate limb study is reviewed. The July selection controls the head only; candidate 03 controls the supported common body interpretation. Dimensions are authored reconstruction choices, not measurements from perspective art.

The sources preserve individual rigid parts and editable profile curves. Export batching is limited to identical rigid owner, era eligibility, region and surface role; the jaw, bill, cranial cover, inspection panels, shoulder/elbow assemblies and digits remain independently attached. The complete iteration history preserves rejected geometry and its receipts. New results do not supersede an earlier result for a different hash.

## Regeneration and review

- Work through `scripts/build-uncaged-alignment-v6.py`, `scripts/alignment-v6-head.py`, `scripts/alignment-v6-neck.py` and the pinned inherited v5 body recipe.
- Preserve manually edited Blender work as a new named version first. The composer refuses to overwrite generated files whose recorded hashes differ; do not change the receipt to bypass that protection.
- The composer freezes exact input recipe bytes and archives each prior candidate under `iterations/<model-sha-prefix>/`. Only files declared in the inventory are active recipe inputs; an older source snapshot retained alongside them is historical.
- Render with `scripts/render-alignment-v6.py`. Full rendering creates the era previews required by `scripts/verify-alignment-v6-assets.py`; a quick shape pass alone is insufficient.
- Check the jaw against the head and neck, active optic clearance, rigid motion/contact and inspection, then inspect the exported browser result. Discrete proper triangle-crossing checks do not prove continuous clearance, containment, coplanar contact, physical force or artistic likeness.
- The [local v6 review](../../audit/alignment-v6/index.html) states the actual candidate and current result scope. The [v5 review](../../audit/alignment-v5/index.html) is a separate earlier browser checkpoint; its recordings and test results are not v6 evidence.

Neutral material equality is not three-era appearance acceptance. Earlier eras must retain passive structure and appropriate external/transmission hardware while Advanced power, processing and active optics remain separately gated. Finished surface work and owner artistic acceptance remain outstanding. No audit tree or native source is implicitly selected for browser distribution.
