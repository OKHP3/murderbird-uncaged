# Three-era movement review

Current local implementation of the [owner's three-era brief](../context/threads/three-era-movement-owner-brief-2026-09-27.md), with the subsequent [Advanced jump and thrust direction](../context/threads/advanced-power-owner-direction-2026-09-27.md). This supersedes the Stage Two assumption that both earlier machines are static and the earlier finite-power Advanced exhibit copy. The published story source and all earlier study artifacts remain preserved.

The [browser demonstration and comparison](../assets/audit/three-era-review/era-review.html) present the three control systems in sequence. Local behavior verification and creative acceptance are separate: likeness, mechanical plausibility and final character acting remain under review. Nothing in this milestone publishes the exhibit.

## Implemented progression

| Era | Control and movement | Revealed construction |
| --- | --- | --- |
| I · Maker | Fixed root and yaw. Five external controls operate a leg, shield wing, short tail, neck and jaw. With controls at rest there is no independent motion, tracking or attack. | Floor base, post, pelvic cradle, lever rack, guide supports, joint attachments and causal rods/lines. Later power, transmission and processing assemblies are absent. |
| II · Mechanic | User-engaged limited traversal. A 1.48-second cycle loads, releases a short step, settles and dwells; turns use separate increments. Stop completes the current cycle and plants the feet. A finite illustrative spring charge can be rewound. | One wound mainspring, reduction gears, eccentric sequencing cam, cross-shaft and links to the actual leg pivots. No steam system, sensors or tactical controller. |
| III · Advanced | Coordinated pacing, attention, cage tests, visitor-directed strikes and recovery. Advanced-only power jump and planted shield thrust add a deliberate demonstration of strength and agility. | Enclosed fictional continuity supply, distribution bus/conduits, joint actuators, optical sensing and separate cranial processing. No ordinary winding or power depletion. |

The root controller explicitly gates capabilities. Maker and Mechanic do not inherit visitor targeting or predatory actions. Era switches finish and ground the current action, close separated parts, briefly cover the reconstruction, restore the appropriate support and reset the new machine. Camera orientation is retained. Inspection during an Advanced jump waits for the landing; pause freezes the action; reduced motion blocks new power moves.

The jump uses a proposed 36 cm vertical rise within the cage, with loading, airborne travel, landing compression and recovery. The shield thrust keeps the feet planted and drives the right shoulder and elbow, with restrained counter-motion on the repaired left. Neither action introduces flight, a dinosaur silhouette, a cloud AI service or copied franchise machinery.

## Source and construction status

The existing Stage Two rigid model is reused unchanged: 24 GLB meshes, 63 nodes, 89,068 unique triangles; no skin/armature. Its native Blender file and one short exported head-animation proof remain preserved. This milestone adds era mechanisms procedurally in Three.js and drives the rigid assembly through separate motion paths. Those new assemblies and the continuous movements are **not newly authored Blender animations or a replacement model export**.

Source authority, historical mechanism research and the reconstruction decision are in [three-era construction direction](three-era-construction-direction.md). The cradle, control layout, spring/cam walking transmission and Advanced internals are proposed reconstructions. Runtime kinematics establish sampled joint positions, foot placement and selected cage contacts; they do not establish balance through force simulation, real load-bearing capacity or manufacturable engineering.

## Validation

Local checks on 2026-09-27:

| Check | Result | Receipt |
| --- | --- | --- |
| Node controller/state tests | 34/34 passed | [Controller tests](../assets/audit/three-era-review/controller-tests.txt) |
| Loaded GLB era motion and prior encounter regressions | 14/14 passed | [Motion validation](../assets/audit/three-era-review/motion-validation.json) |
| Loaded GLB jump, pause/inspection and rotated-position thrust | 4/4 passed | [Power-move validation](../assets/audit/three-era-review/power-move-validation.json) |
| Headed Chromium era, transition, mobile and fallback checks | 13/13 passed, no console/page errors | [Browser validation](../assets/audit/three-era-review/browser-validation.json) |
| Headed Chromium power actions and landing transitions | 9/9 passed, no console/page errors | [Power browser validation](../assets/audit/three-era-review/power-browser-validation.json) |
| Install, production build and output inspection | `npm ci` and `npm run build` completed; 26-file output allowlist passed | [Asset validation](../assets/audit/three-era-review/asset-validation.json) |

The loaded-model jump peaked at 0.35998 m above its standing root, with the head/body top at 2.4263 m inside the 2.55 m cage convention. Both feet returned to the 2 mm floor clearance used by this model. The thrust also passed from a translated root at yaw 0.63 radians; the right shoulder/elbow reached −0.64/+0.72 radians while the repaired left remained +0.07/+0.18. Solve errors are numerical kinematic residuals, not real-world measurement precision.

Mechanic browser sampling showed eight short foot steps, 0.55 m travel and a π/2 turn in twelve seconds, including load/release/settle/dwell phases. Its illustrative spring charge decreased during the routine, stopped draining after disengagement and returned to 1 on winding. These figures describe one sampled local run, not a physical performance specification.

The production JavaScript bundle remains above Vite's 500 kB warning threshold (about 747 kB, 196 kB gzip); this is a warning, not a failed build. Source artifacts, audit pages, recordings, story snapshots, production sessions and provenance remain outside the emitted build. The unchanged GLB is 3,425,344 bytes, SHA-256 `cbf75f80876669505a8919eac0875575d0ce8f2a5dcf189d84f01b76e7f3d851`.

## Recorded demonstration

The [continuous browser recording](../assets/audit/three-era-review/three-era-demonstration.mp4) runs 114.04 seconds at 1600 × 1400 and 25 recorded frames per second, with sound off. It includes all five Maker controls, a 35-second Mechanic routine with segmented turns, stop/inspection, Advanced pacing, jump, thrust, right-rail target acquisition and contact, recovery, and separate actuation/power/processing views. The original uncut [WebM](../assets/audit/three-era-review/three-era-demonstration.webm) is retained; MP4 is a format conversion without cuts.

The actual capture used headed Chromium on Apple M4 Max through ANGLE Metal at device pixel ratio 1. The scene canvas was 1150 × 648 within the page. Sampled rolling frame rate had a median of 100.0 fps; this is device-specific, distinct from the recording's 25 fps. Exact event timestamps, sampled state and hardware are in [demonstration.json](../assets/audit/three-era-review/demonstration.json), with [video metadata](../assets/audit/three-era-review/video-metadata.json). The final camera adjustment is demonstrated in this recording and was visually checked; the subsequent [production/review-page check](../assets/audit/three-era-review/final-preview-validation.json) verifies the final build's power controls, video playback, chapter seeking, links and mobile layout.

## Remaining review

The current model remains a study. Bill/cheek identity, neck transition, armor repetition and wear still need artistic refinement. The new linkages are illustrative and do not constitute closed-chain dynamics or complete collision geometry. Jump height and thrust timing are tunable acting choices. The Maker lever hardware relies on the matching interface labels; no operator character is modeled.

The illustrated fallback preserves the fixed reference image and exposes different construction schematics for each era; it does not simulate the 3D articulation, jump or thrust. Human screen-reader review, physical-phone testing, Safari/Firefox coverage, clean-clone LFS retrieval, remote CI and deployment remain unverified. Existing build-size and local installation warnings are recorded with the final receipts.
