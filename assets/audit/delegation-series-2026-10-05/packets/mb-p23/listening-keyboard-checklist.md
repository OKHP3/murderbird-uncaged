# MB-P23 listening and keyboard checklist

**Status: source reviewed; actual listening and browser/keyboard operation NOT RUN.** The checks below are pending observations, not failures. Run them on the actual exhibit route with sound enabled and record browser, OS, route/revision, date, selected version, and observed result before marking any item complete.

## Human listening

- [ ] Start **Full song** with Play; confirm audible output begins after the user gesture and listen through the full 147.75-second track. Record cutouts, distortion, unexpected silence, or completion message. **NOT RUN.**
- [ ] Start **Seamless loop**; listen through the end/start boundary and at least three consecutive cycles. Record any click, gap, level jump, or content mismatch. **NOT RUN.** The release record reports three repeated cycles checked, but this task has not independently listened.
- [ ] Adjust Volume low / mid / high while playing; confirm audible level changes smoothly. Mute and unmute; confirm mute silences and restores output at the slider setting. **NOT RUN.**
- [ ] Pause and resume; confirm the selected track resumes at its prior position. Restart; confirm it returns to the beginning. **NOT RUN.**

## Keyboard and readable lyrics

- [ ] Tab to the player; verify visible focus and logical order through Play, Restart, Version, Mute, Volume, then Read the lyrics. **NOT RUN.**
- [ ] Activate Play/Pause and Restart with Enter/Space; change Version with arrow keys; adjust Volume with arrow keys/Home/End; toggle Mute from the keyboard. Confirm status and pressed states remain understandable. **NOT RUN.**
- [ ] Open **Read the lyrics** using the keyboard. Confirm the complete lyrics appear as readable text, with sensible browser navigation/back behavior. **NOT RUN.** The linked UTF-8 text file was read directly from the checkout; browser access was not tested.
- [ ] At a throttled/failed request or supported test route, start loading and cancel; confirm loading stops and retry is available. Simulate failed fetch/decode if a safe existing route permits; confirm useful status and retry. Do not break production assets to create a failure. **NOT RUN.**
- [ ] Repeat with screen reader/status announcements if available; confirm labels and status updates are announced. **NOT RUN.**

## Closure boundary

The owner-accepted `production-v3` release is a synthesized sung performance, not a claim of a human vocalist recording. Keep historical GarageBand/instrumental work and optional soundscape records distinct. Hash parity confirms the three approved runtime files match their release ledger; it does not prove playback, loop audibility, keyboard operation, or deployment delivery.
