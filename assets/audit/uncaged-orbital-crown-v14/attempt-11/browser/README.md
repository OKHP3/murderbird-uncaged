# Attempt 11 browser review

Local development review only. The actual GLB is `assets/models/uncaged-orbital-crown-v14/attempt-11/murderbird-orbital-crown-v14.glb`, SHA-256 `181e31fe50afe7f01e912e9974e7fcdd5827f739ac007bcef64dc8f9909fdfd8`.

Main diagnostic: <http://127.0.0.1:5183/?review-body=v14-11&review-seed=927>. Gallery: <http://127.0.0.1:5183/assets/audit/uncaged-orbital-crown-v14/index.html>.

| Evidence | Scope |
|---|---|
| `head-comparison.png` | Gallery screenshot: matched native V13 and V14 head renders. These two comparison images are fixed renders, not browser WebGL. |
| `inspection-open.png` and `.json` | Actual exhibit WebGL, paused Advanced state, neutral review light and head camera, crown open. |
| `inspection-separated.png` and `.json` | Same diagnostic with the separation slider at its maximum. |
| `reassembled-paused-head.png` and `.json` | Actual WebGL after reassembly; recorded opening and separation are both zero. |
| `gallery-fixed-fallback.png` | Deliberately selected and labeled native fixed-render fallback. It is not evidence of successful WebGL. |
| `whole-body-webgl.png` and `.json` | Gallery's actual GLB viewer in its Advanced era filter. This static viewer does not include the exhibit's procedural motion and era mechanisms. |

The gallery was switched through Maker, Mechanic and Advanced, and from fixed fallback back to 3D. A fresh DOM image check found no incomplete or zero-width images. The main exhibit was restored after capture to its intended lighting, default view, visible part labels and running encounter.

The paused reassembled head window reported Apple M4 Max / ANGLE Metal, canvas 856 × 648, pixel ratio 1, frame-time median 10 ms and 95th percentile 10.9 ms; 225 draw calls, 556,126 triangles, 217 geometries and four GPU textures. These rolling metrics are not a sustained benchmark or acceptance on other devices.

Opening, separation and reassembly were visually inspected. Full Maker controls, Mechanic stepped turns and all Advanced power moves were not visually re-reviewed in this browser session. The separate 21-pose packet records transforms only. No full-motion clearance, physical simulation, artistic acceptance or deployment is established. The main application's illustrated fallback retains V9 and is identified as such in its diagnostic notice.
