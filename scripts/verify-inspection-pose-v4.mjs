import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { loadRigidValidation } from './load-rigid-validation.mjs';
import { applyInspectionPose, INSPECTION_EXPLODED_OFFSETS } from '../src/scene/inspection-pose.js';

const MODEL_PATH = process.env.UNCAGED_MODEL || 'assets/models/uncaged-alignment-v3/murderbird-alignment-v3.glb';
const EXPECTED_MODEL_SHA256 = process.env.UNCAGED_EXPECTED_MODEL_SHA256
  || 'c4dc308f77399410368b82443a1b21b9113cfedb258aa055906b4f13c92dda21';
const REPORT_PATH = resolve(process.env.UNCAGED_AUDIT || 'assets/audit/regression-v4', 'inspection-pose-validation.json');
const ERAS = ['maker', 'mechanic', 'builder'];
const NODE_NAMES = [
  'body', 'neck', 'head', 'jaw', 'breastplate', 'cranial-cover', 'winding-drive',
  'power-core', 'processing', 'industrial-repairs', 'builder-optics', 'left-mantle',
  'right-mantle', 'left-wing-shield', 'right-wing-shield',
];
const OUTPUT = {
  generatedAt: new Date().toISOString(),
  model: MODEL_PATH,
  modelDescription: 'declared GLB input',
  expectedModelSha256: EXPECTED_MODEL_SHA256,
  environment: { node: process.version, platform: process.platform, architecture: process.arch },
  checks: [],
};
let template;

function check(name, run) {
  try { OUTPUT.checks.push({ name, status: 'passed', result: run() }); }
  catch (error) { OUTPUT.checks.push({ name, status: 'failed', error: error.stack || error.message }); }
}

function makeRig() {
  const model = clone(template);
  const scene = new THREE.Scene();
  scene.add(model);
  const nodes = Object.fromEntries(NODE_NAMES.map(name => [name, model.getObjectByName(name)]));
  assert.ok(Object.values(nodes).every(Boolean), 'declared GLB is missing a required exported inspection node');
  const rest = Object.fromEntries(NODE_NAMES.map(name => [name, {
    position: nodes[name].position.clone(), rotation: nodes[name].rotation.clone(),
  }]));
  return { scene, model, nodes, rest };
}

function applyEraEligibility(rig, era) {
  // Match the active exhibit's GLB-tag eligibility without importing its
  // WebGL/DOM setup. The tagged meshes are the same objects toggled by
  // presence-exhibit.setEra(); explicit system visibility follows that code.
  rig.model.traverse(object => {
    if (!object.isMesh) return;
    const tags = String(object.userData?.exteriorEras || '').split(',').map(value => value.trim());
    if (tags.some(value => ERAS.includes(value))) object.visible = tags.includes(era);
  });
  rig.nodes['winding-drive'].visible = false;
  rig.nodes['power-core'].visible = era === 'builder';
  rig.nodes.processing.visible = era === 'builder';
  rig.nodes['builder-optics'].visible = era === 'builder';
  rig.nodes['industrial-repairs'].visible = era !== 'maker';
}

function effectiveVisible(object, root) {
  for (let current = object; current && current !== root.parent; current = current.parent) {
    if (!current.visible) return false;
  }
  return true;
}

function eligibleMeshesByOwner(rig, era) {
  return Object.keys(INSPECTION_EXPLODED_OFFSETS).map(name => {
    const owner = rig.nodes[name];
    const meshes = [];
    owner.traverse(object => {
      if (!object.isMesh || !effectiveVisible(object, rig.scene)) return;
      const eras = String(object.userData?.exteriorEras || '').split(',').map(value => value.trim());
      if (eras.includes(era)) meshes.push(object);
    });
    return { name, owner, meshes };
  }).filter(entry => entry.meshes.length > 0);
}

function resetMotionNodeBaseline(rig) {
  // Match the active tick's pre-motion reset and keep the kinematic rig fixed
  // at its exported rest pose so these assertions isolate inspection transforms.
  for (const name of NODE_NAMES) {
    rig.nodes[name].position.copy(rig.rest[name].position);
    rig.nodes[name].rotation.copy(rig.rest[name].rotation);
  }
  rig.model.position.set(0, 0, 0);
  rig.model.rotation.set(0, 0, 0);
  rig.model.updateMatrixWorld(true);
}

function applyAt(rig, open, separation) {
  resetMotionNodeBaseline(rig);
  applyInspectionPose(rig.nodes, rig.rest, open, separation);
  rig.scene.updateMatrixWorld(true);
}

function matrixSnapshot(meshes) {
  return meshes.map(mesh => [mesh.uuid, [...mesh.matrixWorld.elements]]);
}

function vectorChanged(a, b, epsilon = 1e-8) {
  return a.distanceTo(b) > epsilon;
}

function verifyEra(era) {
  const rig = makeRig();
  applyEraEligibility(rig, era);
  const ownerEntries = eligibleMeshesByOwner(rig, era);
  assert.ok(ownerEntries.length >= 6, `${era}: too few eligible exploded mesh owners (${ownerEntries.length})`);
  assert.ok(ownerEntries.every(entry => entry.meshes.length > 0), `${era}: an eligible owner has no eligible descendant meshes`);
  const allMappedMeshes = [...new Set(Object.keys(INSPECTION_EXPLODED_OFFSETS).flatMap(name => {
    const meshes = [];
    rig.nodes[name].traverse(object => { if (object.isMesh) meshes.push(object); });
    return meshes;
  }))];

  const cycles = [];
  for (let cycle = 1; cycle <= 5; cycle += 1) {
    applyAt(rig, 0, 0);
    const assembledWorldMatrices = matrixSnapshot(allMappedMeshes);
    const assembledBreastQuaternion = rig.nodes.breastplate.quaternion.clone();
    const assembledCoverY = rig.nodes['cranial-cover'].position.y;

    applyAt(rig, 1, 0);
    assert.ok(rig.nodes.breastplate.quaternion.angleTo(assembledBreastQuaternion) > 1,
      `${era} cycle ${cycle}: opening did not rotate the exported breastplate`);
    if (rig.nodes.breastplate.userData?.inspectionAxis === 'x') {
      assert.ok(rig.nodes.breastplate.rotation.x > 1 && Math.abs(rig.nodes.breastplate.rotation.y) < 1e-8,
        `${era} cycle ${cycle}: the bottom-hinged cover did not open about its declared local X axis`);
    }
    assert.ok(Math.abs(rig.nodes['cranial-cover'].position.y - assembledCoverY) >= .079,
      `${era} cycle ${cycle}: opening did not raise the exported cranial cover`);
    const openOwnerPositions = Object.fromEntries(ownerEntries.map(({ name, owner }) => [name, owner.position.clone()]));
    const openWorldMatrices = new Map(matrixSnapshot(ownerEntries.flatMap(entry => entry.meshes)));
    const separationEvidence = [];

    for (const separation of [0, 0.5, 1]) {
      applyAt(rig, 1, separation);
      const changedOwners = [];
      const changedMeshes = new Set();
      if (separation > 0) {
        for (const { name, owner, meshes } of ownerEntries) {
          assert.ok(vectorChanged(owner.position, openOwnerPositions[name]),
            `${era} cycle ${cycle} ${name}: local exported owner transform did not change at separation ${separation}`);
          changedOwners.push(name);
          for (const mesh of meshes) {
            const prior = openWorldMatrices.get(mesh.uuid);
            assert.ok(prior, `${era} cycle ${cycle}: missing world-matrix baseline for ${mesh.name}`);
            assert.notDeepEqual(mesh.matrixWorld.elements, prior,
              `${era} cycle ${cycle} ${mesh.name}: eligible mesh world transform did not change at separation ${separation}`);
            changedMeshes.add(mesh.uuid);
          }
        }
      }
      separationEvidence.push({ separation, changedEligibleOwners: changedOwners,
        changedUniqueEligibleMeshes: changedMeshes.size });
    }

    applyAt(rig, 0, 0);
    assert.deepEqual(matrixSnapshot(allMappedMeshes), assembledWorldMatrices,
      `${era} cycle ${cycle}: descendant mesh world matrices did not restore exactly after reset and zero pose`);
    assert.deepEqual(rig.nodes.breastplate.quaternion.toArray(), assembledBreastQuaternion.toArray(),
      `${era} cycle ${cycle}: breastplate rotation did not return to assembled pose`);
    assert.equal(rig.nodes['cranial-cover'].position.y, assembledCoverY,
      `${era} cycle ${cycle}: cranial-cover position did not return to assembled pose`);
    cycles.push({ cycle, eligibleMeshOwners: ownerEntries.map(({ name, meshes }) => ({ name, meshCount: meshes.length })),
      separationEvidence, exactDescendantWorldMatrixRestoration: true });
  }
  return { era, cyclesPerEra: cycles.length, eligibleMeshOwnerCount: ownerEntries.length,
    mappedMeshCount: allMappedMeshes.length, cycles, baseline: 'fixed exported rest pose; no motion tick or collision inference' };
}

const modelBytes = await readFile(MODEL_PATH);
const modelSha256 = createHash('sha256').update(modelBytes).digest('hex');
assert.equal(modelSha256, EXPECTED_MODEL_SHA256, `model SHA256 mismatch: expected ${EXPECTED_MODEL_SHA256}, got ${modelSha256}`);
OUTPUT.modelSha256 = modelSha256;

const selfPath = fileURLToPath(import.meta.url);
const sourcePaths = [
  'src/scene/inspection-pose.js',
  'src/scene/presence-exhibit.js',
  'src/scene/era-motion.js',
  'scripts/load-rigid-validation.mjs',
  'package-lock.json',
  selfPath,
];
OUTPUT.sourceSha256 = Object.fromEntries(await Promise.all(sourcePaths.map(async path => {
  const absolutePath = path === selfPath ? path : resolve(path);
  const label = path === selfPath ? 'scripts/verify-inspection-pose-v4.mjs' : path;
  return [label, createHash('sha256').update(await readFile(absolutePath)).digest('hex')];
})));

const gltf = await loadRigidValidation(modelBytes);
assert.ok(gltf.scene, 'GLB parse returned no scene');
template = gltf.scene;
check('active-exported-inspection-pose-restores-eligible-mesh-world-matrices', () => {
  return Object.fromEntries(ERAS.map(era => [era, verifyEra(era)]));
});
OUTPUT.status = OUTPUT.checks.every(item => item.status === 'passed') ? 'passed' : 'failed';
OUTPUT.report = REPORT_PATH;
OUTPUT.scope = [
  'Calls the same pure inspection-pose helper used by the active presence-exhibit runtime.',
  'Uses actual declared GLB descendants at a fixed exported rest pose.',
  'Per-era exteriorEras eligibility is mirrored in the fixture from presence-exhibit.setEra; the verifier does not test that runtime wiring. Model geometry and extras compatibility remain bounded to the declared GLB and recorded hash.',
  'Verifies local owner movement at 50% and 100%, eligible mesh world-matrix movement, opening transforms, and exact reassembly world-matrix restoration.',
  'Does not model UI easing, animation timing, collision, rendering, GPU/WebGL, or artistic acceptance.',
];
await mkdir(dirname(REPORT_PATH), { recursive: true });
await writeFile(REPORT_PATH, `${JSON.stringify(OUTPUT, null, 2)}\n`, { flag: 'wx' });
console.log(`${OUTPUT.status}: ${OUTPUT.checks.filter(item => item.status === 'passed').length}/${OUTPUT.checks.length} checks`);
if (OUTPUT.status !== 'passed') {
  for (const item of OUTPUT.checks.filter(entry => entry.status === 'failed')) console.error(`${item.name}: ${item.error.split('\n')[0]}`);
  process.exitCode = 1;
}
