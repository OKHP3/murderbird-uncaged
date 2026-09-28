# Regional transfer recipe: guard plates and talon profiles

This note binds two isolated native studies and the selected V5 sixth regional composition. The studies are not complete-model replacements. Study files are preserved under `assets/models/uncaged-alignment-v5-regional/iterations/`; candidate02 remains historical, and candidate04 is the current regional transfer proposal. Neither candidate has been integrated into the later head/neck composition.

## Bound source studies

The studies inherit a replacement/compatibility contract from c8 native `cc6bfafc9ab044bba1abcbec86761afb9ef67ee60e252ec7ee838948ea7dfd04` and c8 GLB `c8a7a7e14253075414d8e55390ebad2bf605ad09962fa62769417834000ccaa3`. Their direct inputs are guard-study05 and talon-study02, respectively; the table below identifies their resulting study outputs.

| Study | Native output | GLB output | Manifest |
| --- | --- | --- | --- |
| Guards | `iterations/guard-study-06/murderbird-limb-profile-study-06.blend` — `6541f629bf3dd5c94dc01cacd260cbffef73f6fde867256385c15e6a6476746d` | `iterations/guard-study-06/murderbird-limb-profile-study-06.glb` — `3147e19da27707e8484ff0787b256142b487e38129f6517b8e0322cc2cd7ba65` | [`guard-study-06/manifest.json`](../assets/models/uncaged-alignment-v5-regional/iterations/guard-study-06/manifest.json) — `a02cc7b4abe04ad591c433e09f51fc54f14a73560bd1f853edcd77265a858023` |
| Talons | `iterations/talon-study-03/murderbird-talon-profile-study-03.blend` — `41ffac20895a59041b0c51bb44f0f13c9ec1d44a0347a694039798ee415265fc` | `iterations/talon-study-03/murderbird-talon-profile-study-03.glb` — `8f3a8359b3f8c8c2c2852f57cc70871ce55dace6e1baed7810da4c30c9b0dfda` | [`talon-study-03/study-manifest.json`](../assets/models/uncaged-alignment-v5-regional/iterations/talon-study-03/study-manifest.json) — `47199ec35e890730416dbc5eba9a9c7fcf9bb4375beec81dc52c1c4c61b1ab6e` |

- guard-study-06 direct input: native `assets/models/uncaged-alignment-v5-regional/iterations/guard-study-05/murderbird-limb-profile-study.blend` — `c1ea75d32edcc2a356589549651553b52fc7b641a17de9a2b9c532ce7050dcc1`; GLB `assets/models/uncaged-alignment-v5-regional/iterations/guard-study-05/murderbird-limb-profile-study.glb` — `d7074699b566dac07d40b226865db766c48cb36be104b0845cec5c2ddf059268`.
- talon-study-03 direct input: native `assets/models/uncaged-alignment-v5-regional/iterations/talon-study-02/murderbird-talon-profile-study-02.blend` — `40322c404bef7a1d281658d80f315e36c87efdd981d8358cdc43fd32af49655c`; GLB `assets/models/uncaged-alignment-v5-regional/iterations/talon-study-02/murderbird-talon-profile-study-02.glb` — `c0c98700bfd7b043e20a85d7e65132fd363ce68dfc1b4cd87ac0c6650ebc5765`.

## Selected combined candidate

The current proposal is `assets/models/uncaged-alignment-v5-regional/candidate-04/murderbird-v5-sixth-guard-talon-study.blend` (SHA-256 `376718193b9859cf7e454a0e148dde420c74061e6cdfbec7dd84ae6a4d3c960b`) and `.glb` (SHA-256 `829d416a9eb65226543ce619ffc37ce8f135f3f8869ffb291b65da2a5c664c67`). The exact composition manifest is [`candidate-04/manifest.json`](../assets/models/uncaged-alignment-v5-regional/candidate-04/manifest.json), SHA-256 `321fd2e01420e9fc06132822badedb79d2c6b0d27e26da0b8919ed434e4dc9ed`. It applies the ten guard-study06 meshes to the exact 26 replacement surfaces and the six talon-study03 profile meshes to the original six talon sheaths. Candidate02 remains available as historical evidence under `candidate/` and is not the current transfer proposal.

Candidate04's composition manifest records its exact source identities and replacement set. Guard-study06 retains its complete c8 contract of 26 replaced source surfaces and ten new guard objects; relative to guard-study05 it changes only two instep meshes. Talon-study03 refines six existing talon sheaths relative to talon-study02. These isolated studies preserve their stated owner/pivot contracts; candidate04's independent direct-GLB parity is recorded below. None is evidence that a future head/neck integration passed.

## Guard replacement allowlist

Only delete these 26 source mesh objects. Do not match by broad prefixes or remove owners, joints, bearings, rails, or other descendants.

```text
left ankle sheath lap rib 0.27
left ankle sheath lap rib 0.53
left ankle sheath lap rib 0.78
left articulated ankle sheath 0
left articulated ankle sheath 1
left articulated ankle sheath 2
left articulated ankle sheath 3
left tapered limb sheath left-shin 0
left tapered limb sheath left-shin 1
left tapered limb sheath left-shin 2
left tapered limb sheath left-thigh 0
left tapered limb sheath left-thigh 1
left tapered limb sheath left-thigh 2
right ankle sheath lap rib 0.27
right ankle sheath lap rib 0.53
right ankle sheath lap rib 0.78
right articulated ankle sheath 0
right articulated ankle sheath 1
right articulated ankle sheath 2
right articulated ankle sheath 3
right tapered limb sheath right-shin 0
right tapered limb sheath right-shin 1
right tapered limb sheath right-shin 2
right tapered limb sheath right-thigh 0
right tapered limb sheath right-thigh 1
right tapered limb sheath right-thigh 2
```

Copy these ten guard objects from the guard native study, retaining each object's owner and editable modifier stack:

| Owner | New mesh objects |
| --- | --- |
| `left-thigh` | `left shaped thigh guard proximal`; `left shaped thigh guard distal-overlap` |
| `left-shin` | `left shaped shin guard proximal`; `left shaped shin guard distal-overlap` |
| `left-foot` | `left curved instep guard` |
| `right-thigh` | `right shaped thigh guard proximal`; `right shaped thigh guard distal-overlap` |
| `right-shin` | `right shaped shin guard proximal`; `right shaped shin guard distal-overlap` |
| `right-foot` | `right curved instep guard` |

Guard mesh metadata in the study identifies `surfaceRole=plate`, `region=leg` or `foot`, and `geometryStatus=editable regional profile proposal`. Preserve the target's era visibility (`maker,mechanic,builder`), inherited/passive construction classification, and proposal state when integrating; do not change any era controller or owner node.

## Talon mesh transfer

Replace mesh data only on these six existing objects from the talon study. Keep the target object, local/world transforms, distal parent, pivots, digit links, and knuckles.

```text
left digit 1 tapered claw sheath  -> left-digit-1-distal
left digit 2 tapered claw sheath  -> left-digit-2-distal
left digit 3 tapered claw sheath  -> left-digit-3-distal
right digit 1 tapered claw sheath -> right-digit-1-distal
right digit 2 tapered claw sheath -> right-digit-2-distal
right digit 3 tapered claw sheath -> right-digit-3-distal
```

The study preserves talon centerlines, source terminal rings 14–16, and lateral/ventral bounds; its six objects retain `region=foot`, `surfaceRole=edge`, and the matching distal owners. The profile change is a visual study, not a final-identity decision.

## Compatibility and verification gates

Before transfer, confirm the target native source contains every allowlisted source object and six talon meshes with the expected types, owners, era metadata, and compatible rigid-owner hierarchy. Confirm all relevant joint pivots/endpoints are compatible with the c8 study base. Abort on missing, extra, renamed, or reparented targets rather than guessing. Preserve the six distal and six proximal digit articulation nodes and all unrelated geometry.

For a future head/neck composition, use native `.blend` object/data transfer, then save a new integrated native fork. Copy the ten exact guard-study06 mesh objects (two each for thigh/shin, one each foot) while removing only the listed 26 base replacement surfaces. Replace mesh data on only the six existing distal talon sheath objects from talon-study03. Preserve their target owner, local/world transforms, parents, eras, metadata, and all pivots/joints; do not transfer study owners or scene state. The talon study reports 637 unchanged native mesh signatures and 51 unchanged pivots; guard-study06 is a two-mesh delta from guard-study05 under the same 26-surface/10-object c8 contract. These are source-study checks, not proof that a future head/neck integration has passed. Validate any integrated native against its own pre-transfer snapshot, then rerun export, viewer, runtime, and visual checks against its exact new identity.

Independent direct-GLB export parity passes for candidate04 SHA `829d416a9eb65226543ce619ffc37ce8f135f3f8869ffb291b65da2a5c664c67`. The [candidate04 parity receipt](../assets/audit/alignment-v5-regional/export-parity-candidate04/regional-export-parity-829d416a9eb6.json) compares all 90 owner/era/region/role/material groups: expected and candidate each contain 230,900 triangles, 116,693 unique world positions, and 692,700 vertex occurrences, with zero failed groups. All 51 pivot world matrices are unchanged (maximum component delta 0), and all runtime meshes are classified.

The corrected foot-edge partition uses source-native geometry for the exact retained hallux sheath and two axle caps per side (276 triangles total each, matching the candidate world-position cloud exactly). It documents that the three ankle lap ribs per side (268 triangles each) were among the 26 exact guard replacements, not retained parts missing from export. See the [partition receipt](../assets/audit/alignment-v5-regional/edge-partition-audit/retained-foot-edge-source.json). An earlier candidate02 batch comparison reported the count delta without this replacement mapping; its interpretation is superseded but its raw receipt remains preserved under `export-parity-v2/` and the historical note is retained in [rejection-note.superseded.json](../assets/audit/alignment-v5-regional/rejection-note.superseded.json).

These checks establish sampled point-cloud and triangle/material-group parity, not full topology identity, collision clearance, or physical behavior. Candidate04's fixed-camera native review is in [alignment-v5-regional-candidate04-independent-review.md](alignment-v5-regional-candidate04-independent-review.md): the leg guards improve, while the foot-to-claw transition remains revision-required. This candidate remains a regional study, not the active application reference.

Candidate04 has additional exact-GLB local evidence. The [motion-demonstration receipt](../assets/audit/alignment-v5-regional/candidate04/motion/motion-demonstration.json) is status `passed`, records 125.122 seconds, 413 telemetry samples and 39 events, and confirms the served model SHA matches candidate04. It is a scripted multi-control demonstration using a temporary V4 route override; it is neither a no-input run nor runtime integration or human acting acceptance. The six [rig-check receipts](../assets/audit/alignment-v5-regional/candidate04/rig-checks/) report 65 checks total (structural 4, motion 14, kinematic 4, mechanism 7, power-move 4, claw-contact 32), each top-level status `passed`. The [limb plate clearance matrix](../assets/audit/alignment-v5-regional/candidate04/limb-clearance/limb-guard-clearance-829d416a9eb6.json) covers seven actual reachable states; the [jaw/neck matrix](../assets/audit/alignment-v5-regional/candidate04/neck-clearance/jaw-neck-era-matrix.json) covers nine actual reachable states in Maker, Mechanic, and Advanced. Both report zero strict proper triangle-crossing candidates in those sampled poses. They are discrete surface tests and do not establish continuous collision freedom, contained/coplanar overlap absence, force, grip, or physical behavior. Candidate02's earlier visual/parity review is retained in [alignment-v5-regional-independent-review.md](alignment-v5-regional-independent-review.md) as historical evidence.
