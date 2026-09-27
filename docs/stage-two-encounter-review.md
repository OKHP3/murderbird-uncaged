# Stage Two — a moving, flightless MurderBird

**2026-09-27 · local production prototype · owner acceptance pending.** The Builder now travels through its enclosure, watches, tests a bar, notices a chosen visitor position, braces, strikes, recovers and remains agitated. Inspection brings it to a supported stop; reassembly restores the encounter. This is an integrated direction review, not a finished-character or release approval.

- [Play the local exhibit](http://127.0.0.1:5174/) or [the production build](http://127.0.0.1:4176/).
- [Watch the uncut encounter and compare the likeness](../assets/audit/uncaged-presence-review/encounter-review.html).
- [Exact owner brief](../context/threads/stage-two-owner-brief-2026-09-27.md), [before-work baseline](stage-two-reference-baseline.md), [tool research](stage-two-tool-research.md), [model provenance](../provenance/uncaged-presence-study-2026-09-27.json).

## What changed and why

The inspected shield study had rigid named upper-body assemblies, no exported animation clips, no moving leg hierarchy and no root travel. Its visitor response moved the head, neck and wing shields against a fixed front rail. That confirmed the owner's experience of a largely stationary exhibit. A different rendering engine would not supply the missing articulation, locomotion or behavior.

The new derivative narrows the round torso, tapers the lower trunk, gives the head and hooked bill more prominence, revises the neck/shoulder relationship, compacts the toes and darkens the metal palette. Overlapping cranial plates and bill seams improve its silhouette. These are visible design changes; their success as MurderBird likeness remains an artistic judgment. The close comparison still exposes a simplified cheek/bill, thin crown plates, repetitive armor and insufficient material wear.

The animal analogy controls attention, speed and confidence. MurderBird remains a flightless mechanical bird with a compact rear outline, hooked bill, bird feet and tucked shields. The right shoulder and elbow drive the short guard/shove while the repaired left side has less travel. No dinosaur body, dinosaur opponent, flight animation or cloud AI was added. The character's fictional tactical intelligence is represented by local behavior rules.

| Bottleneck | Implemented locally | Remaining limit |
|---|---|---|
| Likeness/model | Revised proportions and a larger plated head; earlier models preserved | Bill/cheek construction, neck transitions, plate pattern and wear still need an art pass |
| Rig/articulation | Rigid thigh → shin → foot → toes hierarchy; shoulder → elbow shields; dedicated upper bill | Hidden bearings, geometry and mechanisms are production proposals, not certified construction |
| Animation | Starts, planted steps, turns, head tracking, loading, contact, recoil and settling | Mostly procedural poses; no finished authored animation library or claw-grip action |
| Behavior | Seeded watch/pacing/boundary choices, cooldowns, attention and residual agitation | Choreography and personality need owner judgment; long-duration variety is limited |
| Grounding/contact | World-space planted feet, two-link leg solve, pelvis reach correction, actual bill contact at the target bar | Kinematic constraints, not rigid-body dynamics, force simulation or center-of-mass certification |
| Rendering/materials | Existing Three.js scene, opaque armor, contact-related cage movement | Simplified shading and surface history; close views expose reconstruction seams |
| Browser delivery | Existing Vite/Three/Web Audio pipeline; local hardware browser and fallback checked | Large main bundle; broader devices and browsers untested |

## Model and motion contract

The editable source is [murderbird-presence-study.blend](../assets/models/uncaged-presence-study/murderbird-presence-study.blend), built by [the new generator](../scripts/build-uncaged-presence-study.py). It contains **2,038 mesh objects, 39 empties and no armature**. The [GLB](../assets/models/uncaged-presence-study/murderbird-presence-study.glb) batches these into **24 meshes, 63 nodes and 89,068 unique triangles**, at **3,425,344 bytes**. All earlier source studies and generators remain intact. Creative material remains all rights reserved under [NOTICE.md](../NOTICE.md).

The character uses rigid articulated assemblies, with no skinned deformation. Units are metres, Y is up and +Z is forward. The approximate two-metre authoring convention is not a story measurement. Thighs are children of the character root; their hip origins follow the transformed pelvis. Each shin follows its thigh, its ankle-pivot foot follows the shin, and its toes follow the foot. Armor retains its shape.

One short head-rotation action, `attention-export-proof`, survives Blender export as a 1.033-second glTF clip. The actual browser's `AnimationMixer` sampled a **0.11847-radian** head rotation. That proves this asset's animation export path; it does not imply the complete encounter was baked in Blender. Encounter choreography is produced by [presence-state.js](../src/scene/presence-state.js), [presence-motion.js](../src/scene/presence-motion.js) and [presence-exhibit.js](../src/scene/presence-exhibit.js).

Root acceleration/deceleration and turning are bounded. A planted foot keeps a world-space position until its next swing. Predicted root movement sets the next placement, while cadence shortens with speed. Each swing lifts the foot, advances it and returns it to the floor; the pelvis and leg solve keep the structural chain connected. Loaded forward travel alternates supports. Small corrective same-side steps are permitted during turning or settling. The test records distinguish these from repeated same-side travel.

The cage has usable interior half-extents of 2.9 × 2.1 m. Three front visitor targets align with bars at x = −1.2, 0 and +1.2 m. The leading vertex of the dedicated upper-bill mesh is constrained to the inside of the selected bar and checked against its cylindrical surface. A slow cage press differs from the fast, anticipated visitor strike. Vibration follows contact; the camera does not shake. This does not model force, deforming bars or continuous general-purpose collision detection.

## Behavior, controls and interruption

The Builder alone has autonomous `watch`, `pace`, `boundary`, `cage-test`, `notice`, `approach`, `warning`, `strike`, `contact`, `recover`, `agitated` and `settle` phases. Seed **927** makes the default sequence reproducible. Attention, agitation, dwell times, recent interactions and physical readiness constrain transitions. The control system waits for arrival, alignment and planted feet before committing contact actions.

Choose **Your position**, then **Reach toward bars** using mouse, touch or keyboard. An armed tap is also available. Orbiting, zooming and ordinary dragging do not provoke an attack. The bird first turns its attention, then approaches, prepares and strikes toward that rail. Repeated input cannot stack attacks. Retreat before commitment cancels the approach; after commitment, the action completes and recovers before residual agitation subsides.

Inspection requests deceleration and completed foot placement before opening. Autonomous motion remains suspended while covers or separated parts are open. Reassembly closes them before returning to watch/pacing. Pause freezes the actual pose; requesting inspection while paused still permits the short grounding transition. Reduced motion finishes any active step, then provides a stationary textual response without a strike. Maker and Mechanic remain interpretive, non-autonomous eras with their separate winding/power/processing visibility.

## Executed local checks

| Check | Evidence and result |
|---|---|
| Required install/build | `npm ci` and `npm run build` passed; no added runtime dependencies. Existing fsevents install-policy warning and Vite main-chunk warning remain |
| Pure behavior | `node --test tests/presence-state.test.mjs`: **9/9 passed** |
| Actual GLB integration | `node scripts/verify-presence-motion.mjs`: **12/12 passed**, including three seeds, 60-second unattended samples, a coarse 0.1-second step, all three target rails, pre/post-commit retreat and inspection during activity. [Receipt](../assets/audit/uncaged-presence-review/motion-validation.json) |
| Native source | Reopened in Blender with automatic script execution disabled; editable objects and action found. [Receipt](../assets/audit/uncaged-presence-review/native-source.json) |
| Source/build validation | `python3 scripts/verify-presence-assets.py`: required hierarchy, one proof clip, zero skins, source/build GLB byte identity and exact **26-file** runtime allowlist passed. [Receipt](../assets/audit/uncaged-presence-review/asset-validation.json) |
| Continuous encounter | 60 seconds without input, followed by approach, directed contact, retreat, residual agitation, inspection/reassembly and resumed travel. Four assertion groups passed, muted, no page/console errors. [Receipt](../assets/audit/uncaged-presence-review/browser-encounter.json) |
| Final delivery | Three checks passed after the small-screen overlay correction: retained part controls, all review images and video playback, and final production WebGL without development diagnostics. [Receipt](../assets/audit/uncaged-presence-review/delivery-validation.json) |
| Browser regressions | **10/10 passed**: orbit/keyboard, target contact, repeat rejection, pause/inspection, eras, reduced motion, retreat, mobile touch, failed-model fallback/retry, production audio/context-loss recovery and console health. [Receipt](../assets/audit/uncaged-presence-review/browser-regressions.json) |

The unattended integration runs cover approximately 4.9–9.3 m of travel with 61–91 steps. Solved foot-origin error stayed below the 2 mm tolerance; planted soles stayed at the intended 2 mm floor clearance. Contact and character bounds passed the tested scenarios. These numerical results address slipping, reach and penetration in those runs; they do not establish convincing acting or engineering balance.

The final recording uses headed Chromium **151.0.7922.34**, Apple **M4 Max Metal** rendering, macOS **27.0**, 36 GB RAM, a 1440×1200 viewport, a 989×648 scene and device scale 1. [Host receipt](../assets/audit/uncaged-presence-review/host.json). Its sampled rolling frame-rate estimates have a **99.98 fps median**, with a **44.69 fps minimum during startup**. The video capture itself is 25 fps. Performance must not be compared directly with the baseline's 9.2 fps software-rendered sample as if they used the same GPU path.

The final MP4 is **90.40 seconds**, 1440×1200 H.264 at 25 fps, 8,607,898 bytes, with no audio track. It is an uncut transcode of the browser's WebM recording, including the initial load. The measured encounter after readiness lasts 89.179 seconds. Before visitor input, the bird travels about **8.31 m over 82 steps**. Approach occurs at encounter time 60.114 s, contact at 68.240 s, retreat at 68.264 s, inspection request at 71.203 s, stable separation at 73.619 s, and reassembly request at 75.243 s; travel resumes before the recording ends.

Normal lighting, default camera and muted sound were used. Close neutral and side-step captures supplement the recording; they are not substituted into it. Reference comparisons have approximately matched viewpoints, not calibrated camera/lens matches. Visual review of captured frames and automated telemetry does not substitute for the owner's continuous perceptual review.

Mobile coverage is Chromium touch emulation at 390×844 with the operating-system reduced-motion preference. Small-screen part markers are hidden to avoid obscuring the character; the accessible part list remains available. A physical phone, Safari, Firefox and a screen reader were not tested. Illustrated fallback is a fixed image plus assembly explanation, not 3D locomotion.

An initial browser test failed because it expected `pace` at a point where `boundary` was also a valid choice; the test now reloads the fixed seed and accepts either moving state. A subsequent audio check read the existing asynchronous loading label too early; it now waits for playback readiness. These were corrected test assumptions. No observed application error was suppressed. The preserved initial failure receipt is historical, not the current pass result.

## Handoff and remaining owner decisions

This branch is **`codex/uncaged-production-review`**, based on local commit `4ba4a46`, in the existing managed production worktree. The independently active primary checkout was left untouched. New code, model source/export, owner-direction snapshot, evidence and review documents belong to this repository. Source assets, provenance, audit pages and recordings are excluded from `dist/`; only explicitly imported runtime assets and existing public delivery files are emitted. The bundle includes the existing optional theme audio, which accounts for most of its approximately 44.9 MB total.

No remote CI, push, PR, deployment, external model upload, purchase or new plugin installation was performed. The baseline report records the public build checked before this work; it is not this local Stage Two version. Publication and clean-clone retrieval remain separate unperformed release checks.

**Owner review needed:** does this now read as a deliberate, formidable mechanical bird while it moves, and are the revised proportions a useful base? In particular, judge head/bill identity, supported turning, strike preparation/recovery and the continuing sense of attention. Technical checks pass, but likeness, weight, personality and final art are not accepted by those tests. The recommended next production pass is head/cheek and neck construction plus authored pose/timing refinement, guided by that review, before expanding the action catalog or considering another engine.
