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
| Assess the project and plan a course to completion | Done November 11. Executed through other threads: v1.0 closeout and tag (November 13), Living Plates and v1.1.0 (November 14 and 15), the website project page update, and the November 16 Codex audit and execution register (E01 to E19, kept in the owner's Notion workspace). |
| End with archival of this thread and the project's other threads | Owner action. Threads are archived in each app. This ledger, the v1.0 closeout and the November 16 register are the records to keep. |

## Housekeeping done in this change

- Corrected the bill guidance in [project-closeout-2026-11-13.md](project-closeout-2026-11-13.md).
- Paused Dependabot version-update PRs (`open-pull-requests-limit: 0`) on the frozen repository. Security alerts are unaffected. Dependency PR #95 (vite 8.3.8) is closed unmerged on the same grounds as #89.
- Deleted the four remote branches already contained in `main`: `claude/living-plates-20261114`, `claude/v1-closeout-20261113`, `codex/lfs-cache-preflight-20261029` and `codex/lfs-download-repair-20261026`. Their commits stay reachable through `main` and the merged pull requests. Register item E11's local Mac branch and paused automation still need host access.
- Register item E10 (links from the exhibit and folio to Living Plates, and sitemap entries) is handled in a separate pull request.

## Still open, and why

Each item needs owner access or owner judgment. None of them blocks archiving the threads.

| Item | Blocker |
|---|---|
| Independent backup of the local mirror and private production (E07) | Needs an owned destination with roughly 75 GB or more free |
| ASUS clone and four historical Git histories (E08) | Host access |
| Replit checkout state (E09) | Authenticated workspace |
| Native Blender editability and strict normal replay (E04, E15) | A desktop Blender session |
| Human device, listening and screen-reader checks (E12) | A person and hardware |
| TRELLIS result recovery (E13), promo reel disposition (E14), CRT source attachments (E18) | Original sessions and an editorial call |
| Full standard Pages republish | LFS budget restored. The live base stays `914956e` with the Living Plates overlay. |
| Final model likeness (E16) | Parked by owner decision. It needs a new, separately authorized project. |
