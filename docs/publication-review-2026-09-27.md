# Assessment publication — exterior v1

The owner explicitly requested: “Let’s get it all published so that the other agents can perform their own assessments.” This authorizes source/evidence publication and an accessible exhibit/review release. It does not approve the artistic result or authorize private archives.

## Review entry points

- Current three-era exhibit: <https://okhp3.github.io/murderbird-uncaged/>
- Reference comparisons, close-ups and continuous motion: <https://okhp3.github.io/murderbird-uncaged/review/>
- Preserved story/media folio: <https://okhp3.github.io/murderbird-uncaged/folio.html>
- [Editable model and era exports](../assets/models/uncaged-exterior-v1/README.md), [regional inheritance/attachments](exterior-regional-map.md), [surface pipeline](exterior-surface-pipeline.md), and [historical checkpoint assessment](exterior-stage-record.md).

The gallery prints the full build revision and links sources at that immutable revision. GitHub Actions must complete its Pages deployment and the public edge must serve that revision before a live-publication claim is valid. The comparison evidence remains explicitly tied to `5016f7573319a9152f3592e1019ca5e556e52056`.

## Exact model and preserved concurrent work

The reviewed combined GLB is **16,956,956 bytes**, SHA-256 `3ec668b0b9bbaf1cb546ec2e04b09030c5f45b0f0893adc5b7fe5aa57baacdc5`. Publication integration does not regenerate its geometry or surfaces. Maker remains externally operated, Mechanic mechanically stepped, and Advanced coordinated. The earlier folio reconstruction is separately identified; it is not substituted for this model.

Remote `main` at `fa020f88835b50971f701206f4283b216ff55645` had concurrent story stills, media controls, lyrics and a different presentation. Those are preserved under `folio.html` with their own styles and fallback. The current model stays at the root. Shared audio retains both interfaces. Navigation links the exhibit, folio and assessment gallery.

The imported `docs/murderbird-unified-direction.md` is restored to its original recorded hash. Current flightless/three-era clarifications remain in `creative-authority.md` and their dedicated records. This repairs source-byte verification without deleting the newer direction or altering story canon.

## Explicit delivery boundary

`npm run build` builds both Vite entry pages, then creates the allowlisted review derivative. The gallery manifest pins 82 unique media files (81 PNG images and one MP4), totaling 49,808,261 bytes. It produces 83 image elements, matched comparisons, the 114.88-second motion demonstration, and source/evidence links. It ships no editable Blender scenes, raw receipts, provenance ledgers, archive trees or private sessions. Those eligible public sources remain accessible in GitHub rather than copied into Pages.

The separately pinned 12 story-folio imports include eight WebP stills, the First Choice poster/video and two distinct historical audio demos. The original theme release remains visitor-started. The old CI audio failure was an exact-allowlist mismatch: it expected only the two theme files despite the folio importing two additional MP3s. Validation now checks those two exact approved demo hashes, not arbitrary extra audio.

## Reproduction and evidence

Run `npm ci`, `npm run build`, `node scripts/verify-theme-release.mjs`, `node scripts/verify-publication.mjs`, `python3 scripts/verify-media-import.py`, and `node --test tests/*.test.mjs`. The publication validator verifies the unchanged model, fallback renders, exact folio media and complete runtime boundary; the review generator independently checks the pinned gallery inputs and exact output list. GitHub Actions uses clean LFS-enabled checkout and validates Node 24 and 26.

`verify-publication-browser.mjs` takes an existing Playwright module path; `PUBLICATION_URL` selects local preview or the actual public base. It records public-control WebGL, fallback, folio media and mobile-layout observations under ignored `.local/publication/`. Analytics is stubbed during automated browser QA. Local results do not prove hosted delivery; verify the exact Pages run/SHA and fetched GLB hash separately. No Replit publication is used.

## Open assessment questions

This build does not yet meet the full artistic criteria. Assess crown/bill identity, broad folded-wing contour, breast taper/panel rhythm, leg/foot construction, and physically motivated wear placement against the selected references. July remains head-only. New hidden surfaces, repair topology, material history and mechanism details remain proposals. Passing kinematic, export or browser checks does not certify physical simulation, continuous collision freedom, phone performance or artistic acceptance.
