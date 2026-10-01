# Crown layout checkpoint — rejected shape

The single saved 13-plate layout is preserved for review, not adopted. It removes the inherited thin strips but reads as a smooth cap and barely improves the whole bird. Root and the independent visual reviewer agree. Four plates also have 24 nonmanifold boundary edges. Stop repair of this particular shape; retain jaw-stock01 as the review default and V37 as production.

## Identity and scope

- Working branch: `codex/v38-crown-layout-integration-01`; parent `836eb5919e1007b699f7b0a947dd79bed1df55f2`. The commit containing this note is the checkpoint; remote acknowledgments must name its full SHA.
- July owner selection controls head only. Its body, perch and hanging wing train remain excluded. Master candidate03 supplies the whole-character comparison. Actual verified media hashes are in `reference-scope.json`.
- Source: repaired-jaw native `507a58f5670677276f8f06d3769deb9eb6cbd178a20f20a2993986d02374f63a`; GLB `0099e5026750db916bb05ac1c66f3fc51a169d941448d6b834d6058e33d0dc04`.
- Rejected native: `cf8ad159a977b4f245867e25bb7547695e264e62df4cbb2008cf0d6aee3c3386`; GLB `3e9f7fd3d88fdda6d6360d369f788a78d7b473085b7a1c0edb1a95bb8a290edb`.
- 58 crown nodes replaced with 13 passive plates. Actual export comparison proves all 642 surviving nodes, material definitions, geometry, hierarchy, transforms and metadata unchanged. No new era capability or powered hardware.

## Review and checks

Local review: http://127.0.0.1:5185/assets/audit/whole-character-v38/crown-layout-integration01/review.html

Matched profile, head three-quarter and complete-bird images accompany the editable native and GLB. New development selector is excluded from production. `npm ci` and `npm run build` passed once during integration; all 52 emitted paths and four production model/capture hashes match the prior build. Existing Three.js chunk-size warning remains. Build verification does not establish deployment.

The already-completed geometry screen found no strict self crossings but failed boundary stock. Crown-to-unchanged-head crossings were 38/31 at rest and 4/12 at inspection for source/candidate. Replacement crown identities prevent inherited-pair equivalence. Root surfaces, continuous clearance, full movement envelope and owner likeness remain unaccepted. No additional motion suite is justified for this rejected shape. `browser-evidence.json` records only the runtime checks actually performed.

## Paths and next action

Owned additions: `scripts/build-v38-crown-layout01.py`, `scripts/regions/v38-crown-layout01.py`, `assets/models/whole-character-v38/crown-layout01/`, `assets/audit/whole-character-v38/crown-layout01/`, and `assets/audit/whole-character-v38/crown-layout-integration01/`. Integrator changes only the development selector in `src/scene/presence-exhibit.js`. Historical assets and production remain intact.

Do not start another crown micro-adjustment or repair this rejected stock. The next assignment must choose a visibly larger complete-bird discrepancy from the controlling reference, with an early image before geometric elaboration. The pending narrow-versus-full neck choice is unchanged and is not answered by this study.

## Bounded Replit delivery

Free mode only. Fetch and fast-forward only the existing detached preview from the parent above to the pushed checkpoint. Preserve workspace main, untracked briefs, servers, dependencies and all 46 previously hydrated files. Hydrate only the four entries in `asset-routes.json`, verifying committed LFS pointer hashes. Do not rescan or hydrate the full archive. Existing LFS credentials failed previously; use the authorized public GitHub media route when required.

Run the new read-only `verify-preview.py --sha FULL_CHECKPOINT_SHA --parent 836eb5919e1007b699f7b0a947dd79bed1df55f2 --port 5000` once. It verifies current assets/routes and proves earlier tracked assets unchanged by an ancestor diff. If exact hydrated files have stale index metadata, refresh only those paths and check status once. Return the exact SHA and concise receipt, then stop. No install, build, test, restart, push, main reconciliation or publication. Repeat any input question in ordinary chat; never rely on a hidden response card.
