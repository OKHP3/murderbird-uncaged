# V6 sixth-candidate integration source check

This read-only comparison is bound to GLB SHA-256 `ce35024adda89681a0f37e7018e2563a74af67cd06558a887222df87b78a87fe` and native BLEND SHA-256 `5a7a51941423dd0efcb48b9641b7a49597dad117e218ccb4e94f26315c5e9ded`. The 29 current authoring views all declare that GLB and native source. This checks source and inventory scope; it is not an independent visual acceptance review.

The sixth head source preserves the v5 crown geometry source exactly. The `_head_sections` block SHA-256 is `7dda0223fed55ebd61e798b01ba37764a79f3139b019d346102e106e47cac47b` in both head modules. The block from `_roof` through the temporal shell and course tuples, ending before the orbital plate, is byte-identical at `dbfb08de28786e24668cb119106ff651fe0a81f1d9d20d4e8ff705802038e0f4` in both. The jaw hinge world tuple is also unchanged at `(0, -.300, 1.704)`.

Geometry-authoring source hashes support the declared regional scope:

- The v5 body recipe included by v6 is byte-identical in v5 and v6: `alignment-v5-body.py`, SHA-256 `480ca02fbeead7b83d19509ebfc0231d79e1933a41b5d2d616ac3e4ac84cdee7`.
- V6 uses its revised head recipe, SHA-256 `a921130111ac27f14f1ddda10328f7dd21bf2cffa1d4e34aee8d1756fd738472`, for orbital surround, cheek, and mandible changes while retaining the crown source block above.
- V6 uses its revised neck recipe, SHA-256 `288d2bd52a317d72af131f936380bf8a8570147a212bd1ee584225aa6e048bf8`, adding the local forward and anterolateral jaw-clearance pocket. The source comments retain posterior/nape contours, support forks, bearings, and pivots.
- The composer changes to select those head and neck recipes. Preserved common builder helpers match the v5 inventory hashes. The v5 and v6 inventory records have identical 703 part entries, 51 pivots, bill-contact contract, and joint contract.

The current exact-model [asset-validation receipt](asset-validation-ce35024adda8.json) and [build-boundary receipt](build-boundary-ce35024adda8.json) passed their declared checks. The [six-validator rig manifest](rig-suite-ce35024adda8/run-manifest.json) records 59/59 declared rig assertions passed and source hashes captured before/verified after. Its associated [jaw-head sweep](rig-ce35024adda8/jaw-head-sweep/jaw-sweep.json) reported no crossings in 33 samples, [jaw/neck stress check](rig-ce35024adda8/jaw-neck-structure.json) reported no crossings in 27 poses, and the [fixed-rest optic check](optic-clearance-ce35024adda8/optic-clearance.json) reported no proper crossings in the selected mesh pairs. Browser inspection and motion review are still in progress. These bounded results do not establish continuous clearance, intentional seat fit, appearance approval, or deployment.
