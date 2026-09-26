# Replit media handoff

The target project is
[murderbird-uncaged](https://replit.com/t/overkill-hill/repls/murderbird-uncaged).
The website project and FoundRy project keep their separate roles.

Before incorporating this migration, inspect the Replit branch and working
tree, fetch GitHub, and compare exact revisions. Preserve local work before
integrating. Use the reviewed migration branch or its eventual merged `main`
revision. A local Mac transfer does not update Replit.

After integration:

1. Retrieve the Git LFS objects and run `python3 scripts/verify-media-import.py`.
2. Read `docs/media-catalog.md`, `docs/repository-boundaries.md`, and `NOTICE.md`.
3. Run `npm ci` and `npm run build`; verify source archives are absent from
   the `dist/` output.
4. Use the existing app as the exhibit foundation. Choose reviewed image,
   video, and music delivery copies through explicit imports or `public/`.
   Preserve source files and record derivative relationships.
5. Keep the origin story's public link. Clearly label the fictional creature,
   procedural model, instrumental demo, and any unfinished production work.
6. Keep playback user-controlled, retain keyboard access and the illustrated
   fallback, and verify the app on a small screen before release.

Do not import `.local/` archives into Replit or publish this app using Replit
hosting. GitHub Pages remains the configured deployment path. The private
Mac archives include machine-specific environments and personal context, not
additional public app inputs.
