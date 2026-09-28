# Alignment v6 era-eligibility audit

**Result: no actionable era misclassification proven in the current visible geometry.** Scope is the inventory-bound v6 candidate GLB, SHA-256 `dbc90402e3fe73c150e40ec51a37af2bbed6a474962b69acfd3491dbbb7764eb`, and the source-level visibility rules in the current local app. This is a read-only classification audit, not visual acceptance or a browser run.

## Evidence

The [v6 inventory](../../models/uncaged-alignment-v6/alignment-inventory.json) contains 703 native mesh parts. Every part has an explicit `eras` list:

| Construction class | Count | Era eligibility | Representative owners and parts |
|---|---:|---|---|
| `inherited-passive` | 667 | Maker, Mechanic, Builder | body, breastplate, head, cranial-cover, neck, mantle, wing shields, legs, feet, passive optic seats |
| `advanced-system` | 35 | Builder only | power-core 9, processing 24, builder-optics 2 |
| `later-repair` | 1 | Mechanic and Builder | `Proposed later left bearing strap v4`, owned by `industrial-repairs` |

The app reads each exported mesh's `exteriorEras` and sets visibility from that tag in [`presence-exhibit.js`](../../../src/scene/presence-exhibit.js). The additional assembly gates agree: the power core, processing assembly, and `builder-optics` pivot are Builder-only; `industrial-repairs` is shown in Mechanic and Builder. In [`era-mechanisms.js`](../../../src/scene/era-mechanisms.js), the Maker cradle/controls, Mechanic wound drive, and Advanced distribution/actuation are separate groups, and only the selected era group is visible.

## Checks against the three concerns

- **Maker active hardware:** no self-powered internal system is tagged for Maker. The only Maker-specific visible mechanism is the separately generated external cradle and control rig, matching the documented fixed, externally operated Maker capability. Passive bearings and joints remain shared structure; their shape alone does not establish an engine.
- **Mechanic Advanced optics:** the two active `Seated Advanced optic` parts are `builder-optics` children, `advanced-system`, and eligible only in Builder. The Mechanic-visible `Recessed orbital bearing` and `Seated passive optic housing` parts are passive socket structure, consistent with the regional map's “no powered sensor implied” boundary.
- **Inherited body missing in Advanced:** all 667 `inherited-passive` parts, including the complete body, breast, neck, shoulder/wing, leg, foot, head, and passive optic structures, include Builder eligibility. The runtime applies the exported tags before its explicit system gates, so no inventory-level exclusion of the inherited body is present.

These classifications match [creative authority](../../../docs/creative-authority.md), [three-era construction direction](../../../docs/three-era-construction-direction.md), [structural construction contract](../../../docs/structural-construction-contract.md), and [exterior regional map](../../../docs/exterior-regional-map.md): external Maker operation; a distinct constrained Mechanic drive with later repair; Advanced-only power, processing and active sensing; and passive inherited structure retained across eras.

The source documents note that a generic `inherited` metadata flag can be wrong on some Advanced additions. This audit used the explicit `eras` / exported `exteriorEras` field and `constructionClass`, which control current visibility; neutral materials were not treated as an eligibility signal. Appearance finish, historical surface age, detailed mechanism plausibility, and owner approval remain outside this finding. No mismatch justified a code or geometry change.
