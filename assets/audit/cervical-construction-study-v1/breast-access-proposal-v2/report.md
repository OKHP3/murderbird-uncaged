# Panel-only staged access screen

**Result: reject this particular slide path for the proposed V4 actuator envelope.** The panel-only trajectory reaches its final pose without a sampled actuator-envelope conflict, but the straight slide at fixed opening angle passes through the proposed actuator's 12 mm housing envelope. The moving support/carriage itself is not modeled. This is a candidate diagnostic, not hardware or runtime acceptance.

The screen uses attempt-07's pinned native and the V4 proposed anchor locations. It sampled 101 points along the complete three-stage route, not 101 points per stage:

1. Rotate the breastplate from `open=0` to `1/3`, angle `0` to `−0.675 rad`, holding panel slide at 0.
2. Hold the angle at `−0.675 rad` while translating only the breastplate along its existing inspection offset, scalar 0 to 0.5.
3. Hold the panel offset at 0.5 while rotating to `−1.35 rad`.

The other native owners remain at their attempt-07 rest transforms throughout. The global assembly-separation behavior is not applied.

## Actuator-to-panel result

Stage A's minimum conservative 12 mm housing margin is **+15.876 mm** at the last sampled point before the first stage boundary. Stage C's minimum is **+184.476 mm**. The problem is Stage B: at panel slide scalar **0.070**, the proposed actuator centerline comes within **0.072 mm** of the `Breast inner access shell`. The sampled 12 mm housing margin is **−11.928 mm** and the conservative segment margin is **−16.271 mm**. Four samples at scalars 0.040, 0.055, 0.070 and 0.085 fall directly within the 12 mm envelope. The conservative bound also identifies possible conflict over scalar interval 0.025–0.100.

The sampled 12 mm bound is nonmonotonic during translation: scalar 0.010 is a locally clear sample; 0.025–0.100 has a negative conservative margin; samples from 0.115 through 0.490 return to nonnegative margin. That isolated safe sample does not make the route traversable: a straight slide from zero to 0.5 crosses the flagged interval. Thus the specified panel-only trajectory is not a viable access path without changing the slide direction or actuator side/route. No panel-carriage support was added or assessed.

The line-to-panel method transforms the complete evaluated breastplate descendant mesh set at each sample. It samples the proposed actuator centerline at 17 equal intervals, then subtracts half the point spacing for a conservative distance-to-surface lower bound; the 12 mm radius is subtracted separately. Direct sampled proximity and conservative uncertainty are reported separately in the JSON.

## Stationary-geometry screen

The transformed breastplate also received a separate triangle-overlap candidate screen against stationary native mesh groups owned by `body`, `neck`, `cervical-upper`, `head`, `jaw`, `upper-bill`, `cranial-cover`, `builder-optics`, `processing`, both mantles and both wing shields. The screen reports candidate triangle pairs, not interpreted collisions: closed/rest samples and early rotation produce candidates against body, neck, both mantles and both wing shields; the sliding middle stage still has candidates against body, neck, the right mantle and right wing shield; no triangle-overlap candidates were returned in stage C. The detailed per-sample owner counts are in `panel-trajectory-clearance.json`. Existing plate laps, intentional contacts and coplanar boundaries are not adjudicated by this broadphase screen.

## Coordinate and evidence boundary

The attempt-07 GLB packet's converted **world** breastplate matrix differs from the native scene by a common root translation, so the first world-space preflight was stopped. The corrected run verified the packet/native **parent-local** breastplate matrix and applied its converted local delta around the actual native body parent. Both actuator endpoints were reconciled to their V4 native-owner anchors. This uses one consistent native world frame for the moving panel, actuator, and stationary target meshes; no guessed global offset was subtracted.

Inputs, source hashes, 101-pose output, panel mesh list, owner groups, thresholds, and limitations are bound in [receipt.json](receipt.json). No application or model was edited; no render, support design, or continuous swept-volume validation was performed.
