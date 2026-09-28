# Browser evidence

Actual local WebGL captures of V13 attempt 01. The head comparison page contains native renders, clearly labeled; it is not itself a motion capture.

- `head-comparison.png`: matched native before/after images displayed in the browser.
- `whole-body-webgl.png` / `.json`: actual V13 GLB viewer, neutral rest, reference-angle camera.
- `fixed-native-fallback.png`: explicit fixed native-render mode, then returned to actual 3D.
- `maker-jaw-control.png`: external control UI at 100%, not a model-pose image.
- `maker-jaw-open-model.png`: first frontal three-quarter jaw inspection.
- `controls-after-orbit.png`: intermediate controls view, not model evidence.
- `maker-jaw-open-reference-side.png`: actual Maker full-open jaw from the side.
- `maker-jaw-rest-reference-side.png`: same camera after Release all levers.
- `maker-jaw-open.json` / `maker-jaw-rest.json`: browser controller, model URL, motion and renderer snapshots. The first records the earlier head camera, before four ordinary left-orbit actions; the rest snapshot records the side camera.

Camera and lighting review API were used to select a neutral head close-up; ordinary UI supplied era, lever, orbit, release and fallback interactions. Exhibit lighting, default camera and part labels were restored afterwards. Mechanism rod placement is inherited and not accepted by these captures.
