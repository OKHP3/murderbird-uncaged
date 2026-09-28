import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import * as THREE from 'three';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { loadRigidValidation } from './load-rigid-validation.mjs';
import { createEraController } from '../src/scene/era-controller.js';
import { createEraMechanisms } from '../src/scene/era-mechanisms.js';
import { createEraMotion } from '../src/scene/era-motion.js';

// Deterministic Node-only interruption and assembly regression against the
// versioned production GLB. This does not claim browser, GPU, camera-focus,
// or visual-region coverage.
const MODEL_PATH = process.env.UNCAGED_MODEL || 'assets/models/uncaged-alignment-v3/murderbird-alignment-v3.glb';
const MODEL_SHA256 = process.env.UNCAGED_EXPECTED_MODEL_SHA256 || 'c4dc308f77399410368b82443a1b21b9113cfedb258aa055906b4f13c92dda21';
const REPORT_PATH = (process.env.UNCAGED_AUDIT || 'assets/audit/regression-v4') + '/interruption-validation.json';
const ERAS = ['maker', 'mechanic', 'builder'];
const NODE_NAMES = [
  'body', 'neck', 'head', 'jaw', 'breastplate', 'cranial-cover', 'winding-drive',
  'power-core', 'processing', 'industrial-repairs', 'builder-optics', 'left-mantle',
  'right-mantle', 'left-wing-shield', 'right-wing-shield',
];
const OUTPUT = { generatedAt: new Date().toISOString(), runtime: { node: process.version, platform: process.platform, architecture: process.arch }, model: MODEL_PATH, expectedModelSha256: MODEL_SHA256, checks: [] };
let template;

function check(name, run) {
  try { OUTPUT.checks.push({ name, status: 'passed', result: run() }); }
  catch (error) { OUTPUT.checks.push({ name, status: 'failed', error: error.stack || error.message }); }
}

function createRun({ seed = 927, dt = 1 / 60 } = {}) {
  const model = clone(template.scene);
  const scene = new THREE.Scene();
  scene.add(model);
  const nodes = Object.fromEntries(NODE_NAMES.map(name => [name, model.getObjectByName(name)]));
  assert.ok(Object.values(nodes).every(Boolean), 'versioned GLB is missing a required motion node');
  const rest = Object.fromEntries(NODE_NAMES.map(name => [name, {
    position: nodes[name].position.clone(), rotation: nodes[name].rotation.clone(),
  }]));
  const motion = createEraMotion(model, nodes, rest);
  const mechanisms = createEraMechanisms({ scene, model, nodes, rest });
  const machine = createEraController({ seed });
  let era = 'builder';
  let time = 0;

  function step(seconds = dt, inspectionPose = { open: 0, separation: 0 }) {
    const state = machine.update(seconds, motion.feedback());
    if (state.era !== era) { era = state.era; mechanisms.setEra(era); }
    for (const name of NODE_NAMES) {
      nodes[name].position.copy(rest[name].position);
      nodes[name].rotation.copy(rest[name].rotation);
    }
    motion.tick(seconds, state);
    mechanisms.tick(seconds, state, motion.driveMetrics(), inspectionPose);
    time += seconds;
    return { state, metrics: motion.metrics(), time };
  }

  function advanceUntil(predicate, limitSeconds = 18) {
    for (let i = 0, max = Math.ceil(limitSeconds / dt); i < max; i += 1) {
      const frame = step();
      if (predicate(frame.state, frame.metrics)) return frame;
    }
    assert.fail(`condition not reached within ${limitSeconds}s; state=${machine.getSnapshot().state}`);
  }

  function advanceFor(seconds) {
    const end = time + seconds;
    while (time + 1e-9 < end) step(Math.min(dt, end - time));
  }

  function enterEra(value) {
    assert.equal(machine.setEra(value), true);
    era = value;
    mechanisms.setEra(value);
    advanceUntil(state => state.era === value && !state.inspection && !state.inspectionRequested, 3);
  }

  function dispose() { mechanisms.dispose(); }
  return { model, scene, nodes, rest, motion, mechanisms, machine, step, advanceUntil, advanceFor, enterEra, dispose };
}

function connectorState(metrics) {
  return {
    era: metrics.era,
    visible: metrics.visible,
    anchors: metrics.anchors,
    inspectionConnections: metrics.inspectionConnections,
  };
}

function verifyFiveInspectionCyclesPerEra() {
  const run = createRun();
  const results = {};
  for (const era of ERAS) {
    run.enterEra(era);
    const cycles = [];
    for (let cycle = 1; cycle <= 5; cycle += 1) {
      run.machine.setInspection(true);
      const opened = run.advanceUntil(state => state.inspection && run.motion.feedback().settled, 8);
      assert.equal(opened.state.era, era);
      run.mechanisms.tick(0, opened.state, run.motion.driveMetrics(), { open: 1, separation: 0 });
      const assembledConnectors = connectorState(run.mechanisms.metrics());
      const separationEvidence = [];
      for (const separation of [0, 0.5, 1]) {
        run.mechanisms.tick(0, opened.state, run.motion.driveMetrics(), { open: 1, separation });
        const metrics = run.mechanisms.metrics();
        assert.ok(metrics.tickCount > 0, `${era} cycle ${cycle}: mechanism inspection did not tick`);
        const current = connectorState(metrics);
        if (era === 'builder' && separation >= 0.5) {
          assert.notDeepEqual(current.inspectionConnections, assembledConnectors.inspectionConnections,
            `Builder cycle ${cycle}: nonzero separation did not change connector state`);
          assert.equal(metrics.inspectionConnections.wing.mode, 'disengaged-at-sockets', 'Builder wing link did not separate at its sockets');
          assert.equal(metrics.inspectionConnections.powerCore.mode, 'disengaged-at-sockets', 'Builder power link did not separate at its sockets');
        } else if (era !== 'builder' && separation > 0) {
          assert.equal(metrics.inspectionConnections.separationMode, 'not-eligible', `${era} exposed Builder separation mechanics`);
          assert.deepEqual(current, assembledConnectors, `${era} cycle ${cycle}: inapplicable separation altered era mechanisms`);
        }
        separationEvidence.push({ separation, era: metrics.era,
          wingMode: metrics.inspectionConnections.wing.mode,
          powerCoreMode: metrics.inspectionConnections.powerCore.mode,
          cervicalModes: metrics.inspectionConnections.cervical.map(link => link.mode) });
      }
      // Reassembly here means mechanism connectors return to their exact
      // connected state. Exported shell/cap offsets are owned by presence-exhibit.js
      // and intentionally remain outside this Node-only check.
      run.mechanisms.tick(0, opened.state, run.motion.driveMetrics(), { open: 1, separation: 0 });
      assert.deepEqual(connectorState(run.mechanisms.metrics()), assembledConnectors,
        `${era} cycle ${cycle}: connector state did not restore after separation`);
      run.mechanisms.tick(0, opened.state, run.motion.driveMetrics(), { open: 0, separation: 0 });
      run.machine.setInspection(false);
      const closed = run.advanceUntil(state => !state.inspection && !state.inspectionRequested
        && !state.powerMove && run.motion.feedback().settled, 8);
      assert.equal(closed.state.era, era);
      assert.equal(closed.state.powerMove, null, `${era} cycle ${cycle}: stale action survived inspection close`);
      cycles.push({ cycle, separationEvidence, reassembled: true, settledOnClose: true });
    }
    results[era] = cycles;
  }
  run.dispose();
  return { cyclesPerEra: 5, eras: results, builderConnectorsChangedAtNonzeroSeparation: true,
    connectorStateRestored: true, shellAndCoverOffsetsCovered: false };
}

function verifyRapidReachDoesNotStack() {
  const run = createRun();
  run.enterEra('builder');
  assert.equal(run.machine.requestReach({ x: 0 }), true, 'first reach was not accepted');
  const acceptedInputs = [0];
  const rejectedInputs = [];
  for (let input = 1; input < 10; input += 1) {
    assert.equal(run.machine.requestReach({ x: (input % 3) - 1 }), false, `rapid input ${input + 1} stacked another reach`);
    rejectedInputs.push(input);
  }
  const interrupted = run.advanceUntil(state => ['approach', 'warning', 'strike', 'contact', 'recover'].includes(state.state), 8);
  run.machine.setInspection(true);
  const inspected = run.advanceUntil(state => state.inspection && run.motion.feedback().settled, 12);
  assert.equal(inspected.state.visitorPresent, false, 'inspection retained an active visitor target');
  assert.equal(inspected.state.actionKind, null, 'inspection retained a stale attack action');
  run.machine.setInspection(false);
  const ready = run.advanceUntil(state => state.canReach && !state.visitorPresent && !state.inspectionRequested, 8);
  assert.equal(ready.state.actionKind, null, 'recovery resumed a stale attack');
  assert.equal(run.machine.requestReach({ x: -1 }), true, 'reach control did not recover after interruption');
  const recoveredRejected = [];
  for (let input = 1; input < 10; input += 1) {
    assert.equal(run.machine.requestReach({ x: (input % 3) - 1 }), false, `post-recovery input ${input + 1} stacked another reach`);
    recoveredRejected.push(input);
  }
  run.dispose();
  return { acceptedInputs, rejectedInputs, interruptedAt: interrupted.state.state, inspectionClearedVisitor: true,
    recoveredReachable: ready.state.canReach, postRecoveryAcceptedInputs: 1, postRecoveryRejectedInputs: recoveredRejected };
}

function verifyEraActionInterruptionMatrix() {
  const cases = [];
  for (const era of ERAS) {
    for (const interruption of ['pause', 'reduced-motion', 'inspection', 'rapid-era-change']) {
      const run = createRun();
      run.enterEra(era);
      if (era === 'maker') run.machine.setArticulation('wing', 0.8);
      if (era === 'mechanic') assert.equal(run.machine.requestRoutine(), true);
      if (era === 'builder') assert.equal(run.machine.requestReach({ x: 0 }), true);
      run.advanceFor(0.15);
      if (interruption === 'pause') {
        run.machine.setPaused(true);
        const before = run.machine.getSnapshot();
        run.advanceFor(0.25);
        assert.equal(run.machine.getSnapshot().paused, true);
        if (era === 'mechanic') assert.equal(run.machine.getSnapshot().routineRunning, before.routineRunning);
        run.machine.setPaused(false);
      } else if (interruption === 'reduced-motion') {
        run.machine.setReducedMotion(true);
        run.advanceFor(0.25);
        assert.equal(run.machine.getSnapshot().reducedMotion, true);
        if (era === 'mechanic') assert.equal(run.machine.getSnapshot().routineRunning, false, 'reduced motion left the Mechanic routine running');
      } else if (interruption === 'inspection') {
        run.machine.setInspection(true);
        const state = run.advanceUntil(snapshot => snapshot.inspection && run.motion.feedback().settled, 12);
        assert.equal(state.state.visitorPresent, false, `${era}: inspection retained visitor presence`);
        assert.equal(state.state.actionKind, null, `${era}: inspection retained action kind`);
      } else {
        const nextEra = ERAS[(ERAS.indexOf(era) + 1) % ERAS.length];
        // Several requests in one tick must leave one deterministic final era.
        for (const value of [nextEra, era, nextEra]) assert.equal(run.machine.setEra(value), true);
        const switched = run.step().state;
        assert.equal(switched.era, nextEra, `${era}: final rapid era request did not win`);
        assert.equal(switched.inspection, false, 'era change retained inspection');
        assert.equal(switched.inspectionRequested, false, 'era change retained a pending inspection');
        assert.equal(switched.visitorPresent, false, 'era change retained a stale visitor target');
        assert.equal(switched.routineRunning, false, 'era change retained a stale Mechanic routine');
        assert.equal(switched.powerMove, null, 'era change retained a stale power action');
      }
      if (interruption !== 'rapid-era-change') {
        run.machine.setInspection(false);
        run.advanceFor(0.6);
      }
      const settled = run.motion.metrics();
      assert.ok(settled.maxFootError < 0.002, `${era}/${interruption}: foot support error exceeded 2 mm`);
      cases.push({ era, supportedAction: { maker: 'external-articulation', mechanic: 'routine', builder: 'reach' }[era], interruption, state: run.machine.getSnapshot().state });
      run.dispose();
    }
  }
  return { combinations: cases, count: cases.length, footSolveBoundMet: true };
}

function verifyPowerActionCancelPoints() {
  const cases = [];
  for (const kind of ['jump', 'thrust']) {
    for (const interruption of ['pause-resume', 'inspection', 'controller-reset-api-diagnostic']) {
      const run = createRun();
      run.enterEra('builder');
      assert.equal(run.machine.requestPowerMove(kind), true, `${kind} was rejected from settled Builder`);
      const active = run.advanceUntil(state => state.powerMove?.kind === kind && state.powerMove.phase >= 0.42, 5);
      if (interruption === 'pause-resume') {
        run.machine.setPaused(true);
        const phase = run.machine.getSnapshot().powerMove.phase;
        run.advanceFor(0.3);
        assert.equal(run.machine.getSnapshot().powerMove.phase, phase, `${kind}: paused phase advanced`);
        run.machine.setPaused(false);
        const landed = run.advanceUntil(state => !state.powerMove && state.canReach && run.motion.feedback().settled, 5);
        assert.equal(landed.state.inspection, false, `${kind}: pause/resume left inspection open`);
      } else if (interruption === 'inspection') {
        run.machine.setInspection(true);
        const inspected = run.advanceUntil(state => state.inspection && !state.powerMove && run.motion.feedback().settled, 6);
        assert.equal(inspected.state.era, 'builder');
        assert.equal(inspected.metrics.powerMove, null);
      } else {
        run.machine.reset();
        const cleared = run.advanceUntil(state => !state.powerMove && !state.powerMovePending
          && !state.inspection && !state.inspectionRequested && state.canReach, 5);
        assert.equal(cleared.state.actionKind, null, `${kind}: reset allowed stale action to resume`);
      }
      const result = run.motion.metrics();
      const grounded = result.feet.every(foot => Math.abs(foot.groundMin - 0.002) <= 0.002);
      if (interruption !== 'controller-reset-api-diagnostic') {
        assert.ok(grounded, `${kind}/${interruption}: feet did not return to the floor (${result.feet.map(foot => foot.groundMin).join(', ')})`);
      }
      cases.push({ kind, interruption, requestedPhase: active.state.powerMove.phase, endedOnGround: grounded,
        feetGroundMin: result.feet.map(foot => Number.isFinite(foot.groundMin) ? foot.groundMin : String(foot.groundMin)),
        gating: interruption !== 'controller-reset-api-diagnostic' });
      run.dispose();
    }
  }
  return { cases, count: cases.length };
}

const bytes = await readFile(MODEL_PATH);
const modelSha256 = createHash('sha256').update(bytes).digest('hex');
assert.equal(modelSha256, MODEL_SHA256, `model SHA256 mismatch: expected ${MODEL_SHA256}, got ${modelSha256}`);
OUTPUT.modelSha256 = modelSha256;
const SOURCE_PATHS = [
  'src/scene/era-controller.js', 'src/scene/presence-state.js',
  'src/scene/era-motion.js', 'src/scene/era-mechanisms.js',
  'src/scene/rigid-leg-kinematics.js', 'scripts/load-rigid-validation.mjs',
  'scripts/verify-interruption-v4.mjs', 'package-lock.json',
];
OUTPUT.sourceSha256 = Object.fromEntries(await Promise.all(SOURCE_PATHS.map(async path => [
  path, createHash('sha256').update(await readFile(path)).digest('hex'),
])));
template = await loadRigidValidation(bytes);
assert.ok(template.scene, 'GLB parse returned no scene');
check('five-era-inspection-cycles-restore-mechanism-connectors', verifyFiveInspectionCyclesPerEra);
check('ten-rapid-reach-inputs-do-not-stack-or-resume-stale-attack', verifyRapidReachDoesNotStack);
check('each-era-supported-action-interruption-matrix', verifyEraActionInterruptionMatrix);
check('jump-and-thrust-pause-inspection-and-reset-cancel-points', verifyPowerActionCancelPoints);
OUTPUT.status = OUTPUT.checks.every(item => item.status === 'passed') ? 'passed' : 'failed';
OUTPUT.report = REPORT_PATH;
OUTPUT.coverageLimits = [
  'Node state and actual-GLB kinematic/mechanism regression only.',
  'Does not exercise browser UI orchestration, region selection, camera focus, visual appearance, GPU/WebGL, or human acceptance.',
  'Five-cycle separation coverage verifies era mechanism connector modes and exact connector-state restoration. Exported breastplate/cranial-cover and other shell offsets in src/scene/presence-exhibit.js are not executed by this Node fixture.',
  'Bare controller.reset() while retaining an airborne motion rig is recorded as an API diagnostic only: the app reload path destroys and recreates the rig, while Reset view changes only the camera.',
];
const resetDiagnostic = OUTPUT.checks.find(check => check.name === 'jump-and-thrust-pause-inspection-and-reset-cancel-points')
  ?.result?.cases?.find(item => item.kind === 'jump' && item.interruption === 'controller-reset-api-diagnostic');
OUTPUT.apiDiagnostics = resetDiagnostic ? [{
  case: 'jump/controller-reset-api-diagnostic',
  endedOnGround: resetDiagnostic.endedOnGround,
  feetGroundMin: resetDiagnostic.feetGroundMin,
  inPublicResetPath: false,
}] : [];
await mkdir(dirname(REPORT_PATH), { recursive: true });
await writeFile(REPORT_PATH, `${JSON.stringify(OUTPUT, null, 2)}\n`, { flag: 'wx' });
console.log(`${OUTPUT.status}: ${OUTPUT.checks.filter(item => item.status === 'passed').length}/${OUTPUT.checks.length} checks`);
if (OUTPUT.status !== 'passed') {
  for (const item of OUTPUT.checks.filter(entry => entry.status === 'failed')) console.error(`${item.name}: ${item.error.split('\n')[0]}`);
  process.exitCode = 1;
}
