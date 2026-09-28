# MurderBird exhibit direction

This is working guidance for the Vite/Three.js exhibit. It records visual and
media boundaries; it is not artistic acceptance, a blanket license, or
authorization for an unrelated future release. The current assessment
publication authorization is recorded in
[the publication review](publication-review-2026-09-27.md).

## Authority and scope

- The story and `docs/murderbird-unified-direction.md` govern the fictional
  timeline and cross-era appearance. The story is fiction, not a claim about
  real archaeology, biology, or engineering.
- The unified production brief sets **2.0 m floor-to-crown in a neutral upright
  pose as a production target**, not as a published measurement. Do not put
  that number into exhibit labels as established fact.
- Replit is the development preview. GitHub Pages is the configured production
  destination. Do not use Replit Publish or treat a successful local build as
  public-release approval.
- The root interactive viewer loads the exterior-v1 combined GLB through
  `src/scene/presence-exhibit.js` and adds runtime Three.js behavior. This is an
  implemented review study, not accepted final art, validated engineering, or
  a finished rig. The older procedural scene in `src/scene/exhibit.js` is used
  by the folio path, not as the root model. Distinct still images do not combine
  into a rig.

## Shared visual canon

- MurderBird is a formidable, floor-standing, flightless robotic terrorbird:
  deep hooked bill, swept segmented crown, compact strong neck, modern circular
  optic, load-bearing legs and talons, and compact folded ornamental wings.
  Avoid cute/toy proportions, perched or casing-supported poses, broad flying
  wings, and small crow-like silhouettes.
- The inherited anatomical **left shoulder** was fitted twice and has limited
  travel. Do not mirror that repair history to the other shoulder.
- Ancient construction uses hand-worked bronze, irregular hammer marks, and
  peened pins. The Water stage is inert, with a dark eye and restrained
  sediment/mineral deposits. Mechanic-era iron braces, brass bearings, and
  external/wound power remain visibly distinct from later systems.
- Modern energy and processing are separate additions. Do not show a glowing
  chest reactor. The Heart still is a power inspection, not a completed mind.
  Keep the modern amber optic out of Water and Mechanic imagery.
- Floor or a credible assembly cradle carries the body. A workbench and CRT
  can establish scale but do not bear the Bird's weight.
- Preserve the story's uncertainty about the ancient mechanism. Do not claim a
  full fossil reconstruction, certified hidden anatomy, or proven modern
  intelligence.

## Stills and delivery relationships

The selected stills have feature-specific visual scopes and may appear in the
owner-authorized public assessment/review package. This does not approve final
art or model likeness, expand an asset's permitted use, or grant a blanket
license. Keep source masters and provenance intact; browser imports use the
existing WebP derivatives.

| Story use | Source master | Browser delivery | Limits |
|---|---|---|---|
| Common silhouette / hero | `assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png` | `assets/img/webp/murderbird-unified-master-03-2026-09-06-{480,960,1536}.webp` | Head, silhouette, compact folded-wing/rear contour, modern materials, and floor staging only; not a rig or exact height. |
| Maker | `assets/img/library/murderbird-unified-maker-clean-candidate-2026-09-06.png` | `assets/img/webp/murderbird-unified-maker-clean-2026-09-06-{480,960,1536}.webp` | Quiet inspection, intact lowered hammer; not hammer breaking or exact attire. |
| Water | `assets/img/library/murderbird-unified-water-candidate-2026-09-06.png` | `assets/img/webp/murderbird-unified-water-2026-09-06-{480,960,1536}.webp` | Inert submerged body and mineral history; no exact chemistry or hidden-mechanism claim. |
| Mechanic | `assets/img/library/murderbird-unified-mechanic-candidate-2026-09-06.png` | `assets/img/webp/murderbird-unified-mechanic-2026-09-06-{480,960,1536}.webp` | Industrial repair around old bronze and floor supports; not autonomous awakening. |
| Heart / power | `assets/img/library/murderbird-unified-heart-candidate-2026-09-06.png` | `assets/img/webp/murderbird-unified-heart-2026-09-06-{480,960,1536}.webp` | Power inspection only; not a completed mind. |
| Sentinel | `assets/img/library/murderbird-unified-sentinel-candidate-2026-09-06.png` | `assets/img/webp/murderbird-unified-sentinel-2026-09-06-{480,960,1536}.webp` | Floor-standing beside CRT; do not invent an unpictured talon gesture or screen text. |

`assets/img/og/murderbird-story-share-2026-09-06.png` is an existing
1200×630 story social derivative; its "heart and mind of its own" copy is not
used in this exhibit because it implies a completed mind. `public/og-image.png`
is a text-free, 1200×630 contain composite of the existing 1536px
common-silhouette WebP on the exhibit's dark background. `public/social-preview.png`
is a 1024×1024 center crop of that same source. These existing browser copies
may be included in the authorized assessment delivery as review/metadata
derivatives; their publication does not make the underlying stills final art
or expand their feature-specific scope.
Legacy caged-bird art and old square brand artwork are not current character
references; existing favicon/app-icon files remain unchanged pending an
approved replacement mark.

Held Maker/master candidates, opening-frame candidate, legacy video studies,
production sessions, stems, guides, and `.local/` archives are not to be
promoted into browser delivery by filename or technical playability alone.

## Runtime model and story mapping

The fictional source of truth is `content/story/index.main.html`. The three
interactive layer choices are narrative eras, not a claim that each repair is
historically or mechanically verified:

| Exhibit layer | Story anchor | Exhibit distinction |
|---|---|---|
| I / Maker | `#the-maker` | Hand-worked bronze, irregular marks, peened pins, hooked bill, and the asymmetric twice-fitted left shoulder. The initial mechanism and the incomplete fossil fragments remain uncertain and separate. |
| Water interlude | `#the-water` | A narrative and still-image interval only. Water is not a selectable powered scene; the body remains inert and dark-eyed. |
| II / Mechanic | `#the-mechanic` | Later iron braces, brass bearings, and externally borrowed power over the older body. |
| III / Builder | `#the-builder` | The story describes finite energy and a later learning mind as separate systems. The Advanced exhibit instead uses effectively inexhaustible fictional encounter power, kept separate from processing; inspection links the chest to `#the-heart` and the head to `#the-mind`. |

The five anatomy/story selections are anchored to the narrative: hooked beak
and left shoulder to `#the-maker`, ankle/load response to `#first-choice`,
finite energy to `#the-heart`, and adaptive processing to `#the-mind`. Their
origin, repair, constraint, and excerpt are shown beside the preview. The left
shoulder history is not mirrored. The finite-energy excerpt is a story fact;
it does not override the Advanced exhibit's later, effectively inexhaustible
encounter-supply direction. Selecting an era changes its described material
layer and story passage; it does not turn the Water interlude into a machine
animation.

The root Three.js viewer uses the floor-supported exterior-v1 combined GLB,
with runtime motion, inspection, and mechanisms. It is the current three-era
review study, not owner-accepted likeness, measured anatomy, validated
engineering, or a finished rig. The proportions and hidden construction remain
reconstruction choices. The separate procedural scene at
`src/scene/exhibit.js` belongs to the folio path and is not the root model.
The root no-WebGL path presents scoped existing story imagery as a fixed
illustrated fallback; it does not advertise that illustration as an orbitable
model.

The score sheet labels bar 53 as `1:60.00`; the visitor view uses the bar
number, not that irregular timestamp. Its stated final vocal release
(2:04.04) and final band hit (2:04.62) are retained.

## Source-to-exhibit media provenance

| Exhibit use | Source and evidence | Delivered form | Scope and limit |
|---|---|---|---|
| Shared silhouette / hero | `assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png`; SHA-256 `538c51bcdbf5bfce95a0932fdbbb0f5868b446f4985346d15e6cacd32430e633` | Existing responsive WebP derivatives listed above; reference in `src/media.js` | Scoped common-body visual reference, also present in the authorized assessment/review package. It does not certify the current model, exact anatomy, or 2.0 m target. |
| Narrative and part excerpts | `content/story/index.main.html` and the anchors in the table above | Curated excerpts and linked passages in the folio | Fictional source text; not archaeological or engineering evidence. |
| Controlled motion pilot | `assets/video/murderbird-first-choice-635f0e15.mp4`; SHA-256 `635f0e1552bac61699c03c8406157207f6230ea817bb1ecaeb3adbb3a7bf8613`; H.264, 1280×720, 8 seconds, silent | Native visitor-started video control and poster; the exact poster/video pair is included in the authorized assessment folio | The exact story-page use and assessment-folio inclusion are scoped approvals. They do not approve final art, another pilot, a 3D rig, a longer film, or a blanket license. No Firefly generation was used. |
| Iron Verdict / original | `assets/murderbird/production/audio/iron-verdict/murderbird-iron-verdict.mp3`; SHA-256 `426b0158eb9d6e0e5866183f27d346e546ea0218f4d47a4f5fc1342549c1ff31`; 129.88 seconds, stereo MP3, 44.1 kHz | Original programmed instrumental in its own visitor-started player | This historical demo has no vocal track. It is distinct from the GarageBand interpretation and the accepted synthesized sung v3 release. |
| Iron Verdict / GarageBand interpretation | Source: `assets/murderbird/production/audio/iron-verdict/murderbird-iron-verdict-garageband-preview.wav`; SHA-256 `e783fb4122e422445737297a47d9a8f0ae23ce7c193fd3ff48e8dc8d0b3dedf4`; 136.64 seconds, stereo 24-bit PCM WAV | Visitor-started historical comparison derivative: `assets/audio/murderbird-iron-verdict-garageband-preview-192k.mp3`; 192 kb/s, 136.67 seconds, 3,281,170 bytes; SHA-256 `b0ef516d6a963b8766a6490bbe5ad6ac0e76d54d428b4b53beb88f720a918860` | Separate native-instrument performance. Its current inclusion is limited to the authorized assessment/review package; that does not grant broader rights or a general music release. The `.band` session and stems are not imported. |
| Iron Verdict v3 / accepted sung release | Owner-accepted release and scoped publication are recorded in [the audio brief](audio-brief.md#accepted-theme-song) and [release provenance](../provenance/iron-verdict-v3-release.json). | Separate visitor-started synthesized sung performance; see the audio brief for exact delivered files and checks. | This is distinct from both historical instrumental versions. No human-vocalist recording is claimed; do not infer broader rights from assessment publication. |
| Vocal text and performance context | `assets/murderbird/production/audio/iron-verdict/vocal-score-v2/performance-sheet.md` | Complete lyrics and stage directions in `src/vocal-score.js` | Score only: 104 BPM, 4/4, D minor, 56 bars, sounding D3–F4; 233 words and 279 syllables. The two historical demos do not contain these vocals. The separately accepted v3 is synthesized; no human vocalist recording is claimed. Synthetic pitch guides and rehearsal mixes remain excluded. |

## Motion, music, and visitor control

- `assets/video/murderbird-first-choice-635f0e15.mp4` is the reviewed,
  owner-approved controlled pilot for the story page. It is an 8-second,
  silent H.264 2D motion study, not a 3D mechanism reconstruction, completed
  film, or approval of other clips. Use native controls, `playsinline`,
  `preload="none"`, a poster, and an adjacent visual description. Do not add
  dialogue or sound captions; it has no audio track.
- The original instrumental, GarageBand interpretation, and accepted
  synthesized sung v3 release are separate visitor-started assets with
  separate labels. The two historical demos are included only within the
  documented assessment/review scope; this does not grant broader rights. Do
  not load the `.band` session, stems, pitch guide, or rehearsal mix into the
  exhibit.
- Neither audio nor video autoplays. Starting a track or the silent pilot
  pauses competing players and the procedural soundscape. Keep the complete
  score and performance details separate from the historical demos; identify
  the accepted v3 as synthesized and do not imply a human vocalist or broader
  rights clearance from technical validation.

## Review checklist

- The Three.js view shows the grounded, formidable silhouette and limited
  response; the no-WebGL fallback shows scoped story stills, not a blank panel.
- Every still remains in its scoped era and retains the limits above in its
  accessible description or nearby caption.
- Era and five-part selections preserve their narrative anchors and the
  Maker's asymmetric left-shoulder history.
- Video and each distinct music release require visitor action and use native
  controls; only one player or soundscape is audible at a time. The silent
  pilot has a visible visual description; the original and GarageBand demos
  are labeled as instrumental, and the accepted v3 as a synthesized sung
  performance.
- Keep score metrics and performance provenance explicit, and do not describe
  the historical instrumental files as the accepted sung v3 release.
- Verify a production build and responsive preview before handoff. A successful
  build is not release approval; any release beyond the currently authorized
  assessment package needs its own asset and deployment review.