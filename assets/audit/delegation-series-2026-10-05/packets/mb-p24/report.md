# MB-P24 — Existing video and story controls

## Result

Source/provenance review of the existing First Choice video is complete at base `4984f39bdca13e87ead9b446b1d033dc0f2898ee`. The story source snapshot embeds the video in its First Choice passage; the current Folio player is separately rendered from `src/folio-main.js` using `src/media.js`. The source's claimed version is “Controlled Pilot 03 / 8 seconds / silent.” The canonical source page is `https://overkillhill.com/writings/murderbird/`; `content/story/README.md` says the local snapshots came from `OKHP3/overkill-hill@f1142a02f1e73cd45e46e981022aef27f1c6e095` and are not working app routes.

The MP4 at `assets/video/murderbird-first-choice-635f0e15.mp4` and preserved production binary `assets/murderbird/production/video/murderbird-first-choice-controlled-pilot-03.mp4` are both 824,339 bytes and hash to `635f0e1552bac61699c03c8406157207f6230ea817bb1ecaeb3adbb3a7bf8613`. The poster is 185,405 bytes with SHA-256 `897faf4814ba0ed59b95c1ae43558a34aa3e4154b49f9f4ba0d86942227144c6`. Both match `provenance/story-media-publication-2026-09-27.json`; the LFS alias and preserved-binary relation is recorded in `provenance/exterior-construction-v1-2026-09-27.json`.

## Findings and limits

- **Confirmed in story source:** native controls, `playsinline`, `preload="none"`, poster, explicit accessible name, visible caption and separately linked visual description. No `autoplay` attribute.
- **Confirmed in Folio source:** controls, `playsinline`, `preload="none"`, poster/description wiring, no autoplay attribute, and a play handler that pauses the other media and stops the soundscape. **Source gap:** Folio's video element has no explicit accessible name (`aria-label`/`title` or direct heading association), although it has a descriptive `aria-describedby`.
- **Declared, not independently verified:** both surfaces label the clip silent. Neither sets `muted`; the actual binary audio-stream inventory and audible playback were not verified. `ffprobe` was unavailable. Treat “silent” as source description until runtime listening/stream inspection confirms it.
- **Confirmed rights boundary:** the September provenance records owner-authorized assessment publication without finality upgrade. `NOTICE.md` keeps MurderBird creative material all rights reserved; the code MIT license grants no creative-content rights.
- **NOT RUN:** actual browser playback, seek, poster rendering, accessibility tree/screen-reader behavior, mobile behavior, live URL/deployment bytes, and failure handling. No browser was opened and no build was run.

The detailed executable steps are in [visitor-video-checklist.md](visitor-video-checklist.md). Source inspection establishes code and provenance facts only; it does not prove visitor playback or current publication.

## Next action

Run the checklist against exact current story and Folio routes, record their revisions, and address Folio's missing explicit video name if accessibility-tree testing confirms an unnamed player. Verify the actual audio stream and audible result before relying on the silent label. Preserve the all-rights-reserved boundary and do not infer artistic acceptance or a longer-video/3D scope from the existing pilot.
