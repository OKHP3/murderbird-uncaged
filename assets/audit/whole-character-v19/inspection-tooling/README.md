# V19 breast-opening checker

`../../../..`-relative Blender invocation:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python scripts/check-v19-breast-opening.py -- \
  --native assets/models/whole-character-v19/attempt-NN/model.blend \
  --sha256 EXPECTED_NATIVE_SHA256 \
  --out assets/audit/whole-character-v19/inspection-tooling/attempt-NN
```

The checker applies the production inspection transform to the candidate's own
rest hierarchy at open fractions 0, .25, .5, .75, and 1, with separation fixed
at zero. It reads the candidate breastplate's declared `inspectionAxis` and
`inspectionOpenRadians` and mirrors the runtime validity range (`.2` through
`π/2` in magnitude); missing or invalid declarations fall back to the legacy
local Y rotation of `-1.35 * open`. Under the established Three/native basis
conversion, browser local X/Y/Z map to native X/Z/-Y. The cranial cover's local
Three.js Y translation `+0.08 * open` maps to native local Z. It records the
actual candidate local and world matrices instead of reusing a packet captured
before a hinge move.

The screen checks the breastplate-owned mesh assembly against direct body,
neck, head/jaw/bill, mantle, wing-shield, thigh, shin, and foot owner meshes. It records the moving
cover assembly's minimum world Z at each sample as a floor-clearance indicator.
It uses the repository's frozen strict noncoplanar triangle crossing kernel. A pass
means only that no strict crossings were found for those surfaces at the five
discrete samples; tangencies, full containment, unsampled motion, support,
strength, and visual acceptance remain outside scope. Outputs are write-once.
