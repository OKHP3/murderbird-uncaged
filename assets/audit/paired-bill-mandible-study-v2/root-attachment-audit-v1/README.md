# Bill-root attachment audit

This bounded read-only native audit compares the V8 source, its bill-section V2 derivative, and the paired-bill/mandible V2 study. Exact file hashes and detailed per-mesh measurements are in [root-attachment-audit.json](root-attachment-audit.json). Three raw evaluated-mesh proximity outputs and three containment outputs are preserved alongside it.

## Bill-root fixings

All four `Bill root fixing` meshes are identical in geometry and world transform across the three files. Their extents are small: roughly 5 mm wide, 7 mm deep, and 6.7 mm high. The actual evaluated `Profiled upper bill blade 0` is a closed mesh (zero boundary or nonmanifold edges), as are the root-fixing meshes. Across four non-axis ray directions, each of every pin's 20 vertices, 12 face centers, and center point classifies inside the blade volume; the BVH surface-pair broad phase finds zero pin-to-blade face candidates. The evidence supports the fasteners being fully buried, rather than suspended across an exterior gap.

The sampled blade surface lies 5.57–6.06 mm from the root fixings in V8 and 12.22–13.15 mm away in bill-section V2. The paired-bill V2 study retains that depth. On the anatomical right side (-X), the sampled blade surface shifts from x about -0.0783 m in V8 to -0.0852–-0.0873 m in the section-derived versions while the pin stays centered near x=-0.071 m. This points to the bill-section cross-section redistribution as the step that further covers the unchanged fixings. Anatomical left is +X. If the fixings are meant as visible bearing heads, the current assembly hides them; if they are internal anchors, this is consistent with that intent. The evidence does not decide that design intent.

## Stationary root seams

`Profiled upper bill blade 0` and `Overlapping nasal hood` are essentially touching in the sampled rest geometry (about 0.02 mm) with 58 broad-phase face-pair candidates in the later versions. Blade 0 and each `Cere root transition` are about 0.001 mm apart with 35 broad-phase candidates per side in the two section-study files; V8 had a 5.59 mm sampled separation and no candidates. These are plausible seated/lapped joints. Candidate counts alone cannot distinguish proper crossings from shared boundary or coplanar contact.

Two small seams remain measurable: blade 0 to blade 1 is about 1.08 mm in paired-bill V2 (2.03 mm in V8 and bill-section V2), and the nasal hood to each cere transition is about 0.84–0.88 mm across all three files. Neither pair produces broad-phase surface-pair candidates. They may be intentional panel breaks; if a continuous closed surface is required there, the seams need owner review.

The audit uses evaluated native meshes and finite vertex/edge-midpoint/polygon-center distance samples. It does not prove strict triangle crossings, complete solid containment, all-head collision clearance, motion behavior, manufacturing tolerance, or owner acceptance. It does not modify any model or existing evidence.

For a later isolated reseating study, the fixings' local X basis is exactly native/world X; their geometry is near-isotropic (5.0 × 7.0 × 6.7 mm), so this is an object-transform axis rather than a long shaft. Rays along signed outward X from the pin centers meet the corresponding blade side wall 15.64–16.00 mm away in paired V2, with wall normals nearly parallel to the rays (dot 0.990–0.997). This supports ±X as a direction for a proposal, but no reseating or geometry change was performed.
