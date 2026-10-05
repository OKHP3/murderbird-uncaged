# MB-T018 bounded replay

## Scope

Base checkout: `4984f39bdca13e87ead9b446b1d033dc0f2898ee`. The retained checker receipt is `assets/audit/cg-recursive-three-loop01/loop03/independent-proof01/export-replay/checker-results.json`; it declares normalized-normal vector L2 tolerance `2e-5`. The crown procedure is retained at `assets/audit/cg-recursive-three-loop01/loop03/independent-proof01/evidence-replay/crown-normal-association.py`. Its recorded result is `crown-normal-association.json`.

## Replay

Ran `bounded-replay.py` with the bundled Python runtime. The script makes no writes outside this packet except `normal-diagnosis.json`; it reads retained GLBs and JSON evidence. It verified each of the three current GLB SHA-256 values against the checker receipt, required identity mesh-node transforms for current and prior exports, and replayed the existing crown association: material-indexed, oriented triangle keys from position plus UV0 rounded to six decimals, followed by component-exact stored-normal comparison.

The checker receipt contains 75 failing material records. The global maximum is `0.008557185882560697` L2 (`0.49029213149792866` degrees), on `CGRF02 left forward toe 2 recessed joint shoulder 1` in the builder receipt. Its worst native and GLB triangle records have matching positions (0 max absolute error), no position-key mismatches, and UV maximum error `1.1920928955078125e-7` with no bad UV triangles; the three corner normals differ. This is a replay of retained native/export correspondence evidence, not a new Blender evaluation.

The crown is a separate failure in each era: 3823 of 3824 triangles exceed the unchanged threshold; the maximum is `0.0005350984722657378` L2 (`0.03065888445049866` degrees). Position and UV associations pass. The prior/final crown procedure associated all 3824 current crown triangles in all eras, found no unmatched triangles and no changed stored-normal components, and verified identity transforms. The finding isolates unchanged encoded crown normals across the two exports; it does not establish why the retained native-to-export crown comparison fails.

## Limits and next step

Current GLB hashes and mesh transforms were freshly checked. Native `.blend` evaluation, exporter execution, renderer behavior, and source-side transform history were not rerun. The cause remains `UNKNOWN`; no threshold change, geometry repair, acceptance, shader/pixel equivalence, or PRD scoring is claimed. Resolve cause only with a separately scoped native/export trace that preserves `2e-5` and associates the failing toe and crown records through the producer/export boundary.
