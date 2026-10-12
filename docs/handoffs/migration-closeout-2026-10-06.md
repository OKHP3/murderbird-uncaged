# MurderBird migration closeout — October 6, 2026

This is a dated addendum to the [ASUS migration verification](../asus-migration-verification-2026-09-26.md). The owner requested a retry, learning from the earlier failure, and archival only after this thread's delivery is verified on GitHub, Replit and Notion. The current shared goal was reviewed at `5ea85843593706ae0c0efcf1ec00e417c6b1dedb`; its later cinematic and delegation work remains a separate scope.

## Preserved work and fresh local checks

- Uncaged PR11 (`37a6a8130b63925b742564b48fa3c92971328875`), website PR122 (`c380ff599ab4424aa6c098440bb9315dac16db03`) and FoundRy PR46 (`6d48317fece4769dd8cb5e774779ad646def461b`) remain ancestors of their respective fetched `origin/main` revisions.
- All three ASUS mirrors were clean and equal to fetched main: Uncaged `5ea85843593706ae0c0efcf1ec00e417c6b1dedb`, website `de6a1a0f4f74f153cdae414a7f2eb24d26d2038b`, FoundRy `6a502342ec30418277e78600f6cee9b3ce8d40c7`.
- `python scripts/verify-media-import.py` passed 768/768 current entries, including the original 404 public imports. The original ledgers and source paths remain unchanged.
- The private ASUS snapshot passed 387/387 size/hash comparisons; the private export snapshot passed 4/4. Both destinations remain Git-ignored. No private archive was staged or uploaded.
- The website's targeted private-music release tests passed: ordinary-file exclusion passed; the symlink case correctly skipped for Windows privilege error 1314. A broader rerun was stopped without a completion claim after prolonged workspace-copy work. Only this task's identified processes were stopped. No source correction was needed.

## Cross-system evidence before this documentation commit

Uncaged's exact-main validation [37551448753](https://github.com/OKHP3/murderbird-uncaged/actions/runs/37551448753) and Pages deployment [37551448787](https://github.com/OKHP3/murderbird-uncaged/actions/runs/37551448787) passed. A fresh public release manifest identified clean revision `5ea85843593706ae0c0efcf1ec00e417c6b1dedb` and 154 payloads. These observations establish delivery, not artistic acceptance.

Signed-in Replit browser Shell checks, with Free mode visible, showed:

| Surface | Observed state |
|---|---|
| Uncaged active root | Clean `codex/pet-closeout-main-20261006`, tracking origin/main, exact `5ea85843`, 0 ahead / 0 behind. The old main and its 17 unique commits remain preserved separately. |
| Uncaged isolated preview | Clean main at exact `5ea85843`, 0/0. The stopped port 3000 server was restarted from its existing same-SHA build; the served manifest identified that clean SHA and 154 payloads. |
| Website | Contains current upstream `de6a1a0f` and the original migration/test changes; six later local commits and unrelated in-progress foundation edits belong to its active Replit task. No checkout, staging, reset or merge was performed there. |
| FoundRy | Clean main equal to `6a502342`, 0/0; the MurderBird routing change is present. |

The Replit APIs still require reauthentication. Browser Shell evidence is independent of connector authorization. Replit remains a development preview; no paid Agent work or Replit publication occurred.

## Retry corrections and lessons

1. Refresh the current shared goal, Git refs and live destination before reusing an old failure report. Another completed task had already preserved the legacy Replit history and aligned its active checkout; repeating the old divergence diagnosis would have been wrong.
2. Verify asset bytes separately from Git identity. The isolated preview initially passed only 137/404 original-import checks because 267 files were LFS pointers. The active root had the original binaries. The repair verifies source hashes and same Git revision before replacing only those pointers with exact copies; final verification must pass both ledgers in both checkouts.
3. Starting a preview can automatically edit `.replit`. Preserve that exact generated configuration locally and revert only the proven added port block; do not discard unrelated work or commit incidental platform edits.
4. Keep execution handles when a test yields. Poll the existing invocation rather than starting duplicates. Use the two relevant release tests for this documentation closeout instead of repeatedly copying the entire website workspace.
5. Treat current model acceptance, later delegation work and unrelated active website edits separately from this migration's closure. The published story stays on the website, production provenance stays here, and FoundRy stays a routing/incubation surface.

## Final closeout gate

This handoff records the pre-merge evidence. Its own PR must pass required checks and merge to main; then fast-forward both Uncaged Replit checkouts, refresh the same-SHA preview manifest and verify the final Pages run. Append and read back the final receipt on the existing Notion production and architect pages, preserving their historical records. Archive this migration thread only after those checks succeed. Do not infer completion of source likeness, owner acceptance, strict-normal diagnosis or the broader delegation program.

There is no active native goal token budget on this migration thread. No platform quota or billing limit was changed. The private final receipt records the actual final SHA and surface observations without creating a self-referential commit claim.
