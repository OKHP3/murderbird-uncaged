"""Retired entry point for the frozen exterior-v1 build boundary.

The former script checked a fixed 28-file dist tree and overwrote the pinned
exterior-v1 asset receipt. Current builds have a dynamic release manifest.
Run scripts/verify-publication.mjs after npm run build instead.
"""
raise SystemExit(
    'Retired historical validator: run `npm run build` and '
    '`node scripts/verify-publication.mjs` for the current release inventory.'
)
