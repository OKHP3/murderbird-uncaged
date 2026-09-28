# V10 attempt 02 native/export surface parity

Status: **pass within the stated surface-position scope**. This compares the exact saved native and its existing diagnostic GLB; it does not select or approve the model. The candidate remains held for likeness review.

Inputs:

- Native `assets/models/uncaged-whole-body-v10/attempt-02/murderbird-whole-body-v10.blend`, SHA-256 `6b2b43209d0474771010f3711f7d7ad2c00521f4d331c22a17d998f61a86c69f`.
- GLB `assets/models/uncaged-whole-body-v10/attempt-02/murderbird-whole-body-v10.glb`, SHA-256 `4fbd15830f390d357ea1f4197d7a45241c1657746d4fb4f1cf97708f86c52e1c`.
- Export receipt: `assets/audit/whole-body-v10/attempt-02/export-receipt.json`.

The independent Blender snapshot evaluates the native at frame 1, converts evaluated triangle positions to browser coordinates `(X, Z, -Y)`, and groups by rigid owner, era, region, surface role, and material. The GLB comparator independently loads and transforms exported positions, checks those group identities, triangle totals, unique-position bijection at 10 micrometres, and all exported pivot parent/world matrices.

Results: all 106 groups passed, all 52 pivots passed, and both sides contained 273,348 triangles. Maximum matched-position distance was `6.365778852490731e-8` m; maximum pivot matrix delta was `7.450580596923828e-9`. Native snapshot SHA-256 is `a4d678475eea83343645c648473743293dce2fc677e45c68e3766ccdd9793624`. Frozen snapshot script SHA-256 is `eb07398e228735c958489784b73163a50fbfbe8a3bd7dc3fd5def140b1ee110f`; comparator SHA-256 is `1341937ab825fe59227e1b11ed5451214d033d6b2efa0727c8bf75cbf5072242`; shared GLB loader SHA-256 is `a9c08ca44a57695b0db369feca69b9fe3ea41e590f033781397cb2b1fae6ba62`.

The check does not compare topology/order, winding, normals, UVs, shading, runtime motion, collision clearance, or artistic likeness. No source/native/export edits or commits were made during this check.
