# V20 whole-body and cervical construction studies

These are held production studies. The owner target remains the whole-bird reference; the July image controls head identity only. No study here is owner likeness approval, complete runtime clearance, publication, or a new app default. The proportions-only runtime derivative has separate bounded engineering checks documented in whole-character-v20-checkpoint.md.

Pinned starting native: V19 attempt02 `assets/models/whole-character-v19/attempt-02/murderbird-whole-character-v19.blend`, SHA `d98c46770101ad608fe2c50212a7b307ca66d5389f93ce7d43b79b9c7d41dded`. All prior binaries and executed sources are preserved.

| Study | Native SHA | Visual finding |
| --- | --- | --- |
| proportions01 | `f2d301f7418b6fef68aadc6f98bd914166aab91f628e8e23a4d5364525d3042e` | Held/rejected: excessive head rise, stretched smooth throat, undersized mantle, flattened angular talons. |
| proportions02 | `3bfd8381ef8910382da8642f3d076a62e066988d448d4ddc8556cdd2db897306` | Useful provisional base: retained curved talons, stronger limb sections and substantial breast; neck skirt/collar and blanket mantle unresolved. |
| cervical01 | `2dd289331e7b1590a2b2a144a8f3885fb3e565abaa8c77efaa754ebc1277cedd` | Held: shorter courses remove skirt, but broad horizontal bands, angular two-bank bend and straight reveal slot remain. Root course5 was effectively flush at breast rather than deeply underlapped. |
| cervical02 | `8907942e733a31b8d7d9de97eaf066b98a4cd39acf964214ef335e3441c166fb` | Rejected by independent and root final visual gate: smoother front and removed straight slot still read as broad horizontal collar/drum bands with gaps. No integration, export or motion test. Negative backing-offset fade repair is current source only and was never built into any native. |

Native paths use `assets/models/whole-character-v20/attempt-<study>/murderbird-whole-character-v20.blend`; matched clay, receipts, executed sources and numerical section records use matching audit folders. Before/after cameras and lighting are identical within each study. Source appearance and era eligibility are retained, with neutral clay and no material polish.

## Broad proportion contract

`whole-character-v20-proportions.py` exposes `map_point(owner, old_native_world_point)` for attachment derivation. `SOURCE_ROOT` may be supplied when loading exact frozen source. Native coordinates are metres, Z up, negativeY front; browser conversion is `(X,Z,-Y)`. `attempt-proportions02/rig-shape-contract.json` contains all52 old/new world/local matrices. Fifty-one world node transforms change; the root `murderbird` world transform remains unchanged. All52 named owners and their parent relationships remain.

The second study raises the unscaled head100mm and moves it forward55mm; torso retains anterior depth×1.10 and rear depth×.94, with modest height compression and broad shoulders. Mantle uses an independent map retaining depth and fan area instead of compounding torso compression. Limb journals grow equally in the two radial directions about nativeX. Thigh/shin/foot roots strengthen around the coordinated joint segments; toe, phalanx and curved claw surfaces move as a planted cluster without per-vertex height warping.

The first study's foot-height interpolation destroyed talon curvature; its200mm head rise and compounded mantle depth compression were implementation mistakes, not evidence of a desired reference proportion. They are preserved as rejected studies. The second corrects those operations. The remaining whole-body failures are construction relationships: the mantle still reads as a plated blanket; breast repeats remain broad; limbs retain exposed ladder structure. Larger recognition is not solved by the local-neck improvement.

The broad derivative maps historical guides as well as744 source meshes. It does not assert guide geometry identical to V19. Its editable controls are Python profile tables, native JSON on `body`, and one meridian guide; the result is baked rigid geometry rather than a live lattice modifier. Body/cervical bearings still pass through the regional cage and do not have a demonstrated circularity result. Procedural transmission gear spacing must remain rigid under the mapped attachment metadata.

## Local cervical scope and construction

The independent `whole-character-v20-cervical-guards.py` starts from preserved proportions02 and changes exactly20 surfaces: six `Throat formed lamina` courses, twelve `Cervical flank lamina -1/1` courses, `Lower cervical open backing`, and `Cervical articulated inner guards`. No node or head change. Courses1–3 remain cervical-upper-owned;4–6 remain neck-owned. All source era properties remain.

Cervical02 uses continuously differentiable shape-preserving interpolation through its shared root/intermediate/head profile. Rounded free edges extend down; flank edges sweep aft and taper14%, with alternating+17/-10mm elevations. Angular overlap between front/flank guards breaks the straight reveal. Finite outer walls are4.5mm; radial lap step5.5mm is an authored proposal, not a running-clearance proof. Inner backings are separate open strips, rather than a closed smooth cervical tube.

Actual central-band evaluated sections atZ1.36: breast frontY=-.40221m, course5 frontY=-.38702m, a15.19mm buried depth relationship. AtZ1.32: breast frontY=-.41663m, course6 frontY=-.38636m,30.27mm depth. Breast lip topZ=1.38758m. These are discrete rest sections and do not prove all-angle or moving clearance.

`finite-scope.json` for each cervical study confirms20 evaluated closed positive-volume solids,52 exact rigid rest snapshots,724 exact other mesh snapshots,463 exact curves and retained source properties relative to proportions02. This finite/scope result does not validate intersections or motion.

The cervical02 executed source fades all radial offsets at the root, accidentally fading negative backing offsets too. Current editable source repairs that by fading positive offsets only. The preserved cervical02 native/source are not rewritten. Any selected combined derivative must freeze this repaired source separately as `executed-cervical-guards.py` and report its distinct hash.

## Attachment metadata and gate

The root-authored `attempt-proportions02/mapped-mechanism-proposal.json` contains glTF owner-local socket proposals derived from the exact proportion map. The proposal is embedded in the proportions-only runtime01 native and preserved in runtime02. It was not embedded into a cervical combined native. Both cervical forms were rejected, and no cervical combined01 was created. These are transformed legacy placements, not proven new bearing seats. Joint/socket fit and live hardware appearance require separate review.

The builder executed its proportions-only runtime01 path with that JSON property, frozen source chain, exact52 node rest checks, metadata save/reopen check, rear clay and fixed Maker/Mechanic views. No cervical combined native, GLB export or expensive regional motion checker was run. Geometry work stops at this checkpoint. The root will change the reconstruction method before another neck attempt.

## Final source state

The current editable cervical module differs from the preserved cervical02 executed source by one technical statement only: `radial*=ease((z-1.375)/.035)` became `if radial>0:radial*=ease((z-1.375)/.035)`. This retains negative inner-backing offsets instead of collapsing them toward the outer root. It has never been built into any native. The proposed `attempt-combined01` was specifically cancelled after the visual rejection. The builder enhancements for source naming, metadata preservation and additional era/rear views were executed in the separate proportions-only runtime01 candidate; no repaired cervical source was used.

Final stable source hashes: proportions module `31fc8d2cb1626570403e823eb1d97ac8b763e6849a00660a9ee58dff4163cd00`, byte-identical to proportions02 executed source; current unbuilt cervical repair `47490056aa289ef9e90e52814da66fb04aee6f395910d84f37f8ecfbe42724e4`; preserved cervical02 executed source `4805daf873e149976b2e4913f670f5a56487674411fb100c62d565b5186156a8`; enhanced builder executed for proportions-only runtime01 `5a89b4ef7f6dcc337211493ef126833ac259bfae75398c47fc8fc26bd2daba90`.

Root exported proportions02 as runtime01 for bounded pivot/attachment validation with socket metadata, then preserved runtime02 with the two inherited NaN-producing breast tips repaired. See the checkpoint for exact native/export hashes and actual results. That does not advance either cervical variant or confer likeness acceptance. Next geometry should establish one coarse shared neck and upper-breast silhouette before guard subdivision; guard variants around independently inherited envelopes are exhausted at this checkpoint.
