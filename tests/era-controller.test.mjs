import test from 'node:test';
import assert from 'node:assert/strict';
import {
  createEraController,
  ERA_CAPABILITIES,
  POWER_MOVE_DURATIONS,
  POWER_MOVE_PHASES,
} from '../src/scene/era-controller.js';

const READY = Object.freeze({ arrived: true, settled: true, aligned: true });
const MOVING = Object.freeze({ arrived: false, settled: false, aligned: false });

function advance(controller, seconds, feedback = READY, dt = 0.1) {
  let snapshot = controller.getSnapshot();
  const frames = Math.ceil(seconds / dt);
  for (let i = 0; i < frames; i += 1) snapshot = controller.update(Math.min(dt, seconds - i * dt), feedback);
  return snapshot;
}

function advanceUntil(controller, predicate, { limit = 200, feedback = READY } = {}) {
  for (let i = 0; i < limit; i += 1) {
    const snapshot = controller.update(0.1, feedback);
    if (predicate(snapshot)) return snapshot;
  }
  assert.fail(`expected state not reached: ${controller.getSnapshot().state}`);
}

test('capability table gives each era a distinct and immutable movement/control model', () => {
  assert.equal(ERA_CAPABILITIES.maker.autonomousLocomotion, false);
  assert.equal(ERA_CAPABILITIES.maker.externalArticulation, true);
  assert.equal(ERA_CAPABILITIES.maker.internalPower, false);
  assert.equal(ERA_CAPABILITIES.mechanic.autonomousLocomotion, true);
  assert.equal(ERA_CAPABILITIES.mechanic.mechanicalRoutine, true);
  assert.equal(ERA_CAPABILITIES.mechanic.visitorTracking, false);
  assert.equal(ERA_CAPABILITIES.mechanic.predatoryBehavior, false);
  assert.equal(ERA_CAPABILITIES.builder.visitorTracking, true);
  assert.equal(ERA_CAPABILITIES.builder.predatoryBehavior, true);
  assert.notDeepEqual(ERA_CAPABILITIES.maker.inspectionAssemblies, ERA_CAPABILITIES.mechanic.inspectionAssemblies);
  assert.notDeepEqual(ERA_CAPABILITIES.mechanic.inspectionAssemblies, ERA_CAPABILITIES.builder.inspectionAssemblies);
  assert.ok(Object.isFrozen(ERA_CAPABILITIES.builder.inspectionAssemblies));
});

test('Maker stays anchored and still until an explicit articulation control moves', () => {
  const controller = createEraController();
  controller.setEra('maker');
  const rest = controller.getSnapshot();
  assert.equal(rest.state, 'puppet-rest');
  assert.equal(rest.goal, null);
  assert.equal(rest.speed, 0);
  assert.equal(rest.lookTarget, null);
  assert.equal(rest.energy, null);
  assert.equal(rest.canReach, false);
  assert.equal(controller.requestReach({ x: 1 }), false);
  assert.equal(controller.requestRetreat(), false);
  advance(controller, 30);
  assert.equal(controller.getSnapshot().state, 'puppet-rest');
  assert.equal(controller.getSnapshot().goal, null);

  assert.equal(controller.setArticulation('leg', 0.8), true);
  assert.equal(controller.getSnapshot().state, 'puppet-articulation');
  assert.deepEqual(controller.getSnapshot().articulation, { leg: 0.8, wing: 0, tail: 0, neck: 0, jaw: 0 });
  assert.equal(controller.setArticulation('wing', 4), true);
  assert.equal(controller.getSnapshot().articulation.wing, 1);
  assert.equal(controller.setArticulation('leg', 0), true);
  assert.equal(controller.getSnapshot().state, 'puppet-articulation');
  assert.equal(controller.setArticulation('wing', 0), true);
  assert.equal(controller.getSnapshot().state, 'puppet-rest');
  assert.equal(controller.setArticulation('head', 0.5), false);
  assert.equal(controller.setArticulation('jaw', NaN), false);
  assert.equal(controller.getSnapshot().speed, 0);
  assert.equal(controller.getSnapshot().goal, null);
});

test('Maker manual controls respect pause and inspection, and inspection waits for a grounded pose', () => {
  const controller = createEraController();
  controller.setEra('maker');
  controller.setPaused(true);
  assert.equal(controller.setArticulation('neck', 0.5), false);
  controller.setPaused(false);
  controller.setArticulation('leg', 0.9);
  controller.setInspection(true);
  const requested = controller.getSnapshot();
  assert.equal(requested.state, 'settle');
  assert.equal(requested.inspectionRequested, true);
  assert.equal(requested.articulation.leg, 0, 'inspection returns the puppet to its supported rest pose');
  advance(controller, 0.8, { settled: false });
  assert.equal(controller.getSnapshot().inspection, false);
  advanceUntil(controller, s => s.inspection, { feedback: { settled: true } });
  assert.equal(controller.getSnapshot().state, 'inspection');
  assert.equal(controller.setArticulation('jaw', 0.4), false);
  controller.setInspection(false);
  assert.equal(controller.getSnapshot().state, 'puppet-rest');
  assert.equal(controller.getSnapshot().inspectionRequested, false);
});

test('Mechanic performs a bounded, non-predatory route and uses no visitor reach interface', () => {
  const controller = createEraController({ seed: 42 });
  controller.setEra('mechanic');
  const ready = controller.getSnapshot();
  assert.equal(ready.state, 'mechanical-ready');
  assert.equal(ready.energy, 1);
  assert.equal(ready.lookTarget, null);
  assert.equal(ready.actionKind, null);
  assert.equal(ready.canReach, false);
  assert.equal(controller.requestReach({ x: 0 }), false);
  assert.equal(controller.requestRetreat(), false);
  assert.equal(controller.requestRoutine(), true);
  assert.equal(controller.requestRoutine(), false, 'routine cannot stack');
  assert.equal(controller.getSnapshot().state, 'mechanical-run');
  assert.equal(controller.getSnapshot().routineRunning, true);
  assert.ok(controller.getSnapshot().goal.x >= -0.55 && controller.getSnapshot().goal.x <= 0.55);
  assert.ok(controller.getSnapshot().goal.z >= -0.25 && controller.getSnapshot().goal.z <= 0.32);
  assert.ok(Number.isFinite(controller.getSnapshot().heading));

  const firstGoal = controller.getSnapshot().goal;
  controller.update(0.1, READY);
  assert.equal(controller.getSnapshot().state, 'mechanical-run', 'stale idle feedback must not finish a new goal');
  assert.deepEqual(controller.getSnapshot().goal, firstGoal);
  const startingEnergy = controller.getSnapshot().energy;
  controller.update(0.1, MOVING);
  assert.ok(controller.getSnapshot().energy < startingEnergy);
  advanceUntil(controller, s => s.state === 'mechanical-settle');
  assert.equal(controller.getSnapshot().routineRunning, true);
  const settledGoal = controller.getSnapshot().goal;
  advanceUntil(controller, s => s.state === 'mechanical-run', { limit: 20 });
  assert.notDeepEqual(controller.getSnapshot().goal, settledGoal);
  assert.ok(controller.getSnapshot().goal.x >= -0.55 && controller.getSnapshot().goal.x <= 0.55);
  assert.ok(controller.getSnapshot().goal.z >= -0.25 && controller.getSnapshot().goal.z <= 0.32);
});

test('Mechanic energy drains only during the routine, remains paused in pause/stop, then empties safely', () => {
  const controller = createEraController();
  controller.setEra('mechanic');
  advance(controller, 10);
  assert.equal(controller.getSnapshot().energy, 1);
  controller.requestRoutine();
  controller.update(0.1, MOVING);
  const energyAfterStart = controller.getSnapshot().energy;
  controller.setPaused(true);
  advance(controller, 2, READY);
  assert.equal(controller.getSnapshot().energy, energyAfterStart);
  controller.setPaused(false);
  assert.equal(controller.stopRoutine(), true);
  const stoppedEnergy = controller.getSnapshot().energy;
  advanceUntil(controller, s => s.state === 'mechanical-ready', { feedback: READY });
  advance(controller, 2);
  assert.equal(controller.getSnapshot().energy, stoppedEnergy);
  assert.equal(controller.requestRoutine(), true);
  advance(controller, 75, MOVING);
  assert.equal(controller.getSnapshot().energy, 0);
  assert.equal(controller.getSnapshot().routineRunning, false);
  assert.equal(controller.getSnapshot().goal, null);
  advanceUntil(controller, s => s.state === 'mechanical-empty', { feedback: READY });
  assert.equal(controller.requestRoutine(), false);
  assert.equal(controller.wind(), true);
  assert.equal(controller.getSnapshot().energy, 1);
  assert.equal(controller.getSnapshot().state, 'mechanical-ready');
});

test('Mechanic inspection, reduced motion, and pause cancel movement before interaction resumes', () => {
  const controller = createEraController();
  controller.setEra('mechanic');
  controller.requestRoutine();
  controller.update(0.1, MOVING);
  const energy = controller.getSnapshot().energy;
  controller.setReducedMotion(true);
  assert.equal(controller.getSnapshot().routineRunning, false);
  assert.equal(controller.getSnapshot().goal, null);
  assert.equal(controller.getSnapshot().speed, 0);
  advanceUntil(controller, s => s.state === 'mechanical-ready', { feedback: READY });
  assert.equal(controller.getSnapshot().energy, energy);
  assert.equal(controller.requestRoutine(), false);
  assert.equal(controller.wind(), false);

  controller.setReducedMotion(false);
  controller.requestRoutine();
  controller.update(0.1, MOVING);
  controller.setPaused(true);
  controller.setInspection(true);
  assert.equal(controller.getSnapshot().inspectionRequested, true);
  assert.equal(controller.getSnapshot().routineRunning, false);
  assert.equal(controller.getSnapshot().goal, null);
  advanceUntil(controller, s => s.inspection, { feedback: { settled: true } });
  assert.equal(controller.getSnapshot().paused, true);
  assert.equal(controller.getSnapshot().state, 'inspection');
  assert.equal(controller.requestRoutine(), false);
  controller.setInspection(false);
  assert.equal(controller.getSnapshot().state, 'mechanical-ready');
  assert.equal(controller.getSnapshot().paused, true);
  assert.equal(controller.getSnapshot().routineRunning, false);
});

test('era changes clear incompatible behavior while preserving pause and reduced-motion preferences', () => {
  const controller = createEraController({ seed: 77 });
  controller.setPaused(true);
  controller.setReducedMotion(true);
  controller.setInspection(true);
  advanceUntil(controller, s => s.inspection, { feedback: READY });
  assert.equal(controller.setEra('maker'), true);
  assert.equal(controller.getSnapshot().state, 'puppet-rest');
  assert.equal(controller.getSnapshot().paused, true);
  assert.equal(controller.getSnapshot().reducedMotion, true);
  assert.equal(controller.getSnapshot().inspection, false);
  assert.equal(controller.getSnapshot().inspectionRequested, false);
  assert.equal(controller.setArticulation('tail', 0.7), false, 'pause remains active after era switch');

  controller.setPaused(false);
  controller.setArticulation('tail', 0.7);
  controller.setEra('mechanic');
  assert.equal(controller.getSnapshot().state, 'mechanical-ready');
  assert.deepEqual(controller.getSnapshot().articulation, { leg: 0, wing: 0, tail: 0, neck: 0, jaw: 0 });
  assert.equal(controller.getSnapshot().routineRunning, false);
  assert.equal(controller.getSnapshot().energy, 1);
  assert.equal(controller.getSnapshot().reducedMotion, true);
  assert.equal(controller.requestRoutine(), false, 'mechanic route remains disabled under reduced motion');

  controller.setReducedMotion(false);
  controller.requestRoutine();
  controller.setEra('builder');
  assert.equal(controller.getSnapshot().state, 'watch');
  assert.equal(controller.getSnapshot().goal, null);
  assert.equal(controller.getSnapshot().routineRunning, false);
  assert.equal(controller.getSnapshot().energy, null);
  assert.equal(controller.getSnapshot().inspection, false, 'old Builder inspection must not return on era switch');
  assert.equal(controller.getSnapshot().reducedMotion, false);
  assert.equal(controller.requestReach({ x: 0.5 }), true);
  controller.reset();
  assert.equal(controller.getSnapshot().state, 'watch');
  assert.equal(controller.getSnapshot().visitorPresent, false);
  assert.equal(controller.getSnapshot().goal, null);
});

test('Builder delegates autonomous timing, reach behavior, and preserves zero speed while paused', () => {
  const controller = createEraController({ seed: 42 });
  const seen = new Set();
  for (let i = 0; i < 400; i += 1) seen.add(controller.update(0.1, READY).state);
  assert.ok(seen.has('pace') || seen.has('boundary'), 'Builder wrapper failed to advance the underlying state machine');
  const moving = createEraController({ seed: 42 });
  advanceUntil(moving, s => s.state === 'pace', { limit: 60 });
  assert.equal(moving.getSnapshot().speed, 0.9);
  moving.setPaused(true);
  assert.equal(moving.getSnapshot().speed, 0);

  const s = controller.getSnapshot();
  assert.equal(s.era, 'builder');
  assert.equal(s.energy, null);
  assert.equal(s.routineRunning, false);
  const visitor = createEraController({ seed: 42 });
  assert.equal(visitor.requestReach({ x: -0.8 }), true);
  assert.equal(visitor.getSnapshot().state, 'notice');
  assert.equal(visitor.getSnapshot().speed, 0);
});

test('reset clears controls, inspection and routines but preserves user pause/motion settings', () => {
  const controller = createEraController();
  controller.setEra('maker');
  controller.setPaused(true);
  controller.setReducedMotion(true);
  controller.setArticulation('wing', 1);
  controller.reset();
  assert.equal(controller.getSnapshot().state, 'puppet-rest');
  assert.deepEqual(controller.getSnapshot().articulation, { leg: 0, wing: 0, tail: 0, neck: 0, jaw: 0 });
  assert.equal(controller.getSnapshot().paused, true);
  assert.equal(controller.getSnapshot().reducedMotion, true);

  controller.setEra('mechanic');
  controller.setPaused(false);
  controller.setReducedMotion(false);
  controller.requestRoutine();
  controller.reset();
  assert.equal(controller.getSnapshot().state, 'mechanical-ready');
  assert.equal(controller.getSnapshot().routineRunning, false);
  assert.equal(controller.getSnapshot().energy, 1);
});

function builderCanReach(controller) {
  if (controller.getSnapshot().canReach) return controller.getSnapshot();
  return advanceUntil(controller, s => s.canReach, { limit: 180, feedback: READY });
}

function startPowerMove(controller, kind = 'jump') {
  builderCanReach(controller);
  assert.equal(controller.requestPowerMove(kind), true);
  assert.deepEqual(controller.getSnapshot().powerMovePending, { kind });
  assert.equal(controller.getSnapshot().powerMove, null);
  return advanceUntil(controller, s => s.powerMove?.kind === kind, { limit: 20, feedback: READY });
}

test('Advanced power moves are gated, ground through inspection, then expose bounded phase snapshots', () => {
  const controller = createEraController({ seed: 42 });
  assert.equal(controller.requestPowerMove('jump'), true);
  const pending = controller.getSnapshot();
  assert.equal(pending.state, 'settle');
  assert.equal(pending.inspection, false);
  assert.equal(pending.inspectionRequested, true);
  assert.deepEqual(pending.powerMovePending, { kind: 'jump' });
  assert.equal(pending.goal, null);
  assert.equal(controller.requestPowerMove('jump'), false, 'a queued move cannot stack');
  assert.equal(controller.requestPowerMove('thrust'), false, 'a different move cannot stack');

  const active = advanceUntil(controller, s => s.powerMove?.kind === 'jump', { limit: 20, feedback: READY });
  assert.equal(active.state, 'power-jump');
  assert.equal(active.inspection, false);
  assert.equal(active.inspectionRequested, false);
  assert.equal(active.powerMove.phase, 0);
  assert.equal(active.powerMove.duration, POWER_MOVE_DURATIONS.jump);
  assert.equal(active.powerMove.stage, 'load');
  assert.equal(active.goal, null);
  assert.equal(active.speed, 0);
  assert.equal(active.canReach, false);
  assert.equal(active.visitorPresent, false);
  assert.equal(active.actionKind, null);

  const advancing = controller.update(0.31, { settled: false });
  assert.ok(advancing.powerMove.phase > 0 && advancing.powerMove.phase < 0.1,
    'large frame deltas are bounded to the controller maximum');
  const flight = advance(controller, 0.4, { settled: false });
  assert.equal(flight.powerMove.stage, 'flight');
  assert.ok(flight.powerMove.phase > POWER_MOVE_PHASES.jump.loadEnd);
  assert.equal(controller.requestPowerMove('thrust'), false, 'an active move cannot be interrupted or stacked');
  assert.ok(Object.isFrozen(POWER_MOVE_DURATIONS));
  assert.ok(Object.isFrozen(POWER_MOVE_PHASES.jump));
});

test('power move availability is Advanced-only and respects pause, reduced motion, and inspection', () => {
  const controller = createEraController();
  assert.equal(controller.requestPowerMove('jump'), true, 'Builder can queue from a reachable state');
  controller.setInspection(true);
  assert.equal(controller.getSnapshot().powerMovePending, null, 'explicit inspection cancels preparation');
  assert.equal(controller.getSnapshot().inspectionRequested, true);
  assert.equal(controller.requestPowerMove('thrust'), false);
  advanceUntil(controller, s => s.inspection, { feedback: READY });
  controller.setInspection(false);

  controller.setPaused(true);
  assert.equal(controller.requestPowerMove('jump'), false);
  controller.setPaused(false);
  controller.setReducedMotion(true);
  assert.equal(controller.requestPowerMove('jump'), false);
  controller.setReducedMotion(false);

  controller.setEra('maker');
  assert.equal(controller.requestPowerMove('jump'), false);
  controller.setEra('mechanic');
  assert.equal(controller.requestPowerMove('thrust'), false);
  controller.setEra('builder');
  controller.requestReach({ x: 0 });
  assert.equal(controller.requestPowerMove('jump'), false, 'visitor response in progress is not reachable');
});

test('power move pause freezes phase; inspection and reduced motion allow a safe finish', () => {
  const controller = createEraController();
  const active = startPowerMove(controller, 'thrust');
  assert.equal(active.powerMove.duration, POWER_MOVE_DURATIONS.thrust);
  assert.equal(active.powerMove.stage, 'load');
  controller.update(0.2, READY);
  const phaseBeforePause = controller.getSnapshot().powerMove.phase;
  controller.setPaused(true);
  advance(controller, 0.5, READY);
  assert.equal(controller.getSnapshot().powerMove.phase, phaseBeforePause);

  controller.setReducedMotion(true);
  controller.setInspection(true);
  assert.equal(controller.getSnapshot().inspectionRequested, true);
  advanceUntil(controller, s => s.inspection && !s.powerMove, { limit: 30, feedback: READY });
  assert.equal(controller.getSnapshot().paused, true);
  assert.equal(controller.getSnapshot().reducedMotion, true);
  assert.equal(controller.getSnapshot().inspectionRequested, true);
  assert.equal(controller.getSnapshot().powerMove, null);
  assert.equal(controller.getSnapshot().state, 'inspection');
});

test('power moves finish their phase before resuming Builder, while era change/reset clears them immediately', () => {
  const controller = createEraController();
  startPowerMove(controller, 'jump');
  advance(controller, 1.5, { settled: true });
  assert.equal(controller.getSnapshot().powerMove, null);
  assert.equal(controller.getSnapshot().inspection, false);
  assert.equal(controller.getSnapshot().inspectionRequested, false);

  startPowerMove(controller, 'thrust');
  controller.setEra('maker');
  assert.equal(controller.getSnapshot().powerMove, null);
  assert.equal(controller.getSnapshot().powerMovePending, null);
  assert.equal(controller.getSnapshot().inspection, false);
  assert.equal(controller.getSnapshot().state, 'puppet-rest');

  controller.setEra('builder');
  startPowerMove(controller, 'jump');
  controller.reset();
  assert.equal(controller.getSnapshot().powerMove, null);
  assert.equal(controller.getSnapshot().powerMovePending, null);
  assert.equal(controller.getSnapshot().state, 'watch');

  assert.equal(controller.requestPowerMove('thrust'), true);
  assert.deepEqual(controller.getSnapshot().powerMovePending, { kind: 'thrust' });
  controller.setEra('mechanic');
  assert.equal(controller.getSnapshot().powerMovePending, null);
  assert.equal(controller.getSnapshot().powerMove, null);
  assert.equal(controller.getSnapshot().state, 'mechanical-ready');
});
