import assert from 'node:assert/strict';
import test from 'node:test';
import { createEncounterState, ENCOUNTER_DURATIONS } from '../src/scene/encounter-state.js';

const normalSequence = ['notice', 'warning', 'strike', 'contact', 'recover', 'cooldown', 'idle'];

function advance(state, seconds, step = 0.05) {
  let remaining = seconds;
  let snapshot = state.getSnapshot();
  while (remaining > 0) {
    const dt = Math.min(step, remaining);
    snapshot = state.update(dt);
    remaining -= dt;
  }
  return snapshot;
}

test('follows the complete response and returns to idle after cooldown', () => {
  const state = createEncounterState();
  const seen = [state.getSnapshot().state];

  assert.equal(state.requestReach({ x: 0.25, y: -0.5 }), true);
  seen.push(state.getSnapshot().state);
  for (const phase of normalSequence.slice(1)) {
    const duration = ENCOUNTER_DURATIONS[seen.at(-1)] + (phase === 'idle' ? 0.01 : 0);
    advance(state, duration);
    seen.push(state.getSnapshot().state);
  }

  assert.deepEqual(seen, ['idle', ...normalSequence]);
  assert.deepEqual(state.getSnapshot().reach, { x: 0, y: 0 });
  assert.equal(state.getSnapshot().phase, 0);
});

test('rejects a second reach until cooldown completes', () => {
  const state = createEncounterState();
  assert.equal(state.requestReach(), true);
  assert.equal(state.requestReach({ x: 1 }), false);
  advance(state, 2.9);
  assert.equal(state.getSnapshot().state, 'cooldown');
  assert.equal(state.requestReach(), false);
  advance(state, 1.1);
  assert.equal(state.requestReach(), true);
});

test('cancels cleanly when inspection begins and does not resume stale motion', () => {
  const state = createEncounterState();
  state.requestReach({ x: 0.8, y: -0.4 });
  advance(state, 0.25);
  state.setInspection(true);
  assert.deepEqual(state.getSnapshot(), {
    state: 'idle', phase: 0, reach: { x: 0, y: 0 }, paused: false,
    inspection: true, reducedMotion: false, era: 'maker',
  });
  advance(state, 3);
  assert.equal(state.getSnapshot().state, 'idle');
  assert.equal(state.requestReach(), false);
  state.setInspection(false);
  assert.equal(state.requestReach(), true);
});

test('pause cancels immediately and requires a new deliberate reach after resume', () => {
  const state = createEncounterState();
  state.requestReach({ x: -1, y: 0.6 });
  advance(state, 0.4);
  state.setPaused(true);
  assert.equal(state.getSnapshot().state, 'idle');
  assert.deepEqual(state.getSnapshot().reach, { x: 0, y: 0 });
  assert.equal(state.requestReach(), false);
  advance(state, 5);
  state.setPaused(false);
  assert.equal(state.getSnapshot().state, 'idle');
  assert.equal(state.requestReach(), true);
});

test('era switch cancels response and invalid era is ignored', () => {
  const state = createEncounterState();
  state.requestReach({ x: 1, y: 1 });
  advance(state, 1.1);
  assert.equal(state.setEra('mechanic'), true);
  assert.equal(state.getSnapshot().era, 'mechanic');
  assert.equal(state.getSnapshot().state, 'idle');
  assert.deepEqual(state.getSnapshot().reach, { x: 0, y: 0 });
  assert.equal(state.setEra('unknown'), false);
  assert.equal(state.getSnapshot().era, 'mechanic');
});

test('reduced motion uses finite notice, warning, recovery, and cooldown only', () => {
  const state = createEncounterState();
  state.setReducedMotion(true);
  state.requestReach();
  const seen = new Set([state.getSnapshot().state]);
  const final = advance(state, 3.5);
  assert.equal(final.state, 'idle');
  for (const phase of seen) assert.ok(['notice', 'warning', 'recover', 'cooldown'].includes(phase));
  assert.deepEqual(final.reach, { x: 0, y: 0 });
  assert.equal(state.requestReach(), true);
});

test('sanitizes coordinates and returns immutable, independent snapshots', () => {
  const state = createEncounterState();
  assert.equal(state.requestReach({ x: 4, y: Number.NaN }), true);
  const snapshot = state.getSnapshot();
  assert.deepEqual(snapshot.reach, { x: 1, y: 0 });
  assert.equal(Object.isFrozen(snapshot), true);
  assert.equal(Object.isFrozen(snapshot.reach), true);
  assert.throws(() => { snapshot.reach.x = 0; }, TypeError);
  assert.deepEqual(state.getSnapshot().reach, { x: 1, y: 0 });
  state.reset();
  assert.equal(state.requestReach(null), true);
  assert.deepEqual(state.getSnapshot().reach, { x: 0, y: 0 });
});

test('clamps large and invalid frame deltas without skipping phases', () => {
  const state = createEncounterState();
  state.requestReach();
  assert.equal(state.update(50).state, 'notice');
  assert.equal(state.getSnapshot().phase, 0.125);
  assert.equal(state.update(Infinity).state, 'notice');
  assert.equal(state.update(-3).state, 'notice');
  assert.ok(Number.isFinite(state.update(1e9).phase));
  assert.equal(state.getSnapshot().state, 'notice');
});

test('onChange receives frozen snapshots when observable values change', () => {
  const changes = [];
  const state = createEncounterState({ onChange: snapshot => changes.push(snapshot) });
  state.requestReach({ x: 0.2 });
  state.update(0.1);
  assert.ok(changes.length >= 2);
  assert.ok(changes.every(snapshot => Object.isFrozen(snapshot) && Object.isFrozen(snapshot.reach)));
});

test('idle inspection, pause, and reduced-motion toggles each notify once', () => {
  const changes = [];
  const state = createEncounterState({ onChange: snapshot => changes.push(snapshot) });

  state.setInspection(true);
  assert.equal(changes.length, 1);
  assert.equal(changes[0].inspection, true);
  state.setInspection(false);
  assert.equal(changes.length, 2);
  assert.equal(changes[1].inspection, false);

  state.setPaused(true);
  assert.equal(changes.length, 3);
  assert.equal(changes[2].paused, true);
  state.setPaused(false);
  assert.equal(changes.length, 4);
  assert.equal(changes[3].paused, false);

  state.setReducedMotion(true);
  assert.equal(changes.length, 5);
  assert.equal(changes[4].reducedMotion, true);
});

test('inspection and pause changes during a reaction emit only one cancellation snapshot', () => {
  for (const setter of ['setInspection', 'setPaused']) {
    const changes = [];
    const state = createEncounterState({ onChange: snapshot => changes.push(snapshot) });
    state.requestReach({ x: 0.4, y: -0.2 });
    changes.length = 0;

    state[setter](true);

    assert.equal(changes.length, 1);
    assert.equal(changes[0].state, 'idle');
    assert.deepEqual(changes[0].reach, { x: 0, y: 0 });
    assert.equal(changes[0][setter === 'setInspection' ? 'inspection' : 'paused'], true);
  }
});

test('enabling reduced motion during a reaction cancels once before calmer requests', () => {
  const changes = [];
  const state = createEncounterState({ onChange: snapshot => changes.push(snapshot) });
  state.requestReach();
  changes.length = 0;

  state.setReducedMotion(true);

  assert.equal(changes.length, 1);
  assert.equal(changes[0].state, 'idle');
  assert.equal(changes[0].reducedMotion, true);
  state.requestReach();
  const observed = new Set();
  for (let index = 0; index < 50 && state.getSnapshot().state !== 'idle'; index++) {
    observed.add(state.update(0.1).state);
  }
  assert.deepEqual([...observed].sort(), ['cooldown', 'idle', 'notice', 'recover', 'warning']);
});
