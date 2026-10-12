# MB-P19 bounded browser failure steps

These are concrete steps already represented by current browser QA source. They were **not run** for this packet; no rendered result is claimed. Use loopback only, existing dependencies only, and save any QA receipt under the MB-P19 packet directory. Do not publish the fixture or target a remote host.

## Recovery verifier

1. Start the existing Vite dev preview on `127.0.0.1:5174`. In another terminal, confirm its page loads and the candidate is local.
2. Use the already-installed Playwright module path and run `scripts/verify-recovery-v4.mjs` against that loopback URL. Set `UNCAGED_RECOVERY_AUDIT` to `assets/audit/delegation-series-2026-10-05/packets/mb-p19/browser-evidence` so its receipt stays within this packet. Do not install Playwright if the module is unavailable.
3. Confirm the verifier records two failed model loads, a truthful illustrated label, retry visibility and disabled 3D-only controls; let the first retry fail again, then confirm the next retry restores WebGL and controls.
4. Confirm the forced Maker preview image failure is explained while part descriptions and inspection remain available; retry the image/3D and navigate to the story folio.
5. Confirm theme audio HTTP 503 returns the player to Play with an error/retry message, then allow the next request and confirm playback can start and stop.
6. Confirm unavailable WebGL produces the illustrated fallback and recovers after restoring context creation; then induce two `WEBGL_lose_context` cycles, checking each fallback label/control state and retry recovery.
7. Retain browser console/resource errors, forced-failure events, resulting renderer state, screenshots or video, and exact source SHA. Any timeout or unsupported context-loss extension is a failure/unknown for that check, not a pass.

## Calm and visibility state

1. In the rendered preview, use a browser context with `prefers-reduced-motion: reduce`; verify the calm-motion control begins checked and the presence state is stationary outside a currently grounding step. Toggle it during a moving step; confirm it settles, then verify reach does not advance to strike/contact.
2. Toggle the OS/browser preference while open and confirm both the control and state follow it. Repeat with the checkbox alone. Capture initial preference, state/phase and motion samples.
3. Start a normal moving encounter, switch the tab out of view for five seconds, then return. Record whether the encounter phase and pose resume without a jump; compare to the current source behavior that skips frame updates while `document.hidden`.
4. Repeat at a 390×844 touch viewport with reduced motion. Retain screenshot, viewport, browser version, console/errors and state samples. The existing `scripts/verify-presence-browser.mjs` has matching cases but writes to `assets/audit/uncaged-presence-review`; do not run it unchanged under this packet's output boundary.

**Current evidence:** only the three Node suites listed in `recovery-coverage.json` ran.
