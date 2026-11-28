# Three Eras standalone Windows replay

The November 24, 2026 Windows replay passed on one Intel Arc device using the installed Chrome 158.0.8127.37 and Edge 158.0.4370.33 with hardware WebGL 2 via ANGLE/Direct3D 11. Both browsers ran the same standalone from disk in offline, sandboxed browser contexts.

## Artifact and custody

| Item | Verified identity |
| --- | --- |
| Tested standalone | `MurderBird-Three-Eras.html`, 47,367,367 bytes, SHA-256 `ff21d980020c4654ced6e1617df1076e63eb599e99b9af1e6461643db6ad23e9` |
| Full decoded model in the standalone | 55,884,688 bytes, SHA-256 `20632ff6116f93827bc814d53301749dec1ef035165749db2d819bb89edcd41c` |
| Preview decoded model in the standalone | 46,141,044 bytes, SHA-256 `2f9ff345f3a06732367d5c1dd2d2703b924bc3061b25d7a040bf24b9b597ba54` |
| Windows evidence receipt used here | 15,094 bytes, SHA-256 `7738c7814581a935c37b1197777c0263f493eaaf033b5767712d3b53e84bf997`. The transferred copy matched on readback. |
| Final compact delivery kit | 44,466,650 bytes, SHA-256 `2066487052fcf23c48f7243bbcaffca1999fd104541e0f6d6fa3084dda643601`. All 223 manifest entries matched. The top-level HTML and `Evidence/closeout/release/ff21d980020c4654/MurderBird-Three-Eras-Windows-QA.md` matched the tested artifact and original QA receipt byte for byte. |
| Standalone source provenance | The kit records authoring commit `ed949e3892042f2f736f77f52c6f1dcc7bffd231` for `atelier/three-eras` and hosted build source commit `0af388142552113aacd4568809b2ac2d9257abe4`. The kit includes matching source and hashes, with Git commit objects outside the compact package and outside the inspected public tree. The browser tests here used the standalone SHA above. The separately identified hosted script has SHA-256 `69e9632fa2fbf7a86d91b270ac393a25163839e20eecd23da7511c1fa92070e4`. |
| Main inspected for this record | [`ac1570aba21092e88f0f8930c21587b7a0695499`](https://github.com/OKHP3/murderbird-uncaged/commit/ac1570aba21092e88f0f8930c21587b7a0695499) |

The earlier compact archive, SHA-256 `0770f03653a71056b89c1c021ba9a8336d437a4047b39479b127568fff7111a8`, contained an earlier 47,367,632-byte standalone, SHA-256 `fcdb653b78f939a848bf7e35361f2982cddaf9aa567fab9d07325e55e07feb09`. That Windows run exposed 27 overflow errors when 768×768 uploads targeted 192×192 allocations. The passing numbers below belong to the corrected artifact.

The November 27 First Choice closeout on main documents the earlier Advanced study in `atelier/`. Its tracked standalone is `atelier/runtime/.qa/First-Choice-portable.html` (63,123,668-byte Git blob, SHA-256 `da9597ad22b8a72590510885c5814e407da208e6f29fa47490141a33f2b2fc05`). The repository comparison found no exact Three Eras replay receipt or runner at the inspected main revision. See the [First Choice study closeout](handoffs--first-choice-thread-closeout-2026-11-27.md).

## Observed Windows results

| Check | Chrome | Edge |
| --- | ---: | ---: |
| Offline runtime interaction checks | 11/11 | 11/11 |
| Normal 768×768 uploads matched the destination allocation | 57/57 | 57/57 |
| Uploads matched during the attempt with a simulated final-commit rejection | 57/57 | 57/57 |
| Uploads matched after Retry full surfaces | 54/54 | 54/54 |
| Full textures with complete framebuffer and nonzero RGB beyond coordinate 192, normal and retry | 30/30 each | 30/30 each |
| Native WebGL errors and texture overflow warnings during texture verification | 0 | 0 |
| Preview texture sample sets that matched across rollback | 28/28 | 28/28 |
| Canvas PNG bytes matched across rollback | yes | yes |

The test read nine 1×1 RGBA samples per full texture at mip 0. The probe returned a single synthetic `INVALID_OPERATION` at the final commit check while the underlying native call returned `NO_ERROR`. The preview stayed at rest and Retry full surfaces restored the full tier. A separate runtime check induced context loss through `WEBGL_lose_context`, then verified the illustrated fallback and Retry 3D recovery.

Startup held the illustrated view with no AudioContext, foley muted, and music and pilot paused. The five Maker controls, the Mechanic wind/pause/reverse/reset cycle, Advanced First Choice keyboard orbit and return to rest, and era-specific regional inspection all passed. Enabling reduced motion during the Advanced autonomous encounter froze time at 4.109 s in Chrome and 4.101 s in Edge for the 650 ms observation window. Per browser, the test measured active contact foley before the change, cut three oscillators early, then measured 44 consecutive zero-PCM buffers. Head and breast inspection stayed usable. The evidence is browser-measured PCM, with human listening outside the test.

These results cover the recorded artifact on the recorded Windows device and browsers. The test sampled GPU content and did not score likeness, sound quality, or creative acceptance. Project release status is recorded in [goal.md](../goal.md).

## Reproduce the replay

Use Node 24 or later, locally available Playwright, and installed Chrome and Edge with a visible desktop and hardware WebGL. The exact historical standalone is [available in this repository](../atelier/three-eras/three-eras-offline.html?raw=1). The [runner](../scripts/verify-three-era-windows-replay.mjs) checks bytes and SHA-256 before and after the replay, launches the browsers sequentially, and writes a numeric result to stdout. No dependency or build change is required on the exhibit. If Playwright is installed outside the repository, make its `node_modules` available through `NODE_PATH`.

```sh
node scripts/verify-three-era-windows-replay.mjs atelier/three-eras/three-eras-offline.html
```

Add `chrome` or `msedge` as the second argument to select a single installed browser. The runner calculates canvas-byte equality in memory. It stores no images or recorded audio. The report and runner are evidence for the historical standalone replay and have no role in the v1.1 publication pipeline.

On November 27, the portable runner rejected a deliberately wrong input and passed on the same hardware with Chrome 158.0.8127.37 and Edge 158.0.4370.45. Both reruns passed all 11 runtime checks and repeated the allocation, framebuffer and rollback counts above.
