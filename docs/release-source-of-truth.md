# Release source of truth

`OKHP3/murderbird-uncaged` **main** is the integration source. GitHub Pages is the public host. The exhibit, folio, review gallery, icons, and sharing metadata ship together from one Actions artifact. Replit is a development preview and does not publish this application.

## Verify a release

1. Read `release.json` from the public site and record its full `revision`.
2. Verify the Pages deployment run succeeded for that exact revision, not merely for a preceding commit.
3. Compare the served files with the manifest's byte counts and SHA-256 hashes. It covers every emitted file except the manifest itself.
4. Check the WebGL exhibit, illustrated fallback, folio, and review gallery in the browser. Hash parity alone does not establish usable interactions.
5. Keep technical publication status separate from artistic acceptance.

Local builds record whether tracked or untracked changes existed at build time. CI release builds must be clean. The manifest contains only public output paths and hashes, never local filesystem paths or archive inventories.

For local boundary checks, `scripts/verify-publication.mjs` reads the emitted manifest's current path inventory, verifies each listed file's byte count and hash, and checks the active exhibit model and three era previews against the current model inventory's recorded hashes. Historical review media is checked by its separate pinned inventory. The retired exterior-v1 validator's former fixed checkpoint count is not a current release requirement.

## September 27 reconciliation

Baseline `96514f4a9264dce4de4fde746385a7439b4cb587` integrated the exterior assessment, runtime, folio, and authorized gallery through PR #12. Both inspected Mac checkouts were clean at that revision.

| Historical branch | Verified disposition |
| --- | --- |
| `codex/murderbird-asset-migration` at `8c4f87c1f0e6f699b7a3f977fb0b8f39f1a76500` | PR #10 merged; complete tree equals merge result `ba2bae23acdc4e08446d1a4430f950d9dc7c40cf`. |
| `codex/murderbird-asus-migration-verification-20260926` at `6e2fcb49a66db3edfacf7595d44fdba38525a259` | PR #11 merged; complete tree equals merge result `37a6a8130b63925b742564b48fa3c92971328875`. |
| `codex/uncaged-vertical-slice` at `6042b5da8282429d3e12febf59dbcceaaad7442c` | Reachable from the integrated baseline through subsequent production history. |
| `codex/uncaged-production-review` at `6852dcaf25446b5d9685c77ec0c6c2cfc5c2a215` | PR #12 merged; reachable from baseline. |

Before cleanup, all local/remote branch tips and 18 otherwise unreachable historical commits were preserved under local `refs/archive/2026-09-27-reconciliation/`, with an ignored local recovery bundle. These are recovery records, not alternate deployment branches. No history rewrite, source deletion, or private-archive publication is part of consolidation.

Delete redundant remote branches only with an expected-tip check, after preserving them and confirming their disposition. Do not remove a branch advanced by concurrent work. Keep an active development checkout available; retire worktrees only when no task or process needs them.

## Presentation maintenance

The icon package reuses the existing MurderBird head derivatives; original files and generation history remain intact. The sharing card is a native SVG composition using the preserved full-body reference. It is labeled reference art and does not imply that the interactive model has passed likeness review.

Rebuild it with an existing authoring installation of `sharp`:

```sh
node scripts/build-brand-assets.mjs /absolute/path/to/sharp
node scripts/verify-presentation.mjs
```

No application dependency is added. See `provenance/presentation-package-2026-09-27.json` for exact inputs and outputs. `public/repository-social-preview.png` is the GitHub Settings social card; `public/og-image.png` is the web sharing card. The manifest, Apple icon, browser favicons, Windows tile, and Safari pinned-tab silhouette are updated together.

An existing OS-installed shortcut may retain its old cached icon until the operating system refreshes it or the user reinstalls that shortcut. Publishing the package does not prove every external cache has refreshed.

## Scope limits

This reconciliation covers GitHub and the two inspected Mac checkouts. It does not certify a Windows or Replit checkout that has not been inspected. Historical story and review snapshots stay immutable and are labeled separately from the live runtime.
