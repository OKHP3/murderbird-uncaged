# Three Eras technical study — desktop verification, 24 November 2026

The corrected First Choice study passed the full-resolution texture upload, rollback and retry tests on Intel Arc and Apple M4 Max GPUs. The release decision on 27 November kept v1.1 final and parked cinematic likeness. The shared exterior was accepted for era development. Final likeness across the three eras remains unmet.

| Tested object | Identity |
| --- | --- |
| Offline standalone HTML, before and after Windows tests | 47,367,367 bytes, SHA-256 `ff21d980020c4654ced6e1617df1076e63eb599e99b9af1e6461643db6ad23e9` |
| Reassembled full model in the browser | SHA-256 `20632ff6116f93827bc814d53301749dec1ef035165749db2d819bb89edcd41c` |
| Separate local HTTP rehearsal | 34 files, 66,981,042 bytes, script SHA-256 `69e9632fa2fbf7a86d91b270ac393a25163839e20eecd23da7511c1fa92070e4` |

## Windows GPU and offline playback

Stock Chrome 158.0.8127.37 and Edge 158.0.4370.33 ran the standalone from disk with the network offline. Both used Intel Arc through ANGLE Direct3D 11, driver 32.0.101.8237. The earlier study displayed full detail even though the GPU rejected 27 attempts to upload a 768 × 768 image to a 192 × 192 allocation. The corrected build allocates storage for the larger image before promotion.

| Per-browser measurement | Chrome | Edge |
| --- | ---: | ---: |
| Full-size uploads with matching storage on normal promotion | 57/57 | 57/57 |
| Matching uploads before deliberate rejection of the final commit | 57/57 | 57/57 |
| Matching uploads after Retry full surfaces | 54/54 | 54/54 |
| Live full textures with RGB data beyond pixel 192 after promotion | 30/30 | 30/30 |
| Live full textures with RGB data beyond pixel 192 after retry | 30/30 | 30/30 |
| Preview texture sample sets preserved after rejection | 28/28 | 28/28 |
| Native WebGL errors or overflow warnings in these tests | 0 | 0 |
| Offline interaction checks passed | 11/11 | 11/11 |

**Reproducing the texture observations.** Verify the standalone digest. Instrument texture storage and upload calls separately. For each live full texture, attach mip level zero to a framebuffer and check completeness. Read RGB at (221,229), (371,389), (515,575), (713,687), (249,599), (643,305), (553,411), (235,700) and (695,220). Each texture had a nonzero RGB component at one or more points. To test rollback, report a one-time `INVALID_OPERATION` to the application at its final commit check while the underlying GPU reports `NO_ERROR`. Compare preview samples and canvas PNG bytes before and after rejection. Both browsers retained the paused frame exactly. Click Retry full surfaces and repeat the readbacks.

**Reproducing the interaction checks.** Start with sound and pilot paused. Operate and release all five Maker levers, then inspect and close the head. Run the 5.2-second Mechanic cycle, pause, reverse, reset and inspect the breast. Play Advanced First Choice, orbit by keyboard and return to rest. Trigger WebGL context loss, check for the illustrated fallback and use Retry 3D. Both browsers recovered full detail with the timeline at zero and foley muted.

During Advanced contact foley, switching on reduced motion stopped three active oscillators in each browser. The timeline held for 650 ms at 4.109 seconds in Chrome and 4.101 seconds in Edge. At 48 kHz the next 44 measured PCM buffers were silent in each. Head and breast inspection still worked. Human listening remains untested.

## Mac GPU, performance of the rig and inspection

Chromium 156.0.8078.4 ran the standalone texture tests on an Apple M4 Max through ANGLE Metal. After both normal promotion and injected failure followed by retry, all 30 full textures had complete framebuffers, zero readback errors and nonzero RGB at one or more of three points beyond the preview boundary. A separate HTTP rehearsal on Chrome 158.0.8127.37 verified the full model digest, matched all 34 response bodies, and recorded zero external requests or browser errors.

- **Maker** stayed externally operated. Each lever moved visible geometry, and all five released to the original rendered pixels.
- **Mechanic** completed both bounded 5.2-second turns, preserved the world root and stopped at the ends. The paused trial recorded zero clock drift.
- **Advanced** accepted left, center and right inputs using pointer, emulated touch and keyboard. Two unprompted 120-second trials recorded distinct sequences, each with four rail contacts. The phase-interruption tests exercised orient, commit, contact and cooldown five times each.
- **First Choice and clearance.** Across 253 frames all 32 tracked group transforms matched the original opening. The rig sweep covered 4,057 sampled poses. The tested solid pairs recorded zero transverse crossings. Twelve panel pairs across 612 sampled positions had a minimum continuous gap of 0.012166 model units. These measurements apply to the tested geometry and motions.
- **Inspection.** Sixteen region selections across three eras gave 48 combinations. Fifteen opening samples and five reassemblies per combination covered 720 opening states and 240 returns.

## Requirement accounting

The study evaluated 52 criteria in 122 applicable era or global cells. Numeric reviews cover 104 cells. The weighted lower bound was 60.99 points out of 100 and the weighted coverage of numeric reviews was 85.76%. The CSV retains each score and disposition. An empty score means the review recorded a nonnumeric result. [All 122 scored and unscored cells](three-eras--requirement-scores-2026-11-24.csv)

| Nonnumeric disposition | Cells | Evidence or remaining work |
| --- | ---: | --- |
| Owner decision | 3 | V01, final recognition in each era |
| Withheld | 3 | V03, dedicated closed/open Mechanic jaw excursion. V12, approved continuous historical motion for Maker and Mechanic |
| Human study | 3 | I06, first-time visitors performing each reversible journey |
| Human or device | 3 | A02, assistive-technology and real-device use |
| Device evidence | 3 | A06, physical iPhone Safari and sustained device performance |
| Global delivery / custody / presentation | 3 | D01, study delivery verified. D02, wider archive custody partial. D04, installed and external presentation partial |

Ten historical findings were reviewed. F01–F06 retain art work on body silhouette, bill and optic, mantle, feet, plate hierarchy and era-specific material history. F03 and F04 also record repaired clearance and contact in the tested motions. F07 claw action and F08 sustained waiting were observed. F09 retains a partial access finding. F10 verifies the study build while wider custody remains open. The narrower feet, exposed optic and smoother shoulder mantle still differ from the visual references.

Of 18 procedures, 12 were observed (T01, T03–T09, T11, T12, T14, T15). Five remained partial (T02 identity, T13 access, T16 performance, T17 delivery and T18 presentation). T10, Advanced jump and thrust, remained a later gated item. The evaluation assigned zero to the corresponding B09 capability. Native Safari on this exact build, physical iPhone use, human listening and first-time visitor behavior remain unverified.
