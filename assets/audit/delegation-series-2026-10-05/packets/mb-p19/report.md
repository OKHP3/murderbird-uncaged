# MB-P19 fallback and calm-state coverage

**Outcome:** Source/local coverage recorded; rendered browser failure checks remain NOT RUN.

Verified checkout base 4984f39bdca13e87ead9b446b1d033dc0f2898ee. Ran the existing recovery-lifecycle, presence-state and encounter-state Node test files together: **25 passed, 0 failed, 0 skipped**. The unit coverage includes fallback-image failure persistence/reload, presence recovery and interruption, calm-motion state transitions, and encounter cooldown/snapshot behavior.

Source review found model startup errors and WebGL context loss route into the illustrated fallback; retry calls the normal exhibit loader again. Fallback image errors hide the image and preserve an unavailable message. Reduced-motion is initialized from `prefers-reduced-motion`, updated on media-query changes, and user controlled. While the document is hidden, the main loop still schedules animation frames but skips presence/exhibit updates; browser suspension and return remain unverified.

The existing `scripts/verify-recovery-v4.mjs` defines bounded injected browser cases for repeated model failures, unavailable fallback artwork, audio 503 and retry, unavailable WebGL, and repeated context loss. `failure-injection-steps.md` records the exact follow-up checks and output boundary. They were not executed because this packet prohibits browser interaction. No rendered, mobile, physical-device, audio-device, human or deployment acceptance is inferred.

**Changed paths:** packet artifacts only. No application code or existing test files changed.
