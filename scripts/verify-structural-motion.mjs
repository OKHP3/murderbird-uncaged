import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { createHash } from 'node:crypto';
import * as THREE from 'three';
import { loadRigidValidation } from './load-rigid-validation.mjs';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { createEraController } from '../src/scene/era-controller.js';
import { createEraMechanisms } from '../src/scene/era-mechanisms.js';
import { createEraMotion } from '../src/scene/era-motion.js';

// Structural reconciliation regression. It intentionally loads the versioned
// v1 GLB and writes to a new receipt path, leaving the Stage Two receipts intact.
const MODEL_PATH = process.env.UNCAGED_MODEL || 'assets/models/uncaged-exterior-v1/murderbird-exterior-v1.glb';
const REPORT_PATH = (process.env.UNCAGED_AUDIT || 'assets/audit/exterior-v1') + '/structural-motion-validation.json';
const NODE_NAMES = [
  'body', 'neck', 'head', 'jaw', 'breastplate', 'cranial-cover', 'winding-drive',
  'power-core', 'processing', 'industrial-repairs', 'builder-optics', 'left-mantle',
  'right-mantle', 'left-wing-shield', 'right-wing-shield',
];
const OUTPUT = { generatedAt: new Date().toISOString(), model: MODEL_PATH, checks: [] };
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
  assert.ok(Object.values(nodes).every(Boolean), 'v1 GLB is missing a required motion node');
  const rest = Object.fromEntries(NODE_NAMES.map(name => [name, {
    position: nodes[name].position.clone(), rotation: nodes[name].rotation.clone(),
  }]));
  const motion = createEraMotion(model, nodes, rest);
  const mechanisms = createEraMechanisms({ scene, model, nodes, rest });
  const machine = createEraController({ seed });
  let era = 'builder';
  let time = 0;

  function step(seconds = dt) {
    const state = machine.update(seconds, motion.feedback());
    if (state.era !== era) {
      era = state.era;
      mechanisms.setEra(era);
    }
    for (const name of NODE_NAMES) {
      nodes[name].position.copy(rest[name].position);
      nodes[name].rotation.copy(rest[name].rotation);
    }
    motion.tick(seconds, state);
    mechanisms.tick(seconds, state, motion.driveMetrics(), { open: 0, separation: 0 });
    time += seconds;
    return { state, metrics: motion.metrics(), time };
  }

  function advanceUntil(predicate, limitSeconds = 16) {
    const limit = Math.ceil(limitSeconds / dt);
    for (let i = 0; i < limit; i += 1) {
      const frame = step();
      if (predicate(frame.state, frame.metrics)) return frame;
    }
    assert.fail(`condition not reached within ${limitSeconds}s; state=${machine.getSnapshot().state}`);
  }

  function advanceFor(seconds) {
    const end = time + seconds;
    while (time + 1e-9 < end) step(Math.min(dt, end - time));
  }

  return { scene, model, nodes, rest, motion, mechanisms, machine, step, advanceUntil, advanceFor };
}

function checkFixedNeckAndHead(run, metrics = run.motion.metrics()) {
  assert.ok(metrics.cervical, 'motion metrics must expose cervical structural checks');
  assert.ok(metrics.cervical.baseTranslationError < 1e-9, `neck pivot moved ${metrics.cervical.baseTranslationError}m`);
  assert.ok(metrics.cervical.skullTranslationError < 1e-9, `head pivot moved ${metrics.cervical.skullTranslationError}m`);
  assert.ok(Math.abs(metrics.cervical.neckPitch - run.rest.neck.rotation.x) <= metrics.cervical.maxContactPitch + 1e-6,
    `neck pitch exceeded its ${metrics.cervical.maxContactPitch}rad bound`);
}

function verifyThreeRailContact() {
  const contacts = [];
  for (const normalizedX of [-1, 0, 1]) {
    const run = createRun();
    assert.equal(run.machine.requestReach({ x: normalizedX }), true, `reach at rail ${normalizedX} was rejected`);
    let maxPitch = 0, maxNeckTranslation = 0, maxHeadTranslation = 0;
    const seenStates = new Set();
    const contactFrame = run.advanceUntil((state, metrics) => {
      seenStates.add(state.state);
      checkFixedNeckAndHead(run, metrics);
      maxPitch = Math.max(maxPitch, Math.abs(metrics.cervical.neckPitch - run.rest.neck.rotation.x));
      maxNeckTranslation = Math.max(maxNeckTranslation, metrics.cervical.baseTranslationError);
      maxHeadTranslation = Math.max(maxHeadTranslation, metrics.cervical.skullTranslationError);
      assert.ok(metrics.bodyBounds.max.z <= 2.1 + 1e-6, `bill/assembly crossed front cage plane at rail ${normalizedX}`);
      return state.state === 'contact' && metrics.contact;
    }, 12);
    const targetX = contactFrame.state.lookTarget?.x ?? contactFrame.state.goal?.x;
    const radial = Math.hypot(contactFrame.metrics.contactPoint[0] - targetX, contactFrame.metrics.contactPoint[2] - 2.1);
    assert.ok(Math.abs(radial - 0.021) <= 0.008, `rail ${normalizedX}: contact radius ${radial}m is outside 0.021±0.008m`);
    assert.ok(contactFrame.metrics.contactPoint[2] >= 2.079 - 0.008, 'contact is not on the measured front-bar surface');
    assert.ok(maxPitch <= .65 + 1e-6, `rail ${normalizedX}: neck articulation exceeded the bound`);
    assert.ok(seenStates.has('strike') && seenStates.has('contact'), `rail ${normalizedX}: strike/contact sequence incomplete`);

    let maxJaw = 0, maxRightWing = 0, maxRightElbow = 0, maxLeftWing = 0;
    const finish = run.advanceUntil((state, metrics) => {
      checkFixedNeckAndHead(run, metrics);
      maxJaw = Math.max(maxJaw, Math.abs(run.nodes.jaw.rotation.x));
      maxRightWing = Math.max(maxRightWing, Math.abs(run.nodes['right-mantle'].rotation.x));
      maxRightElbow = Math.max(maxRightElbow, Math.abs(run.nodes['right-wing-shield'].rotation.x));
      maxLeftWing = Math.max(maxLeftWing, Math.abs(run.nodes['left-mantle'].rotation.x));
      return ['recover', 'agitated', 'settle', 'watch'].includes(state.state);
    }, 4);
    assert.ok(maxJaw > .02, 'visitor strike did not articulate the jaw');
    assert.ok(maxRightWing > maxLeftWing, 'shield drive lost its asymmetric shoulder motion');
    assert.ok(maxRightElbow > .05, 'shield drive did not articulate the elbow');
    checkFixedNeckAndHead(run);
    contacts.push({
      normalizedX, targetX, root: contactFrame.metrics.root,
      contactPoint: contactFrame.metrics.contactPoint, radial,
      maxPitch, maxNeckTranslation, maxHeadTranslation,
      maxJaw, maxRightWing, maxRightElbow, maxLeftWing,
      finishedState: finish.state.state,
    });
    run.mechanisms.dispose();
  }
  return { rails: contacts, noTelescoping: true, allThreeRailsContacted: true };
}

function verifyMakerChannels() {
  const channels = {};
  for (const id of ['leg', 'wing', 'tail', 'neck', 'jaw']) {
    const run = createRun();
    run.machine.setEra('maker');
    run.mechanisms.setEra('maker');
    run.advanceFor(.2);
    const rootBefore = run.motion.metrics().root;
    assert.equal(run.machine.setArticulation(id, 1), true, `${id} control rejected in Maker`);
    run.advanceFor(.8);
    const m = run.motion.metrics();
    assert.deepEqual(m.root, rootBefore, `${id} moved the anchored Maker root`);
    assert.ok(m.maxFootError < .002, `${id} control destabilized the support solve`);
    const tail = run.model.getObjectByName('compact-articulated-tail');
    const visible = {
      leg: m.feet[0].target[1] - m.feet[1].target[1] > .14,
      wing: run.nodes['right-mantle'].rotation.x < -.3,
      tail: Boolean(tail && tail.rotation.x < -.2),
      neck: run.nodes.neck.rotation.y < -.4,
      jaw: run.nodes.jaw.rotation.x > .3,
    }[id];
    assert.ok(visible, `${id} control did not move its visible linkage`);
    channels[id] = { applied: m.actualArticulation[id], visible, tailPivot: id === 'tail' ? tail.name : null };
    run.mechanisms.dispose();
  }
  return { channels, rootRemainsFixed: true };
}

function verifyMechanicTurn() {
  const run = createRun();
  run.machine.setEra('mechanic');
  run.mechanisms.setEra('mechanic');
  run.advanceFor(.2);
  assert.equal(run.machine.requestRoutine(), true);
  let maxYaw = 0, maxFootError = 0;
  run.advanceFor(12);
  const metrics = run.motion.metrics();
  maxYaw = Math.abs(metrics.root.yaw);
  maxFootError = metrics.maxFootError;
  checkFixedNeckAndHead(run, metrics);
  assert.ok(maxYaw > 1, `Mechanic segmented turn only reached ${maxYaw}rad`);
  assert.ok(metrics.steps >= 6, `Mechanic produced only ${metrics.steps} steps in 12s`);
  assert.equal(metrics.contact, false, 'Mechanic must not inherit Builder cage contact');
  run.mechanisms.dispose();
  return { maxYaw, steps: metrics.steps, maxFootError, routineRunning: run.machine.getSnapshot().routineRunning };
}

function verifyPowerInspectionLanding() {
  const run = createRun();
  assert.equal(run.machine.requestPowerMove('jump'), true);
  const airborne = run.advanceUntil((state, metrics) => metrics.powerMove?.kind === 'jump' && metrics.powerMove.phase > .3, 5);
  checkFixedNeckAndHead(run, airborne.metrics);
  run.machine.setInspection(true);
  const inspectedAfterJump = run.advanceUntil(state => state.inspection && !state.powerMove, 5);
  assert.equal(inspectedAfterJump.state.inspection, true);
  assert.ok(run.motion.feedback().settled, 'jump inspection opened before grounded landing');
  checkFixedNeckAndHead(run);

  run.machine.setInspection(false);
  run.advanceUntil(state => state.canReach, 3);
  assert.equal(run.machine.requestPowerMove('thrust'), true);
  const drive = run.advanceUntil((state, metrics) => metrics.powerMove?.kind === 'thrust' && metrics.powerMove.phase > .3, 5);
  checkFixedNeckAndHead(run, drive.metrics);
  run.machine.setInspection(true);
  const inspectedAfterThrust = run.advanceUntil(state => state.inspection && !state.powerMove, 5);
  assert.equal(inspectedAfterThrust.state.inspection, true);
  assert.ok(run.motion.feedback().settled, 'thrust inspection opened before settled pose');
  checkFixedNeckAndHead(run);
  run.mechanisms.dispose();
  return {
    jumpPhaseAtRequest: airborne.metrics.powerMove.phase,
    jumpInspectionWaitedForLanding: true,
    thrustPhaseAtRequest: drive.metrics.powerMove.phase,
    thrustInspectionWaitedForSettle: true,
  };
}

async function main() {
  const bytes = await readFile(MODEL_PATH);
  OUTPUT.modelSha256 = createHash('sha256').update(bytes).digest('hex');
  OUTPUT.modelBytes = bytes.byteLength;
  const buffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
  template = await loadRigidValidation(bytes);
  assert.ok(template.scene, 'GLB parse returned no scene');
  check('three-front-rails-use-articulated-cervical-contact-through-recovery', verifyThreeRailContact);
  check('maker-five-controls-have-visible-structural-response', verifyMakerChannels);
  check('mechanic-turn-retains-grounded-motion-without-builder-contact', verifyMechanicTurn);
  check('jump-and-thrust-inspection-wait-for-safe-pose', verifyPowerInspectionLanding);
  OUTPUT.status = OUTPUT.checks.every(item => item.status === 'passed') ? 'passed' : 'failed';
  OUTPUT.report = REPORT_PATH;
  await mkdir(dirname(REPORT_PATH), { recursive: true });
  await writeFile(REPORT_PATH, `${JSON.stringify(OUTPUT, null, 2)}\n`);
  console.log(`${OUTPUT.status}: ${OUTPUT.checks.filter(item => item.status === 'passed').length}/${OUTPUT.checks.length} checks`);
  if (OUTPUT.status !== 'passed') {
    for (const item of OUTPUT.checks.filter(item => item.status === 'failed')) console.error(`${item.name}: ${item.error.split('\n')[0]}`);
    process.exitCode = 1;
  }
}

await main();
