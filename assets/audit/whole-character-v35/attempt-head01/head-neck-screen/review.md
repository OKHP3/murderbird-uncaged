# Head01 discrete structural screen

The read-only Blender screens used the exact V35 head01 native: `assets/models/whole-character-v35/attempt-head01/murderbird-whole-character-v35.blend`, SHA-256 `5f7319fb656945f054781f5d515f036418a00abba17ab81490221dc945f6c6df` (3,441,577 bytes). The V34 comparison native is SHA-256 `3f4c12983feea5e4d45f5609d749c1dfa78ecdafc34936d3e702ffa403fed716`.

The adapted jaw/cap screen found **zero strict crossing pairs in all seven sampled states** (jaw at 0, .08, .16, .24, .32 rad; cover lift 0 and .08 m). The corresponding V34 screen also found zero in all seven. It checks evaluated head-subtree meshes, with active jaw- or cranial-cover-owned geometry against the remaining distinct rigid owners.

The adapted neck screen found these **six newly appearing distinct-owner pair identities** relative to V34’s zero-pair baseline:

- `V23 cervical 4 directional guard 2` × `V33 tapered throat cheek plate -1 0 0`
- `V23 cervical 4 directional guard 2` × `V33 tapered throat cheek plate 0 0 0`
- `V23 cervical 4 directional guard 3` × `V33 tapered throat cheek plate 0 0 0`
- `V23 cervical 4 directional guard 4` × `V33 tapered throat cheek plate 0 0 2`
- `V23 cervical 4 directional guard 4` × `V33 tapered throat cheek plate 1 0 0`
- `V23 cervical 4 directional guard 5` × `V33 tapered throat cheek plate 1 0 0`

They are strict evaluated-triangle edge-through-face witnesses between `cervical-upper` guard geometry and head-owned cheek plates, concentrated at the lower cheek/throat lap (for example, rest witnesses cluster around native x≈−0.03 to −0.07, y≈−0.43 to −0.45, z≈1.45–1.48 m; yawed views show the mirrored side). Five are present at rest, Maker-neck-jaw, attention, and both yaw samples; four at thrust-neck; none in the sampled contact-neck pose. Full witnesses, triangle indices, exact pose definitions, tolerances, and executed source hashes are retained in `neck/results/screen.json` and `comparison.json`.

**Disposition:** head01’s 1.16 head enlargement introduces a repeatable head-to-neck guard intersection set in these sampled poses even though its jaw/cap screen stays clear. This is evidence against treating the scaled head/cheek transition as a fitted assembly. The native’s Maker jaw socket metadata is not certified here; this is a mesh screen only, and any corrected module or composed native needs its own source-bound review. The finite discrete tests do not cover continuous motion, tangencies/coplanar contacts, full containment, or physical clearance.
