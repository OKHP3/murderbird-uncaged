# MurderBird migration record: September 26, 2026

## Scope and authority

The owner requested that all MurderBird creative resources and the interactive
application be collected in `OKHP3/murderbird-uncaged`, while the primary
website remains the public brand, portfolio, and story publication. This
supersedes earlier advice to keep creative production in the website repo.
Three GPT-6 Luna workers supported inventory, repository guidance, and
independent review; the orchestrator performed the transfers and integration.

## Verified local transfer

| Collection | Entries | Bytes |
|---|---:|---:|
| Imported public source files | 386 | 841,280,921 |
| Private/local files | 5375 | 1,577,979,608 |
| Private symlinks | 4 | Targets preserved without dereferencing |
| Recorded private directories | 646 | Structure preserved |

The [public manifest](../provenance/overkill-hill-import-2026-09-26.json)
records source commit `f1142a02f1e73cd45e46e981022aef27f1c6e095`, original and destination paths,
byte counts, and SHA-256 hashes. Every copied file was checked at transfer.
The private manifest is `.local/migration/private-import-2026-09-26.json` in
the owner's clone. No private archive was staged for Git or placed in the
browser delivery directory.

Public material preserves images and icon variants, 13 MP4 files including
the existing website clip, the Iron Verdict instrumental/native project/stems,
vocal-score v2 and performance sheet, the Blender scale proxy, story snapshots,
visual canon, and historical production/review records. Matching duplicate
source files remain separate where the original collection kept them.

## Source cleanup and compatibility

After checking source and destination against the recorded hashes or symlink
targets, 5,432 file/link entries were removed from these original website roots:

- `assets/murderbird/production/audio/`
- `assets/murderbird/production/video/`
- `assets/murderbird/.local/`
- `assets/downloads/music-session-2026-09-17/`

The local source-relocation receipt records every recoverable path. Git history
also preserves all removed tracked sources. Website story routes, delivery
images, public video, and the v2/image fixtures needed by existing build tests
remain in place. Those retained creative copies are documented compatibility
snapshots; new production belongs here.

The website release builder now explicitly rejects private music-session
archives under its downloads path, including files and symlinks. Its technology
inventory no longer treats the relocated audio-production dependencies as
website tooling. NumPy and FFmpeg remain represented for the existing motion
renderer.

## Checks and evidence limits

- Public import and private import hashes and symlink targets verified.
- Exhibit dependency installation and production build passed. The build had
  19 files, about 4.5 MB, and no production, provenance, private archive, or
  story-source snapshot directories. A pre-existing bundle-size warning remains.
- Website release-package tests passed: 13 tests, one skipped.
- Website technology-inventory tests passed: 20 tests.
- Website structure, generated HTML/search freshness, and internal links passed.
  Existing locale metadata and reviewed voice warnings remain unchanged.
- FoundRy documentation links and whitespace passed review.

Original source files keep their bytes and historical names. Some use CRLF,
Markdown hard breaks, or old absolute workstation paths. Those are preservation
exceptions, not newly authored formatting or evidence that the old tools run
unchanged. Check whitespace in newly authored files separately.

Both Replit connectors require reauthentication. The Replit desktop app was
accessible, and a fresh fetch showed a clean MurderBird `main` at
`74c0705883cfdbdb657707bf93fccd215da36316`, matching GitHub before this migration.
That baseline check is distinct from integration of the migration itself.

The app's procedural model and synthesized soundscape remain its current
experience. A finished character rig, a recorded vocal performance, and a
curated integration of the transferred media remain separate production work.
See the [media catalog](media-catalog.md) and [Replit handoff](replit-media-handoff.md).

## Recovery

Restore tracked source paths from source commit
`f1142a02f1e73cd45e46e981022aef27f1c6e095` only if rollback is needed. Restore
private entries from their destination paths using the ignored migration
receipt after verifying the old path is vacant. Do not rewrite repository
history or remove destination copies during recovery.
