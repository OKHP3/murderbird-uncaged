# Story media playback verification

**Checked:** 2026-09-27
**Scope:** Local development preview only. No publication, release, asset-rights, or approval-scope changes.

## Results

| Source | Visitor-started playback | Switching behavior |
| --- | --- | --- |
| First Choice silent pilot | Started from the native video controls with Space on desktop and touch in the phone-sized viewport. The 8-second H.264 MP4 contains a video stream only. | Starting either music track or the soundscape paused it. Starting the pilot again stopped the soundscape. |
| Iron Verdict original demo | Started with Space and touch; the MP3 loaded and its playback clock advanced. | Starting it paused the pilot. Starting GarageBand paused it. |
| GarageBand interpretation | Started with Space and touch; its separate MP3 loaded and its playback clock advanced. | Starting it paused the original demo. Starting the soundscape paused it. |
| Procedural soundscape | Started from its button with Space on desktop and touch in the phone-sized viewport. | Starting it paused active media. Starting the pilot again returned the button to OFF. |

No media began on initial page load: the video and audio elements were paused, had `preload="none"`, and did not have autoplay enabled; the soundscape button showed OFF.

The two music versions remain distinct in the interface and in delivery: the original is labeled as the custom-synthesis demo (about 2:09.9), while GarageBand is labeled as the separate instrument interpretation (about 2:16.7). They resolve to separate MP3 files.

## Browser and viewport

- **Desktop:** Headless Chromium 152.0.7977.64 on Linux, 1280 × 720 CSS pixels. Native media controls and the soundscape button responded to Space. Source changes paused the previously active source.
- **Phone-sized touch emulation:** The same Chromium build at 390 × 844 CSS pixels, 1× scale, with touch input enabled. The playback cards stacked in one column without horizontal overflow. Video, both audio players, and the soundscape button responded to touch; switching sources paused the previous one.
- The local Vite server returned the pilot and both MP3 assets successfully. The pilot is 8 seconds; the original and GarageBand files report durations of about 129.9 and 136.7 seconds.
- `npm run build` passed. Vite reported its existing large Three.js exhibit chunk warning.

## Limitations

This was a local, headless Linux browser check, not a visit from a physical phone. No iPhone/iOS Safari, Android device/browser, mobile data connection, physical speaker/headphone route, or human listening-quality check was available. Playback readiness and advancing media clocks were verified in Chromium; acoustic output and device-specific behavior remain unverified. The phone viewport is an emulation, not a claim of physical-device acceptance.