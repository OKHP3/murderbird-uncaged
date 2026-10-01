# Head fit checkpoint — 2026-10-01

Both versions are **VISUAL / ASSEMBLY FIT HOLD**, preserved as bounded repair evidence. No adoption, owner approval or production claim. The swept outer crown is preserved; its self-fold repair is useful. The hollow channel, broad rear shell and nape likeness remain unresolved. Two saved attempts used; shaping stopped.

Input is actual HELD cheek-nape02, fetched integration `307c3b3add4c460ad754f854959b7f16b61a3da8`. Native SHA256 `835d427c1b83692dcbeb7936770322c4ea55679d2861c452a6f9b350c81f6399`; rigid GLB `8b90593ebaf4d7bc883e1109a509e83f90b7cdd4da73b373cee4d86374618743`. July owner reference controls HEAD ONLY; Master03 and Maker-clean cross-check the whole bird. Exact actual reference paths/hashes and matched source camera links are in each receipt. Dimensions here are authored reconstruction, not art metrology.

## Scope and construction

Actual **65** meshes change inside the unchanged **83**-mesh watch: 58 `V38 swept crown course …` inner caps/side closures; `V38 optic cheek shield ±1 0/2`; `V31 temporal fitting root ±1 0`; and `V38 fixed occipital closure plate`. No additions, removals or reparenting. Exact names and before/after signatures are in receipts. The other **1156** objects retain signatures; exclusion digest `09f807d3a180e65689397837ea2f25427578661dbad3964fc2546f2547b69c1b`. True optic cups/floors/lips/apertures, bowl/socket, journals, bill/contact, body and all joint matrices remain exact.

Crown leaves use one fitted constant extrusion direction per leaf and a 2% inset inner perimeter, replacing fold-prone per-vertex normals. All 58 outer vertex arrays remain exact. Local extrusion is 1.024–5.970 mm; maximum actual paired-vertex distance is 6.257 mm. Minimum matched outer-triangle projected stock is 0.999961 mm, approximately the proposed 1 mm target. This does **not** prove minimum solid/rim thickness, manufacturing gauge or load capacity. All 65 changed meshes have zero nonmanifold edges, one component and positive signed volume; those properties do not establish assembly fit.

Root0 feet are closed volumes made from actual wall triangles clipped to 12×12 mm finite patches, retaining the unchanged 8 mm annular fitting bases. Per side, all 96 fitting-base triangles have 672 vertex/edge/centroid samples; maximum sample gap to return is 0.000030 mm. Receiver subtriangles also sample to ≤0.000030 mm. Clipped subtriangles intentionally differ from original full-face keys. These observations do not waive the root0/moving-inner-shell crossing.

All parts remain rigid, inherited passive Maker/Mechanic/Builder, with original material definitions/extras. Crown belongs to `cranial-cover`, withdrawing vertically by native Z / runtime Y +0.08 m open and +0.14 m separation; roots/shields/nape belong to fixed `head`. No bridge to moving neck. Nape is a short inboard overlap proposal, not a validated enclosure. Actual GLTFLoader → applyEraFinishes checks all 12 loaded material profiles in three eras with zero invalid; no powered sensing is added to earlier eras.

## Actual diagnostics and failures

Unchanged strict predicate: 1e-7 m plane, 1e-6 edge/barycentric; same 83 watch against the full eligible head/cervical finite pool, including same-owner pairs. Source/candidate five declared actual-chain samples include rest, Maker neck turn/jaw .32, contact neck/jaw .10, crown open and crown open+separated. These are sampled triangle screens, not containment, continuous motion, physical simulation or engineering certification.

| Sample | Source | 01 | 02 | New pairs 01 / 02 |
| --- | ---: | ---: | ---: | ---: |
| Rest | 183 | 134 | 134 | 0 / 2 |
| Maker neck turn | 183 | 133 | 135 | 0 / 2 |
| Contact neck | 183 | 134 | 134 | 0 / 2 |
| Cover open | 145 | 97 | 97 | 0 / 2 |
| Open + separated | 138 | 91 | 91 | 0 / 2 |

Self-screen over the same 83 source/candidate meshes: **64 → 0** for both. 01 removes wall/root0, wall/nape, shield2/throat and many crown contacts, but retains both cheek0/bowl crossings. Its actual witnesses are in `head-fit01/residual-witnesses.json`.

02 changes **only the two shield0 meshes** relative to 01, lifting/narrowing the measured lower transition. It eliminates both bowl/shield0 pairs in all five samples but introduces `V31 optic recessed receiving cup -1` / `V38 optic cheek shield -1 0` and the mirrored +1 pair in every sample. Actual cup triangles 240/241 cross shield triangle 154 at native Y −0.546…−0.530, Z 1.685…1.696 m. Witness triangles are retained in `head-fit02/surface-screen.json`. This is a protected bearing-seat regression, not an accepted joint contact. Root0 versus `V38 compact cranial inner shell`, inherited crown laps and other support contacts remain HOLD. Physical socket coordinate, metadata and matrices remain exact, with sampled distance <1e-6 m; this does not certify surrounding interfaces.

Next method must evaluate the required jaw-pose **union of actual cup + bowl volumes** before finalizing a cheek contour, rather than sequentially repairing one witness and crossing another. Moving root0 and its entire fitting requires a coherent finite wall land clear of crown withdrawal; it was deliberately left unresolved here. No further shape is assigned by this note.

## Frozen files and reproduction

01 native `fb5a23fb6f24d33b1e5ebb67a0daffb25409b714719469b487470691e0f8da49`; GLB `6906ba234f132bd42405cc4add4287bd3049e428c33ad22f766082d7ec926fc8`.

02 native `23265a4b21217945b6a6b88eb92be233ff34d77f9eb090714f79901ede5a61b6`; GLB `d5f6dbea68aa310f7ef7d92d6e6ff7295e08f115e5e7c56274246d3ba84f8189`.

Each model/audit `head-fit01/02` tree includes six matched neutral images, receipt, executed builder/region, screens and logs. Current `scripts/build-v38-head-fit.py` and regional recipe reproduce **02** from the pinned input and refuse existing outputs. 01 executed header has a stale swept-cranium run command; its bytes remain frozen, and the actual invocation was the head-fit builder. Header corrected before 02 execution. For reproduction, place each executed pair into a fresh normal `scripts/build-v38-head-fit.py` / `scripts/regions/v38-head-fit.py` layout, provide the pinned model pair, and invoke Blender `--background --python scripts/build-v38-head-fit.py`. Reference and Three.js helper paths are machine-specific read-only inputs; use equivalent hash-matching files. Do not overwrite frozen output paths.

The exact transfer union is `assets/audit/whole-character-v38/head-fit02/union-manifest.json`; it excludes itself. Root owns exported scope audit, actual browser motion/build and publication. Worker claims above are native/export diagnostics only; V37 production remains unchanged.
