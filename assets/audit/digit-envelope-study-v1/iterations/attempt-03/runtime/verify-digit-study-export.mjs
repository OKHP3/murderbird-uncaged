import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { loadRigidValidation } from '../../../../../../scripts/load-rigid-validation.mjs';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../../../../../');
const manifestPath = path.join(path.dirname(new URL(import.meta.url).pathname), 'runtime-derivative.json');
const manifest = JSON.parse(await readFile(manifestPath, 'utf8'));
const modelPath = path.resolve(root, manifest.outputGlb.path);
const bytes = await readFile(modelPath);
const digest = createHash('sha256').update(bytes).digest('hex');
assert.equal(digest, manifest.outputGlb.sha256, 'Derivative GLB SHA changed after export receipt');
const { scene } = await loadRigidValidation(bytes);
scene.updateMatrixWorld(true);
const pivotNames = Object.keys(manifest.pivotWorldMatrices);
const pivotSet = new Set(pivotNames);
const close = (a, b, tolerance = 1e-8) => a.length === b.length && a.every((v, i) => Math.abs(v - b[i]) <= tolerance);
function matrixRows(matrix) {
  const e = matrix.elements;
  return [[e[0], e[4], e[8], e[12]], [e[1], e[5], e[9], e[13]],
    [e[2], e[6], e[10], e[14]], [e[3], e[7], e[11], e[15]]];
}
function multiply(a, b) {
  return a.map((row, i) => b[0].map((_, j) => row.reduce((sum, value, k) => sum + value * b[k][j], 0)));
}
function blenderToGlb(matrix) {
  const convert = [[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]];
  const inverse = [[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]];
  return multiply(multiply(convert, matrix), inverse);
}
const pivots = [];
for (const name of pivotNames) {
  const matches = [];
  scene.traverse(node => { if (node.name === name) matches.push(node); });
  assert.equal(matches.length, 1, `Expected one exported pivot named ${name}`);
  const node = matches[0];
  assert.ok(close(matrixRows(node.matrixWorld).flat(), blenderToGlb(manifest.pivotWorldMatrices[name]).flat()), `Pivot world matrix changed after Blender-to-glTF Y-up conversion: ${name}`);
  pivots.push({ name, parent: node.parent?.name ?? null, worldMatrix: matrixRows(node.matrixWorld) });
}
const expected = new Map(manifest.batchContract.map(record => [
  JSON.stringify([record.parent, record.exteriorEras, record.region, record.surfaceRole]), record,
]));
assert.equal(expected.size, manifest.batchContract.length, 'Native batch contract contains duplicate grouping keys');
const actual = new Map();
const meshNames = [];
scene.traverse(mesh => {
  if (!mesh.isMesh) return;
  meshNames.push(mesh.name);
  const lineage = [];
  for (let node = mesh; node; node = node.parent) lineage.push(node);
  const owner = lineage.find(node => pivotSet.has(node.name))?.name;
  const inherited = Object.assign({}, ...lineage.toReversed().map(node => node.userData || {}));
  const eras = inherited.exteriorEras;
  const region = inherited.region;
  const role = inherited.surfaceRole;
  assert.ok(owner && eras && region && role, `Exported mesh is missing ownership/tags: ${mesh.name}`);
  const key = JSON.stringify([owner, eras, region, role]);
  assert.ok(expected.has(key), `Unlisted export batch/tag: ${mesh.name} ${key}`);
  const prior = actual.get(key) || { meshNames: [], triangles: 0 };
  prior.meshNames.push(mesh.name);
  const index = mesh.geometry.index;
  const position = mesh.geometry.attributes.position;
  const count = index?.count ?? position.count;
  const ranges = mesh.geometry.groups.length ? mesh.geometry.groups : [{ start: 0, count }];
  for (const range of ranges) {
    assert.equal(range.count % 3, 0, `Exported primitive is not triangulated: ${mesh.name}`);
    prior.triangles += range.count / 3;
  }
  actual.set(key, prior);
});
assert.equal(meshNames.length, manifest.summary.batchCount, 'Exported mesh-group count differs from native grouping contract');
assert.equal(new Set(meshNames).size, meshNames.length, 'Exported mesh object names are not unique');
assert.deepEqual([...actual.keys()].sort(), [...expected.keys()].sort(), 'Exported group keys differ from native parent/era/region/role contract');
for (const [key, record] of expected) {
  const batch = actual.get(key);
  const names = record.objectNames;
  const expectedNamePrefix = `${record.parent}-${record.region}-${record.surfaceRole}`;
  assert.ok(batch.meshNames.every(name => name === expectedNamePrefix || name.startsWith(`${expectedNamePrefix}.`)),
    `Exported name differs from reviewed parent/region/role base: ${batch.meshNames.join(', ')}`);
  assert.ok(names.length > 0, `Empty native input batch for ${key}`);
}
const report = {
  generatedAt: new Date().toISOString(),
  status: 'pass',
  candidate: manifest.outputGlb,
  exportReceiptSha256: createHash('sha256').update(await readFile(manifestPath)).digest('hex'),
  summary: { exportedMeshes: meshNames.length, nativeBatches: expected.size, pivots: pivots.length,
    meshNamesUnique: true, allTagsAndOwnersExact: true, pivotWorldMatricesExact: true,
    triangles: [...actual.values()].reduce((sum, batch) => sum + batch.triangles, 0) },
  pivots,
  groups: [...expected].map(([key, contract]) => ({ key: JSON.parse(key), inputObjectCount: contract.objectNames.length,
    exportedMeshNames: actual.get(key).meshNames, exportedTriangleCount: actual.get(key).triangles })),
  limits: ['Checks GLB names, tag grouping, unique exported mesh names and pivot matrices against the exact native export contract.',
    'Does not prove source topology equivalence, collision clearance, physical performance or artistic acceptance.'],
};
const output = path.join(path.dirname(new URL(import.meta.url).pathname), 'export-inventory-check.json');
await writeFile(output, `${JSON.stringify(report, null, 2)}\n`, { flag: 'wx' });
console.log(JSON.stringify({ status: report.status, ...report.summary, output }));
