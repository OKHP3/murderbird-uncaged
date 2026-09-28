# Independent review: talon profile study 01

**Status:** bounded diagnostic and visual review; likeness, contact, and runtime acceptance remain open.

## Identity and scope

The study manifest binds the source native file (`cc6bfafc…dfd04`), source GLB (`c8a7a7e1…ccaa3`), and inventory (`5fda3638…b7ee0`). The six talon sheaths in the manifest are the only edited native meshes. The executed generator snapshot is 41,732 bytes with SHA-256 `7d5b5eda32244dfc503bc8e55bed7c9ab1d1c621ee2a43258c518a63c850dfdb`; its on-disk hash matches. Output native and GLB hashes/byte counts also match their manifest entries. The matched render manifest points to the output GLB hash `c17272ed…70632f`; all four image byte counts and hashes verify.

The generator retains the distal owner, pivots, sampled centerline, source terminal rings, and existing lateral/ventral envelope in its checks. It reports 51 source and output pivot empties with exact hierarchy/transforms, maximum talon centerline sample error below `6.7e-8 m`, zero measured lateral or ventral overrun, and exact source geometry for terminal rings 14–16. The native fork also records matching geometry signatures for its 637 unmodified meshes. These checks support the stated bounded authoring operation; they do not establish source dimensional accuracy or talon contact performance.

## Why each talon has 572 rather than 540 GLB triangles

This difference is intentional and follows from the generator topology. Each source sheath has 17 rings of 16 vertices, 256 side quads, and two 16-vertex caps. The GLB triangulates each side quad into two triangles and each cap into 14, yielding `256×2 + 2×14 = 540` triangles. The study inserts a 16-vertex ring at `t=.85` by splitting the 16 quads between original rings 13 and 14. That adds 16 side quads, or 32 triangles, producing `272×2 + 28 = 572` triangles and 288 position vertices. The loaded output GLB exposes all six talons at 288 vertices and 1,716 indices each, consistent with 572 triangles. This is not evidence of an accidental triangle-count mismatch.

The report calls the inserted ring an exact-source-surface ring. The code places its vertices by linear interpolation across corresponding vertices of the original quad strip. This is exact to that interpolation; the manifest does not separately compare those points against the triangulated source GLB surface for non-planar quads.

## Export fidelity limitation

Native preservation evidence is stronger than export-parity evidence. For the six changed meshes, the manifest records output GLB primitive counts, POSITION counts, bounds, and payload hashes, but does not report a vertex-by-vertex comparison of exported coordinates against the evaluated saved-native mesh after the documented Blender-to-glTF basis conversion. The study GLB contains 643 mesh objects while the source GLB contains 90; among 84 same-named untouched meshes compared by the generator, only 30 match exact primitive counts, vertex counts, bounds, and payload hashes. This may reflect batching/serialization differences, but the manifest does not map the other 54 back to source geometry. Therefore “only six native meshes edited” is supported; “the exported candidate differs only at those six runtime meshes” is not demonstrated by this receipt.

Before treating this GLB as a runtime candidate, compare the six exported talon vertex sets against the saved native evaluated meshes and reconcile the unmatched GLB mesh packaging. This is a fidelity evidence gap, not a finding that the six talons themselves exported incorrectly.

## Bounded visual judgment

The matched views show the cross-section change is restrained and not a large silhouette revision. At limb scale, the distal claws remain simple smooth, pale hooked sheaths with limited visible mechanical articulation. Candidate 03 and the Maker illustration show longer-looking, more strongly hooked tips and denser mechanical definition around the toes. Those are qualitative perspective references, not dimensional drawings. The study may be worth preserving as a cross-section direction, but its visual gain is subtle in the full-body views and should be judged in a close, matched front/side comparison before adoption.

The profile invariants do not establish sharpness, grip, floor contact, collision clearance, strength, or likeness. No such approval is implied here.
