import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { createEraMotion } from '../src/scene/era-motion.js';
import { createEraController } from '../src/scene/era-controller.js';

const MODEL_PATH = process.env.UNCAGED_MODEL || 'assets/models/uncaged-structure-v1/murderbird-structure-v1.glb';
const REPORT_PATH = (process.env.UNCAGED_AUDIT || 'assets/audit/structural-reconciliation-v1') + '/motion-validation.json';
const NODE_NAMES = [
  'body', 'neck', 'head', 'jaw', 'breastplate', 'cranial-cover', 'winding-drive',
  'power-core', 'processing', 'industrial-repairs', 'builder-optics', 'left-mantle',
  'right-mantle', 'left-wing-shield', 'right-wing-shield',
];
const OUTPUT = { generatedAt: new Date().toISOString(), model: MODEL_PATH, report: REPORT_PATH, checks: [] };
let template;

function check(name, fn) {
  try {
    OUTPUT.checks.push({ name, status: 'passed', result: fn() });
  } catch (error) {
    OUTPUT.checks.push({ name, status: 'failed', error: error.message });
  }
}

function makeRig() {
  const model = clone(template.scene);
  const nodes = Object.fromEntries(NODE_NAMES.map(name => [name, model.getObjectByName(name)]));
  assert.ok(Object.values(nodes).every(Boolean), 'model is missing required named nodes');
  const rest = Object.fromEntries(NODE_NAMES.map(name => [name, {
    position: nodes[name].position.clone(),
    rotation: nodes[name].rotation.clone(),
  }]));
  const motion = createEraMotion(model, nodes, rest);
  return { model, nodes, rest, motion };
}

function resetPose(nodes, rest) {
  for (const name of NODE_NAMES) {
    nodes[name].position.copy(rest[name].position);
    nodes[name].rotation.copy(rest[name].rotation);
  }
}

function createRun({ seed = 927, dt = 1 / 60 } = {}) {
  const rig = makeRig();
  const machine = createEraController({ seed });
  const tracker = {
    previousState: '', stateTimes: {},
    distance: 0, steps: 0, stepOrder: [], maxFootError: 0,
    maxSupportTargetShift: 0, maxFloorOffset: 0, minGroundY: Infinity, maxGroundY: -Infinity,
    bounds: { minX: Infinity, maxX: -Infinity, minZ: Infinity, maxZ: -Infinity },
    contacts: [], lastFootSteps: { left: 0, right: 0 }, lastTargets: {},
  };
  let time = 0;

  function sample() {
    const state = machine.getSnapshot();
    const metrics = rig.motion.metrics();
    tracker.stateTimes[state.state] = (tracker.stateTimes[state.state] || 0) + dt;
    if (state.state !== tracker.previousState) tracker.previousState = state.state;
    tracker.distance = Math.max(tracker.distance, metrics.distance);
    tracker.maxFootError = Math.max(tracker.maxFootError, ...metrics.feet.map(foot => foot.solveError));
    tracker.bounds.minX = Math.min(tracker.bounds.minX, metrics.bodyBounds.min.x);
    tracker.bounds.maxX = Math.max(tracker.bounds.maxX, metrics.bodyBounds.max.x);
    tracker.bounds.minZ = Math.min(tracker.bounds.minZ, metrics.bodyBounds.min.z);
    tracker.bounds.maxZ = Math.max(tracker.bounds.maxZ, metrics.bodyBounds.max.z);

    for (const foot of metrics.feet) {
      if (!foot.swinging) {
        const floorOffset = Math.abs(foot.groundMin - 0.002);
        tracker.maxFloorOffset = Math.max(tracker.maxFloorOffset, floorOffset);
        tracker.minGroundY = Math.min(tracker.minGroundY, foot.groundMin);
        tracker.maxGroundY = Math.max(tracker.maxGroundY, foot.groundMin);
      }
      const prior = tracker.lastTargets[foot.side];
      if (!foot.swinging && prior && !prior.swinging) {
        const shift = Math.hypot(...foot.target.map((v, i) => v - prior.target[i]));
        tracker.maxSupportTargetShift = Math.max(tracker.maxSupportTargetShift, shift);
      }
      tracker.lastTargets[foot.side] = { target: foot.target, swinging: foot.swinging };
      if (foot.steps > tracker.lastFootSteps[foot.side]) {
        const priorStep = tracker.stepOrder.at(-1);
        const yawDelta = priorStep ? Math.atan2(Math.sin(metrics.root.yaw - priorStep.yaw), Math.cos(metrics.root.yaw - priorStep.yaw)) : 0;
        tracker.stepOrder.push({ side: foot.side, state: state.state, speed: metrics.root.speed, yaw: metrics.root.yaw, yawDelta });
        tracker.lastFootSteps[foot.side] = foot.steps;
      }
    }

    if (state.state === 'contact' || state.state === 'cage-test') {
      if (metrics.contact) {
        const targetX = state.lookTarget?.x ?? state.goal?.x ?? metrics.root.x;
        const radial = Math.hypot(metrics.contactPoint[0] - targetX, metrics.contactPoint[2] - 2.1);
        tracker.contacts.push({ state: state.state, radial, point: metrics.contactPoint, targetX });
      }
    }
    return { state, metrics };
  }

  function step(seconds = dt) {
    const feedback = rig.motion.feedback();
    const state = machine.update(seconds, feedback);
    resetPose(rig.nodes, rig.rest);
    rig.motion.tick(seconds, state);
    time += seconds;
    return { state, metrics: rig.motion.metrics(), time };
  }

  function advanceUntil(predicate, limitSeconds = 20) {
    const maxFrames = Math.ceil(limitSeconds / dt);
    for (let i = 0; i < maxFrames; i += 1) {
      const frame = step(dt);
      sample();
      if (predicate(frame.state, frame.metrics)) return frame;
    }
    assert.fail(`condition not reached within ${limitSeconds}s (state=${machine.getSnapshot().state})`);
  }

  function advanceFor(seconds) {
    const end = time + seconds;
    while (time + 1e-9 < end) {
      const frame = step(Math.min(dt, end - time));
      sample();
    }
  }

  function result() {
    const metrics = rig.motion.metrics();
    return {
      time, endState: machine.getSnapshot().state, stateTimes: tracker.stateTimes,
      distance: metrics.distance, steps: metrics.steps, stepOrder: tracker.stepOrder,
      maxFootError: tracker.maxFootError, maxSupportTargetShift: tracker.maxSupportTargetShift,
      maxFloorOffsetFrom2mm: tracker.maxFloorOffset,
      plantedGroundY: [tracker.minGroundY, tracker.maxGroundY], bounds: tracker.bounds,
      contacts: tracker.contacts,
      endRoot: metrics.root,
      finalFeet: metrics.feet.map(({ side, actual, target, swinging, solveError, groundMin }) => ({ side, actual, target, swinging, solveError, groundMin })),
    };
  }
  return { ...rig, machine, tracker, step, sample, advanceUntil, advanceFor, result, get time() { return time; } };
}

function checkPhysicalEnvelope(run, { requireTravel = false, requireContact = false } = {}) {
  const result = run.result();
  assert.ok(result.maxFootError < 0.002, `foot solve error ${result.maxFootError} m is not below 0.002 m`);
  assert.ok(result.maxSupportTargetShift < 1e-7, `planted foot target shifted ${result.maxSupportTargetShift} m`);
  assert.ok(result.maxFloorOffsetFrom2mm < 0.0015, `planted sole differs from 0.002 m floor by ${result.maxFloorOffsetFrom2mm} m`);
  assert.ok(result.bounds.minX >= -2.9 && result.bounds.maxX <= 2.9, `body exceeded cage x envelope: ${JSON.stringify(result.bounds)}`);
  assert.ok(result.bounds.minZ >= -2.1 && result.bounds.maxZ <= 2.1, `body exceeded cage z envelope: ${JSON.stringify(result.bounds)}`);
  if (requireTravel) {
    assert.ok(result.distance > 3, `root traveled only ${result.distance} m`);
    assert.ok(result.stateTimes.pace > 0 && result.stateTimes.boundary > 0 && result.stateTimes['cage-test'] > 0,
      'unattended cycle omitted pacing, boundary approach, or cage test');
    assert.ok(result.steps > 2, `too few planted steps (${result.steps})`);
    const travelRepeats = [];
    for (let i = 1; i < result.stepOrder.length; i += 1) {
      const previous = result.stepOrder[i - 1], current = result.stepOrder[i];
      if (previous.side === current.side && previous.state === 'pace' && current.state === 'pace'
          && previous.speed > 0.15 && current.speed > 0.15 && Math.abs(current.yawDelta) < 0.1) {
        travelRepeats.push({ index: i, previous, current });
      }
    }
    assert.equal(travelRepeats.length, 0, `same-foot steps during straight loaded travel: ${JSON.stringify(travelRepeats)}`);
  }
  if (requireContact) {
    assert.ok(result.contacts.length > 0, 'no physical bill contact was reported');
    for (const contact of result.contacts) {
      assert.ok(Math.abs(contact.radial - 0.021) <= 0.008,
        `bill contact radius ${contact.radial} m is outside 0.021 ± 0.008 m`);
    }
  }
  return result;
}

function simulate(seconds, dt, seed = 927) {
  const run = createRun({ seed, dt });
  run.advanceFor(seconds);
  const result = checkPhysicalEnvelope(run, { requireTravel: true, requireContact: true });
  return result;
}

function verifyAnimationExport() {
  const model = template.scene;
  const head = model.getObjectByName('head');
  assert.ok(head, 'head node missing');
  assert.ok(template.animations.length > 0, 'GLB exported no animation clips');
  const animation = template.animations[0];
  const mixer = new THREE.AnimationMixer(model);
  const action = mixer.clipAction(animation);
  action.play();
  mixer.setTime(Math.min(0.5, animation.duration));
  const sample = { name: animation.name, duration: animation.duration, tracks: animation.tracks.length, headRotationY: head.rotation.y };
  mixer.stopAllAction();
  mixer.uncacheRoot(model);
  assert.ok(Math.abs(sample.headRotationY) > 0.05, `AnimationMixer head rotation ${sample.headRotationY} rad is not visible`);
  return sample;
}

function testReachAt(x) {
  const run = createRun({ seed: 927, dt: 1 / 60 });
  assert.equal(run.machine.requestReach({ x, y: 0.25 }), true, `reach ${x} not accepted`);
  assert.equal(run.machine.requestReach({ x: -x, y: 0 }), false, 'repeated reach was accepted');
  run.advanceUntil(s => s.state === 'contact', 14);
  const s = run.machine.getSnapshot();
  const target = x < -0.34 ? -1.2 : x > 0.34 ? 1.2 : 0;
  assert.equal(s.goal.x, target, `reach x=${x} mapped to goal ${s.goal.x}, expected ${target}`);
  run.advanceUntil(snap => snap.state === 'recover', 1);
  return checkPhysicalEnvelope(run, { requireContact: true });
}

function testRetreat(preCommit) {
  const run = createRun({ seed: 927 });
  assert.equal(run.machine.requestReach({ x: preCommit ? -0.6 : 0.6 }), true);
  run.advanceUntil(s => s.state === (preCommit ? 'approach' : 'strike'), 10);
  assert.equal(run.machine.requestRetreat(), true);
  if (preCommit) {
    assert.equal(run.machine.getSnapshot().state, 'agitated');
    run.advanceFor(1.2);
    assert.equal(run.tracker.stateTimes.strike || 0, 0, 'pre-commit retreat still struck');
    return checkPhysicalEnvelope(run);
  }
  run.advanceUntil(s => s.state === 'contact', 2);
  run.advanceUntil(s => s.state === 'recover', 1);
  assert.equal(run.machine.getSnapshot().visitorPresent, false);
  return checkPhysicalEnvelope(run, { requireContact: true });
}

function testInspection(fromState) {
  const run = createRun({ seed: 927 });
  if (fromState === 'pace') run.advanceUntil(s => s.state === 'pace', 20);
  else {
    run.machine.requestReach({ x: 0.4 });
    run.advanceUntil(s => s.state === 'strike', 10);
  }
  run.machine.setInspection(true);
  assert.equal(run.machine.getSnapshot().state, 'settle');
  assert.equal(run.machine.getSnapshot().actionKind, null);
  run.advanceUntil(s => s.state === 'inspection', 4);
  const settled = run.motion.feedback().settled;
  assert.equal(settled, true, `inspection opened before grounded settle after ${fromState}`);
  assert.equal(run.machine.getSnapshot().inspection, true);
  run.machine.setInspection(false);
  return checkPhysicalEnvelope(run);
}


function testMaker(){
  const run=createRun();run.machine.setEra('maker');run.advanceFor(1);
  const fixed=run.motion.metrics().root;const head=run.nodes.head.rotation.toArray();run.advanceFor(12);
  assert.deepEqual(run.motion.metrics().root,fixed);assert.deepEqual(run.nodes.head.rotation.toArray(),head);
  assert.equal(run.machine.requestReach({x:0}),false);
  const effects={};
  for(const id of ['leg','wing','tail','neck','jaw']){
    assert(run.machine.setArticulation(id,1));run.advanceFor(1.8);
    const m=run.motion.metrics();assert.deepEqual(m.root,fixed);assert(m.actualArticulation[id]>.99);assert(m.maxFootError<.002);
    effects[id]=m.actualArticulation[id];
    if(id==='leg')assert(m.feet[0].actual[1]-m.feet[1].actual[1]>.14);
    if(id==='jaw')assert(run.nodes.jaw.rotation.x<-.3);
    if(id==='neck')assert(run.nodes.neck.rotation.y<-.4);
    run.machine.setArticulation(id,0);run.advanceFor(1.8);
  }
  run.machine.setArticulation('leg',1);run.advanceFor(.8);run.machine.setInspection(true);
  run.advanceUntil(s=>s.inspection,5);assert(run.motion.feedback().settled);
  assert(run.motion.metrics().actualArticulation.leg<.003);
  return {stationaryRoot:fixed,manualChannels:effects,inspectionGrounded:true};
}
function testMechanic(){
  const run=createRun();run.machine.setEra('mechanic');run.advanceFor(1);assert(run.machine.requestRoutine());
  const stages=new Set(),speeds=[];let maxTurn=0,previousYaw=0;
  for(let i=0;i<60*48;i++){
    const {metrics:m}=run.step();run.sample();stages.add(m.mechanicalStage);speeds.push(m.root.speed);maxTurn=Math.max(maxTurn,Math.abs(m.root.yaw));previousYaw=m.root.yaw;
    assert(m.maxFootError<.002);assert(m.bodyBounds.min.y>-.002);assert(!m.contact);
  }
  assert(run.motion.metrics().distance>.8);assert(maxTurn>1);for(const stage of ['load','release','settle','dwell'])assert(stages.has(stage));
  assert(speeds.filter(v=>v<.001).length>speeds.length*.35);assert(Math.max(...speeds)<.4);
  assert.equal(run.machine.requestReach({x:1}),false);assert.equal(run.machine.getSnapshot().lookTarget,null);
  run.machine.stopRoutine();run.advanceUntil((s,m)=>s.state==='mechanical-ready'&&m.settled,8);
  const stopped=run.motion.metrics().root;run.advanceFor(2);assert.deepEqual(run.motion.metrics().root,stopped);
  run.machine.requestRoutine();run.advanceFor(.8);run.machine.setInspection(true);run.advanceUntil(s=>s.inspection,8);
  assert(run.motion.feedback().settled);assert(run.machine.getSnapshot().energy<1);
  return {distance:run.motion.metrics().distance,steps:run.motion.metrics().steps,camStages:[...stages],maxInstantaneousSpeed:Math.max(...speeds),stationaryFraction:speeds.filter(v=>v<.001).length/speeds.length,turnRadians:maxTurn,energy:run.machine.getSnapshot().energy,inspectionGrounded:true};
}

async function main() {
  const bytes = await readFile(MODEL_PATH);
  const buffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
  template = await new GLTFLoader().parseAsync(buffer, '');
  assert.ok(template.scene, 'GLB parse returned no scene');

  check('exported-head-animation', verifyAnimationExport);
  check('maker-fixed-external-articulation',testMaker);
  check('mechanic-phased-traversal-and-stop',testMechanic);
  for (const [seed, dt] of [[927, 1 / 60], [42, 1 / 60], [2026, 1 / 60], [927, 0.1]]) {
    check(`unattended-${seed}-${dt}`, () => simulate(60, dt, seed));
  }
  for (const x of [-1, 0, 1]) check(`visitor-rail-${x}`, () => testReachAt(x));
  check('retreat-before-commit', () => testRetreat(true));
  check('retreat-after-commit', () => testRetreat(false));
  check('inspection-during-pace', () => testInspection('pace'));
  check('inspection-during-strike', () => testInspection('strike'));

  OUTPUT.status = OUTPUT.checks.every(item => item.status === 'passed') ? 'passed' : 'failed';
  await mkdir(dirname(REPORT_PATH), { recursive: true });
  await writeFile(REPORT_PATH, `${JSON.stringify(OUTPUT, null, 2)}\n`);
  console.log(`${OUTPUT.status}: ${OUTPUT.checks.filter(item => item.status === 'passed').length}/${OUTPUT.checks.length} checks`);
  if (OUTPUT.status !== 'passed') {
    for (const item of OUTPUT.checks.filter(item => item.status === 'failed')) console.error(`${item.name}: ${item.error}`);
    process.exitCode = 1;
  }
}

await main();
