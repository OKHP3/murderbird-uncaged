# MB-P17 — Current exhibit controls and identity

**Outcome:** COMPLETE for source inventory, focused state tests, and diagnostic procedure. Base SHA `4984f39bdca13e87ead9b446b1d033dc0f2898ee` verified.

## Confirmed source capabilities

The V37 entrypoint is `src/main.js`; its UI calls the third era “Advanced” while controller/model state uses `builder`. Maker exposes five outside articulation sliders. Mechanic exposes engage, stop-after-cycle, wind, and charge status. Advanced exposes visitor position/reach/retreat, tap-to-reach, power jump, shield thrust, and claw scrape. The renderer source provides orbit/zoom, reset/focus, enclosure, and inspection/separation/reassembly paths. The fallback adapter provides fixed era stills, textual descriptions and an explicitly illustrative assembly diagram; it does not implement camera orbit/zoom/focus.

## Checks and limits

The three existing state suites passed: 36/36 (`era-controller`, `presence-state`, `encounter-state`). These establish tested state logic, not visible rendering. `diagnostic-steps.md` specifies desktop WebGL, forced fallback, identity-reference scoping, and separate mobile observation. Those browser/device steps remain NOT RUN. No source or runtime files changed. No PRD score or artistic acceptance is asserted; current goal still records likeness UNMET and owner acceptance PENDING.

**Next action:** when a visible check is authorized and a browser/device is available, run the recorded procedure against a named exact V37 revision; keep local test evidence separate from rendered and human observations.
