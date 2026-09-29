# Next option: one passive floating front-shingle carrier

**Proposal only; no geometry, code or test executed.** Independently rigid guards could retain more of the directional S-shaped rest envelope. Clearance and likeness remain unknown.

V23 parents all ten guards in each course directly to one structural pitch link. Equal quarter-pitch weights force each entire wide core through the neighboring core's swept space. Removing that space created disconnected bands; sphericalizing it created stacked cylindrical/squared bands. Rigidity is compatible with directional plates; requiring every plate to follow its load link without a separate guided motion is the limiting assumption. Half-angle carriers alone would not suffice: adjacent carriers still accumulate the serial link rotations.

The four links, equal weights, exact pivots and immutable rests were **our bounded-study constraints, not owner-approved engineering**. V23 labels this a proposal, changed `neck`/`cervical-upper`, and introduced `cervical-mid-a`/`cervical-mid-b`. The owner requires recognizable mechanical MurderBird construction and reference likeness. Retaining this load chain below minimizes the experiment; it does not approve its pivots.

## One minimal change

Add one rigid `cervical-mid-a-front-guard-slide` carrier, parented to `neck`, resting at the existing mid-a center. Reparent only `V23 cervical 2 directional guard 2`, `3`, and `4` to it. Retain their directional rest forms/world placement except necessary mating-edge seating; leave structural joints, load links, races and head attachment unchanged.

A **captive curved guide and push-pull link driven by the actual mid-a hinge** would turn the carrier approximately half the hinge excursion while lifting/withdrawing it toward native +Z/-Y. This is one constrained passive degree of freedom, valid in all eras; root yaw is inherited from `neck`. The guide law and travel must be derived from actual mating solids. Neither a travel number nor clearance is established. Its finite hardware must fit: an unsupported mathematical offset does not qualify as mechanical construction. The whole upper shingle can retract during bending while retaining its curved directional silhouette at rest, instead of permanently deleting its core.

It targets guard `1/3` versus `2/3` and neighboring front sectors. The short-lap study found crossings 15–31 mm below mid-a, beyond its lip patch. Correction02 found the same pair's witness vertices approximately 28–39 mm above mid-a in the transition core. Changing only the lip cannot solve that core motion. Bounds are triangle-vertex bounds, not penetration depths. This one-joint option leaves the other hinges, rest side corners, root/breast receiver and protected head neighbors unresolved.

## Runtime impact if authorized

In `src/scene/cervical-articulation.js`, add an optional `body.userData.cervicalGuardGuidesV1` descriptor alongside unchanged `cervicalLayoutV2`. `createChain()` validates/resolves the carrier and `neck` parent. Existing `setPitch()` evaluates its authored guide from the captured-rest-relative mid-a angle before world-matrix updates; `updateCovers()` synchronizes/reports changes. Include the carrier in `capturePose()`, `restorePose()` and `restoreAttachments()` for contact probes/reset; `metrics()` reports guide parameter, displacement and rigid basis. Existing `createEraMotion()` callers/final receiver update can remain; no new control or `createEraMechanisms` dependency is needed. Sliding guard ownership must be explicitly allowed while structural-joint translations remain fixed.

Gate the single joint's actual rest/Maker/contact likeness and clearance throughout travel before replication. Reject if its hardware is implausible or it still crosses; a different structural pivot layout remains a separate scope.
