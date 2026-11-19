# MurderBird: Uncaged — Three Eras, Three Distinct Movement Systems

This is an owner-directed clarification of the earlier PRDs. Apply it to the ongoing implementation.

The three eras must represent fundamentally different machines. Changing color, surface finish, or visible accessories is insufficient.

This direction supersedes earlier assumptions that all three generations should pace, react, or contain comparable internal mechanisms.

## 1. The defining progression

The evolution is:

1. **The Maker:** an externally operated articulated construct.
2. **The Mechanic:** a limited, internally powered mechanical automaton.
3. **The advanced MurderBird:** a powerful, intelligent, fast, fluid mechanical predator.

Preserve one recognizable character across that progression. Its capabilities, articulation, control, and internal construction change substantially.

| Characteristic | Era One — Maker | Era Two — Mechanic | Era Three — Advanced |
|---|---|---|---|
| Movement source | External ropes, lines, rods, or linkages | Internal mechanical drive | Advanced power system and actuators |
| Independent walking | None | Slow, limited, constrained | Fast, coordinated, capable |
| Movement character | Individually operated articulation | Rigid, stepped, jerky | Fluid, precise, forceful |
| Independent intent | None | Limited mechanical routines | Apparent awareness and tactical behavior |
| Cage behavior | Stationary demonstration | Restricted mechanical traversal | Agitated pacing, tracking, testing, and attacks |
| Inspection focus | External control and articulation | Mechanical power transmission | Power, actuation, sensing, and processing |

Do not implement these as three playback speeds applied to one animation.

## 2. Era One: the Maker’s articulated construct

Era One is essentially an advanced-for-its-time marionette or mechanically operated puppet.

It cannot independently walk, pace, pursue, attack, or reposition itself.

Its location within the cage remains fixed. Its support must make that physically credible, especially when one leg is lifted.

Individual parts may articulate:

- Lift and lower a leg.
- Raise and lower a wing.
- Move the tail.
- Turn or incline the neck.
- Open and close the mouth.

These are externally driven demonstrations. They do not imply autonomous life.

### External control

Do not assume that the only valid puppet arrangement is strings suspended from above.

Investigate an appropriate configuration using:

- Tensioned ropes or control lines.
- Rods operating from below or behind.
- A support post or cradle.
- Mechanical linkages connecting external controls to particular joints.

Choose an arrangement that suits MurderBird’s weight, anatomy, and historical appearance. Present its exact construction as a proposed reconstruction where the references do not establish it.

Make the causal relationship visible: operating a control should move the corresponding component.

Avoid decorative strings that terminate nowhere, rods that pass through solid parts, or a lifted leg that leaves an unsupported body floating.

### Default behavior

At rest, Era One is stationary.

Do not add:

- Predatory tracking.
- Autonomous head scanning.
- Breathing-like idle animation.
- Self-directed cage testing.
- Walking or lunging.
- An internal power source or brain.

The visitor may operate clearly labeled articulation controls. An optional demonstration sequence may operate those controls in order, provided the interface makes its external operation clear.

The stationary nature of this era is intentional. Do not “improve” it by giving it capabilities it has not yet acquired.

### Inspection

Era One has no internal powered machinery.

A shell, supporting frame, pivots, attachment points, or through-linkages may exist where necessary to explain construction. Those are not an internal engine.

Its inspection experience should reveal **how it is manipulated**, including control paths and joint relationships.

Do not populate it with later-era gears, springs, processors, power units, or actuators merely to fill an exploded view.

## 3. Era Two: the Mechanic’s limited automaton

Era Two introduces internal mechanical power and limited locomotion.

It can move around inside the cage, but slowly and awkwardly. Its movement should feel constrained by its transmission, available power, and mechanical construction.

The owner’s comparison is the heavy, primitive first Iron Man suit. This is a capability analogy, not permission to copy its appearance, components, names, or sounds.

### Movement character

Demonstrate:

- Slow starts.
- Deliberate weight transfer.
- Short, constrained steps.
- Pauses between mechanical operations.
- Segmented turns.
- Limited joint travel.
- Uneven movement tied to the drive mechanism.
- Noticeable settling after an action.

The legs, wings, and body should not move with Era Three’s coordination or fluidity.

However, “jerky” must not mean low frame rate, random vibration, broken interpolation, or uncontrolled foot sliding.

Make the irregularity mechanically motivated: engagement, loading, release, restricted gearing, or another coherent cause.

### Mechanical power

The owner identifies gears, springs, and steam-era mechanisms as relevant possibilities.

Determine which power arrangement best fits the established material and this direction. Do not casually combine every mechanism into an unexplained machine.

Document the selected design as confirmed or proposed, as appropriate.

Its power transmission should explain its limitations. Winding, pressure, or stored-energy depletion may be useful interpretive features if supported by the selected design; they need not become burdensome gameplay.

### Behavior

Era Two can perform limited sequences, such as slow traversal, stopping, turning, and restarting.

It must not display Era Three’s apparent intelligence or rapid predatory response.

Any visitor-triggered action should read as a limited mechanical response, not sophisticated threat assessment.

### Inspection

Reveal the mechanism that enables motion:

- Power or energy storage.
- Transmission.
- Linkages.
- Joint drive.
- Any governing or sequencing mechanism.

Show enough causal connection that the visitor understands why this machine can walk and why its motion remains limited.

## 4. Era Three: the advanced MurderBird

Era Three is the major transformation.

It gains an advanced fictional power source and capable actuators, together with the sensing and processing needed for intelligent, responsive behavior.

The owner describes its power as virtually unlimited for the purposes of the encounter. Use that as a fictional operating premise, not a real-world engineering claim.

Do not introduce routine winding, exhaustion, fuel depletion, or pressure-recovery behavior inherited from Era Two.

The later Iron Man suits are an analogy for this leap in capability. Give MurderBird its own power-system design and terminology. Do not copy the arc reactor’s name or recognizable design.

### Movement character

Era Three should be:

- Fast.
- Fluid.
- Coordinated.
- Precise.
- Powerful.
- Responsive.

Remove inherited clockwork hesitation and steam-era clunkiness from its primary movement.

Retain believable mass, balance, contact, and momentum. Abundant power does not mean teleportation, impossible joint travel, or movement without physical consequences.

It can accelerate sharply, stop with control, turn efficiently, and deliver a forceful attack.

### Behavior

This is the era that fulfills the agitated apex-predator brief:

- Autonomous pacing.
- Scanning and focused attention.
- Frustration with confinement.
- Deliberate cage testing.
- Visitor tracking.
- Attack preparation.
- Fast directed strikes.
- Controlled recovery.
- Continued attention after an encounter.

Its apparent intelligence should emerge through behavior and timing.

Do not add a cloud AI service merely because the fictional creature has advanced intelligence.

### Inspection

Distinguish:

- Power generation or supply.
- Power distribution.
- Actuation.
- Sensing.
- Processing and control.

Power and cognition are separate systems.

The advanced power source need not be an exposed glowing chest ornament. Develop a treatment consistent with MurderBird’s established identity, with any newly invented form clearly marked for creative review.

## 5. Implement genuine capability differences

Use explicit era-specific capabilities to determine available behaviors and controls.

A shared model or rig may be practical, but it must not accidentally give every era the same abilities.

At minimum:

- Era One disables autonomous locomotion and predatory behavior.
- Era Two enables limited mechanical traversal and appropriate routines.
- Era Three enables the complete advanced encounter behavior.
- Each era exposes only its relevant inspection assemblies.
- Controls and explanatory text reflect the selected era.

Treat the eras as different control systems, not merely material presets.

## 6. Handle era transitions deliberately

Switching eras must not carry incompatible behavior into the next machine.

Examples to prevent:

- Switching to Era One while a lunge continues.
- Leaving the puppet at an unsupported location in the cage.
- Retaining advanced tracking in Era Two.
- Showing an advanced power core inside Era One.
- Leaving parts detached when autonomous motion resumes.

Transition through a stable state, restore the appropriate support or staging, load the correct capabilities, and then enable that era’s interactions.

A brief reset or clearly presented reconstruction transition is preferable to a misleading instantaneous transformation.

Preserve camera orientation where practical, but prioritize valid physical staging.

## 7. Make the differences immediately legible

The visitor should understand the progression through observation:

- **Era One:** “Someone must operate it.”
- **Era Two:** “It can move itself, but its machinery limits it.”
- **Era Three:** “It is powerful, aware, and dangerous.”

Explain each era briefly in plain language.

Do not rely on lengthy labels to compensate for identical animation.

A useful comparison demonstration would show the same basic action across eras—for example, raising a leg, turning the head, or opening the mouth—followed by the locomotion capability each era actually possesses.

## 8. Acceptance criteria

### Era One

- Remains anchored with no independent translation.
- Is stationary when its controls are not operated.
- Demonstrates individual articulations through credible external control.
- Shows no internal powered machinery or autonomous intelligence.
- Remains physically supported during articulation.

### Era Two

- Walks with clearly limited speed, range, and coordination.
- Starts, stops, and turns with mechanically motivated irregularity.
- Displays a power-transmission system consistent with that motion.
- Has substantially less capability than Era Three.
- Does not simulate advanced tactical awareness.

### Era Three

- Moves quickly and fluidly while retaining mass and contact.
- Performs the complete predatory encounter behavior.
- Demonstrates advanced actuation and responsive attention.
- Operates without ordinary winding or power-depletion interruptions.
- Preserves MurderBird’s own appearance and fictional identity.

### Across all eras

- Differences remain obvious without sound or color changes.
- Inspection views match the actual selected construction.
- Era switching leaves no invalid pose, support, behavior, or assembly state.
- The same character remains recognizable.
- Source evidence, proposed reconstructions, and owner-approved decisions stay distinct.

## 9. Execute and demonstrate

Inspect the current era implementation and identify where it is only cosmetic.

Implement this capability progression while preserving the existing project’s privacy, provenance, architecture, and publication boundaries.

Return a side-by-side or sequential browser demonstration showing:

1. Era One at rest and under external articulation.
2. Era Two walking, stopping, and turning.
3. Era Three pacing, acquiring a target, attacking, and recovering.
4. The appropriate construction revealed in each era.

Do not report this clarification as implemented based solely on documentation or material changes.

The objective is to make MurderBird’s evolution visible in what each machine can do—and in how it does it.