# Corrected envelope03 neck-pose review

The pinned native is V21 envelope03, SHA-256 `720c343645ef2de298a50e53c82fad66448c187b1eaf9311de2514cac079f280`. The earlier `native-dip.png` is not reliable evidence: Blender frame evaluation restored inherited head animation after the pose was assigned.

This review clears object, data-block, and scene animation in memory before frame evaluation and before each temporary pose override. It never saves the native. After each render, the measured world X rotations matched the requested hierarchy to at most `0.0000021°`:

| Pose | Neck local X | Upper cervical local X | Head local X | Head world X after render |
|---|---:|---:|---:|---:|
| Rest | 0 | 0 | 0 | 0° |
| Corrected dip | +0.2275 rad | +0.4225 rad | −0.65 rad | 0° |
| Corrected extension | −0.2275 rad | −0.4225 rad | +0.65 rad | 0° |

The evaluated BVH screen compared all 18 newly authored `neck` and `cervical-upper` meshes at these three discrete poses. It found 6 cross-owner pairs at rest and 11 at each endpoint. The principal unresolved plate crossings are the lower/upper swept throat keels at +0.65 rad (458 overlapping triangle pairs) and lower/upper swept nape returns at −0.65 rad (489 pairs). These are rigid inter-owner surface intersections; this review grants no intentional-lap or contact exemption. The same-side ascending root yokes also intersect the upper cervical directional guards at both endpoints (122–134 triangle pairs per side). At all three poses, each intermediate passive journal intersects its cervical upper load bow (about 100 pairs per side); root load bows also intersect the intermediate captive shaft (56–58 pairs per side). These are named support/shaft contacts that still need local construction review.

This is a discrete triangle-intersection screen, not a penetration-depth, continuous-clearance, structural, or acceptance test. It compares only the 18 new neck-owned meshes, not surrounding body, breast, or head geometry.

Renders: [rest](rest.png), [corrected dip](corrected-dip-plus-065.png), [corrected extension](corrected-extension-minus-065.png). Full structured evidence is in [review.json](review.json); its first-pass label snapshot is preserved as [review-initial-labels.json](review-initial-labels.json).
