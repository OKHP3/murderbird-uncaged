# Correction v2 — integration contract

Stage A / B work starts from `4b1c726f5d9bbd1ba1048f89049a5b422001c506` on `codex/neutral-correction-v2`. The production checkout was clean at `0263692`; the later evaluation documents at `4b1c726` were retained before edits. The primary clone's untracked `docs/handoffs/` and ignored inspector packet remain untouched. No new release is authorized.

## Shared model contract

- Metres are an authoring convention, not measurements from art. Blender X is anatomical left, Z up, −Y forward. Three.js maps `(X,Z,−Y)`. Approximately two metres at crown is the existing production convention.
- Supervisor is the sole full-body geometry integrator. Only the supervisor writes `scripts/build-uncaged-neutral-v2.py`, the new `assets/models/uncaged-neutral-v2/` source/exports and `src/scene/presence-exhibit.js` model integration. Historical models/generators/receipts are preserved.
- Named assembly pivots remain `body`, `neck`, `head`, `jaw`, `upper-bill`, `cranial-cover`, `breastplate`, bilateral shoulder/mantle/elbow/wing/hip/knee/ankle/toe chains. Existing transforms and movement limits are the initial runtime compatibility contract, not likeness authority. Any changed pivot/contact is recorded in the generated inventory and coordinated before runtime adoption.
- Body regions: head, optic, neck, breast, shoulder, wing, pelvis, leg, foot, back. Each rigid piece has exactly one parent assembly. Metal does not deform across joints. Overlapping pieces stay assigned to their moving side; flexible routes remain distinct.
- Maker: passive inherited structure and external support/controls only. Mechanic adds transmission/repair. Advanced adds power, actuation, sensing and separate processing. Neutral material does not erase era eligibility. Anatomical-left restriction persists; proposed repair chronology awaits a concrete owner decision.
- Contact interfaces retain actual bill-contact landmark and foot/toe descendants. New digit chains must be separate named transforms; no behavior worker may assume new coordinates until the geometry inventory is supplied.
- Runtime camera, inspection, era selection, reduced motion, fallback, song and story remain in place. No dependency changes, publication, private uploads or edits to frozen evaluation files.

## Bounded worker ownership

1. Reference worker: `docs/correction-v2-reference-packet.md`, `assets/models/uncaged-neutral-v2/reference-packet.json`, optional new review diagrams under `assets/audit/neutral-v2/decisions/`. Read-only source/reference inspection; never source edits or model generation.
2. Tooling worker: F09/F10 only; label layout helper, relevant CSS and validator scope. Must coordinate any `presence-exhibit.js` edit with supervisor and provide a patch rather than edit that owned file. No model, release receipt, source artwork, package/dependency or frozen assessment edits.
3. Supervisor: F01–F04 neutral geometry first, integration/captures/evidence and owner review. F05/F06 material work remains gated on neutral review. Motion work F07/F08 begins against the agreed pivot inventory after the immediate neutral deliverable.

Workers report exact changed paths, checks, evidence, known defects and risks. A worker return is not acceptance. The neutral model, hidden engineering and all artistic decisions remain proposals until reviewed.

## Frozen Stage B rest-pose changes

The new head rest pivot moves 0.072 m lower and 0.035 m forward in Blender neck-local coordinates. Neck-owned guards/frame use the corresponding shortened rest envelope; head-owned rigid pieces move together. Body and hips move down 0.08 m; knee and ankle local links each gain 0.04 m in Z, leaving the foot world pivot unchanged. These are authored proportions, not measured anatomy. The actual exported transforms and contact point are in `neutral-inventory.json`. Runtime constraints continue using the supplied pivots and surface contact; no neck translation is added during contact.

The final Stage B GLB is `48229ba5526ccd7a227db56d225ef88643eb6b3388eb07662452cc2c67636ac7`, 6,038,136 bytes. The earlier D model and independent observations remain under `iterations/iteration-d/`. F08's seeded intention/route plan is integrated but its action families still share the current cage-press choreography; metadata variety is not gesture completion. No final surface worker was released past the owner's Stage B gate.
