# Restore the historical appearance checkpoint

The verified local package is at `.local/archives/appearance-thread-2026-10-22/` in the canonical Mac repository `/Volumes/OKH-Local/04_GitHub_Mirrors/murderbird-uncaged`. It is outside the disposable closeout checkout and Git-ignored. Keep this package and the original snapshot ref; a Git bundle alone does not contain LFS payloads.

Files:

- `appearance-snapshot.bundle`: complete reachable Git history for snapshot `7da906d1f59bbcb75c533354cdbcc145ccb690f2` and its advertised `refs/codex/snapshots/138e4b97cbb2edb38a35974653c3770efd814b5f`.
- `appearance-lfs.tar`: 309 verified payloads under `lfs/objects/<first-two>/<next-two>/<sha256>`.
- `manifest.json`, `canonical-selection.json`, `preservation-verification.json`: exact inventory and archive identities.
- `restore-smoke-test.json`: fresh read-only reconstruction checks performed during closeout.

The tar covers the **appearance delta only**, not every LFS object in the baseline or complete Git history. Baseline assets must come from the preserved canonical LFS store or a verified authorized source. Do not run a broad LFS fetch or publish a restored candidate without checking scope.

Use a new isolated destination; never reset an existing working checkout. Verify the bundle and archive hashes against `preservation-verification.json`, initialize the destination, then fetch the advertised snapshot ref from the bundle. Check out the snapshot with `GIT_LFS_SKIP_SMUDGE=1`. Validate tar member names against the manifest before extracting into that new checkout's `.git/` directory; hydrate the 317 scoped paths using Git LFS. Confirm actual SHA-256 and sizes against `manifest.json`. Restore the original paths, including `scripts/`, before considering any historical command.

The October 22 smoke test separately initialized a bare repository, fetched the bundle, matched the snapshot tree and all 492 scoped Git blobs, and read all 309 archived payloads to validate their names, sizes and hashes. It did not render the model, rebuild the September application, or assert deterministic regeneration. The original native files, raw/packed GLBs, all iteration evidence and source files can be recovered from the snapshot plus the scoped payload archive. The ignored original local build-validation file is not recoverable from this snapshot.

The old archive ref `refs/archive/2026-10-13-consolidation/codex/appearance-production` resolves only to parent `3e6d340e616e79708d2a62ec9255fd997d14ea4f`; it is not an adequate substitute for the snapshot and LFS package.
