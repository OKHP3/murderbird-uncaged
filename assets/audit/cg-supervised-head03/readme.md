# Source-head03 — stopped after two design attempts

**Visual status: FAIL / not recommended for promotion.** Source landmark proportions improved, but this is not yet a convincing coherent match. The first attempt's open skull revealed the far optic; the second closes that vault and reduces the orange optic to a small core. The broad brow return still reads as a smooth roof, crown feathers as blade-like cards, and the cheek volume as sparse. No third design attempt was made.

## Scope and source

Base `be2ee153e1367085b30080e9280338ba92cfaff0`; shared goal read at `origin/main` `251f2f0243181e97140179c2aff6eb057e165438`. API: `scripts/cg-supervised-head03.py`, `apply(scene, root_path=None, era='builder')`. Input is preserved head-neck01+shoulder01 attempt01 native, SHA-256 `e5fc6a39662bcb7f5ab82679dd719757edc4f0f39fc3cc5ae433bae962409d43`. Rejected face02 is neither loaded nor retained.

July controls head only: `47658dba6496f2c8594a40ad412a8bfaa087939e90044d1597329a27ca68d4e9`. Full-bird canon: owner-reissued JPEG `645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114`. Both verified before use. No July body, wings or stance was copied. Contours were individually traced in source pixel coordinates; transverse depth and hidden construction are inferred. All creative content remains all rights reserved.

## Visible evidence

Open `review.html`. `before-head-neck.png` / `after-head-neck.png` are uncropped 1100×1100 head comparisons; full-bird before/after are 1100×900. Both states use identical neutral lighting and cameras. Head orthographic scale widened equally from .85 to 1.12; location, rotation, shift, lens and lighting are recorded in `receipt.json`. No exposure or light change masks the geometry result. First-attempt images/native/script are preserved in `attempt01/`.

Gains: larger nested optic seat, deep leaf-shaped upper bill with backward tip, diagonal upper brow, thinner downturned inner jaw and varied pointed posterior plates. Regressions: planar side faces and excessive smooth dorsal bridge; overall head still looks assembled from cards. These findings are worker judgment, not owner acceptance.

## Validation

PASS: Python parse; Blender application/save/render; exact source hashes; 6,114 original meshes and 9 empty anchors preserved. Geometry, world matrices, parents, custom properties, UVs, color attributes, material slots/indices and modifier names/types compare unchanged. Visibility changes are confined to original head meshes. No neck, shoulder, body, leg or foot objects changed. `preservation.json` contains the result and native hash. All 111 new meshes have JSON `cgSurfaceFamilies` aligned with slots; optic families remain protected. Maker/Mechanic lens/core emission tested at zero.

NOT RUN: browser/WebGL/fallback integration, app build, export parity, CI or deployment; no runtime files changed. Owner likeness acceptance remains pending. Root integrator owns any further branch integration or remote synchronization. Stop this construction direction here; a subsequent source-specific volume redesign needs a fresh bounded assignment.
