# V16 — whole-silhouette correction checkpoint

**September 28, 2026. Partial improvement; likeness still fails the target.** V16 corrects the whole bird's rest proportions instead of continuing an isolated eye-detail loop. It is a local working proposal, not completion of structural reconciliation or the three-era exterior assignment. The owner's rejection is not overturned by passing movement checks.

Worktree: `/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged`, branch `codex/review-regression-v4`. Preserved starting checkpoint: `26d32906a8f5aad9fa6a457c20f7aca9f0da5d89`. Local development now opens **V16 attempt03**; `?review-body=v15-04` restores V15 and `?review-body=stable-v9` restores V9. Production still selects V9. This checkpoint has not been pushed or deployed.

[Local matched comparison and actual export](http://127.0.0.1:5183/assets/audit/whole-silhouette-v16/index.html) · [Local movement exhibit](http://127.0.0.1:5183/?review-body=v16-03&review-seed=927)

## Visible change and outstanding problems

| Area | V15 before | V16 attempt03 | Remaining discrepancy |
|---|---|---|---|
| Whole body | Slender transition, small shoulder cap, tapered breast | Fuller and vertically longer breast; broader lower body; stronger shoulder transition | Front now reads too squared; broad regular panels obscure the reference's curved plate hierarchy |
| Neck/head relationship | Long, narrow visible interval | Head 6% smaller, moved lower and back; curved neck and both joints remapped; lower guard edges eased | Cleanup at the neck base is modest; collar crowding and exposed/unresolved spaces remain |
| Eye/face | Large round socket field | Complete housing reduced, surrounding plate narrowed, existing fixings moved with its edge | Eye remains a plain focal disk; bill remains overly smooth; cover/brow and cheek construction are still weak |
| Wings | Compact narrow caps | Mantles broadened and lowered with their elbow assemblies | Still insufficient folded shield mass against the reference; left-side restriction remains |
| Legs/feet | Light journals and narrow stance | Thicker passive members/bearings, wider stance, enlarged complete feet | Exposed trusses and toes remain visually thin and simpler than the reference |

The [independent visual review](../assets/audit/whole-silhouette-v16/attempt-03/independent-review.md) inspected all six matched views and the actual owner, Candidate03, Maker and Mechanic media. It recommends holding this as a working proposal. The gallery makes the before/after scale, camera and neutral lighting consistent; source art remains perspective illustration, not an orthographic measurement source. July's authority remains head-only. The [regional construction and inheritance contract](whole-silhouette-v16-regions.md) records the mechanical interpretation and remaining attachment obligations.

Root's actual browser close-up at the Maker neck limit also exposes unresolved spaces beside the crown and at the upper breast. Functional controls and connected named joints do not make those areas resolved exterior construction. No finished material treatment was applied to conceal them.

## Versioned source and derivative

| Artifact | SHA-256 |
|---|---|
| [Editable Blender attempt03](../assets/models/whole-silhouette-v16/attempt-03/murderbird-whole-silhouette-v16.blend) | `3bd4b2e34d086fa15dbc9c06cdbcc0606b02430f9482f9d8d6877d39bec1318a` |
| [Runtime GLB attempt03, 6,409,788 bytes](../assets/models/whole-silhouette-v16/attempt-03/murderbird-whole-silhouette-v16.glb) | `a67df98c6e9cb3bcbba6a773859caaa5ccf161b33d63e4523128b0e6c9f7749c` |

The [composition receipt](../assets/audit/whole-silhouette-v16/attempt-03/receipt.json) binds the pinned V15 source, executed composer and two regional refinements. All 52 node names, 647 mesh names, parent relationships and materials survive; 51 node translations change with the rest geometry. Joint bases are unchanged. Geometry changes are baked into editable rigid meshes, with no animation-time scaling or stretching of metal. The 462 historical guide curves are preserved and remapped but hidden; they are not presented as functional cables. Save/reopen matches exactly. The [export receipt](../assets/audit/whole-silhouette-v16/attempt-03/export/export-receipt.json) verifies unchanged native bytes and all 52 exported nodes.

Attempt01 is preserved as a tooling failure with no saved model. Attempt02 preserves the first whole-body proposal and its successful bounded checks. Attempt03 adds the orbital/guard cleanup. The first exploratory orbital refit folded intermediate radial strips and was rejected before native output; the corrected module keeps positive radial spacing and exact aperture seating. Its [preflight record](../assets/audit/whole-silhouette-v16/orbital-refit-preflight.json) explicitly states that the rejected intermediate script was edited in place and has no preserved source hash. Historical native files, creative references and story snapshots remain intact.

## Verification performed

- **Fresh exact-model checks pass:** kinematics 4/4, inspection restoration 1/1, Advanced power moves 4/4, claw contact 32/32. Nine native jaw positions from 0 to 0.32 radians have zero strict crossings against the named bill/cheek/optic surfaces. These are bounded kinematic and sampled surface checks, not force simulation, full containment or continuous collision. [Check summary](../assets/audit/whole-silhouette-v16/attempt-03/check-summary.json).
- **Fresh pose evidence:** 21 recorded poses bound to the final GLB and eight [native pose illustrations](../assets/audit/whole-silhouette-v16/attempt-03/motion-renders/pose-render-manifest.json). All 52 native pivot matrices are applied from the packet. Historical guide curves stay hidden. Native illustrations omit the browser's procedural external controls and powered/transmission hardware.
- **Actual browser:** hardware WebGL loaded the final GLB. The five Maker sliders were individually operated and released; the Mechanic routine was engaged and sampled through its slow sequence; Advanced live observation accepted jump and thrust and recorded load/airborne/landing/recover and load/drive/brace/recover. The sampled jump height reached about 0.360 in fictional scene units. Opening, full separation and reassembly were exercised; separated wing, neck and power connections reported disengaged states. Maker/Mechanic inspection and every surface crossing were not exhaustively screened. Raw traces, images and conditions are under `assets/audit/whole-silhouette-v16/attempt-03/browser/`.
- **Gallery:** actual WebGL and fixed native render toggle were verified as distinct views; era filters showed 99/100/103 native mesh groups. This does not include the main exhibit's procedural mechanisms. The illustrated exhibit fallback remains the explicitly labeled older V9, not V16 acceptance evidence.
- **Performance sample:** the reassembled, paused Advanced view under neutral light reported a 10 ms median and 11.4 ms 95th-percentile frame at an 856×648 canvas, pixel ratio 1, on Apple M4 Max hardware WebGL (282 draw calls; 635,540 triangles). This is a local rolling sample, not a sustained motion benchmark or device matrix. [Browser summary and exact capture hashes](../assets/audit/whole-silhouette-v16/attempt-03/browser/summary.json).
- **Build/boundary:** `npm ci`, `npm run build` and publication-boundary verification pass. The emitted 134 files exclude V15/V16 studies, natives, raw audits and source archives. The [local modified-tree build receipt](../assets/audit/whole-silhouette-v16/attempt-03/build/summary.json) lists exact emitted hashes. Existing allowScripts coverage and bundle-size warnings remain. No remote CI or deployment claim.

## Next artistic and mechanical decisions

The next work should refine the exterior form around the new body: curved, varied breast layers; a distinct constructed optic/brow/cheek; a fuller folded mantle; and stronger ankle/toe machinery. These are already supported by the references and need implementation, not another direction questionnaire. The squared front and crowded neck base require caution before adding coverage. Known crown interference remains unresolved. Fixed-offset Maker horns, Advanced neck anchors, Mechanic crank locations and support dimensions still require an explicit surface-fit reconciliation; their module checks are not that proof.

Owner acceptance remains a later gate on a convincingly closer whole bird. Finished era surfaces, comprehensive articulation clearance and any new publication remain outstanding.
