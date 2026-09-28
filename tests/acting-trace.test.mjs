import test from 'node:test';
import assert from 'node:assert/strict';
import { analyzeActingTrace } from '../scripts/analyze-acting-trace.mjs';

function trace() {
  return Array.from({ length: 1201 }, (_, i) => ({
    seconds: i / 10, era: 'builder', state: i >= 100 && i < 120 ? 'cage-test' : 'pace',
    visitorPresent: false, paused: false, inspection: false, reducedMotion: false,
    beatId: 'one-route', actionFamily: 'rail-press', routeKind: 'front', intensity: .6,
    clawAction: null,
    motion: { contact: i >= 108 && i < 115, clawAction: null, root: { x: 0, z: i / 12000, yaw: 0, speed: .01 }, distance: i / 12000, steps: Math.floor(i / 100) },
  }));
}

function setClawSample(samples, index, stage, contact = false) {
  const action = stage ? {
    stage, phase: .5, side: 'left', target: 'floor-scrape', contact,
    tipMinY: contact ? .002 : .04,
  } : null;
  samples[index].clawAction = action && { ...action };
  samples[index].motion.clawAction = action && { ...action };
}

test('counts actual action episodes and contact intervals, not persistent plan labels', () => {
  const result = analyzeActingTrace(trace());
  assert.deepEqual(result.executedFamilyCounts, { 'rail-press': 1 });
  assert.equal(result.executedActions[0].duration, 2);
  assert.ok(Math.abs(result.contactIntervals[0].duration - .7) < 1e-9);
  assert.equal(result.measuredSeconds, 120);
  assert.ok(result.warnings.some(s => s.includes('Fewer than three')));
});

test('counts plan repeats and repeated executed action families across separate episodes', () => {
  const samples = trace();
  samples.forEach(sample => { sample.state = 'watch'; });
  samples[0].state = 'pace';
  for (let i = 40; i < 100; i++) samples[i].state = 'pace';
  for (let i = 100; i < 120; i++) samples[i].state = 'cage-test';
  for (let i = 120; i < 200; i++) samples[i].state = 'watch';
  for (let i = 200; i < 210; i++) samples[i].state = 'cage-test';

  const result = analyzeActingTrace(samples);
  assert.deepEqual(result.selectedPlans.map(plan => plan.id), ['one-route', 'one-route']);
  assert.equal(result.consecutiveRepeatedPlans, 1);
  assert.deepEqual(result.executedFamilyCounts, { 'rail-press': 2 });
  assert.equal(result.executedActions.length, 2);
  assert.equal(result.executedActions[1].duration, 1);
  assert.equal(result.consecutiveRepeatedActionFamilies, 1);
});

test('approach-only claw cancellation is not counted as an executed claw episode', () => {
  const samples = trace();
  samples.forEach(sample => { sample.state = 'watch'; sample.actionFamily = 'claw-scrape'; sample.motion.contact = false; });
  for (let i = 100; i < 102; i++) setClawSample(samples, i, 'approach');
  for (let i = 102; i < 104; i++) setClawSample(samples, i, 'recovery');

  const result = analyzeActingTrace(samples);
  assert.equal(result.clawTelemetrySamples, 4);
  assert.deepEqual(result.executedClawActions, []);
  assert.deepEqual(result.clawContactIntervals, []);
  assert.deepEqual(result.executedFamilyCounts, {});
});

test('separate claw episodes count after lift and retain renderer contact evidence', () => {
  const samples = trace();
  samples.forEach(sample => { sample.state = 'watch'; sample.actionFamily = 'claw-scrape'; sample.motion.contact = false; });
  const firstStages = ['lift', 'contact', 'scrape', 'release', 'recovery'];
  firstStages.forEach((stage, offset) => setClawSample(samples, 100 + offset, stage, false));
  const secondStages = ['lift', 'contact', 'scrape', 'release', 'recovery'];
  secondStages.forEach((stage, offset) => setClawSample(samples, 200 + offset, stage, offset === 2));

  const result = analyzeActingTrace(samples);
  assert.equal(result.executedClawActions.length, 2);
  assert.deepEqual(result.executedClawActions.map(action => action.stagesObserved), [firstStages, secondStages]);
  assert.deepEqual(result.executedClawActions.map(action => action.hadRendererContact), [false, true]);
  assert.equal(result.clawContactIntervals.length, 1);
  assert.equal(result.clawContactIntervals[0].start, 20.2);
  assert.ok(Math.abs(result.clawContactIntervals[0].duration - .1) < 1e-9);
  assert.deepEqual(result.executedFamilyCounts, { 'claw-scrape': 2 });
  assert.equal(result.executedActions.length, 2);
  assert.equal(result.executedCageActions.length, 0);
  assert.equal(result.consecutiveRepeatedActionFamilies, 1);
  assert.equal(result.warnings.some(s => s.startsWith('No autonomous action')), false);
});

test('a claw action-family label alone does not create executed action or contact evidence', () => {
  const samples = trace();
  samples.forEach(sample => { sample.state = 'watch'; sample.actionFamily = 'claw-scrape'; sample.motion.contact = false; });

  const result = analyzeActingTrace(samples);
  assert.equal(result.clawTelemetrySamples, 0);
  assert.deepEqual(result.executedClawActions, []);
  assert.deepEqual(result.clawContactIntervals, []);
  assert.deepEqual(result.executedFamilyCounts, {});
});

test('legacy v3 traces remain analyzable while claw-state samples require explicit telemetry fields', () => {
  const samples = trace();
  samples.forEach(s => { delete s.clawAction; delete s.motion.clawAction; });
  const result = analyzeActingTrace(samples);
  assert.equal(result.clawFieldsAvailable, false);
  assert.deepEqual(result.executedFamilyCounts, { 'rail-press': 1 });
  samples[5].state = 'claw-scrape';
  assert.throws(() => analyzeActingTrace(samples), /lacks controller claw-action telemetry/);
  samples[5].clawAction = { stage: 'lift' };
  assert.throws(() => analyzeActingTrace(samples), /lacks renderer claw-action telemetry/);
});

test('rejects short, gapped, duplicated-clock, and interrupted evidence', () => {
  assert.throws(() => analyzeActingTrace(trace().slice(0, 1161)), /Only 116/);
  const gap = trace(); gap.splice(500, 10);
  assert.throws(() => analyzeActingTrace(gap), /Telemetry gap/);
  const duplicate = trace(); duplicate[2].seconds = duplicate[1].seconds;
  assert.throws(() => analyzeActingTrace(duplicate), /does not advance/);
  for (const key of ['visitorPresent', 'paused', 'inspection', 'reducedMotion']) {
    const interrupted = trace(); interrupted[5][key] = true;
    assert.throws(() => analyzeActingTrace(interrupted));
  }
  const missingDistance = trace(); delete missingDistance[5].motion.distance;
  assert.throws(() => analyzeActingTrace(missingDistance), /lacks finite motion\.distance/);
  const missingSteps = trace(); missingSteps[5].motion.steps = Number.NaN;
  assert.throws(() => analyzeActingTrace(missingSteps), /lacks finite motion\.steps/);
});

test('an absent action produces a warning instead of a fabricated variation pass', () => {
  const samples = trace(); samples.forEach(s => { s.state = 'pace'; s.motion.contact = false; });
  const result = analyzeActingTrace(samples);
  assert.deepEqual(result.executedFamilyCounts, {});
  assert.equal(result.contactIntervals.length, 0);
  assert.ok(result.warnings.some(s => s.startsWith('No autonomous action')));
});
