# Optic awake final calibration — browser gate pending

The first moderate amber proposal remains frozen. Actual browser review found it too evenly orange. This final material-only candidate reduces emission to `[0.10, 0.025, 0.0025]`, restores source base `[0.095, 0.031, 0.007, 1]`, and sets roughness `0.22`; metallic remains `0.2`.

Only `V38 contrast / optic` and its builder finish profile change. The two Advanced aperture nodes retain exact geometry, hierarchy and eligibility. All other native object records and materials remain exact; runtime non-material records and binary chunks remain exact. The native Principled shader and its actual diagnostic export agree within 1e-6. No textures, bloom or earlier-era changes.

Regenerate from repository root with Blender background execution of `scripts/build-v38-optic-awake01.py -- --attempt02`. Both modes refuse existing output binaries; frozen executed recipes are evidence snapshots. Root owns actual browser and owner acceptance. No third calibration.

Native SHA256: `9b196ebe4ec6def5d81a755c187076ce8a985cea3b3794c2e2849297d38a1563`

GLB SHA256: `c8584f1bcb0147020e86c5f75c3146622dc51d10705ec95d3fe517fd24b875f0`

Scope and correspondence evidence: `scope.json`, `receipt.json`, `native-optic-export-check.glb`, `executed-builder.py`, `build.log` in this directory.
