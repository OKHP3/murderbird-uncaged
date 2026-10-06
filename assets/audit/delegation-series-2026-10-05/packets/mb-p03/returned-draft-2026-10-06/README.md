# Returned MB-P03 draft — preserved, failed validation

This is the exact untracked `control-drill.mjs` found in the original MB-P03
delegate checkout during the owner's October 6 save-to-main request. The
checkout's base is `4984f39bdca13e87ead9b446b1d033dc0f2898ee`; this file was
not part of that commit. Its SHA-256 is
`e0ed19e61e2cc1a9afe40d1feebcd9e0e3e4571e0fe67069f886b0d10d7ab1a0`.
The copy preserves every source byte; `assets/** -text` disables Git text
conversion. The original checkout is retained.
The final source line has its original CRLF ending. The archive whitespace
check allows carriage returns at line end rather than changing these bytes.

Status: **FAILED DRAFT / historical reference only**. Running
`node control-drill.mjs --dry-run` with Node 24.11.1 exits 1 at
`foreign-process-refused`: the script returns `STOP` instead of its expected
`REFUSE_FOREIGN_STOP`. Its unknown-counter check runs before the ownership
branch, and that fixture supplies no numeric counters. The later owned-thread
fixture is not reached. The synthetic 2,000/6,000 defaults are not the owner's
actual allocation. No real process stop, app interruption or billing control
is established by this draft.

The reviewed controller remains [../control-drill.mjs](../control-drill.mjs),
delivered through [PR #39](https://github.com/OKHP3/murderbird-uncaged/pull/39).
Use that controller and the existing resource receipts for the effective
MB-P03 preparation slice. This archive does not replace it, accept the failed
draft, or close the pending app-control duty. It is excluded from the Vite
release along with the rest of the audit tree.
