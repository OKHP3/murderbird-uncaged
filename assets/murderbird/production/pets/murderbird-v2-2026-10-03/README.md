# MurderBird v2 ChatGPT pet

Created and selected on 2026-10-03 with the Pets create-pet workflow. Fresh service readback on 2026-10-06 confirmed the same custom pet remains active: `pet_6ac06533cd088191a400e56274adf1ff`.

The controlling likeness is the owner-supplied [Advanced guardian image](../../images/murderbird-v2-legal-guardian-square-1254-2026-09-08.png). The exhibit's V37 model was contextual reference, with owner likeness acceptance still pending. This compact generated pet does not establish acceptance of the cinematic model or completion of the repository's broader goal.

The final `spritesheet-extended.png` is a transparent 1536 × 2288 PNG with 73 used frames: nine standard animation states and sixteen gaze directions. SHA256: `e693eda0bbb73ee3f22de2e09df39c8562285598d84f8cafc48af6ff0f20ddb8`.

`source-workflow.zip` preserves generated source strips, references, prompts, extracted frames and the original manifest. Its historical pending labels are preserved; `imagegen-jobs.json`, the creation receipt and final QA reports record the resulting completion. The three independent `quality-and-previews-part-*.zip` archives preserve QA and final-derived motion previews. They are separate ZIPs, not binary pieces requiring concatenation. These archives were split to satisfy the Library's 10 MiB upload limit.

The [Library production page](https://chatgpt.com/space/page_322426f0ec908191b128f352c915fd25) holds the original uploads. The original request and reports retain historical local paths for provenance; they are not portable execution paths. `checksums.json` inventories the preserved files except itself.

## Validation and limits

The bundled create-pet atlas and quality validators were rerun against the imported final bytes on 2026-10-06. Both report `ok: true`; structural validation has no warnings. Quality warnings remain explicit: five subtle intermediate gaze directions, deliberate claw gaps at the feet, and a side-to-front head difference. The independent final motion review and blind direction validation passed before creation. Motion inspection does not claim live UI playback observation.

## Failure causes and corrected method

- A broad-wing jump forced excessive shared scaling. Regenerating a compact tucked-wing hop produced 19 pixels of lift and zero landing displacement.
- The second gaze row shrank when anchored to an already registered strip. Regenerating the complete row against the raw first gaze row restored body scale and baseline; final center drift is at most 1.5 pixels and width ratio 1.032.
- Mirroring equal-width raw source slots fragmented an unevenly spaced gait. Mirroring each complete approved extracted frame in place preserved pose integrity and temporal order. The earlier attempt remains in the source archive; the bundled compositor was retained.
- The generator's five-reference limit was handled by a deterministic pair collage, retaining all required identity anchors.
- A 19 MiB Library QA upload was rejected. Splitting the evidence into three smaller independent archives allowed successful preservation.

Future retries should classify the failure first, preserve passing rows, correct deterministic extraction errors deterministically, regenerate only visually incorrect rows, and rerun the exact final-byte gates and motion previews after any repair. Never repeat a rejected oversized upload or create a duplicate pet to compensate for a documentation failure.

Creative materials remain all rights reserved under [NOTICE.md](../../../../../NOTICE.md). These production archives are outside `public/` and have no application runtime references.
