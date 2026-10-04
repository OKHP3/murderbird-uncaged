# Regional finish02 and readable lighting checkpoint

Reviewed shared goal: `origin/main:goal.md` at `251f2f0243181e97140179c2aff6eb057e165438`; input track `8efb5ba11eaa208d802ee876516648b1b08b79d1`. Exact four reference hashes are in `reference-hashes.json` and match the shared goal. Input native SHA-256 `89a0a885bf21f7b03f2f6bf394154ccbbc9e80ea7621f369dc01253141a7f742` matches the recorded surface01 receipt.

## API and final evidence

- `scripts/cg-supervised-finish02.py`: `apply(scene, output_dir, era='builder', reference_root=None)`; color and ORM maps derive from the retained original regional maps, with original normals retained. Output directories are write-once. Pass checkout root as reference_root to select existing era maps.
- `scripts/cg-supervised-lighting02.py`: `profiles()` and `stage(scene, min_z)` compatible with the supervised renderer. Neutral is identical to the inherited neutral rig. Workshop/cinematic use warm area key, broad cool fill, stronger ambient and contact ground at exposure 0. Stage is optional and marks ground authoringGuide.
- `attempt02/`: final frozen-camera before/candidate neutral, before/candidate inherited workshop and candidate readable workshop. First attempt remains preserved in the parent directory. Exactly two focused finish attempts.
- Integrator should apply `head-neck.apply(scene, ROOT, era)` first. Its existing optical rule darkens Maker/Mechanic. Finish02 does not touch optical material slots, so builder retains restrained authored awakened orange optics. Final proof is builder only.

## Diagnosis and visible assessment

Actual source graph correctly links color, green roughness and blue metallic channels. Source armor metallic means .722-.739; roughness .541-.583; machined steel metallic .899/roughness .349. Subtle green-gray source colors under broad white reflection produce the pale appearance. New armor treats protective paint/patina as lower metallic, with exposed abrasion retaining bare-metal response; machined hardware is warm, black recesses are matte, steel bill/talons remain distinct. Existing map wear placement is retained, not replaced by additional scratch counts.

Confirmed from images: warm hardware separation improves across neck, shoulder and legs; armor is darker under the identical neutral rig; readable workshop reveals the torso, bill and leg construction with normal exposure. Gain is modest relative to canon: armor remains comparatively smooth and broad, several visible gaps are geometric, and the workshop warmth reduces green contrast. No likeness acceptance is claimed.

## Checks

PASS: Blender 5.2.1 renders; both finish invocations asserted exact mesh/pose/parent/UV/polygon material index/visibility/slot-count preservation. PASS: source hash matches retained receipt, four pinned reference hashes match goal, all five final image hashes verified, Python parsers pass. Original normal maps and optical slots are preserved. No source binaries were overwritten.

NOT RUN: Maker/Mechanic renders, integrated eight-angle/hero/animation views, runtime/WebGL/fallback, npm build, CI/deployment, owner artistic acceptance. This task changes no runtime asset references and publishes nothing. Integration must run the complete coupled character review before promotion.
