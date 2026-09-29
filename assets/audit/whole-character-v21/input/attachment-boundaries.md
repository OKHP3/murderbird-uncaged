# V21 attachment boundaries

Read-only native inventory for planning the coupled breast/neck reconstruction. Source: V20 Runtime 02 native, SHA256 `eb15a9d87de56fb8a06004d9c69448c38089f0ecacd888e3e7fde921a353d42a`; its export receipt records 52 pivots. Coordinates are metres, +X anatomical left, -Y forward, +Z up. Exact transforms, owner counts, selected mesh names, and local bounds are in [`attachment-boundaries.json`](attachment-boundaries.json); the extractor is [`inspect-attachment-boundaries.py`](../../../../scripts/inspect-attachment-boundaries.py).

| Node | Parent | Rest world position (X,Y,Z) | Relevant direct mesh ownership |
|---|---|---:|---|
| `body` | `murderbird` | `(0, -0.005223, 0.880091)` | Fixed body structure: two thoracic load rails, four passive ribs, fixed access liner and bottom hinge bearings/supports; also lower/outboard breast courses. |
| `breastplate` | `body` | `(0, -0.171400, 0.847402)` | Moving access shell, 72 directional breast laminae, keel returns, fasteners, moving axle and two cover returns. Its current authored inspection transform is local `+X`, `1.1 rad`. |
| `neck` | `body` | `(0, -0.219252, 1.283504)` | Lower cervical flank/throat courses 4–6, lower backing, passive fork/clevis, and posterior laps 4–6. |
| `cervical-upper` | `neck` | `(0, -0.355836, 1.412866)` | Upper cervical flank/throat courses 1–3, inner guard, curved load rails, axle, and posterior laps 1–3. |
| `head` | `cervical-upper` | `(0, -0.418525, 1.510600)` | Brow, cheek bands, mandible journals and passive optic housings. |
| `cranial-cover` | `head` | `(0, -0.418525, 1.510600)` | Crown and temporal shell/laminae; shares the head rest transform. |
| `jaw` | `head` | `(0, -0.384782, 1.647307)` | Two forged mandible halves, distal bridge and journal caps. |
| `upper-bill` | `head` | `(0, -0.418525, 1.510600)` | Upper bill blades, nasal hood, cere transitions and proximal cheek plates. |
| `builder-optics` | `head` | `(0, -0.418525, 1.510600)` | Advanced-only optic meshes. The passive optic housings remain directly head-owned. |

## Coupled envelope implications

- The breast access shell and fixed body opening are separate assemblies. Any reshaping must account for both sides of their seam: moving `breastplate` geometry plus body-owned liner, ribs, rails, bearings, hinge supports and fixed lower courses. Keep the designed opening path and restore the closed mating relationship; the present shapes are not approved constraints.
- The lower neck is split across two independently articulated owners. `neck` owns courses 4–6 while `cervical-upper` owns courses 1–3 and the head chain. A continuous exterior can lap across that boundary, but a rigid bridge cannot bind those owners. Check the free-edge relationship at both neck joints and through the breast opening.
- `head`, `cranial-cover`, `jaw`, `upper-bill`, optics and processing are separate descendants. Reprofiled skull/crown surfaces must retain their respective clearances and not transfer the jaw, bill or optic geometry to a different pivot implicitly. If a pivot moves, preserve intended visible shape with explicit child-transform compensation and obtain fresh motion samples.
- Maker/Mechanic/Advanced motion hardware is generated separately by `era-mechanisms.js`; it is not evidence that the passive surfaces fit. The V20 `mechanismLayoutV1` cervical body/neck socket points are owner-local proposals. If the new envelope changes their bearing/contact surfaces, re-seat/review them even when the node transforms are unchanged. Preserve era eligibility: shared structure may be passive; power, sensing and internal Mechanic/Maker hardware retain their existing gates.

This packet records the V20 proposal's current ownership and transforms, not a requirement to retain its plates, guards, frame, or silhouette. It does not establish surface continuity, collision clearance, support strength, or artistic acceptance. V21 geometry and its new pivots must be inventoried from the actual saved candidate before using these boundaries as current evidence.
