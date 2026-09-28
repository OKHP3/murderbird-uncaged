import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import * as THREE from 'three';

const folder = process.argv[2] || 'assets/audit/alignment-v9/live-browser-pose-v1';
const bytes = await readFile(`${folder}/paused-pose.json`);
const capture = JSON.parse(bytes);
const repeat = JSON.parse(await readFile(`${folder}/paused-pose-repeat.json`));
const recorded = JSON.parse(await readFile(`${folder}/capture-validation.json`));
const inventory = JSON.parse(await readFile('assets/models/uncaged-alignment-v9/alignment-inventory.json'));
assert.equal(createHash('sha256').update(bytes).digest('hex'), recorded.captureSha256);
assert(capture.sameRead && capture.returnedArraysDetached && capture.finite && capture.before.paused);
assert.deepEqual(capture.before, capture.after);

const rows = capture.pose.pivotMatrices;
const names = new Map();
for (const row of rows) names.set(row.name, [...(names.get(row.name) || []), row]);
for (const pivot of inventory.pivots) assert.equal(names.get(pivot.name)?.length, 1, pivot.name);
const paths = new Map(rows.map(row => [row.path, row]));
assert.equal(paths.size, rows.length);
let maximumError = 0;
for (const row of rows) {
  const matrix = new THREE.Matrix4().fromArray(row.localMatrix);
  const parentPath = row.path.split('/').slice(0, -1).join('/');
  const parent = paths.get(parentPath);
  if (parent) matrix.premultiply(new THREE.Matrix4().fromArray(parent.worldMatrix));
  maximumError = Math.max(maximumError, ...matrix.elements.map((v, i) => Math.abs(v - row.worldMatrix[i])));
}
assert(maximumError < 1e-12);
const later = new Map(repeat.pose.pivotMatrices.map(row => [row.path, row]));
let maximumDrift = 0;
for (const row of rows) {
  assert(later.has(row.path));
  maximumDrift = Math.max(maximumDrift, ...row.worldMatrix.map((v, i) => Math.abs(v - later.get(row.path).worldMatrix[i])));
}
assert.equal(maximumDrift, 0);
assert.equal(maximumDrift, repeat.maxWorldMatrixDrift);
assert.equal(maximumError, recorded.maxHierarchyMatrixError);
console.log(JSON.stringify({status:'pass', nativePivots:inventory.pivots.length,
  recordedTransforms:rows.length, maximumHierarchyError:maximumError, pausedWorldMatrixDrift:maximumDrift,
  scope:'Saved browser capture and hierarchy consistency; not surface clearance or continuous movement proof.'}));
