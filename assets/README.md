# Assets

This directory holds MurderBird production material and selected files used by the exhibit. The story, artwork, models, video, music, and lyrics remain all rights reserved under [../NOTICE.md](../NOTICE.md); the repository's MIT license covers code only.

## Preserve imported source trees

Imported source and production material is retained under `murderbird/` at its original relative paths, including the `v2/`, stills, and production branches. Keep names, nesting, companion files, and embedded metadata intact. Do not flatten or rename source files to fit the app. Record each migration and any derived files in the repository's `provenance/` ledgers.

Use `assets/img/` for existing image paths and website-related images whose source paths must remain stable. Do not create a parallel `website-images/` tree. The existing `audio/`, `images/`, and `models/` directories remain future organization areas for approved working or delivery copies; their `.gitkeep` files do not indicate that finished media is present.

## Future organization areas

- `audio/` — organized theme-song stems, mixes, and interaction sound effects.
- `images/` — organized concept art, working images, and reference stills when a copy is needed for app work.
- `models/` — organized geometry, rigs, and exported GLB/GLTF models when a copy is needed for app work.
- `murderbird/` — preserved imported source and production hierarchy; retain historical versions and their supporting files.
- `img/` — existing source-relative and website-related image paths; preserve import paths and references.

Video and additional deliverable types should remain in the preserved `murderbird/` hierarchy unless a documented application need establishes a separate path. Do not create a second source archive just to match a proposed folder taxonomy.

## Browser delivery and Git LFS

The Vite build copies files from `public/` into the distributable. Keep source archives, production sessions, private material, provenance records, and unrelated historical support files out of `public/`. An asset becomes a website dependency only through an explicit app reference or by placement under `public/`; verify the built `dist/` contents before publishing.

`.gitattributes` configures Git LFS for models, audio, video, Blender scenes, ZIPs, PDFs, and the imported image trees. Confirm that LFS is installed and available on the machine handling binary imports. Before relying on a LFS-managed asset in the deployed site, verify the remote contains the object and that a clean GitHub Actions checkout retrieves the actual asset. A committed pointer alone does not prove that visitors can retrieve the media.

Keep production state explicit. Preserve the source's recorded draft, working, or final designation, and use `unknown` when evidence is missing. A filename or file extension does not establish that media is finished, licensed for every use, or approved for publication.
