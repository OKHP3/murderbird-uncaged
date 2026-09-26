# MurderBird: Uncaged

- This is a static Vite/Three.js interactive exhibit intended for **GitHub Pages**. Do not publish it as a Replit-hosted application. The Replit workflow is for local development preview only.
- Install dependencies with `npm ci` (or Replit's package tooling), run `npm run dev -- --host 0.0.0.0 --port 5000` for development, and verify the distributable with `npm run build`.
- Deployment is configured in `.github/workflows/deploy.yml` for the GitHub repository's `main` branch. Enable GitHub Pages with GitHub Actions as the source.
- The model and audio are procedural drafts; do not present them as final licensed assets. Finished 3D, music, image, and video files have not been supplied. Keep the existing stack and the story's three-era structure.

## Git synchronization

- GitHub `origin/main` is canonical; the Windows mirror and Replit are separate checkouts. Committing or pulling in one does not update the other.
- Before syncing, inspect `git status --short --branch`, then `git fetch --no-prune origin` and `git rev-list --left-right --count HEAD...origin/main`. Preserve uncommitted work and divergent branch tips before integrating.
- If only behind and clean, use `git pull --ff-only origin main`. If both ahead and behind, integrate on a review branch and use a PR; do not force-push or reset away work. A failed fast-forward is a request to inspect history, not to repeat the same pull.
- After a squash merge, compare trees and preserve the old branch tip before cleanup. Replit agent branches can have different commit IDs with identical content. Leave the `gitsafe-backup` remote intact.
- Refresh the Git panel after Shell operations. A stale unpushed-commit badge is not evidence of divergence; verify fresh Shell counts, exact GitHub SHA, and clean status. Confirm UI authentication separately if prompted.
