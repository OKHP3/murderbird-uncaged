import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
import * as THREE from '../../../../../../node_modules/three/build/three.module.js';
import { loadRigidValidation } from '../../../../../../scripts/load-rigid-validation.mjs';
import { createEraMotion } from '../../../../../../src/scene/era-motion.js';
import { createEraController } from '../../../../../../src/scene/era-controller.js';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../../../../..');
const runtimeDir = path.dirname(new URL(import.meta.url).pathname);
const receipt = JSON.parse(await readFile(path.join(runtimeDir, 'runtime-derivative.json'), 'utf8'));
const modelPath = path.resolve(root, receipt.outputGlb.path);
const bytes = await readFile(modelPath);
const modelSha256 = createHash('sha256').update(bytes).digest('hex');
assert.equal(modelSha256, receipt.outputGlb.sha256, 'Runtime derivative changed');
const { scene: template } = await loadRigidValidation(bytes);
const NODES = ['body','neck','head','jaw','breastplate','cranial-cover','winding-drive','power-core','processing','industrial-repairs','builder-optics','left-mantle','right-mantle','left-wing-shield','right-wing-shield'];
const DT = 1 / 60;
const GRID = 0.025;
const model = template;
const nodeMap = Object.fromEntries(NODES.map(name => [name, model.getObjectByName(name)]));
assert.ok(Object.values(nodeMap).every(Boolean), 'Runtime derivative missing a required motion node');
const rest = Object.fromEntries(NODES.map(name => [name, { position: nodeMap[name].position.clone(), rotation: nodeMap[name].rotation.clone() }]));
const motion = createEraMotion(model, nodeMap, rest);
const controller = createEraController({ seed: 927 });

function step() {
  const state = controller.update(DT, motion.feedback());
  for (const name of NODES) {
    nodeMap[name].position.copy(rest[name].position);
    nodeMap[name].rotation.copy(rest[name].rotation);
  }
  motion.tick(DT, state);
  model.updateMatrixWorld(true);
  return { state: controller.getSnapshot(), metrics: motion.metrics() };
}
function capture() {
  model.updateMatrixWorld(true);
  return model.clone(true);
}
const poses = [];
step();
assert.equal(controller.getSnapshot().era, 'builder');
poses.push({ label: 'planted-neutral', trigger: 'initial settled Builder pose, before any action', tree: capture(), state: controller.getSnapshot(), metrics: motion.metrics() });
assert.equal(controller.requestPowerMove('jump'), true, 'Could not request jump from the settled Builder pose');
let jumpPeak = null, jumpLanding = null, jumpFinished = false, jumpStarted = false;
for (let frame = 0; frame < 400; frame++) {
  const frameState = step();
  const power = frameState.metrics.powerMove;
  if (power?.kind === 'jump') jumpStarted = true;
  if (power?.kind === 'jump' && (!jumpPeak || power.height > jumpPeak.metrics.powerMove.height)) {
    jumpPeak = { label: 'jump-flight-peak', trigger: 'sample with maximum reported jump height', tree: capture(), state: frameState.state, metrics: frameState.metrics };
  }
  if (power?.kind === 'jump' && power.stage === 'landing' && !jumpLanding) {
    jumpLanding = { label: 'jump-landing', trigger: 'first runtime landing stage sample', tree: capture(), state: frameState.state, metrics: frameState.metrics };
  }
  if (jumpStarted && !frameState.state.powerMove && !frameState.state.powerMovePending && frameState.metrics.settled) { jumpFinished = true; break; }
}
assert.ok(jumpFinished && jumpPeak && jumpLanding, 'Could not sample jump peak and landing stages');
poses.push(jumpPeak, jumpLanding);
let watch = false;
for (let frame = 0; frame < 600; frame++) {
  const frameState = step();
  if (frameState.state.state === 'watch' && frameState.metrics.settled) { watch = true; break; }
}
assert.ok(watch, 'Builder did not return to settled watch after jump');
assert.equal(controller.requestClawAction(), true, 'Could not request claw action from settled Builder watch');
let contact = null, recovery = null, maxAnglePose = null, maxToeAngle = -1;
const actionStages = new Set();
for (let frame = 0; frame < 720; frame++) {
  const frameState = step();
  const claw = frameState.metrics.clawAction;
  if (claw) {
    actionStages.add(claw.stage);
    const toeAngle = Math.max(...frameState.metrics.feet.flatMap(foot => foot.digits.map(digit => Math.abs(digit.angle))));
    if (toeAngle > maxToeAngle) {
      maxToeAngle = toeAngle;
      maxAnglePose = { label: 'claw-toe-angle-extreme', trigger: 'largest absolute runtime toe hinge angle during the measured action',
        tree: capture(), state: frameState.state, metrics: frameState.metrics };
    }
    if (claw.stage === 'contact' && claw.phase >= 0.90 && !contact) {
      contact = { label: 'claw-contact', trigger: 'first contact-stage sample at or above 90% phase', tree: capture(), state: frameState.state, metrics: frameState.metrics };
    }
    if (claw.stage === 'recovery' && claw.phase >= 0.50 && !recovery) {
      recovery = { label: 'claw-recovery', trigger: 'first recovery-stage sample at or above 50% phase', tree: capture(), state: frameState.state, metrics: frameState.metrics };
    }
  }
  if (!frameState.state.clawAction && !frameState.metrics.clawAction && frame > 0) break;
}
assert.ok(contact && recovery && maxAnglePose, 'Could not sample contact, recovery and maximum toe articulation');
assert.deepEqual(['approach','lift','contact','scrape','release','recovery'].filter(stage => !actionStages.has(stage)), [],
  'Runtime action did not visit all expected claw phases');
poses.push(maxAnglePose, contact, recovery);

function parentOwner(mesh) {
  for (let node = mesh; node; node = node.parent) {
    if (/^(left|right)-digit-[123]-(proximal|distal)$/.test(node.name)) return node.name;
  }
  return null;
}
function triangleList(mesh) {
  const position = mesh.geometry.attributes.position;
  const index = mesh.geometry.index;
  const count = index ? index.count : position.count;
  const matrix = mesh.matrixWorld;
  const result = [];
  for (let offset = 0; offset < count; offset += 3) {
    const vertices = [0,1,2].map(j => new THREE.Vector3().fromBufferAttribute(position, index ? index.getX(offset + j) : offset + j).applyMatrix4(matrix));
    const triangle = new THREE.Triangle(...vertices);
    if (triangle.getArea() < 1e-12) continue;
    result.push({ vertices, box: new THREE.Box3().setFromPoints(vertices), mesh: mesh.name, triangle: offset / 3 });
  }
  return result;
}
function keys(box) {
  const result = [];
  for (let x = Math.floor(box.min.x / GRID); x <= Math.floor(box.max.x / GRID); x++)
    for (let y = Math.floor(box.min.y / GRID); y <= Math.floor(box.max.y / GRID); y++)
      for (let z = Math.floor(box.min.z / GRID); z <= Math.floor(box.max.z / GRID); z++) result.push(`${x},${y},${z}`);
  return result;
}
function crossings(first, second) {
  const contacts = [];
  const ray = new THREE.Ray(), point = new THREE.Vector3();
  for (const [from, to] of [[first, second], [second, first]]) {
    for (let i = 0; i < 3; i++) {
      const a = from.vertices[i], b = from.vertices[(i + 1) % 3];
      const direction = b.clone().sub(a), length = direction.length();
      if (length < 1e-8) continue;
      ray.set(a, direction.divideScalar(length));
      if (ray.intersectTriangle(...to.vertices, false, point)) {
        const distance = point.distanceTo(a);
        if (distance > 0.00001 && distance < length - 0.00001) contacts.push(point.clone());
      }
    }
  }
  return contacts;
}
const fixture = { vertices: [new THREE.Vector3(-1, -1, 0), new THREE.Vector3(1, -1, 0), new THREE.Vector3(0, 1, 0)] };
const through = { vertices: [new THREE.Vector3(0, -0.5, -1), new THREE.Vector3(0, -0.5, 1), new THREE.Vector3(0, 0.5, 0)] };
assert.ok(crossings(fixture, through).length > 0, 'Crossing kernel failed its intersecting fixture');
assert.equal(crossings(fixture, { vertices: through.vertices.map(v => v.clone().add(new THREE.Vector3(0, 0, 3))) }).length, 0,
  'Crossing kernel failed its separated fixture');

function meshList(root) {
  const output = [];
  root.traverse(mesh => { if (mesh.isMesh) output.push(mesh); });
  return output;
}
function classify(guard, other) {
  const go = parentOwner(guard), oo = parentOwner(other);
  if (/^(left|right)-foot-foot-plate$/.test(other.name)) return 'digit-guard-to-instep-review';
  const g = go?.match(/^(left|right)-digit-(\d+)-(proximal|distal)$/);
  const o = oo?.match(/^(left|right)-digit-(\d+)-(proximal|distal)$/);
  if (g && o && g[1] === o[1] && g[2] === o[2]) return 'same-digit-articulated-neighbor-review';
  if (g && o && g[1] === o[1]) return 'neighbor-digit-review';
  return 'other-foot-geometry';
}

const poseReports = [];
for (const pose of poses) {
  const sampleModel = pose.tree;
  sampleModel.updateMatrixWorld(true);
  const meshes = meshList(sampleModel);
  const guards = meshes.filter(mesh => mesh.userData.geometryStatus === 'native digit-envelope study proposal' &&
    mesh.userData.region === 'foot' && mesh.userData.surfaceRole === 'plate');
  const targets = meshes.filter(mesh => mesh.userData.region === 'foot' &&
    mesh.userData.surfaceRole === 'plate' && (parentOwner(mesh) || /^(left|right)-foot-foot-plate$/.test(mesh.name)));
  assert.equal(guards.length, 12, `Expected 12 guard groups in ${pose.label}`);
  assert.equal(targets.length, 14, `Expected 12 digit guards and two instep groups in ${pose.label}`);
  const intendedPairs = guards.flatMap(guard => targets.filter(target => target !== guard &&
    target.name.startsWith(parentOwner(guard).split('-digit-')[0]) &&
    (!parentOwner(target) || guard.name < target.name)).map(target => [guard.name, target.name]));
  assert.equal(intendedPairs.length, 42, `Expected 42 unique same-foot guard pairs in ${pose.label}`);
  const guardTris = guards.map(mesh => ({ mesh, triangles: triangleList(mesh) }));
  const targetTris = targets.map(mesh => ({ mesh, triangles: triangleList(mesh) }));
  const targetGrid = new Map();
  targetTris.forEach((group, groupIndex) => group.triangles.forEach((triangle, triangleIndex) => {
    const id = { groupIndex, triangleIndex };
    for (const key of keys(triangle.box)) {
      if (!targetGrid.has(key)) targetGrid.set(key, []);
      targetGrid.get(key).push(id);
    }
  }));
  const pairCounts = new Map(), examples = [], guardFloor = {};
  let testedPairs = 0, crossingTrianglePairs = 0;
  for (const group of guardTris) {
    const owner = parentOwner(group.mesh);
    const ownerFoot = owner?.split('-digit-')[0];
    const minY = new THREE.Box3().setFromObject(group.mesh, true).min.y;
    guardFloor[group.mesh.name] = Number(minY.toFixed(6));
    for (const moving of group.triangles) {
      const candidates = new Set(keys(moving.box).flatMap(key => targetGrid.get(key) || []));
      for (const id of candidates) {
        const fixedGroup = targetTris[id.groupIndex], fixed = fixedGroup.triangles[id.triangleIndex];
        if (!fixedGroup.mesh.name.startsWith(ownerFoot) || fixedGroup.mesh === group.mesh ||
            (parentOwner(fixedGroup.mesh) && group.mesh.name >= fixedGroup.mesh.name) ||
            !moving.box.intersectsBox(fixed.box)) continue;
        testedPairs++;
        const points = crossings(moving, fixed);
        if (!points.length) continue;
        crossingTrianglePairs++;
        const kind = classify(group.mesh, fixedGroup.mesh);
        const key = `${kind} :: ${group.mesh.name} / ${fixedGroup.mesh.name}`;
        pairCounts.set(key, (pairCounts.get(key) || 0) + 1);
        if (examples.length < 32) examples.push({ classification: kind,
          guardMesh: group.mesh.name, targetMesh: fixedGroup.mesh.name,
          guardOwner: owner, targetOwner: parentOwner(fixedGroup.mesh),
          guardTriangle: moving.triangle, targetTriangle: fixed.triangle,
          pointModelSpace: points[0].toArray().map(value => Number(value.toFixed(6))) });
      }
    }
  }
  const feet = pose.metrics.feet.map(foot => ({ side: foot.side, groundMin: foot.groundMin, swinging: foot.swinging,
    toeAngles: foot.digits.map(digit => ({ name: digit.name, angle: digit.angle })) }));
  poseReports.push({ label: pose.label, trigger: pose.trigger,
    runtimeState: { era: pose.state.era, state: pose.state.state, powerMove: pose.state.powerMove ?? null,
      clawAction: pose.state.clawAction ?? null, clawMetrics: pose.metrics.clawAction ?? null,
      powerMetrics: pose.metrics.powerMove ?? null, root: pose.metrics.root },
    feet, comparedGuardMeshes: guardTris.map(group => ({ name: group.mesh.name, owner: parentOwner(group.mesh), triangleCount: group.triangles.length,
      minWorldY: guardFloor[group.mesh.name] })),
    comparedTargetMeshes: targetTris.filter(group => group.mesh.name.startsWith('left-') || group.mesh.name.startsWith('right-'))
      .map(group => ({ name: group.mesh.name, owner: parentOwner(group.mesh), region: group.mesh.userData.region,
        surfaceRole: group.mesh.userData.surfaceRole, triangleCount: group.triangles.length })),
    intendedMeshPairs: intendedPairs, sampledTrianglePairs: testedPairs, crossingTrianglePairs,
    crossingPairs: [...pairCounts].map(([pair, count]) => ({ pair, crossingTrianglePairs: count })), examples,
    limits: ['Discrete sampled production-rig poses only; no continuous motion or exhaustive all-object collision test.',
      'Proper segment/triangle crossings only; coplanar contact and full containment are not detected.',
      'Only newly added digit guards against other same-foot digit guards and the existing instep plate are screened.',
      'Instep targets are owner-batched GLB plate meshes; this does not isolate each source instep plate.'] });
}
const output = { generatedAt: new Date().toISOString(), candidate: receipt.outputGlb, modelSha256,
  sourceHashes: Object.fromEntries(await Promise.all(['src/scene/era-motion.js','src/scene/era-controller.js',
    'scripts/load-rigid-validation.mjs','assets/audit/digit-envelope-study-v1/iterations/attempt-03/runtime/diagnose-digit-guard-pairs.mjs']
    .map(async file => [file, createHash('sha256').update(await readFile(path.resolve(root, file))).digest('hex')]))),
  kernel: { method: 'bidirectional triangle-edge ray/triangle segment crossings with 25 mm spatial-grid broad phase', selfTest: 'intersecting fixture passed; separated fixture passed' },
  poseSampling: { sampleCount: poseReports.length, steps: 'actual createEraController + createEraMotion at 60 Hz', capturedLabels: poses.map(({ label, trigger }) => ({ label, trigger })),
    clawActionStagesObserved: [...actionStages] },
  poses: poseReports,
  summary: { poseCount: poseReports.length, guardGroupsPerPose: 12,
    posesWithAnyCrossing: poseReports.filter(pose => pose.crossingTrianglePairs > 0).map(pose => pose.label),
    totalCrossingTrianglePairs: poseReports.reduce((sum, pose) => sum + pose.crossingTrianglePairs, 0),
    guardMinimumWorldY: Object.fromEntries(poseReports.map(pose => [pose.label,
      Math.min(...pose.comparedGuardMeshes.map(mesh => mesh.minWorldY))])) },
  overallLimits: ['This is a bounded diagnostic, not a pass/fail physical collision clearance proof.',
    'Separate from the earlier frame/edge diagnostic; no frame or talon geometry is screened here.',
    'No force, contact pressure, self-collision completeness, browser/WebGL or artistic acceptance.'] };
const out = path.join(runtimeDir, 'toe-guard-pairs.json');
await writeFile(out, `${JSON.stringify(output, null, 2)}\n`, { flag: 'wx' });
console.log(JSON.stringify({ modelSha256, poses: poseReports.map(pose => ({ label: pose.label, pairs: pose.crossingTrianglePairs,
  categories: [...new Set(pose.crossingPairs.map(item => item.pair.split(' :: ')[0]))] })), output: out }));
