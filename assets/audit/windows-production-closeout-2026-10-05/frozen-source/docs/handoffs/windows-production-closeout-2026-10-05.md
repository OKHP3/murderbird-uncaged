# MurderBird Windows production closeout — October 5, 2026

Source host: owner Windows / Codex. This dated continuation preserves the October 4 production and architect handoffs and their exact review records.

The owner requested delivery of all improvements to GitHub production, the Replit development preview and Notion, followed by five review passes against the prior handoff and PRD. Initial read-only inspection found clean Windows main 31 commits behind GitHub. It was fast-forwarded to `ca675a828bb968ed941e24e06e7fc30505ce2d25`. There were no uncommitted creative improvements here. Prior retained04 delivery and detailed reviews are already integrated; branch studies and preserved Replit-only commits are not automatically accepted improvements.

## New defect and bounded repair

Fresh Windows `npm ci` passed, but the first build emitted 58 payloads rather than 154. The direct-entry guard in `scripts/prepare-cg-release.mjs` did not recognize Windows path separators and silently skipped the 96-file CG allowlist. Publication validation correctly failed. Windows CRLF checkout conversion also broke pinned runtime lyric/SVG hashes and changed the three emitted HTML hashes.

The repair compares resolved native paths with `fileURLToPath(import.meta.url)` and sets LF checkout attributes only for release text and the three active HTML entries. Clean tracked text files were restored to their canonical Git bytes. Imported creative source trees and pinned hashes remain unchanged. No dependencies, models, source references or visitor interactions change.

Local results after repair: build emits all 154 payloads; publication, theme and presentation checks pass; 79 tests pass; media-import custody verifies 768/768 entries. A subsequent HTML-line-ending correction makes all 154 local manifest payload entries equal the current Pages manifest. Local modified-tree metadata is not a deployment receipt. The standard Vite large-chunk warning remains; hardware performance and full PRD acceptance are not established by these checks.

## Initial surface inspection

GitHub main and Pages release are clean at `ca675a82`; main validation `37251028357` and Pages deployment `37251028354` succeeded. The existing Notion continuation and architect task page identify that same revision and contain the 62-task roadmap.

Both Replit connectors return reauthentication required. Direct signed-in browser shell inspection confirms the isolated preview checkout and port 3000 served manifest are clean at that exact revision, with 154 payloads. Parent main remains at `0d7366d8e8924cacebf48b19a0a0dbb27bd0b673`, with 17 local-only commits; its previously fetched origin is stale. Preserve this parent and all old work. Synchronize only the clean isolated preview by fast-forward. Replit is Free mode only and is never a publication destination.

## Next action and limits

Commit the narrow repair through a checked PR, verify its exact Pages deployment and live bytes, fast-forward and rebuild the isolated Replit preview without touching its parent, and append a dated Notion receipt. Only then freeze the delivered release, prior Loop03/production/architect handoffs, current goal, PRD and task ledger for the requested five-pass review. Save independent role findings, conditional falsification and root adjudication with explicit analytical limits.

Source likeness remains UNMET, owner artistic acceptance PENDING, strict normal parity FAIL with cause unresolved. New CG motion, mechanics, physical-device acceptance and monitoring readiness remain open or conditional. No new modeling phase begins under this delivery/review request.
