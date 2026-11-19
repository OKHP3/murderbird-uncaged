# MurderBird: Uncaged — Stage Two: Give the Creature Physical Presence

## 1. Continue the project; change the immediate priority

You remain the primary architect and production lead for MurderBird: Uncaged. Continue from the current implementation and the original PRD.

This is the owner’s second-stage creative direction. It sharpens the intended outcome and establishes a more demanding behavior and animation milestone.

The first stage has not yet reached the physical presence I expected. My experience of the current result is primarily a static, spinnable model, and its likeness still falls short of the existing MurderBird imagery and video.

Treat that as owner feedback. Inspect the actual current implementation before describing which capabilities are present or absent.

I recognize this is a work in progress. I am not asking for photorealism in this phase. I am asking you to turn an inanimate object into a convincing mechanical creature with:

- A recognizable physical identity.
- Weight and articulated motion.
- Agitation and frustrated confinement.
- Attention and apparent intent.
- Autonomous behavior while nobody is interacting.
- Believable, responsive aggression when a visitor gets too close.

A few moving parts, a generic idle bob, or a click-triggered twitch will not satisfy this direction.

## 2. The emotional and physical target

Imagine approaching the cage of a very agitated apex predator.

It is pacing. It changes direction. It watches the space outside its enclosure. It tests the boundary. Occasionally it becomes still because something has caught its attention—not because its animation has stopped.

Its confinement frustrates it. It appears to be looking for an opportunity.

When a visitor approaches, the creature notices. Its posture changes. Its attention becomes focused. It may interrupt its pacing, square its weight, and lash out toward the visitor’s position.

Afterward, it must recover physically and remain behaviorally engaged. It should not instantly reset to a neutral pose as if nothing happened.

The visitor’s impression should be:

> “That thing is aware of me. It wants out. I am glad there is a cage between us.”

This must read through silhouette, movement, timing, orientation, and response. Sound and lighting can reinforce it, but they cannot carry the entire performance.

## 3. MurderBird is not a velociraptor

The Jurassic Park and Jurassic World cage encounters are references for tension, attention, confinement, and predatory performance.

They are not the anatomical design brief.

**Do not turn MurderBird into a velociraptor.**

Do not replace its appearance with a dinosaur mesh, add dinosaur skin beneath armor, or reshape its proportions merely to fit an available animation rig.

MurderBird’s existing visual references remain authoritative for its identity.

The owner’s fictional power comparison is that MurderBird could plausibly stand against one or several velociraptors because of its armor, mechanical power, and advanced AI-enhanced capabilities.

Translate that into:

- Formidable physical mass and protection.
- Controlled force.
- Deliberate threat assessment.
- Efficient, dangerous movement.
- Confidence and tactical attention.

Do not turn this comparison into a new combat simulator or a requirement to add dinosaur opponents. It communicates capability and presence.

“Advanced AI” describes the character’s fictional capabilities. It does not require an online language model, cloud inference, cameras, microphones, or collection of visitor data.

## 4. Interpret the game-quality benchmark correctly

Fortnite is a reference for the degree of polish and embodiment expected from an interactive game character: coherent form, readable poses, convincing animation, and immediate responsiveness.

It is not a request to copy Fortnite’s art style or assets.

Unreal Engine and other tools are candidates to evaluate, not predetermined solutions.

Identify the actual bottlenecks separately:

1. Character likeness and model construction.
2. Rigging and mechanical articulation.
3. Animation quality.
4. Behavior selection and transitions.
5. Contact, grounding, and spatial constraints.
6. Rendering and materials.
7. Browser delivery and performance.

Do not claim that changing the rendering engine will automatically solve deficiencies in the other six areas.

The current local package declares Three.js, with Vite and Web Audio in the established architecture. Verify the current implementation and applicable repository instructions.

Research broadly, but preserve the application architecture unless a separately scoped change is justified and approved. If you recommend another runtime, explain its browser delivery path, hosting requirements, cost, latency, operational burden, and migration implications.

Distinguish asset-authoring tools from the runtime that displays the final experience.

## 5. Establish a current baseline

Before editing, inspect the current scene and identify what actually exists.

Record:

- Current model source and production status.
- Whether the character uses articulated objects, a skeleton, deformation, or some combination.
- Existing animation clips and procedural motion.
- Current reaction triggers.
- Available collision or contact handling.
- Camera and input behavior.
- Inspection and exploded-view functionality.
- Actual browser performance.
- Differences between the local implementation and any deployed version.

Review the selected reference images and representative video footage directly.

Provide a concise gap assessment with separate findings for:

- Likeness.
- Locomotion.
- Idle performance.
- Predatory attention.
- Attack and recovery.
- Mechanical credibility.
- Integration.

Do not use the owner’s dissatisfaction as a substitute for technical inspection. Equally, do not dismiss that dissatisfaction because the application builds successfully.

## 6. Improve the character’s likeness while preparing it to move

Correct the most important identity defects before building an extensive animation library.

Prioritize the features that dominate recognition:

- Overall silhouette.
- Head and bill.
- Neck and shoulder relationship.
- Torso and pelvis.
- Leg proportions and stance.
- Feet and claws.
- Compact wing or forelimb structures.
- Armor arrangement and material history.

Use matched-angle comparisons against the selected MurderBird references.

Build an articulation plan that preserves these features through motion. A model that resembles MurderBird only in one static pose is insufficient.

Where reference material does not establish a hidden joint or mechanism, label the reconstruction as a production proposal.

Do not overwrite historical assets or promote a candidate to owner-approved status without evidence.

## 7. Give it a coherent autonomous behavior system

In the normal active encounter, MurderBird must perform without waiting for a click.

Use context-sensitive variation rather than a random playlist of unrelated animations.

At minimum, design the following behavior families:

| Behavior | Intended impression | Required physical cues |
|---|---|---|
| Restless watch | Contained energy | Weight shifts, head orientation, restrained mechanical adjustments |
| Pacing | Frustration with confinement | Real steps, travel across the enclosure, grounded turns |
| Boundary inspection | Searching for an opportunity | Attention to bars, seams, openings, or visitor positions |
| Cage test | Controlled aggression | Deliberate claw, beak, or body contact appropriate to its construction |
| Attention lock | Visitor detected | Gaze or head alignment followed by body preparation |
| Threat preparation | Attack may be imminent | Bracing, lowering or loading the body, anticipatory stillness |
| Strike or lunge | Dangerous power | Fast committed action with a readable target and bounded reach |
| Recovery | Force has consequences | Deceleration, restored balance, repositioning |
| Residual agitation | Encounter has affected it | Continued tracking, altered pacing, delayed relaxation |

Do not make every action equally likely at every moment.

Consider internal variables such as agitation, attention target, time since a boundary test, recent visitor interaction, and recovery state.

Use bounded variation, minimum dwell times, cooldowns, and valid transition rules. Avoid jitter, rapid state changes, and obvious identical repetition.

Provide reproducible behavior sequences for testing, such as a fixed random seed or developer playback mode. Keep diagnostic controls separate from the visitor interface.

## 8. Make pacing real locomotion

Pacing must involve movement through the enclosure.

Rotating a stationary model, translating it while its feet remain fixed, or looping a walk in place does not meet the requirement.

The motion should communicate:

- Alternating support.
- Foot lift, swing, placement, and contact.
- Pelvis and torso response.
- Head stabilization or purposeful counter-motion.
- Acceleration and deceleration.
- Appropriate stride length.
- Turning through articulated steps.
- Clearance from the cage.

Choose a locomotion method suitable for this mechanical body. You may combine authored animation with procedural correction.

Explain how travel speed and foot motion stay synchronized.

Evaluate foot sliding, floating, penetration, abrupt direction changes, and implausible balance. Fix these at the movement level rather than hiding them with camera angles.

The cage must have enough usable space for the intended behavior. Adjust staging thoughtfully if the current enclosure prevents credible pacing.

## 9. Mechanical embodiment, not biological imitation

The owner’s request for physiological characteristics means physical embodiment and coherent behavior. MurderBird remains a machine.

Do not automatically add lungs, flesh, organic breathing, or mammalian muscle deformation.

Use construction-appropriate equivalents:

- Loaded joints settling under weight.
- Mechanical tension before a strike.
- Plates responding to articulation.
- Linkages following their attachment points.
- Claws opening and closing with purpose.
- Head and neck mechanisms transmitting force.
- Appropriate lag, backlash, or vibration where supported.
- Controlled stillness that suggests attention.

Armor plates should remain rigid where they are rigid. They should not stretch like skin.

Cables, flexible elements, and overlapping plates may need different treatment from the structural frame. Choose a rig that supports those differences.

Avoid exaggerated springiness, rubbery limbs, toy-like bouncing, and constant whole-body oscillation.

A powerful machine can move quickly while still conveying mass. Speed must be accompanied by preparation, control, contact, and recovery.

## 10. Visitor proximity and attacks

Translate “getting too close” into a clear virtual interaction.

Do not assume the browser knows the visitor’s physical distance from the screen.

Establish a usable interaction model for mouse, touch, and keyboard. Possibilities include an explicit reach interaction, a virtual proximity target, or another understandable method.

Separate this from ordinary orbiting, zooming, scrolling, and selecting interface controls.

Requirements:

- The creature responds to the relevant virtual target.
- Approaching changes attention before or as aggression escalates.
- The attack is directed rather than a canned motion unrelated to the visitor.
- Contact or stopping distance respects the enclosure.
- Recovery returns the creature to a valid position and stance.
- Repeated input cannot stack attacks or break the pose.
- Retreat affects behavior in a coherent way.
- Touch and keyboard visitors can experience equivalent intent.

Predatory does not mean constantly flailing. Brief watchfulness can make the next movement more convincing.

No gore or injury depiction is required. Convey the danger through performance and the cage boundary.

## 11. Cage interaction must have physical credibility

A cage strike should connect with something.

Choose contact actions compatible with MurderBird’s anatomy and the enclosure:

- A claw grips or scrapes a bar.
- The bill snaps toward a reachable opening.
- A shoulder or armored surface presses against a boundary.
- A foot braces before force is applied.

These are candidate actions, not permission to invent anatomy.

Prevent obvious pass-through, detached contact, and impossible reach.

If the cage moves or vibrates, relate that response to the contact. Avoid unrelated screen shake as a substitute for physical interaction.

Preserve a visible distinction between a frustrated test of the enclosure and a visitor-directed attack.

## 12. Animation and behavior must work together

Provide a movement vocabulary, not one endless clip.

Create or obtain suitable movements for the required performance, including:

- Restless standing.
- Pacing steps.
- Starts and stops.
- Direction changes.
- Attention acquisition.
- Cage testing.
- Attack anticipation.
- Strike.
- Recovery.
- Return to watch or pacing.

The implementation may combine clips, articulated transforms, inverse kinematics, or other methods. Choose based on the character and delivery requirements.

Demonstrate:

- Smooth pose transitions.
- Consistent coordinate systems and scale.
- Correct root movement.
- Reliable interruption rules.
- No snapping back to an origin.
- Stable transitions between locomotion and stationary actions.
- Correct replay after repeated interactions.

Do not assume animation that works inside an authoring application will survive export unchanged. Test the actual exported asset in the browser early.

## 13. Investigate the supplied tools and references

The owner has supplied Blender, Mixamo, generation services, model marketplaces, and a workflow video as research leads.

Evaluate them for a specific production role. Do not assume that providing a link authorizes uploads, purchases, downloads of executables, or acceptance of new terms.

### Blender

Inspect the available installation and capabilities. Assess its suitability for modeling corrections, mechanical rigging, animation, contact controls, and browser-ready exports.

Prove the export path with a small animation before investing in a large production.

### Mixamo

Verify suitability for MurderBird’s non-humanoid mechanical anatomy.

Adobe’s documentation states that its auto-rigger and animation library are for bipedal humanoids. Do not distort MurderBird to fit that system or assume a human movement library will transfer convincingly.

If useful, specify the limited role and cleanup required. If unsuitable, move on promptly.

Reference: [Adobe Mixamo FAQ](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html).

### AI-assisted geometry services

Evaluate Meshy, Hyper3D, and Hi3D as possible sources of starting geometry or related production assistance.

Judge actual outputs for:

- Reference fidelity across views.
- Editable topology.
- Separation of rigid components.
- Articulation clearance.
- Rigging suitability.
- Texture and material quality.
- Export reliability.
- Privacy and rights.
- Cleanup effort.

A visually appealing fused mesh may be unsuitable for animation and exploded inspection.

### Model marketplaces and dinosaur references

Use velociraptor listings to investigate movement principles, rig structures, or production techniques where appropriate.

Do not adopt a dinosaur model as MurderBird.

Verify the license of each specific asset before download, derivative use, or browser distribution. A marketplace listing is not proof that its assets may be redistributed within this application.

### Supplied references

- [Creature-production workflow video](https://youtu.be/PW4DETRraW8)
- [Mixamo motion library](https://www.mixamo.com/#/?page=4&query=&type=Motion%2CMotionPack)
- [Meshy discovery](https://www.meshy.ai/discover?page=landing)
- [Hyper3D](https://hyper3d.ai/)
- [Hi3D](https://www.hi3d.ai/)
- [Meshy velociraptor references](https://www.meshy.ai/tags/velociraptor)
- [Sketchfab velociraptor references](https://sketchfab.com/tags/velociraptor)
- [TurboSquid animated velociraptor references](https://www.turbosquid.com/Search/3D-Models/velociraptor?animated=true)

Inspect the video itself where possible. Record useful timestamps and concrete observations. Do not claim to have watched it based on a title or search snippet.

For each resource, return a concise verdict: useful for a defined purpose, unsuitable for a stated reason, or unverified because access or evidence is missing.

Do not let tool exploration displace the production milestone.

## 14. Keep earlier requirements intact

Stage two prioritizes presence and behavior. It does not cancel the interactive interior or generation-specific construction.

Preserve the ability to open, inspect, separate, and reassemble relevant components.

Define a safe transition from encounter mode into inspection mode:

1. Finish or interrupt the current action according to clear rules.
2. Move to a stable inspection stance.
3. Suspend incompatible autonomous behavior.
4. Permit opening and exploded views.
5. Reassemble before returning to normal movement.

Do not allow detached assemblies to attack or resume pacing accidentally.

For the first convincing behavior demonstration, prioritize the later, advanced MurderBird incarnation that matches the owner’s description of AI-enhanced predatory capability.

Do not apply that intelligence indiscriminately to earlier wound-mechanical generations. Preserve their distinct capability limits and the narrative’s unresolved questions.

## 15. First milestone: a convincing encounter

Before expanding the full animation catalog, deliver one integrated encounter that proves the direction.

It must include:

- A materially improved MurderBird likeness.
- Autonomous pacing with grounded steps and turns.
- At least one distinct cage-testing action.
- Attention acquisition toward visitor input.
- An anticipatory pose.
- A directed attack.
- Physically credible recovery.
- Continued agitation after the encounter.
- Transition into and out of inspection mode.

Show an uninterrupted browser demonstration of approximately 60–90 seconds. Include a period with no input, an approach, an attack, retreat, and continued behavior.

Also provide the interactive local build. A video alone does not establish responsiveness.

Use ordinary viewing angles and lighting. Do not conceal defects with cuts or a cinematic presentation.

Submit this early enough that the owner can judge whether the creature’s personality and movement are finally moving in the right direction.

## 16. Acceptance tests

Use these as concrete review scenarios:

| Scenario | Passing result |
|---|---|
| No input for 60 seconds | The creature performs a coherent mixture of pacing, watchfulness, and boundary behavior rather than remaining inert or repeating one obvious short loop. |
| Inspect locomotion from multiple angles | Feet, travel, turns, and body response remain credible. |
| Approach from different virtual positions | Attention and attacks address the intended target. |
| Retreat after provoking it | The creature responds coherently and retains some agitation before settling. |
| Repeated interaction | No overlapping attacks, pose corruption, teleportation, or permanent stuck state. |
| Cage contact | The intended body part reaches a plausible contact point without obvious penetration. |
| Muted playback | The character still communicates weight, attention, and danger. |
| Matched reference views | MurderBird’s identity remains recognizable through representative poses. |
| Open inspection during activity | The scene transitions safely to a stable inspection state. |
| Reassemble and resume | Autonomous behavior returns without a broken rig or displaced components. |
| Reduced motion and pause | Visitors can access a calm, usable alternative. |
| Browser export verification | The delivered animation works in the actual application, not only in the authoring tool. |

The durations above are proposed review conditions, not claims about current capability.

Measure performance on identified devices and browsers. Record the conditions and remaining limits.

A passing build does not establish animation quality. A technically valid rig does not establish a convincing creature. Owner acceptance remains a separate status.

## 17. Working method and delegation

Use GPT-6 Astra with Ultra reasoning as the primary architect configuration where available. Delegate bounded supporting work to GPT-6 Luna agents where supported.

Useful parallel assignments include:

- Reference and silhouette analysis.
- Rig and asset inspection.
- Official documentation research.
- Animation export testing.
- Behavior implementation within a defined interface.
- Browser testing and evidence capture.

Retain primary responsibility for creative direction, integration, and review.

Do not let different workers invent conflicting anatomy, coordinate systems, animation names, or behavioral assumptions. Establish shared contracts before parallel implementation.

Load the narrowest applicable project skills from `.agents/skills/README.md`. Use evidence, research, validation, and handoff workflows where relevant.

Keep scope boundaries explicit and preserve other work in progress.

## 18. Safeguards and architecture decisions

Preserve the original privacy, provenance, licensing, and publication boundaries.

- No private archive uploads.
- No unapproved exposure of unpublished creative assets.
- No untrusted installers or security bypasses.
- No unauthorized purchases or credit consumption.
- No replacement of source assets with generated derivatives.
- No new runtime dependencies or architecture migration without the required scope decision.
- No publication through Replit.
- No claims of remote synchronization or deployment without current evidence.

Proceed autonomously with authorized research and reversible local production work.

When a material decision is required, present a concrete recommendation with its cost, privacy implications, expected benefit, and fallback. Continue independent work rather than halting the entire project.

## 19. Report results honestly

For this stage, report:

1. What currently prevented convincing motion.
2. Which likeness defects were corrected.
3. Which model and rig were used.
4. How animations were produced and exported.
5. How autonomous behavior and visitor interaction work.
6. What was verified in the actual browser.
7. What remains visibly weak or technically incomplete.
8. Which decisions still require owner review.

Use confirmed, inferred, proposed, and unknown labels where they matter.

Follow the repository’s required installation, build, emitted-asset inspection, WebGL, and fallback checks for application changes. Keep local verification, remote CI, deployment, and human acceptance separate.

Do not spend this phase primarily on menus, labels, decorative lighting, or additional documentation while the creature remains inert.

## 20. Start with the creature

Inspect the current implementation, diagnose the model–rig–animation–behavior gaps, and build the representative encounter.

The defining outcome is:

> MurderBird moves around its cage as a frustrated, formidable mechanical apex predator. It notices the visitor, prepares, attacks with intent, recovers with weight, and continues behaving after the interaction ends.

Make that visible and playable.