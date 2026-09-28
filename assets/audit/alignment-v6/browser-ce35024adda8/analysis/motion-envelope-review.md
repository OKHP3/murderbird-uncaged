# Motion envelope review

This review uses the normal-clock UI-driven browser capture and a separate fresh visitor-strike capture. Both declare the same v6 model SHA. A requested UI event counts as successful only when motion samples support it.

## Findings

- **Maker:** jaw, neck, wing, leg, and tail articulation channels all moved away from rest and were within about 0.002 of zero before the next control request. The tail node rotation was not exported directly; its movement is supported by the articulation telemetry and runtime mapping.
- **Mechanic:** load, release, settle, and dwell phases were sampled; root yaw ranged from 0 to π/2 rad during the routine, showing turns. After stop was requested, the active cycle completed and settled; subsequent samples remained mechanical-ready with zero root speed.
- **Advanced:** samples show jump load/airborne/landing/recovery, thrust load/drive/brace/recovery, and a floor-claw action with contact. Left shoulder and elbow angles stayed within the narrow ranges recorded in the JSON; these samples do not prove swept-volume clearance.
- **Inspection:** Maker, Mechanic, and Builder each opened, reached separation 1, and returned to closed at separation 0 within the recorded windows.
- **Visitor attempt in the 86-second clip:** although the event was labeled “Advanced strike,” samples show warning/approach followed by retreat, with zero kinematic bill/rail contact frames. This clip does not demonstrate a strike.
- **Separate visitor-strike clip:** the fresh run records upper-bill/rail-centre-plane kinematic contact at 4.6817 s, recovery at 4.8643 s, and retreat after contact. Two sampled frames report this kinematic contact; the reported point is about 0.021 m from the rail centerline. Neck pitch is about 0.569–0.573 rad, below its 0.65 rad cap; skull counter-pitch is about -0.651 to -0.654 rad. Neck-base and skull translation errors both report 0 m. The root is stationary at contact. This telemetry does not establish a physical bar intersection.

## Limits

The JSON preserves source hashes, sample spans, recorder-completion durations, phases, and measurements. These are discrete browser samples, not continuous proof of every frame or every input path. They do not establish exhaustive collision clearance, physical forces, structural durability, or visual likeness. The separate kinematic contact result covers the sampled center-rail scenario only and does not prove physical bar intersection.
