---
title: "MurderBird production thread closeout"
last_updated: "2026-10-23T16:07:37.269176+00:00"
status: "owner-authorized-closeout"
thread_id: "01a0e13f-9459-72b3-a1ec-015b73ff89dc"
canonical_repository: "OKHP3/murderbird-uncaged"
---

# Closeout scope

The October 23 owner allocation resumes the October 22 checkpoint for **closeout only**, with no new modeling. This receipt records the bounded production, integration, review and preservation work of **Prototype MurderBird Exhibit**. It does not close the wider cinematic likeness goal: source likeness remains **UNMET** and full-character owner artistic acceptance remains **PENDING**. Technical publication, software checks and partial head approval are separate claims.

The current `goal.md` delegation program and the separate **Assess 3D Model Completion Gaps** thread (`01a1050b-6c87-7c91-9d4f-56003ec98a76`) continue independently. Their queued work is retained. The remaining 61 records include both current evidence gaps and future implementation proposals. Their individual closeout dispositions are recorded in [the obligation ledger](../../assets/audit/thread-closeout-2026-10-23/task-dispositions.json); none is silently converted into modeling work or declared passed. T029's historical closed disposition also remains preserved.

# Recovered commitments and dispositions

Accessible conversation history was recovered from this thread's September 27 onward local session record; owner instructions, cancellations, prior handoffs, PR records and current repository instructions were compared. Tool outputs alone were not treated as owner authorization. Earlier messages before that accessible record are not claimed independently audited. The original PRD, later appearance-first direction and later no-modeling closeout boundary have different scopes.

| Commitment | Disposition and evidence |
|---|---|
| Shared, stable goal near the repository root with YAML update metadata and AGENTS pointer | `goal.md`, root `AGENTS.md`, GitHub issue #14. Existing shared status is retained. One obsolete branch link is replaced by its immutable preserved commit. |
| Preserve engineering before creating CG work | Frozen `9cc1b3c2da8cb064f343ab5915b32d0ab53236b1` remains available in Git and local `codex/v38-engineering-archive`; it is an ancestor of main. CG studies remain separately identified. No engineering/model edits in this closeout. |
| Exact September 22 canon, candidate-03 relationship, July head/era/video inventory | All seven pinned paths and SHA-256 values rechecked from current `goal.md`; PASS. Reissued locked canon `645d…` and candidate03 `538c…` are distinct binaries; both retained. July selection remains head-only. No substituted reference. |
| Milestone 1 reference/camera/baseline checkpoint | Historical camera/reference/baseline artifacts remain in Git. A completed baseline was not represented as owner likeness acceptance. |
| M1b proportion and avian stance corrections; rounded-polygon studies; softened rear skull, pointed torso, embedded hips, shoulder roots and enlarged wings | Preserved editable study05 and overlay01 at `5eeacc07ebce2d46ca7784c477e6dba454d00135`; M1c review at `a927c4f6d48f67b44e365e20d90fd655d1ddc51a`. These are historical bounded deliverables, not fabricated new results. |
| Source-image overlays and biomechanics source | Study/overlay records preserve the supplied paper and the distinction between inferred mechanical counterweight proposals and physical validation. No fabrication certification claimed. |
| M1c, M2 posture, M3 and M2a photorealistic attempts; later large bounded attempts | Retained source `e305989bff863aab827a0bdc4ee3395de32e0d61`, production release handoff and recursive-loop evidence remain preserved. The owner rejected the degree of likeness; no new artistic approval is inferred. Current direction ends modeling in this closeout. |
| Deliver retained improvements to production | Historical PRs #31–33 merged. V37 carries movement/inspection; `/cg.html` publishes the retained static CG assessment. Native sources and the 96-asset CG allowlist remain preserved; a static GLB is not an animated or validated machine. |
| Reconcile GitHub, local canonical main and linked Replit | Fresh live reconciliation recorded below. Replit's unique validator improvement integrated in PR #66; automatic deletion of eight historical logs explicitly excluded. |
| Notion continuation and requested five-pass review with detailed next tasks | Original five-pass record in `assets/audit/cg-production-delivery01/equilibrium/review-record.json`, 62 task records and all 52 PRD criteria/F01–F10/T01–T18 preserved. `docs/cg-next-goals.md` and the established Notion continuation remain the detailed backlog; the architect child is retained. |
| Defects discovered during closeout | Three source/test files from Replit recovered selectively, raw-run capture conditions now required to agree with the performance receipt. PR #66 merged at `06550c6aae1b69ebbd59e3464fa1885fbf691aed`. Synthetic fixture is test data, not ASUS hardware evidence. |
| Fresh validation and independent second pass | Local/CI/browser/custody evidence below; review results and final gate appended after completion. No claim that skipped checks passed. |
| Preservation, cleanup, durable receipt and archival last | Exact inventory and recovery outside disposable worktrees below. Cleanup and archival remain gated until verified. Shared or ownership-uncertain checkouts are retained. |

GitHub is the confirmed origin; the earlier Bitbucket idea was explicitly corrected. Siri/Muse/Gemini/OpenClaw capability exploration did not authorize compulsory execution by every provider. Replit remains a Free-mode development preview, with no paid fallback or Replit publication. Mechanics/fitment remains separately authorized future work.

# Source and integration evidence

- Canonical local mirror: `/Volumes/OKH-Local/04_GitHub_Mirrors/murderbird-uncaged`; configured origin `https://github.com/OKHP3/murderbird-uncaged.git`, default branch `main`, verified public repository.
- Starting fetched GitHub main: `fb412487c2bb03ae940a4aa9943cba8647128455`; clean canonical checkout, no stashes. This supersedes the October 22 locally cached `2f0d919…` observation.
- New isolated worktree: `/Volumes/OKH-Local/01_ChatGPT_Exports/Codex/worktrees/murderbird-thread-closeout-20261023/murderbird-uncaged`, branch `codex/thread-closeout-20261023`.
- Replit root `/home/runner/workspace` started clean on divergent `main` at `cff2b2e0d87ee3e6c8e00897c0e5bfe19613ec4c`. Parent `5df7e074…` deleted eight historical `.log` files; top commit alone supplied the intended three-file validator change. Its 9,204-byte format patch SHA-256 is `9f5d9e52f09e4ec62f77a9a44af3cd072c978a4d7f679023d86595f389aa63ae`.
- That patch was applied with `git am --3way` as `4d73d5f2488d17c61a55d71422681a974327f595`, pushed and merged through [PR #66](https://github.com/OKHP3/murderbird-uncaged/pull/66). PR run [39963213344](https://github.com/OKHP3/murderbird-uncaged/actions/runs/39963213344) passed Node 24 and 26. External Mermaid check was skipped and is not a required check; it is not counted as a pass.
- No relevant open PR remained at the initial audit; attached historical PRs #12 and #15–33 were merged. Other chats' new PRs and branches are not cleanup targets.

# Fresh verification and diagnosis

At `fb412487…`, `npm ci` completed with zero reported vulnerabilities. After hydrating LFS content, build, theme, publication allowlist, presentation, device-receipt validator, 137 unit tests (zero failures/skips) and all 768 media-import checks passed. PR #66's targeted receipt suite passed 33 tests including matching raw evidence, four changed capture-condition fields and missing/unreferenced/path-traversal cases; its Node CI covers the final source change.

The first build/test attempt failed because the new worktree contained LFS pointers rather than asset bytes. `git lfs checkout` hydrated 6,169 objects from the existing shared cache; unchanged source then passed. No model was regenerated. This is a repaired setup failure, not artistic progress.

The production-build CG browser regression passed using Chrome 156 with software ANGLE/SwiftShader: all three eras, both light rigs, explicit 3D loading, delayed-download lighting, orbit/zoom/reset, native-detail and eight-angle images, 390px layout, HTTP model failure/retry, WebGL-unavailable fallback, original/model hashes and console errors. This proves bounded software behavior; it is not physical-device performance, full T12 acceptance or owner likeness approval.

The V37 recording harness initially failed on the production build because `window.__uncaged` is intentionally exposed only in development. The next attempt uses the existing development server and preserves the initial failed receipt. Its result is recorded in the final gate below. No production debug object was added.

The live Pages baseline manifest at `fb412487…` was clean and all 154 payload path/size/hash tuples matched the fresh local build. Seven pinned reference hashes passed. Latest merged deployment and source/readback checks are recorded in the final gate; an older green deployment does not prove a later SHA.

Raw logs, failed attempts, browser screenshots/video, JSON receipts, hashes, current Git inventories and the frozen independent review packet live in the Git-ignored canonical archive below. They are not copied into `public/` or bulk committed.

# Preservation and cleanup contract

Durable private recovery outside disposable workspaces:
`/Volumes/OKH-Local/04_GitHub_Mirrors/murderbird-uncaged/.local/archives/thread-closeout-2026-10-23/`.

- Verified all-refs bundle: `pre-cleanup-all-refs.bundle`, 272,022,926 bytes, SHA-256 `5fdfef9a6ee2b8171f767e0cef763cefe397e17f69f85772b4e80f8103dd39b9`; `git bundle verify` passed.
- `preservation-receipt.json` maps 236 changed/untracked files (372,903,878 bytes) to source paths and SHA-256 recovery copies, including two ignored failure logs and six hydrated LFS files not captured by an initial filtered diff. Source/copy/source hashing verified preservation.
- Four proven thread-owned obsolete V38 worktrees: crown-construction at `864e1e6e…`, crown-lap-fit at `c035d256…`, head-profile at `66926a6e…`, hip-transition at `84934040…`. Their exact heads have `refs/archive/thread-closeout-20261023/<name>` recovery refs. Fresh process-use and change checks precede recoverable app archival.
- The hip-transition head's unique recovery-document commit is preserved rather than promoted; its hidden-input troubleshooting is superseded by current instructions. Other three heads are ancestors of main. Unapproved study renders remain recovery material, not a production release.
- Replit's Git-ignored `.local/archives/thread-closeout-20261023/` contains its verified 271,360,765-byte all-refs bundle, pre-sync inventory, exact validator patch and sync receipt. Old source is retained through two recovery branch names. No GitHub credentials were granted or copied; public source fetch succeeded without credential prompts after a requested credential handoff was declined.
- Shared `cg-production-delivery01`, uncertain/other-thread `cg-supervised-*`, Replit-evidence, LEGO, architect-closeout and other worktrees are retained. Canonical `.local` private music/source archives and nested repositories are untouched. Previously absent attached paths are recorded as already absent, not removed this run.
- Existing hourly reconciliation belongs to another task and remains intact; the old thread-specific progress heartbeat was not present in automation files. No duplicate task/agent or background-resume promise was created.

Restore recovery with `git bundle verify <bundle>` and fetch the desired archived ref into a separate checkout; use the per-file manifest to restore working files. The bundle alone does not contain ignored/untracked bytes or hydrated LFS payloads: retain the sibling recovery tree and shared LFS cache. App-managed snapshots are an additional recovery layer.

# Final gate

Pending: final Replit/build/runtime readback, independent review, recoverable cleanup, documentation integration, exact final main/Pages/Notion parity, own server/worktree cleanup, and actual thread archival. Do not treat this draft as a COMPLETE receipt.


# October 23 resumption — current runtime verified; historical recovery remains blocked

The owner resumed the complete closeout request after the resource stop. The native app returned no exhausted active goal; closeout work resumed without modeling. While this chat was stopped, the owner-account advanced the closeout branch, merged PR #67 at `65deb5161b8c816e6364de106a0685e690acdefc` and synchronized canonical main/Replit. These are freshly verified external changes, not work claimed as performed by this run.

PR #67 contains the four-line fixture portability correction plus this receipt's earlier draft and the immutable goal link. A synthetic global `.local/` ignore reproduced the original failure; the isolated fixture then passed. Production privacy checks were unchanged. Current source was subsequently fast-forwarded preserving all refs/files to `7c32048ee17954c573e7d043d9e748540befd854`, including the independently owned documentation/provenance PRs #68–70 and media-verifier portability PR #71.

At **2026-10-23T14:43:11.470856Z**, actual Replit `/home/runner/workspace` clean `main` and its fetched `origin/main` both equaled `7c32048ee17954c573e7d043d9e748540befd854`. All eight checks completed with exit 0: npm ci, build, theme, publication, presentation, performance receipt validation, full Node tests and media custody. The initial 640/768 media result identified 128 historical LFS pointers; only those paths were fetched/hydrated, and all 768 entries passed on rerun. No expected hash or asset was replaced. Current Node suite is 143 tests; the earlier 140-count applies before PR #71. Free was visibly selected; no Agent, Power/Max, billing or Publish operation was used. The existing port 5000 process was retained.

The current shared parity receipt is `.local/archives/thread-closeout-20261023/parity-final.json` in Replit, with eight logs `parity-final-{0..7}.log`. Root's native UI readback is preserved in the canonical Mac private archive. It closes current-source parity for the coordinated closeout chats without certifying this thread's historical ancestry recovery. Communication with those chats followed a directly verified owner reply authorizing coordination of active chats; one operator owned Shell at a time.

Additional automated production-build observations at `65deb516…` passed: V37 system reduced motion/calm status, disabled jump, keyboard pause toggles; full/loop theme decoding and advancing clock, pause/restart/mute/volume; approved-version lyrics opened by keyboard; silent First Choice visitor playback and seek with truthful source labels. V37's uncut 177.809-second development sequence and production illustrated fallback also passed. Human listening/seam quality, actual screen-reader and physical-device journeys, controlled network/memory measurements, full T12 matrix and strict native/export normals remain explicitly unclaimed. The [62-row disposition ledger](../../assets/audit/thread-closeout-2026-10-23/task-dispositions.json) separates these current gaps from future modeling; it does not rewrite or close the original task ledger.

## Exact historical recovery blocker

The older October 4/5 records identify **15 preserved Replit-only commits plus two later configuration commits**, rooted at `6b9548081ba278bc9a7bf48c0061056c1b9f70ca`, then `76c6f152950349ce8c414bd7e0fd58f66188dabd` and `0d7366d8e8924cacebf48b19a0a0dbb27bd0b673`. Fresh `git cat-file` lookups for all three fail in the current Replit object database. GitHub commit lookup also reports no commit for the two queried endpoint tips. The canonical Mac database does not contain these historical tips. No source/ref deletion was performed during this closeout.

The surviving `.local/archives/replit-pre-v37.bundle` is 125,751,364 bytes and verifies, with head `c1bfca3736fd9f981cc6f8f05e6ce79113b95724`. It preserves a different earlier history, with ten commits not reachable from current main. This does not establish the exact original 15 plus 2 inventory or prove the October 4 main-history bundle's coverage. The current 271,360,765-byte all-refs bundle protects the current store; it is not promoted into proof of missing earlier ancestry. Searches of persistent `.local` recovery bundles and recorded migration recovery artifacts did not locate the former roughly 167 MB October 4 main-history bundle. The source session's original preservation statements remain historical reports, not current recovery verification.

The unique older widened-exterior GLB **was recovered** from Replit's local LFS cache: 17,340,120 bytes, SHA-256 `e57bca8d183808a7dd808b03616f807039b8693879deb4ef3fdbf20e36322692`. Its exact bytes were copied separately to `.local/archives/thread-closeout-20261023/historical-unique-exterior.glb`; this is recovery only, with no runtime promotion. A bounded authenticated GitHub LFS retrieval reported object 404, so no remote availability or successful Mac copy is claimed. Failed local downloads are 133-byte pointer artifacts, not the recovered binary.

**Smallest missing input:** access to the former October 4 main-history recovery bundle, or another clone/backup containing the three exact historical tips above. Once available, produce the exact 15 plus 2 commit/path inventory, compare intended contributions to retained04/V37, and preserve/import only reviewed improvements. A count, a different bundle or a commit subject cannot establish equivalence. The independent audit requires this disposition before this thread can be declared COMPLETE.

## Cleanup and final disposition

Status remains **BLOCKED by historical recovery**, rather than by the expired token allocation. All 236 preserved file copies, all-refs bundle, four old thread-owned V38 worktrees, frozen engineering line, shared/uncertain worktrees and the isolated closeout worktree remain retained. No recoverable worktree archival or branch deletion is claimed. Cleanup and actual thread archival wait for the historical recovery gate; no permanent deletion is authorized or needed now. Existing independent review decisions defer final archival. Final documentation/readback evidence is appended separately after its actual merge; no self-referential SHA is invented.


## Independent resumption audit

Three separate reviewer contexts rechecked the frozen v2 receipt and all 62 dispositions. Evidence, outcome and safety/portability each approved publication **with limits**; none approved COMPLETE or archival. They confirmed that only historical MB-T029 is closed, current observations do not certify human/device/full T12 results, and the unique binary does not establish older ancestry recovery. A raw-readback omission was found and repaired by printing the complete actual Replit JSON: all eight check exits were 0, clean 7c32048 HEAD/origin, three missing-tip exits 128 and ten earlier commit identities. Raw AX SHA-256 is `4dba25ae086b4eba3de83c5f7c57f67a1a669abf9e9705d1937cecda91508c94`. No suite was rerun merely to repair evidence capture. Same model family and overlapping sources limit independence; no protected visual holdout or artistic review was claimed. The negotiated disposition is publish an accurate BLOCKED checkpoint, finish its transport/readbacks and retain every workspace.

## October 23 owner exception and verified legacy-workspace cleanup

**Current authority supersedes the recovery hold above:** the owner directly answered **“Authorize the documented historical exception, then finish safe cleanup and archive.”** The original 15 plus 2 Replit contribution coverage is permanently **UNVERIFIED — OWNER-AUTHORIZED EXCEPTION**. It is no longer a closure prerequisite for this thread. No missing commit, contribution equivalence, remote binary availability or artistic acceptance is manufactured by this decision. The earlier blocked records remain dated history.

All available recovery remains intact: the 272,022,926-byte verified canonical bundle, 236 exact file copies / 372,903,878 bytes, all four full archive refs, the shared LFS object cache and the available Replit bundles/private recovered GLB. Original historical task-ledger statuses remain unchanged. MB-T061's closeout disposition now records the exception; its wider program task is not declared complete.

A fresh independent safety review verified every source/copy hash, both ignored failure logs, exact heads/archive refs and no open-file use. All tracked LFS objects in each of the four old worktrees were checked against the retained shared cache (6,506;6,542;6,454;6,391 entries); none required recovery. The app archive request returned queued without observed removal, so no app snapshot is claimed. After fresh per-target checks, Git-aware worktree removal and exact local branch deletion succeeded for:

| Worktree | Original head | Durable recovery ref | Local branch disposition |
|---|---|---|---|
| `v38-crown-construction` | `864e1e6eddf105667a999b63bce1cb9b225ba192` | `refs/archive/thread-closeout-20261023/v38-crown-construction` | `codex/v38-crown-construction-01` deleted; recovery retained |
| `v38-crown-lap-fit` | `c035d25625bec9521661e8ec5ab13ee9f547e278` | `refs/archive/thread-closeout-20261023/v38-crown-lap-fit` | `codex/v38-crown-lap-fit-01` deleted; recovery retained |
| `v38-head-profile` | `66926a6e5d7dfcd65796dd696c0c24b3d68fde45` | `refs/archive/thread-closeout-20261023/v38-head-profile` | `codex/v38-head-profile-01` deleted; recovery retained |
| `v38-hip-transition` | `8493404082a3d12b1284ff42b8fe7034805eade7` | `refs/archive/thread-closeout-20261023/v38-hip-transition` | `codex/v38-shoulder-form-01` deleted; recovery retained |

The first three heads are ancestors of main. The hip-transition recovery-document commit was preserved and explicitly superseded rather than promoted into current models. All four source directories are absent from disk and the Git worktree registry; prune dry-run reports no stale Git registration. No shared clone, other-thread workspace, private archive, LFS cache, source model, frozen engineering ref or Replit recovery was deleted. This run's isolated documentation worktree remains until final integration/readback, after which its unique ignored publication receipt is already hash-backed for removal.

Final technical evidence before this documentation change remains separately attributable: PR 74/cafabbb Node 24/26 and Pages passed; all 154 live payload files (407,610,132 bytes) matched SHA-256. Actual Free-selected Replit clean source/origin/build 4e844db6 passed five focused checks and three HTTP 200 routes; the earlier full 7c32048 suite passed 143 tests / 768 media entries / eight checks. Later independently owned goal/closeout changes through ae0bd134 are documentation only. This closeout changes no model or runtime payload.

The established Notion continuation retains all 62 IDs and its architect child; raw fetch custody is saved privately. A final transport receipt beside the preserved archive records this document's actual merge, CI/Pages, local/Replit/Notion readbacks, final isolated-worktree removal and actual thread archival after those operations occur. This committed document cannot self-certify its own future merge or archival. Source likeness stays UNMET, whole-character artistic acceptance PENDING, strict normal parity FAIL, and human/device/full T12 evidence unclaimed; the separate CG program retains those boundaries.
