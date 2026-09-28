# Opposite-side actuator anchor screen

This is a read-only geometric proposal screen. It reflects only the two proposed V4 actuator anchors to native +X (anatomical left), preserves their Y/Z coordinates, and leaves all pivots and the existing breast-panel motion unchanged. No actuator, housing, fittings, or support hardware was built.

The straight 12 mm envelope clears the sampled neck and upper cervical owners throughout both the 21 captured operating poses and the 101-point normal breast-opening sweep. In the operating packet, the closest conservative neck-side margin is +47.8 mm; in the opening sweep the closest conservative margins are +50.0 mm to the neck and +49.2 mm to the upper cervical assembly. The 21 operating poses have no direct sampled point within 12 mm of the breast assembly, though one conservative segment bound is uncertain at the quarter-open inspection pose (−2.8 mm).

The normal opening sweep remains a blocker for the proposed envelope: 12 of 101 sampled opening values put a sampled centerline point within 12 mm of the breast assembly, from open 0.26 through 0.37. The closest point is 0.058 mm from “Breast lateral feather 1 0 2” at open 0.30; the conservative 12 mm margin is −16.3 mm there and is negative at 13 samples from open 0.25 through 0.37. Thus this reflected anchor pair improves the sampled neck and mantle clearance but does not establish a usable inspection trajectory.

The check samples the straight centerline at 17 points and subtracts half the sample spacing for a conservative bound. It is not a continuous collision test, full solid-containment test, or proof of fit, mounting, or physical support. The proposed 12 mm envelope is only a clearance proxy. The Maker guide, wing restriction, native model, and runtime were not changed.

Evidence and exact input identities are recorded in [receipt.json](receipt.json); all detailed per-pose and per-opening measurements are in [opposite-side-clearance.json](opposite-side-clearance.json). The measurement script is [analyze-opposite-side-mount.py](analyze-opposite-side-mount.py).
