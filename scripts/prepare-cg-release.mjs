/** Emit only the owner-authorized CG assessment assets. Never copy an archive tree. */
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile, mkdir, readdir, unlink } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export const cgManifestPath = 'assets/review/cg-publication.json';
export async function readCGManifest() {
  const manifest = JSON.parse(await readFile(cgManifestPath, 'utf8'));
  assert.equal(manifest.schemaVersion, 1);
  assert.equal(manifest.version, 'cg-loop03-retained04');
  assert.match(manifest.sourceRevision, /^[a-f0-9]{40}$/);
  assert(Array.isArray(manifest.assets) && manifest.assets.length > 0);
  const sources = new Set(), targets = new Set();
  for (const asset of manifest.assets) {
    assert.match(asset.source, /^(assets|context)\/[a-zA-Z0-9_./-]+\.(png|jpg|glb)$/);
    assert.match(asset.publicPath, /^cg\/[a-z0-9./-]+\.(png|jpg|glb)$/);
    assert(!asset.source.split('/').includes('..') && !asset.publicPath.split('/').includes('..'));
    assert(!sources.has(asset.source) && !targets.has(asset.publicPath), 'Duplicate CG selection');
    sources.add(asset.source); targets.add(asset.publicPath);
    assert(Number.isSafeInteger(asset.bytes) && asset.bytes > 0);
    assert.match(asset.sha256, /^[a-f0-9]{64}$/);
  }
  return manifest;
}
export async function verifyCGAsset(asset, path = asset.source) {
  const bytes = await readFile(path);
  assert.equal(bytes.length, asset.bytes, `CG byte count: ${path}`);
  assert.equal(createHash('sha256').update(bytes).digest('hex'), asset.sha256, `CG SHA-256: ${path}`);
  if (asset.publicPath.endsWith('.glb')) {
    assert.equal(bytes.subarray(0, 4).toString(), 'glTF', `Not a hydrated GLB: ${path}`);
    const json = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString());
    assert.equal(json.skins?.length || 0, 0, 'CG static model must not replace the mechanism rig');
    assert.equal(json.animations?.length || 0, 0);
    assert.equal([...(json.images || []), ...(json.buffers || [])].filter(value => value.uri).length, 0, 'GLB must be self contained');
  } else if (asset.publicPath.endsWith('.png')) {
    assert(bytes.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])), `Not a hydrated PNG: ${path}`);
  } else assert.equal(bytes.readUInt16BE(0), 0xffd8, `Not a hydrated JPEG: ${path}`);
  return bytes;
}
async function walk(dir, prefix = '') {
  let entries;
  try { entries = await readdir(dir, { withFileTypes: true }); } catch (error) { if (error.code === 'ENOENT') return []; throw error; }
  const result = [];
  for (const entry of entries) {
    const relative = prefix + entry.name;
    if (entry.isDirectory()) result.push(...await walk(dir + '/' + entry.name, relative + '/'));
    else result.push(relative);
  }
  return result;
}
export async function prepareCGRelease() {
  const manifest = await readCGManifest();
  // Validate the complete selection before writing any public file.
  for (const asset of manifest.assets) await verifyCGAsset(asset);
  const approved = new Set(manifest.assets.map(asset => asset.publicPath));
  for (const path of await walk('public/cg', 'cg/')) if (!approved.has(path)) await unlink('public/' + path);
  for (const asset of manifest.assets) {
    const bytes = await verifyCGAsset(asset);
    const target = 'public/' + asset.publicPath;
    await mkdir(dirname(target), { recursive: true });
    await writeFile(target, bytes);
  }
  console.log(`CG assessment allowlist: ${manifest.assets.length} verified assets, ${(manifest.assets.reduce((sum, asset) => sum + asset.bytes, 0) / 1e6).toFixed(1)} MB. Artistic acceptance remains pending.`);
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await prepareCGRelease();
