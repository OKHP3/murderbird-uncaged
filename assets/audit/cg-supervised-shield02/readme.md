# Compact shield plate correction

Bounded wing-only proposal from equilibrium QA's cycle01 cap-tier regression.
Shared main goal read at `251f2f0243181e97140179c2aff6eb057e165438`;
working authority read in `goal.md` at base `8efb5ba11eaa208d802ee876516648b1b08b79d1`.

## Deliverable and integration

`scripts/cg-supervised-shield02.py` exposes
`apply(scene, root_path=None, era='builder')`. Run after the existing
`cg-supervised-head-neck.py` and `cg-supervised-shoulder-body.py` modules.
It requires shoulder01 surfaces, preserves the compact recess, hides/retains
its former wing plates and adds 90 editable wing-only scalloped sheets.
Body, throat/upper breast, head/neck, stance and machinery are untouched.
New meshes have UVs and face/sidewall/underside material slots, using existing
regional material graphs. No material graph, lighting or microfastener edit.

Source native: `assets/models/cg-supervised01/attempt01/murderbird-supervised-builder.blend`.
Source SHA-256: `e5fc6a39662bcb7f5ab82679dd719757edc4f0f39fc3cc5ae433bae962409d43`.
Controlling full-bird reference: owner-reissued JPEG
`assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg`,
SHA-256 `645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114`.
July wing/body imagery is excluded. All creative content remains all rights reserved.

## Visual evidence

`before-whole.png` / `after-whole.png` and `before-shield.png` /
`after-shield.png` use identical frozen neutral lights and camera settings.
`shoulder-construction-comparison.png` displays a labeled source crop and
matched before/after crops; it is diagnostic composition, not camera registration
of the source. The complete reference stays preserved.

Two focused attempts: first reduced cap protrusions but lost visible seams;
second increased a small overlap step and is the supplied final proposal.
Visible gain is limited: the square raised cap tiers become curved tapered
scallops and the compact rounded shoulder flows more coherently. The same
exposed underwing hardware and flank remain. Source fine hardware, sharp edge
contrast and dense diagonal plate articulation are still substantially stronger.
The candidate shoulder still reads too smooth under neutral light; this is not
owner likeness acceptance or a completed source twin. No third attempt made.

## Validation

`preservation-checks.json`: PASS for all 6,114 original mesh geometry,
transforms, UVs and material assignments, original lights/world, finite new
geometry, UVs and three material slots. `receipt.json`: 5,732 non-wing meshes
unchanged, source binary preserved, original wing plates retained hidden.
New editable native: `murderbird-shield02.blend`.

Blender 5.2.1 LTS CPU Cycles, 16 samples, 1000px images. No browser export,
three-era renders, app/runtime build, animation, physical validation, remote
publication or artistic acceptance check ran. Root owns integration and
three-era/browser fidelity validation. This worker changed only its script and
this audit directory.
