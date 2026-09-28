# Alignment v4 native geometry and runtime derivative

This directory contains the current neutral geometry and articulation proposal. The authored dimensions interpret the scoped source illustrations; they are not measured dimensions, final likeness approval or a public release.

`murderbird-alignment-v4.blend` preserves independently editable rigid mesh pieces and named profile/cross-section curves. `murderbird-alignment-v4.glb` batches pieces by their actual rigid owner, era and region for the existing browser runtime. Both identities, ownership, pivots and exact generated-file hashes are in [alignment-inventory.json](alignment-inventory.json). Curves document construction inputs; moving a curve does not automatically regenerate a mesh. Runtime-generated mechanisms remain runtime components.

The composer opens the exact preserved v3 native source, then executes the head, body and neck regional modules. It retains unit joint scales and existing rest transforms; the bill-contact marker is recalculated from the actual upper bill surface. Twelve digit hinges remain individually owned. No skins or image textures are exported.

## Editing and regeneration

1. Save manual work as a new native file before regenerating. The composer refuses to replace a recorded output whose hash changed. Never update the receipt simply to bypass that refusal.
2. Edit the appropriate profile module under `scripts/alignment-v4-*.py`, or use a separately preserved manually edited native version as the next explicitly selected source.
3. Run Blender with `--background --python scripts/build-uncaged-alignment-v4.py`, followed by `--background --python scripts/render-alignment-v4.py`.
4. Run asset, joint, jaw-sweep, claw and browser checks against the new identity. Previous receipts do not transfer to a new model.

Each generated iteration preserves its native model, export, inventory, views and recorded generator snapshots under matching `iterations/<model-sha-prefix>/` directories. Current `generation-source/` files are the exact regional/composer source used to produce the current native model. Earlier helper scripts and source illustrations remain preserved and hash-referenced. The first v4 generation did not record generator snapshots retroactively; its native meshes, control curves and evidence remain available.

See [the current review](../../../docs/alignment-v4-review.md) and [local comparison gallery](../../audit/alignment-v4/alignment-review.html) for observed improvements, limitations and validation. No source archive, native file or audit gallery is selected as a runtime build asset.
