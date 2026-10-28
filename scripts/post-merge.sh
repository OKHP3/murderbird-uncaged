#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

node scripts/ci-lfs-assets.mjs hydrate --scope=build
npm ci --no-audit --no-fund
npm run build
