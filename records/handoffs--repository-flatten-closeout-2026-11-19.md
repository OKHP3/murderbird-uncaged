# Repository flatten, Replit reset and cross-repo cleanup: closeout ledger

Date: 2026-11-19 to 2026-11-20 (America/Chicago). Base reviewed: `main` at `35b156f`.
Thread: the Claude (Cowork) thread that began on September 27 with the media-migration review, assessed the project on November 12, and from November 18 to 20 consolidated the local clones, flattened this repository, reset the Replit workspace and pruned stale branches here and in `OKHP3/overkill-hill`.

This ledger records what that thread changed and how to recover anything it retired. It adds no modeling, no publication and no artistic acceptance. The [assessment ledger](handoffs--assessment-thread-closeout-2026-11-17.md) and the [visual critique ledger](handoffs--visual-critique-thread-closeout-2026-11-17.md) remain the records for the earlier requests.

## Requests and their dispositions

| Request | Disposition | Evidence |
|---|---|---|
| Flatten the repository so no iteration is buried in nested folders (owner chose "product-only main") | Done. `main` keeps the shipping exhibit plus two flat folders: `media/` (runtime assets) and `records/` (history). About 12,000 iteration files left `main`. | Commit `5f1c2cd`, [flatten-map-2026-11-19.csv](flatten-map-2026-11-19.csv), tag `archive/pre-flatten-2026-11-19` at `e0d3976` |
| Verify the flatten before pushing | Done with real hydrated media: `npm run build`, 55 of 55 unit tests, and the theme-release, publication-boundary and presentation verifiers all pass. | Commits `5f1c2cd`, `621ce82` |
| Keep the publish workflow able to hydrate what it needs | Done. The manual Pages run now pulls `media/*` and `public/audio/**`, because the theme audio lives under `public/`. | Commit `621ce82` |
| Clean up the laptop clone's branches and worktrees | Done. Local `main` only, no linked worktrees, in step with `origin/main`. Unpushed work from other clones was preserved as bundles in the owner's adjacent archives folder before removal. | Laptop clone, `murderbird-uncaged-archives/retired-worktrees-2026-11-19/` |
| Stop the Replit agent queue and reset the Repl to the flattened `main` | Done. 63 queued tasks and 4 suggested drafts were cancelled before they ran; none had started. The Repl now tracks `main` with no other branches, and its 185 stale remote-tracking refs were pruned. | Replit task board: 0 drafts, 0 active, 0 ready |
| Preserve the Replit workspace's local history before the reset | Done inside the Repl. Every local branch, `refs/archive/*` and `refs/replit/*` ref (90 refs, 65 distinct commits) is reachable from one annotated tag, `archive/replit-workspace-2026-11-19`. A 9.5 MB bundle of the 222 commits GitHub does not have sits beside it. GitHub refused the tag because it references 171 Git LFS objects that were never uploaded while the repository is over its LFS budget. | Repl only; see "Still open" |
| Fix the Replit post-merge install failure | Done. Replit blocks Vite 8.3.4, so `npm ci` failed after every merge. Vite is now exact-pinned to 8.3.8 with a registry.npmjs.org lockfile; build, tests and verifiers pass in the Repl. | Commit `425409c` |
| Clear GitHub issues, pull requests, notifications and old workflow runs | Done. Zero open issues and pull requests, `main` is the only branch, all repository notifications are marked done, and the 423 runs from before the flatten were deleted. The four runs left are all green. | REST API, November 20 |
| Repoint overkillhill.com links that the flatten broke | Done. Six links on the MurderBird project page now point to `records/` on `main`, or to the archive tag for the retired instrumental production notes. All nine repository links on the live page return HTTP 200. | `OKHP3/overkill-hill` commit `6e53c2c` |
| Prune stale branches in `OKHP3/overkill-hill` | Done. All 15 non-main branch tips were preserved in tag `archive/branches-2026-11-19` before deletion, and the 8 open pull requests on them were closed. | `OKHP3/overkill-hill` tag `archive/branches-2026-11-19` at `b3652070` |
| Archive this thread and the project's other threads | Owner action in the Claude app. No assistant tool can archive a chat. | |

Dependabot reopened two update branches in `OKHP3/overkill-hill` on November 20, as designed; those are live update proposals, not stale branches.

The visual critique ledger's E09 item (Replit checkout state) is resolved by the Replit reset above.

## How to recover retired work

- Any file that left `main` in the flatten: look up its old path in [flatten-map-2026-11-19.csv](flatten-map-2026-11-19.csv), then open it at tag `archive/pre-flatten-2026-11-19`.
- Replit-only history: in the Repl, `git log archive/replit-workspace-2026-11-19` lists each preserved ref tip as a parent of one archive commit, with the ref names in its message.
- Pruned overkill-hill branches: each tip is a parent of the commit under tag `archive/branches-2026-11-19` in that repository.

## Still open

| Item | Owner | Next action |
|---|---|---|
| The Replit archive exists only inside the Repl | Owner | When the Git LFS allowance is restored, run `git lfs push --all origin` in the Repl, then push tag `archive/replit-workspace-2026-11-19`. Until then, do not delete the Repl. |
| Copilot-extraction closeout content is not on overkill-hill `main` | Owner, or the Copilot-extraction thread | Its branch `docs/murderbird-copilot-thread-closeout-2026-11-18` reached GitHub and was pruned with the other 14 branches on November 19. Tip `08e2363f` is preserved in `archive/branches-2026-11-19`. The closeout receipt, Plate III images and `oxide-positivism.md` are not on `main`. A November 20 commit (`c340596c`) separately marked the brief superseded, so cherry-picking the two commits conflicts in `context/threads/README.md` and the brief; keep `main`'s wording there and take the three new files. |
| The live exhibit still serves release `914956e` | Owner | Run the Validate workflow manually with `publish_pages` once the Git LFS download allowance is back. |
| Mac Studio clone is behind `main` | Owner | The owner declined a scheduled pull; pull whenever the Mac is next used. |

Every other request this thread received is done or superseded. It is ready to archive in the Claude app.
