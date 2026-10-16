import { readFile, realpath, lstat, open } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { resolve, relative, sep } from 'node:path';
import { pathToFileURL } from 'node:url';
import { parseArgs } from 'node:util';
import { loadRigidValidation } from './load-rigid-validation.mjs';
import { buildTriangleSurface, measureSurfaceClearance, measureSurfaceContacts } from './triangle-clearance.mjs';

const names = ['left-toes', 'right-toes', 'left-foot', 'right-foot', 'left-shin', 'right-shin'];
export const snapshotPairs = [
  ['left-toes', 'right-toes'],
  ...['left', 'right'].flatMap(side => ['left', 'right'].flatMap(other =>
    ['foot', 'shin'].map(part => [`${side}-toes`, `${other}-${part}`]))),
];

/** Exported transforms only. Labels never select an era or animate the scene. */
export function diagnoseSnapshot(scene, { era, pose, minimumSeparationMeters } = {}) {
  if (!era?.trim() || !pose?.trim()) throw new Error('Explicit era and pose labels are required');
  if (!Number.isFinite(minimumSeparationMeters) || minimumSeparationMeters < 0) {
    throw new Error('minimumSeparationMeters must be finite and non-negative');
  }
  const surfaces = {}, coverage = {};
  for (const name of names) {
    const matches = [];
    scene.traverse(object => { if (object.name === name) matches.push(object); });
    try {
      if (matches.length !== 1) throw new Error(`Expected one named group; found ${matches.length}`);
      const root = matches[0];
      for (let ancestor = root; ancestor; ancestor = ancestor.parent) {
        if (!ancestor.visible) throw new Error('Group or ancestor is hidden in exported visibility');
      }
      const excludedName = name.endsWith('-foot') ? name.replace('-foot', '-toes')
        : name.endsWith('-shin') ? name.replace('-shin', '-foot') : null;
      // Exclude only a descendant: unrelated surfaces are never subtracted.
      const excluded = excludedName ? root.getObjectByName(excludedName) : null;
      function check(object) {
        if (object === excluded || !object.visible) return;
        if (object.isSkinnedMesh || object.isInstancedMesh || object.geometry?.morphAttributes?.position?.length) {
          throw new Error('Skinned, instanced or morph geometry is unsupported');
        }
        for (const child of object.children) check(child);
      }
      check(root);
      surfaces[name] = buildTriangleSurface(root, { exclude: excluded });
      coverage[name] = { status: 'MEASURED', triangles: surfaces[name].triangles.length,
        excludedDescendant: excluded?.name ?? null };
    } catch (error) {
      coverage[name] = { status: 'NOT RUN', reason: error.message };
    }
  }
  const pairs = snapshotPairs.map(([first, second]) => {
    if (!surfaces[first] || !surfaces[second]) return { first, second, status: 'NOT RUN',
      reason: 'One or both surfaces unavailable; separation unknown' };
    const contacts = measureSurfaceContacts(surfaces[first], surfaces[second], { minimumSeparationMeters });
    return { first, second, status: 'MEASURED', classification: 'UNCLASSIFIED',
      nearestSummary: measureSurfaceClearance(surfaces[first], surfaces[second]),
      contactCount: contacts.length, contacts };
  });
  return {
    schema: 'murderbird-structural-clearance-snapshot/v1', status: 'PARTIAL',
    snapshot: { eraLabel: era, poseLabel: pose, transforms: 'exported resting transforms',
      visibility: 'exported visibility; labels do not select geometry or visibility' },
    minimumSeparationMeters, thresholdStatus: 'Diagnostic input; not an accepted engineering threshold',
    surfaces: coverage, pairs,
    legDrive: ['left', 'right'].map(side => ({ side, status: 'NOT RUN',
      reason: 'Current main lacks the held getToeDriveSurface selection API; no substitute used' })),
    temporal: { status: 'NOT RUN', reason: 'No poses sampled or continuous sweeps evaluated' },
    acceptance: { engineering: 'NOT ESTABLISHED', wholeModelLikeness: 'PENDING',
      modelRuntimeIntegration: 'HELD' },
  };
}

/** New receipts only, inside an existing Git-ignored .local directory, with no symlink traversal. */
export async function writePrivateReceipt(repositoryRoot, output, receipt) {
  const root = await realpath(repositoryRoot), target = resolve(root, output);
  const rel = relative(root, target), parts = rel.split(sep);
  if (parts[0] !== '.local' || parts.length < 3 || parts.includes('..')
      || parts[1] === 'archives' || !target.endsWith('.json')) {
    throw new Error('Output must be a new JSON receipt below .local, outside recovery archives');
  }
  let current = root;
  for (const part of parts.slice(0, -1)) {
    current = resolve(current, part);
    const stat = await lstat(current);
    if (stat.isSymbolicLink() || !stat.isDirectory()) throw new Error('Output ancestors must be real directories');
  }
  execFileSync('git', ['check-ignore', '-q', '--', rel], { cwd: root });
  const handle = await open(target, 'wx', 0o600);
  try { await handle.writeFile(`${JSON.stringify(receipt, null, 2)}\n`); }
  finally { await handle.close(); }
  return target;
}

export async function main(args = process.argv.slice(2)) {
  const { values } = parseArgs({ args, options: Object.fromEntries(
    ['model', 'sha256', 'era', 'pose', 'minimum-separation-m', 'output'].map(key => [key, { type: 'string' }])) });
  for (const key of ['model', 'sha256', 'era', 'pose', 'minimum-separation-m', 'output']) {
    if (!values[key]?.trim()) throw new Error(`Missing --${key}`);
  }
  if (!/^[a-f0-9]{64}$/i.test(values.sha256)) throw new Error('Expected a full SHA-256');
  const threshold = Number(values['minimum-separation-m']);
  if (!Number.isFinite(threshold) || threshold < 0) throw new Error('Invalid minimum separation');
  const root = execFileSync('git', ['rev-parse', '--show-toplevel'], { encoding: 'utf8' }).trim();
  const model = await realpath(resolve(values.model)), bytes = await readFile(model);
  const sha256 = createHash('sha256').update(bytes).digest('hex');
  if (sha256 !== values.sha256.toLowerCase()) throw new Error('Model SHA-256 mismatch; no diagnostic written');
  const gltf = await loadRigidValidation(bytes);
  const receipt = diagnoseSnapshot(gltf.scene, { era: values.era, pose: values.pose, minimumSeparationMeters: threshold });
  receipt.input = { path: model, sha256, bytes: bytes.length };
  receipt.source = {
    checkoutSha: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim(),
    originMainSha: execFileSync('git', ['rev-parse', 'refs/remotes/origin/main'], { cwd: root, encoding: 'utf8' }).trim(),
    originMainCoverage: 'Local remote-tracking ref; not a live remote verification',
    dirty: !!execFileSync('git', ['status', '--porcelain'], { cwd: root, encoding: 'utf8' }).trim(),
  };
  receipt.createdAt = new Date().toISOString();
  const output = await writePrivateReceipt(root, values.output, receipt);
  console.log(JSON.stringify({ output, status: receipt.status, measuredPairs: receipt.pairs.filter(p => p.status === 'MEASURED').length }));
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  main().catch(error => { console.error(error.message); process.exitCode = 1; });
}
