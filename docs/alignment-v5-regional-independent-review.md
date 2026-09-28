# Historical independent visual review: candidate02

This review and its image evidence concern candidate02 only. Candidate04 has its own identity-bound assessment in [alignment-v5-regional-candidate04-independent-review.md](alignment-v5-regional-candidate04-independent-review.md); do not treat candidate02's aesthetic findings or motion receipts as candidate04 results.

**Assessment: revision-required.** The selected regional candidate improves the leg armor’s plate reading, but the feet still do not carry the broad, flattened hooked-claw character of Candidate03/Maker. This is a fixed-camera native geometry review only; it does not accept final likeness or dynamic behavior.

## Export-parity adjudication

An earlier follow-up interpreted the first direct GLB comparison as loss of retained rear-hallux geometry. That interpretation is superseded; the original comparison receipt remains preserved at `assets/audit/alignment-v5-regional/export-parity-v2/`, and the original note is retained in [rejection-note.superseded.json](../assets/audit/alignment-v5-regional/rejection-note.superseded.json). Its raw batch-count difference was real, but its expected partition was wrong: each base foot-edge batch contained 1,080 triangles, of which 804 came from three 268-triangle ankle sheath lap ribs explicitly removed by the guard-study05 replacement manifest. The retained rear hallux sheath and two foot axle caps contribute 276 triangles per side.

The [corrected direct GLB parity report](../assets/audit/alignment-v5-regional/export-parity-final/regional-export-parity-8f8ec3290eba.json) uses the exact frozen native base geometry for those six retained objects and checks their actual world-position clouds against candidate `8f8ec329…d7f1ee`. All 90 owner/era/region/role/material groups pass: expected and candidate each have 232,660 triangles, 117,573 unique world positions, and 697,980 vertex occurrences. The six retained edge pieces match with zero unmatched positions; all 51 pivot world matrices match exactly; every runtime mesh is classified. The [edge-partition audit](../assets/audit/alignment-v5-regional/edge-partition-audit/retained-foot-edge-source.json) binds the source objects, six replaced ribs, manifests, and model hashes. This supersedes only the earlier export-loss interpretation. The original raw comparison is not erased.

Export parity does not change the visual assessment below. The fixed-camera native images still support **revision-required** for the instep ridge massing and broad, flattened hooked-claw character; this is not final likeness or human acceptance. The motion receipts remain separate evidence and are not used as a substitute for either geometry parity or visual review.

## Compared assets

The selected candidate is `assets/models/uncaged-alignment-v5-regional/candidate/murderbird-v5-sixth-guard-talon-study.glb` (SHA-256 `8f8ec3290eba430d17af0f2f50fe24fa3ba318e783869d0e8ad08dcf87d7f1ee`) with native source `murderbird-v5-sixth-guard-talon-study.blend` (SHA-256 `919c924055e35431cd3b2d7019349399e048b9d784c173a59c5066ee1f192702`). The comparison base GLB is c8 sixth: `1e7febcc03d9f8d1a644580c8422b124403cf4e5768aa01df747e3d9b6af9f1e`.

Each paired render below uses the same camera location, target, orthographic scale, renderer SHA (`88615d68b2f8fc753e5771cfeeb94295d5f5c12771d0eded464cb720b7edee0b`), and neutral `builder` era. Thus base-to-candidate differences in these pairs are suitable for a static visual comparison.

Base renders are in `.local/alignment-composed-study/render-base-sixth-v2/`; selected renders are in `assets/audit/alignment-v5-regional/native-builder/`. Their camera and image hashes are recorded in each directory's `views.json`.

| Matched view | Base image SHA-256 | Selected image SHA-256 |
| --- | --- | --- |
| `full-three-quarter.png` | `9bb33e0545ebb534de7f1a80fbb4a455d37ef966fcc3772cf7ce2194097ba6fd` | `1461ed427401116746b25ae0e9acd79d48a8d2076f9e219978ea599461a30e28` |
| `full-side.png` | `499cb03d1afa44a4faf2caaff1bad121f88ce309963fe2e4ae50028e4c945def` | `5b573ae8ffafe03ec1b8de0c9e4c7e14bcb65b99620fcdddf21f1132541cda75` |
| `limbs-front.png` | `128bef2b6ecdcfa8f28172d18f5721e8d6f74a7863ade3c8036e663d834b5226` | `185bd03bb3538e7a5364722df83264485f92ea601653e1466d63b53ae0f05a28` |
| `limbs-three-quarter.png` | `2ebfad4097eec2bc448cd4d67b3fc53ffa679b552fe1a5b78ec3e29b518a443b` | `6d3f561c5ee12182f8c60d97b7b7073a1d235df159a3a9162e40c66574cae445` |
| `feet-three-quarter.png` | `4745ff2d7f531554a62d55a294c211849f2b706fae048e5bad5c8a5933b0b376` | `e77abd331617d45191def629e740e62fcbd8a57b46c0ad1ef58d940a5d237f01` |

Context references are not camera-matched renders: Candidate03 master image `assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png` (SHA-256 `538c51bcdbf5bfce95a0932fdbbb0f5868b446f4985346d15e6cacd32430e633`), Maker feet close-up `assets/audit/alignment-v3/maker-feet-closeup.png` (SHA-256 `02c339f2e09d7f7a7f7b9f14b0fc16a5b66ec8d9fa3c868a07284f1abc0d90ac`), and Maker raised-foot view `assets/audit/alignment-v3/maker-feet-extreme.png` (SHA-256 `a0ef8444e68ddf8120c4c59277da022bd885377279183a84990a30acdb5c11f5`). They inform visual vocabulary, not pixel-aligned measurements.

## Findings

The ten replacement guards improve the thighs and shins over the base’s mostly cylindrical sleeves: the selected front and three-quarter views show tapered front plates with distinct overlapping sections, while leaving the knee and ankle bearing forms visible. The upper/lower limb transitions now read as applied armor panels instead of one continuous tube. The selected instep guards also give the ankle-to-foot transition a visible plate surface.

The instep remains over-fluted. Four prominent lengthwise ridges dominate the small foot shell and make it read as a corrugated cover. Maker’s reference shows a broad, smoothly crowned dorsal shell with a clear outer edge. Reducing the ridge count and height would bring the guard closer to that massing while retaining its current articulation clearances for later motion review.

The talons still read largely as round, swollen-root tubes. The candidate side and foot views show hooked tips, but the cross-section change is modest at normal viewing distance; Candidate03 and Maker show broader, flatter blade-like claws that sweep to a distinct hook. The talon bases in the candidate remain rounded and visually bulky, so the selected profile is an improvement over its study base but does not yet resolve the defining claw-shape difference.

The full-side pair confirms the guard changes do not alter the overall stance or body envelope. In that view, the new guard coverage is less legible than in the closer limb renders and still appears as narrow inserts over exposed structural members. A later visual pass should evaluate shell width and continuity from side angles, without hiding the joints or assuming a mechanical enclosure requirement.

## Evidence boundary

This review used the five matched image pairs above plus the separate reference images; it did not use helper tests as a substitute for visual inspection. Separate exact-candidate runtime and motion receipts are recorded under `assets/audit/alignment-v5-regional/` and do not change these visible shape findings. The image evidence supports a regional visual revision assessment only, not final model acceptance, dimensional accuracy, mechanical certification, or runtime approval.
