# Three era-specific exteriors — v1

Local proposal derived from structural checkpoint `21ac417`. Artistic acceptance is pending. Creative files remain all rights reserved; see `NOTICE.md`.

- `murderbird-exterior-v1.blend`: editable rigid components with per-era surface variants. The Advanced variant is shown by default. Select objects by their `exteriorEras` custom property to show Maker or Mechanic; hidden variants are preserved.
- `murderbird-exterior-v1.glb`: combined browser derivative. Runtime uses era tags to show one construction state at a time.
- `murderbird-exterior-{maker,mechanic,builder}-v1.glb`: individual review exports. Builder is the internal identifier for Advanced.
- `textures/`: seven portable 1024-pixel PBR maps; no external shader system is needed.
- `previews/`: fixed renders used by the illustrated fallback. These show the actual local exterior study, not approved character art.
- `exterior-inventory.json`: source hash, rigid attachment, regional assignment, era eligibility and generated-file hashes.

The source retains distinct crown and breast covers, shoulder and elbow assemblies, and rigid leg/toe groups. Continuous animation and the era-specific external controls, spring/cam transmission and Advanced drives remain in `src/scene/era-motion.js` and `era-mechanisms.js`; they are not baked into these review exports. The single exported head clip tests transform export only.

Generate with `scripts/build-uncaged-exterior-v1.py` in Blender. It verifies the preserved structural source and refuses regeneration if recorded output hashes have changed. Preserve hand-edited work under a new version before regeneration. Render proofs with `scripts/render-exterior-authoring.py`; see `docs/exterior-surface-pipeline.md` for the UV and material contract.

The preserved `iterations/iteration-a/` snapshot contains the earlier editable scene, runtime model, scripts and comparison renders. It is working history, outside the emitted runtime. The current package adds conforming layered mantles, fitted leg guards, and a deeper bill; see the dated review and exact GLB hash before treating any image as current.

Metadata limitation: joined `surfaceRole` values summarize mixed-role meshes, and the generic `inherited` boolean is not a reliable chronology field for Advanced-only additions. Use the detailed inventory, material primitives and `docs/exterior-regional-map.md` inheritance table. Runtime era eligibility uses explicit era gates.
