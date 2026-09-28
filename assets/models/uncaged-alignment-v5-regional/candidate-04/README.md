# Candidate 04: V5 sixth with regional limb studies

Candidate04 is an isolated V5 sixth regional composition: the frozen V5 sixth base, ten guard meshes from guard-study-06, and six talon meshes from talon-study-03. It replaces the original 26 limb sleeve/ankle surfaces and six distal talon sheaths. It is a regional proposal and evidence candidate, not a final likeness or mechanical certification.

The active application model reference is unchanged; this folder does not integrate candidate04 into the exhibit. This candidate is based on V5 sixth and is not a V6 whole-model replacement. The selective transfer boundary is described in [the regional transfer note](../../../../docs/alignment-regional-transfer.md).

## Exact identities

- Native composition: `murderbird-v5-sixth-guard-talon-study.blend`, SHA-256 `376718193b9859cf7e454a0e148dde420c74061e6cdfbec7dd84ae6a4d3c960b`.
- Batched GLB: `murderbird-v5-sixth-guard-talon-study.glb`, SHA-256 `829d416a9eb65226543ce619ffc37ce8f135f3f8869ffb291b65da2a5c664c67`.
- Composition manifest: `manifest.json`, SHA-256 `321fd2e01420e9fc06132822badedb79d2c6b0d27e26da0b8919ed434e4dc9ed`.
- Candidate composition used the preserved `compose-alignment-regional-study.py` snapshot in this directory (SHA-256 `4d5e513917abbc14b4a013b0a0d1f9082aebacd8273aa6256a0e3b9cc2cb947d`). The current composer entrypoint at `scripts/compose-alignment-regional-study.py` has SHA-256 `c6a0643d196d90b0e9bc0d5a58eb20e72546c3baaad6c7fc9ff674aa57e5b546`; it was separately exercised with legacy guard-study05/talon-study02 manifests for the diagnostic below, not to create this selected candidate.
- Base V5 sixth: `fd5c8a21e8e7808fa94c9baa3499574bac3d0c1ed5a44573637286c359cea0e4` native, `1e7febcc03d9f8d1a644580c8422b124403cf4e5768aa01df747e3d9b6af9f1e` GLB.
- Guard study 06: `6541f629bf3dd5c94dc01cacd260cbffef73f6fde867256385c15e6a6476746d` native, `3147e19da27707e8484ff0787b256142b487e38129f6517b8e0322cc2cd7ba65` GLB, `a02cc7b4abe04ad591c433e09f51fc54f14a73560bd1f853edcd77265a858023` manifest. Its input is guard-study05; two instep guard meshes changed, with all 51 pivots exact.
- Talon study 03: `41ffac20895a59041b0c51bb44f0f13c9ec1d44a0347a694039798ee415265fc` native, `8f3a8359b3f8c8c2c2852f57cc70871ce55dace6e1baed7810da4c30c9b0dfda` GLB, `47199ec35e890730416dbc5eba9a9c7fcf9bb4375beec81dc52c1c4c61b1ab6e` manifest. Its input is talon-study02; six named talon sheaths changed, preserving owners, pivots, and source tip rings.

## Checks

Composition records 32 replacements, 10 guards, six talons, 90 owner/era/region/role batches, and 230,900 triangles. Native/batch pivot deltas and maximum direct world-geometry/export errors are zero. Model-bound rig checks passed 65/65. The sampled limb guard clearance and jaw/neck matrix checks recorded no strict crossings; their limits are stated in their receipts. Fixed-camera native images and receipts are in `assets/audit/alignment-v5-regional/candidate04/native-builder/`; additional source-study renders are in `assets/audit/alignment-v5-regional/candidate04/source-studies/`.

Legacy v1 compatibility receipt: [legacy-v1-compatibility-receipt.json](../../../../assets/audit/alignment-v5-regional/candidate04/final-audit/legacy-v1-compatibility-receipt.json). It binds the current entrypoint and guard-study05/talon-study02 inputs to a separate diagnostic output; that output is not candidate04.
