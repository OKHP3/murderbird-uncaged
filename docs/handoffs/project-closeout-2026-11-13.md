# MurderBird: Uncaged project closeout (v1.0)

Date: 2026-11-13 (America/Chicago)
Decision: frozen at v1.0 as a finished creative production and study. Likeness parked, not accepted.
Authority: owner direction of 2026-11-13 to drive every open MurderBird thread to completion and archival. Recorded in [goal.md](../../goal.md).

## What shipped

| Deliverable | Where | Status |
|---|---|---|
| Interactive exhibit (V37 foundation, three eras) | https://okhp3.github.io/murderbird-uncaged/ | Live. Deployed revision `914956e` (Oct 23). |
| Static CG assessment | https://okhp3.github.io/murderbird-uncaged/cg.html | Live. Labeled under assessment. |
| Story and media folio | https://okhp3.github.io/murderbird-uncaged/folio.html | Live. |
| Origin story, "What the Water Kept" | https://overkillhill.com/writings/murderbird/ | Live on the OverKill Hill site. |
| Theme song, Iron Verdict v3 | Exhibit audio, `assets/` sources | Owner-accepted synthesized sung performance. |
| Editable sources, exports, audit evidence | This repository (Git LFS) | Preserved. |

## What did not ship

Whole-bird source likeness against the pinned references is **UNMET** and owner artistic acceptance is **not given**. The October 2 to November 12 reviews found the modeling effort had optimized for engineering and manufacturability rather than screen likeness. A future likeness effort should be a new, separately authorized project that starts from a VFX hero-asset approach: silhouette and proportion first (short, heavy neck; low head; short hooked bill), a shingle-layered breast over a dark under-body, and fine detail in normal and displacement maps instead of modeled parts.

## Repository state at closeout

- `main`: `53069474` (2026-11-10). The eight commits after the deployed revision are CI and LFS plumbing; the exhibit content matches.
- Validate build: fails on `main` and every open branch at "Hydrate verified required assets." This is the documented cold-cache guard, not a code defect. GitHub currently reports that **the repository has exceeded its LFS budget**, so no cache fill or republication is possible until the owner restores allowance. None is authorized by this closeout.
- Open pull requests at closeout, all closed unmerged with branches kept. Each head also stays reachable as `refs/pull/<n>/head`.

| PR | Branch | Disposition |
|---|---|---|
| #83 | `codex/asus-visual-technical-acceptance` | Closed: preserved study, out of v1.0 scope |
| #84 | `codex/mac-completion-coordination-20261026` | Closed: portability tooling, cannot be validated while CI is cold |
| #86 | `dependabot/npm_and_yarn/three-0.187.0` | Closed: renderer bump on a frozen exhibit |
| #87 | `dependabot/github_actions/actions/cache/save-6.1.0` | Closed: frozen |
| #88 | `dependabot/github_actions/actions/cache/restore-6.1.0` | Closed: frozen |
| #89 | `dependabot/npm_and_yarn/vite-8.3.6` | Closed: frozen |
| #90 | `codex/simultaneous-contact-report-dedup` | Closed: verification tooling, out of scope |
| #91 | `codex/foot-motion-png-evidence-validator` | Closed: verification tooling, out of scope |
| #92 | `codex/archived-timing-diagnostics` | Closed: verification tooling, out of scope |

- Issue #14 (shared cinematic goal commentary): closed, pointing here.
- No GitHub release existed before closeout. Tag `v1.0.0` marks the closeout merge.

## Preservation

- The owner's local mirror holds the hydrated working tree and roughly 43 GB of LFS objects. Until an off-machine copy exists, it is the only verified complete copy outside GitHub. Copy it to separate storage before any repository archival or LFS cleanup.
- LinkedIn series media regenerated from repository originals lives in the mirror's ignored `.local/linkedin-media-2026-11/` folder and is not published here.

## Remaining owner actions

1. Restore LFS allowance only if a republish is ever wanted; nothing in v1.0 requires it.
2. Back up the local mirror to separate storage.
3. Optionally archive this GitHub repository after the LinkedIn series runs. Pages keeps serving from an archived repository; confirm after archiving.
4. Archive the related assistant threads once their contents are confirmed preserved.
