# Read-only export proof preparation

Run `zsh /tmp/cg-recursive-export-proof02/run-checker.sh REPOSITORY_ROOT RELATIVE_RETAINED_PACKET_DIRECTORY NEW_TEMP_OUTPUT_DIRECTORY builder,maker,mechanic`.

The output must stay under `/tmp/cg-recursive-export-proof02`; use a fresh subdirectory. The expected native and GLB names are `murderbird-recursive-ERA.blend` and `.glb`. Immutable09 native inputs supply object-origin names. No producer helpers are imported. Native files open with auto-execution disabled; no save, render or export occurs.

Execution completion is distinct from proof PASS. Read `checker-results.json` and each material's component statuses. Strict normals FAIL is intentionally retained. Sparse GLB accessors and shared/cyclic scene nodes are rejected. Active render UV is channel0; explicit shader UVMap references follow native layer order. A different policy needs a new scoped mapping decision, not automatic tolerance adjustment.

The comparator rotates whole oriented triangles cyclically, sorts material-indexed triangles by position and associated attributes, and compares the UV/normal values on those same corners. It does not compare separate unordered UV/position sets. Identical rounded geometry keys have reported ambiguity counts. UV seams remain per-corner. Float32 world transformations, inverse-transpose normalized normals, determinant-based winding, and GLTF Y-up/UV-V conventions are explicit.

Calibration: all three Loop01 retained02 packets have position-and-UV correspondence PASS; strict normal correspondence FAIL. The maximum normal difference is already present in original09 GLB on an unchanged receiving panel. Normal-rounding/custom-normal assignment pipeline facts are recorded, but the precise maximum-delta cause is not certified. No shader, color-management, lighting, rendered-pixel or owner acceptance claim follows.
