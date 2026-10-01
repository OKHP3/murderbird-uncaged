# Cervical laps and raised skull joint study

Both saved proposals are frozen. FIRST exterior was rejected: large globe cheek armor and tall side channels. SECOND removes much of the globe but retains a broad cheek band/long rectangular rails and a large side opening; no reference gain or fit acceptance is claimed. No third attempt or production promotion. Root owns final visual/runtime verdict.

## Pinned lineage and output

Input checkpoint `9dcf57991c1bd9a6a8cb36390cb11e8d508cd5d3`; actual geometry is FIRST neck-envelope01 native `081337aa8e7c12f657f5f18dcdf27462491bf89d52b344fcbae52702770022a0` / GLB `29c815673c14c7f07d2a6a01b0881a3c2707f8b93e051d874b81625e0953ec19`. Rejected neck-envelope attempt02 was not used.

| Study | Native SHA256 | GLB SHA256 |
|---|---|---|
| FIRST cervical-laps01 | `ee89fbe177d8bbd2a64beb2139df7f196ef6b88780c3d581edd3720a6fd91d53` | `bbb911c7996165fb724cc5bd6f99a1acf51a0f0dcb8c1ab4c7ea17796e279bee` |
| SECOND attempt02 | `7d8472f23ceba59d2faa02753f30eaefd836c0f0ecfcc8c0c7442db692f10116` | `4e3e721040cdde3316eb84f19051829e771a93f80e243975e572e5707a6f007c` |

Models are under `assets/models/whole-character-v38/cervical-laps01/`, second in `attempt02/`, with corresponding `murderbird-v38-cervical-laps01[-attempt02].blend` and `-rigid.glb` names.

## Concrete layout learning

Actual old skull pivot `(0,−.3406000137,1.3888840675)` sits33.184mm above cervical-upper and below skullbase. At a170–180mm front lap radius, head counterpitch−.509 demands about83–88mm travel, causing a long head-owned skirt to reach cervical3. This motivated an integrator-authorized layout reconstruction rather than preserving obsolete pivot coordinates.

New skull pivot `(0,−.392,1.520)`, delta `(0,−.051399986,+.131115932)`m. Actual head rest geometry is compensated via direct-child local translations. No skull receiver empty exists in either saved study: the conditional code did nothing, only head moved. All18 throat guards remain head-owned; no reparenting, added nodes or body layout metadata. Jaw-local control socket is retained. Old absolute contact receipts cannot validate the new joint.

Ten additional frame meshes are reconstructed: V21 head shaft becomes32mm spherical ball; V23 cervical4 pin becomes rotating stem; two cervical4 distal races become33.2mm-inner/39mm-outer split cups with50degree upper stem aperture; two cervical4 links reach the raised cups; two V31 shaft seats relocate; two cranial bow root branches refit while upper skull stock remains. This is passive proposed compound-motion construction, not an approved spherical bearing.

Total explicit geometry boundary78 meshes (40guards+18throat+10carriers+10frame),98 declared pivot/direct-child compensation nodes. FIRST changed150 actual objects,1079 exact. SECOND changes48 actual objects versus immediateFIRST,1181 exact; the original78-mesh/translation boundary carries forward. Exact names/owner/era/root/land coordinates in each scope and receipt. Head identity rest-world comparison and actual fresh contact are root responsibilities; do not claim blanket763nodesunchanged.

## Geometry and evidence limits

Mid laps use directly authored axial-X radius functions and circular angles, radially ordered stock, and monotonic endpoint-to-endpoint core lofts. No blended/clamped sector projection. A narrow mid-b anterior fixture showed zero strict crossings at four relative pitches and3.5mm analytic radial separation. Its angular domains differ from final fullcourse domains; it is not fullskin/carrier/head-motion validation. The initial full topology assertion caught a0.061mm reversed core before saving; child root endpoint+.16→+.13rad provided a monotonic core. Earlier syntax error also occurred before saving. Both preexport failed recipes/logs remain as diagnostic history.

FIRST outer throat151/158mm spheres produced the rejected globe. SECOND retains the small bearing but authors tapered elliptical cheek plates, only a126mm hidden spherical head lip mating118mm upstream lip; rear axial coverage.80→.94 of section width reduces part of sideopening. The final visible layout still fails to form the desired directional shingled C transition. It was frozen without another shape loop.

Ten compact carriers each span one actual selected source-face quad to one actual newly authored guard inner quad. Finite common stock, self-intersection, all-other-guard support and sweep remain unproven. Positive connected/manifold stock checks during construction do not establish these. No broad finite scan ran after root rejected FIRST; SECOND was also rejected by root and the independent reviewer. Actual source/candidate old-angle body-rest pitch images are a diagnostic comparison, not complete strike or freshcontact proof.

## Files and reproducibility

In the authoring worktree each audit directory has immutable `receipt.json`, `scope.json`, `executed-builder.py`, `executed-region.py`, `build.log`, four whole views, rest neck crops and matched old-angle pitch profiles. Qualified receipts correct stale inherited prose without changing frozen models. Initial audit also holds `joint-fixture.py/json/log`, `layout-inspect.py/json/log` and two preexport error recipe/log pairs. No pervertex dumps were added.

Canonical owned scripts now reproduce SECOND. FIRST executed hashes: builder `9bcdbe1d106a977436960e2616832b8df0b98d05d9844f9c4e45e54b45e158a5`, region `f78bf648927c50552e28c7c634b7069c754835dc5c5a3bb1cb99c3c89ee28db0`. SECOND hashes: builder `7d32810833a2229d5148468a5b585acbad5b82f4f7bf546b44f97200eac37e63`, region `dbad30993e9440c36dd8fdb5e44a8521b5bb088d88eb5f1986da425c6ae9948f`. Reproduce in fresh scratch canonical script/region locations with pinned inputs and unused output directories; builders are write-once.

No new textures/UV pipeline, materials, era rules, app code, production promotion or owner approval. First successful build19287 and final52250 exited0; no live builder remains. Source history and frozen outputs untouched.

Integration preserves the completed models, views, scopes and executed recipes. Build logs and failed pre-export recipes remain in the isolated authoring worktree rather than this review commit. Root integration evidence is the authority for final export/rest/contact/browser/build results.
