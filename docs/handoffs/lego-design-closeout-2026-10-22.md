# LEGO MurderBird research thread closeout — October 22, 2026

Thread: `01a0f093-0273-7583-b8b1-cb2df6a378b0`, **Plan LEGO MurderBird Design Tools**, local Mac host.

The research, manual-build brief and October 1 model review are complete. This closes that research scope, not physical LEGO construction or the separate cinematic production goal. Final integration, CI and cleanup evidence is recorded after the containing pull request merges in `.local/closeouts/lego-design-2026-10-22/final-receipt.json` in the preserved canonical clone. Archive the chat only after that final audit passes.

## Recovered commitments and result

The available seven original user requests, prior replies, saved session and two artifacts were reviewed. Later instructions replace earlier powered brainstorming.

| Commitment | Result |
| --- | --- |
| Compare open-source and LEGO-supported design tools | September 29 research recommended proprietary BrickLink Studio as the practical LEGO-recommended workflow, with LeoCAD plus LPub3D as the open-source alternative and LDraw interchange. No installation was promised or performed. |
| Assess Powered Up motion, hardware packaging and rough cost | Answered as hypothetical feasibility and sizing research. The owner later explicitly dropped animatronics for affordability; motor, hub, sensor and powered-control proposals are superseded. Historical prices are not current quotes or purchasing authority. |
| Record an advanced, manually movable Technic/conventional-brick concept | [Manual design brief](../lego-murderbird-design-brief.md): structural frame, brick armor, proposed joints and optional support. “Advanced” describes construction ambition, not a selected era. |
| Review models saved in the days preceding the October 1 request | [Dated model review](../lego-murderbird-35cm-model-review.md): V37 and retained/held V38 studies, source hashes, measured saved-pose proportions and physical limitations. This is not a claim to have reviewed all later October CG work. |
| Confirm approximately 14 inches, with an assumed 84-inch full-size bird | Exactly 1:6; 14 inches is 35.56 cm. The source height is the owner's premise. Remeasured V38 saved-pose envelope: 192.8584 × 231.9719 × 355.6 mm, width × depth × height. |
| Preserve, reconcile, verify, clean up and archive | Scoped originals preserved; existing integration verified; documentation corrected on an isolated branch. Final remote/CI/parity/cleanup evidence follows in the local final receipt before chat archival. |

The unselected era, owner budget, reusable inventory, CAD assembly, instructions, priced shopping list, physical load tests and final likeness acceptance were future-phase proposals or unknowns. This thread contains no instruction to build or buy them. They do not become outstanding implementation requirements through this closeout. A future physical phase should first establish era, inventory and budget, then test the loaded head/neck and leg/foot construction.

Historical tooling sources retained from the September 29 research: [Studio introduction](https://studiohelp.bricklink.com/hc/en-us/articles/5404381697559-Introduction-to-Studio), [LDraw export](https://studiohelp.bricklink.com/hc/en-us/articles/6502197862679-Exporting-to-other-formats), [LeoCAD](https://www.leocad.org/), [LPub3D](https://trevorsandy.github.io/lpub3d/). These preserve the research trail, not a fresh October 22 vendor-feature or pricing audit.

## Repository and integration identity

- Canonical repository: `https://github.com/OKHP3/murderbird-uncaged.git`, default branch `main`, verified owner account `OKHP3`; CLI access reports admin permission. No branch-protection rule or repository ruleset was returned at preflight. Required review/security/check gates must still be respected if configuration changes.
- Canonical working directory: `/Volumes/OKH-Local/04_GitHub_Mirrors/murderbird-uncaged`. At initial inspection, its tracked state was clean and HEAD matched fetched `origin/main` at `12418f803160e29b17114a78d9ac9d3a8443794c`. Another active thread subsequently advanced it to `2f0d919cb89aedc6a00575e686e81baa3bd2d27e`; this closeout did not create or alter that thread's commit.
- Both LEGO documents were already committed on October 2 as `7a89dcec755b6bcb02b90713c184b45ba6477e0b`, an ancestor of current `main`. Their bytes were unchanged through the inspected pre-closeout main. GitHub returned no associated PR for that historical commit. Its exact-SHA Validate build run [37035854844](https://github.com/OKHP3/murderbird-uncaged/actions/runs/37035854844) and Pages run [37035854858](https://github.com/OKHP3/murderbird-uncaged/actions/runs/37035854858) succeeded. This supersedes the last chat's accurate-at-the-time untracked status.
- Reviewed shared authority: `origin/main:goal.md` at `2f0d919cb89aedc6a00575e686e81baa3bd2d27e`, front matter `last_updated: 2026-10-05T22:41:46.655Z`. Its unmet likeness/engineering/continuation duties belong to the separate visual-production program.
- Closeout branch: `codex/lego-design-closeout-20261022`, based on that fetched main. Only the two LEGO documents and this receipt belong to the closeout PR. Final receipt records the PR, head and merge identities.
- No Replit project, Replit branch, agent task, deployment or synchronization commitment was established by this LEGO thread. Other repository threads' Replit projects remain outside its scope. No agent was dispatched, paid mode selected or Replit synchronization claimed.

## Corrections and fresh validation

- Clarified that the V38 recommendation applies to the October 1 reference set; the retired worktree path is historical provenance, not a current dependency. The brief no longer calls that study the latest without a date.
- Replaced the stale pending budget-question statement with a future inventory-phase prerequisite. Preserved the manual scope, 1:6 target, unknown cost and non-certified construction status.
- Recovered both V38 GLBs using immutable Git revision `a06c243d4cd3c764c3bacb876c2bf149c566fa25` and cached LFS objects, without recreating the historical worktree. All three reported SHA-256 hashes matched. Every POSITION vertex was transformed through the node hierarchy; finite coordinates, scale conversion and V38 whole-envelope parity passed. All recorded regional dimensions agree at their published rounding.
- GitHub API checks resolved the three immutable V38 handoff/disposition paths and the V37 production record. Local documentation links, relative destinations, content boundaries and whitespace were checked. No creative source, runtime, app, dependency, test or acceptance threshold changed.
- A separate final pass checks the seven original requests against the final diff and verifies content on remote main, CI, local parity and cleanup. App/runtime behavior was not changed; new local app build and browser sessions are not acceptance requirements for this documentation-only increment. The normal repository CI remains the integration gate.
- Recoverable execution issues: the thread tools rejected oversized inventory limits; corrected calls succeeded. Sparse setup initially left the new no-checkout worktree empty, so the first attempted edit found no file and changed nothing. Materializing the owned sparse index with `git read-tree -mu HEAD` corrected setup; subsequent edits and validation succeeded. Initial V38 paths were absent from current main; immutable pointers and verified cached LFS bytes supplied the exact historical sources instead of substituting later models.

## Preservation and cleanup boundary

Preflight recorded staged/unstaged/untracked/ignored state, branch tips, unpublished divergence, stashes, worktrees and active-thread inventory. The canonical clone had no staged, unstaged or untracked files, and the shared stash list was empty. No old LEGO-specific branch or worktree was found. Other live threads share the canonical checkout, so this closeout uses an isolated sparse worktree instead of switching their branch.

Nine pre-existing linked worktrees were inspected. Several contain dirty/untracked files or local-only commits; none belongs to this LEGO thread. Their sources, ignored directories, shared branches, private `.local/` archive and nested ACE-Step repository remain in place. This closeout neither resets nor deletes them. The historical `review-regression` directory was already absent; its immutable source revision and LFS data remain recoverable.

Recovery evidence lives outside the disposable checkout at `.local/closeouts/lego-design-2026-10-22/` in the canonical clone: exact pre-closeout copies of both documents, `preflight.json`, `measure.py`, `measurements.json`, and the final verification receipt. The location was confirmed Git-ignored before writing; no private archive or raw process/session inventory is staged.

The only eligible cleanup targets created by this thread are its new closeout worktree and branch. Remove them using Git only after the three intended document blobs are verified on `origin/main`, required CI passes, the worktree is clean and final active-use checks find no dependency. Preserve the merged commit and all recovery evidence. Record actual removal and ref absence in the final receipt; do not infer cleanup or archival from an attempted command.
