# Lower-leg construction study V2

## Current candidate

One bilateral passive shin replacement was built from Alignment V9 (`assets/models/uncaged-alignment-v9/murderbird-alignment-v9.blend`, SHA-256 `4d7568d1c2ba7cab716876f57a6c20cb6a788d4daeef1d5d34f85c1910ed2bbe`). The native is `assets/models/uncaged-lower-leg-construction-study-v2/murderbird-lower-leg-construction-study-v2.blend`, SHA-256 `5ed49b3fd61ba10dd83eb54af850d6d9cc3dc3a81dccf4e14ced8c66f32ba85d` (1,974,612 bytes). It was built with Blender 5.2.1 LTS from the frozen generator `executed-generator.py`, SHA-256 `eee43d1ff9624e7a07aeda69c460d417ed91730ea33aaf256a3ded2bbdd837b8`; the working script and frozen copy have identical bytes.

The replacement removes exactly these twenty named source meshes: both sides' `shaped shin guard proximal`, `shaped shin guard distal-overlap`, and `tapered passive load rail.002` / `.003`, plus `Limb sheath fixing.006`–`.011` on the left and `.018`–`.023` on the right. It adds four rigid parts per side: proximal and distal fitted bearing saddles, a twin-bearing load cage, and an anterior wrap guard. The cages run between the existing shin and foot bearing centers. Guard hems join the rails; saddle seats mate to the cage. Additions are assigned to their existing shin owners and eligible in Maker, Mechanic, and Builder as static passive structure. No pivot or neighboring foot/talon owner was changed.

## Visual review and limits

Twelve fixed-rest Workbench views were rendered for the three eras at 1100 square. Their cameras, targets, scale, and renderer settings are recorded in `render-manifest.json`, alongside the matching V9 source images and hashes. The side and feet views show a more constructed paired-member assembly than V9's single plain shank bar. In the whole-body view the gain is modest and the lower-leg assembly remains visually small relative to the body. This is a proposal for visual review, not an owner-accepted design.

The first native attempt had an axis-unit error that placed its guards below the shank. Its exact native, generator, receipt, renders, and manifest are preserved in `attempt-01-initial/`; it is invalid and superseded by the current candidate.

The current work stopped after saving and reviewing matched rest renders at the supervisor's checkpoint. No strict crossing or adjacent-owner clearance audit was run for this candidate. Runtime poses, continuous motion, collision containment, physical load behavior, and browser/export appearance remain unverified. The available 37-sample V9 pose packet is Node-derived and was not applied here. No model/runtime application files, exports, commits, or publications were changed or made.
