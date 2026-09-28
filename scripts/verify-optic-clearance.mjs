import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, relative, resolve } from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';
import { loadRigidValidation } from './load-rigid-validation.mjs';

// Fixed-rest proper triangle-crossing diagnostic for Builder lens surfaces.
// It reports intersections for review; it cannot decide whether lens/bearing
// intersection is intentional machined-seat adjacency.
const options = { model: '', expectedSha256: '', out: '', label: 'optic-clearance' };
const flags = new Map([
  ['--model', 'model'],
  ['--expected-sha256', 'expectedSha256'],
  ['--out', 'out'],
  ['--label', 'label'],
]);
for (let i = 2; i < process.argv.length; i += 1) {
  const flag = process.argv[i];
  assert.ok(flags.has(flag), `Unknown option: ${flag}`);
  const value = process.argv[i + 1];
  assert.ok(value && !value.startsWith('--'), `Missing value for ${flag}`);
  options[flags.get(flag)] = value;
  i += 1;
}
assert.ok(options.model, '--model is required.');
assert.match(options.expectedSha256, /^[a-f0-9]{64}$/i, '--expected-sha256 must be a SHA-256 digest.');
assert.ok(options.out, '--out is required; report writes are exclusive.');

const modelPath = resolve(options.model);
const outputPath = resolve(options.out);
const bytes = await readFile(modelPath);
const modelSha256 = createHash('sha256').update(bytes).digest('hex');
assert.equal(modelSha256, options.expectedSha256.toLowerCase(), 'Declared model SHA-256 does not match input.');
const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const expectedOutputDir = resolve(repoRoot, 'assets/audit/alignment-v6', `optic-clearance-${modelSha256.slice(0, 12)}`);
assert.equal(dirname(outputPath), expectedOutputDir,
  `Output must be in this model's unique audit directory: ${relative(repoRoot, expectedOutputDir)}`);

const { scene: model } = await loadRigidValidation(bytes);
const head = model.getObjectByName('head');
const cranialCover = model.getObjectByName('cranial-cover');
const builderOptics = model.getObjectByName('builder-optics');
const jaw = model.getObjectByName('jaw');
assert.ok(head && cranialCover && builderOptics && jaw, 'GLB must retain head, cranial-cover, builder-optics, and jaw pivots.');

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

model.updateMatrixWorld(true);
const modelInverse = model.matrixWorld.clone().invert();
const activeLenses = [];
builderOptics.traverse(object => {
  if (!object.isMesh) return;
  const data = object.userData || {};
  if (data.region === 'optic' && data.surfaceRole === 'optic'
      && data.constructionClass === 'advanced-system'
      && data.exteriorEras === 'builder') activeLenses.push(object);
});
assert.ok(activeLenses.length > 0, 'No Builder-only active optic meshes found beneath builder-optics.');

const fixedTargets = [];
head.traverse(object => {
  if (!object.isMesh || isDescendantOf(object, builderOptics) || isDescendantOf(object, jaw)) return;
  const data = object.userData || {};
  const headOrCrownPlate = data.region === 'head' && data.surfaceRole === 'plate'
    && (isDescendantOf(object, cranialCover) || isDescendantOf(object, head));
  const opticBearing = data.region === 'optic' && data.surfaceRole === 'bearing';
  if (headOrCrownPlate || opticBearing) fixedTargets.push(object);
});
assert.ok(fixedTargets.some(mesh => mesh.userData?.region === 'head' && mesh.userData?.surfaceRole === 'plate'),
  'No fixed head/crown plate descendants selected.');
assert.ok(fixedTargets.some(mesh => mesh.userData?.region === 'optic' && mesh.userData?.surfaceRole === 'bearing'),
  'No fixed optic-bearing surfaces selected.');
assert.ok(!fixedTargets.some(mesh => mesh.userData?.region === 'optic' && mesh.userData?.surfaceRole === 'recess'),
  'Passive optic housing/recess must remain excluded from active-lens comparison.');

function trianglesFor(mesh) {
  const geometry = mesh.geometry;
  const positions = geometry.attributes.position;
  const index = geometry.index;
  const count = index ? index.count : positions.count;
  assert.equal(count % 3, 0, `Non-triangle geometry in ${mesh.name}`);
  const matrix = modelInverse.clone().multiply(mesh.matrixWorld);
  const result = [];
  for (let i = 0; i < count; i += 3) {
    const vertices = [0, 1, 2].map(j => new THREE.Vector3()
      .fromBufferAttribute(positions, index ? index.getX(i + j) : i + j)
      .applyMatrix4(matrix));
    if (new THREE.Triangle(...vertices).getArea() < 1e-12) continue;
    result.push({ vertices, box: new THREE.Box3().setFromPoints(vertices), name: mesh.name, index: i / 3 });
  }
  return result;
}

const cellSize = 0.025;
function triangleKeys(box) {
  const keys = [];
  for (let x = Math.floor(box.min.x / cellSize); x <= Math.floor(box.max.x / cellSize); x += 1) {
    for (let y = Math.floor(box.min.y / cellSize); y <= Math.floor(box.max.y / cellSize); y += 1) {
      for (let z = Math.floor(box.min.z / cellSize); z <= Math.floor(box.max.z / cellSize); z += 1) {
        keys.push(`${x},${y},${z}`);
      }
    }
  }
  return keys;
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

// Positive and negative controls for the same proper-crossing kernel.
const planeTriangle = { vertices: [new THREE.Vector3(-1, -1, 0), new THREE.Vector3(1, -1, 0), new THREE.Vector3(0, 1, 0)] };
const crossingTriangle = { vertices: [new THREE.Vector3(0, -0.5, -1), new THREE.Vector3(0, -0.5, 1), new THREE.Vector3(0, 0.5, 0)] };
const separatedTriangle = { vertices: crossingTriangle.vertices.map(point => point.clone().add(new THREE.Vector3(0, 0, 3))) };
const positiveFixtureContacts = crossing(planeTriangle, crossingTriangle).length;
const negativeFixtureContacts = crossing(planeTriangle, separatedTriangle).length;
assert.ok(positiveFixtureContacts > 0, 'Positive crossing fixture was not detected.');
assert.equal(negativeFixtureContacts, 0, 'Separated negative fixture produced a crossing.');

const targetTriangles = fixedTargets.flatMap(trianglesFor);
const lensTriangles = activeLenses.flatMap(trianglesFor);
assert.ok(targetTriangles.length > 0 && lensTriangles.length > 0, 'Selected mesh triangle inventory is empty.');
const fixedGrid = new Map();
targetTriangles.forEach((triangle, i) => {
  for (const key of triangleKeys(triangle.box)) {
    if (!fixedGrid.has(key)) fixedGrid.set(key, []);
    fixedGrid.get(key).push(i);
  }
});

let testedCandidatePairs = 0;
let crossingTrianglePairs = 0;
const pairCounts = new Map();
const examples = [];
for (const lens of lensTriangles) {
  const candidates = new Set(triangleKeys(lens.box).flatMap(key => fixedGrid.get(key) || []));
  for (const candidateId of candidates) {
    const target = targetTriangles[candidateId];
    if (!lens.box.intersectsBox(target.box)) continue;
    testedCandidatePairs += 1;
    const points = crossing(lens, target);
    if (!points.length) continue;
    crossingTrianglePairs += 1;
    const name = `${lens.name} / ${target.name}`;
    pairCounts.set(name, (pairCounts.get(name) || 0) + 1);
    if (examples.length < 64) examples.push({
      activeLensMesh: lens.name,
      activeLensTriangle: lens.index,
      fixedTargetMesh: target.name,
      fixedTargetTriangle: target.index,
      fixedTargetRole: fixedTargets.find(mesh => mesh.name === target.name)?.userData?.surfaceRole,
      pointInModelSpace: points[0].toArray(),
    });
  }
}

const runtime = { node: process.version, platform: process.platform, architecture: process.arch };
const validatorPath = fileURLToPath(import.meta.url);
const report = {
  generatedAt: new Date().toISOString(),
  label: options.label,
  gitHead: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: repoRoot, encoding: 'utf8' }).trim(),
  model: { path: relative(repoRoot, modelPath), bytes: bytes.length, sha256: modelSha256, expectedSha256: options.expectedSha256 },
  validatorSha256: createHash('sha256').update(await readFile(validatorPath)).digest('hex'),
  runtime,
  scope: 'One fixed-rest pose from the declared GLB. Every Builder-only mesh below builder-optics with region=optic and surfaceRole=optic is compared against fixed head/crown meshes with region=head and surfaceRole=plate plus fixed region=optic, surfaceRole=bearing meshes. Moving jaw descendants and passive optic housings/recesses are excluded. Proper segment/triangle crossings only.',
  kernelSelfTest: {
    positiveCrossingFixture: { status: 'passed', properCrossingContacts: positiveFixtureContacts },
    separatedNegativeFixture: { status: 'passed', properCrossingContacts: negativeFixtureContacts },
  },
  fixedRest: {
    head: { path: parentPath(head), position: head.position.toArray(), rotation: head.rotation.toArray() },
    cranialCover: { path: parentPath(cranialCover), position: cranialCover.position.toArray(), rotation: cranialCover.rotation.toArray() },
    builderOptics: { path: parentPath(builderOptics), position: builderOptics.position.toArray(), rotation: builderOptics.rotation.toArray() },
  },
  comparedMeshes: {
    activeLensMeshes: activeLenses.map(mesh => ({ name: mesh.name, parentPath: parentPath(mesh), region: mesh.userData.region,
      surfaceRole: mesh.userData.surfaceRole, constructionClass: mesh.userData.constructionClass,
      exteriorEras: mesh.userData.exteriorEras, triangleCount: trianglesFor(mesh).length })),
    fixedHeadCrownPlateAndOpticBearingMeshes: fixedTargets.map(mesh => ({ name: mesh.name, parentPath: parentPath(mesh),
      region: mesh.userData.region, surfaceRole: mesh.userData.surfaceRole, exteriorEras: mesh.userData.exteriorEras,
      triangleCount: trianglesFor(mesh).length })),
    excludedPassiveOpticHousingMeshes: (() => {
      const excluded = [];
      head.traverse(mesh => {
        if (mesh.isMesh && mesh.userData?.region === 'optic' && mesh.userData?.surfaceRole === 'recess') {
          excluded.push({ name: mesh.name, parentPath: parentPath(mesh), reason: 'passive housing/recess excluded by scope' });
        }
      });
      return excluded;
    })(),
    excludedMovingJawMeshes: (() => {
      const excluded = [];
      jaw.traverse(mesh => {
        if (mesh.isMesh) excluded.push({ name: mesh.name, parentPath: parentPath(mesh),
          reason: 'jaw articulation is outside the fixed head/crown comparison scope' });
      });
      return excluded;
    })(),
  },
  comparison: {
    restPoseOnly: true,
    movingLensTriangleCount: lensTriangles.length,
    fixedTargetTriangleCount: targetTriangles.length,
    testedCandidatePairs,
    crossingTrianglePairs,
    exactIntersectingMeshPairs: [...pairCounts.entries()].map(([meshPair, triangles]) => ({ meshPair, crossingTrianglePairs: triangles }))
      .sort((a, b) => a.meshPair.localeCompare(b.meshPair)),
    examples,
    interpretation: pairCounts.size
      ? 'Crossings detected and listed for review. Lens/optic-bearing crossings may represent intentional machined-seat adjacency; this report does not classify design intent or automatically mark them as a defect.'
      : 'No proper crossings detected in this selected fixed-rest mesh comparison. This does not establish a clearance gap or confirm artistic fit.',
  },
  limits: [
    'Fixed-rest geometry comparison only; no articulation, animation, dynamic clearance, force, or contact simulation.',
    'Proper segment/triangle crossings only; coplanar contact, shared boundaries, near-clearance distance, and complete containment are not tested.',
    'All crossings are reported for review. Intentional machined-seat adjacency between active lens and optic bearing is not automatically a failure.',
    'Passive optic housing/recess meshes are excluded by design; the comparison does not cover every head surface or every possible pair.',
    'This geometric diagnostic does not establish artistic likeness, exposed-surface quality, final geometry, owner acceptance, or runtime WebGL appearance.',
  ],
};

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, { flag: 'wx' });
console.log(JSON.stringify({ label: report.label, modelSha256, outputPath,
  activeLensMeshes: activeLenses.map(mesh => mesh.name), fixedTargetMeshes: fixedTargets.length,
  status: pairCounts.size ? 'crossings-detected-review-required' : 'no-proper-crossings-detected',
  testedCandidatePairs, crossingTrianglePairs, exactIntersectingMeshPairs: report.comparison.exactIntersectingMeshPairs,
  fixtures: 'positive and separated negative passed' }));
