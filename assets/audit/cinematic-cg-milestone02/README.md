# Milestone 2 — creature silhouette checkpoint

Owner accepted 1C as good enough to proceed. This checkpoint is a **single
focused contour pass**, not final likeness acceptance or a production release.
[Fixed comparisons and browser review](review.html).

## Visible result

Rounded folded shoulder caps and smoother torso transitions retain the owner-
accepted pointed body, compact neck, embedded avian hips and enlarged folded
shields. Body/wing profiles use bounded curved interpolation that passes through
study05 section anchors. Plates and backing move together; maximum vertex shift
is 0.02448 study units. Head/bill cage faceting is softened with a light
subdivision pass. No overall rescale, stance or joint change.

Gain is modest and concentrated on the shoulder caps. Broad shallow shell-like
plating, overly regular seams and flat optics remain; these belong to the proposed
surface-polish Milestone 3. No animation or engineering balance is validated.
The paper remains posture rationale with limits recorded in the 1C research note.

## Inputs, scope and evidence

- Base: owner-reviewed `a927c4f6d48f67b44e365e20d90fd655d1ddc51a`, original three-era
  native sources and maps retained unchanged.
- Study05 shapes/anchors, pinned artwork and paper remain unchanged.
- Separate track: `codex/cinematic-vfx-milestone02`; root owns integration.
- Three existing workers: body contour module, head contour module, read-only
  silhouette reviewer. No further delegation.
- Modules: `scripts/cinematic-cg-2-body.py`, `scripts/cinematic-cg-2-head.py`.
- Source/render builder: `scripts/build-cinematic-cg-milestone02.py`.
- New editable sources/browser models: `assets/models/cinematic-cg-milestone02/`.
- Same-camera before/after, eight outline pairs, eight neutral views, hero and
  close-up images; three era exports keep the original 1C regional finishes.
  Cameras, lights and display transforms are identical across comparisons.
- Exact object/leg/foot/material preservation: [preservation.json](preservation.json).
- Technical checks and remaining limits: [validation.json](validation.json).

Local build and browser checks are distinct from owner artistic acceptance.
Production code, public assets, illustrated fallback and deployment are untouched.
New CG models and audit files are excluded from the exhibit build. Frozen
engineering archive remains `9cc1b3c2da8cb064f343ab5915b32d0ab53236b1`.
All MurderBird creative assets remain all rights reserved under NOTICE.md.

## Budget and stop boundary

Plan ceiling: 45 minutes / 12,000 aggregate tokens. Clock started
2026-10-03T14:33:05Z; deadline 15:18:05Z. Worker ceilings 1,500 tokens each;
root 7,500 including setup/integration/checks. Exact aggregate telemetry is
unavailable; no exact usage total is claimed. One visual attempt delivered.
Stop for owner review before Milestone 3; do not infer motion or release approval.
