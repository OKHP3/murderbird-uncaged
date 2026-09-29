# V20 — proportion checkpoint; likeness remains held

**Work in progress; likeness remains below the owner target.** This local continuation starts at commit `f10d0d96982c37dbeea47e346c66427385fd2700` on `codex/review-regression-v4`, worktree `/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged`. The canonical clone and historical production assets are preserved. No new candidate has been published or artistically accepted.

[Local comparison](http://127.0.0.1:5183/assets/audit/whole-character-v20/index.html) requires this Mac’s local server. The comparison leads with the actual owner-supplied reference, then uses the same orthographic cameras and neutral lighting for before/after model views. It is not perspective-image metrology.

## What the review changed

The previous approach repeatedly improved small connections without solving the whole character. V20 changes the body, shoulder, head height and supporting leg relationships. The independent final review finds only modest improvement for the effort; this is not whole-character convergence. Named rigid joints and their parents remain available to the existing exhibit; their old locations are not treated as approved anatomy.

| Study | Implemented change | Review disposition |
| --- | --- | --- |
| proportions01 | Raised head/neck, compressed torso and mantle, heavier limb sections, new joint positions | Rejected early. The actual head rise was 200 mm instead of the proposed 100 mm; compounded body/mantle compression removed too much mass, and a nonlinear foot-height mapping flattened the talons. No runtime export. |
| proportions02 | Head rise corrected to 100 mm with 55 mm forward shift; anterior breast depth retained/increased, mantle no longer doubly compressed, heavier limb members/journals, toe/claw clusters translated without changing their curves | Retained only as a provisional construction base. Independent review finds modest breast/shoulder/support improvement over V19, but a collar-like neck, blanket-like mantle and generic head remain. |
| cervical01 | Twenty front/flank guard and backing surfaces rebuilt as finite short courses | Rejected. Plain bands, a continuous vertical slot and an abrupt profile bend still give a collar appearance. |
| cervical02 | Smooth profile interpolation, staggered side courses, shaped free edges and root underlap | Rejected by root and independent review. Broad bands/gaps still read as a collar/drum. Neither neck variant is included in the runtime candidate. |
| runtime01 | Proportions02 with mapped mechanism sockets; same geometry and materials | Engineering-only derivative. Motion/attachment checks passed, but export investigation found two inherited NaN-producing breast tips. Preserved and superseded technically by runtime02. |
| runtime02 | Exact runtime01 with coincident tip vertices welded on two breast plates | Current local engineering review copy. Export warning and ten damaged triangles removed. Likeness remains held. |

All studies are preserved as separate editable `.blend` files and neutral renders under `assets/models/whole-character-v20/` and `assets/audit/whole-character-v20/`. Exact source, native hashes, 52-node before/after matrices and save/reopen evidence are in each attempt’s receipt. They are working constructions, not final art.

## Reference and regional contract

The owner’s resupplied whole bird controls the powerful body, compact wing and grounded presence. The documented July image controls head identity only; its excluded hanging wing and body proportions are not restored. [Reference relationships](../assets/audit/whole-character-v20/reference-relationships.md) and [image-space landmarks](../assets/audit/whole-character-v20/reference-landmarks.json) explicitly distinguish visual estimates from measurements. The original story, selected era images and preserved media remain unchanged.

| Region | Structure and exterior change | Era eligibility / motion source | Surface and inspection relationship |
| --- | --- | --- | --- |
| Head, bill, optic, crown | Shape preserved through rigid translation in the proportion pass; head/casing identity remains unresolved | Passive head structure inherited; Advanced sensing remains separately gated | Existing head/jaw/crown owners and contact relationships preserved; no new texture or sensor added |
| Neck | Proportions02 relationship to breast/head retained; twenty-surface guard reconstructions rejected and excluded | Passive guards in all eras; outside controls / limited transmission / coordinated actuators retain their prior roles | Inherited rigid guards remain on `neck` or `cervical-upper`; the short-course proposals are preserved only as rejected studies |
| Breast, waist, pelvis | Coordinated envelope/frame cage, broader breast and revised leg attachment | Inherited passive shell and frame | V19 front access door, fixed walls and bottom hinge retained; old shaft/return interference is not presumed solved |
| Shoulders and wings | Substantial compact mantle restored after rejected compression; no flight area or tail extension | Passive shield structure, historical repair eligibility retained; left motion restriction unchanged | Existing shoulder/elbow ownership remains; blanket-like plate hierarchy still needs reconstruction |
| Legs and feet | Members and journals enlarged around revised chain; toe/claw clusters retain their curved geometry | Passive frame inherited; procedural drive hardware remains era-specific | Fresh motion/contact checks pass; detailed moving clearance remains unproven. Heavier sections are not strength proof |
| Rear and unseen surfaces | Short counterbalancing outline retained; runtime rear hinge can read authored local position | Passive inherited rear plates | Reconstructed details remain proposals |

Materials remain the existing neutral/vertex-based production system. No UV, texture, aging or finished surface pass is claimed. Geometry is rigid at runtime; the authoring cage is baked into a versioned derivative rather than stretching armor during motion.

## Runtime attachment work

`src/scene/era-mechanisms.js` now optionally reads a complete `mechanismLayoutV1` contract from the model’s body. It covers Maker horn offsets/cradle width, the compact rear pivot, whole Mechanic transmission origin, Advanced distribution origin and body/neck cervical sockets. Historical models without the property retain their original placement. Malformed contracts are identified as legacy fallback in metrics.

[Mapping helper](../scripts/derive-mechanism-layout-v20.py) executes the frozen cage source against its exact old/new rig matrices, converting native world points to glTF owner-local coordinates. It writes a new proposed layout and never edits an existing native or GLB. These are transformed source placements; actual surface seating still requires inspection. The Mechanic gear train is translated as a rigid assembly, not nonuniformly scaled.

[Attachment checker](../scripts/verify-mechanism-layout-v20.mjs) measures produced cylinder endpoints/fixed mesh centers against the declared owner-local sockets through selected transformed poses. It also checks disconnect/reconnect and procedural era visibility. V19 and V9 legacy paths each pass 103 checks; runtime01 and runtime02 each pass 103 authored-layout checks, with maximum measured endpoint discrepancy 4.77e-9 m. The first V19 receipt is preserved with checker failures; scene-sibling lookup and fixed-cylinder endpoint measurements were corrected before the fresh successful runs. This is attachment propagation evidence, not a clearance, strength or likeness verdict.

## Exact current candidate and export repair

[Runtime 02 on this Mac](http://127.0.0.1:5183/?review-body=v20-runtime02&review-seed=927) is selected only by its explicit development query. The development default remains V16 and production remains V9. The local comparison links to the correct current candidate; no live-site update is claimed.

- Editable native: `assets/models/whole-character-v20/attempt-runtime02/murderbird-whole-character-v20.blend`; SHA256 `eb15a9d87de56fb8a06004d9c69448c38089f0ecacd888e3e7fde921a353d42a`.
- Browser derivative: sibling `.glb`, 12,017,272 bytes; SHA256 `d8d0192d89dc5e16973b86c834997b9aab694f0bf464336c2168330a6263267c`.
- Exact reference-angle render and render receipt are under `attempt-runtime02`. Matched seven-view comparisons and eight illustrated movement poses remain explicitly labeled **runtime01**, before the tiny repair; they are not misrepresented as new runtime02 captures.

Two inherited breast laminas each had three exactly coincident raw tip vertices. Their bevel modifier generated a nonfinite vertex, which the exporter substituted with the origin, stretching ten connected triangles. The new write-once repair welds only those tips at 1e-8 m tolerance. All 744 evaluated meshes are finite and validate without repair. The other 742 mesh snapshots, 52 rigid joints, 463 guides, all materials and socket metadata remain exact. The native was reopened and its hash preserved through export and rendering. The export warning, two substituted origin vertices and their ten incident triangles are gone. **115 other near-zero exported triangles remain**; this repair does not certify every surface. See [technical repair record](../assets/audit/whole-character-v20/attempt-runtime02/repair-report.md).

## Verification boundaries

Fresh exact-runtime02 checks pass: mechanism attachment 103/103; kinematics 4/4; inspection/reassembly 1/1; Advanced power 4/4; claw contact 32/32. Reports and logs live under the corresponding `attempt-runtime02` folders and each embeds the exact GLB hash. The 21-pose packet (290 named transforms) has SHA256 `df6920b012338c12f7620397eb13b7e6f2a11163d61992012c339e119f245422`. These are kinematic and attachment checks, not physical simulation, complete collision detection or likeness acceptance. Prior breast-opening and neck interference findings are not presumed resolved by these tests.

Runtime01 was exercised in actual Apple M4 Max WebGL at a 856 × 648 drawing area and DPR1: all five Maker levers, the Mechanic driven sequence, Advanced jump and thrust, opening, separation, reassembly and era changes. Its brief thrust trace reported rolling frame p50 10 ms/p95 10.6 ms, 362 draw calls and about 1.108 million rendered triangles. This is a short desktop observation, not sustained performance or a mobile claim. Saved traces and screenshots are under `attempt-runtime01/browser`; a control-focused Maker screenshot does not show the whole model. Runtime02 was separately loaded in actual WebGL, its served GLB hash verified, and opening/separation/reassembly reviewed. Its browser warning/error log was empty at capture. Illustrated fallback loaded the 1100 × 1100 V9 still and was explicitly labeled as such. Its own browser evidence is under `attempt-runtime02/browser`; runtime01 timing is not presented as runtime02 timing.

The initial dependency install, build and publication-boundary check passed. Its [receipt](../assets/audit/whole-character-v20/build/receipt.json) records 134 emitted files. The final build after adding the explicit repaired-model route is recorded separately under `build-final`. V20 native/study files and private sources are excluded; production remains V9. Existing optional fsevents-script and bundle-size warnings remain. This does not establish remote CI, deployment or artistic acceptance.

## Remaining artistic work and changed method

[Independent visual verdict](../assets/audit/whole-character-v20/progress-verdict.md): breast/shoulder mass and limb bearing scale improve slightly; the more squared front risks reinforcing the barrel impression. The head still reads as a smooth casing with a goggle-like optic, the neck as an upright collar, wings as a broad wedge, and legs as open ladder structures. The finished three-era exterior assignment is **not complete**.

The next geometry pass must establish one coarse, shared **neck-to-upper-breast envelope** in side, front and three-quarter views before subdividing plates. The forward-full chest must flow into a curved mechanical neck rather than receive a separate tube. Do not resume standalone collar variants, material polishing or minor fitting work as a substitute. Review the coordinated envelope before rebuilding articulated overlapping guards, then check its actual extremes and breast-door clearance. Head cheek/bill/optic construction, compact shoulder fan, load-bearing leg density and regional plate hierarchy remain subsequent substantive work.

No owner decision is needed to reject known defects. July head authority and the current whole-bird target remain distinct; newly reconstructed unseen surfaces, mechanism arrangements and final era finishes still require artistic review once a coherent candidate exists. No new candidate is approved or published.
