# Browser regression checks for the three-era study

This suite opens the preserved three-era web build and the standalone HTML through their visitor controls. It records observations in `.results/` beside the scripts. The two application inputs are `../web/` and `../MurderBird-Three-Eras.html`. A checkout of the application can also be selected using `MB_QA_APP`. The root exhibit and its Pages build have separate tests.

## Run the suite

Use Node.js 24–26 and a desktop that can run the selected browsers. From `atelier/three-eras/qa/`, install the QA dependency with `npm ci`. Playwright is pinned in this directory's lockfile.

```sh
npx playwright install chromium firefox webkit
npm test
```

The complete run uses Chromium, Firefox, desktop WebKit, installed Microsoft Edge and installed Google Chrome. Playwright selects its installed bundled engines by default. Edge and Chrome use the `msedge` and `chrome` channels. An operator can select executables through `MB_QA_CHROMIUM_PATH`, `MB_QA_FIREFOX_PATH`, `MB_QA_WEBKIT_PATH`, `MB_QA_EDGE_PATH` and `MB_QA_CHROME_PATH`. Firefox and WebKit need Playwright-compatible builds. Use the custom path variables when reusing such installations. The harness enables Metal on macOS for Chromium-family tests and records the actual WebGL renderer.

`npm test` runs the seven suites, checks each fresh receipt against the recorded final viewer, verifies viewer and hosted script hashes before and after the run, and writes `.results/verified.json`. After running all component suites individually, `node verify.cjs --receipts-only` checks those existing receipts. Each server binds to an ephemeral IPv4 loopback port and serves only real files within the selected `web/` directory. The file-open viewer is measured with the browser context offline.

| Command | Workload |
| --- | --- |
| `npm run runtime` | Four engines run local hosted and offline cases. Chromium adds three local fast and three controlled slow measurements, a missing first draw, a single-click retry, and a detail-tier retry. Check the announced cutaway control, camera orbit and Home, era transport endpoints, reset matrices and the narrow viewport. Use `npm run runtime -- chromium` for a partial diagnostic. |
| `npm run failure` | Disable WebGL, lose the context during the model request, and lose it after first draw. Check the decoded poster and illustrated walkthrough in each case. |
| `npm run soak` | Run three cold/warm page pairs. Leave Maker idle for at least 60 seconds and inspect each opened era for at least 120 seconds, with camera moves ten seconds apart. Compare rest and reset matrices. |
| `npm run regions` | Exercise all 16 inspection choices in each era through five 0%, 50%, 100%, reset cycles. Check 720 sampled states, 240 restorations and 75 interruptions. Capture 48 region images. |
| `npm run capture` | Capture three rest and three open canvas images using the original 1152 × 900 viewport and JPEG quality 86. Record the active mode, camera, model and pixel-file hashes. |
| `npm run textures` | Instrument full-size WebGL2 uploads, attach the surviving textures to a read framebuffer, and check RGB samples at 257, 515 and 767. Repeat after injecting an allocation error and using Retry full surfaces. The assertions require matching 768 × 768 allocations and zero native errors. |
| `npm run motion` | Switch a running Advanced scene to reduced motion eight times. Alternate First Choice and enclosure. Observe motion state at 350 and 1,200 ms and require the timeline to remain stopped. |

The first-draw GLB has digest `2f9ff345f3a06732367d5c1dd2d2703b924bc3061b25d7a040bf24b9b597ba54`. The full reconstructed GLB has digest `20632ff6116f93827bc814d53301749dec1ef035165749db2d819bb89edcd41c`. GPU readback exercises texture acceptance in addition to the full-model digest. The independent Windows evidence covers PCM silence and rollback at the final texture commit. Desktop engine emulation measures desktop behavior. Human listening, screen-reader use, handheld performance and aesthetic approval require their own observations.

The browser cases retain the promotion suite's timings, camera steps, region matrix, dwell lengths, failure scenarios and screenshot settings. This directory exposes those checks as standalone QA commands. `verified.json` records a fresh run against the public-source candidate and contains SHA-256 digests for the detailed machine-generated receipts kept under `observations/`. Raw captures are regenerated inside `.results/` when running the tests.

The separate [panel clearance replay](panel-clearance/README.md) measures twelve digital mesh pairs through 612 opening samples and their continuous hinge sweeps.
