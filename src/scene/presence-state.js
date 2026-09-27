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
 * receives autonomous pacing, cage tests, and visitor-directed attacks.
 * `cage-test` uses a 2.4 s normalized phase for a slow press: 0.32 build,
 * 0.43 hold, then 0.25 release. Renderer feedback remains responsible for
 * locomotion, feet, contact geometry, and articulation.
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

const MAX_FRAME_DELTA = 0.1;
const VALID_ERAS = new Set(['maker', 'mechanic', 'builder']);
const PACE_X = [-1.35, -0.65, 0.65, 1.35];
const PACE_Z = [-0.42, 0.08, 0.42];
const RAIL_X = [-1.2, 0, 1.2];
const FRONT_CONTACT_Z = 0.7;
const NORMALIZED_LIMIT = 1;

const finiteNumber = (value, fallback = 0) => typeof value === 'number' && Number.isFinite(value) ? value : fallback;
const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
const lerp = (a, b, t) => a + (b - a) * t;
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

  function chooseWatchRoute() {
    if (random() < 0.68) {
      const x = PACE_X[Math.floor(random() * PACE_X.length)];
      const z = PACE_Z[Math.floor(random() * PACE_Z.length)];
      if (Math.abs(x - lastPosition.x) < 0.1 && Math.abs(z - lastPosition.z) < 0.1) {
        return { state: 'pace', goal: { x: -x, z: z === PACE_Z[0] ? PACE_Z[2] : PACE_Z[0] } };
      }
      return { state: 'pace', goal: { x, z } };
    }
    const x = RAIL_X[Math.floor(random() * RAIL_X.length)];
    return { state: 'boundary', goal: { x, z: FRONT_CONTACT_Z } };
  }

  function headingTo(nextGoal) {
    return Math.atan2(nextGoal.x - lastPosition.x, nextGoal.z - lastPosition.z);
  }

  function startBoundary() {
    const x = RAIL_X[Math.floor(random() * RAIL_X.length)];
    const nextGoal = { x, z: FRONT_CONTACT_Z };
    setGoal(nextGoal, 0);
    lookTarget = { x, y: 1.28, z: 2.1 };
    agitation = Math.min(0.9, agitation + 0.12);
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

    // An inspection request is allowed to settle even while paused. The scene
    // integrator must let the grounding controller finish this safe transition.
    const settlingForInspectionWhilePaused = paused && inspectionRequested && state === 'settle';
    if ((paused && !settlingForInspectionWhilePaused) || dt === 0) return snapshot();

    elapsed += dt;

    if (state === 'inspection') return snapshot();

    if (inspectionRequested) {
      if (state !== 'settle') {
        enter('settle', PRESENCE_DURATIONS.settle, { goal: null, actionKind: null });
      } else {
        settleInspectionIfReady(fb);
      }
      return snapshot();
    }

    if (reducedMotion || era !== 'builder') {
      if (reducedStopPending) {
        if (fb.settled === true) {
          reducedStopPending = false;
          reducedStopSpeed = 0;
          visitorPresent = false;
          actionKind = null;
          enter('watch', durationBetween(PRESENCE_DURATIONS.watch), { goal: null, agitation: Math.min(agitation, 0.48) });
        }
        return snapshot();
      }
      if (state === 'notice' && elapsed >= stateDuration) enter('settle', PRESENCE_DURATIONS.settle, { goal: null, actionKind: null });
      else if (state === 'settle' && elapsed >= stateDuration && fb.settled === true) {
        visitorPresent = false;
        actionKind = null;
        enter('watch', durationBetween(PRESENCE_DURATIONS.watch), { goal: null });
      } else if (state !== 'watch' && state !== 'notice' && state !== 'settle') {
        visitorPresent = false;
        actionKind = null;
        enter('watch', durationBetween(PRESENCE_DURATIONS.watch), { goal: null });
      }
      return snapshot();
    }

    switch (state) {
      case 'watch': {
        if (elapsed >= stateDuration) {
          const route = chooseWatchRoute();
          if (route.state === 'pace') {
            setGoal(route.goal, headingTo(route.goal));
            agitation = Math.min(0.82, agitation + 0.04);
            enter('pace', Math.max(PRESENCE_DURATIONS.paceMinimum, 1.6 + Math.hypot(route.goal.x - lastPosition.x, route.goal.z - lastPosition.z)), { goal: route.goal, heading: headingTo(route.goal) });
          } else {
            startBoundary();
            enter('boundary', Math.max(PRESENCE_DURATIONS.boundaryMinimum, 1.1 + Math.abs(goal.x - lastPosition.x) * 0.3), { goal, heading: 0 });
          }
        }
        break;
      }
      case 'pace':
        if (elapsed >= stateDuration && settledFeedback(fb)) {
          lastPosition = goal ? { x: goal.x, z: goal.z } : lastPosition;
          startBoundary();
          enter('boundary', Math.max(PRESENCE_DURATIONS.boundaryMinimum, 1.1 + Math.abs(goal.x - lastPosition.x) * 0.3), { goal, heading: 0 });
        }
        break;
      case 'boundary':
        if (elapsed >= stateDuration && settledFeedback(fb)) {
          lastPosition = goal ? { x: goal.x, z: FRONT_CONTACT_Z } : lastPosition;
          agitation = Math.min(0.94, agitation + 0.08);
          enter('cage-test', PRESENCE_DURATIONS.cageTest, { goal: { x: lastPosition.x, z: FRONT_CONTACT_Z }, heading: 0, actionKind: 'cage', agitation });
        }
        break;
      case 'cage-test':
        if (elapsed >= stateDuration) {
          enter('recover', PRESENCE_DURATIONS.recover, { goal: null, actionKind: 'cage', agitation: Math.min(1, agitation + 0.05) });
        }
        break;
      case 'notice':
        if (elapsed >= stateDuration) {
          if (reducedMotion) enter('settle', PRESENCE_DURATIONS.settle, { goal: null, actionKind: null });
          else enter('approach', Math.max(PRESENCE_DURATIONS.approachMinimum, 0.4 + Math.abs(reachWorldX) * 0.15), {
            goal: { x: reachWorldX, z: FRONT_CONTACT_Z }, heading: 0,
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
            enter('watch', durationBetween(PRESENCE_DURATIONS.watch), { goal: null, agitation });
          }
        }
        break;
      default:
        enter('watch', durationBetween(PRESENCE_DURATIONS.watch), { goal: null });
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
      enter('watch', durationBetween(PRESENCE_DURATIONS.watch), { goal: null, lookTarget, actionKind: null, agitation });
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
    visitorPresent = false;
    retreatRequested = false;
    actionKind = null;
    goal = null;
    reducedStopPending = false;
    reducedStopSpeed = 0;
    reach = { x: 0, y: 0 };
    reachWorldX = 0;
    if (inspection) enter('inspection', 0, { goal: null, actionKind: null, agitation: Math.min(agitation, 0.3) });
    else if (inspectionRequested) enter('settle', PRESENCE_DURATIONS.settle, { goal: null, actionKind: null });
    else enter('watch', durationBetween(PRESENCE_DURATIONS.watch), { goal: null, actionKind: null, agitation: value === 'builder' ? 0.42 : 0.12 });
    return true;
  }

  function reset() {
    random = makeRandom(initialSeed);
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
    agitation = era === 'builder' ? 0.42 : 0.12;
    state = inspection ? 'inspection' : inspectionRequested ? 'settle' : 'watch';
    if (state === 'settle') stateDuration = PRESENCE_DURATIONS.settle;
    emit();
    return snapshot();
  }

  stateDuration = durationBetween(PRESENCE_DURATIONS.watch);

  return Object.freeze({
    update,
    getSnapshot: snapshot,
    requestReach,
    requestRetreat,
    setInspection,
    setPaused,
    setReducedMotion,
    setEra,
    reset,
  });
}
