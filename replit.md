# MurderBird: Uncaged

- This is the standalone static Vite/Three.js MurderBird exhibit and creative-production repository. The OverKill Hill public site is generated static HTML and does not use this app's Vite pipeline.
- GitHub Actions builds the exhibit for **GitHub Pages**. Do not publish it as a Replit-hosted application. Replit is for development preview only.
- Install dependencies with `npm ci`, run `npm run dev -- --host 0.0.0.0 --port 5000` for a Replit preview, and verify the distributable with `npm run build`. The workflow definitions are in `.github/workflows/validate.yml` and `.github/workflows/deploy.yml`.
- Preserve the current stack and three-era exhibit structure unless a separately scoped change requires otherwise. The root exhibit loads the exterior-v1 combined GLB with runtime Three.js mechanisms. This is an implemented review study, not owner-accepted final art or validated engineering. The owner accepted and authorized publication of the synthesized sung Iron Verdict v3; no human-vocal recording is claimed. Keep that release distinct from the historical instrumental demo, GarageBand derivative, and optional synthesized soundscape. Do not infer final status, rights, or publication approval from a file name.
- Follow [AGENTS.md](AGENTS.md) and [the repository boundaries](docs/repository-boundaries.md) for source retention, privacy, provenance, and release checks. Never put source archives, production sessions, or private material under `public/`.
- Apply the current visual canon and asset-specific use limits in [the exhibit direction](docs/exhibit-direction.md). Selected stills have feature-specific scopes and may appear in the authorized public assessment/review package; this does not approve final art or model likeness, expand their use, or grant a blanket license. Keep the original instrumental, GarageBand derivative, and accepted Iron Verdict v3 song distinct and visitor-started; assessment-package inclusion does not establish broader rights. Do not imply a finished rig, measured anatomy, reactor, or human vocalist.

## MurderBird exhibit boundaries

- Treat the character as a formidable, floor-standing, flightless terrorbird with a deep hooked bill, segmented crown, strong legs/talons, compact folded wings, and an anatomically left shoulder fitted twice with limited travel. Keep the shoulder history asymmetric. The July-selected image controls head identity only; candidate 03 is the lead common-body reference, not a measured drawing or final-art approval.
- Keep era materials distinct: Water is inert and dark-eyed; Mechanic-era repairs are visibly industrial; modern energy and processing are separate, and the Heart still is not a completed mind. Do not show a glowing chest reactor or put a modern amber optic into earlier eras.
- The root viewer loads `assets/models/uncaged-exterior-v1/murderbird-exterior-v1.glb` through `src/scene/presence-exhibit.js`. It is the current three-era review study, not accepted canonical art, a validated engineering model, or a finished rig. The older procedural scene in `src/scene/exhibit.js` is used by the folio path, not as the root model. Selected stills remain the scoped visual references; use [the source-to-exhibit map](docs/exhibit-direction.md) for narrative anchors and media provenance. See the [dated alignment checkpoint](docs/murderbird-alignment-2026-09-27.md).
- Replit remains development preview only. A successful build or local-media integration does not approve a GitHub Pages release.

## Git synchronization

- GitHub `origin/main` is canonical; the Windows mirror and Replit are separate checkouts. Committing or pulling in one does not update the other.
- Before syncing, inspect `git status --short --branch`, then `git fetch --no-prune origin` and `git rev-list --left-right --count HEAD...origin/main`. Preserve uncommitted work and divergent branch tips before integrating.
- If only behind and clean, use `git pull --ff-only origin main`. If both ahead and behind, integrate on a review branch and use a PR; do not force-push or reset away work. A failed fast-forward is a request to inspect history, not to repeat the same pull.
- After a squash merge, compare trees and preserve the old branch tip before cleanup. Replit agent branches can have different commit IDs with identical content. Leave the `gitsafe-backup` remote intact.
- Refresh the Git panel after Shell operations. A stale unpushed-commit badge is not evidence of divergence; verify fresh Shell counts, exact GitHub SHA, and clean status. Confirm UI authentication separately if prompted.

## Replit connection status

As recorded for this migration on 2026-09-26, the Replit connectors for both relevant accounts report **UNAUTHORIZED**. No current remote synchronization is proven by connector access. Treat a Replit UI, Git panel, or shell as unavailable evidence until access is restored and the exact remote and commit are checked. Local preview instructions above remain valid; they do not prove a remote sync or publication.
