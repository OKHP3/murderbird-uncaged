# Whole-character V15 construction studies

Attempt04 is the current **local review candidate**, not an accepted character or release. It combines head, breast and leg construction on the inherited V14 source. The production exhibit still uses V9. Source and runtime hashes, reference scope, failed studies, changed components and checks are in [the checkpoint](../../../docs/whole-character-v15-checkpoint.md).

Every numbered output is preserved. Attempts01/02 are head studies; attempt03 is the first combination with known jaw interference; attempt04 corrects jaw seating. `legs-study-02` is an isolated input study. Breast and held crown studies remain in the audit tree with their exact executed scripts. Do not overwrite any of them during regeneration.

To create a new candidate, use `scripts/build-whole-character-v15.py` with a new attempt identifier. It refuses existing output directories and pins its V14 input. Only `head,breast,legs` are supported composition modules; held crown-relief modules are intentionally excluded. Preserve manual edits as a new version before running any generator. The Blender source is editable, uses rigid regional owners, and exports through `scripts/export-native-diagnostic.py` with an explicit expected source hash.

Creative assets are all rights reserved under `NOTICE.md`. None of these new studies belongs under `public/` or in the release allowlist without a later publication decision.
