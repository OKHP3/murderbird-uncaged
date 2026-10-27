# Bounded LFS downloads and release validation

Git LFS storage, download bandwidth, and successful publication are separate measurements. This workflow reduces repeated downloads; it does not reclaim hosted storage or reset consumed bandwidth.

## One hydrated workspace

`Validate build` checks out Git pointers with automatic LFS hydration disabled. `scripts/ci-lfs-assets.mjs` derives the required set from the committed import ledgers, publication manifests, tracked public files, runtime references, active verifiers, and real test fixtures. The current plan is 499 distinct SHA-256 objects / 2,736,090,200 declared bytes across 518 paths. Run `plan` to obtain the current quantities; they are not metered usage.

The helper enforces a 3,000,000,000-byte unique-object ceiling. Enlarging that ceiling requires reviewing the asset scope. It is not a retention policy: editable source masters and historical objects outside the CI set remain preserved.

After hydration, the same workspace runs the existing builds, publication/theme/presentation/device verifiers and full test suite on Node 24 and Node 26 sequentially. The unchanged Python import verifier checks every recorded source entry. Pages receives the validated output from that job; it performs no second checkout or build. Superseded non-main runs are cancelled. Main runs serialize without cancelling an active run, preserving an approved cache fill; the activation plan below also requires a main-ref freeze and queue drain.

## Local development and synchronization

For a new clone, suppress smudging during the clone itself:

```sh
git -c filter.lfs.smudge= -c filter.lfs.process= -c filter.lfs.required=false clone https://github.com/OKHP3/murderbird-uncaged.git
cd murderbird-uncaged
git lfs install --local --skip-smudge
node scripts/ci-lfs-assets.mjs plan --scope=build
node scripts/ci-lfs-assets.mjs hydrate --scope=build
```

`hydrate` uses existing local cache objects or already-real selected working-tree files. It checks sizes and SHA-256 hashes, rejects pointer files masquerading as originals, and refuses to overwrite edited files, altered pointers or symlinks. Missing or corrupt payloads cause a clear failure before the build. It makes no network request by default.

The build scope selects the publication inputs, tracked public files, and runtime references required for the preview: currently 114 distinct objects / 403,607,607 declared bytes. It excludes CI-only historical import sources and test fixtures. Omit `--scope=build` before running the full verification suite: the default CI plan retains those required source checks.

The Replit environment also skips smudging. Its post-merge script runs verified build-scope local hydration before installation/build. This repository change does not prove that a particular external Replit checkout has synchronized or that its cache is populated. Replit remains Free mode development only.

Only after confirming current zero-dollar stop-usage enforcement and enough unused bandwidth for the plan, explicitly fetch missing selected content:

```sh
node scripts/ci-lfs-assets.mjs hydrate --scope=build --fetch \
  --expected-head=APPROVED_FULL_SHA --expected-plan-key=APPROVED_BUILD_CACHE_KEY \
  --max-download-bytes=403607607
```

Replace the placeholders with the reviewed `plan` result. A stale revision, asset-plan key, malformed byte ceiling or ceiling below the plan fails before fetching. This retrieves only missing selected paths at the current commit, with recent-history fetching disabled and transfers serialized. Git LFS's minimum supported retry setting is **one**; zero silently restores its default of eight. The byte ceiling bounds unique selected payloads, not wire traffic or metered usage. Budget conservatively for up to one retry per object, plus protocol overhead, and stop after a failed run for allowance reconciliation. For full CI validation, omit `--scope=build` and budget against the larger CI plan. It does not use `git lfs pull`, `fetch --all`, prune, or a history rewrite. Corrupt payloads require investigation rather than an automatic destructive repair. Restore existing verified originals where possible.

## Cache and zero-spending behavior

The Actions cache contains only selected LFS object bytes and is keyed by the sorted object IDs and sizes. Every restored object is verified again. Ordinary pull-request, push, and manual runs are cache-only. If the exact cache is unavailable and real files are missing, CI fails; it does not skip the asset-dependent checks or report a successful build.

To fill a cold cache after financial enforcement and available allowance have been checked, manually run `Validate build` on main, select `allow_lfs_download`, and provide `expected_revision`, `expected_lfs_plan_key`, and `max_lfs_download_bytes`. They must identify the exact approved main SHA, current CI plan key, and reviewed unique-payload ceiling. The input is an explicit acknowledgement, not an API verification of the account budget. Feature-branch fills are refused. The workflow separately reads the repository's cache storage limit and refuses the fill when the limit is invalid, exceeds the free 10 GB ceiling or the read fails. It does not change budgets, cache limits, credentials, or payment settings.

Only an explicitly requested fill saves a new asset cache. No raw archive is uploaded as a workflow artifact. GitHub caches may expire or be evicted. A cache filled on a feature branch does not prime main; fill it on main after the repair is merged so ordinary PRs can reuse the default-branch cache. Keep a verified independent preservation archive: a disposable Actions cache is not a backup.

A main push publishes only after all checks succeed. Manual validation defaults to no publication; `publish_pages` permits publication only when the selected ref is main. This allows an approved main-branch cache fill and validated deployment in one run, without a dummy commit or repeated downloads.

## Bounded activation and rollback

Activation is approval-blocked. A reported November 1 reset is historical information, not current allowance. Finance must first confirm current zero-dollar stop-usage enforcement and available LFS allowance for the conservative transfer envelope. Cache-limit verification is separate from billing verification.

1. Recheck the exact PR head, base, diff, checks, cache scope/size and merge eligibility. Preserve failing build status; a cold-cache guard is not full validation. Freeze main updates and unrelated deployment dispatches during activation. Merge only after the owner explicitly approves the reviewed head and its documented missing-cache hold. Before a validation-only fill, let the merge-triggered main push finish its expected cold-cache failure and confirm no queued/running automatic main runs remain. A queued push could otherwise find the newly warmed cache and publish automatically despite `publish_pages=false` on the manual run. If an LFS cache unexpectedly already exists, stop and reassess before merging because the merge push can publish.
2. Read the resulting main SHA and recompute its CI plan with skip-smudge; require the reviewed key `ci-lfs-v2-ci-d8724a1b7f443177ab9dbe8c0a6c2894c2c6227a7ba1754fcbaa9aca8731987f`, **499 objects / 518 paths / 2,736,090,200 unique bytes**, or stop for scope review. The CI ceiling input is **2736090200**. The separate preview plan is **114 objects / 403,607,607 bytes** and cannot satisfy full CI.
3. With the current empty cache, expected first-pass LFS payload is **2,736,090,200 bytes** (about 2.548 GiB). Conservatively reserve **5,472,180,400 payload bytes** (about 5.097 GiB) for the supported one-retry setting, plus protocol overhead and other account activity. This is an allowance-planning envelope, not a hard network-meter cap. No second run or manual retry is preapproved.
4. Dispatch `validate.yml` once on main with `allow_lfs_download=true`, the exact resulting main SHA as `expected_revision`, the key above as `expected_lfs_plan_key`, `max_lfs_download_bytes=2736090200`, and `publish_pages=false`. A separate explicit publication approval may set that last input true. An approved combined run avoids another build; a later cache-only publication run should incur zero LFS downloads if the verified cache remains available. Main runs serialize without cancelling an active fill; the ref freeze also prevents a queued later revision from superseding it.
5. Inspect the exact run: verified selected objects, successful saved default-branch cache, both Node 24 and Node 26 builds/full tests, all 768 import entries, and publication/privacy checks. A cache save alone is not a pass. Record the actual SHA and run. Release the main freeze only after a deliberate outcome. If publishing was approved, verify that deployment run and SHA, live `release.json`, and all intended payload sizes/hashes; otherwise deployment remains unverified.

On any fetch, cache, test or deployment failure, stop; preserve existing local/successfully-saved caches, all recovery copies and the last good Pages site. A failed fill before the cache-save step leaves no proven durable partial cache: runner-local partials may disappear and a fresh runner may need those bytes again. Reconcile transferred bytes with Finance before any retry. Do not revert this PR wholesale: that restores automatic LFS checkouts. Keep skip-smudge and cache-only guards, suspend manual fill/publication dispatches, and prepare a reviewed forward fix. Any deployment rollback needs its own approval and an already-validated artifact; do not rebuild by bulk downloading historical assets. Cache corruption/eviction requires diagnosis and a new bounded decision, not purge or blind reruns.

## Evidence boundaries

- A declared object size is not proof that GitHub hosts or bills that object.
- A Git bundle preserves pointers and history, not LFS payloads.
- Deleting current paths or compressing local backups does not reclaim hosted objects.
- Re-encoding an asset creates a new version; retaining old hosted versions can increase storage.
- A quota notice is not a checkout failure. Inspect the failed job and actual error before assigning a cause.
- Successful local builds do not establish final-commit CI, live deployment, external synchronization, or owner artistic acceptance.

Before any historical migration or purge, preserve complete payload copies with explicit paths, sizes, SHA-256 hashes, and restoration evidence. Missing originals remain a hold. Hosted removal is a separate owner-approved operation through a supported GitHub procedure.

Sources checked October 26, 2026: [GitHub LFS billing](https://docs.github.com/en/billing/concepts/product-billing/git-lfs), [removing hosted LFS objects](https://docs.github.com/en/repositories/working-with-files/managing-large-files/removing-files-from-git-large-file-storage), [cache limits and scope](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching), [Git LFS include/exclude behavior](https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-fetch.adoc), and [Git LFS retry configuration](https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-config.adoc).
