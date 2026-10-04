# Local static GLB export parity checkpoint

Unapproved appearance review; no publication or owner likeness acceptance claim.

Native input: `assets/models/cinematic-cg-milestone02b/murderbird-cg-2b-builder.blend`, SHA-256 `9ba7fc471a86e5f1f9b8db881900725f8abf56546c69fecb125a236ec5b4a64c` (hydrated from local LFS). Input file is never saved by the exporter.

## Callable APIs

- Blender: `export(scene, output_path)` in `scripts/cg-supervised-export.py` creates an exact-material batched static GLB. `batched=False` retains individual objects for the audit baseline. World transforms are baked into copied vertices; evaluated corner normals use the inverse transpose. Active texture UVs become channel zero, explicit shader UVMap references retain their names, unused historical UV channels remain in the native source. No material flattening, map resizing or source-pixel baking.
- Browser: `await createSupervisedReview(container, glbUrl, {lighting: 'neutral'})` in `scripts/cg-supervised-browser.js`. Returns `setLighting`, `setView`, `resetView`, `snapshot`, `resize`, `dispose` and scene/camera/model handles. Neutral/exhibit settings use the current Three.js exhibit presets; the review has no production integration.
- Preview: `npm run dev -- --host 127.0.0.1 --port 5177`, then `/assets/audit/cg-supervised-export01/review.html`.

## Evidence and limits

`fidelity-baseline-receipt.json`: native evaluated per-object material triangle coverage; mesh fingerprints and temporary-data cleanup. `export-receipt.json`: batched triangle coverage, UV corner readback, original fingerprints, cleanup, embedded material records. `inspect-parity.py` independently parses both GLBs without Blender and checks material triangle coverage, embedded image bytes and normalized PBR records; results in `independent-glb-parity.json`. Independent indexed UV value-set comparison is WARN: small float differences and some triangulation corner differences remain; exact cross-export indexed UV parity is not established. Native evaluated UV corner copying/readback passes.

Chrome actually loaded and displayed the static GLB under both lighting presets. This confirms real WebGL loading, not native/browser pixel equality. Exact glass volume/absorption, render lighting/color management and procedural nodes can differ between engines. This pinned source exports transmission, IOR and clearcoat; no volume extension is fabricated. Rig hierarchy, animation, device/accessibility qualification and owner artistic acceptance are outside this support task.

`npm ci` and `npm run build` passed; this isolated checkout retains unrelated LFS pointers for the baseline app assets, so the build is not release-ready. The export review/audit files are absent from `dist/`; no `public/` changes, remote CI, deployment, purchases or publication occurred.
