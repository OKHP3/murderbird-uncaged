# Neutral correction v2 — Stage B proposal

This is a new editable neutral structure derived from the preserved structural-v1 **pivot contract and Advanced internals**, with newly authored external geometry. It is not a finished era exterior or an artistically approved MurderBird.

- `murderbird-neutral-v2.blend`: independent editable plates, guards, frames, fasteners, digit hinges and inspection groups.
- `murderbird-neutral-v2.glb`: rigid browser derivative, batched only by parent, era eligibility, region and material role. Shared pieces remain shared; later repairs and Advanced systems have explicit eligibility.
- `neutral-inventory.json`: exact source/export/preview hashes, per-piece ownership, authored world/local pivots and reconstruction classification.
- `reference-packet.json`: unchanged scoped source references/hashes.
- `maker-preview.png`, `mechanic-preview.png`, `builder-preview.png`: era-aware fixed neutral authoring views; these do not show runtime-only controls/transmissions/actuators.
- `iterations/`: preserved rejected/intermediate generated sources and renders. These are never regeneration targets.

The supervisor owns `scripts/build-uncaged-neutral-v2.py`. Existing output hashes are checked before regeneration; a manual source change must be preserved in a new version before that generator may replace outputs. Run it with the existing Blender installation. `scripts/render-neutral-v2.py` makes neutral reconstruction and approximate reference-perspective views. No new dependency or online generation service was used.

## Changed mechanical conventions

Blender metres, +X anatomical left, −Y forward, +Z up; Three.js `(X,Z,−Y)`. These are production dimensions, not measurements recovered from illustrations. Body and attached upper structure are lowered 0.08 m from structural-v1. Hip pivots also lower 0.08 m; each leg's knee link changes by +0.04 m in local Z and its ankle link by +0.04 m, leaving the ankle/foot world pivot unchanged while reducing leg exposure. The head rest pivot is lowered 0.072 m and moved 0.035 m forward relative to the neck; neck-owned guard/frame vertices receive the matching shorter, bowed rest envelope. Joints remain fixed at these authored rest offsets during motion, with no contact-driven neck translation. The contact landmark is derived from the actual upper bill surface.

Each foot has three independently hinged digits, named `left/right-digit-1/2/3-proximal/distal`. Their existence is **not** a completed gripping action. Rigid panel owners include `cranial-cover`, `breastplate`, both mantles and both wing-shields. No plate stretches across a joint. The left restriction persists; the small later strap is proposed, pending the owner's chronology decision.

## Scope of neutral materials and inspection

Solid glTF metallic-roughness materials distinguish plate, frame, recess, bearing and inner surfaces. There are no image maps, normal maps or final wear. This makes silhouette and overlap review possible without dramatic surface treatment. The current inherited forms are common across eras; the runtime adds the existing Maker external controls/support, Mechanic drive and Advanced actuation/distribution. Those runtime constructions are not baked into the `.blend`.

Read [the backlog](../../../docs/correction-v2-backlog.md) and [local review](../../audit/neutral-v2/neutral-review.html). Automated checks establish only the contracts they sample. They do not certify likeness, unseen engineering, all moving collisions, physical balance or a final score. Source art, story and the old assessment remain unchanged. Creative content is all rights reserved under `NOTICE.md`; no publication is authorized by this source package.
