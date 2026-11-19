# MurderBird: Uncaged Agent Guidance

**Current shared goal:** read the root-level [goal.md](goal.md) before assigning, reviewing or starting work. Its YAML front matter records `last_updated`; use GitHub `main` for the latest shared revision. Cross-system review and commentary: [issue #14](https://github.com/OKHP3/murderbird-uncaged/issues/14).

**Project frozen (November 13, 2026).** MurderBird: Uncaged closed at v1.0 by owner direction, with likeness parked and not accepted. Do not open branches, pull requests or worker threads, and do not resume packets or milestones, without a new explicit owner authorization naming scope, budget and stop rule. See the closeout section at the top of [goal.md](goal.md).

These instructions govern work in this repository only. They do not replace or modify OverKill Hill P³ universal governance. Read [the repository boundaries](records/repository-boundaries.md), [the asset guide](records/README.md), and [NOTICE.md](NOTICE.md) before migrating or publishing MurderBird material.

## Repository roles

- This repository is the canonical home for MurderBird creative production and the interactive exhibit application, including source imagery, video, music, lyrics, story-source snapshots, production material, models, and app code.
- The OverKill Hill website retains the published MurderBird story, its page shells, and stable deployment assets. Preserve a source snapshot here when required for production provenance; identify its published URL and source revision. Do not imply a local snapshot is the live page.
- FoundRy routes and incubates separate work. Route accepted MurderBird production material to this repository; do not treat a FoundRy copy as the canonical production archive.
- Imported website scripts, tests, and configuration are kept as `records/website-support--*` files. They are historical reference material, not active exhibit tooling.

## Layout and preservation

- Keep the tree flat (flattened November 19, 2026). Shipped media goes in `media/` with descriptive lowercase names; records go in `records/` with a `group--name` prefix instead of subfolders. Do not recreate deep iteration trees (`v15/attempt-02/browser-<hash>/...`) on `main`.
- Every file in `media/` is pinned by `media/cg-publication.json`, `media/production-v37.json` or a `records/` ledger. Add a file only together with its manifest or ledger entry.
- Retired iterations, renders and study scripts are in Git history at tag `archive/pre-flatten-2026-11-19`; `records/flatten-map-2026-11-19.csv` maps every old path. Recover from there rather than re-importing.
- Record facts from the files and source system. Mark unknown provenance, licensing, production status, and technical dependencies as unknown; do not infer them from names, dates, or appearance.
- Preserve the source's draft, working, and final labels. The owner-accepted Iron Verdict v3 is a synthesized sung performance; no human vocalist recording is claimed. Do not upgrade any asset's status without supporting evidence.

## Privacy, licensing, and publication

- The MurderBird character, story, art, models, music, and related creative content are all rights reserved under `NOTICE.md`; the MIT license applies to code. Do not imply that a source or migration makes creative material open licensed.
- Private local archives belong under `.local/archives/`, including `music-session-2026-09-17/`. Before copying files there, confirm the path is Git-ignored. Never stage, commit, upload, or publish a private session archive.
- Never put provenance ledgers, source archives, production sessions, private material, or imported historical support files under `public/`. Vite copies `public/` into the website build. Browser use of any other file must be explicit in application code.
- Before a release, build with `npm run build` and inspect `dist/` to verify that only intended, approved runtime files are included. A local build does not prove a successful GitHub Pages deployment; verify the exact deployment run and SHA for publication claims.
- Replit is a development preview only. Do not publish this application through Replit. Connector authorization and mirror state must be checked before claiming live remote synchronization.
- Replit communication and execution must use **Free mode only**. Always decline Power or Max prompts. Never select, authorize, or recommend a paid-mode fallback or change billing. If Free mode cannot continue, preserve the checkpoint and report the actual limit. This explicit owner rule supersedes any skill's Free-first or escalation guidance.

## Changes and verification

- Use [the incremental delivery workflow](records/incremental-delivery.md) for short visual checkpoints, bounded parallel work, and confirmed remote synchronization.

- Preserve the existing Vite, Three.js, and Web Audio architecture. Do not add dependencies or turn this exhibit into a general publishing or backend application without a separately scoped request.
- Keep changes small and limited to the requested asset, story, or exhibit scope. Use lowercase kebab-case for new ordinary files and directories; retain tool-required names and established source paths.
- For app or asset-reference changes, run `npm ci` and `npm run build`. Review the emitted `dist/` paths and confirm referenced assets resolve. For scene changes, check both the WebGL scene and the illustrated fallback; see `.agents/memory/webgl-preview.md`.
- Report which files changed, what evidence supports their provenance and status, and which checks actually ran. Separate local verification from remote CI, deployment, and human acceptance.

## Project agent skills

See [.agents/skills/README.md](.agents/skills/README.md) for the seven installed Skillz workflows and their source provenance. Load the narrowest matching skill before using it. These workflows supplement this guide; they do not change creative authority, asset preservation, private archive, or publication boundaries.
