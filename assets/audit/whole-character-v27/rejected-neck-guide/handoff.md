# V27 first-hinge guide — HOLD

**Do not replicate or integrate. No runtime source was changed.** Both the original coarse study and the one corrected guide are preserved. `correction02/` retains the correction before its analytic interpolation implementation fix; `correction02-smooth/` is the final measured version.

Only course2 front guards2/3/4 changed rigid ownership/placement; their directional mesh forms, modifiers and material assignments remain exact. Added one carrier node plus31 finite, closed, positive hardware solids using existing materials. All54 original named-node snapshots, other original meshes and material definitions remain exact. Native save/reopen is exact. The guard rest seat moves8mm forward; this was measured from actual solids and is a proposed placement, not an owner-approved dimension.

Root found the coarse curved directional appearance useful. The initial half-angle guide left two moving-guard/static-flank pairs at contact: guard2 versus course2 guard1, and guard4 versus course2 guard5. Its independently selected lattice travel reversed direction between adjacent knots. The bounded correction selects full-angle orientation and analytic cubic forward travel from8mm at rest to32mm at contact, with zero end slopes. It clears those flank pairs but trades them for six upper-course pairs: each moved sector2/3/4 versus that sector in courses3 and4. This is not a successful clearance repair.

Final strict sampling covers130 poses, including41 total-pitch values with three root yaws. Actual interior-range worst view/data: `correction02-smooth/worst-interior-range-neck.png` and `.json`. Full hardware diagnosis views: `rest-hardware-complete.png`, `interior-hardware-complete.png`, `contact-hardware-complete.png`. Hiding plates is diagnostic only; the saved native retains all geometry. Untouched other-hinge openings and inherited guard/head/body pairs are reported separately.

Final moved-guard/inherited-guard/hardware-hardware/hardware-original pair counts:

| Pose | Moved | Inherited | Hardware / hardware | Hardware / original |
|---|---:|---:|---:|---:|
| Rest |0|46|16|3|
| Maker |0|41|15|3|
| Attention |2|42|17|3|
| Contact |6|37|10|21|

Follower-center deviation from finite slot polylines is at most1.854µm; push-pull endpoint error is at most0.133µm. The rigid member stays approximately41.4367mm long. These measurements demonstrate captured trajectory/connection centers, **not captive-solid fit**. Guide rails intersect moving follower webs/rollers; cam rails intersect the rigid push-pull member; mounting webs conflict with an existing pin. Dense hardware pair count reaches35. Exact selected contact triangle witnesses are in `contact-failure-witnesses.json`; witness bounds are not penetration depths. No continuous collision, engineering, pressure-angle or physics proof is claimed.

Final source SHA256 `708d0f9798c2dd3fab49874873505b9a93a4277838e09ee0445ac8c4a6ac6414`. Native SHA256 `94faa8821a68be51c6143570715638b0e8ad6383681cf2d066b0a53699288d00`. Frozen file hashes are in each candidate `manifest.json`. Optional runtime integration would require authored guide metadata and carrier synchronization/capture/restore/reset in `cervical-articulation.js`; it is expressly not authorized by this failed gate.
