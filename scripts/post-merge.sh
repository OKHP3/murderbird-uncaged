#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

# Runtime media lives flat in media/. Fetch that folder and the theme audio in public/audio; history stays unfetched.
git lfs pull --include="media/*,public/audio/**" || echo "Git LFS media unavailable; the build will report what is missing."
npm ci --no-audit --no-fund
npm run build
