/**
 * Renderer-independent behavior selector for MurderBird's Builder encounter.
 *
 * Coordinates are metres in Three.js world space (Y up, forward +Z). `goal`
 * and `heading` are requests to the renderer; this module does not move a rig.
 * Feedback booleans describe the *current snapshot's* goal: `arrived` means
 * within 0.065 m, `aligned` within 0.045 rad, and `settled` means grounded with
 * no residual root motion. Contact states are gated on all three signals.
 *
 * Maker and Mechanic remain static interpretive studies. The Builder alone
 * receives autonomous pacing, varied route plans, cage tests, and
 * visitor-directed attacks. Autonomous beat families choose distinct routes,
 * attention points, intensity and timing. They still share the existing
 * normalized cage-test motion profile until the renderer implements those
 * family tags. Renderer feedback remains responsible for locomotion, feet,
 * contact geometry, and articulation.
 */

export const PRESENCE_DURATIONS = Object.freeze({
  watch: Object.freeze([1.8, 3.2]),
  paceMinimum: 0.65,
  boundaryMinimum: 0.55,
  cageTest: 2.4,
  notice: 0.65,
  approachMinimum: 0.25,
  warning: 0.75,
  strike: 0.18,
  contact: 0.2,
  recover: 0.9,
  agitated: Object.freeze([2.8, 4.3]),
  settle: 0.45,
});

export const CAGE_TEST_PHASE = Object.freeze({ buildEnd: 0.32, holdEnd: 0.75, releaseEnd: 1 });
export const CLAW_SCRAPE_DURATIONS = Object.freeze({ approach: 0.3, lift: 0.3, contact: 0.24, scrape: 0.42, release: 0.24, recovery: 0.42 });

const MAX_FRAME_DELTA = 0.1;
const VALID_ERAS = new Set(['maker', 'mechanic', 'builder']);
const RAIL_X = [-1.2, 0, 1.2];
// Fallback for renderer-independent state tests. A loaded model supplies its
// calibrated approach through feedback before either contact route is chosen.
const FRONT_CONTACT_Z = 1.02;
const AUTONOMOUS_BEATS = Object.freeze([
  Object.freeze({ id:'left-sweep', intention:'Sweep the left side before testing its rail.', routeKind:'left-sweep', actionFamily:'edge-probe', intensity:.56, recoveryStyle:'step-back-and-look-up', routeGoal:{x:-1.35,z:-.42}, routeFocus:{x:-1.2,y:1.18,z:1.1}, boundaryGoal:{x:-1.2,z:FRONT_CONTACT_Z}, boundaryFocus:{x:-1.2,y:1.3,z:2.15}, recoveryFocus:{x:-1.2,y:1.38,z:2.5}, watch:[1.2,2.3], boundary:[.8,1.45], action:[1.8,2.55], recovery:[.72,1.08] }),
  Object.freeze({ id:'right-sweep', intention:'Sweep the right side, then push at the outer rail.', routeKind:'right-sweep', actionFamily:'rail-press', intensity:.72, recoveryStyle:'hold-low-then-turn', routeGoal:{x:1.35,z:-.42}, routeFocus:{x:1.2,y:1.15,z:.9}, boundaryGoal:{x:1.2,z:FRONT_CONTACT_Z}, boundaryFocus:{x:1.2,y:1.3,z:2.1}, recoveryFocus:{x:.65,y:1.05,z:1.9}, watch:[1.7,3.0], boundary:[1.05,1.75], action:[2.1,2.8], recovery:[.9,1.35] }),
  Object.freeze({ id:'cross-left-to-center', intention:'Cross inward and test the center seam.', routeKind:'cross-inward', actionFamily:'seam-rattle', intensity:.64, recoveryStyle:'recenter-and-reorient', routeGoal:{x:-.65,z:.42}, routeFocus:{x:0,y:1.42,z:.55}, boundaryGoal:{x:0,z:FRONT_CONTACT_Z}, boundaryFocus:{x:0,y:1.25,z:2.25}, recoveryFocus:{x:0,y:1.48,z:2.5}, watch:[1.4,2.8], boundary:[.75,1.3], action:[1.55,2.25], recovery:[.65,1.15] }),
  Object.freeze({ id:'cross-right-to-center', intention:'Cross inward from the right and press the middle rail.', routeKind:'cross-inward', actionFamily:'rail-press', intensity:.82, recoveryStyle:'step-back-and-look-up', routeGoal:{x:.65,z:.42}, routeFocus:{x:0,y:1.15,z:.6}, boundaryGoal:{x:0,z:FRONT_CONTACT_Z}, boundaryFocus:{x:0,y:1.22,z:2.2}, recoveryFocus:{x:0,y:1.36,z:2.45}, watch:[1.8,3.2], boundary:[1.0,1.65], action:[1.9,2.7], recovery:[.85,1.4] }),
  Object.freeze({ id:'back-corner-left', intention:'Check the rear-left corner before returning to the bars.', routeKind:'corner-check', actionFamily:'seam-rattle', intensity:.48, recoveryStyle:'hold-low-then-turn', routeGoal:{x:-1.35,z:.42}, routeFocus:{x:-1.15,y:1.55,z:-.15}, boundaryGoal:{x:1.2,z:FRONT_CONTACT_Z}, boundaryFocus:{x:1.2,y:1.28,z:2.15}, recoveryFocus:{x:1.2,y:1.08,z:1.8}, watch:[2.0,3.4], boundary:[1.15,1.9], action:[1.45,2.1], recovery:[1.05,1.55] }),
  Object.freeze({ id:'back-corner-right', intention:'Check the rear-right corner, then probe the opposite rail.', routeKind:'corner-check', actionFamily:'edge-probe', intensity:.68, recoveryStyle:'recenter-and-reorient', routeGoal:{x:1.35,z:.42}, routeFocus:{x:1.15,y:1.5,z:-.15}, boundaryGoal:{x:-1.2,z:FRONT_CONTACT_Z}, boundaryFocus:{x:-1.2,y:1.25,z:2.1}, recoveryFocus:{x:-.6,y:1.3,z:2.15}, watch:[1.5,2.7], boundary:[1.0,1.7], action:[1.7,2.45], recovery:[.78,1.2] }),
  Object.freeze({ id:'short-center-check', intention:'Pause near center, then make a brief direct test.', routeKind:'short-approach', actionFamily:'rail-press', intensity:.52, recoveryStyle:'recenter-and-reorient', routeGoal:{x:0,z:-.42}, routeFocus:{x:0,y:1.25,z:.7}, boundaryGoal:{x:-1.2,z:FRONT_CONTACT_Z}, boundaryFocus:{x:-1.2,y:1.25,z:2.2}, recoveryFocus:{x:0,y:1.35,z:2.35}, watch:[2.2,3.8], boundary:[.65,1.1], action:[1.35,1.95], recovery:[.7,1.1] }),
  Object.freeze({ id:'side-step-center', intention:'Side-step across the front and test the opposite seam.', routeKind:'front-crossing', actionFamily:'edge-probe', intensity:.76, recoveryStyle:'hold-low-then-turn', routeGoal:{x:.65,z:.08}, routeFocus:{x:.8,y:1.18,z:1.0}, boundaryGoal:{x:-1.2,z:FRONT_CONTACT_Z}, boundaryFocus:{x:-1.2,y:1.32,z:2.2}, recoveryFocus:{x:-.5,y:1.05,z:1.9}, watch:[1.3,2.6], boundary:[.9,1.55], action:[2.0,2.65], recovery:[.88,1.3] }),
  Object.freeze({ id:'front-left-floor-scrape', intention:'Settle at the front-left edge, then scrape the floor with the left claw.', routeKind:'low-floor-probe', actionFamily:'claw-scrape', intensity:.63, recoveryStyle:'lift-back-and-replant', routeGoal:{x:-.65,z:.08}, routeFocus:{x:-.85,y:.65,z:.75}, boundaryGoal:{x:-1.2,z:FRONT_CONTACT_Z}, boundaryFocus:{x:-1.2,y:.8,z:1.55}, recoveryFocus:{x:-.8,y:1.12,z:1.8}, watch:[1.5,2.8], boundary:[.9,1.5], action:[1.8,2.3], recovery:[.8,1.25] }),
]);
const NORMALIZED_LIMIT = 1;

const finiteNumber = (value, fallback = 0) => typeof value === 'number' && Number.isFinite(value) ? value : fallback;
const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
const clonePoint = point => point ? { ...point } : null;

function makeRandom(seed) {
  let value = Number.isFinite(seed) ? Math.trunc(seed) >>> 0 : 927;
  return () => {
    value = (value + 0x6D2B79F5) >>> 0;
    let t = value;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/**
 * Create a seeded, bounded behavior state machine.
 *
 * `update(dt, feedback)` consumes seconds and renderer readiness flags for the
 * previous snapshot. It returns a frozen snapshot. `requestReach` maps x to
 * the discrete front rail targets -1.2, 0, or 1.2 m; y only steers attention.
 * An inspection request settles first. The owner integration should call
 * `setInspection(false)` after all parts have been reassembled.
 */
export function createPresenceState({ seed = 927, onChange } = {}) {
  const initialSeed = Number.isFinite(seed) ? Math.trunc(seed) >>> 0 : 927;
  let random = makeRandom(initialSeed);
  let state = 'watch';
  let elapsed = 0;
  let stateDuration = PRESENCE_DURATIONS.watch[0];
  let reach = { x: 0, y: 0 };
  let reachWorldX = 0;
  let goal = null;
  let heading = 0;
  let lookTarget = { x: 0, y: 1.25, z: 2.55 };
  let paused = false;
  let inspection = false;
  let inspectionRequested = false;
  let reducedMotion = false;
  let era = 'builder';
  let visitorPresent = false;
  let actionKind = null;
  let agitation = 0.42;
  let lastPosition = { x: 0, z: 0 };
  let retreatRequested = false;
  let reducedStopPending = false;
  let reducedStopSpeed = 0;
  let currentBeat = null;
  let contactApproachZ = FRONT_CONTACT_Z;
  let recentBeatIds = [];
  let recentActionFamilies = [];
  let clawStage = null;
  let lastRendererFeedback = { arrived: true, settled: true, aligned: true };

  function canReachNow() {
    return era === 'builder'
      && !paused
      && !inspection
      && !inspectionRequested
      && ['watch', 'pace', 'boundary'].includes(state);
  }

  function speedNow() {
    if (paused && !(inspectionRequested && state === 'settle')) return 0;
    if (reducedStopPending) return reducedStopSpeed;
    if (state === 'inspection' || state === 'settle' || state === 'watch' || state === 'agitated') return 0;
    if (reducedMotion && !reducedStopPending) return 0;
    if (state === 'pace') return 0.55;
    if (state === 'boundary') return 0.28;
    if (state === 'approach') return 0.72;
    return 0;
  }

  function phaseNow() {
    if (state === 'inspection') return 1;
    if (!(stateDuration > 0)) return 0;
    return clamp(elapsed / stateDuration, 0, 1);
  }

  function snapshot() {
    return Object.freeze({
      state,
      phase: phaseNow(),
      reach: Object.freeze({ x: reach.x, y: reach.y }),
      paused,
      inspection,
      reducedMotion,
      era,
      goal: clonePoint(goal) && Object.freeze(clonePoint(goal)),
      heading: Number.isFinite(heading) ? heading : null,
      lookTarget: clonePoint(lookTarget) && Object.freeze(clonePoint(lookTarget)),
      speed: speedNow(),
      agitation: clamp(agitation, 0, 1),
      visitorPresent,
      actionKind,
      clawAction: clawStage ? Object.freeze({
        phase: stateDuration > 0 ? clamp(elapsed / stateDuration, 0, 1) : 0,
        stage: clawStage,
        side: 'left',
        target: 'floor-scrape',
      }) : null,
      canClawAction: era === 'builder' && !paused && !inspection && !inspectionRequested && !reducedMotion
        && state === 'watch' && !visitorPresent && !clawStage
        && lastRendererFeedback.settled === true && lastRendererFeedback.aligned === true,
      beatId: currentBeat?.id ?? null,
      intention: currentBeat?.intention ?? (visitorPresent ? 'respond to the visitor at the selected rail' : null),
      routeKind: currentBeat?.routeKind ?? (visitorPresent ? 'visitor-approach' : null),
      actionFamily: currentBeat?.actionFamily ?? (visitorPresent ? 'visitor-strike' : null),
      intensity: currentBeat?.intensity ?? (visitorPresent ? 1 : null),
      recoveryStyle: currentBeat?.recoveryStyle ?? (visitorPresent ? 'complete committed contact, then disengage' : null),
      inspectionRequested,
      canReach: canReachNow(),
    });
  }

  function emit() {
    if (typeof onChange === 'function') onChange(snapshot());
  }

  function durationBetween([min, max]) {
    return min + random() * (max - min);
  }

  function chooseAutonomousBeat() {
    let candidates = AUTONOMOUS_BEATS.filter(beat => !recentBeatIds.includes(beat.id));
    const previousFamily = recentActionFamilies.at(-1);
    const withoutImmediateRepeat = candidates.filter(beat => beat.actionFamily !== previousFamily);
    if (withoutImmediateRepeat.length) candidates = withoutImmediateRepeat;
    if (!candidates.length) candidates = AUTONOMOUS_BEATS;
    const weighted = candidates.map(beat => ({ beat, weight: recentActionFamilies.slice(-2).includes(beat.actionFamily) ? 0.32 : 1 }));
    const totalWeight = weighted.reduce((sum, entry) => sum + entry.weight, 0);
    let choice = random() * totalWeight;
    let beat = weighted.at(-1).beat;
    for (const entry of weighted) {
      choice -= entry.weight;
      if (choice < 0) { beat = entry.beat; break; }
    }
    recentBeatIds = [...recentBeatIds, beat.id].slice(-3);
    recentActionFamilies = [...recentActionFamilies, beat.actionFamily].slice(-2);
    return beat;
  }

  function scheduleAutonomousWatch({ nextAgitation = agitation } = {}) {
    currentBeat = chooseAutonomousBeat();
    lookTarget = clonePoint(currentBeat.boundaryFocus);
    enter('watch', durationBetween(currentBeat.watch), {
      goal: null,
      lookTarget,
      actionKind: null,
      agitation: nextAgitation,
    });
  }

  function setGoal(nextGoal, nextHeading = heading) {
    goal = nextGoal ? { x: finiteNumber(nextGoal.x), z: finiteNumber(nextGoal.z) } : null;
    heading = Number.isFinite(nextHeading) ? nextHeading : null;
  }

  function enter(nextState, duration = 0, options = {}) {
    state = nextState;
    elapsed = 0;
    stateDuration = duration;
    if ('goal' in options) setGoal(options.goal, options.heading ?? heading);
    if ('lookTarget' in options) lookTarget = clonePoint(options.lookTarget);
    if ('actionKind' in options) actionKind = options.actionKind;
    if ('agitation' in options) agitation = clamp(finiteNumber(options.agitation, agitation), 0, 1);
    emit();
  }

  function advanceClawAction(fb) {
    if (!clawStage) return false;
    if (clawStage === 'approach') {
      if (elapsed >= stateDuration && fb.arrived === true && fb.settled === true && fb.aligned === true) {
        clawStage = 'lift'; enter('claw-scrape', CLAW_SCRAPE_DURATIONS.lift, { goal: null, actionKind: 'claw-scrape' });
        return true;
      }
      return false;
    }
    if (elapsed < stateDuration) return false;
    if (clawStage === 'contact' && fb.clawContact !== true) {
      if (elapsed < stateDuration + 0.6) return false;
      clawStage = 'recovery';
      enter('claw-scrape', CLAW_SCRAPE_DURATIONS.recovery, { goal: null, actionKind: 'claw-scrape' });
      return true;
    }
    const next = { lift: 'contact', contact: 'scrape', scrape: 'release', release: 'recovery', recovery: null }[clawStage];
    if (next) {
      clawStage = next;
      enter('claw-scrape', CLAW_SCRAPE_DURATIONS[next], { goal: null, actionKind: 'claw-scrape' });
      return true;
    } else {
      clawStage = null;
      actionKind = null;
      enter('settle', PRESENCE_DURATIONS.settle, { goal: null, actionKind: null });
      return true;
    }
  }

  function settledFeedback(feedback) {
    return feedback.arrived === true && feedback.settled === true && feedback.aligned === true;
  }

  function settleInspectionIfReady(feedback) {
    if (!inspectionRequested || elapsed < PRESENCE_DURATIONS.settle || feedback.settled !== true) return false;
    inspection = true;
    visitorPresent = false;
    actionKind = null;
    reducedStopPending = false;
    enter('inspection', 0, { goal: null, actionKind: null, agitation: Math.min(agitation, 0.3) });
    return true;
  }

  function headingTo(nextGoal) {
    return Math.atan2(nextGoal.x - lastPosition.x, nextGoal.z - lastPosition.z);
  }

  function startBoundary() {
    const nextGoal = { x: currentBeat?.boundaryGoal.x ?? 0, z: contactApproachZ };
    setGoal(nextGoal, 0);
    lookTarget = clonePoint(currentBeat?.boundaryFocus) ?? { x: nextGoal.x, y: 1.28, z: 2.1 };
    agitation = Math.min(0.94, agitation + .04 + (currentBeat?.intensity ?? .5) * .08);
  }

  function visitorTarget(point) {
    return {
      x: reachWorldX,
      y: clamp(1.2 + point.y * 0.48, 0.72, 1.85),
      z: 2.65,
    };
  }

  function startAgitated(look = lookTarget) {
    visitorPresent = visitorPresent && !retreatRequested;
    retreatRequested = false;
    actionKind = null;
    reducedStopPending = false;
    enter('agitated', durationBetween(PRESENCE_DURATIONS.agitated), {
      goal: null,
      lookTarget: look,
      actionKind: null,
      agitation: Math.max(0.72, agitation),
    });
  }

  function update(dtSeconds, feedback = {}) {
    const dt = clamp(finiteNumber(dtSeconds), 0, MAX_FRAME_DELTA);
    const fb = feedback && typeof feedback === 'object' ? feedback : {};
    lastRendererFeedback = { arrived: fb.arrived === true, settled: fb.settled === true, aligned: fb.aligned === true };
    if (Number.isFinite(fb.contactApproachZ) && fb.contactApproachZ >= -.65 && fb.contactApproachZ <= 1.08) contactApproachZ = fb.contactApproachZ;

    // An inspection request is allowed to settle even while paused. The scene
    // integrator must let the grounding controller finish this safe transition.
    const settlingForInspectionWhilePaused = paused && inspectionRequested && ['settle', 'claw-scrape'].includes(state);
    if ((paused && !settlingForInspectionWhilePaused) || dt === 0) return snapshot();

    elapsed += dt;

    if (state === 'inspection') return snapshot();

    if (inspectionRequested) {
      if (state === 'claw-scrape') {
        if (!advanceClawAction(fb)) emit();
        return snapshot();
      }
      if (state !== 'settle') {
        enter('settle', PRESENCE_DURATIONS.settle, { goal: null, actionKind: null });
      } else {
        settleInspectionIfReady(fb);
      }
      return snapshot();
    }

    if (state === 'claw-scrape') {
      if (!advanceClawAction(fb)) emit();
      return snapshot();
    }

    if (reducedMotion || era !== 'builder') {
      if (reducedStopPending) {
        if (fb.settled === true) {
          reducedStopPending = false;
          reducedStopSpeed = 0;
          visitorPresent = false;
          actionKind = null;
          currentBeat = null;
          enter('watch', durationBetween(PRESENCE_DURATIONS.watch), { goal: null, actionKind: null, agitation: Math.min(agitation, 0.48) });
        }
        return snapshot();
      }
      if (state === 'notice' && elapsed >= stateDuration) enter('settle', PRESENCE_DURATIONS.settle, { goal: null, actionKind: null });
      else if (state === 'settle' && elapsed >= stateDuration && fb.settled === true) {
        visitorPresent = false;
        actionKind = null;
        currentBeat = null;
        enter('watch', durationBetween(PRESENCE_DURATIONS.watch), { goal: null, actionKind: null });
      } else if (state !== 'watch' && state !== 'notice' && state !== 'settle') {
        visitorPresent = false;
        actionKind = null;
        currentBeat = null;
        enter('watch', durationBetween(PRESENCE_DURATIONS.watch), { goal: null, actionKind: null });
      }
      return snapshot();
    }

    switch (state) {
      case 'watch': {
        if (elapsed >= stateDuration) {
          if (!currentBeat) currentBeat = chooseAutonomousBeat();
          const route = currentBeat.routeGoal;
          setGoal(route, headingTo(route));
          lookTarget = clonePoint(currentBeat.routeFocus);
          agitation = Math.min(0.84, agitation + currentBeat.intensity * 0.025);
          enter('pace', Math.max(PRESENCE_DURATIONS.paceMinimum, 1.25 + Math.hypot(route.x - lastPosition.x, route.z - lastPosition.z) * 1.05), { goal: route, heading: headingTo(route), lookTarget });
        }
        break;
      }
      case 'pace':
        if (elapsed >= stateDuration && settledFeedback(fb)) {
          lastPosition = goal ? { x: goal.x, z: goal.z } : lastPosition;
          startBoundary();
          enter('boundary', durationBetween(currentBeat?.boundary ?? [1.0, 1.7]), { goal, heading: 0, lookTarget });
        }
        break;
      case 'boundary':
        if (elapsed >= stateDuration && settledFeedback(fb)) {
          lastPosition = goal ? { x: goal.x, z: goal.z } : lastPosition;
          agitation = Math.min(0.98, agitation + (currentBeat?.intensity ?? .5) * .09);
          if (currentBeat?.actionFamily === 'claw-scrape') {
            clawStage = 'approach';
            enter('claw-scrape', CLAW_SCRAPE_DURATIONS.approach, { goal: null, actionKind: 'claw-scrape', lookTarget: currentBeat.boundaryFocus, agitation });
          } else {
            enter('cage-test', durationBetween(currentBeat?.action ?? [PRESENCE_DURATIONS.cageTest, PRESENCE_DURATIONS.cageTest]), { goal: { ...lastPosition }, heading: 0, actionKind: 'cage', agitation });
          }
        }
        break;
      case 'cage-test':
        if (elapsed >= stateDuration) {
          lookTarget = clonePoint(currentBeat?.recoveryFocus) ?? lookTarget;
          enter('recover', durationBetween(currentBeat?.recovery ?? [PRESENCE_DURATIONS.recover, PRESENCE_DURATIONS.recover]), { goal: null, actionKind: 'cage', lookTarget, agitation: Math.min(1, agitation + (currentBeat?.intensity ?? .5) * .06) });
        }
        break;
      case 'notice':
        if (elapsed >= stateDuration) {
          if (reducedMotion) enter('settle', PRESENCE_DURATIONS.settle, { goal: null, actionKind: null });
          else enter('approach', Math.max(PRESENCE_DURATIONS.approachMinimum, 0.4 + Math.abs(reachWorldX) * 0.15), {
            goal: { x: reachWorldX, z: contactApproachZ }, heading: 0,
            lookTarget: visitorTarget(reach), actionKind: 'visitor', agitation: 0.92,
          });
        }
        break;
      case 'approach':
        if (elapsed >= stateDuration && settledFeedback(fb)) {
          lastPosition = goal ? { x: goal.x, z: goal.z } : lastPosition;
          enter('warning', PRESENCE_DURATIONS.warning, { goal, heading: 0, actionKind: 'visitor', agitation: 0.96 });
        }
        break;
      case 'warning':
        if (elapsed >= stateDuration && settledFeedback(fb)) {
          enter('strike', PRESENCE_DURATIONS.strike, { goal, heading: 0, actionKind: 'visitor', agitation: 1 });
        }
        break;
      case 'strike':
        if (elapsed >= stateDuration && settledFeedback(fb)) {
          enter('contact', PRESENCE_DURATIONS.contact, { goal, heading: 0, actionKind: 'visitor', agitation: 1 });
        }
        break;
      case 'contact':
        if (elapsed >= stateDuration) enter('recover', PRESENCE_DURATIONS.recover, { goal: null, actionKind: 'visitor', agitation: 1 });
        break;
      case 'recover':
        if (elapsed >= stateDuration) {
          if (inspectionRequested) enter('settle', PRESENCE_DURATIONS.settle, { goal: null, actionKind: null });
          else startAgitated(lookTarget);
        }
        break;
      case 'agitated':
        agitation = Math.max(0.56, 0.9 - elapsed * 0.055);
        if (elapsed >= stateDuration) enter('settle', PRESENCE_DURATIONS.settle, { goal: null, actionKind: null, agitation: Math.max(0.52, agitation - 0.08) });
        break;
      case 'settle':
        if (elapsed >= stateDuration && fb.settled === true) {
          if (inspectionRequested) settleInspectionIfReady(fb);
          else {
            visitorPresent = false;
            actionKind = null;
            agitation = Math.max(0.4, agitation - 0.12);
            scheduleAutonomousWatch({ nextAgitation:agitation });
          }
        }
        break;
      default:
        scheduleAutonomousWatch();
    }
    emit();
    return snapshot();
  }

  function requestReach(input = {}) {
    if (!canReachNow()) return false;
    const safeInput = input && typeof input === 'object' ? input : {};
    const x = clamp(finiteNumber(safeInput.x), -NORMALIZED_LIMIT, NORMALIZED_LIMIT);
    const y = clamp(finiteNumber(safeInput.y), -NORMALIZED_LIMIT, NORMALIZED_LIMIT);
    const worldX = RAIL_X.reduce((closest, candidate) => Math.abs(candidate - x * 1.2) < Math.abs(closest - x * 1.2) ? candidate : closest, RAIL_X[0]);
    reach = { x, y };
    reachWorldX = worldX;
    currentBeat = null;
    clawStage = null;
    visitorPresent = true;
    retreatRequested = false;
    lookTarget = visitorTarget(reach);
    actionKind = 'visitor';
    agitation = Math.max(0.82, agitation);
    enter('notice', reducedMotion ? 0.75 : PRESENCE_DURATIONS.notice, { goal: null, lookTarget, actionKind: 'visitor', agitation });
    // Keep the normalized input in the public snapshot and the discrete rail
    // target privately for the renderer's world-space travel goal.
    return true;
  }

  function requestClawAction() {
    const current = snapshot();
    if (!current.canClawAction) return false;
    visitorPresent = false;
    retreatRequested = false;
    currentBeat = null;
    clawStage = 'approach';
    actionKind = 'claw-scrape';
    goal = null;
    lookTarget = { x: 0, y: 0.08, z: 0.55 };
    enter('claw-scrape', CLAW_SCRAPE_DURATIONS.approach, { goal: null, actionKind: 'claw-scrape', agitation: Math.max(agitation, 0.5) });
    return true;
  }

  function requestRetreat() {
    if (!visitorPresent) return false;
    visitorPresent = false;
    retreatRequested = true;
    const retreatLook = { x: reachWorldX, y: 1.15, z: 3.1 };
    lookTarget = retreatLook;
    if (['notice', 'approach', 'warning'].includes(state)) {
      actionKind = null;
      agitation = Math.max(0.76, agitation);
      startAgitated(retreatLook);
    } else if (['strike', 'contact', 'recover'].includes(state)) {
      // A committed action completes its contact and recovery before decay.
      emit();
    } else {
      retreatRequested = false;
      actionKind = null;
      agitation = Math.max(0.66, agitation);
      emit();
    }
    return true;
  }

  function setInspection(value) {
    const next = Boolean(value);
    if (next === inspectionRequested) return snapshot();
    inspectionRequested = next;
    if (next) {
      visitorPresent = false;
      retreatRequested = false;
      currentBeat = null;
      if (clawStage) {
        clawStage = 'recovery';
        actionKind = 'claw-scrape';
        enter('claw-scrape', CLAW_SCRAPE_DURATIONS.recovery, { goal: null, actionKind: 'claw-scrape' });
        return snapshot();
      }
      // Inspection interrupts any reaction immediately. The renderer grounds
      // the pose during settle and only then may expose the parts.
      actionKind = null;
      enter('settle', PRESENCE_DURATIONS.settle, { goal: null, actionKind: null });
    } else if (inspection) {
      inspection = false;
      inspectionRequested = false;
      visitorPresent = false;
      actionKind = null;
      agitation = Math.max(0.42, agitation);
      if (era === 'builder' && !reducedMotion) scheduleAutonomousWatch({ nextAgitation:agitation });
      else enter('watch', durationBetween(PRESENCE_DURATIONS.watch), { goal: null, lookTarget, actionKind: null, agitation });
    } else {
      emit();
    }
    return snapshot();
  }

  function setPaused(value) {
    const next = Boolean(value);
    if (paused !== next) {
      paused = next;
      emit();
    }
    return snapshot();
  }

  function setReducedMotion(value) {
    const next = Boolean(value);
    if (reducedMotion === next) return snapshot();
    reducedMotion = next;
    if (next && !inspection) {
      if (clawStage) {
        clawStage = 'recovery';
        enter('claw-scrape', CLAW_SCRAPE_DURATIONS.recovery, { goal: null, actionKind: 'claw-scrape' });
        return snapshot();
      }
      currentBeat = null;
      const wasTraveling = ['pace', 'boundary', 'approach'].includes(state);
      visitorPresent = false;
      retreatRequested = false;
      actionKind = null;
      if (wasTraveling) {
        reducedStopPending = true;
        reducedStopSpeed = state === 'pace' ? 0.55 : state === 'boundary' ? 0.28 : 0.72;
        // Keep the current goal until the renderer reports a grounded step.
        enter('settle', PRESENCE_DURATIONS.settle, { goal, actionKind: null, agitation: Math.min(0.55, agitation) });
      } else if (['strike', 'contact', 'warning', 'notice', 'cage-test', 'recover'].includes(state)) {
        reducedStopPending = false;
        reducedStopSpeed = 0;
        enter('settle', PRESENCE_DURATIONS.settle, { goal: null, actionKind: null, agitation: Math.min(0.55, agitation) });
      } else {
        enter('watch', durationBetween(PRESENCE_DURATIONS.watch), { goal: null, actionKind: null, agitation: Math.min(0.48, agitation) });
      }
    } else {
      emit();
    }
    return snapshot();
  }

  function setEra(value) {
    if (!VALID_ERAS.has(value)) return false;
    if (era === value) return true;
    era = value;
    currentBeat = null;
    visitorPresent = false;
    retreatRequested = false;
    actionKind = null;
    clawStage = null;
    goal = null;
    reducedStopPending = false;
    reducedStopSpeed = 0;
    reach = { x: 0, y: 0 };
    reachWorldX = 0;
    if (inspection) enter('inspection', 0, { goal: null, actionKind: null, agitation: Math.min(agitation, 0.3) });
    else if (inspectionRequested) enter('settle', PRESENCE_DURATIONS.settle, { goal: null, actionKind: null });
    else if (value === 'builder' && !reducedMotion) scheduleAutonomousWatch({ nextAgitation:.42 });
    else enter('watch', durationBetween(PRESENCE_DURATIONS.watch), { goal: null, actionKind: null, agitation: value === 'builder' ? 0.42 : 0.12 });
    return true;
  }

  function reset() {
    random = makeRandom(initialSeed);
    recentBeatIds = [];
    recentActionFamilies = [];
    elapsed = 0;
    stateDuration = durationBetween(PRESENCE_DURATIONS.watch);
    reach = { x: 0, y: 0 };
    reachWorldX = 0;
    goal = null;
    heading = 0;
    lookTarget = { x: 0, y: 1.25, z: 2.55 };
    visitorPresent = false;
    retreatRequested = false;
    reducedStopPending = false;
    reducedStopSpeed = 0;
    actionKind = null;
    clawStage = null;
    agitation = era === 'builder' ? 0.42 : 0.12;
    currentBeat = null;
    state = inspection ? 'inspection' : inspectionRequested ? 'settle' : 'watch';
    if (state === 'settle') stateDuration = PRESENCE_DURATIONS.settle;
    else if (state === 'watch' && era === 'builder' && !reducedMotion) {
      currentBeat = chooseAutonomousBeat();
      lookTarget = clonePoint(currentBeat.boundaryFocus);
      stateDuration = durationBetween(currentBeat.watch);
    } else stateDuration = durationBetween(PRESENCE_DURATIONS.watch);
    emit();
    return snapshot();
  }

  if (era === 'builder' && !reducedMotion) {
    currentBeat = chooseAutonomousBeat();
    lookTarget = clonePoint(currentBeat.boundaryFocus);
    stateDuration = durationBetween(currentBeat.watch);
  } else stateDuration = durationBetween(PRESENCE_DURATIONS.watch);

  return Object.freeze({
    update,
    getSnapshot: snapshot,
    requestReach,
    requestClawAction,
    requestRetreat,
    setInspection,
    setPaused,
    setReducedMotion,
    setEra,
    reset,
  });
}
