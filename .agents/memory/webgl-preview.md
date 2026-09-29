---
name: WebGL preview limitation
description: Why the exhibit needs both a real 3D view and a non-WebGL preview path
---

The automated Replit screenshot browser failed to create a WebGL context in this project, while local headless Chromium with ANGLE/SwiftShader rendered the current 3D exhibit. Useful flags were `--use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader`.

**Why:** A blank 3D panel in a screenshot is not necessarily a broken Three.js scene; the preview environment itself may lack WebGL. Software rendering confirms scene loading and visible output, but says nothing about hardware-GPU performance.

**How to apply:** Check both the illustrated fallback in the Replit screenshot and the 3D path in a WebGL-capable browser before concluding a rendering change is correct or broken. If the managed screenshot browser cannot create WebGL, try a local Chromium session with ANGLE/SwiftShader and label it as a software-render check. Keep a visible fallback for visitors without WebGL.