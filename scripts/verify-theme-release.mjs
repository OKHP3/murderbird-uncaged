import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';

// Verify hydrated LFS media and the actual Pages payload, not just pointers.
const root = process.cwd();
const release = JSON.parse(await readFile(path.join(root, 'provenance/iron-verdict-v3-release.json'), 'utf8'));
const expected = new Set(['audio/iron-verdict-v3/full-song.mp3', 'audio/iron-verdict-v3/seamless-loop.flac', 'audio/iron-verdict-v3/lyrics.txt']);
assert.equal(release.assets.length, expected.size, 'Release must identify exactly the approved runtime copies');
for (const asset of release.assets) {
  const relative = asset.path.replace(/^public\//, '');
  assert(expected.delete(relative), `Unexpected or duplicate release asset: ${asset.path}`);
  for (const folder of ['public', 'dist']) {
    const bytes = await readFile(path.join(root, folder, relative));
    assert.equal(bytes.length, asset.bytes, `${folder}/${relative}: incorrect size or unhydrated LFS pointer`);
    assert.equal(createHash('sha256').update(bytes).digest('hex'), asset.sha256, `${folder}/${relative}: hash mismatch`);
  }
}
async function files(directory, prefix = '') {
  const result = [];
  for (const item of await readdir(directory, { withFileTypes: true })) {
    const name = path.posix.join(prefix, item.name);
    if (item.isDirectory()) result.push(...await files(path.join(directory, item.name), name));
    else result.push(name);
  }
  return result;
}
const built = await files(path.join(root, 'dist'));
const audio = built.filter(name => /\.(?:mp3|flac|wav|m4a|ogg)$/i.test(name)).sort();
// The separately preserved story folio has two explicitly released historical
// demos. Identify their emitted bytes; do not allow arbitrary additional audio.
const folio = JSON.parse(await readFile(path.join(root, 'provenance/story-media-publication-2026-09-27.json'), 'utf8'));
const folioAudio = [];
for (const asset of folio.assets.filter(asset => /\.mp3$/.test(asset.path))) {
  const source = await readFile(path.join(root, asset.path));
  assert.equal(source.length, asset.bytes, `Unhydrated story audio: ${asset.path}`);
  assert.equal(createHash('sha256').update(source).digest('hex'), asset.sha256);
  const matches = [];
  for (const name of audio.filter(name => name.startsWith('assets/'))) {
    const bytes = await readFile(path.join(root, 'dist', name));
    if (createHash('sha256').update(bytes).digest('hex') === asset.sha256) matches.push(name);
  }
  assert.equal(matches.length, 1, `Expected one emitted story audio copy: ${asset.path}`);
  folioAudio.push(matches[0]);
}
assert.deepEqual(audio, [...release.assets.filter(asset => /\.(mp3|flac)$/.test(asset.path)).map(asset => asset.path.slice('public/'.length)), ...folioAudio].sort(), 'Unexpected built audio');
for (const name of built) {
  assert(!/(?:^|\/)(?:\.local|provenance|stems|tools|research|Backup)(?:\/|$)|\.(?:sesx|rpp|safetensors|pt|ckpt)$/i.test(name), `Private production file in build: ${name}`);
  if (/\.(?:html|js|css|json)$/i.test(name)) {
    const text = await readFile(path.join(root, 'dist', name), 'utf8');
    assert(!/\/__theme-preview\/|\.local\/theme-production|LOCAL LISTENING PREVIEW/.test(text), `Private preview reference in build: ${name}`);
  }
}
console.log(`Theme release verified: ${audio.length} hydrated audio files; ${built.length} intended build files.`);
