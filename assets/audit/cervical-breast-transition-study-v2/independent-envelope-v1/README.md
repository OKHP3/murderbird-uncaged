# Cervical-breast transition V2: independent four-state review

The saved V2 native was inspected without modification. Its rest pivot hierarchy matches both source14 and source07 exactly across 52 pivot names, parent assignments, local rest matrices, and world rest matrices. The source14 native is `ef9e28ddbce9d62aabc8181a058640ea1e8b7a339b673df37b913d96699f9440`; source07 is `751d8149032941774c6ba31824c76f6fa840bb0d767e433bae8000535f3a2b98`; V2 is `f98d4a5a3dbed932b82ac1abc82e51dc79356321a3a9292ed718749387c403a8`.

I visually compared the matched before/after three-quarter, profile, and neck views with Candidate03. V2 improves the continuous curved neck-to-breast transition over V1. The broader lap plates still read coarse and repetitive, and the close view exposes internal backing and frame through the open throat. This is an independent review, not approval. Candidate03 image identity: `538c51bcdbf5bfce95a0932fdbbb0f5868b446f4985346d15e6cacd32430e633`.

The four pinned states were `runtime-rest`, `advanced-contact`, `advanced-recovery-entry`, and `inspection-open-1-separation-0`. They come from the existing Node-derived 21-state controller packet (SHA-256 `1cb4a2f75ecae625a44c768ba543e9b99e1caa9791a3056e20f5d88bd73d2f26`) and the 41-state inspection packet (SHA-256 `3ae1b5a0f81adcb70a567e66c906c4631eebf75758171fc7aeddc7bdf8033781`). These are deterministic module-generated matrix packets, not browser captures. After C⁻¹ · browserMatrix · C conversion, maximum world-matrix application error was below `2.4e-7` for every state. Profile and neck close views were rendered for contact and fully open breast inspection.

The focused triangle-overlap screen reports these prominent candidates:

- At contact and recovery, `Cervical flank lamina -1 1` / `Cervical flank lamina 1 1` overlap the head-parented `Coaxial mandible journal` / `.001` by 150 / 146 triangle pairs. These upper guard-to-journal interactions warrant close review near the jaw hinge.
- `Cervical flank lamina -1 4` / `Cervical flank lamina 1 4` overlap the `Cervical intermediate axle -1` / `+1` surfaces by roughly 147–156 triangle pairs in all four states. These span the neck/cervical-upper owner boundary.
- `Throat formed lamina 6` and bilateral flank course 6 overlap the breast-owned yokes at rest/contact; at fully open inspection, the flank course 6 still overlaps its yoke by 158 triangle pairs. At open inspection, the breast inner access shell also has overlap candidates with flank course 6 and both yokes (up to 190 pairs). This may obstruct the intended breast opening and should be resolved by owner-aware motion/geometry review.

The BVH reports triangle-surface overlap pairs, including deliberate lap/contact. Counts are candidate intersections, not severity scores; the screen does not classify intended bearing contacts automatically. It cannot detect complete solid containment and does not certify continuous clearance or physical construction. The two actual-state render pairs are linked below; no pose matrix beyond these four states was run. No native, app, or GLB was changed.

- Contact profile: [image](advanced-contact-profile.png)
- Contact neck close: [image](advanced-contact-neck-close.png)
- Breast-open profile: [image](inspection-open-1-separation-0-profile.png)
- Breast-open neck close: [image](inspection-open-1-separation-0-neck-close.png)
- Machine-readable result and all tested pair counts: [review.json](review.json)

The exact executed script snapshot is `executed-review.py` (SHA-256 `e7f90b280f6d8180d9d814a29f626b8f048da8dbb512a6c528f8349d15978e6e`). A first preflight attempt rejected the runtime packet's extra scene/mechanism transforms; its script snapshot is retained under `preflight-failure-01/`. The successful run filters packet rows to the exact native pivot names while requiring all 52 native pivots to be present.
