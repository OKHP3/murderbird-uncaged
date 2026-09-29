# Excluded V27 wing terminal coarse study

**HOLD — not in Form01. One coarse implementation only; no correction or runtime edits.** Root found the tapered aft-down terminal visually useful, but the upper sleeve cue remains and moving intersections increased.

Source: `scripts/regions/whole-character-v27-wing-terminal.py`, SHA256 `b734342bee7cf0a544afbe035a06cbef7c5056f7b4054c7c252eb036b224ad15`. Frozen native: `coarse01/murderbird-v27-wing-terminal.blend`, SHA256 `0a09a402d3100c24d70d3e5140f5b7507f261f92f2203817e1fb878f122ae06a`. Matched before/after front, side, three-quarter and wing close-ups cover folded and short-shove wing angles. Exact paired screens, selected witness triangles, receipt and file-hash manifest are in `coarse01/`.

Only 40 existing elbow-owned plate/return/backing meshes changed together. All 54 named rests, 644 other meshes, hardware, materials and era tags remain exact. All 40 evaluated changed solids are finite, closed and positive; 6301 receiving-seat vertices verified exact; native save/reopen exact. Maximum new sampled plate-root-to-liner gap increase is 0.130 mm; inherited gap reaches 40.7 mm, so fastening/engineering attachment is not validated. No large new attachment separation was observed.

Crossowner strict pairs: folded 0→0; Maker 0→2; guard 5→21; short shove 23→35 (14 introduced, 2 removed). The two new Maker pairs are **right profiled mantle backing v4 right-wing-shield** versus **V21 refined right mantle course 6 plates 3 and 4**. The restricted-left short shove introduces the analogous **left liner versus left mantle course 6 plates 3 and 4**.

Read-only component attribution identifies **inboard X taper** as sufficient to cause those four previously clear liner/mantle pairs. Z lift/drop alone, Y aft sweep alone, and YZ together remain clear for those pairs. Z lift combined with X taper strengthens some witness counts. The full XYZ diagnostic reproduces frozen candidate witness counts exactly: Maker 128/30; restricted-left shove 146/50. The active-right liner already crossed those mantle plates in the baseline shove, and remains inherited. Other introduced plate/return pairs are recorded without individual component attribution.

These are finite posed triangle witnesses, not penetration depths or continuous collision/physics proof. The motion regression excludes the study despite its useful rest silhouette; no further variant is part of this checkpoint.
