# Head02 discrete structural screen

The exact head02 native is `assets/models/whole-character-v35/attempt-head02/murderbird-whole-character-v35.blend`, SHA-256 `eb2e121af642d0620f062da4c3ecf11d0fbce121fef1f62f29d9b2c53f537d94` (3,441,880 bytes), matching the saved receipt.

- **Jaw/cap:** zero strict pair identities in all seven jaw/cap states; V34 baseline was also zero.
- **Neck:** zero strict pair identities in all seven states: rest, Maker neck/jaw, attention, contact-neck, thrust-neck, and both yaw directions. V34 baseline was zero across the same states. This clears the six upper-neck-guard/throat-cheek pair identities observed after head enlargement in head01 for these discrete samples.
- **Throat/bow:** the bounded rest check found zero strict crossings among 18 tapered throat cheek plate meshes and 2 passive cranial load bow meshes. Both sets are parented to `head`; therefore the extra cranial-cover local Z offsets in the script did not change their relative positions and must not be treated as articulation coverage. The rest-only adjudication is preserved in `adjacent/owner-adjudication.json`.

This is bounded geometry evidence for the exact head02 native. The mesh screens do not verify the corrected Maker jaw socket metadata or its runtime consumer alignment. They also do not prove continuous clearance, full containment, or physical behavior. No export or browser check was run. Exact poses, pair results, witnesses, tolerances, script hashes, and the head01 comparison are in `comparison.json` and the nested screen outputs.
