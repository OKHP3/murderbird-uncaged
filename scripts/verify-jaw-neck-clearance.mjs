import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';
import { loadRigidValidation } from './load-rigid-validation.mjs';

// Sampled jaw/neck triangle crossings only. This is a pose stress matrix, not
// an exhaustive collision solver or a set of simultaneous runtime poses.
const defaults = {
  model: 'assets/models/uncaged-alignment-v4/murderbird-alignment-v4.glb',
  expectedSha256: '',
  out: 'assets/audit/alignment-v5/clearance-6b0e59540145/jaw-neck-v4.json',
  label: 'model',
};
const options = { ...defaults };
const names = new Map([
  ['--model', 'model'],
  ['--expected-sha256', 'expectedSha256'],
  ['--out', 'out'],
  ['--label', 'label'],
]);
for (let i = 0; i < process.argv.length - 2; i += 1) {
  const flag = process.argv[i + 2];
  if (!names.has(flag)) throw new Error(`Unknown option: ${flag}`);
  const value = process.argv[i + 3];
  if (!value || value.startsWith('--')) throw new Error(`Missing value for ${flag}`);
  options[names.get(flag)] = value;
  i += 1;
}

const modelPath = resolve(options.model);
const outputPath = resolve(options.out);
assert.ok(options.expectedSha256, '--expected-sha256 is required to bind this run to the declared GLB.');
const bytes = await readFile(modelPath);
const modelSha256 = createHash('sha256').update(bytes).digest('hex');
assert.equal(modelSha256, options.expectedSha256, 'Declared GLB hash mismatch.');

const { scene: model } = await loadRigidValidation(bytes);
const head = model.getObjectByName('head');
const jaw = model.getObjectByName('jaw');
const neck = model.getObjectByName('neck');
assert.ok(head && jaw && neck, 'GLB must retain named head, jaw, and neck pivots.');

function isDescendantOf(object, ancestor) {
  for (let current = object; current; current = current.parent) {
    if (current === ancestor) return true;
  }
  return false;
}

function parentPath(object) {
  const path = [];
  for (let current = object; current; current = current.parent) path.unshift(current.name || current.type);
  return path;
}

const movingMeshes = [];
jaw.traverse(object => { if (object.isMesh) movingMeshes.push(object); });
const neckOwnedMeshes = [];
neck.traverse(object => {
  if (!object.isMesh || object.userData?.region !== 'neck'
      || !['plate', 'frame'].includes(object.userData?.surfaceRole)) return;
  if (isDescendantOf(object, head)) return;
  neckOwnedMeshes.push(object);
});
const excludedHeadDescendantNeckPlates = [];
neck.traverse(object => {
  if (object.isMesh && object.userData?.region === 'neck'
      && ['plate', 'frame'].includes(object.userData?.surfaceRole)
      && isDescendantOf(object, head)) excludedHeadDescendantNeckPlates.push(object);
});
assert.ok(movingMeshes.length, 'No jaw-descendant moving meshes found.');
assert.ok(neckOwnedMeshes.some(mesh => mesh.userData.surfaceRole === 'plate'), 'No neck-owned plate meshes outside head descendants found.');

model.updateMatrixWorld(true);
const modelInverse = model.matrixWorld.clone().invert();
const fixedTriangles = neckOwnedMeshes.flatMap(mesh => trianglesFor(mesh, modelInverse));
assert.ok(fixedTriangles.length, 'Neck structural triangle inventory is empty.');

const cell = 0.025;
function triangleKeys(box) {
  const result = [];
  for (let x = Math.floor(box.min.x / cell); x <= Math.floor(box.max.x / cell); x += 1) {
    for (let y = Math.floor(box.min.y / cell); y <= Math.floor(box.max.y / cell); y += 1) {
      for (let z = Math.floor(box.min.z / cell); z <= Math.floor(box.max.z / cell); z += 1) {
        result.push(`${x},${y},${z}`);
      }
    }
  }
  return result;
}

function trianglesFor(mesh, rootInverse) {
  const result = [];
  const positions = mesh.geometry.attributes.position;
  const index = mesh.geometry.index;
  const matrix = rootInverse.clone().multiply(mesh.matrixWorld);
  const count = index ? index.count : positions.count;
  for (let i = 0; i < count; i += 3) {
    const vertices = [0, 1, 2].map(j => new THREE.Vector3()
      .fromBufferAttribute(positions, index ? index.getX(i + j) : i + j)
      .applyMatrix4(matrix));
    if (new THREE.Triangle(...vertices).getArea() < 1e-12) continue;
    result.push({ vertices, box: new THREE.Box3().setFromPoints(vertices), name: mesh.name, index: i / 3 });
  }
  return result;
}

function crossing(first, second) {
  const contacts = [];
  const point = new THREE.Vector3();
  const ray = new THREE.Ray();
  for (const [from, to] of [[first, second], [second, first]]) {
    for (let i = 0; i < 3; i += 1) {
      const a = from.vertices[i];
      const b = from.vertices[(i + 1) % 3];
      const direction = b.clone().sub(a);
      const length = direction.length();
      if (length < 1e-8) continue;
      ray.set(a, direction.divideScalar(length));
      if (!ray.intersectTriangle(...to.vertices, false, point)) continue;
      const distance = point.distanceTo(a);
      if (distance > 0.00001 && distance < length - 0.00001) contacts.push(point.clone());
    }
  }
  return contacts;
}

// Keep the crossing implementation honest with one known crossing and one
// separated pair before evaluating either candidate.
const fixture = { vertices: [new THREE.Vector3(-1, -1, 0), new THREE.Vector3(1, -1, 0), new THREE.Vector3(0, 1, 0)] };
const through = { vertices: [new THREE.Vector3(0, -0.5, -1), new THREE.Vector3(0, -0.5, 1), new THREE.Vector3(0, 0.5, 0)] };
assert.ok(crossing(fixture, through).length > 0, 'Crossing kernel failed its intersecting fixture.');
assert.equal(crossing(fixture, { vertices: through.vertices.map(v => v.clone().add(new THREE.Vector3(0, 0, 3))) }).length, 0,
  'Crossing kernel rejected its separated fixture.');

const headRest = head.rotation.clone();
const jawRest = jaw.rotation.clone();
const pitches = [0, -0.32, -0.65];
const yaws = [-0.35, 0, 0.35];
const jawOpenings = [0, 0.16, 0.32];
const fixedGrid = new Map();
fixedTriangles.forEach((triangle, i) => {
  for (const key of triangleKeys(triangle.box)) {
    if (!fixedGrid.has(key)) fixedGrid.set(key, []);
    fixedGrid.get(key).push(i);
  }
});

const samples = [];
for (const pitch of pitches) {
  for (const yaw of yaws) {
    for (const jawOpen of jawOpenings) {
      head.rotation.copy(headRest);
      head.rotation.x += pitch;
      head.rotation.y += yaw;
      jaw.rotation.copy(jawRest);
      jaw.rotation.x += jawOpen;
      model.updateMatrixWorld(true);
      const jawTriangles = movingMeshes.flatMap(mesh => trianglesFor(mesh, modelInverse));
      assert.ok(jawTriangles.length, 'Sampled jaw triangle inventory is empty.');
      let crossingTrianglePairs = 0;
      let testedCandidatePairs = 0;
      const meshPairs = {};
      const examples = [];
      for (const moving of jawTriangles) {
        const candidates = new Set(triangleKeys(moving.box).flatMap(key => fixedGrid.get(key) || []));
        for (const id of candidates) {
          const fixed = fixedTriangles[id];
          if (!moving.box.intersectsBox(fixed.box)) continue;
          testedCandidatePairs += 1;
          const points = crossing(moving, fixed);
          if (!points.length) continue;
          crossingTrianglePairs += 1;
          const pairName = `${moving.name} / ${fixed.name}`;
          meshPairs[pairName] = (meshPairs[pairName] || 0) + 1;
          if (examples.length < 16) examples.push({
            movingMesh: moving.name,
            movingTriangle: moving.index,
            fixedMesh: fixed.name,
            fixedTriangle: fixed.index,
            pointInModelSpace: points[0].toArray(),
          });
        }
      }
      samples.push({ pitch, yaw, jawOpen, movingTriangles: jawTriangles.length, fixedTriangles: fixedTriangles.length,
        testedCandidatePairs, crossingTrianglePairs, intersectingMeshPairs: Object.keys(meshPairs).length, meshPairs, examples });
    }
  }
}
head.rotation.copy(headRest);
jaw.rotation.copy(jawRest);
model.updateMatrixWorld(true);

const crossedSamples = samples.filter(sample => sample.crossingTrianglePairs > 0);
const runtimePaths = [
  'src/scene/presence-exhibit.js',
  'src/scene/era-motion.js',
  'scripts/load-rigid-validation.mjs',
  'scripts/verify-alignment-v4-jaw-sweep.mjs',
  'package.json',
  'package-lock.json',
];
const selfPath = fileURLToPath(import.meta.url);
const runtimeHashes = Object.fromEntries(await Promise.all([...runtimePaths.map(async path => [path,
  createHash('sha256').update(await readFile(path)).digest('hex')]), [
  'scripts/verify-jaw-neck-clearance.mjs', createHash('sha256').update(await readFile(selfPath)).digest('hex'),
]]));
const output = {
  generatedAt: new Date().toISOString(),
  label: options.label,
  gitHead: execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(),
  workingTreeSnapshot: 'Local QA diagnostic; model/source status is recorded separately by its declared hashes.',
  model: { path: modelPath, bytes: bytes.length, sha256: modelSha256, expectedSha256: options.expectedSha256 },
  runtime: { node: process.version, platform: process.platform, architecture: process.arch },
  runtimeHashes,
  pivotTransforms: {
    head: { parentPath: parentPath(head), position: head.position.toArray(), rotation: headRest.toArray() },
    jaw: { parentPath: parentPath(jaw), position: jaw.position.toArray(), rotation: jawRest.toArray() },
    neck: { parentPath: parentPath(neck), position: neck.position.toArray(), rotation: neck.rotation.toArray() },
  },
  poseMatrix: { pitches, yaws, jawOpenings, combinationCount: samples.length,
    note: 'Stress combinations for clearance sensitivity; not asserted to be simultaneous production-animation poses.' },
  kernelSelfTest: { intersectingFixture: 'passed', separatedFixture: 'passed' },
  comparedMeshes: {
    jawDescendantMovingMeshes: movingMeshes.map(mesh => ({ name: mesh.name, parentPath: parentPath(mesh), region: mesh.userData?.region,
      surfaceRole: mesh.userData?.surfaceRole, triangleCount: trianglesFor(mesh, modelInverse).length })),
    neckOwnedMeshesOutsideHeadDescendants: neckOwnedMeshes.map(mesh => {
      const bounds = new THREE.Box3().setFromObject(mesh);
      return { name: mesh.name, parentPath: parentPath(mesh), region: mesh.userData?.region,
        surfaceRole: mesh.userData?.surfaceRole, exteriorEras: mesh.userData?.exteriorEras,
        triangleCount: trianglesFor(mesh, modelInverse).length,
        modelSpaceBounds: { min: bounds.min.toArray(), max: bounds.max.toArray(), size: bounds.getSize(new THREE.Vector3()).toArray() } };
    }),
    excludedHeadDescendantNeckMeshes: excludedHeadDescendantNeckPlates.map(mesh => ({ name: mesh.name, parentPath: parentPath(mesh),
      surfaceRole: mesh.userData?.surfaceRole })),
  },
  summary: { status: crossedSamples.length ? 'crossings-detected' : 'no-sampled-crossings-detected',
    sampledPoseCount: samples.length, crossingPoseCount: crossedSamples.length,
    totalCrossingTrianglePairs: samples.reduce((sum, sample) => sum + sample.crossingTrianglePairs, 0),
    uniqueIntersectingMeshPairs: [...new Set(samples.flatMap(sample => Object.keys(sample.meshPairs)))].sort() },
  samples,
  limits: [
    'Proper segment/triangle crossings sampled at these 27 discrete poses only; coplanar contact and full containment are not certified.',
    'Stress pitch/yaw/jaw-opening combinations are not guaranteed to occur simultaneously in the runtime animation.',
    'No force/contact proof, continuous between-sample clearance, all-pairs collision test, GPU/WebGL rendering, or artistic acceptance.',
    'Neck comparison includes region=neck structural meshes with surfaceRole plate or frame; this is still pair filtering and excludes non-structural neck objects and head-descendant objects.',
    'The v5 candidate changes the jaw hinge; runtime sources are hash-recorded for context, but this diagnostic applies transforms directly to the declared GLB nodes.',
  ],
};
await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(output, null, 2)}\n`, { flag: 'wx' });
console.log(JSON.stringify({ label: output.label, status: output.summary.status, modelSha256, outputPath,
  sampledPoseCount: samples.length, crossingPoseCount: crossedSamples.length,
  totalCrossingTrianglePairs: output.summary.totalCrossingTrianglePairs, uniqueIntersectingMeshPairs: output.summary.uniqueIntersectingMeshPairs }));
if (crossedSamples.length) process.exitCode = 1;
