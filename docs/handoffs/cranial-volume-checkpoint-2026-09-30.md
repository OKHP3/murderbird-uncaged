# Cranial volume checkpoint — 2026-09-30

Both studies are VISUAL / ASSEMBLY HOLD. Study02 improves the rear downturn and coverage over01, but the helmet/broad-cheek appearance and under-back gap remain. Neither replaces cumulative jaw-fit02 or production V37. Two saved shapes; no further shaping.

## Source and authority

Read-only checkpoint: `9905c02113dfeea36f776416bbd1c743327a6812`. Actual input is `assets/models/whole-character-v38/jaw-fit02/murderbird-v38-jaw-fit02.blend` (SHA256 92470b6c7eb52004d9d3874645dc82bb5ecc2543482bdcede7f738898aea4ca9) and its rigid GLB (1f0091611676d1a8a75e609e5e0154f05acdd93c92a00ece24929fc87e0cc600). Actual July HEAD ONLY controls the head; master03 and Maker-clean are whole-bird cross-checks. Exact reference paths/hashes are in both receipts. Crown compaction is a reconstructed silhouette proposal, not dimensions measured from art.

## Construction and ownership

Each receipt enumerates99 replaced existing meshes:58 crown leaves,2 temporal walls,6 brows,6 cheek shields,14 temporal leaves,6 fitting roots,6 passive fittings and1 fixed frontal receiving seat. No topology from the malformed source crown was warped into the replacement. A regular shared field directly constructs finite panels and a recessed4mm inner cover;02 progressively turns the rear down and tapers short free tips.

Two additions: `V38 compact cranial inner shell` belongs to `cranial-cover`; `V38 fixed occipital closure plate` belongs to `head`. These are passive rigid Maker/Mechanic/Builder parts using inherited material/profile definitions. Crown58+inner support move together; fixed receiving41+occipital remain on head. All original owners, local/world matrices, pivots, inspection groups and contact marker are exact. Cranial-cover withdraws upward nativeZ/runtimeY by0.08m open plus0.14m separation; it is not hinged. Actual moving/fixed closure clearance is NOT verified.

True optic cups/floors/lips/Builder-only apertures, upper bill/contact, jaw bowl/socket/journals/clevis/axle, neck/body/limbs and left restriction are excluded and exact. Both native save/reopen comparisons preserve1120 original excluded objects; common exclusions digest `65258ca8d054e03af6dd522b83058eaed1dd719319b9cd314c6767d2e3b56bd0`.

## Evidence and limits

Six matched1200px neutral candidate views per version use the source jaw-fit02 camera settings. Source views are reused by receipt links; no duplicate baselines.01's high rear cutoff became02's curved nape boundary, but rear coverage and cheek likeness are unfinished.

All101 new/rebuilt candidate meshes have one component, closed edges and positive signed volume.02's unchanged strict nonadjacent triangle self predicate finds48 witnesses across5 crown plates, versus1045 in99 source meshes. Specifically C2/col0/leaf2:10; C2/col1/leaf1:14; C2/col5/leaf1:12; C2/col6/leaf2:10; C3/col4/leaf2:2. New crown topology is therefore SELF-FIT HOLD. Exact first triangles are saved.01 self diagnostic, full-pool interobject poses and withdrawal sweep were NOT RUN after visual hold.

Actual fitting base checks cover96 triangles/672 vertex-edge-centroid samples per8mm annular base on12mm pads: maximum gap0.000034mm. Pad inner faces have56 samples each, residual up to0.018534mm and0/8 exact matching receiver triangle keys. These are bounded finite-face distance observations, not full continuous conformity, support/load or manufacturing acceptance. Intended crown support/closed interfaces in executed recipe descriptions remain unproven and are corrected in validation-disposition.json.

The rebuilt crown pairs retain nominal3mm vectors; inner and occipital shells4mm. Component/stock signs do not waive self witnesses. The actual02 GLTFLoader→era-finishes check applies all3 profiles with0invalid materials; all12 exported PBR/profile definitions equal input. Root owns browser/runtime/build evidence separately.

## Frozen outputs

| Study | Native SHA256 | Rigid GLB SHA256 |
|---|---|---|
|01|9de4ddf945973c55cc5ce97b01b667b151bb7dec7373361dd303121e738b838f|07640315a8e4bcfb18c5354be4f8d1469880239ee168b688bfc9e3c0db30408e|
|02|1a48cbfbc44594d4140f27f9637d3b80a9d877283fd3be8c3dfc8fc0e1ec8087|968b45d7266719e11af7b34ed024a729e7ad73f68777ed18cb20648d43923433|

Actual finite-vertex crown bounds source→01→02 are in `cranial-volume02/geometry-check.json`; source top1.943684m/rearY−0.127520m,01top1.905767m/rearY−0.237928m,02top1.902247m/rearY−0.237928m.02rear lower boundZ1.672789m. These include plate stock/lifts, not only nominal field values.

Current top-level recipe reproduces02 and refuses existing model/receipt outputs.01's exact executed-builder.py/region.py are retained in01 audit;02 copies likewise. Reproduce an earlier version in a clean checkout by placing those copies at `scripts/build-v38-cranial-volume.py` and `scripts/regions/v38-cranial-volume.py`, with the exact jaw-fit02 pair available, then run `blender --background --python scripts/build-v38-cranial-volume.py`. Builders derive paths from repository root; canonical reference paths in the recipe are machine-specific and must resolve to the hash-recorded binaries. Do not execute an audit copy in place. No old assets/recipes were overwritten.

Next method should refine a complete compact cover/fixed skull boundary together while preventing finite normal-offset folds; broad parameterized cheek backing still dominates the exterior. No automatic continuation/adoption, joint approval or owner acceptance is implied. Root handles integration; no worker runtime/build/push or broader checks ran.
