# Compact shoulder and breast checkpoint

Status: unaccepted visual proposal for root integration. Two focused attempts;
local modeling stopped after attempt02. Reviewed shared goal at
`251f2f0243181e97140179c2aff6eb057e165438`; bounded new production authorization
comes from the owner-directed architect cycle. Base worktree commit:
`d4798d079c467892d4a5703caef77a1ed120d10e`.

## Inputs and scope

Input: `assets/models/cinematic-cg-milestone02b/murderbird-cg-2b-builder.blend`,
SHA-256 `9ba7fc471a86e5f1f9b8db881900725f8abf56546c69fecb125a236ec5b4a64c`.
Controlling full-bird image: owner-reissued Sept22 JPEG, SHA-256
`645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114`.
Maker, Mechanic and Advanced pinned era references were visually inspected.
July head reference does not govern this shoulder/body assignment.

Only new `scripts/cg-supervised-shoulder-body.py` and this audit tree are owned.
API: `apply(scene, root_path=None, era='builder')`, returning a receipt. It
requires a fresh preserved source; a duplicate application raises an error.
It uses existing wing/body regional materials without changing their graphs.
New parts have `cg1cRegion`, `cg2bRegion`, `surfaceRole` and era tags for root
surface integration. Parent root handles export, integrated viewpoints and
browser checks.

Reproduce diagnostic from repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/cg-supervised-shoulder-body.py -- --resolution 1000 --attempt attempt02
```

## Visible result

Attempt02 retains a convex rounded shoulder with smaller cap courses, varied
medium oblique armor and short posterior terminals. Upper breast courses roll
inward to the existing `[0,-.105,1.30]` neck junction. The lowest descending
curtain was traced to posterior body casing. Copies of those parts were locally
compacted below the shield; their source meshes remain hidden and retained.
Both attempts include identical-camera `before-canon.png` and `after-canon.png`,
an additional whole-bird view and an editable diagnostic native.

Gain: shorter rear contour and fuller compact shoulder; local upper breast has
a more connected inward roll. Limit: armor remains sparse and visually softer
than the reference, particularly with the inherited surface normals and finish.
The source's fine angular overlaps and hardware density are not reproduced.

## Verification

- PASS: Blender execution and three renders per attempt.
- PASS: source native hash unchanged; original source meshes retained.
- PASS: 1797 tagged head/neck/leg/foot objects retain exact vertex coordinates,
  world transforms and visibility in each attempt receipt.
- PASS: Python parser and Git whitespace check.
- NOT RUN: full three-era integration, GLB/browser parity, eight-angle/exhibit
  review, application build and deployment. No runtime changes are made.
- NOT ESTABLISHED: owner likeness acceptance or engineering validation.

Next: root integrates the module with the independently corrected head/neck,
then evaluates the full bird and surface response in matched views.
