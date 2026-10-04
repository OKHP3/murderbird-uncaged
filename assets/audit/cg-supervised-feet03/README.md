# Heavy feet03 exterior checkpoint

Status: **CG proposal; owner artistic acceptance pending.** Two focused design attempts. Final attempt replaces inflated cuff bulges with straighter sleeves and smooths claw centerline transitions. A readback boundary failure led to a mechanical clip of the instep crest to the original ankle bounds within attempt02.

Controlling full-bird source: `assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg`, SHA-256 `645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114`. No substituted image or modified source binary. Frozen receiving native: `assets/models/cg-supervised01/attempt01/murderbird-supervised-builder.blend`, SHA-256 `e5fc6a39662bcb7f5ab82679dd719757edc4f0f39fc3cc5ae433bae962409d43`. Base Git revision: `8efb5ba11eaa208d802ee876516648b1b08b79d1`; shared main goal read at `251f2f0243181e97140179c2aff6eb057e165438`, architect working goal with owner budget read separately.

## Visible change

The inherited toes read as small rails. The candidate has broader curved overlapping toe sleeves, recessed dark tendons and warm seam bands, a curved ankle/foot bridge, and substantial descending talons. This improves foot mass in the complete bird. Sleeve construction, hook contour, hidden rear detail and exact volume are image-derived proposals. Current finish remains too smooth and dark, and the source's finer irregular hardware/wear is unresolved. The parent finish worker must remap the preserved role graphs. This checkpoint does not establish a visual twin.

## Integration

`apply(scene, root_path=None, era='builder')` in `scripts/cg-supervised-feet03.py`. Apply once after other new modules to a fresh receiving scene. All added meshes carry `cgSupervisedFeet03`, `cg1cRegion=foot`, era and `surfaceRole` properties. Existing material graphs are reused. No above-ankle/body/head/wing edits. All original mesh geometry, UVs, material slots, face assignments, parents and world transforms remain unchanged. Nine source empties are preserved; stance in this native is represented by named hinge and plantar meshes as well. Original narrow foot geometry is retained hidden, except two ankle ferrules remaining visible. There are no retained visible old toe/talon/hook meshes.

## Evidence and checks

- `before-canon.png` / `after-canon.png`: exact frozen attempt01 camera transform, projection, scale and shift; identical neutral lighting and 768×512 resolution.
- `before-feet.png` / `after-feet.png`: identical diagnostic feet camera and lighting. No pose change or ground claimed.
- `receipt.json`: source hashes, camera settings, source payload digests, stance mesh/empty matrices, hidden mesh names, added meshes/UVs, native hash and proposed toe endpoints.
- `validation.json`: independent saved-native readback of original payloads, superseded visibility, finite editable UVs, strict ankle upper-bound limit and unchanged source SHA.
- `murderbird-feet03-study.blend`: editable final native in audit only. `attempt01/` retains the earlier design, exact module, renders, receipt and native.
- Python AST parsing and Blender render/application passed. No runtime references changed. Browser/GLB, three-era integration, npm build, CI and deployment were not run by this worker; integrator owns those checks. No publication or engineering acceptance is claimed.

First matched images were available approximately four minutes after assignment. Independent QA and owner review remain the next gates.
