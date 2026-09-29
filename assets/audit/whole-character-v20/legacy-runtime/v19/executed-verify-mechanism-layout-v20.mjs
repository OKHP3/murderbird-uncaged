import assert from 'node:assert/strict';
import { copyFile, mkdir, readFile, writeFile } from 'node:fs/promises';
import { constants as fsConstants } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, isAbsolute, relative, resolve, sep } from 'node:path';
import * as THREE from 'three';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { loadRigidValidation } from './load-rigid-validation.mjs';
import { createEraMechanisms } from '../src/scene/era-mechanisms.js';

const ROOT = resolve('.');
const MODEL = process.env.UNCAGED_MODEL;
const EXPECTED_SHA = process.env.UNCAGED_EXPECTED_MODEL_SHA256;
const AUDIT = process.env.UNCAGED_AUDIT;
const EXPECT_LAYOUT = process.env.UNCAGED_EXPECT_LAYOUT || 'authored-model-points';
const TOL = 2e-5;
const SOURCE_PATH = resolve('src/scene/era-mechanisms.js');
const REPORT_NAME = 'mechanism-layout-v20.json';
const FALLBACK = {
  makerControlOffsets: {
    leg: [.065, .015, .045], wing: [-.095, -.10, .10], tail: [-.07, 0, -.16],
    neck: [-.16, .06, .02], jaw: [-.18, -.06, .20],
  },
  tailPosition: [0, .20, -.31], transmissionPosition: [0, 0, 0],
  distributionPosition: [-.21, .29, .07],
  cervical: [
    { side: 'left', bodyPoint: null, neckPoint: [.055, .16, -.025] },
    { side: 'right', bodyPoint: null, neckPoint: [-.055, .16, -.025] },
  ],
  makerCradleWidth: .62,
};
const failures = [];
const checks = [];
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
const vec = value => new THREE.Vector3(value[0], value[1], value[2]);
const dist = (a, b) => a.distanceTo(b);
const vectorArray = v => v.toArray().map(n => Number(n.toFixed(9)));

function requireRelativeRepoPath(value, label) {
  assert.ok(value, `${label} is required`);
  assert.ok(!isAbsolute(value), `${label} must be repository-relative`);
  const abs = resolve(ROOT, value);
  const rel = relative(ROOT, abs);
  assert.ok(rel && rel !== '..' && !rel.startsWith(`..${sep}`), `${label} must remain under repository`);
  return abs;
}
function record(name, measured, expected, details = {}) {
  const error = dist(measured, expected);
  const passed = Number.isFinite(error) && error <= TOL;
  const row = { name, status: passed ? 'passed' : 'failed', errorMeters: error,
    toleranceMeters: TOL, measuredWorld: vectorArray(measured), expectedWorld: vectorArray(expected), ...details };
  checks.push(row);
  if (!passed) failures.push(row);
  return error;
}
function visibility(name, actual, expected, details = {}) {
  const passed = actual === expected;
  const row = { name, status: passed ? 'passed' : 'failed', actual, expected, ...details };
  checks.push(row);
  if (!passed) failures.push(row);
}
function segmentEnds(object) {
  object.updateWorldMatrix(true, false);
  return [new THREE.Vector3(0, -.5, 0).applyMatrix4(object.matrixWorld),
    new THREE.Vector3(0, .5, 0).applyMatrix4(object.matrixWorld)];
}
function nearestEndpoint(object, point) {
  const ends = segmentEnds(object);
  const index = dist(ends[0], point) <= dist(ends[1], point) ? 0 : 1;
  return { point: ends[index], other: ends[1 - index], endpointIndex: index };
}
function checkEndpoint(object, point, name, details = {}) {
  const actual = nearestEndpoint(object, point).point;
  return record(name, actual, point, { mesh: object.name, ...details });
}
function geometryEndpoints(object) {
  object.updateWorldMatrix(true, false);
  const geometry = object.geometry;
  const position = geometry.attributes.position;
  let min = Infinity, max = -Infinity;
  for (let i = 0; i < position.count; i++) {
    const p = new THREE.Vector3().fromBufferAttribute(position, i).applyMatrix4(object.matrixWorld);
    min = Math.min(min, p.x);
    max = Math.max(max, p.x);
  }
  return { minX: min, maxX: max };
}
function isEffectivelyVisible(object) {
  for (let node = object; node; node = node.parent) if (!node.visible) return false;
  return true;
}
function byName(model, name) {
  const object = model.getObjectByName(name);
  assert.ok(object, `Missing required rig object ${name}`);
  return object;
}
function parseLayout(body) {
  const raw = body.userData?.mechanismLayoutV1;
  if (raw == null) return null;
  return typeof raw === 'string' ? JSON.parse(raw) : raw;
}
function check(name, fn) {
  try { fn(); }
  catch (error) {
    const row = { name, status: 'failed', error: error.stack || error.message };
    checks.push(row); failures.push(row);
  }
}

assert.ok(MODEL, 'Set UNCAGED_MODEL to an explicit repository-relative GLB');
assert.ok(/^[a-f0-9]{64}$/i.test(EXPECTED_SHA || ''), 'Set UNCAGED_EXPECTED_MODEL_SHA256 to the exact 64-digit SHA-256');
assert.ok(AUDIT, 'Set UNCAGED_AUDIT to a new repository-relative audit directory');
const modelPath = requireRelativeRepoPath(MODEL, 'UNCAGED_MODEL');
const auditPath = requireRelativeRepoPath(AUDIT, 'UNCAGED_AUDIT');
const modelBytes = await readFile(modelPath);
const actualModelSha = sha256(modelBytes);
assert.equal(actualModelSha, EXPECTED_SHA.toLowerCase(), 'Model SHA-256 does not match requested identity');
assert.ok(['authored-model-points', 'legacy-placement', 'invalid-contract-legacy-placement'].includes(EXPECT_LAYOUT),
  `Unsupported UNCAGED_EXPECT_LAYOUT=${EXPECT_LAYOUT}`);
try { await readFile(resolve(auditPath, REPORT_NAME)); assert.fail('Refusing to overwrite prior report'); }
catch (error) { if (error.code !== 'ENOENT') throw error; }
try { await readFile(resolve(auditPath, 'executed-verify-mechanism-layout-v20.mjs')); assert.fail('Refusing to overwrite prior source snapshot'); }
catch (error) { if (error.code !== 'ENOENT') throw error; }

const sourceBytes = await readFile(SOURCE_PATH);
const loaded = await loadRigidValidation(modelBytes);
const model = clone(loaded.scene);
const scene = new THREE.Scene();
scene.add(model);
const requiredNames = ['body','neck','head','jaw','left-foot','right-mantle','left-thigh','left-shin',
  'right-thigh','right-shin','left-mantle','left-wing-shield','right-wing-shield','power-core','processing'];
const nodes = Object.fromEntries(requiredNames.map(name => [name, byName(model, name)]));
const rest = Object.fromEntries(requiredNames.map(name => [name, {
  position: nodes[name].position.clone(), rotation: nodes[name].rotation.clone(),
}]));
const body = nodes.body;
const sourceLayout = parseLayout(body);
const mechanism = createEraMechanisms({ scene, model, nodes, rest });
const observedLayout = mechanism.metrics().attachmentLayout;
assert.equal(observedLayout.status, EXPECT_LAYOUT,
  `Expected layout state ${EXPECT_LAYOUT}; runtime reported ${observedLayout.status}`);
if (EXPECT_LAYOUT === 'authored-model-points') {
  assert.equal(sourceLayout?.version, 1, 'V20 model is missing mechanismLayoutV1 version 1');
}
const layout = sourceLayout || null;
const expectedControlOffsets = layout?.makerControlOffsets || FALLBACK.makerControlOffsets;
const tailPosition = layout?.tailPosition || FALLBACK.tailPosition;
const transmissionPosition = layout?.transmissionPosition || FALLBACK.transmissionPosition;
const distributionPosition = layout?.distributionPosition || FALLBACK.distributionPosition;
const cervicalRows = layout?.cervical || FALLBACK.cervical.map(row => ({
  ...row, bodyPoint: nodes.neck.position.clone().add(vec([row.side === 'left' ? .105 : -.105, .02, -.10])).toArray(),
}));
const cradleWidth = Number.isFinite(layout?.makerCradleWidth) && layout.makerCradleWidth > .2
  ? layout.makerCradleWidth : FALLBACK.makerCradleWidth;

// Baseline source-property vs produced geometry checks: geometry endpoints, not
// only the duplicated attachmentLayout metrics, must land on the authored sockets.
const makerTargets = {
  leg: byName(model, 'left-foot'), wing: byName(model, 'right-mantle'),
  tail: byName(model, 'compact-articulated-tail'), neck: nodes.neck, jaw: nodes.jaw,
};
const maker = scene.getObjectByName('era-maker-mechanisms');
const mechanicGroup = scene.getObjectByName('era-mechanic-mechanisms');
const builderGroup = scene.getObjectByName('era-builder-mechanisms');
const gearbox = byName(model, 'mechanic-lower-transmission');
const distribution = byName(model, 'builder-power-distribution-manifold');
const makerCradle = byName(model, 'maker-pelvic-cradle');
const mainBusCase = byName(model, 'builder-sealed-bus-case');
const shaft = byName(model, 'mechanic-cross-shaft');

function tick(era, separation = 0, camAngle = .43) {
  mechanism.setEra(era);
  model.updateMatrixWorld(true);
  mechanism.tick(1 / 60, {}, { camAngle, mechanicalPhase: .19,
    actualArticulation: { leg: .2, wing: .17, tail: .13, neck: .21, jaw: .16 } },
  { open: 0, separation });
  model.updateMatrixWorld(true);
}
function applyPose(kind) {
  model.position.set(.17, -.04, .23);
  model.rotation.set(.025, .31, -.018);
  body.position.copy(rest.body.position).add(new THREE.Vector3(.012, -.019, .024));
  body.rotation.set(.06, -.025, -.035);
  nodes.neck.rotation.set(kind === 'rotated' ? .18 : .03, kind === 'rotated' ? -.11 : 0, 0);
  nodes.head.rotation.set(kind === 'rotated' ? -.09 : 0, .03, 0);
  nodes.jaw.rotation.set(kind === 'rotated' ? .24 : 0, 0, 0);
  nodes['right-mantle'].rotation.x = kind === 'rotated' ? -.23 : 0;
  nodes['left-foot'].rotation.x = kind === 'rotated' ? .13 : 0;
  const upper = model.getObjectByName('cervical-upper');
  if (upper) upper.rotation.x = kind === 'rotated' ? .07 : 0;
  model.updateMatrixWorld(true);
}
function testMakerPose(label) {
  applyPose(label);
  tick('maker');
  const map = { leg: 'leg', wing: 'wing', tail: 'tail', neck: 'neck', jaw: 'jaw' };
  for (const [key, targetKey] of Object.entries(map)) {
    const target = makerTargets[targetKey];
    const expected = target.localToWorld(vec(expectedControlOffsets[key]));
    const horn = byName(model, `maker-control-horn-${key}`);
    const ends = segmentEnds(horn);
    const d0 = dist(ends[0], expected), d1 = dist(ends[1], expected);
    const actual = d0 <= d1 ? ends[0] : ends[1];
    record(`maker-${label}-${key}-horn-geometry-endpoint`, actual, expected,
      { target: target.name, authoredOwnerLocalOffset: expectedControlOffsets[key] });
  }
  const pelvisWorld = body.getWorldPosition(new THREE.Vector3());
  const root = model.getObjectByName('murderbird') || model;
  const pelvisInRoot = root.worldToLocal(pelvisWorld.clone()).add(new THREE.Vector3(0, -.035, 0));
  const expectedCradleWorld = root.localToWorld(pelvisInRoot.clone());
  record(`maker-${label}-cradle-world-center`, makerCradle.getWorldPosition(new THREE.Vector3()), expectedCradleWorld,
    { source: 'live body/pelvis world position plus .035m support drop' });
  const actualCradleWidth = makerCradle.geometry.parameters.width;
  const row = { name: `maker-${label}-cradle-geometry-width`, status: Math.abs(actualCradleWidth - cradleWidth) <= 1e-8 ? 'passed' : 'failed',
    measuredMeters: actualCradleWidth, expectedMeters: cradleWidth, toleranceMeters: 1e-8 };
  checks.push(row); if (row.status === 'failed') failures.push(row);
}

for (const label of ['rest', 'rotated']) check(`maker-${label}`, () => testMakerPose(label));

function testMechanicPose(label) {
  applyPose(label);
  tick('mechanic', 0, .43);
  const signInfo = { left: 1, right: -1 };
  for (const side of ['left', 'right']) {
    const spindleLocal = new THREE.Vector3(signInfo[side] * .4, -.16, .035);
    const expectedCrankBase = gearbox.localToWorld(spindleLocal.clone());
    const crank = byName(model, `mechanic-${side}-crank-link`);
    checkEndpoint(crank, expectedCrankBase, `mechanic-${label}-${side}-crank-root-follows-transmission`);
    const pin = byName(model, `mechanic-${side}-crank-pin`);
    checkEndpoint(crank, pin.getWorldPosition(new THREE.Vector3()), `mechanic-${label}-${side}-crank-terminates-at-pin`);
    const knee = nodes[`${side}-shin`].getWorldPosition(new THREE.Vector3());
    const slider = byName(model, `mechanic-${side}-slotted-knee-link-slider`);
    checkEndpoint(slider, knee, `mechanic-${label}-${side}-slider-terminates-at-live-shin`, { target: nodes[`${side}-shin`].name });
  }
  for (const side of ['left', 'right']) {
    const sgn = side === 'left' ? 1 : -1;
    const expected = gearbox.localToWorld(new THREE.Vector3(sgn * .38, -.16, .035));
    checkEndpoint(shaft, expected, `mechanic-${label}-${side}-crossshaft-physical-endpoint`);
  }
}
for (const label of ['rest', 'rotated']) check(`mechanic-${label}`, () => testMechanicPose(label));

function testBuilderPose(label, separated = false) {
  applyPose(label);
  tick('builder', separated ? .25 : 0);
  const distributionLocal = vec(distributionPosition);
  const expectedManifold = body.localToWorld(distributionLocal.clone());
  const busCenter = mainBusCase.getWorldPosition(new THREE.Vector3());
  record(`builder-${label}-${separated ? 'separated' : 'connected'}-manifold-case-center`, busCenter, expectedManifold,
    { owner: 'body', authoredOwnerLocalPosition: distributionPosition });
  const core = nodes['power-core'].getWorldPosition(new THREE.Vector3());
  const busLink = byName(model, 'builder-core-to-distribution-conduit');
  checkEndpoint(busLink, core, `builder-${label}-core-conduit-actual-core-endpoint`, { target: 'power-core' });
  checkEndpoint(busLink, expectedManifold, `builder-${label}-core-conduit-actual-manifold-endpoint`, { target: 'builder-power-distribution-manifold' });
  const neckAnchors = Object.fromEntries(cervicalRows.map(row => [row.side, row]));
  for (const side of ['left', 'right']) {
    const anchors = neckAnchors[side];
    const bodyAnchor = body.localToWorld(vec(anchors.bodyPoint));
    const neckAnchor = nodes.neck.localToWorld(vec(anchors.neckPoint));
    const suffix = side === 'left' ? 'left' : 'right';
    const sleeve = byName(model, `builder-cervical-${suffix}-actuator-sleeve`);
    const rod = byName(model, `builder-cervical-${suffix}-actuator-rod`);
    const conduit = byName(model, `builder-cervical-${suffix}-power-conduit`);
    if (separated) {
      for (const [partName, part] of [['sleeve', sleeve], ['rod', rod], ['conduit', conduit]])
        visibility(`builder-${label}-${side}-${partName}-disconnect`, isEffectivelyVisible(part), false);
    } else {
      checkEndpoint(sleeve, bodyAnchor, `builder-${label}-${side}-sleeve-body-socket`, { owner: 'body', authoredLocalPoint: anchors.bodyPoint });
      checkEndpoint(rod, neckAnchor, `builder-${label}-${side}-rod-neck-socket`, { owner: 'neck', authoredLocalPoint: anchors.neckPoint });
      checkEndpoint(conduit, expectedManifold, `builder-${label}-${side}-cervical-conduit-manifold-endpoint`);
      checkEndpoint(conduit, bodyAnchor, `builder-${label}-${side}-cervical-conduit-body-socket`);
      for (const [partName, part] of [['sleeve', sleeve], ['rod', rod], ['conduit', conduit]])
        visibility(`builder-${label}-${side}-${partName}-connected`, isEffectivelyVisible(part), true);
    }
  }
}
for (const label of ['rest', 'rotated']) {
  check(`builder-${label}-connected`, () => testBuilderPose(label, false));
  if (label === 'rotated') {
    check('builder-rotated-disconnected', () => testBuilderPose(label, true));
    check('builder-rotated-reconnected', () => testBuilderPose(label, false));
  }
}

check('authored-tail-position-produces-actual-tail-pivot', () => {
  applyPose('rest');
  const tail = byName(model, 'compact-articulated-tail');
  const expected = body.localToWorld(vec(tailPosition));
  record('tail-pivot-world-from-body-local-position', tail.getWorldPosition(new THREE.Vector3()), expected,
    { authoredOwnerLocalPosition: tailPosition, owner: 'body' });
});

check('era-eligibility', () => {
  applyPose('rotated');
  tick('maker');
  visibility('maker-controls-visible-in-maker', isEffectivelyVisible(byName(model, 'maker-control-horn-neck')), true);
  visibility('mechanic-gear-hidden-in-maker', isEffectivelyVisible(byName(model, 'mechanic-reduction-driver-wheel')), false);
  visibility('builder-actuator-hidden-in-maker', isEffectivelyVisible(byName(model, 'builder-cervical-left-actuator-sleeve')), false);
  tick('mechanic');
  visibility('mechanic-drive-visible-in-mechanic', isEffectivelyVisible(byName(model, 'mechanic-reduction-driver-wheel')), true);
  visibility('maker-controls-hidden-in-mechanic', isEffectivelyVisible(byName(model, 'maker-control-horn-neck')), false);
  visibility('builder-actuator-hidden-in-mechanic', isEffectivelyVisible(byName(model, 'builder-cervical-left-actuator-sleeve')), false);
  tick('builder');
  visibility('builder-cervical-visible-in-builder', isEffectivelyVisible(byName(model, 'builder-cervical-left-actuator-sleeve')), true);
  visibility('maker-controls-hidden-in-builder', isEffectivelyVisible(byName(model, 'maker-control-horn-neck')), false);
  visibility('mechanic-gear-hidden-in-builder', isEffectivelyVisible(byName(model, 'mechanic-reduction-driver-wheel')), false);
});

const runtimeMetrics = mechanism.metrics();
const sourceStamp = { path: relative(ROOT, SOURCE_PATH), sha256: sha256(sourceBytes) };
const report = {
  generatedAt: new Date().toISOString(),
  status: failures.length ? 'FAIL' : 'PASS_WITHIN_ENDPOINT_AND_VISIBILITY_CHECKS',
  model: { path: MODEL, sha256: actualModelSha, bytes: modelBytes.length },
  expectedLayout: EXPECT_LAYOUT,
  sourceLayout: sourceLayout || null,
  runtimeLayout: runtimeMetrics.attachmentLayout,
  runtimeSource: sourceStamp,
  tolerances: { endpointPositionMeters: TOL, cradleGeometryWidthMeters: 1e-8 },
  checks,
  failures,
  limits: [
    'This compares actual dynamic-cylinder endpoints and fixed mesh centers against declared owner-local points after world transforms; it does not compare schema metadata only to copied runtime metrics.',
    'The artificial rotated pose only checks attachment propagation under selected neck, jaw, wing, foot, body, and root transforms; it is not a swept-clearance test.',
    'Passing does not establish surface seating, collisions, load path strength, continuous motion clearance, era art acceptance, or browser/runtime visual acceptance.',
    'Legacy mode checks the unchanged fallback branch against known historical fallback constants; it does not validate those old attachment locations against changed anatomy.',
  ],
};

await mkdir(auditPath, { recursive: true });
await copyFile(resolve('scripts/verify-mechanism-layout-v20.mjs'), resolve(auditPath, 'executed-verify-mechanism-layout-v20.mjs'), fsConstants.COPYFILE_EXCL);
await writeFile(resolve(auditPath, REPORT_NAME), `${JSON.stringify(report, null, 2)}\n`, { flag: 'wx' });
mechanism.dispose();
console.log(JSON.stringify({ status: report.status, checks: checks.length, failures: failures.length,
  report: relative(ROOT, resolve(auditPath, REPORT_NAME)), modelSha256: actualModelSha,
  layoutStatus: runtimeMetrics.attachmentLayout.status }));
if (failures.length) process.exitCode = 1;
