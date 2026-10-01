# Upper-joint-fit01 bounded checkpoint — HOLD both attempts

The final attempt repairs twisted head brackets and reduces scoped crossing counts, but introduces two same-head leaf seams in every sample and rear leaf/cervical3 crossings at captured contact. Neither proposal is ready to retain as a fitted construction. No third geometry attempt, runtime change or production promotion was made.

## Frozen models and source

Pinned neck-bearing02 input: native `5212556e154061da8a13be3ecd19195394f0781415776712a4c341f6b498f6d8`, GLB `66cd790e0de7d48c8623bd8471b1488c4b3b93e8eeba175f3c455a20cfeb06bb`; checkpoint `53dfac6aec9a90fe6ef8a483f8b3447efaa67eb9`.

- First native `assets/models/whole-character-v38/upper-joint-fit01/murderbird-v38-upper-joint-fit01.blend`: `d0acd0c2177f9ed88dfb9fcd35ae514f1297bfcd1fd3c1710ba7047103cfae88`; GLB `cffa833bfeaf861287d0f08ed856cf9a62bc68e295e4fadf2418333b077ef1c5`.
- Final native `assets/models/whole-character-v38/upper-joint-fit01/attempt02/murderbird-v38-upper-joint-fit01-attempt02.blend`: `27bfe4b45a8a5c91f94c0872265273e21aadc39de41f899dfe06d4f214468387`; GLB `f25d8af6b2f3717d243351cdcd78be6858aa13e56ae529289dfe9969bd957834`.

## Actual construction and protected scope

Both versions change only nine `V33 tapered throat cheek plate {−1,0,1} 0 {0,1,2}`, five `V23 cervical 4 directional guard {1..5}`, and four `V38 curved-neck formed yoke {head,cervical-upper} {−1,1}` meshes. Exact names are in each `scope.json`. No mesh/node additions, removals, reparenting or pivot movement. The other1211 native objects, fuller body33 plates and supports, head/bill/jaw/crown/optics, other neck courses, limbs, rigid owners, rest transforms, materials and era profiles remain exact. All reconstructed stock is passive structural geometry on its inherited head or cervical-upper owner, eligible in all three eras.

Head shaft centre is `(0,−0.3406000137,1.3888840675)` in native metres. HEAD overlap sits outside cervical-upper receivers. Final front radii178/175.5mm meet receiver168/164.5mm; side175/172.5mm meet receiver163/159.5mm. These are authored7.5/9.5mm nominal gaps, not measured clearances. Head upper16 receiving rows remain exact; only lower9 free exterior rows and connected short2.5mm lap are formed. Neck receiver lower9 rows remain exact. Short side expansion improves coverage but creates the two finite same-head seam crossings.

First head doglegs had negative volume and7/6 strict self-cross triangle pairs. Final head support uses coherently ordered direct two-cap stock with identical actual root/end cap coordinates: original cranial load bow±1 face518 to the side col0 leaf inner seat. Each is one8-vertex connected solid, closed, positive volume and zero sampled strict self-crossings. Cervical-upper roots relocate to unchanged own distal annular race−1 face60 / +1 face61, with actual finite cap loops and original face indices recorded in final receipt. Its two12-vertex connected doglegs reach guard1/5. All four final root/end common stock volumes are nonzero (~1.12–1.90e−8m³); this proves finite overlap at declared seats, not weld/fastener/load or continuous swept validity. Intended seats are still counted in collision evidence.

## Finite evidence and remaining defects

One finite screen per attempt, strict finite edge-through-face triangles, all same-owner/era-common pairs included. Final versus FIRST scoped pairs: neutral20→10; captured contact20→14; authored max pitch20→12; Maker23→13; yaw20→10. New same-head pairs, every sample: side−col0 / frontcol0 (64 triangle pairs), frontcol2 / side+col0 (59). Captured contact also introduces head rear side−col2 / cervical3guard8 (44) and side+col2 / cervical3guard7 (50). Inherited rear side−col2 / cervical4guard8 increases332→338 triangle pairs relative FIRST; relative pinned neck-bearing02 it increases254→338, while opposite rear/guard7 remains320 versus original260. Full existing source comparisons and changed-triangle counts are in qualified receipt.

All18 final stocks have positive signed volume, closed edges, and zero sampled nonadjacent strict self-crossings. Receiver formed rows0–8 have paired radial wall3.499930–3.500058mm (no negative samples). This is radial sampling, not full normal stock certification. Rest residuals include declared same-owner support/frame and support/guard common stock; these are not waived. Five static body-rest slices are neutral; captured four localX+.10675220489501955/head−.5090505059024657; authored four+.1625/head−.509; Maker four−.035/root nativeZ−.45; attention root nativeZ+.312. No complete captured strike, negative-yaw sweep, jaw cycle, containment/depth/coplanar test or engineering acceptance is claimed.

## Evidence and reproduction

Under `assets/audit/whole-character-v38/upper-joint-fit01/`, first and final `attempt02/` each contain `receipt.json`, `scope.json`, `executed-builder.py`, `executed-region.py`, `finite-screen.py`, `finite-screen.json`, logs, four matched `candidate-full-bird-{three-quarter,profile,front,rear}.png`, source/candidate rest/contact neck profiles, contact whole3Q and static inspection neck view. Inspection is breast+1.1 nativeX and cranial coverZ+.08 at body rest, not full runtime exploded proof. `qualified-receipt.json` and final `attempt02/qualified-receipt.json` qualify preserved raw annotations without rewriting frozen binaries/recipes.

Canonical `scripts/build-v38-upper-joint-fit01.py` and `scripts/regions/v38-upper-joint-fit01.py` now reproduce final attempt02 (hashes in final receipt). First frozen executed recipes remain authoritative for first. To rerun, copy the chosen frozen recipes into those canonical script locations in a fresh repository-shaped scratch directory with its pinned inputs and reference paths; write-once output checks deliberately prevent overwriting frozen models. Do not execute an audit-located builder in place because its repository-root calculation assumes `scripts/` placement. The final build is a distinct second design, not a normal-flip repair of first twisted stock.

The remaining narrow next problem is coordinating adjacent side-head course edges and rear head/cervical3 travel together while retaining source gap coverage and these finite supported routes. No next increment has started.
