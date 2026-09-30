# Crown lap-fit checkpoint — 2026-09-30

Both fit versions are frozen; shaping has stopped after the final authorized attempt. **FIT02 passes the narrow29-pair rest-surface screen;42 inherited neighboring-course pairs remain held.** The preferred crown02 appearance is preserved. This is not full-fit certification or owner acceptance; root controls runtime review and integration.

The clean isolated checkout was fetched and verified at `c035d25625bec9521661e8ec5ab13ee9f547e278`, then switched to `codex/v38-crown-lap-fit-01`. Actual inputs are `assets/models/whole-character-v38/crown-study02/murderbird-v38-crown-study02.blend` SHA256 `e4d1077ecaafd64f051f2fa4728aef39c995eeac03d9e0f5daa5dd259caed1c6` and matching rigid GLB `6acb739d715e43dc712bfe6253156d12efaaa1e456d4bfb456435bd28bb13e1e`. Only those tracked LFS inputs were hydrated from root's hash-matched binaries; their working-tree entries remain unstaged. Historical files and old worker checkouts were not edited.

The construction direction remains the already reviewed short swept crown02; July controls the head only, master03 and Mechanic cross-check inheritance. Exact reference paths/hashes are in the receipt. No body or wing geometry was imported. The hidden receiving rebate is reconstructed finite geometry, not a reference-confirmed fabrication specification.

## Exact scope and rigid ownership

Only 29 existing trailing objects named `V38 swept crown course {row} column {col} leaf 2` change: rows0–2 columns0–6, row3 columns1–5, row4 columns2–4. Each retains338 vertices and its topology. The explicit allowlist is vertices0–64 and169–233: the paired outer/inner first five rows,130 vertices per object. Both finite surfaces move together along their source stock direction, at most2mm inward, with a smooth return to unchanged geometry. Paired stock remains3mm within2e-7m; the meshes remain closed and positive-volume. This preserves stock rather than shaving it away.

All29 leading leaf1 meshes,208 excluded vertices in each trailing mesh, and1184 other original objects have exact signatures. No objects are added/deleted, no nodes or attachment matrices change. All58 crown identities remain separate under `cranial-cover`, which opens relative to `head`; the fixed frontal seat and all temporal backing remain head-owned and exact. No bridge between those owners is added. Material `V38 contrast / crown-plate`, plate/inherited-passive roles, and maker/mechanic/builder eligibility are retained. Reconciled bill/cheek, optic seat/lens and illumination gates, jaw/cervical chain, body/wing/legs/feet and left restriction remain exact.

## Actual targeted checks

Native save/reopen signatures, exported node names/rigid parents, and exact standard PBR/material `eraFinishes` records passed. Actual GLTFLoader→applyEraFinishes passed for all58 crown leaves in all three eras using real shared exported materials; visibility and profile references persist. This is parser/material evidence, not browser-render acceptance.

The byte-identical root paired screen uses raw actual triangulated surfaces and unchanged BVH epsilon1e-7m. Baseline29/29 paired laps have candidates; FIT01 has5/29. The five residuals are row3 columns1–5, with110/78/302/77/82 triangle candidates. Exact triangle-index pairs and vertices are frozen in `residual-footprint.json`. All residual trailing vertices lie inside the declared rebate allowlist (outer rows0–3 and inner rows0–2); leading hits reach inner rows9–12 and occasional outer/endwall rows11–12. FIT01 therefore **does not pass all paired laps**.

The additional same-epsilon surface screen compares every changed trailing leaf against builder-eligible native meshes, including same-owner courses, backing and fixed seats. It found48→42 neighboring-course pairs,29→5 paired laps, and0→0 fixed-seat/backing/other pairs. No new pair was introduced;47 were retained and30 removed. Retained triangle counts change and do not measure penetration depth or severity. These are rest-surface dispositions only: no containment, self-intersection, continuous sweep, tolerances, loads or full-solid clearance proof is claimed. Existing neighboring contacts remain unresolved.

Matched1200×1200 neutral baseline/candidate views are full-bird three-quarter plus head profile/three-quarter/front/rear. No motion render or illustrated fallback was authored. Root's browser/opening/contact/build observations must be reported separately.

## Frozen artifacts and reproduction

FIT01 native: `assets/models/whole-character-v38/crown-fit01/murderbird-v38-crown-fit01.blend`, SHA256 `ff982093ab3edaceb031dc75ad7b9bf9492e280c7f165213df2e2a433ac79be5`.

FIT01 rigid GLB: `assets/models/whole-character-v38/crown-fit01/murderbird-v38-crown-fit01-rigid.glb`, SHA256 `a1816fd01994cc4f6f2167c2407ecc26c9430a31d92df3312962c5d4cdd0d35b`.

The recursive `assets/audit/whole-character-v38/crown-fit01/freeze-manifest.json` records28 artifacts; manifest SHA256 `3749b289eb5821494c9c801088673453594fd6fd8e2136cfc7ed35813988970d`. It covers models, ten matched images, receipts, actual checks, and executed source copies including the preserved pre-export failure. It excludes itself and this handoff. All versioned artifacts are write-once.

The latest top-level recipe now produces FIT02 from pinned actual FIT01 inputs. Fresh reproduction from repository root, with no existing FIT02 output directories: `/Applications/Blender.app/Contents/MacOS/Blender -b --python scripts/build-v38-crown-lap-fit.py`. To reproduce FIT01 separately, copy its frozen executed-builder.py and executed-region.py to the two original script paths in a fresh checkout, then invoke the builder there; audit source copies derive ROOT from the original script location and are not standalone runnable from the audit directory. The builder derives project paths from its own location but reads the three actual reference binaries at machine-specific canonical paths under `/Volumes/OKH-Local/04_GitHub_Mirrors/murderbird-uncaged`; those exact paths are recorded in receipt.inputs.viewedReferences. Relocate that read-only reference root explicitly on another machine; do not replace pinned inputs or reuse frozen outputs.

The initial execution stopped before exporting because an assertion compared interleaved changed indices with an ascending allowlist. Its actual sources/log remain under `pre-export-failure/`; the geometry proposal did not change. The corrected executed recipe continued only that pre-export state with `-- --resume-failed-pre-export`, retaining existing baseline images. Both normal and continuation modes reject existing native, GLB, receipt or candidate media. That was the only FIT01 geometry proposal. FIT02 is the one authorized final local correction described below.

Actual parser check invocation is recorded by `executed-gltf-check.mjs`: Node script arguments are GLB, root's era-finish.js, existing Three.js directory, output JSON. This used root integration checkout's existing dependencies, with no installation. Paired/neighbor/residual script arguments are respectively native+output, baseline+candidate+output, candidate+output. Each diagnostic refuses an existing output file.

Owned changed paths are the two new recipe files, new model/audit crown-fit01 and crown-fit02 trees and this handoff. No runtime code, commits, pushes, publication or broad test suite was performed. Retained neighboring surfaces prevent construction acceptance; broader appearance and motion remain root/owner review work.

## Final localized FIT02

FIT02 starts from the exact frozen FIT01 native/GLB hashes above. Only existing row3 trailing leaf2 columns1–5 change; all other FIT01 changes remain exact. The first radial solver stopped before export at its6mm safety bound. Its source/log and existing baseline media were preserved under FIT02/pre-export-failure. The safety bound was not raised. Read-only sparse seating diagnosis showed why radial seating is poorly conditioned against the curved leading/endwall region; actual nearest inner-face normals supported the final local correction.

One final correction samples actual finite leading inner triangles over the receiving triangles, derives a local field using their normals, and moves each paired outer/inner vertex by the same vector. It targets a0.4mm inner-normal sample gap plus0.2mm sampled-triangle envelope allowance. The sample gap is an authored solver target, not a measured minimum clearance certificate. No trial-loop or blanket deeper lowering was used. Actual same-epsilon triangle screens govern the result.

The precise per-mesh changed vertex indices and local normal offsets are in FIT02 receipt.contract. Additional changed vertex counts are108/98/110/102/104 (522 total) within the existing130-index maximum scope per leaf. Maximum additional authored displacement is2.065713mm; actual round-tripped vertex movement is2.065716mm, and maximum cumulative movement from original crown02 is3.394275mm. The29 leading leaves, all excluded receiving vertices and1208 other FIT01 objects are exact. All58 identities/owners/materials/era eligibility remain unchanged. Both finite surfaces retain their paired3mm section vectors within2e-7m, closed topology and positive volume; no normal-thickness/tolerance or load certificate is claimed.

The identical paired screen now reports0/29 surface-candidate pairs (source29→FIT01 five→FIT02 zero). The comprehensive neighbor screen reports source48→FIT01/02 42 neighboring-course pairs, no newly introduced pair against either source or FIT01, and no fixed-seat/backing/other surface pair. Against FIT01,34 retained neighbor triangle counts are unchanged, four decrease and four increase. Those counts are not penetration depth;42 inherited neighboring interfaces remain unresolved. Zero paired candidates does not establish containment, continuous sweep or full-solid fit.

Native save/reopen, rigid export ownership and exact standardPBR/eraFinishes records passed. Actual GLTFLoader→applyEraFinishes again passed58 crown leaves/all three eras. Five matched neutral baselineFIT01/candidateFIT02 views are frozen at1200×1200. No runtime, full suite, fallback or publication work was performed here.

FIT02 native: `assets/models/whole-character-v38/crown-fit02/murderbird-v38-crown-fit02.blend`, SHA256 `11af51be40c3a725daaeb4c7697640e3bb388d575733f1d620f630e172149137`.

FIT02 rigid GLB: `assets/models/whole-character-v38/crown-fit02/murderbird-v38-crown-fit02-rigid.glb`, SHA256 `7b5efb08d497035f98153a14143b41470e7c4234c60dcacf341916aea18d94ea`.

FIT02 recursive freeze-manifest has32 artifacts; manifest SHA256 `993f58da9540c7a304aaf3b666c4475ef47e4ace7a1d711c65f6dadaa1f08fd2`. FIT01's28 entries remain exact. The two manifests cover60 artifacts and exclude themselves/this handoff. Both executed source versions and failures are retained. The latest source recipe is FIT02 and write-once; it was executed with the explicit pre-export continuation flag after the safety-stop diagnosis. Neither version can overwrite existing native/GLB/receipts/candidate media. Saved seating-diagnosis scripts use this machine's absolute worker/tmp paths; they are historical executed snapshots, while the current builder uses project-relative inputs and the canonical reference root described above.
