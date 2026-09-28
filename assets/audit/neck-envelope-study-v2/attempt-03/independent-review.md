# V7 cervical-envelope study, attempt 03 — bounded review

**Decision:** HOLD from V8 composition. This is a native-only authored proposal, not measured from candidate03 and not owner accepted.

The candidate is `assets/models/uncaged-neck-envelope-study-v2/attempt-03/murderbird-neck-envelope-study-v2.blend`, SHA-256 `a5bdb183e05ad32fd77af234c8e8d7b5b7f7f488423c8ad78c104c63c15b0062`. It is derived from frozen V7 native `a8fccaf024a096678415215029b34cae8270b348da2301b8872a34e72c75ed3f` and pose packet `874396ede48a63d37d743a1a85ae885a10e614a4461f46c50f3a62744a9e2813`. The exact V7 scene snapshot helper is pinned in `study-manifest.json`.

Only the existing neck-owned inner guard and 17 existing throat/flank lamina mesh datasets changed. `Throat formed lamina 1` stayed byte-equivalent at mesh-signature level because the falloff is zero there. No object was added or removed; pivots, object transforms, material assignments/shaders, other mesh/curve signatures, and saved visibility matched on reopen. The two pre-existing zero-user materials `Neutral / edge.001` and `Neutral / plate.001` received only a fake-user retention flag so Blender preserved them. Inherited guides remain untouched and do not regenerate the laminae.

The two neutral Workbench images show no obvious new detached exterior edge in the sampled side/rest and strike/three-quarter views. The change is subtle; the broad layered neck-to-breast mass remains visually similar to baseline. These two views do not establish a likeness improvement.

The unchanged actual-runtime pose checker applied all 17 packet poses to both V7 and this candidate. It found nine new different-owner BVH overlap-candidate identities:

- At raw rest and several unchanged Maker/attention/jump/Mechanic poses, `Throat formed lamina 4` and `Throat formed lamina 5` each gain candidate overlaps with both `Breast keel root fixing 0 0` and `Breast keel root fixing 0 1` (four identities). The two source fastener meshes occupy approximately x=±0.03m, y=-0.355m, z=1.343m.
- In recovery-entry and contact, `Cervical articulated inner guards` gains candidate overlaps with `Breast keel root fixing 1 0` and `1 1`; the two `Cervical flank lamina 2` meshes gain candidates with the matching left/right `Breast field root fixing ... 0 1` meshes.
- At inspection open=1, separation=0, left flank lamina 3 gains a candidate against `Breast field root fixing -1 0 2 1`.

The broad-phase triangle pairs do not prove physical penetration, full containment, or a visible defect. The two images do not show an obvious pin detached from a plate, but they are not close enough to establish pin seating; exact fastener gap/clearance remains unresolved. The new candidate identities at the breast fasteners are sufficient reason to hold this proposal from composition.

**Checks:** shared native snapshot and save/reopen parity PASS; exact 51-pivot rest/pose matrix application PASS for all 17 sampled poses; two requested stills rendered and visually reviewed; targeted neck-to-breast/head BVH candidate comparison completed. No GLB export, app selection, browser/WebGL test, continuous collision test, physical simulation, or artistic/owner acceptance was performed.
