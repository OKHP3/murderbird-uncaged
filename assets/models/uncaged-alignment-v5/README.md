# Alignment v5 native candidate and runtime derivative

This directory holds a local neutral-geometry proposal awaiting owner review. It is not an approved model or release. [The inventory](alignment-inventory.json) records the exact GLB, Blender source, generator snapshots, parts, pivots, classes, era eligibility, and reference scopes.

The [editable Blender file](murderbird-alignment-v5.blend) preserves rigid pieces and profile curves. The [GLB](murderbird-alignment-v5.glb) batches pieces by rigid owner, era, region, and surface role for the existing exhibit. Current SHA-256 identities are:

- GLB: `1e7febcc03d9f8d1a644580c8422b124403cf4e5768aa01df747e3d9b6af9f1e`
- BLEND: `fd5c8a21e8e7808fa94c9baa3499574bac3d0c1ed5a44573637286c359cea0e4`

V5 revises breast, mantle/wing cover, jaw hinge and fork, and upper neck guards. The jaw was separately jaw-owned before and after the hinge reconstruction; an earlier reviewer diagnosis incorrectly attributed the apparent mismatch to ownership. The v4 jaw-head sweep passed, while the first raised-hinge v5 attempt failed clearance against fixed cheek and processing meshes. Other rest pivots, neutral materials, head surfaces beyond the jaw reconstruction, legs, feet, and individual digit owners are inherited. The Advanced processing assembly and optics remain separate rigid owners and Builder-only; passive geometry is eligible in Maker, Mechanic, and Builder. The single later repair part is eligible in Mechanic and Builder. Eligibility is encoded per part in the inventory.

The [matched set of 27 neutral authoring renders](../../audit/alignment-v5/authoring-views.json) binds each image to this model and native-source hash. The [asset-validation receipt](../../audit/alignment-v5/asset-validation-1e7febcc03d9.json) passed its declared checks: 703 native mesh pieces, 462 curves, 231,704 triangles, 90 exported meshes, and 141 nodes. The [six-validator run manifest](../../audit/alignment-v5/rig-1e7febcc03d9/run-manifest.json) records 59 passing assertions, jaw-head sweep at 0/33 crossing poses, and expanded jaw/neck check at 0/27. The [five export-contract fixtures](../../audit/alignment-v5/export-contract-tests.log) and [build-boundary receipt](../../audit/alignment-v5/build-boundary-1e7febcc03d9.json) passed; the latter records 133 emitted files and 16 exact approved runtime media assets. These results are bound to their recorded hashes and do not decide likeness, final surfaces, or owner acceptance. Bounded live-browser and normal-speed recording evidence is preserved in [the browser manifest](../../audit/alignment-v5/browser-1e7febcc03d9/evidence-manifest.json); its limits and missed fixed-schedule actions remain explicit.

July's selected illustration constrains the head only; candidate 03 guides the proposed neck/body direction. Neither perspective reference establishes exact dimensions or hidden geometry.

The neutral Maker and Mechanic preview PNGs are byte-identical in this camera view. Caption and controls change by era, but these previews do not demonstrate a visible repair difference. Their distinct appearance remains an exterior-stage requirement. `generation-source/alignment-v4-neck.py` is a preserved predecessor, excluded from current recipe inputs; the inventory's `generatedFiles` and `inheritedHelperSources` identify the actual sixth-iteration sources.

## Editing and regeneration

1. Preserve any manual native-file changes as a new version before running the composer. It refuses to overwrite an inventory-recorded generated file whose hash changed; preserve the changed work rather than changing the receipt to bypass that guard.
2. Edit the regional source modules under `scripts/alignment-v5-*.py` or explicitly base a new candidate on a separately preserved manual version.
3. Run the v5 composer and renderer only when the intended base and output preservation have been reviewed. The composer freezes the exact bytes of its three regional modules, its recipe, and all inherited helper scripts in `generation-source/` before executing them.
4. Regeneration preserves the previous recorded candidate, inventory, authoring views, source snapshots, and audit files under matching `iterations/<model-sha-prefix>/` directories. Verify the new hashes and rerun relevant checks; prior receipts do not transfer to a new model.

See [the v5 review](../../../docs/alignment-v5-review.md) for the scope, comparison, open art decisions, and evidence limits. No source archive or audit gallery is selected as a runtime build asset.
