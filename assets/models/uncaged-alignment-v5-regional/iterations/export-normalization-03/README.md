# Export-normalization study 03

This folder preserves a diagnostic-only rebuild of the guard-and-talon regional composition. Candidate-02 remains the selected model for the current render and runtime evidence because that evidence is bound to its exact GLB. This study has no new render, motion, or runtime acceptance evidence and does not replace candidate-02.

The study preserves the region shapes and source owner pivots from the candidate-02 input snapshots. It changes the export implementation to materialize evaluated meshes through Blender's data API, verify evaluated-to-normalized geometry per object, and remap talon material slots to the exact existing `Neutral / edge` material. The GLB world-geometry comparison produced by the composer is recorded in `manifest.json`; independent runtime/export parity review of this iteration remains pending.

The foot-edge source audit is retained as `foot-edge-source-audit.json`. Its exact V5-sixth native/GLB identity is recorded in the file. It shows that the 804-triangle difference per foot between the old batched edge group and the retained hallux/axle-cap group comes from the six ankle lap ribs, which guard-study05 explicitly replaces. Candidate-02's current independent rejection note and review state remain authoritative until the parent review updates them.

No full input snapshot tree is duplicated here. `source-mapping.json` maps each candidate-03 input record by exact SHA-256 and byte size to the corresponding frozen file under `../candidate/input-snapshots/`; every mapped file was rechecked during preservation.

Preserved artifacts:

- `murderbird-v5-sixth-guard-talon-study.blend` — editable native regional composition.
- `murderbird-v5-sixth-guard-talon-study.glb` — batched export derivative.
- `compose-alignment-regional-study.py` — exact executed composer source snapshot.
- `manifest.json` — source identities, per-object normalization checks, pivot checks, and export checks.
- `foot-edge-source-audit.json` — native source object breakdown for the foot-edge group.
- `source-mapping.json` — candidate-02 frozen-input mapping.
