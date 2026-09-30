# V38 body checkpoint — September 29, 2026

Local Mac geometry checkout, `codex/v38-body-mass-01`, base commit `6c505322827cc036df4a33d36ba19266d53adb29`. Root is the integrator. **Body-study02 is ready for integration review, not approved likeness, runtime integration or publication.** Two focused attempts are complete; no further geometry attempt is authorized here.

The neutral [three-quarter](../../assets/audit/whole-character-v38/body-study02/candidate-three-quarter.png), [front](../../assets/audit/whole-character-v38/body-study02/candidate-front.png), [side](../../assets/audit/whole-character-v38/body-study02/candidate-side.png) and [rear](../../assets/audit/whole-character-v38/body-study02/candidate-rear.png) views retain the fuller lower torso from study01. Separate thigh-owned, tapered open channel segments replace its cup-like guards. Matched V37 baselines and authored hip-step/crouch glances are alongside these 1200 × 1200 neutral Workbench renders. Artistic improvement remains a review judgment.

## Source boundary and frozen outputs

Construction starts from the actual canonical V37 `assets/models/whole-character-v37/attempt-release02/murderbird-whole-character-v37.blend`, not either earlier V38 study. Native SHA-256: `230f67cfaa69ff5bbd42f6167e290c6511dfe05b49571e94179cb5301e86a32a`; source GLB SHA-256: `4b7c3d248d69a038795b0a5c7b7742b8a5b77d0a9050b7e5afa32b544b0d4e25`.

Directly viewed whole-bird references in the canonical repository:

- Owner-resupplied target: `context/threads/assets/murderbird-owner-likeness-rejection-2026-09-28/2-Pasted-Image-2.jpg`, SHA-256 `2024330ac948bceb6a8e19d1467bc25882f57aca6d0abba2b072847f2439a8ce`.
- Candidate03: `assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png`, SHA-256 `538c51bcdbf5bfce95a0932fdbbb0f5868b446f4985346d15e6cacd32430e633`.

These guide apparent contour and construction, not recovered dimensions. Head-only references do not govern this body change. No material contrast fork is combined; `hip-study01` is preserved and was not loaded.

| Frozen body-study02 output | SHA-256 |
| --- | --- |
| [Editable native](../../assets/models/whole-character-v38/body-study02/murderbird-v38-body-study02.blend) | `27667b0766ee95c9fc83c0988750b52bc6c7cdc50c70ebb8b31983a7511b50a8` |
| [Separate rigid GLB](../../assets/models/whole-character-v38/body-study02/murderbird-v38-body-study02-rigid.glb) | `23d7c191a8ca9791a93ec22327a666b8f31c84688e945c3b06a1dde0e3ed08e9` |

## Exact scope and attachments

The [receipt](../../assets/audit/whole-character-v38/body-study02/receipt.json) records complete before/after signatures and the expanded names. The 32 changed mesh allowlist is:

- `V23 lower sternal return`.
- `V30 continuous tapered breast liner` and `V30 continuous dorsal pelvic liner`.
- `V34 formed breast course 4 plate 1–6`, `course 5 plate 1–5`, and `course 6 plate 1–4`.
- `V35 oblique thoracic side guard {−1,1} {2,3,4}`.
- `V25 {left,right} thigh {primary load member,rear return member} {−1,1}`.

No original objects are removed. All five V28 pelvis supports are exact again. The 1,067 other original object snapshots remain exact, including pivots, contact/anchor nodes, head, neck, shoulders, feet, left-side limits and era gates. Changed mesh owners, rest transforms, visibility, properties and material slots remain exact; existing material defaults are preserved.

| New rigid parts | Owner | Role and era eligibility |
| --- | --- | --- |
| Seven `V38 tapered pelvic return course 1–7` | `body` | Passive plate; Maker, Mechanic, Advanced |
| `V38 {left,right} fixed pelvic formed load web` | `body` | Passive frame; Maker, Mechanic, Advanced |
| Six `V38 left thigh {inner,outer} formed load channel 1–3` | `left-thigh` | Passive plate stock; Maker, Mechanic, Advanced |
| Six corresponding right thigh channels | `right-thigh` | Passive plate stock; Maker, Mechanic, Advanced |

All 21 additions carry `exteriorEras=maker,mechanic,builder`; `builder` is Advanced's runtime key. Fixed pelvis stock and rotating thigh stock remain distinct owners. No new powered/sensing eligibility is introduced. The rigid GLB preserves unique exported node identities and parents; it is a review derivative.

## Evidence and limits

**PASS, narrow interface only:** [actual-triangle hip screen](../../assets/audit/whole-character-v38/body-study02/body-thigh-pitch-screen.json) reports zero baseline, candidate or introduced overlap pair-samples at local-X thigh angles `−0.45, −0.30, −0.15, 0, 0.15, 0.30, 0.45` radians. It checks changed/new body stock plus the five unchanged V28 supports against actual direct thigh-owner solids. The enlarged V30 dorsal liner receives relief from sampled actual thigh geometry. This is not containment, tolerance/contact classification, all-axis or continuous collision certification; breast opening, knee/foot clearance and physical loads are outside this screen.

The two pose glances use authored rotations on retained joints: hip step `±0.30` radians, and crouch thigh `−0.45`/shin `+0.65` radians. They are not captured runtime movement, planted-foot validation or physical simulation. Native save/reopen snapshots, rigid node owners and all model/media hashes passed their checks. No full suite was run.

[Body-study01](../../assets/audit/whole-character-v38/body-study01/receipt.json), its native/GLB, views, executed source copies and **FAIL** diagnostic are preserved. Its hip screen found 185 introduced pair-samples in broadened existing V28 supports and the V30 liner. It must not be adopted as clearance-ready. Study02 restores those supports and adds liner relief.

The thigh channel edges remain angular, and whole-character likeness still requires artistic review. Materials remain inherited neutral construction responses. Study02 has no authored illustrated fallback and no runtime hookup; the current production/fallback remains V37. Realtime movement, combined poses, inspection opening and device behavior remain unchecked for this fork. Local rendering and this screen establish neither CI/deployment nor owner acceptance.

## Recipe and next action

The latest repository recipes are `scripts/build-v38-body-mass.py` and `scripts/regions/v38-body-mass.py`; **they now target body-study02 and are write-once**. Exact executed copies and input/script hashes are saved in its audit directory. Study01 has its own frozen executed copies; its historical script hashes do not refer to the now-updated live recipes.

Invocation used, from the geometry repository root, with Blender 5.2.1 LTS:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python scripts/build-v38-body-mass.py
```

There are no custom invocation arguments for source/output relocation. The builder hardcodes canonical source root `/Volumes/OKH-Local/04_GitHub_Mirrors/murderbird-uncaged`; the Blender executable above is Mac-specific. The saved hip checker resolves this repository from its own location, then reads the receipt's absolute canonical source path. On another host, relocate those recipe/source-path settings in a separately scoped fork while preserving the pinned input hashes. Executed builder/region copies are provenance snapshots, not drop-in entry points: their `__file__` root resolution assumes the original `scripts/` locations. Re-running the latest builder against these existing study directories intentionally refuses to overwrite them. Rebuilding equivalent geometry does not promise byte-identical Blender files.

Root should review study02's whole-bird views and receipt, then decide whether to integrate this geometry independently of the material fork. Any runtime selection or release needs its own required build, WebGL/fallback and motion checks. No worker commit, push, remote synchronization, release or owner acceptance is claimed.
