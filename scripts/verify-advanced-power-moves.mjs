import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { createEraMotion } from '../src/scene/era-motion.js';
import { createEraController } from '../src/scene/era-controller.js';

const MODEL_PATH = 'assets/models/uncaged-presence-study/murderbird-presence-study.glb';
const REPORT_PATH = 'assets/audit/three-era-review/power-move-validation.json';
const NODE_NAMES = [
  'body', 'neck', 'head', 'jaw', 'breastplate', 'cranial-cover', 'winding-drive',
  'power-core', 'processing', 'industrial-repairs', 'builder-optics', 'left-mantle',
  'right-mantle', 'left-wing-shield', 'right-wing-shield',
];
const OUTPUT = { generatedAt: new Date().toISOString(), model: MODEL_PATH, report: REPORT_PATH, checks: [] };
let template;

function check(name, fn) {
  try { OUTPUT.checks.push({ name, status: 'passed', result: fn() }); }
  catch (error) { OUTPUT.checks.push({ name, status: 'failed', error: error.message }); }
}

function createRun(dt = 1 / 60) {
  const model = clone(template.scene);
  const nodes = Object.fromEntries(NODE_NAMES.map(name => [name, model.getObjectByName(name)]));
  assert.ok(Object.values(nodes).every(Boolean), 'GLB is missing required named nodes');
  const rest = Object.fromEntries(NODE_NAMES.map(name => [name, { position: nodes[name].position.clone(), rotation: nodes[name].rotation.clone() }]));
  const motion = createEraMotion(model, nodes, rest);
  const machine = createEraController({ seed: 927 });
  let time = 0;

  function step(seconds = dt) {
    const state = machine.update(seconds, motion.feedback());
    for (const name of NODE_NAMES) {
      nodes[name].position.copy(rest[name].position);
      nodes[name].rotation.copy(rest[name].rotation);
    }
    motion.tick(seconds, state);
    time += seconds;
    return { state, metrics: motion.metrics(), time };
  }

  function advanceUntil(predicate, limit = 12) {
    for (let i = 0; i < Math.ceil(limit / dt); i += 1) {
      const frame = step();
      if (predicate(frame.state, frame.metrics)) return frame;
    }
    assert.fail(`condition not reached within ${limit}s; state=${machine.getSnapshot().state}`);
  }

  function advanceFor(seconds) {
    const end = time + seconds;
    while (time + 1e-9 < end) step(Math.min(dt, end - time));
  }

  return { model, nodes, rest, motion, machine, step, advanceUntil, advanceFor, get time() { return time; } };
}

function assertInsideCage(metrics, label) {
  const b = metrics.bodyBounds;
  assert.ok(b.min.y >= -0.002, `${label}: model penetrated floor to y=${b.min.y}`);
  assert.ok(b.max.y <= 2.55, `${label}: model exceeded vertical cage envelope at y=${b.max.y}`);
  assert.ok(b.min.x >= -2.9 && b.max.x <= 2.9, `${label}: model exceeded cage X bounds`);
  assert.ok(b.min.z >= -2.1 && b.max.z <= 2.1, `${label}: model exceeded cage Z bounds`);
}

function verifyJump() {
  const run = createRun();
  run.step();
  assert.equal(run.machine.requestPowerMove('jump'), true, 'settled Builder did not accept jump');
  let peak;
  run.advanceUntil((state, metrics) => {
    if (metrics.powerMove?.kind === 'jump' && (!peak || metrics.powerMove.height > peak.metrics.powerMove.height)) {
      peak = { state, metrics, modelY: run.model.position.y };
    }
    return metrics.powerMove?.kind === 'jump' && metrics.powerMove.phase >= 1;
    }, 5);
  const result = run.motion.metrics();
  assert.ok(peak, 'jump peak was not sampled');
  assert.ok(peak.metrics.powerMove.height >= 0.34, `jump height was ${peak.metrics.powerMove.height} m`);
  assert.ok(peak.metrics.feet.every(foot => foot.groundMin > 0.15), 'both feet were not clearly airborne at jump peak');
  assert.ok(peak.metrics.bodyBounds.max.y < 2.55, `jump exceeded ceiling height ${peak.metrics.bodyBounds.max.y} m`);
  assert.ok(result.root.x === 0 && result.root.z === -0.25 && result.root.yaw === 0, 'jump changed root X/Z/yaw');
  assert.ok(result.maxFootError < 0.002, `jump IK error ${result.maxFootError} m exceeded 2 mm`);
  assert.ok(result.feet.every(foot => foot.groundMin >= -0.002), 'jump penetrated the floor');
  assert.ok(result.feet.every(foot => Math.abs(foot.groundMin - 0.002) <= 0.002), 'jump did not land with both soles within 2 mm of floor');
  assertInsideCage(result, 'jump landing');
  return { peakHeight: peak.metrics.powerMove.height, peakBodyTop: peak.metrics.bodyBounds.max.y, peakFeetGroundMin: peak.metrics.feet.map(foot => foot.groundMin), landingFeetGroundMin: result.feet.map(foot => foot.groundMin), maxFootError: result.maxFootError, root: result.root };
}

function verifyPauseMidair() {
  const run = createRun();
  run.step();
  assert.equal(run.machine.requestPowerMove('jump'), true);
  run.advanceUntil((state, metrics) => metrics.powerMove?.kind === 'jump' && metrics.powerMove.phase >= 0.42 && metrics.powerMove.phase <= 0.62, 4);
  const before = { modelPosition: run.model.position.toArray(), phase: run.motion.metrics().powerMove.phase, feet: run.motion.metrics().feet.map(f => f.actual) };
  run.machine.setPaused(true);
  run.advanceFor(.5);
  const afterMetrics = run.motion.metrics();
  const after = { modelPosition: run.model.position.toArray(), phase: afterMetrics.powerMove.phase, feet: afterMetrics.feet.map(f => f.actual) };
  assert.deepEqual(after.modelPosition, before.modelPosition, 'paused jump changed root position');
  assert.equal(after.phase, before.phase, 'paused jump phase advanced');
  assert.deepEqual(after.feet, before.feet, 'paused jump changed foot positions');
  run.machine.setPaused(false);
  run.advanceUntil((state, metrics) => metrics.powerMove?.phase >= 1, 4);
  const landed = run.motion.metrics();
  assert.ok(landed.feet.every(f => Math.abs(f.groundMin - 0.002) <= 0.002), 'resumed jump failed to land');
  return { frozenForSeconds: .5, phase: before.phase, root: before.modelPosition, feetFrozen: true, resumedAndLanded: true };
}

function verifyInspectionLanding() {
  const run = createRun();
  run.step();
  assert.equal(run.machine.requestPowerMove('jump'), true);
  run.advanceUntil((state, metrics) => metrics.powerMove?.kind === 'jump' && metrics.powerMove.phase >= 0.4 && metrics.powerMove.phase < 0.9, 4);
  run.machine.setInspection(true);
  assert.equal(run.machine.getSnapshot().inspection, false, 'inspection opened in midair');
  let observedCompletion = false;
  run.advanceUntil((state, metrics) => {
    if (metrics.powerMove?.phase >= 1) observedCompletion = true;
    if (state.inspection) {
      assert.ok(observedCompletion, 'inspection opened before jump completed');
      assert.ok(metrics.feet.every(f => Math.abs(f.groundMin - 0.002) <= 0.002), 'inspection opened before both feet landed');
      assert.equal(metrics.settled, true, 'inspection opened before motion settled');
      return true;
    }
    return false;
  }, 5);
  assert.equal(run.machine.getSnapshot().inspection, true);
  return { completedBeforeInspection: observedCompletion, grounded: true, settled: true };
}

function verifyThrust() {
  const run = createRun();
  run.step();
  const moving = run.advanceUntil((state, metrics) => ['pace', 'boundary'].includes(state.state)
    && Math.hypot(metrics.root.x, metrics.root.z + 0.25) > 0.08
    && Math.abs(metrics.root.yaw) > 0.04, 24);
  const stagedRoot = moving.metrics.root;
  assert.equal(run.machine.requestPowerMove('thrust'), true, 'settled Builder did not accept thrust');
  const active = run.advanceUntil((state, metrics) => metrics.powerMove?.kind === 'thrust', 12);
  assert.ok(Math.hypot(active.metrics.root.x, active.metrics.root.z + 0.25) > 0.05, 'thrust did not exercise an off-center starting pose');
  assert.ok(Math.abs(active.metrics.root.yaw) > 0.02, 'thrust did not exercise a rotated starting pose');
  const base = run.motion.metrics();
  let peak = null;
  run.advanceUntil((state, metrics) => {
    if (metrics.powerMove?.kind === 'thrust' && (!peak || Math.abs(run.nodes['right-wing-shield'].rotation.x) > Math.abs(peak.rightElbow))) peak = { metrics, rightShoulder: run.nodes['right-mantle'].rotation.x, rightElbow: run.nodes['right-wing-shield'].rotation.x, leftShoulder: run.nodes['left-mantle'].rotation.x, leftElbow: run.nodes['left-wing-shield'].rotation.x };
    return metrics.powerMove?.kind === 'thrust' && metrics.powerMove.phase >= 1;
  }, 5);
  const result = run.motion.metrics();
  assert.ok(peak, 'thrust pose was not sampled');
  assert.equal(result.root.x, base.root.x, 'thrust shifted root X');
  assert.equal(result.root.z, base.root.z, 'thrust shifted root Z');
  assert.equal(result.root.yaw, base.root.yaw, 'thrust rotated root');
  assert.ok(peak.rightShoulder < -0.5, `right shoulder rotation ${peak.rightShoulder} rad was too small`);
  assert.ok(peak.rightElbow > 0.5, `right elbow rotation ${peak.rightElbow} rad was too small`);
  assert.ok(Math.abs(peak.leftShoulder) < Math.abs(peak.rightShoulder), 'repaired left shoulder was not less mobile than right');
  assert.ok(Math.abs(peak.leftElbow) < Math.abs(peak.rightElbow), 'repaired left elbow was not less mobile than right');
  assert.ok(result.maxFootError < 0.002, `thrust IK error ${result.maxFootError} m exceeded 2 mm`);
  assert.ok(result.feet.every(f => Math.abs(f.groundMin - 0.002) <= 0.002), 'thrust did not keep both feet planted');
  assertInsideCage(result, 'thrust');
  return { stagedRoot, actionRoot: base.root, rightShoulder: peak.rightShoulder, rightElbow: peak.rightElbow, leftShoulder: peak.leftShoulder, leftElbow: peak.leftElbow, maxFootError: result.maxFootError, plantedFeet: result.feet.map(f => f.groundMin), root: result.root, bounds: result.bodyBounds };
}

async function main() {
  const bytes = await readFile(MODEL_PATH);
  template = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
  assert.ok(template.scene, 'GLB parse returned no scene');
  check('jump-height-foot-clearance-and-grounded-landing', verifyJump);
  check('jump-pause-midair-freezes-and-resumes', verifyPauseMidair);
  check('inspection-request-midair-waits-for-landing', verifyInspectionLanding);
  check('thrust-planted-feet-asymmetric-wing-drive-and-envelope', verifyThrust);
  OUTPUT.status = OUTPUT.checks.every(item => item.status === 'passed') ? 'passed' : 'failed';
  await mkdir(dirname(REPORT_PATH), { recursive: true });
  await writeFile(REPORT_PATH, `${JSON.stringify(OUTPUT, null, 2)}\n`);
  console.log(`${OUTPUT.status}: ${OUTPUT.checks.filter(item => item.status === 'passed').length}/${OUTPUT.checks.length} checks`);
  if (OUTPUT.status !== 'passed') {
    for (const item of OUTPUT.checks.filter(entry => entry.status === 'failed')) console.error(`${item.name}: ${item.error}`);
    process.exitCode = 1;
  }
}

await main();
