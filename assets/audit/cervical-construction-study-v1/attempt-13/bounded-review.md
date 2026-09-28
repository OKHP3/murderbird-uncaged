# Attempt13 bounded review

Status: HELD. One native and analysis set was saved; no second geometry trial, export or runtime edit.

Native SHA256: `76c6d99cd81ed13b5227553f03e94946db872b4150a60af71f8f1f43b2ca82e1`. It derives directly from pinned07. All52 pivot/owner transforms, all462 curves, materials and695 untouched source meshes remain exact. Fourteen existing meshes changed; no additions or ownership changes. Every changed control mesh is closed with two faces per edge, and the saved/reopened snapshot matches. The native has no posed review state.

Upper central3 and both upper2 plates remain unchanged. Lower4 is a compound-curved circular underlap with118mm center upper radius (112.38mm at X=.061) and a lower flare. Lower backing is a short closed recessed channel. Side3 keeps its original top/front coordinates and gains a continuous raised rear journal boundary. Annular seats and separated rail stations remove the old solid journal/rail crossings.

Strict intermediate crossings persist:3 pairs at rest,5 at Maker neck/combined,9 at contact/recovery. Upper central3↔lower central4 and the lower-backing/upper guard/rail crossings are gone. The new underlap instead intersects the existing upper inner channel and side3; contact adds side2. This is not an intermediate clearance pass. Head-journal and breast/root candidates remain separate inherited issues and are not claimed repaired.

## Recess versus flare evidence

The table uses saved-rest native XYZ. Radius is measured about the true intermediate X axle at Y=-.235,Z=1.452; this radial coordinate is invariant under relative X pitch. Rows refer to editable native loft grids, not evaluated triangle numbers. Lower4 has13rows perwall layer:0–4 upper recess,5–12 lower flare; upper inner/2 and closed side3 have11rows. Both whole-vertex radius ranges of confirmed penetrating evaluated triangles are given; these are not penetration depths. Full triangle/control IDs are in `underlap-zone-analysis.json` and the strict diagnosis. Return classification uses triangles mapping to both explicit wall layers; bevel attribution is approximate.

| Pose/interface | Upper rows / radius mm | Lower4 rows / radius mm | Confirmed lower-face zones (triangles) | Example evaluated triangle IDs: upper / lower |
|---|---|---|---|---|
| rest: Cervical articulated inner guards ↔ Throat formed lamina 4 | 7,8,9,10 / 84.4–133.0 | 0,1,2,3,4 / 92.9–113.9 | recess:116; return:24 | 172,184,185 / 0,1,4 |
| rest: Cervical flank lamina -1 3 ↔ Cervical flank lamina -1 4 | 7,8,9,10 / 53.6–101.3 | 0,1,2,3,4,5,6,7,8 / 53.8–99.2 | recess:118; transition:14; flare:38; return:19 | 364,368,369 / 12,13,14 |
| rest: Cervical flank lamina 1 3 ↔ Cervical flank lamina 1 4 | 7,8,9,10 / 53.6–93.9 | 0,1,2,3,4,5,6,7,8 / 53.7–95.2 | recess:120; transition:18; flare:34; return:17 | 336,337,340 / 8,9,16 |
| contact: Cervical articulated inner guards ↔ Throat formed lamina 4 | 5,6,7,8,9,10 / 96.6–156.0 | 0,1,2,3,4,5,6,7,8 / 99.8–150.5 | recess:124; transition:29; flare:85; return:12 | 106,122,123 / 6,7,12 |
| contact: Cervical flank lamina -1 2 ↔ Cervical flank lamina -1 4 | 6,7,8,9,10 / 78.1–94.3 | 0,1,2,3,4 / 76.6–94.0 | recess:20; return:10 | 188,220,221 / 30,74,75 |
| contact: Cervical flank lamina -1 2 ↔ Throat formed lamina 4 | 6,7 / 93.6–102.6 | 0,1 / 96.7–102.8 | recess:13 | 909,910,911 / 640,641,642 |
| contact: Cervical flank lamina -1 3 ↔ Cervical flank lamina -1 4 | 1,2,3,4,5,6,7,8,9,10 / 53.3–119.1 | 0,1,2,3,4,5,6,7,8,9,10,11,12 / 53.8–118.7 | recess:199; transition:20; flare:89; return:31 | 44,45,48 / 12,14,15 |
| contact: Cervical flank lamina -1 3 ↔ Throat formed lamina 4 | 0,1,2,3 / 92.3–119.1 | 1,2,3,4,5,6 / 93.7–122.7 | recess:21; transition:5; flare:5; return:4 | 58,59,62 / 64,128,129 |
| contact: Cervical flank lamina 1 2 ↔ Cervical flank lamina 1 4 | 7,8,9,10 / 72.7–97.8 | 0,1,2,3 / 74.8–94.0 | recess:17; return:9 | 192,193,194 / 2,3,35 |
| contact: Cervical flank lamina 1 2 ↔ Throat formed lamina 4 | 5,6,7 / 86.2–108.1 | 0,1 / 94.5–102.0 | recess:9; return:1 | 385,417,904 / 648,649,651 |
| contact: Cervical flank lamina 1 3 ↔ Cervical flank lamina 1 4 | 0,1,2,3,4,5,6,7,8,9,10 / 53.3–118.3 | 0,1,2,3,4,5,6,7,8,9,10,11,12 / 53.7–114.4 | recess:196; transition:22; flare:89; return:26 | 8,9,10 / 0,1,2 |
| contact: Cervical flank lamina 1 3 ↔ Throat formed lamina 4 | 0,1,2,3 / 88.9–121.9 | 2,3,4,5,6 / 96.0–122.7 | recess:24; transition:4; flare:7; return:6 | 2,7,67 / 124,125,185 |

At rest, the upper inner guard crosses only the recessed throat4 upper return (rows0–4,93–114mm) and its formed edge; no throat4 flare is implicated. Upper inner rows7–10 already occupy84–133mm radius. Consequently130mm is not a universal inside keepout: the unchanged inner channel passes through the recessed volume. Ending that upper inner channel higher, with an intentional complete closed return, is a necessary design option if the recessed throat4 is retained.

At contact, the inner channel conflict expands to upper rows5–10 and lower4 rows0–8, including85 lower flare triangles as well as124 recess triangles. The original inner control row5 is approximately native Z1.550–1.554; a proposed shortened upper channel should terminate above that affected neighborhood (around row4/native Z1.567+) and then be rechecked. This is a bounded reconstruction suggestion, not a certified new end height. Raising that channel alone cannot solve the other intersections.

Both side3 shields cross recessed lower4 and its lower flare already at rest. At contact they cross nearly all lower4 rows; the side2 conflicts are concentrated in lower4 rows0–4. Thus both side radial/axial nesting and the lower flare enter the sweep. The13 side underlap reaches the same X/radius neighborhood as the outer side guard: circle radius alone does not establish a nested lateral wall. Preserve07 outer side coverage while deliberately redesigning the inner underlap’s X stations and continuous boundaries, rather than projecting or deleting small face fragments.

## Review artifacts and scope

Matched neutral front/profile-left/3q images are `before07-*` and `after13-*`; the two contact images are `after13-advanced-contact-pose-*`. Only these eight requested views were rendered. Actual21 proof is `actual-runtime-joint-clearance-v1/guard-clearance-native.json`; `underlap-zone-analysis.json` adds exact rest/contact triangles, editable rows and per-zone radial ranges. `executed-generator.py` freezes the saved geometry recipe; `executed-zone-analysis.py` freezes this read-only attribution.

Changed paths in this resumed task: `scripts/study-v8-cervical-construction.py`, new `assets/models/uncaged-cervical-construction-study-v1/attempt-13/`, new `assets/audit/cervical-construction-study-v1/attempt-13/`. Earlier trials and their receipts were not edited. Stop for root visual/construction review; no attempt14 or geometry correction is running.
