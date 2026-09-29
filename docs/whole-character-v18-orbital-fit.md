# V18 orbital and leading crown fit — local proposal

Attempt `orbital-fit04` is the bounded refinement of V17 attempt02. It removes all scoped strict surface crossings among the 16 changed meshes and neighboring head/crown/bill/jaw/optic owners in all 21 unchanged runtime pose samples. The paired passive fittings remain visible behind the optic. This is a bounded regional fit result, **not a continuous whole-head clearance proof or owner likeness acceptance**.

## Exact artifacts and authority

The immutable input is `assets/models/whole-character-v17/attempt-02/murderbird-whole-character-v17.blend`, SHA-256 `7d371907b279eb3d625e67164d84a78b2901a5cb6a79917def07f48ff8792d7b`. The output is [the editable native](../assets/models/whole-character-v18/attempt-orbital-fit04/murderbird-whole-character-v18.blend), SHA-256 `7b7fd9c09ff67426012fb0b714c071f4258e6ca7fc9849cc9d87834540810642`. [The receipt](../assets/audit/whole-character-v18/attempt-orbital-fit04/receipt.json) freezes the executed module and composer. Neither input nor historical assets were overwritten.

The actual owner target at `context/threads/assets/murderbird-owner-likeness-rejection-2026-09-28/2-Pasted-Image-2.jpg` and owner-preferred July image at `context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png` were directly viewed alongside V17's actual native gray render. July remains head-only. Visible clustered circular machinery, a recessed dominant optic, constructed open cheek and swept crown inform the change. Perspective artwork does not establish fitting functions or exact dimensions; the secondary forms remain passive reconstruction proposals with unknown function, not sensors.

## Construction and preservation

[The regional module](../scripts/regions/whole-character-v18-orbital-fit.py) changes 16 existing meshes without adding, deleting or hiding objects:

- The two retaining races keep their existing bearing-seat radius and taper their outer radius from 71 mm to 67 mm. The six bridge inner ends follow that narrower collar.
- Four passive fittings move onto staggered seats on the rear orbital arc. Their face radii are 14 and 12.5 mm; a 149 mm lateral rear seating plane supports stepped faces at 155 and 161 mm. These authored dimensions are proposals. The front faces stand above their backing instead of being stacked beneath the temporal crown.
- The first swept temporal lamina and corresponding root fixing on each side receive a smooth rising lower return, with at most 34 mm vertical rise, 12 mm rearward displacement and 6 mm lateral inset. The upper ridge above world Z 1.745 m keeps its YZ profile; the higher crown and other temporal laminae remain unchanged. A paired-skin forward underlap then moves only the leading shingle laterally beneath the fixed brow/arc, with its outer surface limited to 114 mm lateral distance until Y −285 mm and a smooth aft return. Corresponding skins receive identical lateral translations so their wall vector and YZ profile remain exact at that stage. The matching root fixing is reseated at 118 mm. This forms a tighter shingle return around the seated fittings without arbitrary holes or a whole detached-looking plate lift.

All existing direct owners and object identities are retained. The optic/bearing/housing, bill, jaw, cheek, other region meshes and all material definitions remain exact. The composer verifies 52 rigid nodes and their parents/transforms, 462 historical guide curves and 697 unchanged meshes. Saving and reopening the native reproduces the same snapshot. Crown pieces retain `cranial-cover` ownership; orbital fittings retain `head` ownership. The same passive geometry remains eligible in Maker, Mechanic and Advanced; the optic's original Advanced-only eligibility is preserved.

## Review and verification

The six matched neutral before/after view pairs are in [the attempt04 audit directory](../assets/audit/whole-character-v18/attempt-orbital-fit04/). [The head view](../assets/audit/whole-character-v18/attempt-orbital-fit04/after-head.png) was directly inspected. Draft01 is retained separately; its whole leading-plate rise read as a lifted flap and kept the fittings obscured. Attempt02 replaced that translation with a local return and exposed both stepped round fittings but retained four inherited crown/brow/arc crossing identities. Attempt03 tried an upper lap; it was visually rejected because it flattened the petal into a horizontal blade. Both remain preserved. Attempt04 keeps the successful local return and fitting seats, then forms the finite lateral underlap to resolve the remaining crossings. It was directly viewed; the fittings remain visible and the swept crown remains integrated. This remains a construction draft with broad overall geometry and no finish pass.

[The strict summary](../assets/audit/whole-character-v18/attempt-orbital-fit04/orbital-fit-summary.json) and [full pair evidence](../assets/audit/whole-character-v18/attempt-orbital-fit04/orbital-strict-clearance/strict-clearance.json) bind the native and existing V17 runtime packet, SHA-256 `1964918661da857878376ff95457f3b8e0bc73479bd83225a8419fb1e2a627f9`. The read-only check replays all 21 actual matrices on both input and output, enforces less than 2e-6 world-matrix error, recomputes fresh BVHs and uses the existing strict noncoplanar edge-through-face kernel. Changed meshes are compared to all meshes owned by head, cranial cover, upper bill, jaw and Advanced optics; different direct-owner pairs are screened. It does not rely only on the stored V17 candidates.

| Check | Result |
| --- | --- |
| Native composition and reopen; rigid nodes, historical guides, materials | PASS |
| Six matched view pairs emitted and actual head render inspected | PASS; regional visual improvement, no owner acceptance |
| Race/form/bridge to moving crown/root fittings, all 21 samples | PASS; zero strict crossing identities |
| New different-owner crossing identities relative to V17, all 21 samples | PASS; zero new identities |
| Broader inherited leading-crown/brow/arc fits | PASS in all 21 samples; prior four identities removed |
| Half/full inspection opening and separation in the scoped screen | PASS; no scoped surface crossing identities |
| Continuous sweep, full containment, force/strength, physical contact | NOT RUN |
| Integrated V18 export, app/WebGL/fallback, build, CI, deployment | NOT RUN in this regional task |
| Owner approval and all three finished exteriors | NOT RUN; outstanding |

Different-owner strict surface counts improve from 12 to zero in closed/action samples and from six to zero at quarter opening. These are scoped pair identities, not an overall model defect count. Same-owner designed mating is excluded and not certified. Parent integration must preserve this evidence and test the combined candidate; no app default, commit or publication was made here.

## Exact inherited lap defect and repair

The additional four pairs were surface penetrations between the first moving temporal guard and fixed orbital plates, not intentional fastener seating. Their exact identities were:

| Moving crown | Fixed target | Role and recorded attempt02 rest contact location, metres |
| --- | --- | --- |
| `Swept temporal lamina -1 0 0` | `Forged orbital brow -1` | Crown lower forward surface vs fixed upper brow; target X −0.1478401..−0.1258294, Y −0.3914839..−0.3158017, Z 1.7287819..1.7419283 |
| `Swept temporal lamina 1 0 0` | `Forged orbital brow 1` | Symmetric right-side brow lap; target X 0.1258294..0.1478401, same YZ bounds |
| `Swept temporal lamina -1 0 0` | `Forged orbital mounting plate -1` | Crown forward return vs upper orbital arc; target X −0.1503364..−0.1407915, Y −0.3844266..−0.3625869, Z 1.7112279..1.7286394 |
| `Swept temporal lamina 1 0 0` | `Forged orbital mounting plate 1` | Symmetric right-side arc lap; target X 0.1407915..0.1503364, same YZ bounds |

At quarter opening the two brow pairs remained, with target Y −0.3940215..−0.3759492 and Z 1.7481179..1.7533317. The bounds describe confirmed crossing triangles, not measured penetration depth or a computed intersection line. Full pair/triangle receipts are preserved under `assets/audit/whole-character-v18/attempt-orbital-fit02/orbital-strict-clearance/strict-clearance.json`. Attempt04's underlap pulls that leading surface beneath the fixed brow/arc while retaining its rear sweep. All four identities disappear from its fresh full scoped search at every sampled pose.
