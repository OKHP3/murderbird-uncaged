# Visitor check — First Choice motion study

Run against an identified, exact browser route and revision. Test the canonical story page and the current exhibit Folio separately; the local story HTML is a source snapshot, not proof of the live page. Record browser/OS, route, revision, date, tester and observed result for every step. Do not report a source-only check as playback evidence.

## Before pressing Play

- [ ] Open the story's `#media-first-choice` section and the exhibit's `folio.html#motion-sound` section in a clean session. Confirm both surrounding stories render even if media is blocked.
- [ ] On load and after refresh, confirm no video, music, theme or soundscape starts by itself. Record any autoplay, network or consent prompt.
- [ ] Confirm the First Choice poster is visible before playback, loads without broken-image icon, preserves its intended ratio and is not blank. Confirm the visible caption identifies the eight-second motion study.
- [ ] Keyboard-tab to the player. Confirm focus is visible; screen reader announces a useful control name, Play/Pause state, timeline and volume/mute state. Specifically verify Folio gives the video a name: its source currently has a description but no explicit `aria-label`.
- [ ] Read the nearby description with a screen reader. It should explain the saddle/torso shift, slight head dip and fixed feet/stand/background. Ensure it is available without playing the clip.

## Playback and controls

- [ ] Start only by activating Play. Confirm inline playback on a narrow/mobile viewport where supported, without forced fullscreen unless the browser requires it.
- [ ] Listen through the entire clip at ordinary volume. Confirm it is actually silent. The source calls it silent but does not set `muted`; record whether the file contains/produces audio. If audio is present, log as a defect and stop claiming silent playback.
- [ ] Use native controls to pause, resume, seek to the middle, seek near the end, and return to the start. Confirm timeline updates, the selected frame appears, and duration is approximately eight seconds.
- [ ] Confirm the clip reaches its natural end, remains stopped, and can replay from the beginning. Ensure repeated Play/Pause and seeking do not freeze or reset the poster unexpectedly.
- [ ] While video is playing, start each other media control in Folio. Confirm the existing player pauses and the documented one-source-at-a-time behavior holds. Check that an existing theme/soundscape stops as intended.

## Failure and accessibility paths

- [ ] With media blocked/offline or the source request failed, confirm a useful failure state and working direct-source fallback link; report exact status/error. Check unsupported-video fallback text.
- [ ] Verify captions/transcript expectations: this clip is declared silent and has a visual description; do not invent dialogue/captions. Confirm no audio track contradicts that declaration.
- [ ] Check keyboard-only play/pause/seek/volume, high zoom, reduced motion preference, narrow layout, and screen-reader name/description. Record browser-specific native control limitations.
- [ ] Confirm poster and source URLs resolve on the exact host and path prefix. Absolute `/assets/...` references in the historical story snapshot require original site context; do not assume they resolve in a repository subpath preview.

## Evidence record

Attach exact route/revision, screenshots or recording where permitted, browser/device, outcomes per step, media request status, observed duration, audio-track result, seek result, accessible name/description and any defects. Live deployment, actual visitor playback, human acceptance and playback quality remain **UNKNOWN** until this checklist is executed.
