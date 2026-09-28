import test from 'node:test';
import assert from 'node:assert/strict';
import { CAGE_TEST_PHASE, PRESENCE_DURATIONS, createPresenceState } from '../src/scene/presence-state.js';

const READY = Object.freeze({ arrived: true, settled: true, aligned: true });

function stepUntil(machine, predicate, { limit = 2000, feedback = READY } = {}) {
  for (let i = 0; i < limit; i += 1) {
    const snapshot = machine.update(0.1, feedback);
    if (predicate(snapshot)) return snapshot;
  }
  assert.fail(`state did not reach expected condition; last state: ${machine.getSnapshot().state}`);
}

function assertFiniteSnapshot(snapshot) {
  const visit = value => {
    if (typeof value === 'number') assert.ok(Number.isFinite(value));
    else if (value && typeof value === 'object') Object.values(value).forEach(visit);
  };
  visit(snapshot);
}

test('autonomous Builder cycle reaches pacing, a rail contact, cage press, and recovery without input', () => {
  const machine = createPresenceState({ seed: 42 });
  const seen = new Set([machine.getSnapshot().state]);
  for (let i = 0; i < 600; i += 1) {
    const state = machine.update(0.1, READY);
    seen.add(state.state);
    if (seen.has('cage-test') && seen.has('recover') && seen.has('settle')) break;
  }
  assert.ok(seen.has('pace'));
  assert.ok(seen.has('boundary'));
  assert.ok(seen.has('cage-test'));
  assert.ok(seen.has('recover'));
  assert.ok(seen.has('settle'));
  assert.equal(PRESENCE_DURATIONS.cageTest, 2.4);
  assert.deepEqual(CAGE_TEST_PHASE, { buildEnd: 0.32, holdEnd: 0.75, releaseEnd: 1 });
});

test('autonomous plans vary route, attention, family, intensity, and recovery with seeded cooldowns', () => {
  const trace = seed => {
    const machine = createPresenceState({ seed });
    const beats = [];
    let lastState = machine.getSnapshot().state;
    for (let i = 0; i < 1200; i += 1) {
      const state = machine.update(0.1, READY);
      if (state.state === 'pace' && lastState !== 'pace') {
        beats.push({
          id: state.beatId,
          intention: state.intention,
          route: state.routeKind,
          family: state.actionFamily,
          intensity: state.intensity,
          recovery: state.recoveryStyle,
          goal: state.goal,
          look: state.lookTarget,
        });
      }
      lastState = state.state;
    }
    return beats;
  };

  const first = trace(20260927);
  assert.deepEqual(first, trace(20260927), 'same seed must reproduce the same authored beat sequence');
  assert.ok(first.length >= 7, 'two simulated minutes should contain several complete encounter plans');
  assert.ok(new Set(first.map(beat => beat.id)).size >= 5);
  assert.ok(new Set(first.map(beat => beat.route)).size >= 4);
  assert.ok(new Set(first.map(beat => beat.family)).size >= 3);
  assert.ok(new Set(first.map(beat => `${beat.goal.x},${beat.goal.z}`)).size >= 5);
  assert.ok(new Set(first.map(beat => `${beat.look.x},${beat.look.y},${beat.look.z}`)).size >= 4);
  assert.ok(new Set(first.map(beat => beat.intention)).size >= 5);
  assert.ok(new Set(first.map(beat => beat.recovery)).size >= 2);
  assert.ok(first.every(beat => beat.intensity > 0 && beat.intensity <= 1));
  for (let index = 1; index < first.length; index += 1) {
    assert.notEqual(first[index].id, first[index - 1].id, 'the next route must not repeat the last plan');
    assert.notEqual(first[index].family, first[index - 1].family, 'the next plan must switch action family');
  }
});

test('family weighting avoids the old three-family cycle and autonomously runs a settled floor scrape', () => {
  const traces = [927, 20260928, 42, 20260927, 1].map(seed => {
    const machine = createPresenceState({ seed });
    const families = [];
    const clawStages = new Set();
    let previousState = machine.getSnapshot().state;
    let firstClaw = null;
    for (let i = 0; i < 2400; i += 1) {
      const prior = machine.getSnapshot();
      const state = machine.update(0.1, { ...READY, clawContact: prior.clawAction?.stage === 'contact' });
      if (state.state === 'pace' && previousState !== 'pace') families.push(state.actionFamily);
      if (state.state === 'claw-scrape') {
        clawStages.add(state.clawAction.stage);
        if (!firstClaw) firstClaw = { previousState, snapshot: state };
      }
      previousState = state.state;
    }
    return { families, clawStages, firstClaw };
  });

  for (const trace of traces) {
    assert.ok(trace.families.length >= 12);
    assert.ok(new Set(trace.families).size >= 4);
    for (let index = 1; index < trace.families.length; index += 1) {
      assert.notEqual(trace.families[index], trace.families[index - 1], 'action families do not immediately repeat');
    }
    const periodThree = trace.families.every((family, index) => index < 3 || family === trace.families[index % 3]);
    assert.equal(periodThree, false, 'seeded behavior is not a forced three-family cycle');
    assert.ok(trace.firstClaw, 'the authored claw family is selected autonomously');
    assert.equal(trace.firstClaw.previousState, 'boundary', 'the action begins only after its route settles at the boundary');
    assert.equal(trace.firstClaw.snapshot.actionKind, 'claw-scrape');
    assert.equal(trace.firstClaw.snapshot.clawAction.target, 'floor-scrape');
    assert.ok(['approach','lift','contact','scrape','release','recovery'].every(stage => trace.clawStages.has(stage)));
  }
  assert.equal(new Set(traces.map(trace => trace.families.join('|'))).size, traces.length, 'different seeds produce different plan sequences');
});

test('visitor reach maps normalized input to a discrete world rail and runs one gated sequence', () => {
  const machine = createPresenceState({ seed: 1 });
  assert.equal(machine.requestReach({ x: 0.9, y: -0.5 }), true);
  assert.equal(machine.requestReach({ x: -1 }), false, 'a second reach must not stack');
  const notice = machine.getSnapshot();
  assert.deepEqual(notice.reach, { x: 0.9, y: -0.5 });
  assert.equal(notice.state, 'notice');
  assert.equal(notice.actionKind, 'visitor');

  const approach = stepUntil(machine, s => s.state === 'approach');
  assert.deepEqual(approach.goal, { x: 1.2, z: 1.02 });
  assert.equal(approach.lookTarget.x, 1.2);
  assert.equal(machine.requestReach(), false);

  const blocked = { arrived: true, settled: true, aligned: false };
  for (let i = 0; i < 12; i += 1) machine.update(0.1, blocked);
  assert.equal(machine.getSnapshot().state, 'approach', 'arrival without alignment must not advance');
  const warning = stepUntil(machine, s => s.state === 'warning');
  assert.equal(warning.goal.x, 1.2);
  assert.equal(machine.requestReach(), false);
  stepUntil(machine, s => s.state === 'strike');
  stepUntil(machine, s => s.state === 'contact');
  stepUntil(machine, s => s.state === 'recover');
  stepUntil(machine, s => s.state === 'agitated');
  stepUntil(machine, s => s.state === 'settle');
  stepUntil(machine, s => s.state === 'watch');
  assert.equal(machine.getSnapshot().visitorPresent, false);
});

test('retreat cancels before commitment and waits for committed contact/recovery after strike', () => {
  const before = createPresenceState();
  before.requestReach({ x: -0.8, y: 0.4 });
  stepUntil(before, s => s.state === 'approach');
  assert.equal(before.requestRetreat(), true);
  assert.equal(before.getSnapshot().state, 'agitated');
  assert.equal(before.getSnapshot().visitorPresent, false);
  assert.equal(before.getSnapshot().actionKind, null);

  const after = createPresenceState();
  after.requestReach({ x: 0.7 });
  stepUntil(after, s => s.state === 'strike');
  assert.equal(after.requestRetreat(), true);
  assert.equal(after.getSnapshot().state, 'strike');
  stepUntil(after, s => s.state === 'contact');
  stepUntil(after, s => s.state === 'recover');
  stepUntil(after, s => s.state === 'agitated');
  assert.equal(after.getSnapshot().visitorPresent, false);
});

test('inspection interrupts reaction, grounds before opening, and stays closed until reassembly', () => {
  const machine = createPresenceState();
  machine.requestReach({ x: -1 });
  stepUntil(machine, s => s.state === 'approach');
  machine.setInspection(true);
  assert.equal(machine.getSnapshot().state, 'settle');
  assert.equal(machine.getSnapshot().inspectionRequested, true);
  assert.equal(machine.getSnapshot().inspection, false);
  assert.equal(machine.getSnapshot().actionKind, null);
  stepUntil(machine, s => s.inspection, { feedback: { settled: true, arrived: false, aligned: false } });
  assert.equal(machine.getSnapshot().state, 'inspection');
  assert.equal(machine.getSnapshot().goal, null);

  machine.setInspection(false);
  assert.equal(machine.getSnapshot().inspection, false);
  assert.equal(machine.getSnapshot().inspectionRequested, false);
  assert.equal(machine.getSnapshot().state, 'watch');
});

test('pause freezes encounter phase while inspection can still finish a grounded transition', () => {
  const machine = createPresenceState();
  machine.requestReach({ x: 0.2 });
  machine.update(0.2, READY);
  machine.setPaused(true);
  const phase = machine.getSnapshot().phase;
  for (let i = 0; i < 5; i += 1) machine.update(0.1, READY);
  assert.equal(machine.getSnapshot().phase, phase);
  machine.setInspection(true);
  assert.equal(machine.getSnapshot().state, 'settle');
  stepUntil(machine, s => s.inspection, { feedback: { settled: true } });
  assert.equal(machine.getSnapshot().paused, true);
});

test('reduced motion acknowledges a visitor without travel or strike and lets an active step ground', () => {
  const machine = createPresenceState();
  machine.setReducedMotion(true);
  assert.equal(machine.requestReach({ x: 1 }), true);
  stepUntil(machine, s => s.state === 'settle');
  assert.equal(machine.getSnapshot().speed, 0);
  stepUntil(machine, s => s.state === 'watch');
  assert.equal(machine.getSnapshot().visitorPresent, false);
  assert.equal(machine.getSnapshot().state, 'watch');

  const moving = createPresenceState({ seed: 2 });
  stepUntil(moving, s => s.state === 'pace');
  moving.setReducedMotion(true);
  const stopping = moving.getSnapshot();
  assert.equal(stopping.state, 'settle');
  assert.equal(stopping.speed, 0.55, 'renderer may finish the current planted step');
  assert.ok(stopping.goal);
  moving.update(0.1, { settled: true });
  assert.equal(moving.getSnapshot().state, 'watch');
  assert.equal(moving.getSnapshot().speed, 0);
});

test('earlier eras suppress autonomous behavior and switching eras clears active reach', () => {
  const machine = createPresenceState({ seed: 9 });
  machine.requestReach({ x: 1 });
  machine.setEra('maker');
  assert.equal(machine.getSnapshot().state, 'watch');
  assert.equal(machine.getSnapshot().goal, null);
  assert.equal(machine.getSnapshot().visitorPresent, false);
  assert.equal(machine.requestReach({ x: 0 }), false);
  for (let i = 0; i < 300; i += 1) machine.update(0.1, READY);
  assert.equal(machine.getSnapshot().state, 'watch');
  assert.equal(machine.getSnapshot().speed, 0);
  assert.equal(machine.setEra('mechanic'), true);
  assert.equal(machine.setEra('wrong-era'), false);
});

test('input and elapsed time are sanitized, bounded, and reproducible', () => {
  const a = createPresenceState({ seed: 123 });
  const b = createPresenceState({ seed: 123 });
  assert.equal(a.requestReach({ x: Infinity, y: NaN }), true);
  assert.equal(b.requestReach({ x: Infinity, y: NaN }), true);
  assert.deepEqual(a.getSnapshot().reach, { x: 0, y: 0 });
  for (const dt of [-2, NaN, Infinity, 1e12, 0.1]) {
    assert.deepEqual(a.update(dt, null), b.update(dt, null));
    assertFiniteSnapshot(a.getSnapshot());
  }
  assert.ok(a.getSnapshot().phase <= 1);
  assert.deepEqual(a.getSnapshot().goal, b.getSnapshot().goal);
});

test('idle pause and inspection changes each notify exactly once', () => {
  const changes = [];
  const machine = createPresenceState({ onChange: snapshot => changes.push(snapshot) });
  machine.setPaused(true);
  assert.equal(changes.length, 1);
  assert.equal(changes[0].paused, true);
  machine.setInspection(true);
  assert.equal(changes.length, 2);
  assert.equal(changes[1].inspectionRequested, true);
  assert.equal(changes[1].state, 'settle');
});
