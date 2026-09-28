#!/usr/bin/env node
/** Capture actual exported-rig matrices at selected runtime pose extrema.
 * This is a deterministic kinematic pose sample, not a collision or physics test.
 */
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { loadRigidValidation } from './load-rigid-validation.mjs';
import { createEraController } from '../src/scene/era-controller.js';
import { createEraMotion } from '../src/scene/era-motion.js';
import { createEraMechanisms } from '../src/scene/era-mechanisms.js';
import { applyInspectionPose } from '../src/scene/inspection-pose.js';

const MODEL_PATH = process.env.UNCAGED_MODEL || 'assets/models/uncaged-alignment-v7/murderbird-alignment-v7.glb';
const EXPECTED_MODEL_SHA256 = process.env.UNCAGED_EXPECTED_MODEL_SHA256 || '1c82874b86af6b493ac380536de6af72a30fafa3a4b0ebb3d8790f56ffc03018';
const OUT_DIR = resolve(process.env.UNCAGED_AUDIT || 'assets/audit/neutral-runtime-clearance-poses-v1');
const REPORT_PATH = resolve(OUT_DIR, 'pose-snapshot.json');
const DT = 1 / 60;
const CONTROL_NODES = ['body','neck','head','jaw','breastplate','cranial-cover','winding-drive','power-core','processing','industrial-repairs','builder-optics','left-mantle','right-mantle','left-wing-shield','right-wing-shield'];
const INPUTS = [
  MODEL_PATH, 'package-lock.json', 'scripts/load-rigid-validation.mjs',
  'src/scene/era-controller.js', 'src/scene/presence-state.js',
  'src/scene/era-motion.js', 'src/scene/rigid-leg-kinematics.js',
  'src/scene/cervical-articulation.js',
  'src/scene/inspection-pose.js', 'src/scene/era-mechanisms.js', fileURLToPath(import.meta.url),
];
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const finiteMatrix = matrix => matrix.elements.every(Number.isFinite);
const rounds = value => Math.round(value * 1e9) / 1e9;
const vector = v => v.toArray().map(rounds);
const matrix = m => m.elements.map(rounds);
const jsonClone = value => JSON.parse(JSON.stringify(value));

const modelBytes = await readFile(MODEL_PATH);
const modelSha256 = sha(modelBytes);
assert.equal(modelSha256, EXPECTED_MODEL_SHA256, `model SHA256 mismatch: expected ${EXPECTED_MODEL_SHA256}, got ${modelSha256}`);
const template = await loadRigidValidation(modelBytes);
assert.ok(template.scene, 'declared GLB parsed without a scene');
if (template.scene.getObjectByName('cervical-upper')) CONTROL_NODES.push('cervical-upper');

function makeRig(seed = 927) {
  const model = clone(template.scene);
  model.updateMatrixWorld(true);
  const named = Object.fromEntries(CONTROL_NODES.map(name => [name, model.getObjectByName(name)]));
  assert.ok(Object.values(named).every(Boolean), 'declared GLB lacks one or more active motion nodes');
  const rest = Object.fromEntries(CONTROL_NODES.map(name => [name, {
    position: named[name].position.clone(), rotation: named[name].rotation.clone(),
  }]));
  const motion = createEraMotion(model, named, rest);
  const controller = createEraController({ seed });
  const scene = new THREE.Scene(); scene.add(model); scene.updateMatrixWorld(true);
  const mechanisms = createEraMechanisms({ scene, model, nodes: named, rest });
  let activeEra = controller.getSnapshot().era;
  mechanisms.setEra(activeEra);
  function step(dt = DT) {
    const state = controller.update(dt, motion.feedback());
    if (state.era !== activeEra) { activeEra = state.era; mechanisms.setEra(activeEra); }
    for (const name of CONTROL_NODES) {
      named[name].position.copy(rest[name].position);
      named[name].rotation.copy(rest[name].rotation);
    }
    motion.tick(dt, state);
    mechanisms.tick(dt, state, motion.driveMetrics(), { open: 0, separation: 0 });
    scene.updateMatrixWorld(true);
    return { state: jsonClone(state), metrics: jsonClone(motion.metrics()), time: rounds(motion.metrics().time) };
  }
  return { scene, model, named, rest, motion, controller, step };
}

function allTransformNodes(rig) {
  const rows = [];
  const pathOf = object => {
    const parts = [];
    for (let current = object; current && current !== rig.model.parent; current = current.parent) {
      parts.push(current.name || current.type);
    }
    return parts.reverse().join('/');
  };
  rig.model.traverse(object => {
    if (!object.name) return;
    object.updateMatrix();
    object.updateWorldMatrix(true, false);
    assert.ok(finiteMatrix(object.matrix) && finiteMatrix(object.matrixWorld), `non-finite transform at ${object.name}`);
    rows.push({
      name: object.name,
      path: pathOf(object),
      parent: object.parent?.name || null,
      kind: object.isMesh ? 'mesh' : 'transform',
      localMatrix: matrix(object.matrix),
      worldMatrix: matrix(object.matrixWorld),
      position: vector(object.position),
      quaternion: object.quaternion.toArray().map(rounds),
      scale: vector(object.scale),
    });
  });
  assert.ok(rows.length > 0);
  return rows;
}

function propertyHash(row) {
  return sha(Buffer.from(JSON.stringify({
    name: row.name, path: row.path, parent: row.parent, kind: row.kind,
    position: row.position, quaternion: row.quaternion, scale: row.scale,
  })));
}

function capture(rig, id, category, frame, evidence = {}) {
  rig.scene.updateMatrixWorld(true);
  const pivotMatrices = allTransformNodes(rig);
  return {
    id, category, elapsedSeconds: frame.time,
    controller: frame.state,
    motionMetrics: frame.metrics,
    evidence,
    pivotMatrices,
  };
}

function changedNodes(restPose, pose, names = null, tolerance = 1e-7) {
  const before = new Map(restPose.pivotMatrices.map(row => [row.path, row]));
  return pose.pivotMatrices.filter(row => (!names || names.includes(row.name))
    && row.worldMatrix.some((n, i) => Math.abs(n - before.get(row.path).worldMatrix[i]) > tolerance))
    .map(row => row.name);
}

function freshRun(era = 'builder') {
  const rig = makeRig();
  assert.equal(rig.controller.setEra(era), true);
  const initial = rig.step();
  return { ...rig, initial };
}

function sampleMaker(name, value, id, expectedWorldChanged) {
  const rig = freshRun('maker');
  const restPose = capture(rig, `${id}-rest`, 'maker-rest', rig.initial);
  assert.equal(rig.controller.setArticulation(name, value), true, `Maker control ${name} was rejected`);
  let frame;
  for (let i = 0; i < 120; i += 1) frame = rig.step();
  assert.equal(frame.state.era, 'maker');
  assert.equal(frame.state.articulation[name], value);
  const pose = capture(rig, id, 'maker-articulation', frame, { requestedControl: name, requestedValue: value });
  const changed = changedNodes(restPose, pose, expectedWorldChanged);
  pose.evidence.changedExpectedNodes = changed;
  assert.ok(changed.length > 0, `${id}: runtime produced no change in expected exported node(s)`);
  if (name === 'wing') {
    pose.evidence.leftMantleWorldUnchanged = !changedNodes(restPose, pose, ['left-mantle']).includes('left-mantle');
    assert.equal(pose.evidence.leftMantleWorldUnchanged, true, 'Maker wing control unexpectedly articulated the left mantle');
  }
  return pose;
}

function sampleEncounter() {
  const rig = freshRun('builder');
  assert.equal(rig.controller.requestReach({ x: 0, y: 1.4 }), true, 'Builder did not accept the reachable visitor input');
  const samples = {};
  let strikePeak = null, contact = null;
  for (let i = 0; i < 2400; i += 1) {
    const frame = rig.step();
    const s = frame.state, m = frame.metrics;
    if (!samples.attention && s.state === 'notice' && s.visitorPresent) {
      assert.ok(Math.abs(m.pose.gaze) > .01 || Math.abs(m.root.yaw) > .01 || s.lookTarget,
        'attention state was entered without a visitor target');
      samples.attention = capture(rig, 'advanced-attention', 'advanced-visitor-response', frame,
        { observedState: s.state, visitorPresent: s.visitorPresent, lookTarget: s.lookTarget });
    }
    if (s.state === 'strike' && (!strikePeak || m.pose.extension > strikePeak.evidence.maxExtension)) {
      strikePeak = capture(rig, 'advanced-strike-peak', 'advanced-visitor-response', frame,
        { observedState: s.state, actionKind: s.actionKind, observedPhase: s.phase, maxExtension: m.pose.extension });
    }
    if (s.state === 'contact' && (!contact || m.pose.extension >= contact.evidence.extension)) contact = capture(rig,
      'advanced-contact', 'advanced-visitor-response', frame,
      { observedState: s.state, actionKind: s.actionKind, observedPhase: s.phase,
        motionContact: m.contact, extension: m.pose.extension });
    if (s.state === 'recover' && !samples.recovery) samples.recovery = capture(rig,
      'advanced-recovery-entry', 'advanced-visitor-response', frame,
      { observedState: s.state, actionKind: s.actionKind, observedPhase: s.phase, extension: m.pose.extension });
    if (strikePeak && contact && samples.recovery && samples.attention) break;
  }
  assert.ok(samples.attention, 'visitor attention/notice state was never observed');
  assert.ok(strikePeak, 'visitor strike state was never observed');
  assert.ok(contact, 'visitor contact state was never observed');
  assert.ok(samples.recovery, 'visitor recovery state was never observed');
  samples.strike = strikePeak;
  samples.contact = contact;
  assert.ok(samples.strike.evidence.maxExtension > .35, 'strike did not extend actual rig');
  assert.ok(samples.contact.evidence.extension > .5, 'contact did not retain actual extension');
  return samples;
}

function sampleMakerNeckJaw() {
  const rig = freshRun('maker');
  assert.equal(rig.controller.setArticulation('neck', 1), true);
  assert.equal(rig.controller.setArticulation('jaw', 1), true);
  let frame;
  for (let i = 0; i < 120; i += 1) frame = rig.step();
  assert.equal(frame.metrics.actualArticulation.neck, 1);
  assert.equal(frame.metrics.actualArticulation.jaw, 1);
  return capture(rig, 'maker-neck-and-jaw-combined', 'maker-articulation', frame,
    { requestedControls: { neck: 1, jaw: 1 }, individuallyExposedControlsCombined: true });
}

function samplePowerMove(kind, targetPhase, controllerStageExpected, motionStageExpected) {
  const rig = freshRun('builder');
  if (kind === 'thrust') {
    let ready = null;
    for (let i = 0; i < 2400; i += 1) {
      const frame = rig.step();
      if (['pace','boundary'].includes(frame.state.state)
          && Math.hypot(frame.metrics.root.x, frame.metrics.root.z + .25) > .08
          && Math.abs(frame.metrics.root.yaw) > .04) { ready = frame; break; }
    }
    assert.ok(ready, 'runtime did not reach a moved and turned Builder pose for thrust');
  } else rig.step();
  assert.equal(rig.controller.requestPowerMove(kind), true, `${kind} was rejected at a reachable public state`);
  let frame, selected = null;
  for (let i = 0; i < 1200; i += 1) {
    frame = rig.step();
    const move = frame.state.powerMove;
    if (move?.kind === kind && Math.abs(move.phase - targetPhase) <= DT / move.duration + .004) selected = frame;
    if (move?.kind === kind && move.phase >= targetPhase) { if (!selected) selected = frame; break; }
  }
  assert.ok(selected?.state.powerMove, `${kind} did not become active`);
  assert.equal(selected.state.powerMove.kind, kind);
  assert.equal(selected.state.powerMove.stage, controllerStageExpected);
  assert.equal(selected.metrics.powerMove?.stage, motionStageExpected);
  const id = `advanced-${kind}-${motionStageExpected}`;
  return capture(rig, id, 'advanced-power-move', selected, {
    requestAccepted: true, observedKind: selected.state.powerMove.kind,
    phase: selected.state.powerMove.phase, controllerStage: selected.state.powerMove.stage,
    motionStage: selected.metrics.powerMove?.stage,
    height: selected.metrics.powerMove?.height ?? null,
  });
}

function sampleMechanicTurn() {
  const rig = freshRun('mechanic');
  assert.equal(rig.controller.requestRoutine(), true, 'Mechanic routine was rejected');
  let selected = null;
  for (let i = 0; i < 1500; i += 1) {
    const frame = rig.step();
    if (frame.metrics.mechanicalStage === 'release' && frame.metrics.mechanicalPhase > .35 && frame.metrics.mechanicalPhase < .65) {
      selected = frame; break;
    }
  }
  assert.ok(selected, 'Mechanic routine did not reach an observed segment turn/release phase');
  assert.ok(Math.abs(selected.metrics.root.yaw) > .01 || selected.metrics.steps > 0,
    'Mechanic release phase had no turn or completed segment evidence');
  return capture(rig, 'mechanic-segment-turn-release', 'mechanic-routine', selected, {
    routineAccepted: true, mechanicalStage: selected.metrics.mechanicalStage,
    mechanicalPhase: selected.metrics.mechanicalPhase, camAngle: selected.metrics.camAngle,
    root: selected.metrics.root, steps: selected.metrics.steps,
  });
}

function sampleInspection(open, separation) {
  const rig = makeRig();
  rig.model.position.set(0, 0, 0); rig.model.rotation.set(0, 0, 0);
  rig.model.updateMatrixWorld(true);
  const restTransforms = Object.fromEntries(CONTROL_NODES.map(name => [name, {
    position: rig.named[name].position.clone(), rotation: rig.named[name].rotation.clone(),
  }]));
  applyInspectionPose(rig.named, restTransforms, open, separation);
  rig.scene.updateMatrixWorld(true);
  const frame = { state: rig.controller.getSnapshot(), metrics: rig.motion.metrics(), time: 0 };
  return capture(rig, `inspection-open-${open}-separation-${separation}`, 'inspection-transform', frame,
    { open, separation, helper: 'production applyInspectionPose(nodes, rest, open, separation)' });
}

const baselineRig = freshRun('builder');
const restPose = capture(baselineRig, 'runtime-rest', 'runtime-rest', baselineRig.initial,
  { era: 'builder', state: baselineRig.initial.state.state });
const makerSamples = [
  sampleMaker('leg', 1, 'maker-leg-control', ['left-foot']),
  sampleMaker('tail', 1, 'maker-tail-control', ['compact-articulated-tail']),
  sampleMaker('neck', 1, 'maker-neck-control', ['neck','head']),
  sampleMaker('jaw', 1, 'maker-jaw-control', ['jaw']),
  sampleMaker('wing', 1, 'maker-wing-control-right-mantle', ['right-mantle','right-wing-shield']),
];
// Head follows neck as a parent transform; the five documented control
// channels are leg, wing, tail, neck, and jaw. Wing remains asymmetric.
const unsupportedMakerControls = [
  { requestedAnatomy: 'independent head articulation', status: 'not-exposed', evidence: 'No head key in ARTICULATION_PARTS; head follows neck world transform.' },
  { requestedAnatomy: 'independent left-mantle control', status: 'not-exposed', evidence: 'The single wing channel is coupled asymmetrically by runtime motion.' },
];
const encounter = sampleEncounter();
const power = [
  samplePowerMove('jump', .43, 'flight', 'airborne'),
  samplePowerMove('thrust', .52, 'hold', 'brace'),
];
const mechanic = sampleMechanicTurn();
const inspection = [
  sampleInspection(0, 0), sampleInspection(.25, 0), sampleInspection(.5, 0),
  sampleInspection(.75, 0), sampleInspection(1, 0),
  sampleInspection(1, .5), sampleInspection(1, 1),
];

const allPoses = [restPose, ...makerSamples, sampleMakerNeckJaw(), ...Object.values(encounter), ...power, mechanic, ...inspection];
for (const pose of allPoses) {
  assert.equal(pose.pivotMatrices.length, restPose.pivotMatrices.length, `${pose.id}: transform node inventory changed`);
  assert.ok(pose.pivotMatrices.every(row => row.localMatrix.length === 16 && row.worldMatrix.length === 16));
}
for (const id of ['advanced-strike-peak','advanced-contact','advanced-recovery-entry','advanced-jump-airborne','advanced-thrust-brace']) {
  const pose = allPoses.find(entry => entry.id === id);
  assert.ok(pose, `required actual action sample missing: ${id}`);
  assert.ok(pose.controller.era === 'builder');
}

const sourceHashes = {};
for (const input of INPUTS) sourceHashes[input] = sha(await readFile(input));
const nodeInventory = restPose.pivotMatrices.map(row => ({
  name: row.name, path: row.path, parent: row.parent, kind: row.kind,
  propertySha256: propertyHash(row),
}));
const report = {
  schema: 'neutral-runtime-clearance-poses/v1',
  generatedAt: new Date().toISOString(),
  gitHead: execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(),
  environment: { node: process.version, platform: process.platform, architecture: process.arch },
  model: { path: MODEL_PATH, sha256: modelSha256, bytes: modelBytes.byteLength },
  inputSha256: sourceHashes,
  coordinateConvention: {
    runtime: 'Three.js; Y up; bird forward +Z; matrices are column-major flat 16-element arrays.',
    blenderToRuntime: 'browser=(BlenderX, BlenderZ, -BlenderY); C maps Blender coordinates to runtime; convert a Blender-space transform as C^-1 * M_runtime * C.',
  },
  nodeInventory: { count: nodeInventory.length, nodes: nodeInventory },
  poseCount: allPoses.length,
  poses: allPoses,
  reachableLimits: {
    makerControlsCaptured: ['leg','wing','tail','neck','jaw'],
    makerControlRuntimeLayer: 'createEraMotion plus active createEraMechanisms; tail articulation is applied by createEraMechanisms.tick from motion.driveMetrics().actualArticulation.',
    unsupportedMakerControls,
    inspectionSamplesAreDirectCallsToProductionPoseHelper: true,
    mechanicSegmentTurnSample: 'Captured only after routine returned an observed nonzero mechanical release phase.',
  },
  scope: 'Actual deterministic controller and motion runtime matrices from the declared exported GLB plus production inspection-pose helper. These samples record pose transforms only; they do not test surface intersections, continuous clearance, collision response, physical forces, biological plausibility, browser rendering, or human acceptance.',
};

await mkdir(OUT_DIR, { recursive: true });
await writeFile(REPORT_PATH, `${JSON.stringify(report, null, 2)}\n`, { flag: 'wx' });
const readme = `# Neutral runtime clearance pose snapshot v1\n\nThis immutable receipt stores actual Three.js rig matrices for the declared GLB at bounded runtime samples. Each pose includes the controller state, motion metrics, and every named exported transform node's local and world matrix. Arrays are column-major, as in Three.js. Blender-to-runtime coordinates use \`browser=(BlenderX, BlenderZ, -BlenderY)\`; use \`C^-1 * M_runtime * C\` for transform conversion.\n\nThe Maker runtime has no independent head or left-mantle control: head follows the neck's parent transform, and the single wing control moves the right mantle and shield. Those limits are recorded rather than filled with artificial poses. Inspection values call the production \`applyInspectionPose\` helper at a fixed exported rest pose.\n\nThe samples are deterministic kinematic inputs for later geometry diagnostics. They do not establish collision clearance, continuous swept-volume safety, physical simulation, browser appearance, or owner acceptance. The JSON binds the exact model and source hashes.\n`;
await writeFile(resolve(OUT_DIR, 'README.md'), readme, { flag: 'wx' });
console.log(`captured ${allPoses.length} actual pose snapshots (${nodeInventory.length} named transform nodes), model ${modelSha256}`);
