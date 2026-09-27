# Stage Two visual and movement baseline

**Captured 2026-09-27 · visual inspection by the audit author · no owner acceptance implied.**

This is a bounded baseline for the Stage Two direction in the owner brief supplied 2026-09-27. It records the current shield-study render, the scoped appearance references, nine locally extracted video frames, and the animation channels present in the current exhibit. It does not modify the model or runtime.

## Reference authority and direct visual observations

| Source | Status and scope | Direct visual observation |
|---|---|---|
| `assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png` — SHA-256 `538c51bcdbf5bfce95a0932fdbbb0f5868b446f4985346d15e6cacd32430e633` | Lead-selected full-body identity reference; not owner approval of a 3D model. | The 3/4 view shows a large swept plated head and curved hooked bill; a deep, vertically oval trunk that narrows below the breast; a clear neck rise into the shoulders; folded layered wings; mechanical lower legs; and broad separated bird toes planted on the floor. The rear contour is compact rather than a long balancing tail. It is a single perspective view, not a measurement drawing. |
| `context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png` — SHA-256 `47658dba6496f2c8594a40ad412a8bfaa087939e90044d1597329a27ca68d4e9` | Documented owner-preferred **head identity** reference only. | The close view makes the deep convex hooked bill, layered swept crown, large circular optic housing, and open cheek/mandible line clear. The perched body, long plate train, legs, CRT support, and scale are outside its selected authority. |
| `assets/audit/uncaged-shield-review/reference-angle-model.png` — SHA-256 `c371b36d43836ad80083e39b40e4dfc600664b079c239a5e563bc762220fcba4` | Current shield-study render, captured as the technical/visual baseline. Likeness remains pending. | The rendering has an upright bird stance, a hooked beak and amber optic, overlapping armor, articulated-looking feet, and folded shoulder/forewing shields inside the cage. The torso reads as a broad, nearly spherical barrel; horizontal breast bands reinforce that mass. The head is less dominant than in candidate 03 and its cheek/bill profile is simplified. Neck armor meets the chest as stacked collars rather than a tapered articulated transition. Feet/toes look long and widely splayed relative to the compact legs. The model is stationary in this image. |

The owner’s current direction specifies combat strength and speed as behavior/mass cues while preserving bird anatomy. The Stage Two brief explicitly rejects changing MurderBird into a velociraptor. Keep the hooked-bill/crown/optic identity and bird feet; do not add a dinosaur body plan, tail, human torso, or franchise-specific geometry.

## Concrete silhouette priorities for a moving rigid machine

1. **Narrow the torso across the front and reduce its spherical outline, while retaining breast depth.** Taper toward the pelvis so the mass reads as a deep armored bird trunk rather than a barrel; preserve lateral room for shoulder bearings and shield travel.
2. **Restore head dominance and recognizable profile.** Enlarge the plated skull silhouette and bill/cheek mass toward candidate 03; retain July’s hooked bill, swept crown, circular optic, and open mandible cue. Do not solve scale by simply enlarging the optic.
3. **Build a visible articulated neck-to-shoulder bridge.** Use a compact sloped cervical stack with exposed pivots/actuator gaps and a readable shoulder yoke. Avoid several flat horizontal rings that merge neck, chest, and mantle into one cylinder.
4. **Clarify weight-bearing legs and planted feet before speed gestures.** Add pelvis/thigh/shin/ankle articulation that can transfer trunk mass over a planted foot; keep toe spread compact enough to read as a supported bird stance. Prove a weight shift and recovery without foot skating before a fast strike.
5. **Keep the folded wings compact and mechanically causal.** The current two-stage shoulder/elbow shield is directionally legible in the still, but its shove needs a driven torso/pelvis counterbalance and a recoverable planted stance. Do not add flight flapping or a long feather train to suggest motion.

These are audit recommendations, not approval criteria or owner decisions. Perspective, occlusion, and the lack of orthographic source drawings limit exact dimension claims.

## Local video frame sample

Source media were read from the hydrated primary mirror at `/Volumes/OKH-Local/04_GitHub_Mirrors/murderbird-uncaged/assets/murderbird/production/video/`; no remote media was fetched. The MP4s in this worktree are LFS pointer stubs. FFmpeg extracted the first frame at each requested seek time (0, 4, and 7 seconds) to the image paths below. The time samples are sparse visual evidence, not continuous review or animation acceptance.

| Source clip (SHA-256; format) | Sampled frame paths | Firsthand observations at sampled times |
|---|---|---|
| `murderbird-first-choice-controlled-pilot-03.mp4` — `635f0e1552bac61699c03c8406157207f6230ea817bb1ecaeb3adbb3a7bf8613`; 8 s, 1280×720, 24 fps, H.264, no audio. | [`0s`](../assets/audit/stage-two-baseline/first-choice-controlled-pilot-03-0s.png), [`4s`](../assets/audit/stage-two-baseline/first-choice-controlled-pilot-03-4s.png), [`7s`](../assets/audit/stage-two-baseline/first-choice-controlled-pilot-03-7s.png) | The three sampled frames retain the same workshop composition, both floor-supported feet, and adjacent pivot/support. Any deformation is too subtle to distinguish confidently in these samples. The existing motion record describes restrained torso/saddle shift and slight head lowering. This exact silent 2D clip was accepted for story-page use only; it does not demonstrate 3D rigging, a cage interaction, or locomotion. |
| `murderbird-mechanic-legacy-original.mp4` — `47332a9aa9cae09fdfaee9626cf2fe128eb93f85eea1e94f3b8bcd00035763ce`; 8 s, 1920×1080, 24 fps, H.264 with AAC. | [`0s`](../assets/audit/stage-two-baseline/mechanic-legacy-original-0s.png), [`4s`](../assets/audit/stage-two-baseline/mechanic-legacy-original-4s.png), [`7s`](../assets/audit/stage-two-baseline/mechanic-legacy-original-7s.png) | The sampled workshop composition keeps the plated bird and visible mechanic/operator context. The 0s view includes a loose armor piece on the floor; the 4s sample shows a large blurred forward/downward limb movement; the 7s sample shows the limb nearer a low, supported position. Samples do not establish a continuous, mechanically valid action or modern cage choreography. |
| `murderbird-sentinel-legacy-original.mp4` — `e834ca4d67e57c4e390fda434db154d127d106d483666f901a6be2b23b7d93e3`; 8 s, 1920×1080, 24 fps, H.264 with AAC. | [`0s`](../assets/audit/stage-two-baseline/sentinel-legacy-original-0s.png), [`4s`](../assets/audit/stage-two-baseline/sentinel-legacy-original-4s.png), [`7s`](../assets/audit/stage-two-baseline/sentinel-legacy-original-7s.png) | The scene begins with the bird perched on a CRT. At 4s a talon/limb is extended toward the screen while the other foot remains planted; at 7s the bird is again near a perched stance. This is useful as a visual example of a one-sided reach and return only; sparse frames cannot verify balance, timing, contact forces, or leg mechanism. |

The existing [media catalog](media-catalog.md), [asset capability audit](asset-capability-audit.md), and [video migration record](../assets/docs/murderbird-video-migration-2026-09-08.md) preserve the broader status and history. Older clips remain legacy material; the samples above do not alter their acceptance labels.

## Current rig and motion limits

The inspected current assets are `assets/models/uncaged-shield-study/murderbird-shield-study.glb` (SHA-256 `d65dc8dcd642a1a60a642678118b2abb063db92000d74015fd8cc8ce6f279fbc`) and `src/scene/exhibit.js` (SHA-256 `8dc1ec022699604806208fcf521ddb4511b2266552c6a14126b06a14b122d792`). A read-only parse of the GLB header/JSON reports **0 glTF animation clips and 0 skins**. This is a rigid object hierarchy, not a skeletal rig.

The app resets named object transforms each frame and scripts exhibit response rotations for `neck`, `head`, `jaw`, `left-mantle`, `left-wing-shield`, `right-mantle`, and `right-wing-shield`, plus a bounded rigid neck slide during extension. The source does not drive `body`, pelvis, thighs, shins, ankles, or toes. The current behavior therefore supports an authored neck/head/jaw and shoulder/elbow contact gesture, not full-body locomotion, autonomous attention motion, gait, weight transfer, or a talon strike. The loose contact sequence should be treated as a fixed upper-body interaction until a supported whole-body action is implemented and reviewed.

## Capture limits

The selected candidate and July reference were visually opened from hydrated primary-mirror files because the corresponding worktree entries are LFS pointer stubs. The render and model hashes above identify this worktree baseline. Frames were locally derived from three hydrated primary-mirror MP4s; `ffprobe` reported 8 seconds each at 24 fps, with AAC only on the two legacy clips. Frame PNGs under `assets/audit/stage-two-baseline/` are review derivatives, not production source media. No model, application, source media, or existing catalog was changed for this audit. Owner review and acceptance of the current model or any proposed changes remain outstanding.

## Live local and public baseline

Before runtime edits, the primary architect loaded the actual shield-study scene at `http://127.0.0.1:5174/` for a seven-second no-input sample. State remained `idle`; root travel and leg articulation were absent in the inspected implementation. The measured renderer was SwiftShader software, about **9.20 fps** at 1440×1080. This is a short baseline sample, not the Stage Two 60-second acceptance test. [Browser receipt](../assets/audit/stage-two-baseline/browser.json), [capture](../assets/audit/stage-two-baseline/current-static.png).

The prior interaction used an explicit button or armed tap; ordinary orbit, zoom and UI selection did not request an attack. It had orbit/zoom/keyboard controls, era switches, separate breast/cranial inspection and exploded groups, illustrated fallback and optional audio. Contact was a constrained head-bound cervical slide at a fixed central front bar, without locomotion or simulated forces.

Read-only GitHub API checks found a successful Pages deployment at **`0d4032907ce55f328de10ba4978a5025988606ee`**, run **36293468814**, and the public page returned HTTP 200 with `index-B3rZHVyx.js`. The current local starting point is **`4ba4a46`**, containing later shield-study work absent from that deployed revision. These are separate builds; Stage Two is local only. [Deployment status](../assets/audit/stage-two-baseline/deployment-status.json), [public HTML resource receipt](../assets/audit/stage-two-baseline/public-page.json). No remote write or publication was performed.

| Gap | Confirmed baseline and implication |
|---|---|
| Likeness | Oversized round trunk, simplified bill/crown and wide feet relative to selected images; needs visual correction independent of engine choice. |
| Locomotion | Leg meshes batched into fixed body, no root travel or stepping rig. |
| Idle performance | State remains idle without input; no autonomous repertoire. |
| Predatory attention | Small head rotation from input, with a fixed central contact action. |
| Attack/recovery | Short upper-body timeline returns to rest; no foot bracing or loaded pelvis. |
| Mechanical credibility | Rigid named objects suit armor, but lack leg pivots, planted constraints and connected hip motion. |
| Integration | Existing era, inspection, fallback and sound paths are usable and must survive the motion revision. |
