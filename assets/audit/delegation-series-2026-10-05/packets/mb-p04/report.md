# MB-P04 — strict normal diagnosis

**Outcome: reproduced from retained evidence; cause remains UNKNOWN.** At the unchanged normalized-normal L2 threshold of `2e-5`, the retained checker receipt fails. The maximum is `0.008557185882560697` L2 / `0.49029213149792866°` and maps to `CGRF02 left forward toe 2 recessed joint shoulder 1`. The exact saved triangle correspondence has position error 0 and UV maximum error `1.1920928955078125e-7`; the corresponding corner normals differ. There are 75 failing material records in the retained receipt.

The crown has a distinct failure in each era: 3823/3824 triangles exceed the threshold, with maximum `0.0005350984722657378` L2 / `0.03065888445049866°`. Position and UV association pass. The existing prior/final GLB association matched all 3824 crown triangles per era and found identical stored normal components. Thus the stored crown export normals were preserved across versions, while native-to-export strict parity still fails. Neither result identifies the producer-side cause.

The bounded replay freshly verified all three current GLB hashes against the checker receipt and confirmed identity transforms in retained prior/current exports. It reused the retained toe native/export triangle record and ran a local read-only equivalent of the existing crown association procedure. It did not evaluate native Blender files or rerun the exporter. Transform history on the native side, exporter behavior, and any runtime/render consequence remain unknown.

**Product gates:** strict normal parity remains `FAIL`; source likeness remains `UNMET`; owner artistic acceptance remains `PENDING`; PRD remains `NOT SCORED`. This packet does not repair geometry, alter the threshold, or approve a visual/animation/mechanics phase. Next evidence: a separately authorized native-to-export trace of the toe and crown at the same `2e-5` threshold.

Changed paths are limited to this packet: `bounded-replay.py`, `normal-diagnosis.json`, `reproduction.md`, `report.md`, `result.json`, and `done.json`. See `result.json` for checks and evidence tiers.
