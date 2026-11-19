#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

# Runtime media lives flat in media/. Fetch only that folder; history stays unfetched.
git lfs pull --include="media/*" || echo "Git LFS media unavailable; the build will report what is missing."
npm ci --no-audit --no-fund
npm run build
