# First Choice export normal check

The original frozen Blender scene and its 54,411,132-byte GLB remain preserved. `first-choice-strict.glb` is the full-resolution runtime export carrying the native corner normals.

| Asset | SHA-256 |
| --- | --- |
| Frozen native scene | `1e59785a11aadf491714ef1b5aa682ff1b9efa0a6a3b421414f3bb7de053a05b` |
| Published native, with packed file paths normalized | `019949c70a8aaff3314244b5fc222d9332dcaf23a24ff208576d52791395ae95` |
| Frozen GLB | `88ff5f671a7359c04177b77c3dc01630491189f58d24e6bc0d85d7ed98ccd12e` |
| Strict GLB, 55,884,688 bytes | `20632ff6116f93827bc814d53301749dec1ef035165749db2d819bb89edcd41c` |

## What changed

Both comparisons evaluated 1,790 native mesh objects in Blender 5.2.1 at rest. Source and export were matched by parent pivot, region, material and oriented triangle positions in a common world frame. All 721,254 triangles and 2,163,762 corners have a unique correspondence. The 32 coincident triangles on eight wing fittings are pairs of opposite-winding surfaces. Triangle winding resolves their identities without looking at their normals.

The original exceeded the project's unchanged L2 limit of 0.00002 at 1,673,233 corners. Its largest discrepancy was 0.0175387, or 1.00491 degrees, on the left cervical journal. Failures occur at split vertices and single-normal vertices. The visually similar retained04 audit measured a different asset. Its findings cannot be substituted for this candidate's results.

The repair encoded the evaluated native corner normals in their exported meshes' local coordinate frames. It added 33,492 vertex rows where the former GLB's indexing grouped distinct native normals. The strict derivative has zero failing corners and a maximum L2 difference of 0.00000004837. Its ordered triangle positions, UVs and colors match the original at every corner. All 28 image payloads, 16 materials, 17 nodes, scene hierarchy, animation definitions and five animation accessors match the original.

Blender reimport of the derivative agreed with the source joint probes within 0.000000358 model units over all 253 frames. The ground and stand transforms remained fixed and the animation ended exactly at rest.

Four camera, lighting and pose combinations rendered on Chrome 158 using Apple M4 Max Metal. The maximum mean absolute difference was 0.00189 on an 8-bit RGB scale. In each 593,920-pixel view, 10 to 41 pixels differed by more than eight levels in any channel. The measurement covers four matched camera, light and pose pairs. This covers those sampled views. Cross-renderer pixel parity and human likeness acceptance are separate questions.

## Reproduce the native-to-runtime check

From the repository root, use Blender 5.2.1 LTS. Supply an empty scratch directory for generated files. The normal checker accepts the two recorded native hashes and verifies the GLB identity before comparing triangles.

```sh
model=atelier/delivery/first-choice.blend
source=atelier/delivery/first-choice.glb
tools=atelier/three-eras/normal-correction
out=$(mktemp -d)
blender --disable-autoexec -b "$model" --python-exit-code 1 -P "$tools/repair_normals.py" -- "$source" "$out/strict.glb"
blender --disable-autoexec -b "$model" --python-exit-code 1 -P "$tools/check_normals.py" -- "$out/strict.glb" "$out/normal-check.json" 20632ff6116f93827bc814d53301749dec1ef035165749db2d819bb89edcd41c
blender --disable-autoexec -b --factory-startup --python-exit-code 1 -P "$tools/verify_preservation.py" -- "$source" "$out/strict.glb" "$out/preservation.json"
```

The rig tools take the same native scene and one output directory following Blender’s `--` separator. `rig-source/bind-rigid-parts.py` records the triangle runs for the lower limbs, jaw and posterior assembly. `rig-source/bind-maker-shoulder.py` identifies the later repair hardware omitted in the early Maker era.
