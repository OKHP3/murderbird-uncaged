# Alignment v6 toe-cover study v1

Unaccepted neutral geometry proposal built from the frozen Alignment v6 Blender scene. The source scene and runtime GLB remain unchanged. The editable proposal adds twelve shallow plates, one per proximal and distal digit segment, parented to the existing left/right digit pivots. Each plate is tagged as a proposed passive foot plate for Maker, Mechanic, and Builder eras; that role and its transfer across eras remain unaccepted.

The only new scene objects are listed in the exact addition allowlist in [the receipt](../../audit/toe-cover-study-v1/study-receipt-refined.json). The receipt pins the source model and reference image hashes, proposal parent/era/role metadata, same-camera neutral before/after images, script and native-scene hashes, and saved-file retention checks. It confirms all 1,216 retained objects preserve their parent, local and world transforms and custom properties; all retained mesh positions, topology, face material indices, smoothing flags and material slots match after reloading the saved proposal.

## Review result

The candidate-03 master and Maker-clean references support articulated armored toes with explicit breaks at the joints. The neutral plate experiment clarifies the segmented dorsal surfaces, but the plates read as small applied patches and the rounded digit roots remain the dominant form. The lower view also shows no evidence that this surface treatment resolves the foot-to-claw transition. Hold or reject this treatment for visual integration; it does not address the underlying digit envelope.

The native scene remains useful as a bounded experiment. The neutral renders do not prove fit through articulation, collision clearance, ground contact, or acceptance in any era. Those checks remain open. No GLB or runtime export was created.

## Files

- `murderbird-toe-cover-study-v1-refined.blend` — editable isolated proposal.
- [`feet-three-quarter-before-refined.png`](../../audit/toe-cover-study-v1/feet-three-quarter-before-refined.png) and [`feet-three-quarter-after-refined.png`](../../audit/toe-cover-study-v1/feet-three-quarter-after-refined.png) — matched upper three-quarter comparison.
- [`feet-low-three-quarter-before-refined.png`](../../audit/toe-cover-study-v1/feet-low-three-quarter-before-refined.png) and [`feet-low-three-quarter-after-refined.png`](../../audit/toe-cover-study-v1/feet-low-three-quarter-after-refined.png) — matched low three-quarter comparison to expose attachment and lower-surface gaps.
- Earlier neutral draft outputs are preserved under `assets/audit/toe-cover-study-v1/iterations/draft-02/`.
