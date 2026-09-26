# MurderBird: Uncaged

- This is the standalone static Vite/Three.js MurderBird exhibit and creative-production repository. The OverKill Hill public site is generated static HTML and does not use this app's Vite pipeline.
- GitHub Actions builds the exhibit for **GitHub Pages**. Do not publish it as a Replit-hosted application. Replit is for development preview only.
- Install dependencies with `npm ci`, run `npm run dev -- --host 0.0.0.0 --port 5000` for a Replit preview, and verify the distributable with `npm run build`. The workflow definitions are in `.github/workflows/validate.yml` and `.github/workflows/deploy.yml`.
- Preserve the current stack and three-era exhibit structure unless a separately scoped change requires otherwise. The procedural construction study and synthesized Web Audio sketch are drafts. No finished 3D model or recorded vocal take is verified by this repository guidance; do not infer final status, rights, or publication approval from a file name.
- Follow [AGENTS.md](AGENTS.md) and [the repository boundaries](docs/repository-boundaries.md) for source retention, privacy, provenance, and release checks. Never put source archives, production sessions, or private material under `public/`.

## Git synchronization

- GitHub `origin/main` is canonical; the Windows mirror and Replit are separate checkouts. Committing or pulling in one does not update the other.
- Before syncing, inspect `git status --short --branch`, then `git fetch --no-prune origin` and `git rev-list --left-right --count HEAD...origin/main`. Preserve uncommitted work and divergent branch tips before integrating.
- If only behind and clean, use `git pull --ff-only origin main`. If both ahead and behind, integrate on a review branch and use a PR; do not force-push or reset away work. A failed fast-forward is a request to inspect history, not to repeat the same pull.
- After a squash merge, compare trees and preserve the old branch tip before cleanup. Replit agent branches can have different commit IDs with identical content. Leave the `gitsafe-backup` remote intact.
- Refresh the Git panel after Shell operations. A stale unpushed-commit badge is not evidence of divergence; verify fresh Shell counts, exact GitHub SHA, and clean status. Confirm UI authentication separately if prompted.

## Replit connection status

As recorded for this migration on 2026-09-26, the Replit connectors for both relevant accounts report **UNAUTHORIZED**. No current remote synchronization is proven by connector access. Treat a Replit UI, Git panel, or shell as unavailable evidence until access is restored and the exact remote and commit are checked. Local preview instructions above remain valid; they do not prove a remote sync or publication.
