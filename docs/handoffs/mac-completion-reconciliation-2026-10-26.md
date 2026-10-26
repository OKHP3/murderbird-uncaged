---
title: "Mac completion reconciliation and next release gates"
last_updated: "2026-10-26"
status: "local-validation-complete-shared-acceptance-open"
---

# Current conclusion

The inspected Mac checkout, preservation manifests and historical closeout records are reconciled. Overall MurderBird acceptance remains open. Historical studies that the owner superseded stay retired, and the scoped historical contribution exception in [the production closeout](thread-closeout-2026-10-23.md) remains unverified under that exception. No missing history is represented as recovered.

This public handoff contains product and validation facts only. The original detailed local audit, source readbacks, recovery hashes and test logs remain in the established ignored evidence home. They are not part of this change or the website build.

The current shared goal was reviewed from GitHub main `914956e32b5496600652ed2406b8a80e0eb1f857`; its goal blob is `036e34801e222a175b6c9e03546f218b1550f915`, last updated October 23. [goal.md](../../goal.md) and its owner decisions govern the creative program. A build, archival event or export-data check does not establish artistic acceptance.

# Completion matrix

| Area | Observed status | Existing owner / next gate |
| --- | --- | --- |
| Mac checkout and named preservation holdings | Reconciled; main matched GitHub at the reviewed revision; retained branch tips match deliberate keep dispositions | Preserve recovery; no branch pruning or restoration is needed for this increment |
| LFS workflow/cache | [PR81](https://github.com/OKHP3/murderbird-uncaged/pull/81), draft, head `8aba0d8722cef0373e1df58c011cc40367a62ecf`; remote cache absent | Existing LFS owner retains workflow, helper, cache and activation scope |
| Strict normal/UV/material data | [PR83](https://github.com/OKHP3/murderbird-uncaged/pull/83), draft, head observed `533c6f19c0ee105bf9bf0f056eb91981382511d9`, stacked on PR81; reports three-era local parity at unchanged thresholds | Existing CG acceptance owner retains exporter, parity, receipt tooling and model work; final evolving head must be reviewed |
| Rendered parity, likeness and era finish | Still open; the acceptance owner is preparing a bounded connected-head correction | Matched visual evidence and owner artistic review; no model promotion in this increment |
| Approved target-device performance | PR83 records failed p95 and feedback thresholds; reverted GPU-request experiment did not resolve them | Retain the failures and exact device context; no Mac/software result substitutes for the target device |
| PRD and human acceptance | Scoring, human accessibility/listening/touch and applicable scenario evidence remain incomplete | Named review and measurements; automation must not self-approve human outcomes |
| Windows fixture setup | Existing full Windows run reports four setup failures; this increment repairs the portable fixture/encoding design | Native Windows verification of this exact change remains pending |
| Dependency maintenance | [PR82](https://github.com/OKHP3/murderbird-uncaged/pull/82), open, head `65219afc44635629a9ecefb7ad8b2ca66cb53a4f`; associated validation [40303081464](https://github.com/OKHP3/murderbird-uncaged/actions/runs/40303081464) succeeded | Separate reviewed integration; no dependency change made here |
| Remote CI / deployment | PR83 run [40365214053](https://github.com/OKHP3/murderbird-uncaged/actions/runs/40365214053) passes safeguards then stops at 499 missing cache objects, with no network requested | Existing cache hold; no unchanged-job rerun or deployment requested |

# Completed safe correction

The media verifier previously combined filename-protocol coverage with real paths that ordinary Windows filesystems cannot create. Its manifest reader also inherited the system default text encoding. This increment:

- Reads import manifests explicitly as UTF-8, preserving Unicode destination identity across system locales.
- Keeps real fixtures within ordinary Windows path limits while increasing the filesystem inventory to 2,048 entries so its attribute input still exceeds 200 kB.
- Exercises 1,024 long Unicode/newline paths through the actual Git attribute helper without creating those names on disk. Both accepted binary attributes and rejected text conversion retain exact path assertions.
- Uses a Windows directory junction to test ancestor and existing-output link rejection without requiring file-symlink privileges. POSIX keeps its dangling-file symlink case. No test is skipped and no acceptance threshold changes.

Owned implementation paths are limited to `scripts/verify-media-import.py`, `tests/media-import.test.mjs`, and `tests/structural-clearance-snapshot.test.mjs`. This does not edit PR81's workflow/helper, PR83's exporter/receipt/model paths, dependencies, runtime geometry, creative binaries or published asset selections.

Node's [filesystem contract](https://nodejs.org/api/fs.html#fspromisessymlinktarget-path-type) documents that Windows junction targets are directories. The Windows branch of these fixtures still requires a native execution; a Mac pass does not certify it.

# Validation actually performed

Before editing, the PR81-base Mac checkout passed an offline dependency install and all 160 Node tests. After the correction, the targeted media/snapshot suites passed 11/11 with zero skips. The full post-change Node 26 suite passed **161/161**, zero skips. The build and theme/publication/presentation/device-receipt validators passed; all **768/768** imported entries matched. Inspection found **155** emitted files (154 payloads plus release.json), with no unresolved pointer or source/private leakage. The selected LFS plan remains unchanged at 499 objects / 2,736,090,200 bytes. Node 24 and native Windows execution were not run here. Final commit identity is recorded in the draft PR and local continuation receipt; this document does not invent its own future commit SHA.

The locally available, previously preserved payloads are used for verification. No LFS network hydration, cache fill, account change or remote recovery is inferred from those bytes. Full builds and publication validators are separate from target-device and artistic acceptance. Current GitHub Pages, Replit and other external copies require their own exact-revision readbacks; this checkpoint does not claim they synchronized.

# Critical path and exact approval gates

1. Complete this small fixture change and the active CG owner's bounded candidate independently. Obtain native Windows fixture results and the owner's final acceptance matrix. Do not spawn another overlapping model/export/cache effort.
2. Re-read the final PR heads and base order. PR81 is the prerequisite for both PR83 and this Mac increment, which use its cache-only workflow. PR82 remains an independent dependency change. Any downstream merge needs its own exact-head approval; an approval of PR81 does not approve another PR or an evolving visual candidate.
3. LFS activation remains blocked on the specific prerequisites in [bounded activation and rollback](../lfs-downloads.md#bounded-activation-and-rollback). The currently recorded plan is 499 unique objects / 518 paths / **2,736,090,200 unique payload bytes**, within a **3,000,000,000-byte selection ceiling**. The recorded plan key is `ci-lfs-v2-ci-d8724a1b7f443177ab9dbe8c0a6c2894c2c6227a7ba1754fcbaa9aca8731987f`. Recompute it at the final resulting main SHA and stop if it differs.
4. Finance must confirm current zero-dollar enforcement and sufficient remaining allowance. The existing owner's conservative one-retry envelope is **5,472,180,400 payload bytes plus overhead and other account activity**, not a hard wire-traffic cap. This doubles the unique payload size to reserve one supported retry per object; it is not two planned downloads for Node 24/26, which share one hydrated workspace. A zero retry setting is unsupported and silently restores Git LFS defaults. No fill or additional run/manual retry is authorized by this handoff.
5. Before any separately approved validation-only fill, freeze main updates and drain automatic main runs. A queued push could publish after the cache warms even if the manual run has publication disabled. Merge order, freeze, exact resulting main SHA, plan key and byte ceiling must be explicitly reviewed together. The existing LFS owner performs activation, not this Mac branch. Keep main unfrozen until an operation is actually approved. The contemplated first fill validates the approved resulting main with publish_pages=false. Once its default-branch cache is warm, merging PR83, this Mac increment, PR82 or any other main change can automatically deploy; each therefore needs separate exact-head and publication approval, or an independently reviewed workflow change. No such approval is recorded here.
6. After full Node 24/26, import and publication checks succeed at the approved revision, deployment still requires separate explicit approval and exact-run/live-payload verification. Artistic acceptance and later mechanics retain their own gates.

The smallest remaining technical gate for this increment is native Windows execution of the revised fixtures and review of its exact draft head. The broader critical path remains the existing acceptance owner plus the approval-blocked cache activation. There is no automatic restart of the paused Mac alignment schedule and no additional implementation thread is required for these owned paths.
