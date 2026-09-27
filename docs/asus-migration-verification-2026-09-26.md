# ASUS migration verification, September 26, 2026

This follow-up reconciles the ASUS clones with the migration already merged
in [Uncaged PR 10](https://github.com/OKHP3/murderbird-uncaged/pull/10),
[website PR 121](https://github.com/OKHP3/overkill-hill/pull/121), and
[FoundRy PR 46](https://github.com/OKHP3/overkill-hill-foundry/pull/46).
Three GPT-6 Luna workers inspected source coverage, related repositories,
and destination integrity. The orchestrator integrated and reviewed their work.

## Additional preservation

- The original import contains 386 public source files, 841,280,921 bytes.
  All LFS objects were retrieved on ASUS. Every imported file now matches
  its recorded SHA-256 digest.
- The wider search found 18 additional MurderBird delivery images in Skillz,
  totaling 1,220,695 bytes. The [separate ledger](../provenance/skillz-import-2026-09-26.json)
  records their origin and hashes. Their active Skillz copies remain in place.
  They retain an unknown underlying generation lineage and are not newly
  approved exhibit inputs.
- ASUS-only creative captures and review material (387 files, 135,281,661 bytes)
  and four related export snapshots/notes (50,608 bytes) are preserved under
  ignored `.local/archives/` paths. Private receipts under `.local/migration/`
  and the export archive's `manifest.json` record the files and hashes. These archives are not in Git,
  GitHub Pages, or Replit. The source copies remain available for recovery.
- The earlier private Mac archive described in the [original migration record](migration-2026-09-26.md)
  is machine-local. This ASUS verification does not claim to have retrieved or
  reverified it.

The scoped searches covered the three named repositories, related MurderBird
paths and references in adjacent clones, and relevant local ChatGPT exports.
Tracked source candidates in the website all had entries in the original
import ledger. FoundRy contained routing/context references rather than an
additional production collection. Historical branches, stashes, and Git history
were preserved. Unidentified files in other applications or machines remain
outside this verification.

## Windows preservation repair

Windows Git had converted four imported provenance/canon text files to CRLF.
Their content was readable, but their bytes no longer matched the source
manifest. The files were restored from their existing Git blobs; their source
hashes were not changed.

`.gitattributes` now disables text conversion for all imported asset paths and
the remaining individual snapshot paths. AVIF source images use the existing
LFS storage policy. The import verifier checks both byte identity and effective
Git `text=unset` attributes, so a Linux CI run can also detect a future Windows
checkout regression. By default it checks every `provenance/*-import-*.json`
ledger. `--manifest` limits verification to an explicitly selected ledger.

Verification passed for all 404 public import entries. A temporary attribute
override to `text=auto` made the checker fail as expected; the override was
removed. `npm ci` and `npm run build` passed. The resulting 19-file build was
4,485,072 bytes and contained no imported production archives, provenance,
private files, or story snapshots. Current catalog/navigation links resolved.
The existing JavaScript bundle-size warning remains.

## Repository and publication boundaries

The ASUS website clone was fast-forwarded to
`d9a59d6bca4f4b4f5e9e88cf78a077a6b6c2ab5e`; its relocated production audio and
video directories are absent. The FoundRy clone was fast-forwarded to
`6d48317fece4769dd8cb5e774779ad646def461b`. Both were clean and matched
`origin/main` after integration. An old empty website index lock was preserved
locally after confirming no Git process was running, allowing the fast-forward.

The website retains its editorial story, stable public media paths, and
documented compatibility snapshots required by existing tooling. New creative
production belongs here. This migration does not rewrite the website's Git
history, remove its mascot, or make the two applications share a build system.

Live HTTP checks returned 200 for the story, its ten directly referenced
MurderBird media files, and the Uncaged entry page. The website Pages run
[36281357135](https://github.com/OKHP3/overkill-hill/actions/runs/36281357135)
deployed the website migration revision. These are delivery checks, not a new
visual or artistic acceptance review.

Replit's workspace shell and Git panels remained at loading state after a
reload. No new Replit commit, checkout parity, LFS transfer, or connector
authentication is claimed. Follow [the Replit handoff](replit-media-handoff.md)
once the workspace is responsive.

The current exhibit still uses its procedural model and synthesized audio.
Curating the transferred images, video, music, and lyrics into its interactive
experience remains implementation work. A finished character rig and recorded
vocals are not established by the migration.
