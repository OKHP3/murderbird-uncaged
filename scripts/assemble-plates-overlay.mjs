/**
 * Assemble a Pages artifact that adds public/plates/ to the site that is already published,
 * without rebuilding it. The published files are read back from the live release manifest and
 * verified byte for byte, so this path needs no Git LFS download. Only the allowlisted files in
 * plates-overlay-patch.mjs (index.html, folio.html, sitemap.xml) change, each by one anchored
 * insertion that links Living Plates. The v1.1 final copy fixes in final-copy-fixes.mjs then
 * replace exact published strings in index.html, cg.html and the exhibit and CG bundles, each
 * matching exactly once. Every other base file is republished unchanged.
 *
 * Usage: node scripts/assemble-plates-overlay.mjs <base-url> <expected-base-revision> <out-dir>
 */
import {createHash} from 'node:crypto';
import {mkdir, readFile, readdir, writeFile} from 'node:fs/promises';
import {dirname, join, posix} from 'node:path';
import {BASE_PATCHES, applyBasePatch} from './plates-overlay-patch.mjs';
import {applyCopyFixes, isCopyFixTarget} from './final-copy-fixes.mjs';

const [baseArg, expectedBase, out] = process.argv.slice(2);
if (!baseArg || !expectedBase || !out) throw new Error('Usage: assemble-plates-overlay.mjs <base-url> <expected-base-revision> <out-dir>');
const base = baseArg.replace(/\/+$/, '');
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const safe = path => /^[A-Za-z0-9][A-Za-z0-9_./-]*$/.test(path) && !path.split('/').includes('..') && posix.normalize(path) === path;

async function get(path, attempt = 1) {
  const response = await fetch(`${base}/${path}`, {redirect: 'error', cache: 'no-store'});
  if (!response.ok) {
    if (attempt < 3 && response.status >= 500) return get(path, attempt + 1);
    throw new Error(`${path}: HTTP ${response.status}`);
  }
  return Buffer.from(await response.arrayBuffer());
}

const manifestBytes = await get('release.json');
const manifest = JSON.parse(manifestBytes.toString('utf8'));
if (manifest.revision !== expectedBase) throw new Error(`Live release is ${manifest.revision}, expected ${expectedBase}. Review the base before overlaying.`);
if (manifest.workingTreeDirty) throw new Error('Live release was built from a modified tree.');
if (!Array.isArray(manifest.files) || manifest.files.length === 0) throw new Error('Live release manifest lists no files.');

const queue = [...manifest.files];
let baseBytes = 0;
const patchedBaseFiles = [];
async function worker() {
  for (let item = queue.shift(); item; item = queue.shift()) {
    if (!safe(item.path)) throw new Error(`Unsafe published path: ${item.path}`);
    if (item.path === 'release.json' || item.path.startsWith('plates/')) throw new Error(`Base release already claims ${item.path}`);
    const bytes = await get(item.path);
    if (bytes.length !== item.bytes || sha(bytes) !== item.sha256) throw new Error(`Live file does not match its release record: ${item.path}`);
    await mkdir(dirname(join(out, item.path)), {recursive: true});
    baseBytes += bytes.length;
    if (Object.hasOwn(BASE_PATCHES, item.path) || isCopyFixTarget(item.path)) {
      held.set(item.path, {bytes, baseSha256: item.sha256});
    } else {
      await writeFile(join(out, item.path), bytes);
    }
  }
}
const held = new Map();
await mkdir(out, {recursive: true});
await Promise.all(Array.from({length: 6}, worker));
const texts = {};
for (const [path, {bytes}] of held) {
  texts[path] = bytes.toString('utf8');
  if (Object.hasOwn(BASE_PATCHES, path)) texts[path] = applyBasePatch(path, texts[path]);
}
applyCopyFixes(texts);
for (const [path, {bytes, baseSha256}] of held) {
  const patched = Buffer.from(texts[path], 'utf8');
  if (patched.equals(bytes)) {
    await writeFile(join(out, path), bytes);
  } else {
    await writeFile(join(out, path), patched);
    patchedBaseFiles.push({path, baseSha256, bytes: patched.length, sha256: sha(patched)});
  }
}
await writeFile(join(out, 'release.json'), manifestBytes);
const missingPatch = Object.keys(BASE_PATCHES).filter(path => !patchedBaseFiles.some(file => file.path === path));
if (missingPatch.length) throw new Error(`Live release lacks allowlisted patch targets: ${missingPatch.join(', ')}`);
patchedBaseFiles.sort((a, b) => a.path.localeCompare(b.path));

async function walk(directory, prefix = '') {
  const found = [];
  for (const entry of (await readdir(directory, {withFileTypes: true})).sort((a, b) => a.name.localeCompare(b.name))) {
    const relative = prefix ? `${prefix}/${entry.name}` : entry.name;
    if (entry.isDirectory()) found.push(...await walk(join(directory, entry.name), relative));
    else if (entry.isFile()) found.push(relative);
    else throw new Error(`Refusing non-regular overlay entry: ${relative}`);
  }
  return found;
}
const overlay = [];
for (const relative of await walk('public/plates')) {
  if (!safe(relative) || /\.(?:blend|webm|zip|wav)$/i.test(relative)) throw new Error(`Unexpected overlay file: ${relative}`);
  const bytes = await readFile(join('public/plates', relative));
  if (bytes.subarray(0, 40).toString('latin1').startsWith('version https://git-lfs.github.com/spec/')) throw new Error(`Overlay file is a Git LFS pointer: ${relative}`);
  await mkdir(dirname(join(out, 'plates', relative)), {recursive: true});
  await writeFile(join(out, 'plates', relative), bytes);
  overlay.push({path: `plates/${relative}`, bytes: bytes.length, sha256: sha(bytes)});
}
if (!overlay.some(file => file.path === 'plates/index.html')) throw new Error('public/plates/index.html is missing.');
const record = {
  note: 'Living Plates overlay. Every other file on this site is the unchanged base release named below, verified against release.json. patchedBaseFiles lists the only base files changed: a route to Living Plates and the v1.1 final copy fixes.',
  baseRevision: manifest.revision,
  overlayRevision: process.env.GITHUB_SHA || 'local',
  files: overlay,
  patchedBaseFiles,
};
await writeFile(join(out, 'plates', 'overlay.json'), JSON.stringify(record, null, 2) + '\n');
console.log(`Overlay assembled: ${manifest.files.length} base files (${baseBytes} bytes) verified at ${manifest.revision}; ${patchedBaseFiles.length} base files patched; ${overlay.length} plate files added.`);
