# Bounded LFS downloads and release validation

Git LFS storage, download bandwidth, and successful publication are separate measurements. This workflow reduces repeated downloads; it does not reclaim hosted storage or reset consumed bandwidth.

## One hydrated workspace

`Validate build` checks out Git pointers with automatic LFS hydration disabled. `scripts/ci-lfs-assets.mjs` derives the required set from the committed import ledgers, publication manifests, tracked public files, runtime references, active verifiers, and real test fixtures. The current plan is 499 distinct SHA-256 objects / 2,736,090,200 declared bytes across 518 paths. Run `plan` to obtain the current quantities; they are not metered usage.

The helper enforces a 3,000,000,000-byte unique-object ceiling. Enlarging that ceiling requires reviewing the asset scope. It is not a retention policy: editable source masters and historical objects outside the CI set remain preserved.

After hydration, the same workspace runs the existing builds, publication/theme/presentation/device verifiers and full test suite on Node 24 and Node 26 sequentially. The unchanged Python import verifier checks every recorded source entry. Pages receives the validated output from that job; it performs no second checkout or build. Superseded runs are cancelled.

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
node scripts/ci-lfs-assets.mjs hydrate --scope=build --fetch
```

This retrieves only missing selected paths at the current commit, with recent-history fetching disabled. For full CI validation, omit `--scope=build` and budget against the larger CI plan. It does not use `git lfs pull`, `fetch --all`, prune, or a history rewrite. Corrupt payloads require investigation rather than an automatic destructive repair. Restore existing verified originals where possible.

## Cache and zero-spending behavior

The Actions cache contains only selected LFS object bytes and is keyed by the sorted object IDs and sizes. Every restored object is verified again. Ordinary pull-request, push, and manual runs are cache-only. If the exact cache is unavailable and real files are missing, CI fails; it does not skip the asset-dependent checks or report a successful build.

To fill a cold cache after financial enforcement and available allowance have been checked, manually run `Validate build` and select `allow_lfs_download`. The input is an explicit acknowledgement, not an API verification of the account budget. The workflow separately reads the repository's cache storage limit and refuses the fill when the limit exceeds the free 10 GB ceiling or the read fails. It does not change budgets, cache limits, credentials, or payment settings.

Only an explicitly requested fill saves a new asset cache. No raw archive is uploaded as a workflow artifact. GitHub caches may expire or be evicted. A cache filled on a feature branch does not prime main; fill it on main after the repair is merged so ordinary PRs can reuse the default-branch cache. Keep a verified independent preservation archive: a disposable Actions cache is not a backup.

A main push publishes only after all checks succeed. Manual validation defaults to no publication; `publish_pages` permits publication only when the selected ref is main. This allows an approved main-branch cache fill and validated deployment in one run, without a dummy commit or repeated downloads.

## Evidence boundaries

- A declared object size is not proof that GitHub hosts or bills that object.
- A Git bundle preserves pointers and history, not LFS payloads.
- Deleting current paths or compressing local backups does not reclaim hosted objects.
- Re-encoding an asset creates a new version; retaining old hosted versions can increase storage.
- A quota notice is not a checkout failure. Inspect the failed job and actual error before assigning a cause.
- Successful local builds do not establish final-commit CI, live deployment, external synchronization, or owner artistic acceptance.

Before any historical migration or purge, preserve complete payload copies with explicit paths, sizes, SHA-256 hashes, and restoration evidence. Missing originals remain a hold. Hosted removal is a separate owner-approved operation through a supported GitHub procedure.

Sources checked October 26, 2026: [GitHub LFS billing](https://docs.github.com/en/billing/concepts/product-billing/git-lfs), [removing hosted LFS objects](https://docs.github.com/en/repositories/working-with-files/managing-large-files/removing-files-from-git-large-file-storage), [cache limits and scope](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching), and [Git LFS include/exclude behavior](https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-fetch.adoc).
