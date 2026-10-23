import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { mkdtemp, mkdir, writeFile, readFile, symlink, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { execFileSync, spawnSync } from 'node:child_process';
import { diagnoseSnapshot, writePrivateReceipt } from '../scripts/verify-structural-clearance-snapshot.mjs';

const options = { era: 'export-label', pose: 'rest-label', minimumSeparationMeters: 0.002 };
function mesh(name, x = 0, copies = 1) {
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(
    Array.from({ length: copies }, () => [0, 0, 0, 1, 0, 0, 0, 1, 0]).flat(), 3));
  const object = new THREE.Mesh(geometry); object.name = name; object.position.x = x; return object;
}
function fixture() {
  const scene = new THREE.Group();
  for (const [side, x] of [['left', 0], ['right', 10]]) {
    const shin = new THREE.Group(); shin.name = `${side}-shin`;
    const foot = new THREE.Group(); foot.name = `${side}-foot`;
    shin.add(mesh(`${side}-shin-shell`, x + 3));
    foot.add(mesh(`${side}-foot-shell`, x));
    foot.add(mesh(`${side}-toes`, x, 2)); shin.add(foot); scene.add(shin);
  }
  return scene;
}

test('nine static pairs retain simultaneous contacts and exclude descendant surfaces', () => {
  const scene = fixture(); scene.updateMatrixWorld(true);
  const before = scene.toJSON();
  const result = diagnoseSnapshot(scene, options);
  assert.equal(result.pairs.length, 9);
  assert.equal(result.pairs.filter(pair => pair.status === 'MEASURED').length, 9);
  assert.equal(result.surfaces['left-foot'].triangles, 1);
  assert.equal(result.surfaces['left-shin'].triangles, 1);
  const join = result.pairs.find(pair => pair.first === 'left-toes' && pair.second === 'left-foot');
  assert.equal(join.contactCount, 2); assert.equal(join.contacts.length, 2);
  assert.equal(join.classification, 'UNCLASSIFIED');
  assert.deepEqual(scene.toJSON(), before);
  assert.equal(result.status, 'PARTIAL');
  assert.equal(result.temporal.status, 'NOT RUN');
  assert.deepEqual(result.legDrive.map(item => item.status), ['NOT RUN', 'NOT RUN']);
  assert.equal(result.acceptance.wholeModelLikeness, 'PENDING');
  assert.equal(result.acceptance.modelRuntimeIntegration, 'HELD');
  assert.ok(JSON.parse(JSON.stringify(result)).pairs[0].nearestSummary);
});

test('labels do not activate eras or change exported visibility', () => {
  const scene = fixture(); scene.getObjectByName('left-foot').visible = false;
  const result = diagnoseSnapshot(scene, options);
  assert.equal(result.surfaces['left-toes'].status, 'NOT RUN');
  assert.equal(result.pairs[0].status, 'NOT RUN');
  assert.equal(scene.getObjectByName('left-foot').visible, false);
});

test('missing, ambiguous, empty and unsupported geometry stay unknown', () => {
  for (const kind of ['missing', 'ambiguous', 'empty', 'morph', 'skin', 'instanced']) {
    const scene = fixture(), toe = scene.getObjectByName('left-toes');
    if (kind === 'missing') toe.removeFromParent();
    if (kind === 'ambiguous') scene.add(mesh('left-toes'));
    if (kind === 'empty') toe.geometry = new THREE.BufferGeometry();
    if (kind === 'morph') toe.geometry.morphAttributes.position = [toe.geometry.attributes.position];
    if (kind === 'skin') toe.isSkinnedMesh = true;
    if (kind === 'instanced') toe.isInstancedMesh = true;
    const result = diagnoseSnapshot(scene, options);
    assert.equal(result.surfaces['left-toes'].status, 'NOT RUN', kind);
    assert.equal(result.pairs[0].status, 'NOT RUN', kind);
  }
});

test('parent surfaces stay unknown when their named descendant exclusion is ambiguous', () => {
  const duplicateToes = fixture();
  duplicateToes.getObjectByName('left-foot').add(mesh('left-toes'));
  let result = diagnoseSnapshot(duplicateToes, options);
  assert.equal(result.surfaces['left-foot'].status, 'NOT RUN');
  assert.match(result.surfaces['left-foot'].reason, /Expected one descendant exclusion named left-toes; found 2/);

  const duplicateFeet = fixture();
  const secondFoot = new THREE.Group(); secondFoot.name = 'left-foot';
  secondFoot.add(mesh('additional-left-foot'));
  duplicateFeet.getObjectByName('left-shin').add(secondFoot);
  result = diagnoseSnapshot(duplicateFeet, options);
  assert.equal(result.surfaces['left-shin'].status, 'NOT RUN');
  assert.match(result.surfaces['left-shin'].reason, /Expected one descendant exclusion named left-foot; found 2/);

  const missingToes = fixture();
  missingToes.getObjectByName('left-toes').removeFromParent();
  result = diagnoseSnapshot(missingToes, options);
  assert.equal(result.surfaces['left-foot'].status, 'NOT RUN');
  assert.match(result.surfaces['left-foot'].reason, /Expected one descendant exclusion named left-toes; found 0/);
});

test('explicit labels and finite nonnegative threshold required', () => {
  for (const value of [NaN, Infinity, -1, undefined]) {
    assert.throws(() => diagnoseSnapshot(fixture(), { ...options, minimumSeparationMeters: value }));
  }
  assert.throws(() => diagnoseSnapshot(fixture(), { ...options, era: '' }));
  assert.throws(() => diagnoseSnapshot(fixture(), { ...options, pose: '' }));
});

test('private output refuses overwrite, archives, publication paths, traversal and symlinks', async t => {
  const root = await mkdtemp(join(tmpdir(), 'murderbird-snapshot-test-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  execFileSync('git', ['init', '-q', root]);
  // Keep this temporary repository independent of host-wide ignore rules.
  const excludes = join(root, '.git', 'isolated-excludes');
  await writeFile(excludes, '');
  execFileSync('git', ['-C', root, 'config', 'core.excludesFile', excludes]);
  await writeFile(join(root, '.gitignore'), '.local/\n');
  await mkdir(join(root, '.local', 'diagnostics'), { recursive: true });
  const output = '.local/diagnostics/new.json';
  await writePrivateReceipt(root, output, { status: 'PARTIAL' });
  const original = await readFile(join(root, output), 'utf8');
  await assert.rejects(writePrivateReceipt(root, output, {}), /EEXIST/);
  assert.equal(await readFile(join(root, output), 'utf8'), original);
  for (const path of ['public/new.json', 'dist/new.json', '.local/archives/new.json',
    '.local/../../escape.json', '.local/new.json']) {
    await assert.rejects(writePrivateReceipt(root, path, {}));
  }
  await symlink(join(root, '.local', 'diagnostics'), join(root, '.local', 'link'));
  await assert.rejects(writePrivateReceipt(root, '.local/link/new.json', {}), /real directories/);
  await symlink(join(root, 'target.json'), join(root, '.local', 'diagnostics', 'link.json'));
  await assert.rejects(writePrivateReceipt(root, '.local/diagnostics/link.json', {}), /EEXIST/);
  await writeFile(join(root, '.gitignore'), '');
  await assert.rejects(writePrivateReceipt(root, '.local/diagnostics/unignored.json', {}));
});

test('CLI rejects wrong input hash before parsing or writing a receipt', async t => {
  const root = await mkdtemp(join(tmpdir(), 'murderbird-snapshot-input-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  const model = join(root, 'invalid.glb'); await writeFile(model, 'not a GLB');
  const result = spawnSync(process.execPath, [resolve('scripts/verify-structural-clearance-snapshot.mjs'),
    '--model', model, '--sha256', '0'.repeat(64), '--era', 'label', '--pose', 'rest',
    '--minimum-separation-m', '0.002', '--output', '.local/diagnostics/never.json'], { encoding: 'utf8' });
  assert.equal(result.status, 1); assert.match(result.stderr, /SHA-256 mismatch/);
});
