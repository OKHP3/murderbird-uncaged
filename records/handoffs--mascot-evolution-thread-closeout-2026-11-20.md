# Mascot evolution thread: closeout ledger

Date: 2026-11-20, landed 2026-11-22 (America/Chicago). Base reviewed: `main` at `f3c154e`; overkill-hill `main` at `c340596`.
Thread: the Claude thread that reviewed the manifesto, origin story and project page (October 25), drafted the "Forrest Gump" LinkedIn posts on MurderBird's evolution, mined the series angles, and produced the 2:28 Iron Verdict music video ([session](https://claude.ai/code/session_01XGoqf683ggwt21VrN6S1qg)).

This ledger checks every request the thread made against what now exists. It adds no modeling, no publication and no artistic acceptance, and it does not change the November 13 freeze. The November 20 session prepared it but could not push; the hub thread for this project committed it on November 22.

## Requests and disposition

| Requirement | Disposition |
|---|---|
| Review the manifesto, origin story and project page | Done October 25 from the GitHub source and the live pages. |
| LinkedIn posts on the mascot's evolution and tool stack | Done as drafts (the Run, the Leash, the Walk-On Song). Merged verbatim into the single seven-post series doc by the [orchestration thread](handoffs--orchestration-thread-closeout-2026-11-17.md). Publication is an owner action. |
| Count of posts at ~1,800 characters, media on at least three | Done: five angles, four with media. Superseded by the seven-post series and its media map. |
| Whether the series supports Forward Deployed Engineer positioning | Answered: it shows agent orchestration, budgets and provenance; evaluation frameworks and hands-on Python are the visible gaps, so the series closes on a deployment-playbook post that names evals as next work. Carried into the series doc. |
| LinkedIn video length limits | Answered from third-party spec pages (LinkedIn's own help page could not be fetched): about 15 minutes from desktop and 10 from mobile, so the 2:28 song fits. |
| Full-length MurderBird music video | Done: 2:28, 1080×1350, H.264/AAC, lyrics burned in, plus a title-card thumbnail. A verified copy is kept in the owner's private workspace. Not tracked here: promotional clips stay outside tracked files (goal.md, November 14). |
| Assess, plan, close out and archive the project's threads (November 20) | This ledger. Thread archiving is an owner action in each app. |

## Site findings raised by this thread

| Finding (October 25) | State on `main` today |
|---|---|
| Project page shared the story's share card | Resolved: its own `murderbird-uncaged-exhibit-share-1200x630.png`. |
| Hero status read "Delivery unverified" | Resolved: the hero now states v1.0 complete, v1.1 Living Plates, likeness parked. "Delivery: unknown" remains only in the site's standard status record. |
| Tool credits named GPT-5.6 SOL instead of the lead model | Resolved: the page credits Astra GPT-6 (`gpt-6-astra`), then `gpt-6.1-sol`. |
| Music credits described GarageBand as the composer | Not a site defect: the page already says original MIDI and synthesized parts, with ACE-Step 1.5 vocals. The early post draft was corrected to match. |
| Era III is "The Builder" in the story but "Advanced" in the exhibit | Kept as is. The story and the exhibit are separate canons, and the exhibit is frozen. |
| Project page `dateModified` and sitemap `lastmod` still read November 13 after the November 15 v1.1 update | Resolved 2026-11-23 by overkill-hill #265. Originally open: A source-level fix (`site-src/pages/projects/murderbird-uncaged/index.extras.html` and `sitemap.xml` to 2026-11-15, rebuild, CSP regeneration) passed every site gate on November 20 but was not pushed. Cosmetic; it does not block archiving. |

## Still open, and why

| Item | Owner | Next action |
|---|---|---|
| ~~overkill-hill project page date fix~~ | Resolved 2026-11-23 | Merged as overkill-hill [#265](https://github.com/OKHP3/overkill-hill/pull/265); see the [Copilot-extraction closeout](handoffs--copilot-extraction-thread-closeout-2026-11-23.md). |
| ~~Copilot-extraction (redesign context) closeout in overkill-hill~~ | Resolved 2026-11-23 | Merged as overkill-hill [#264](https://github.com/OKHP3/overkill-hill/pull/264). |
| Archive this thread and the project's other threads | Owner | Archive in each app. No assistant tool can archive threads. |
