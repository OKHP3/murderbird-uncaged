# Current assets and deliverables

This is the editable navigation guide. The imported [source asset guide](README.md) retains its exact recorded bytes and historical descriptions under the CG import ledger. Current selections and checkpoint retirement are described here.

This directory holds MurderBird production material and selected files used by the exhibit. The story, artwork, models, video, music, and lyrics remain all rights reserved under [../NOTICE.md](../NOTICE.md); the repository's MIT license covers code only.

## Preserve imported source trees

Imported source and production material is retained under `murderbird/` at its original relative paths, including the `v2/`, stills, and production branches. Keep names, nesting, companion files, and embedded metadata intact. Do not flatten or rename source files to fit the app. Record each migration and any derived files in the repository's `provenance/` ledgers.

Use `assets/img/` for existing image paths and website-related images whose source paths must remain stable. Do not create a parallel `website-images/` tree. The `audio/` and `models/` directories contain recorded source or delivery packages; `images/` remains reserved scaffolding. Status comes from manifests and receipts; a placeholder, filename or folder name alone establishes no completion.

## Selected production packages and preserved history

Start with the root [selected-deliverable table](../README.md#selected-deliverables) for the three retained04 CG natives/exports and the V37 interactive package. Keep CG packed textures, native views, receipts and supporting files in their established source trees. The [CG publication manifest](review/cg-publication.json), [V37 runtime manifest](review/production-v37.json) and [media catalog](../docs/media-catalog.md) identify current selections and historical context.

- models/ retains versioned editable geometry and exports, including V37 and earlier studies.
- audit/ retains receipt-bound source packages, matched views and diagnostics; the retained04 CG natives remain here at their original paths.
- murderbird/ retains imported artwork, video, music and production hierarchy, including unresolved variants.
- img/, audio/ and images/ retain their existing paths and roles; changing navigation does not authorize moving or replacing source files.

Do not create a second asset tree or copy the archive into a new taxonomy. Add a deliberate derived runtime file only with its source/provenance relationship recorded.

## Historical checkpoint captures

The v4 [iteration](audit/alignment-v4/iterations/README.md) and [pre-yaw-wrap runtime](audit/alignment-v4/runtime-iterations/README.md) PNG/WebM capture sets are now available through an exact preserved Git commit instead of every current checkout. Their receipts, source snapshots and editable native/export inputs remain. The [retirement ledger](../provenance/checkpoint-retirement-2026-10-11.json) records all 399 paths and verified payload hashes; [frozen regression records](audit/regression-v4/README.md) keep their original meaning. This change reduces a hydrated checkout by 334,813,155 bytes and does not reclaim hosted LFS storage. Other checkpoints remain pending dependency and preservation review, rather than being classified as permanent keeps.

## Browser delivery and Git LFS

The Vite build copies files from `public/` into the distributable. Keep source archives, production sessions, private material, provenance records, and unrelated historical support files out of `public/`. An asset becomes a website dependency only through an explicit app reference or by placement under `public/`; verify the built `dist/` contents before publishing.

`.gitattributes` configures Git LFS for models, audio, video, Blender scenes, ZIPs, PDFs, and the imported image trees. Confirm that LFS is installed and available on the machine handling binary imports. Before relying on a LFS-managed asset in the deployed site, verify the remote contains the object and that a clean GitHub Actions checkout retrieves the actual asset. A committed pointer alone does not prove that visitors can retrieve the media.

Keep production state explicit. Preserve the source's recorded draft, working, or final designation, and use `unknown` when evidence is missing. A filename or file extension does not establish that media is finished, licensed for every use, or approved for publication.

## Historical exterior assessment study

`models/uncaged-exterior-v1/` preserves the versioned editable exterior proposal, combined runtime GLB, individual era exports, regional PBR maps and fixed fallback previews. See its [source/export guide](models/uncaged-exterior-v1/README.md). This earlier package is a preserved review study; current selected packages are listed above. It does not establish final character art. The subsequent owner instruction authorizes publication for independent assessment. Earlier `uncaged-*` model versions remain preserved. `audit/exterior-v1/` preserves review media and validation receipts from the local checkpoint. The explicit `review/exterior-v1-publication.json` selects only gallery images and the demonstration MP4 for the public review derivative. Raw receipts, source scenes and provenance stay in the repository; no audit directory is copied wholesale into the runtime.
