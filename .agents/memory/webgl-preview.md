---
name: WebGL preview limitation
description: Why the exhibit needs both a real 3D view and a non-WebGL preview path
---

The automated Replit screenshot browser failed to create a WebGL context in this project, while a separate Chromium session with software WebGL rendered the 3D exhibit.

**Why:** A blank 3D panel in a screenshot is not necessarily a broken Three.js scene; the preview environment itself may lack WebGL.

**How to apply:** Check both the illustrated fallback in the Replit screenshot and the 3D path in a WebGL-capable browser before concluding a rendering change is correct or broken. Keep a visible fallback for visitors without WebGL.