# Visual critique and completion-plan thread: closeout ledger

Date: 2026-11-17 (America/Chicago). Base reviewed: `main` at `bda1ae31` (v1.1.0).
Thread: the Claude thread that ran the independent V38 visual critique (about October 1), the VFX-versus-engineering reorientation, the ChatGPT redirection prompt, and the November 11 state assessment and completion plan.

This ledger checks every request that thread made against what now exists. It adds no modeling, no publication and no artistic acceptance.

## Original request: bounded visual critique

| Requirement | Disposition |
|---|---|
| Inspect both exact-revision images and state whether both were viewed | Done. Both were downloaded and viewed, and the critique says so. |
| Top three visible structural differences | Done: neck and head mass, torso and shield-wing integration, breast construction. |
| Separate color and lighting from geometry | Done. |
| Single highest-value next modeling change | Done: neck, head height and bill. |
| One alternative breast construction in under 300 words | Done: shingle rows over a dark under-body, about 150 words. |
| Proposal only, no owner acceptance | Done. |
| **Correction found on re-audit** | The critique judged against candidate 03, as the request specified, and called its bill "short". The pinned July reference governs head identity and shows a deep, long, strongly hooked bill. The "short hooked bill" wording later reached the v1.0 closeout guidance. That line is corrected in this change. The neck and low-head findings stand: both canon images agree. |

## Additions made during the thread

| Addition | Disposition |
|---|---|
| Reorient from engineering accuracy to screen-quality VFX likeness | Done. Adopted as the October 1 operative mandate in [goal.md](../../goal.md). |
| Write a redirection prompt for ChatGPT | Done. Its gates (same-camera comparisons, two-iteration stop, budget per milestone, visual-only acceptance) appear in the October milestone plan. |
| Assess the project and plan a course to completion | Assessment and plan done November 11 in this thread. The plan was executed in other threads: v1.0 closeout merge and tag (November 13; GitHub release published November 15), Living Plates and v1.1.0 (November 14 and 15), the website project page update, and the November 16 Codex audit and execution register (E01 to E19, kept in the owner's Notion workspace). |
| End with archival of this thread and the project's other threads | Owner action. Threads are archived in each app. This ledger, the v1.0 closeout and the November 16 register are the records to keep. |

## Housekeeping done in this change

- Corrected the bill guidance in [project-closeout-2026-11-13.md](project-closeout-2026-11-13.md).
- Paused Dependabot version-update PRs (`open-pull-requests-limit: 0`) on the frozen repository. Security alerts are unaffected. Dependency PR #95 (vite 8.3.8) is closed unmerged on the same grounds as #89.
- Eight remote branches are fully contained in `main` and can be deleted: `claude/living-plates-20261114`, `claude/v1-closeout-20261113`, `codex/lfs-cache-preflight-20261029`, `codex/lfs-download-repair-20261026`, plus this closeout's own `claude/critique-thread-closeout-20261117`, `claude/ledger-branch-fix-20261117`, `claude/e10-plates-navigation-20261117` and `claude/ledger-final-20261117`. The assistant session that wrote this ledger could not delete branches (its write path refused ref deletion), so the owner removes them on GitHub's Branches page. Register item E11's local Mac branch and paused automation still need host access.
- Register item E10 is done and live. PR #98 added a Living Plates link to the exhibit and folio navigation and the folio and plates entries to the sitemap. The overlay workflow (run 44094659852, overlay revision `2c0603f7`) published it with the three patched base files recorded under `patchedBaseFiles` in `plates/overlay.json`. All other base files stayed byte-identical to `release.json`. Checked live in Chromium: one link in each nav, clicking it opens Living Plates, no page errors.
- An independent read-only check verified every repository and live-site claim in this ledger before the final revision.

## Still open, and why

Each item needs owner access or owner judgment. None of them blocks archiving the threads.

| Item | Blocker |
|---|---|
| Independent backup of the local mirror and private production (E07) | Destination found November 17: gjs-laptop's drive has 398 GB free and already holds a clean clone with about 9 GB of the 45 GB LFS set. The copy itself has to run from the Mac, which holds the full mirror and private production. |
| Replit checkout state (E09) | Authenticated workspace |
| Strict normal parity (E15) | Diagnosed November 17; the FAIL is kept. See below. Owner choice: accept it as a documented export artifact or re-export in a future scope. |
| Human device, listening and screen-reader checks (E12) | A person and hardware |
| TRELLIS result recovery (E13), promo reel disposition (E14), CRT source attachments (E18) | Original sessions and an editorial call |
| Full standard Pages republish | LFS budget restored. The live base stays `914956e` with the Living Plates overlay. |
| Final model likeness (E16) | Parked by owner decision. It needs a new, separately authorized project. |

## Evening round: ASUS clone reconciliation (E08)

The owner linked gjs-laptop (Windows, the ASUS clone) to this session on November 17. A read-only inspection used `git --no-optional-locks` and made no fetch, write or delete.

- The clone is clean and on `main` at `be988a5` (the v1.0 merge). It has no stash, no uncommitted files and no local commits beyond its remote branches.
- All 19 `archive/codex/*` tags in the clone exist on GitHub.
- The only refs not on GitHub are `refs/archive/worktree-consolidation/custody-bounded-replay` and `custody-normal-diagnosis`. Both point to file blobs, not commits: a replay script and its normal-diagnosis result. Both blobs (`df0b12a2`, `f1925e62`) already exist on GitHub, so nothing is unique to this laptop.
- The three Replit-era tips recorded as missing (`6b954808`, `76c6f152`, `0d7366d8`) and the older bundle head `c1bfca37` are not in this clone either. They stay under the October 23 owner-authorized historical exception.
- The remote-only PR heads were inspected on GitHub. `codex/foot-motion-png-evidence-validator` (#91), `codex/simultaneous-contact-report-dedup` (#90), `codex/archived-timing-diagnostics` (#92), `codex/mac-completion-coordination-20261026` and `codex/pr84-windows-followup` (#84) and `codex/asus-visual-technical-acceptance` (#83) are each 1 to 9 commits ahead of their base. All of those PRs were closed unmerged at the November 13 freeze, and the branches are kept as the record.

E08 is closed for everything reachable. Only the Replit-era tips stay unrecovered, under the existing exception.

## Evening round: native Blender checks (E04, E15) and branch cleanup (E11)

Run in the linked laptop's Linux VM with headless Blender 5.2.4 LTS. Each file was opened read-only and never saved; SHA-256 hashes were identical before and after. Scripts and results are kept privately on the laptop in the `murderbird-uncaged-archives` folder.

**E04, done.** The three retained04 natives at v1.0 open cleanly: maker (`bee3118c`), mechanic (`4f9dbbcb`) and builder (`9de7c4d1`, matching its LFS OID). Each has file version 5.2.44, 7,694 objects, 63 materials and 1,958,149 evaluated triangles, with every image packed, none missing and no linked libraries.

**E15, diagnosed, FAIL kept.** The recorded worst case reproduces exactly: max L2 0.008557 between the builder object "CGRF02 left forward toe 2 recessed joint shoulder 1" and the merged GLB mesh "Supervised CG metal05 / machined-steel / builder / retained-uv". All 961 failing vertices are hard-edge vertices with split normals; every smooth vertex passes. Normal quantization is ruled out (the GLB stores float32 normals), and so is the object transform (the worst object has uniform scale). The likely cause is the export merging nearly identical split normals at bevel edges, a deviation of about half a degree. The 2e-5 threshold is unchanged.

**E11, owner step.** An attempt to delete the owner-requested branch `claude/living-plates-20261114` through GitHub's web page was refused by this session's safety check, after the API and git routes had also been refused. The branch is 0 commits ahead of `main` (merged as #94). Delete it from GitHub's Branches page.

## Morning round, November 18: Mac housekeeping (E11, H05) and backup path (E07)

The owner linked the Mac Studio and granted this session its mirrors folder, the Codex settings folder and delete permission within the mirrors folder.

- **Mac mirror fast-forwarded.** The local `main` moved from `859983d` to `e52f3a9` (PR #103) with `merge --ff-only` after a clean preflight: on `main`, no local changes, no lock files, HTTPS origin, and none of the three changed files tracked by LFS. The checkout is clean and level with `origin/main`. Git's LFS post-merge hook reported a missing `git-lfs` binary in the session shell; nothing needed it.
- **E11 local half, done.** The merged local branch `claude/living-plates-20261114` is gone from the Mac mirror, and no MurderBird automation remains in Codex's automations folder. Only the three sibling hourly automations (askjamie, glee-fullytools, overkill-hill) are present, and they belong to other projects.
- **E11 remote half, owner step.** Eleven remote branches are contained in `main`: the eight listed above plus `claude/critique-ledger-round1-20261117`, `claude/critique-ledger-round5-20261117` and `claude/orchestration-thread-closeout-20261117`. The API, git and browser routes were each refused for this session. The owner deletes them on GitHub's Branches page.
- **E07, owner step.** The mirror's LFS store is 43 GB. The laptop answers on the file-sharing port (SMB, 445) from the Mac and on nothing else tested, so the copy needs the owner's Windows sign-in. The owner connects to `smb://gjs-laptop.local` in Finder and copies the mirror and the private production selection into the laptop's `murderbird-uncaged-archives` folder, then spot-checks a few LFS object hashes on the laptop.
- **Cross-thread note.** The Copilot-extraction thread's overkill-hill closeout commit (`dfab7e30`, local branch `docs/murderbird-copilot-thread-closeout-2026-11-18`) is not in the Mac's overkill-hill mirror and not on GitHub. It is on the laptop. The owner pushes it from there, or links the laptop so a session can bundle it and push over HTTPS.
