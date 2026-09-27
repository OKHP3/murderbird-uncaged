# MurderBird: Uncaged

An interactive teardown of **The MurderBird**: turn it, inspect its mechanisms, and watch it choose. The exhibit follows three eras of construction and repair. It is a science-museum-style construction study, not a chase scene.

## What belongs here

This repository is the canonical home for MurderBird creative production and the interactive exhibit application: source images and video, music and lyrics, story-source snapshots, production files, models, and the app. The published MurderBird story and its page shells remain on [overkillhill.com](https://overkillhill.com/writings/murderbird/), along with stable assets needed by that website. This repository preserves versioned story-source snapshots and production provenance; a snapshot does not replace the published page.

FoundRy routes and incubates separate work. Accepted MurderBird production material belongs in this repository at the paths described in [the repository boundaries](docs/repository-boundaries.md).

## Exhibit status

The current local direction gives the same flightless MurderBird three distinct movement systems: **Maker** stays anchored while an operator articulates its joints; **Mechanic** uses a slow, limited wound-spring sequence; **Advanced** (the retained `builder` key) has coordinated movement, a controlled jump, a planted shield thrust and an effectively inexhaustible fictional encounter supply, with power separate from sensing and processing. The controls and mechanism geometry are proposed exhibit reconstructions, not established historical construction or accepted likeness. The Three.js behavior is procedural over the existing rigid presence-study GLB; that export itself is unchanged. The [three-era movement review](docs/three-era-movement-review.md) records the passing local checks, and the [review page](assets/audit/three-era-review/era-review.html) contains the continuous browser demonstration. Earlier [Stage Two review evidence](docs/stage-two-encounter-review.md) records its dated Builder-only checkpoint and does not verify this new direction. See the [recorded construction direction](docs/three-era-construction-direction.md), [requirements](docs/uncaged-requirements.md), [creative authority](docs/creative-authority.md), and [production handoff](docs/production-handoff.md). Owner likeness acceptance, accessibility review, and publication remain pending. The accepted Iron Verdict theme remains visitor-controlled. Imported material retains its recorded status and provenance.

## Getting started

```sh
npm ci
npm run dev
```

## Stack and release

This repository is a static client-side Vite and Three.js app with no backend or secrets. The OverKill Hill public website is a separate generated static-HTML site; it does not use this repository's Vite pipeline.

See the [technology inventory and update plan](docs/technology-stack.md) and [version table](docs/technology-versions.md) for the app's toolchain. Refresh the inventory with `npm run technology:report` and check it with `npm run technology:check`.

GitHub Actions builds the app for GitHub Pages from `main`. The current deployment workflow is in `.github/workflows/deploy.yml`; the validated build command is `npm run build`. Replit is for development preview only, not application publishing. See [replit.md](replit.md) for synchronization boundaries and the current connector limitation.

To inspect a local production build, run `npm run build` followed by `npm run preview`.

Files under `public/` are copied into the distributable. Put only release-approved, browser-delivered files there. Source archives, production sessions, private material, and provenance records are not deployment inputs and must never be placed under `public/`.

## Media and story material

Start with the [media catalog](docs/media-catalog.md), the
[migration record](docs/migration-2026-09-26.md), and the
[Replit handoff](docs/replit-media-handoff.md). Verify the imported public
collection with `python3 scripts/verify-media-import.py`.

The [ASUS verification addendum](docs/asus-migration-verification-2026-09-26.md)
records the Windows byte-preservation repair, additional Skillz imagery, and
machine-specific archive and synchronization evidence.

Use [assets/README.md](assets/README.md) for the media map and [docs/repository-boundaries.md](docs/repository-boundaries.md) for source, publication, and provenance rules. Keep imported source trees intact under `assets/murderbird/` and existing image paths under `assets/img/`; retain story snapshots under `content/story/`; record custody and relationships in `provenance/`. Imported scripts, tests, and configuration from the website belong under `provenance/website-support/`, where they cannot be mistaken for active app tooling. Private local music-session archives belong at `.local/archives/music-session-2026-09-17/` only after that path is confirmed ignored by Git.

## License

This project has a split license; see [NOTICE.md](NOTICE.md):

- **Code** is MIT licensed; see [LICENSE](LICENSE).
- **The MurderBird itself**, including its name, character, story, art, models, and music, is all rights reserved and is not covered by the MIT grant.

## Repository map

```text
src/                         interactive application source
public/                      approved files copied into the website build
assets/murderbird/            preserved MurderBird source and production hierarchy
assets/img/                   source-relative and website-related image paths
assets/audio/                 organized audio delivery and production material
assets/images/                organized image material
assets/models/                organized 3D models and exports
content/story/                versioned story-source snapshots
provenance/                   migration and asset provenance ledgers
.local/archives/              private local archives; must be Git-ignored
docs/                         exhibit and repository guidance
```

The established public story remains at [overkillhill.com/writings/murderbird](https://overkillhill.com/writings/murderbird/).
