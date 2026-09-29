# V35 Form01 head and neck screen

The exact combined native is `assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend`, SHA-256 `d2c704ccf89f3f0e7dbeb3613dcdbdd964c4ba69991783783830803eecf59cb0`.

## Discrete geometry results

- Jaw/cap screen: **0 strict pairs** in seven samples: jaw deltas 0, 0.08, 0.16, 0.24, 0.32 rad; cap local-Z lifts 0 and 0.08 m. The screen compared the jaw/cap subjects against the 140 head-subtree meshes. See [screen result](head/screen.json), [executed checker](head/executed-head-check.py), and [Blender log](head/blender.log).
- Neck screen: **0 strict pairs** in seven prescribed states (rest, Maker neck+jaw, attention, contact neck, thrust neck, yaw−, yaw+), across the 40 cervical guards/root underlaps against adjacent assembly owners. See [screen result](neck/results/screen.json) and [executed checker](neck/results/executed-screen.py).
- Separate same-owner-adjacent check: **0 strict pairs at rest** between 18 head-owned tapered throat cheek plates and 2 head-owned passive cranial load bows. This is a distinct-mesh, rest-only pair screen; it is not a within-mesh self-intersection test. See [screen result](adjacent-rest/screen.json) and [executed checker](adjacent-rest/executed-rest-cheek-bow-check.py).

The jaw/cap and neck checks use the same frozen strict noncoplanar edge-through-face kernel (SHA-256 `b290574245203be09e4eb1e76dba44c1cb9c174b540b962bfef404d2424ee84a`; plane epsilon `1e-7`, edge/barycentric margin `1e-6`). They test only the listed discrete configurations. They do not establish clearance between samples, containment, contact quality, or physical behavior. The cheek/bow comparison is between two mesh groups with the same `head` rigid owner; cranial-cover lift values are not applicable to that check.

## Independent visual read

Reviewed the actual [reference-angle render](../after-reference-angle.png), [front render](../after-front.png), and [rear render](../after-rear.png) against the owner’s [whole-bird reference](../../../../../context/threads/assets/murderbird-owner-likeness-rejection-2026-09-28/2-Pasted-Image-2.jpg). The reference-angle view has a more coherent hooked bill, layered crown, continuous throat, and deliberately layered breast than earlier iterations. The front view has a recognizable bilateral arrangement, but the face reads as a long narrow mask, with the optic mostly lost from this view; the chest still forms a smooth, symmetric armored egg. The rear view exposes a broad plain torso shell and prominent straight center seam, while the reference carries dense mechanical layering across the body. In the full view, the wide exposed hip axles and slender lower-leg members still make the stance feel lightly assembled compared with the reference’s integrated, dense load-bearing legs.

Those are visual observations from these stills, not owner acceptance. V35 remains an unaccepted candidate; these geometry checks do not establish likeness, runtime behavior, or overall clearance.
