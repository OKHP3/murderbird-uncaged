import { createPresenceState } from './presence-state.js';

/** Capability flags exposed to the exhibit UI and renderer for each machine. */
export const ERA_CAPABILITIES = Object.freeze({
  maker: Object.freeze({
    autonomousLocomotion: false,
    externalArticulation: true,
    mechanicalRoutine: false,
    visitorTracking: false,
    visitorResponse: false,
    cageTesting: false,
    predatoryBehavior: false,
    internalPower: false,
    inspectionAssemblies: Object.freeze(['support', 'pivots', 'control-linkages']),
  }),
  mechanic: Object.freeze({
    autonomousLocomotion: true,
    externalArticulation: false,
    mechanicalRoutine: true,
    visitorTracking: false,
    visitorResponse: false,
    cageTesting: false,
    predatoryBehavior: false,
    internalPower: true,
    inspectionAssemblies: Object.freeze(['winding-drive', 'transmission', 'joint-linkages']),
  }),
  builder: Object.freeze({
    autonomousLocomotion: true,
    externalArticulation: false,
    mechanicalRoutine: false,
    visitorTracking: true,
    visitorResponse: true,
    cageTesting: true,
    predatoryBehavior: true,
    internalPower: true,
    inspectionAssemblies: Object.freeze(['power-core', 'distribution', 'actuators', 'sensors', 'processing']),
  }),
});

const VALID_ERAS = new Set(Object.keys(ERA_CAPABILITIES));
const ARTICULATION_PARTS = Object.freeze(['leg', 'wing', 'tail', 'neck', 'jaw']);
const MAX_DELTA = 0.1;
const INSPECTION_SETTLE = 0.45;
const MECHANIC_DWELL = 0.8;
const MECHANIC_SPEED = 0.23;
const ENERGY_DRAIN_PER_SECOND = 1 / 75;
export const POWER_MOVE_DURATIONS = Object.freeze({ jump: 1.4, thrust: 1.1 });
export const POWER_MOVE_PHASES = Object.freeze({
  jump: Object.freeze({ loadEnd: 0.22, flightEnd: 0.64, landingEnd: 0.84, recoverEnd: 1 }),
  thrust: Object.freeze({ loadEnd: 0.25, driveEnd: 0.48, holdEnd: 0.58, recoverEnd: 1 }),
});
const MECHANIC_ROUTE = Object.freeze([
  Object.freeze({ x: 0.55, z: -0.25 }),
  Object.freeze({ x: 0.55, z: 0.32 }),
  Object.freeze({ x: -0.55, z: 0.32 }),
  Object.freeze({ x: -0.55, z: -0.25 }),
]);

const finite = value => typeof value === 'number' && Number.isFinite(value);
const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
const safeDelta = value => clamp(finite(value) ? value : 0, 0, MAX_DELTA);
const angleTo = (from, to) => Math.atan2(to.x - from.x, to.z - from.z);
const zeroArticulation = () => ({ leg: 0, wing: 0, tail: 0, neck: 0, jaw: 0 });
const frozenCopy = value => Object.freeze({ ...value });

/**
 * Wrap the Builder encounter with era-specific capabilities and controls.
 * Coordinates remain metres (Y up, forward +Z). `update(dt, feedback)` uses
 * seconds and renderer feedback for the prior frame. The Builder delegates
 * its encounter to createPresenceState; Maker is a stationary external puppet;
 * Mechanic runs a bounded, energy-limited traversal with no visitor tracking.
 */
export function createEraController({ seed = 927 } = {}) {
  const builder = createPresenceState({ seed });
  let era = 'builder';
  let paused = false;
  let reducedMotion = false;
  let inspection = false;
  let inspectionRequested = false;
  let elapsed = 0;
  let stateDuration = 0;
  let articulation = zeroArticulation();
  let routineRunning = false;
  let energy = 1;
  let goal = null;
  let heading = null;
  let lastPosition = { x: 0, z: -0.25 };
  let routeIndex = 0;
  let settleTo = 'mechanical-ready';
  let lastFeedbackSettled = true;
  let awaitingArrivalFeedback = false;
  let powerMovePending = null;
  let powerMove = null;
  let powerMoveInspectionPending = false;

  function canOperatePuppet() {
    return era === 'maker' && !paused && !inspection && !inspectionRequested;
  }

  function canStartRoutine() {
    return era === 'mechanic' && !paused && !inspection && !inspectionRequested
      && !reducedMotion && state === 'mechanical-ready' && energy > 0;
  }

  let state = 'watch';

  function builderSnapshot() {
    const base = builder.getSnapshot();
    const speeds = { pace: 0.9, approach: 1.1, boundary: 0.4 };
    const common = {
      ...base,
      era: 'builder',
      capabilities: ERA_CAPABILITIES.builder,
      speed: base.speed > 0 ? (speeds[base.state] ?? base.speed) : 0,
      energy: null,
      routineRunning: false,
      articulation: frozenCopy(zeroArticulation()),
      powerMove: null,
      powerMovePending: powerMovePending ? Object.freeze({ ...powerMovePending }) : null,
    };
    if (!powerMove) return Object.freeze(common);
    const stage = powerStage(powerMove.kind, powerMove.phase);
    return Object.freeze({
      ...common,
      state: `power-${powerMove.kind}`,
      phase: powerMove.phase,
      inspection: false,
      inspectionRequested: powerMoveInspectionPending,
      goal: null,
      heading: null,
      lookTarget: null,
      speed: 0,
      agitation: 0,
      visitorPresent: false,
      actionKind: null,
      canReach: false,
      powerMove: Object.freeze({ kind: powerMove.kind, phase: powerMove.phase, duration: powerMove.duration, stage }),
    });
  }

  function snapshot() {
    if (era === 'builder') return builderSnapshot();
    const maker = era === 'maker';
    const actualState = maker
      ? (inspection ? 'inspection' : inspectionRequested ? 'settle' : state)
      : (inspection ? 'inspection' : state);
    const activeGoal = maker || inspection || inspectionRequested ? null : goal;
    return Object.freeze({
      state: actualState,
      phase: actualState === 'inspection' ? 1 : stateDuration > 0 ? clamp(elapsed / stateDuration, 0, 1) : 0,
      reach: frozenCopy({ x: 0, y: 0 }),
      paused,
      inspection,
      reducedMotion,
      era,
      capabilities: ERA_CAPABILITIES[era],
      goal: activeGoal ? frozenCopy(activeGoal) : null,
      heading: maker ? null : Number.isFinite(heading) ? heading : null,
      lookTarget: null,
      speed: !maker && state === 'mechanical-run' && routineRunning && !paused && !reducedMotion ? MECHANIC_SPEED : 0,
      agitation: 0,
      visitorPresent: false,
      actionKind: null,
      inspectionRequested,
      canReach: era === 'builder' ? builder.getSnapshot().canReach : false,
      articulation: frozenCopy(articulation),
      routineRunning: !maker && routineRunning,
      energy: maker ? null : energy,
      powerMove: null,
      powerMovePending: null,
    });
  }

  function powerStage(kind, phase) {
    const marks = POWER_MOVE_PHASES[kind];
    if (phase < marks.loadEnd) return 'load';
    if (kind === 'jump' && phase < marks.flightEnd) return 'flight';
    if (kind === 'thrust' && phase < marks.driveEnd) return 'drive';
    if (kind === 'thrust' && phase < marks.holdEnd) return 'hold';
    if (phase < (kind === 'jump' ? marks.landingEnd : marks.recoverEnd)) return kind === 'jump' ? 'landing' : 'recover';
    return 'recover';
  }

  function setState(next, duration = 0, nextGoal = goal, nextHeading = heading, nextSettleTo = settleTo) {
    state = next;
    elapsed = 0;
    stateDuration = duration;
    goal = nextGoal ? { x: nextGoal.x, z: nextGoal.z } : null;
    heading = Number.isFinite(nextHeading) ? nextHeading : null;
    settleTo = nextSettleTo;
  }

  function mechanicSettle(destination, duration = INSPECTION_SETTLE) {
    awaitingArrivalFeedback = false;
    setState('mechanical-settle', duration, null, heading, destination);
  }

  function beginNextSegment() {
    routeIndex = (routeIndex + 1) % MECHANIC_ROUTE.length;
    const nextGoal = MECHANIC_ROUTE[routeIndex];
    heading = angleTo(lastPosition, nextGoal);
    awaitingArrivalFeedback = true;
    setState('mechanical-run', 0, nextGoal, heading);
  }

  function updateMaker(dt, feedback) {
    if (inspection) return snapshot();
    if (paused && !inspectionRequested) return snapshot();
    if (inspectionRequested) {
      elapsed += dt;
      if (elapsed >= stateDuration && feedback.settled === true) {
        inspection = true;
        state = 'puppet-rest';
        articulation = zeroArticulation();
        stateDuration = 0;
      }
    }
    return snapshot();
  }

  function updateMechanic(dt, feedback) {
    lastFeedbackSettled = feedback.settled === true;
    if (inspection) return snapshot();
    if (paused && !inspectionRequested) return snapshot();
    if (inspectionRequested) {
      elapsed += dt;
      if (state !== 'mechanical-settle') mechanicSettle('inspection');
      else if (elapsed >= stateDuration && feedback.settled === true) {
        inspection = true;
        routineRunning = false;
        energy = clamp(energy, 0, 1);
        setState('inspection', 0, null, heading);
      }
      return snapshot();
    }

    if (routineRunning) energy = Math.max(0, energy - dt * ENERGY_DRAIN_PER_SECOND);
    if (routineRunning && energy <= 0) {
      routineRunning = false;
      mechanicSettle('mechanical-empty');
      return snapshot();
    }

    if (state === 'mechanical-run') {
      if (awaitingArrivalFeedback) {
        awaitingArrivalFeedback = false;
      } else if (feedback.arrived === true && feedback.settled === true && feedback.aligned === true) {
        if (goal) lastPosition = { ...goal };
        setState('mechanical-settle', MECHANIC_DWELL, goal, heading, 'mechanical-ready');
      }
    } else if (state === 'mechanical-settle') {
      elapsed += dt;
      if (elapsed >= stateDuration && feedback.settled === true) {
        if (inspectionRequested) {
          inspection = true;
          routineRunning = false;
          setState('inspection', 0, null, heading);
        } else if (routineRunning && energy > 0) {
          beginNextSegment();
        } else {
          goal = null;
          state = energy > 0 ? 'mechanical-ready' : 'mechanical-empty';
          elapsed = 0;
          stateDuration = 0;
          settleTo = state;
        }
      }
    }
    return snapshot();
  }

  function update(dtSeconds, feedback = {}) {
    const dt = safeDelta(dtSeconds);
    const fb = feedback && typeof feedback === 'object' ? feedback : {};
    if (era === 'builder') {
      const base = builder.update(dt, fb);
      paused = base.paused;
      inspection = base.inspection;
      inspectionRequested = base.inspectionRequested;
      reducedMotion = base.reducedMotion;
      if (powerMove) {
        if (!paused || powerMoveInspectionPending) {
          powerMove.elapsed = Math.min(powerMove.duration, powerMove.elapsed + dt);
          powerMove.phase = clamp(powerMove.elapsed / powerMove.duration, 0, 1);
        }
        if (powerMove.phase >= 1 && fb.settled === true) {
          const remainForInspection = powerMoveInspectionPending;
          powerMove = null;
          powerMoveInspectionPending = false;
          if (!remainForInspection) {
            builder.setInspection(false);
            const resumed = builder.getSnapshot();
            inspection = resumed.inspection;
            inspectionRequested = resumed.inspectionRequested;
          }
        }
        return builderSnapshot();
      }
      if (powerMovePending && base.inspection && fb.settled === true && !paused && !reducedMotion) {
        const kind = powerMovePending.kind;
        powerMovePending = null;
        powerMove = { kind, duration: POWER_MOVE_DURATIONS[kind], elapsed: 0, phase: 0 };
        inspection = false;
        inspectionRequested = false;
        return builderSnapshot();
      }
      return builderSnapshot();
    }
    if (era === 'maker') return updateMaker(dt, fb);
    return updateMechanic(dt, fb);
  }

  function requestReach(input = {}) {
    if (era !== 'builder' || powerMove || powerMovePending) return false;
    return builder.requestReach(input);
  }

  function requestRetreat() {
    if (era !== 'builder' || powerMove || powerMovePending) return false;
    return builder.requestRetreat();
  }

  function setInspection(value) {
    const next = Boolean(value);
    if (era === 'builder') {
      if (powerMove) {
        powerMoveInspectionPending = next;
        inspectionRequested = next;
        return snapshot();
      }
      if (powerMovePending) {
        // An explicit inspection request during preparation cancels the
        // queued move. The already-requested Builder inspection continues
        // normally, so the UI can open once its grounded pose is ready.
        powerMovePending = null;
      }
      builder.setInspection(next);
      inspectionRequested = builder.getSnapshot().inspectionRequested;
      inspection = builder.getSnapshot().inspection;
      return snapshot();
    }
    if (next === inspectionRequested) return snapshot();
    inspectionRequested = next;
    if (next) {
      if (era === 'maker') {
        articulation = zeroArticulation();
        state = 'puppet-rest';
      } else {
        routineRunning = false;
        energy = clamp(energy, 0, 1);
        mechanicSettle('inspection');
      }
      elapsed = 0;
      stateDuration = INSPECTION_SETTLE;
    } else if (inspection) {
      inspection = false;
      if (era === 'maker') {
        state = 'puppet-rest';
        elapsed = 0;
        stateDuration = 0;
      } else {
        state = energy > 0 ? 'mechanical-ready' : 'mechanical-empty';
        elapsed = 0;
        stateDuration = 0;
        goal = null;
        routineRunning = false;
      }
      inspectionRequested = false;
    }
    return snapshot();
  }

  function setPaused(value) {
    paused = Boolean(value);
    if (era === 'builder') {
      if (paused && powerMovePending) {
        powerMovePending = null;
        builder.setInspection(false);
      }
      builder.setPaused(paused);
    }
    else return snapshot();
    return snapshot();
  }

  function setReducedMotion(value) {
    reducedMotion = Boolean(value);
    if (era === 'builder') {
      if (reducedMotion && powerMovePending) {
        powerMovePending = null;
        builder.setInspection(false);
      }
      builder.setReducedMotion(reducedMotion);
      return snapshot();
    }
    if (era === 'mechanic' && reducedMotion && routineRunning) {
      routineRunning = false;
      mechanicSettle(energy > 0 ? 'mechanical-ready' : 'mechanical-empty');
    }
    return snapshot();
  }

  function setEra(nextEra) {
    if (!VALID_ERAS.has(nextEra)) return false;
    if (era === nextEra) return true;
    era = nextEra;
    inspection = false;
    inspectionRequested = false;
    elapsed = 0;
    articulation = zeroArticulation();
    routineRunning = false;
    powerMove = null;
    powerMovePending = null;
    powerMoveInspectionPending = false;
    awaitingArrivalFeedback = false;
    energy = 1;
    goal = null;
    heading = null;
    lastPosition = { x: 0, z: -0.25 };
    routeIndex = 0;
    settleTo = 'mechanical-ready';
    awaitingArrivalFeedback = false;
    stateDuration = 0;
    if (nextEra === 'builder') {
      builder.setInspection(false);
      builder.reset();
      builder.setEra('builder');
      builder.setPaused(paused);
      builder.setReducedMotion(reducedMotion);
    } else if (nextEra === 'maker') {
      state = 'puppet-rest';
    } else {
      state = 'mechanical-ready';
    }
    return true;
  }

  function reset() {
    articulation = zeroArticulation();
    routineRunning = false;
    powerMove = null;
    powerMovePending = null;
    powerMoveInspectionPending = false;
    energy = 1;
    goal = null;
    heading = null;
    lastPosition = { x: 0, z: -0.25 };
    routeIndex = 0;
    inspection = false;
    inspectionRequested = false;
    elapsed = 0;
    stateDuration = 0;
    settleTo = 'mechanical-ready';
    awaitingArrivalFeedback = false;
    if (era === 'builder') {
      builder.setInspection(false);
      builder.reset();
      builder.setEra('builder');
      builder.setPaused(paused);
      builder.setReducedMotion(reducedMotion);
    } else if (era === 'maker') {
      state = 'puppet-rest';
    } else {
      state = 'mechanical-ready';
    }
    return snapshot();
  }

  function setArticulation(id, value) {
    if (!ARTICULATION_PARTS.includes(id) || !canOperatePuppet() || !finite(value)) return false;
    articulation = { ...articulation, [id]: clamp(value, 0, 1) };
    state = Object.values(articulation).some(amount => amount > 0) ? 'puppet-articulation' : 'puppet-rest';
    elapsed = 0;
    stateDuration = 0;
    return true;
  }

  function requestRoutine() {
    if (!canStartRoutine()) return false;
    routineRunning = true;
    if (energy <= 0) energy = 1;
    routeIndex = 0;
    goal = { ...MECHANIC_ROUTE[routeIndex] };
    heading = angleTo(lastPosition, goal);
    awaitingArrivalFeedback = true;
    setState('mechanical-run', 0, goal, heading);
    return true;
  }

  function requestPowerMove(kind) {
    if (era !== 'builder' || !Object.hasOwn(POWER_MOVE_DURATIONS, kind) || powerMove || powerMovePending) return false;
    const base = builder.getSnapshot();
    if (paused || reducedMotion || base.paused || base.reducedMotion || base.inspection || base.inspectionRequested
        || base.visitorPresent || !base.canReach) return false;
    powerMovePending = { kind };
    powerMoveInspectionPending = false;
    builder.setInspection(true);
    const pending = builder.getSnapshot();
    inspection = pending.inspection;
    inspectionRequested = pending.inspectionRequested;
    return true;
  }

  function stopRoutine() {
    if (era !== 'mechanic' || !routineRunning) return false;
    routineRunning = false;
    awaitingArrivalFeedback = false;
    mechanicSettle(energy > 0 ? 'mechanical-ready' : 'mechanical-empty');
    return true;
  }

  function wind() {
    if (era !== 'mechanic' || paused || inspection || inspectionRequested || reducedMotion
        || routineRunning || state === 'mechanical-settle' || !lastFeedbackSettled) return false;
    energy = 1;
    if (state === 'mechanical-empty') state = 'mechanical-ready';
    return true;
  }

  state = 'watch';
  builder.setEra('builder');

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
    setArticulation,
    requestRoutine,
    stopRoutine,
    wind,
    requestPowerMove,
  });
}
