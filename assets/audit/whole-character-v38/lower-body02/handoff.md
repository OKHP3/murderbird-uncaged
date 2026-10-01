# Lower-body checkpoint — two held studies, 2026-10-01

Status: **HOLD**. Upper-contour01 remains the working basis. Production remains V37. Neither lower-body01 nor02 is selected, fitted, owner accepted, merged or deployed. The pelvis taper makes a visible gain, but01's metatarsals read as smooth hulls and02 has a definite missing metatarsal-to-toe receiving transition. Only two shapes were saved; no third shape was attempted.

Fetched GitHub branch `codex/v38-upper-contour-integration-01` at exact `22ebf9955db867e86f37d20e0a10771809fa4ade`. Actual pinned upper-contour01 native SHA256 `c83514b1671c5022ad2ce1d6e06277bb62a8e1c51bfb905a615b3350ecf225a0`; GLB `91b8dbff036b7ac96f8cc03a13f836115f8330526a6085512dfb61882336ab55`. Actual Master03, Maker-clean, Mechanic and baseline neutral front/profile/3Q were viewed. Master03/era media control lower-body identity; July remains head only. Dimensions are reconstruction choices, not image metrology.

## Exact outputs and changed scope

-01 native `4105bb3698d2b97f145245c21835216cc1f60796bbc1cc6069ce3f0c08263505`; GLB `58c6fe6bfdaa81de88d4f58adf8dd7c05ad8150d25c7f2a883f08a1011ce0145`.
-02 native `24669e667ea2a8d0fe1c45f36caeaa1e09273be30aea22a0584885f653f7fa44`; GLB `3002ad4f98ac7c3a98c9cbcbce6c747176441eaba42c9745f73ab0d8ce98f80a`.

Owned paths: `scripts/build-v38-lower-body.py`, `scripts/regions/v38-lower-body.py`, model/audit directories `lower-body01/` and `lower-body02/` under `assets/{models,audit}/whole-character-v38/`. Current scripts generate02 and refuse existing saved outputs. Each audit directory contains its frozen executed recipes, four actual matched neutral whole-bird views, model/export receipt and a read-only neutral surface screen. Original builder receipt is preserved as `generated-receipt.json`; current `receipt.json` adds this postvisual HOLD qualification. Native/GLB files were not altered after their save/export.

Each shape changes71 existing mesh object snapshots, adds/removes0 objects and preserves1150 other snapshots. Exact changed component names/signatures are in each receipt. Components are lower breast plates/backing, side/dorsal/pelvic skins; paired thigh/shin primary channels; foot-owned metatarsal rails, compound truss and instep guard. All changed structures remain inherited passive, eligible Maker/Mechanic/Advanced; no actuator, sensor, new repair or organic skin was introduced. Object transforms, pivots, mechanismLayoutV1, dedicated bearing objects, digits and floor geometry remain exact. That list does not include embedded fixed receivers removed from the compound truss.

## Known defects and mechanical evidence

The entire `Left/Right metatarsus open passive truss` mesh was replaced. The source has1056 native vertices/1026 faces per side, including the broad toe-root crossmember and six split receiving cheeks per foot.01 replaced it with a longitudinal rear web;02 replaced it with two short cross ties (16 native vertices/12 faces). This deleted the actual receiving geometry and its support. The implementation failed to preserve the compound mesh's functional subgeometry; unchanged object names and surviving moving pin/collar meshes do not repair that loss.

02's actual eight distal terminal vertices are25.04–39.76mm from the nearest sampled named toe-bearing flange surfaces. Proximal terminal vertex samples are4.48–22.46mm from the nearest retained yoke. These finite-surface vertex samples document a gap; they do not certify full-face seating or a supported load path.02 cannot become the integrated lower-body basis.

Neutral evaluated surface screen: source104 leg crossing object pairs,01 120,02 106. These are individually listed actual BVH triangle surface crossings at epsilon0, not automatic collision exclusions.02 adds two cross-owner shin/channel vs upstream thigh-clevis crossings,20 triangle pairs each, across all three eras. New same-owner crossings also exist at journals, keeper bolts, channel collars, cross ties and yokes; possible proposed fixed fabrication is not a validated union or blanket exemption. Both evaluated changed-stock screens show0 nonmanifold edges; this does not establish fit.

01 introduced118 crossing triangle pairs between the breast liner and `Power retaining strap` in Advanced.02 preserves the source field within25mm of the actual strap surface with45mm blend and reports0 crossings in the stated named mechanism scope. This limited neutral screen does not establish concealed-volume clearance, attachment seating, posed motion or all mechanism coverage. Fixed frame/skin receiving mismatches and visible torso seams/holes remain review concerns.

Inherited `constructionDescription`, `railEndpointWorld`, `jointCentersWorld`, `footAssemblyRevision` and related extras retain older source/V25/V37 claims on changed meshes. They are **stale historical annotations**, not current fit or receiver evidence. The next source correction must update them alongside geometry; the frozen models are preserved to expose this inconsistency.

## Checks and next action

PASS: pinned native/GLB byte hashes; declared snapshot change scope; native save/reopen equality; object hierarchy/rigid-parent identities; exact material/PBR era-finish retention; actual neutral front/profile/3Q/rear renders; read-only evaluated stock/surface screen execution. FAIL/HOLD: compound metatarsal receiving support preservation and current construction fit. WARN: additional same-/cross-owner surface crossings, torso fixed-frame interfaces and stale extras. NOT RUN by this worker: app/runtime edits, npm/full integration build, illustrated fallback, runtime pose/extreme clearance, engineering/load validation, CI/deployment and owner acceptance. Root owns app review and checkpoint commit/push; this worker made no commit/push and preserved unrelated dirty work.

Next increment starts from upper-contour01. Preserve the actual source split receiving cheeks, their webs and toe-root landing crossmember; develop stronger open paired members around those exact receiving submeshes. Keep the useful pelvis taper as a separately reviewable reconstruction, verify its retained frame/Advanced apparatus interfaces, and reconcile extras before saving a new candidate.
