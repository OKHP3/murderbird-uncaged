# Mechanical finish study01 — local review candidate

This is a material-response fork of released V37, with editable Blender source and a rigid GLB. It does not change the inherited shape, joints or era visibility. Its role-based metallic/roughness factors replace the pale neutral appearance. It is not the complete regional exterior, texture/wear stage, or owner likeness approval.

Maker uses a newly made dark bronze/iron interpretation; Mechanic and Advanced retain a darker oxidized shell with existing repair contrast. Existing Advanced-only optic material has restrained emission. No powered component is made eligible by changing its finish.

The controlling appearance sources are `assets/img/library/murderbird-unified-maker-clean-candidate-2026-09-06.png`, `murderbird-unified-mechanic-candidate-2026-09-06.png` and `murderbird-unified-master-candidate-03-2026-09-06.png`. The material factors are a proposed interpretation of those references, not measured photographic albedo or new approval.

Each new GLB material stores standard linear PBR factors in `extras.eraFinishes.{maker,mechanic,builder}`. Only eligible profiles are present. The default native shader and GLB response is Advanced; the native material stores the same JSON in its `eraFinishes` custom property. To author another era, select its stored profile and apply base color, metallic, roughness and optional emission to the Principled shader while preserving geometry and gates. The runtime helper reads those explicit profiles; it does not recolor untagged V37 or change visibility.

Run the build script through Blender with its documented `--native-source`, `--glb-source` and `--output-directory` arguments. Outputs are write-once: preserve this version and select a new directory for regeneration. The binary input must be actual media, not an LFS pointer.

The [receipt](../../../audit/whole-character-v37/finish-study01/receipt.json) records preservation and role/region/era assignments. The [local review page](../../../audit/whole-character-v38/checkpoint01/review.html) supports before/after WebGL views and explicitly labels the unchanged V37 fallback. The development-only candidate is excluded from the production build; V37 remains the shipped model.
