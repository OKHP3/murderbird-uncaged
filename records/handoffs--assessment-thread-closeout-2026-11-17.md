# Assessment and completion-plan thread (November 13): closeout ledger

Date: 2026-11-17 (America/Chicago). Base reviewed: `main` at `859983d`.
Thread: the Claude thread that, on November 13, assessed the repository, live exhibit and site pages, recommended closing at v1.0 with likeness stated as a known gap, and asked for every thread in the project to be archived. The same thread opened with an unrelated request to update the owner's music preferences from an Apple Music playlist.

This ledger checks each action that thread asked for or recommended against what now exists. It adds no modeling, no publication and no artistic acceptance. The [visual critique ledger](handoffs--visual-critique-thread-closeout-2026-11-17.md) covers the overlapping November 11 plan and the November 16 register, and the [orchestration ledger](handoffs--orchestration-thread-closeout-2026-11-17.md) covers the cross-thread wrap-up. This file does not repeat either.

## Requests and their dispositions

| Request or recommended action | Disposition | Evidence |
|---|---|---|
| Update the owner's music taste from the "Jamie Standard" Apple Music playlist | Done on November 13 in the owner's private memory, from the playlist's featured artists. The public page exposes only featured artists, not the full 79-track list. | Private memory, not this repository |
| Owner decides whether V37 ships with likeness gaps stated | Done. The owner closed the study at v1.0 with likeness parked, not accepted. | [project-closeout-2026-11-13.md](handoffs--project-closeout-2026-11-13.md), `goal.md` status |
| Stop agent threads, then triage the nine open PRs and issue #14 | Done. All nine closed unmerged with branches kept; issue #14 closed November 13. On November 17 the REST API returns zero open PRs and zero open issues. Dependabot version updates are paused. | `.github/dependabot.yml` `open-pull-requests-limit: 0` |
| Same-camera side-by-side gate and a logged owner decision | Superseded by the owner's direct v1.0 decision, then by the November 14 Living Plates authorization. | `goal.md`, [living-plates.md](living-plates.md) |
| Truth-sync the README, project page, share card and Era III naming | Done. The README and `goal.md` carry the v1.0 and v1.1 status. The OverKill Hill project page states "Original study complete at v1.0; Living Plates added in v1.1; final model likeness parked" and has its own 1200x630 share card. Its "Delivery: unknown" line is deliberate: the site's `scripts/project-status.py` hard-codes it because a source review cannot certify runtime delivery. Era III naming needs no change: "The Builder" names the 2025 character in the story and "Advanced" names the exhibit era, as `creative-authority.md` records. | Live project page fetched November 17 |
| Stop agent instructions from pointing back into modeling | Done in this change. `CLAUDE.md` still repeated the September 29 incremental-likeness mandate, which contradicted the freeze in `AGENTS.md` and `goal.md`. It now points to the frozen status, and `records/incremental-delivery.md` carries a superseded notice above its unchanged historical text. | This commit |
| Tag `v1.0.0` and publish a GitHub release | Done, plus `v1.1.0` for Living Plates. Both releases were published November 15. | Tags `v1.0.0` (`be988a5f`), `v1.1.0` (`bda1ae31`) |
| Close the evaluation scorecard honestly | Superseded. The scorecard is the unchanged blank template that earlier handoffs say must not be overwritten. All 122 rows remain `NOT EVALUATED`, and no closeout text claims a score. | `records/murderbird-evaluation-scorecard.csv` |
| Harvest thread contents to Notion and a public closeout doc | Done. Public: the v1.0 receipt and the November 17 ledgers. Private: the November 16 audit and execution register in the owner's Notion workspace, last edited November 17. | `docs/handoffs/` |
| Archive the project's threads, this one last | Owner action in the Claude app. No assistant tool can archive a chat. Nothing in this ledger blocks it. | |

## Live state checked on November 17

- The exhibit, folio, Living Plates, `release.json` and the Iron Verdict audio return HTTP 200 from `okhp3.github.io/murderbird-uncaged`. Both OverKill Hill pages (project and story) return HTTP 200.
- The live base stays release `914956e` with the Living Plates overlay at `2c0603f7`.
- The Validate build workflow on `main` fails at "Hydrate verified required assets" on every run since November 17. That is the documented cold-cache guard while the repository is over its Git LFS budget, not a code defect. Documentation-only merges like this one do not change it.

## Still open

The [visual critique ledger](handoffs--visual-critique-thread-closeout-2026-11-17.md) keeps the single open-items list. As of `859983d` that list is: off-machine backup (E07), Replit checkout state (E09), the strict normal-parity FAIL kept for an owner call (E15), human device and listening checks (E12), TRELLIS, promo reel and CRT source items (E13, E14, E18), a full standard Pages republish once the LFS allowance is restored, and final model likeness (E16, parked). Each needs owner access or owner judgment.

One more owner step: eleven remote branches are fully contained in `main` and can be deleted from GitHub's Branches page. Earlier sessions found that branch deletion is refused for assistant sessions. The branches are the nine `claude/*` branches from November 13 to 17 and `codex/lfs-cache-preflight-20261029` and `codex/lfs-download-repair-20261026`. This change's own branch is the twelfth once merged.
