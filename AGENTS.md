# MurderBird: Uncaged Agent Guidance

These instructions govern work in this repository only. They do not replace or modify OverKill Hill P³ universal governance. Read [the repository boundaries](docs/repository-boundaries.md), [the asset guide](assets/README.md), and [NOTICE.md](NOTICE.md) before migrating or publishing MurderBird material.

## Repository roles

- This repository is the canonical home for MurderBird creative production and the interactive exhibit application, including source imagery, video, music, lyrics, story-source snapshots, production material, models, and app code.
- The OverKill Hill website retains the published MurderBird story, its page shells, and stable deployment assets. Preserve a source snapshot here when required for production provenance; identify its published URL and source revision. Do not imply a local snapshot is the live page.
- FoundRy routes and incubates separate work. Route accepted MurderBird production material to this repository; do not treat a FoundRy copy as the canonical production archive.
- Imported website scripts, tests, and configuration belong under `provenance/website-support/`. They are historical reference material, not active exhibit tooling.

## Preservation and provenance

- Keep imported trees under their established paths, including `assets/murderbird/` and `assets/img/`. Preserve original relative paths, names, nesting, metadata, and companion files. Do not flatten, normalize, or overwrite historical source files as part of import.
- Keep story-source snapshots under `content/story/`. Record the canonical published URL, source repository and revision or retrieval date, file hashes, and known rights/status in the matching `provenance/` ledger. Do not silently replace an earlier snapshot.
- Keep imported historical support material in its source-relative location when that preserves references. Use `provenance/website-support/` for copied scripts, tests, and configuration so they cannot be mistaken for the active Vite app.
- Record facts from the files and source system. Mark unknown provenance, licensing, production status, and technical dependencies as unknown; do not infer them from names, dates, or appearance.
- Preserve the source's draft, working, and final labels. The exterior-v1 three-era model is an implemented review study; owner likeness acceptance remains pending, and it is not validated engineering. The owner-accepted Iron Verdict v3 is a synthesized sung performance; no human vocalist recording is claimed. Keep its release status distinct from historical instrumental/GarageBand material and the optional soundscape. Do not upgrade any other asset's status without supporting evidence.

## Privacy, licensing, and publication

- The MurderBird character, story, art, models, music, and related creative content are all rights reserved under `NOTICE.md`; the MIT license applies to code. Do not imply that a source or migration makes creative material open licensed.
- Private local archives belong under `.local/archives/`, including `music-session-2026-09-17/`. Before copying files there, confirm the path is Git-ignored. Never stage, commit, upload, or publish a private session archive.
- Never put provenance ledgers, source archives, production sessions, private material, or imported historical support files under `public/`. Vite copies `public/` into the website build. Browser use of any other file must be explicit in application code.
- Before a release, build with `npm run build` and inspect `dist/` to verify that only intended, approved runtime files are included. A local build does not prove a successful GitHub Pages deployment; verify the exact deployment run and SHA for publication claims.
- Replit is a development preview only. Do not publish this application through Replit. Connector authorization and mirror state must be checked before claiming live remote synchronization.

## Changes and verification

- Preserve the existing Vite, Three.js, and Web Audio architecture. Do not add dependencies or turn this exhibit into a general publishing or backend application without a separately scoped request.
- Keep changes small and limited to the requested asset, story, or exhibit scope. Use lowercase kebab-case for new ordinary files and directories; retain tool-required names and established source paths.
- For app or asset-reference changes, run `npm ci` and `npm run build`. Review the emitted `dist/` paths and confirm referenced assets resolve. For scene changes, check both the WebGL scene and the illustrated fallback; see `.agents/memory/webgl-preview.md`.
- Report which files changed, what evidence supports their provenance and status, and which checks actually ran. Separate local verification from remote CI, deployment, and human acceptance.

## Project agent skills

See [.agents/skills/README.md](.agents/skills/README.md) for the seven installed Skillz workflows and their source provenance. Load the narrowest matching skill before using it. These workflows supplement this guide; they do not change creative authority, asset preservation, private archive, or publication boundaries.
