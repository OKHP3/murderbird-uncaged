# Repository boundaries and migration map

This note identifies which repository owns each kind of MurderBird material and how migrated files remain traceable without becoming accidental website inputs.

## Canonical roles

| Repository or path | Role |
|---|---|
| `murderbird-uncaged` | Canonical home for MurderBird creative production and its interactive Vite/Three.js exhibit, including images, video, music, lyrics, story-source snapshots, production files, and app code. |
| OverKill Hill public website | Published MurderBird story and page shells, plus stable assets required by that generated static-HTML site. A published page or asset may be represented here by a provenance-linked source snapshot, but this repository does not make that snapshot the live publication. |
| FoundRy | Routes and incubates separate work. It is not the canonical archive for accepted MurderBird production material. |
| Replit | Development preview only. It is not the production host or an independent authority for remote synchronization unless the exact remote state is verified. |

The OverKill Hill website is generated static HTML. It does not use this repository's Vite pipeline. Keep the two build and release boundaries distinct.

## Destination map

| Path | Purpose |
|---|---|
| `assets/murderbird/` | Preserved source and production hierarchy, including historical versions such as `v2/`, stills, and production branches. Keep source-relative paths intact. |
| `assets/img/` | Existing source-relative image paths and website-related image material. Preserve paths where HTML, CSS, or historical records refer to them. Do not create a parallel `assets/website-images/` tree. |
| `assets/audio/`, `assets/images/`, `assets/models/` | Existing placeholder organization areas for future app-facing or working copies. A `.gitkeep` is not evidence that finished assets exist. |
| `content/story/` | Versioned snapshots of story-source material used by the creative production. Keep the published canonical URL and source revision or retrieval date with each snapshot. |
| `provenance/` | Migration manifests and ledgers that connect each imported file or tree to its origin, hash, status, and any derived copy. |
| `provenance/website-support/` | Imported website scripts, tests, and configuration retained for historical reference. Files here are not active app tooling. |
| `.local/archives/music-session-2026-09-17/` | Private local archive of the music session. It must be Git-ignored and remains local; never stage, commit, upload, or publish it. |
| `src/` | Active exhibit application code. Only deliberately integrated and reviewed code belongs here. |
| `public/` | Release-approved browser-delivered files. Vite copies this directory into the build output. |

Existing names and links have evidentiary value. Prefer retaining source-relative paths over reorganizing files into a new taxonomy. If an app needs an optimized, renamed, or converted copy, preserve the source and record the relationship in a provenance ledger.

## Provenance ledger fields

For each imported tree or consequential file, record as available:

- original source repository, directory, or capture location;
- source commit, capture date, or retrieval date;
- original relative path and destination path;
- byte size and SHA-256 digest;
- file role and any relationship to other files;
- source-stated draft, working, or final status;
- rights or license evidence and any unresolved questions;
- transformations, derived files, and validation performed.

Use `unknown` or `not established` when the source does not support a value. A matching hash establishes byte identity, not ownership, license, artistic finality, or publication approval. Retain earlier source snapshots instead of overwriting them.

## Story snapshots

The public story remains on the OverKill Hill site at <https://overkillhill.com/writings/murderbird/>. A `content/story/` snapshot is a production reference with its own provenance, not a route or a claim that the website currently serves that exact revision. Preserve source text and metadata as captured, link the ledger entry, and record differences if a later published revision is compared.

## Publication boundary

The Vite build copies `public/` into `dist/`; source or archive files elsewhere are not automatically public merely because they are tracked. However, imported files may still enter the output if application code references them. Before publishing a change, run the repository build and inspect the complete `dist/` file list and referenced URLs. Keep provenance, private archives, historical support code, and production sessions out of both `public/` and the emitted output.

Git LFS patterns are configured for supported binary types in `.gitattributes`. Verify LFS object availability from a clean remote checkout before treating a pointer as a deployable asset. A local copy, Git pointer, successful build, or configured workflow alone does not prove that visitors can retrieve the media.

## Remote evidence

The Replit connectors for both relevant accounts were reported **UNAUTHORIZED** for this migration on 2026-09-26. The Replit desktop app was accessible. A fresh fetch there showed a clean `main` equal to GitHub `main` at `74c0705883cfdbdb657707bf93fccd215da36316` before migration. This establishes baseline parity, not delivery of this migration branch. Keep claims bounded to inspected evidence, and verify GitHub, Replit, CI, Pages, and local mirror state separately when a task depends on them.
