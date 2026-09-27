---
name: Mobile CDP testing
description: Avoid stale touch coordinates when automating phone-sized browser checks.
---

When driving a phone-emulated page with Chromium DevTools Protocol, touch events use viewport coordinates. This app enables smooth scrolling, so a normal `scrollIntoView()` can return before the viewport has settled and an immediate rectangle measurement can still be offscreen. Use `scrollIntoView({ block: "center", behavior: "instant" })`, then measure the control and dispatch touch at that viewport position.

**Why:** A touch test initially missed the native media control because it used coordinates captured before smooth scrolling finished.

**How to apply:** For automated phone-sized checks of native video/audio controls or page buttons, force an instant scroll before sampling `getBoundingClientRect()` and sending CDP touch input.