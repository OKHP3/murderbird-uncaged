# Triangle clearance diagnostic contract

This offline diagnostic helper is extracted from retained Replit checkpoint `057a305b` and repaired separately from its model/runtime integration. It uses the existing Three.js dependency. No application module imports it, no production model changes, and no historical receipt is rewritten. Whole-model likeness acceptance remains pending; these checks do not establish engineering safety or artistic acceptance.

## Static queries

`buildTriangleSurface` snapshots visible mesh triangles in world space. `measureSurfaceClearance` retains the nearest-distance API: it returns one closest triangle pair and can stop after finding an intersection. It is not a contact inventory.

`measureSurfaceContacts` instead visits all qualifying pairs through the second surface's AABB hierarchy. Returned triangle IDs belong to the supplied surfaces and maintain caller order. It reports either intersection (squared distance at most `1e-18`) or distance plus `1e-9` metres below the requested clearance. Exact positive-threshold equality is not a violation. Thresholds must be finite and non-negative. Units are metres. Duplicate geometry triangles remain distinct triangle pairs; these are not physical contact manifolds.

## Between-pose queries

`measureSweptSurfaceClearance` checks each triangle pair independently. A persistent contact cannot hide another simultaneous or later contact. Shared, stable mesh hierarchies use local position/scale interpolation and shortest-path quaternion interpolation through ancestor chains. Independently constructed synthetic endpoint meshes use linear world-space vertex interpolation. Changed shared hierarchies and changed source vertices are rejected before clearance certification.

A separation lower bound can certify clear intervals; a pair-specific upper bound can certify contact spans. Endpoint/midpoint contact alone cannot certify the entire interval. Bounds are recomputed from each subinterval's endpoint snapshots rather than blindly halved through changing hierarchy scales.

Results retain `violation` and `uncertain` as first-item compatibility aliases and expose complete collected `violations` and `uncertainties` arrays. Cached surface-wide `startMeasurement`/`endMeasurement` options are intentionally not reused for individual pairs. `minimumSeparationMeters` and `minimumAtSeconds` describe observed samples, not a proven global minimum or exact impact time.

Violation entries distinguish:

- `observed-contact`: an observed point in time.
- `bounded-contact-span`: the pair's travel upper bound certifies the reported span.
- `sampled-contact-bracket`: a depth-limited interval containing an observed contact, without claiming contact throughout it.

Only overlapping/touching intervals for the same pair merge; nearby but disjoint intervals are not bridged by temporal tolerance. A merged entry containing a sampled bracket remains a sampled bracket. Every depth-limited unresolved interval remains in `uncertainties`, even if it also contains a detected contact. `status: violation` takes precedence over `uncertain`; callers must inspect both arrays to assess coverage. `clear` requires no observed violation and no unresolved interval.

Depth defaults to16 and must be an integer from0 through20. The smallest terminal interval is `(endTimeSeconds-startTimeSeconds)/2**maximumDepth`; boundaries are diagnostic brackets, not exact contact onset/offset. Zero clearance still tests intersection and cannot certify clear merely because no distance is negative. Unresolved zero-clearance crossings remain uncertain.

## Limits and integration hold

Sweep enumeration currently scales with the product of triangle counts, plus adaptive subdivision. Use bounded offline fixtures; performance on full retained model scenarios has not been established. Finite depth may leave intervals uncertain. These tests do not prove arbitrary articulated travel bounds, actual runtime easing, deforming/skinned/morphed geometry, or physical contact mechanics. Use ordinary static/TRS mesh geometry; no support for deformed or custom matrix-only motion is claimed.

The standalone suite covers the three reported defects, split BVH leaves and swapped caller order, persistent plus transient contact, clear gaps, uncertainty retention, invalid options, hierarchy/source mutation rejection, and the retained static/off-midpoint/articulated-arc examples.

`verify-structural-motion.mjs`, `src/`, models, Blender sources, assets, publication settings and Replit configuration remain outside this PR. In particular, main lacks the held `getToeDriveSurface()` integration API. Review any future scenario adapter and exact model inputs separately; do not promote the held runtime changes to make this helper appear integrated.
