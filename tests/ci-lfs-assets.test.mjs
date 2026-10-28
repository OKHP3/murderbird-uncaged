import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, rm, stat, symlink, realpath } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { execFileSync, spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createPlan, hydrate, MAX_BYTES, parsePointer, safeRelative, summarize, validateDownloadApproval } from '../scripts/ci-lfs-assets.mjs';

const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const pointer = bytes => `version https://git-lfs.github.com/spec/v1\noid sha256:${sha(bytes)}\nsize ${bytes.length}\n`;
function git(root, args) {
  return execFileSync('git', ['-c', `core.hooksPath=${path.join(root, '.disabled-hooks')}`, '-c', 'filter.lfs.process=', '-c', 'filter.lfs.required=false', '-c', 'filter.lfs.clean=', '-c', 'core.autocrlf=false', '-c', 'user.name=CI LFS Test', '-c', 'user.email=test@example.invalid', '-c', 'commit.gpgsign=false', '-C', root, ...args], { encoding: 'utf8', env: { ...process.env, GIT_LFS_SKIP_SMUDGE: '1', GIT_TERMINAL_PROMPT: '0' }, stdio: ['pipe', 'pipe', 'pipe'] });
}
async function fixture(t) {
  // macOS exposes its temp directory through /var -> /private/var. Tests need
  // the physical root; production intentionally refuses linked cache sources.
  const root = await realpath(await mkdtemp(path.join(tmpdir(), 'ci-lfs-assets-test-')));
  t.after(() => rm(root, { recursive: true, force: true }));
  const put = async (name, bytes) => { await mkdir(path.dirname(path.join(root, name)), { recursive: true }); await writeFile(path.join(root, name), bytes); };
  const json = (name, object) => put(name, JSON.stringify(object));
  const bytes = Buffer.from('selected model bytes'), testBytes = Buffer.from('test model bytes');
  const entry = name => ({ path: name, source: name, destination: name, type: 'file', bytes: bytes.length, sha256: sha(bytes) });
  await put('.gitattributes', '*.bin filter=lfs -text\n*.glb filter=lfs -text\n');
  await put('.gitignore', '.local/\n');
  await put('assets/model.bin', pointer(bytes)); await put('assets/model-copy.bin', pointer(bytes));
  await put('assets/archive.bin', pointer(Buffer.from('unselected archived data')));
  await put('assets/test.glb', pointer(testBytes));
  await put('tests/model.test.mjs', "const model = 'assets/test.glb'; const negativeEvidenceExample = 'assets/not-read.png';\n");
  await put('public/readme.txt', 'ordinary tracked public file');
  await json('provenance/fixture-import-2026.json', { files: [entry('assets/model.bin')] });
  for (const file of ['assets/review/cg-publication.json', 'assets/review/production-v37.json', 'provenance/story-media-publication-2026-09-27.json', 'provenance/iron-verdict-v3-release.json']) await json(file, { assets: [entry('assets/model-copy.bin')] });
  await json('provenance/presentation-package-2026-09-27.json', { sources: [entry('assets/model.bin')], outputs: [entry('assets/model-copy.bin')] });
  git(root, ['init', '-q']); git(root, ['add', '.']); git(root, ['commit', '-qm', 'fixture']);
  const cache = async (data, stored = data) => put(`.git/lfs/objects/${sha(data).slice(0, 2)}/${sha(data).slice(2, 4)}/${sha(data)}`, stored);
  const fillCache = async () => { await cache(bytes); await cache(testBytes); };
  return { root, put, json, bytes, testBytes, cache, fillCache };
}
const objectPath = (root, bytes) => path.join(root, sha(bytes).slice(0, 2), sha(bytes).slice(2, 4), sha(bytes));
async function externalCache(f) {
  const source = path.join(f.root, '.local', 'preserved-objects');
  for (const bytes of [f.bytes, f.testBytes, Buffer.from('unselected archived data')]) {
    const file = objectPath(source, bytes);
    await mkdir(path.dirname(file), { recursive: true });
    await writeFile(file, bytes);
  }
  return source;
}

test('pointer parsing rejects payloads, non-SHA256 pointers and unsafe sizes', () => {
  assert.equal(parsePointer(Buffer.from(pointer(Buffer.from('abc')))).size, 3);
  for (const content of ['ordinary media', pointer(Buffer.from('abc')).replace('sha256:', 'sha1:'), pointer(Buffer.from('abc')).replace('size 3', 'size 9007199254740992')]) assert.throws(() => parsePointer(Buffer.from(content)));
});

test('scope is deduplicated and cache key is stable across path ordering', () => {
  const oid = sha('a'), file = { path: 'assets/a.bin', oid, size: 1 };
  const a = summarize([file, { ...file, path: 'assets/b.bin' }]);
  const b = summarize([{ ...file, path: 'assets/b.bin' }, file]);
  assert.equal(a.objectCount, 1); assert.equal(a.bytes, 1); assert.equal(a.cacheKey, b.cacheKey);
  assert.throws(() => summarize([file, { ...file, path: 'assets/c.bin', size: 2 }]), /Conflicting/);
  assert.throws(() => summarize([{ ...file, size: MAX_BYTES + 1 }]), /exceeds/);
  for (const name of ['../asset.bin', '/asset.bin', 'C:/asset.bin', 'assets/../asset.bin', 'assets\\asset.bin', 'assets//asset.bin']) assert.throws(() => safeRelative(name), /Unsafe/);
});

test('plan selects manifests, public paths and actual test references, excluding archive bulk', async t => {
  const f = await fixture(t), plan = await createPlan(f.root);
  assert.deepEqual(plan.files.map(p => p.path), ['assets/model-copy.bin', 'assets/model.bin', 'assets/test.glb']);
  assert.equal(plan.objectCount, 2); assert.equal(plan.bytes, f.bytes.length + f.testBytes.length);
  const firstKey = plan.cacheKey;
  await f.put('docs/notes.md', 'non-media change'); git(f.root, ['add', '.']); git(f.root, ['commit', '-qm', 'docs']);
  assert.equal((await createPlan(f.root)).cacheKey, firstKey);
});

test('plan refuses unsafe destinations and source-manifest hash disagreement', async t => {
  const f = await fixture(t);
  await f.json('provenance/fixture-import-2026.json', { files: [{ destination: '../outside.bin', type: 'file' }] });
  git(f.root, ['add', '.']); git(f.root, ['commit', '-qm', 'unsafe']);
  await assert.rejects(createPlan(f.root), /Unsafe/);
  await f.json('provenance/fixture-import-2026.json', { files: [{ destination: 'assets/model.bin', type: 'file', sha256: '0'.repeat(64), bytes: f.bytes.length }] });
  git(f.root, ['add', '.']); git(f.root, ['commit', '-qm', 'mismatch']);
  await assert.rejects(createPlan(f.root), /Conflicting manifests|Pointer differs/);
});

test('a missing runtime import fails instead of being treated as a synthetic test example', async t => {
  const f = await fixture(t);
  await f.put('src/main.js', "import image from '../assets/missing.png';\n");
  git(f.root, ['add', '.']); git(f.root, ['commit', '-qm', 'missing runtime dependency']);
  await assert.rejects(createPlan(f.root), /Missing regular required asset: assets\/missing.png/);
  await assert.rejects(createPlan(f.root, { scope: 'build' }), /Missing regular required asset: assets\/missing.png/);
});

test('build scope includes real runtime references and skips imported masters and test-only fixtures', async t => {
  const f = await fixture(t), master = Buffer.from('import-only editable master'), runtime = Buffer.from('runtime glb bytes');
  await f.put('assets/source-master.bin', pointer(master));
  await f.json('provenance/fixture-import-2026.json', { files: [
    { destination: 'assets/model.bin', type: 'file', bytes: f.bytes.length, sha256: sha(f.bytes) },
    { destination: 'assets/source-master.bin', type: 'file', bytes: master.length, sha256: sha(master) },
  ] });
  await f.put('assets/runtime.glb', pointer(runtime));
  await f.put('src/main.js', "import model from '../assets/runtime.glb';\n");
  git(f.root, ['add', '.']); git(f.root, ['commit', '-qm', 'separate build and integrity inputs']);
  const full = await createPlan(f.root), build = await createPlan(f.root, { scope: 'build' });
  assert.equal(full.scope, 'ci'); assert.equal(build.scope, 'build');
  assert(full.files.some(f => f.path === 'assets/source-master.bin'));
  assert(full.files.some(f => f.path === 'assets/test.glb'));
  assert.deepEqual(build.files.map(f => f.path), ['assets/model-copy.bin', 'assets/runtime.glb']);
  assert.notEqual(full.cacheKey, build.cacheKey);
  assert.notEqual(summarize(build.files).cacheKey, summarize(build.files, { scope: 'build' }).cacheKey);
  await assert.rejects(createPlan(f.root, { scope: 'archive' }), /Unknown LFS scope/);
  // Neither imported master nor test model is cached or hydrated.
  await f.cache(f.bytes); await f.cache(runtime);
  assert.equal((await hydrate(f.root, build)).hydratedPaths, 2);
  assert.deepEqual(await readFile(path.join(f.root, 'assets/runtime.glb')), runtime);
  assert.equal((await readFile(path.join(f.root, 'assets/source-master.bin'))).toString(), pointer(master));
  assert.equal((await readFile(path.join(f.root, 'assets/test.glb'))).toString(), pointer(f.testBytes));
});

test('missing cache fails without a remote or network attempt and preserves pointers', async t => {
  const f = await fixture(t), plan = await createPlan(f.root), before = await readFile(path.join(f.root, 'assets/model.bin'));
  await assert.rejects(hydrate(f.root, plan), /Missing\/corrupt selected LFS objects: 2\/2.*No network requested/);
  assert.deepEqual(await readFile(path.join(f.root, 'assets/model.bin')), before);
});

test('corrupt cache and pointer masquerading as payload are rejected before writes', async t => {
  const f = await fixture(t), plan = await createPlan(f.root);
  await f.fillCache(); await f.cache(f.bytes, Buffer.alloc(f.bytes.length, 0));
  await assert.rejects(hydrate(f.root, plan), /SHA-256 mismatch/);
  const nested = Buffer.from(pointer(f.bytes)), nestedObject = { path: 'assets/model.bin', oid: sha(nested), size: nested.length };
  await f.put('assets/model.bin', pointer(nested));
  await f.cache(nested);
  await assert.rejects(hydrate(f.root, { head: plan.head, ...summarize([nestedObject]) }), /LFS pointer instead of payload/);
  assert.equal((await readFile(path.join(f.root, 'assets/model.bin'))).toString(), pointer(nested));
});

test('verified cache hydrates exact selected files and leaves unrelated archives alone', async t => {
  const f = await fixture(t), plan = await createPlan(f.root), archive = await readFile(path.join(f.root, 'assets/archive.bin'));
  await f.fillCache(); const result = await hydrate(f.root, plan);
  assert.equal(result.hydratedPaths, 3);
  assert.deepEqual(await readFile(path.join(f.root, 'assets/model.bin')), f.bytes);
  assert.deepEqual(await readFile(path.join(f.root, 'assets/model-copy.bin')), f.bytes);
  assert.deepEqual(await readFile(path.join(f.root, 'assets/archive.bin')), archive);
  assert.equal((await hydrate(f.root, plan)).hydratedPaths, 0);
});

test('edited non-pointers and changed pointers are preserved and fail preflight', async t => {
  const f = await fixture(t), plan = await createPlan(f.root);
  await f.fillCache(); await f.put('assets/model.bin', 'owner local edit');
  await assert.rejects(hydrate(f.root, plan), /Refusing edited non-pointer/);
  assert.equal((await readFile(path.join(f.root, 'assets/model.bin'))).toString(), 'owner local edit');
  assert.equal((await readFile(path.join(f.root, 'assets/model-copy.bin'))).toString(), pointer(f.bytes));
  await f.put('assets/model.bin', pointer(Buffer.from('different model')));
  await assert.rejects(hydrate(f.root, plan), /Refusing edited pointer/);
});

test('verified existing payloads satisfy missing cache without fetching and hydrate selected duplicates', async t => {
  const f = await fixture(t), plan = await createPlan(f.root);
  await f.put('assets/model.bin', f.bytes); await f.put('assets/test.glb', f.testBytes);
  // No cache or remote exists. Even explicit fetch must be unnecessary.
  const result = await hydrate(f.root, plan, { fetch: true, expectedHead: plan.head, expectedPlanKey: plan.cacheKey, maxDownloadBytes: plan.bytes });
  assert.equal(result.hydratedPaths, 1); assert.equal(result.workingTreeSourceObjects, 2);
  assert.deepEqual(await readFile(path.join(f.root, 'assets/model-copy.bin')), f.bytes);
});

test('download approval rejects missing, stale or enlarged scope before any remote access', async t => {
  const f = await fixture(t), plan = await createPlan(f.root);
  const approved = { expectedHead: plan.head, expectedPlanKey: plan.cacheKey, maxDownloadBytes: plan.bytes };
  const original = await readFile(path.join(f.root, 'assets/model.bin'));
  for (const approval of [{}, { ...approved, expectedHead: '0'.repeat(40) }, { ...approved, expectedPlanKey: 'old-plan' },
    { ...approved, maxDownloadBytes: plan.bytes - 1 }, { ...approved, maxDownloadBytes: MAX_BYTES + 1 },
    { ...approved, maxDownloadBytes: NaN }, { ...approved, maxDownloadBytes: String(plan.bytes) }]) {
    await assert.rejects(hydrate(f.root, plan, { fetch: true, ...approval }), /Download approval/);
  }
  assert.deepEqual(await readFile(path.join(f.root, 'assets/model.bin')), original);
  await f.fillCache();
  await assert.rejects(hydrate(f.root, plan, { fetch: true, ...approved, expectedHead: '0'.repeat(40) }), /Download approval/);
  assert.doesNotThrow(() => validateDownloadApproval(plan, approved));
  assert.equal((await hydrate(f.root, plan, { fetch: true, ...approved })).hydratedPaths, plan.files.length);
});

test('CLI rejects malformed and duplicate download approvals without changing payloads or index', async t => {
  const f = await fixture(t), plan = await createPlan(f.root);
  const helper = fileURLToPath(new URL('../scripts/ci-lfs-assets.mjs', import.meta.url));
  const before = git(f.root, ['ls-files', '--stage', '-z']);
  const original = await readFile(path.join(f.root, 'assets/model.bin'));
  const common = ['hydrate', '--fetch', `--expected-head=${plan.head}`, `--expected-plan-key=${plan.cacheKey}`];
  for (const options of [common, ...['-1', '1e9', '123abc', '9007199254740992'].map(n => [...common, `--max-download-bytes=${n}`]),
    [...common, `--max-download-bytes=${plan.bytes}`, `--expected-head=${plan.head}`],
    ['plan', '--fetch'], ['hydrate', `--expected-head=${plan.head}`]]) {
    const result = spawnSync(process.execPath, [helper, ...options], { cwd: f.root, encoding: 'utf8', windowsHide: true,
      env: { ...process.env, GIT_LFS_SKIP_SMUDGE: '1', GIT_TERMINAL_PROMPT: '0' } });
    assert.equal(result.status, 1, result.stderr);
    assert.match(result.stderr, /Download approval|Usage:/);
  }
  assert.equal(git(f.root, ['ls-files', '--stage', '-z']), before);
  assert.deepEqual(await readFile(path.join(f.root, 'assets/model.bin')), original);
});

test('approved fetch uses only selected objects from a local file remote', async t => {
  const f = await fixture(t), plan = await createPlan(f.root);
  const remote = path.join(f.root, '.local', 'origin.git');
  git(f.root, ['init', '--bare', '-q', remote]);
  git(f.root, ['remote', 'add', 'origin', pathToFileURL(remote).href]);
  for (const bytes of [f.bytes, f.testBytes, Buffer.from('unselected archived data')]) {
    const oid = sha(bytes);
    await f.put(`.local/origin.git/lfs/objects/${oid.slice(0, 2)}/${oid.slice(2, 4)}/${oid}`, bytes);
  }
  const result = await hydrate(f.root, plan, { fetch: true, expectedHead: plan.head, expectedPlanKey: plan.cacheKey, maxDownloadBytes: plan.bytes });
  assert.equal(result.hydratedPaths, 3);
  assert.deepEqual(await readFile(path.join(f.root, 'assets/model.bin')), f.bytes);
  assert.deepEqual(await readFile(path.join(f.root, 'assets/test.glb')), f.testBytes);
  assert.equal((await readFile(path.join(f.root, 'assets/archive.bin'))).toString(), pointer(Buffer.from('unselected archived data')));
  const archiveOid = sha(Buffer.from('unselected archived data'));
  await assert.rejects(readFile(path.join(f.root, '.git/lfs/objects', archiveOid.slice(0, 2), archiveOid.slice(2, 4), archiveOid)), { code: 'ENOENT' });
});

test('hydration keeps LFS status clean and preserves unrelated staged content', async t => {
  const f = await fixture(t), plan = await createPlan(f.root);
  await f.put('public/readme.txt', 'unrelated staged edit');
  git(f.root, ['add', 'public/readme.txt']);
  const before = git(f.root, ['ls-files', '--stage', '-z']);
  await f.fillCache(); await hydrate(f.root, plan);
  assert.equal(git(f.root, ['ls-files', '--stage', '-z']), before);
  const status = execFileSync('git', ['-c', 'filter.lfs.process=git-lfs filter-process', '-c', 'filter.lfs.clean=git-lfs clean -- %f', '-c', 'filter.lfs.required=true', '-C', f.root,
    'status', '--porcelain', '--', ...plan.files.map(f => f.path)], { encoding: 'utf8', windowsHide: true });
  assert.equal(status, '');
  assert.equal(git(f.root, ['diff', '--cached', '--name-only']).trim(), 'public/readme.txt');
});

test('selected staged edits fail before hydration and retain their exact index and working bytes', async t => {
  const f = await fixture(t), plan = await createPlan(f.root), edited = pointer(Buffer.from('staged user replacement'));
  await f.put('assets/model.bin', edited); git(f.root, ['add', 'assets/model.bin']);
  const before = git(f.root, ['ls-files', '--stage', '-z']);
  await assert.rejects(hydrate(f.root, plan, { fetch: true }), /Refusing selected staged changes/);
  assert.equal(git(f.root, ['ls-files', '--stage', '-z']), before);
  assert.equal((await readFile(path.join(f.root, 'assets/model.bin'))).toString(), edited);
  assert.equal((await readFile(path.join(f.root, 'assets/model-copy.bin'))).toString(), pointer(f.bytes));
});

test('offline external cache hydrates only selected paths and preserves source files and unrelated staged work', async t => {
  const f = await fixture(t), plan = await createPlan(f.root), source = await externalCache(f);
  const archive = Buffer.from('unselected archived data');
  const originalSources = await Promise.all([f.bytes, f.testBytes, archive].map(async bytes => ({
    file: objectPath(source, bytes), bytes, modified: (await stat(objectPath(source, bytes))).mtimeMs,
  })));
  await f.put('public/readme.txt', 'owner staged work'); git(f.root, ['add', 'public/readme.txt']);
  const before = git(f.root, ['ls-files', '--stage', '-z']);
  assert.equal(git(f.root, ['remote']), '');
  const result = await hydrate(f.root, plan, { cacheSource: source });
  assert.equal(result.externalCacheSourceObjects, 2); assert.equal(result.hydratedPaths, 3);
  for (const file of plan.files) assert.equal(sha(await readFile(path.join(f.root, file.path))), file.oid);
  assert.equal((await readFile(path.join(f.root, 'assets/archive.bin'))).toString(), pointer(archive));
  assert.equal(git(f.root, ['ls-files', '--stage', '-z']), before);
  assert.equal(git(f.root, ['diff', '--cached', '--name-only']).trim(), 'public/readme.txt');
  for (const original of originalSources) {
    assert.deepEqual(await readFile(original.file), original.bytes);
    assert.equal((await stat(original.file)).mtimeMs, original.modified);
  }
  await assert.rejects(readFile(objectPath(path.join(f.root, '.git/lfs/objects'), archive)), { code: 'ENOENT' });
  assert.equal((await hydrate(f.root, plan, { cacheSource: source })).hydratedPaths, 0);
});

test('missing or corrupt external content fails complete preflight without changing any selected path or index', async t => {
  for (const failure of ['missing', 'corrupt']) {
    const f = await fixture(t), plan = await createPlan(f.root), source = await externalCache(f);
    const last = plan.objects.at(-1), file = path.join(source, last.oid.slice(0, 2), last.oid.slice(2, 4), last.oid);
    if (failure === 'missing') await rm(file); else await writeFile(file, Buffer.alloc(last.size, 0));
    const before = git(f.root, ['ls-files', '--stage', '-z']);
    await assert.rejects(hydrate(f.root, plan, { cacheSource: source }), /external cache: missing|external cache: SHA-256 mismatch/);
    for (const asset of plan.files) assert.deepEqual(parsePointer(await readFile(path.join(f.root, asset.path))), { oid: asset.oid, size: asset.size });
    assert.equal(git(f.root, ['ls-files', '--stage', '-z']), before);
  }
  const f = await fixture(t), source = await externalCache(f), nested = Buffer.from(pointer(f.bytes));
  await f.put('assets/model.bin', pointer(nested));
  const file = objectPath(source, nested); await mkdir(path.dirname(file), { recursive: true }); await writeFile(file, nested);
  const plan = { head: git(f.root, ['rev-parse', 'HEAD']).trim(), ...summarize([{ path: 'assets/model.bin', oid: sha(nested), size: nested.length }]) };
  await assert.rejects(hydrate(f.root, plan, { cacheSource: source }), /LFS pointer instead of payload/);
  assert.equal((await readFile(path.join(f.root, 'assets/model.bin'))).toString(), pointer(nested));
});

test('external source cannot mask corrupt local cache or overwrite selected owner edits', async t => {
  const f = await fixture(t), plan = await createPlan(f.root), source = await externalCache(f);
  await f.cache(f.bytes, Buffer.alloc(f.bytes.length, 0));
  await assert.rejects(hydrate(f.root, plan, { cacheSource: source }), /SHA-256 mismatch/);
  assert.equal((await readFile(path.join(f.root, 'assets/model.bin'))).toString(), pointer(f.bytes));
  await f.put('assets/model.bin', 'owner changed media');
  await assert.rejects(hydrate(f.root, plan, { cacheSource: source }), /Refusing edited non-pointer/);
  assert.equal((await readFile(path.join(f.root, 'assets/model.bin'))).toString(), 'owner changed media');
});

test('external cache refuses relative, network, non-directory and linked source paths before hydration', async t => {
  const f = await fixture(t), plan = await createPlan(f.root), source = await externalCache(f);
  for (const invalid of ['', '.local/preserved-objects', '//server/share', '\\\\server\\share', path.join(source, sha(f.bytes).slice(0, 2), sha(f.bytes).slice(2, 4), sha(f.bytes)), source + '/../preserved-objects']) {
    await assert.rejects(hydrate(f.root, plan, { cacheSource: invalid }), /absolute local directory|non-directory or symlink/);
  }
  if (process.platform === 'win32') await assert.rejects(hydrate(f.root, plan, { cacheSource: '\\drive-relative-cache' }), /absolute local directory/);
  const linked = path.join(f.root, '.local', 'linked-objects');
  await symlink(source, linked, process.platform === 'win32' ? 'junction' : 'dir');
  await assert.rejects(hydrate(f.root, plan, { cacheSource: linked }), /symlink cache source/);
  await assert.rejects(hydrate(f.root, plan, { cacheSource: path.join(linked, sha(f.bytes).slice(0, 2)) }), /symlink cache source/);
  const nested = path.join(f.root, '.local', 'nested-source'); await mkdir(nested);
  await symlink(path.join(source, sha(f.bytes).slice(0, 2)), path.join(nested, sha(f.bytes).slice(0, 2)), process.platform === 'win32' ? 'junction' : 'dir');
  await assert.rejects(hydrate(f.root, plan, { cacheSource: nested }), /Refusing symlink/);
  await assert.rejects(hydrate(f.root, plan, { cacheSource: source, fetch: true }), /offline-only/);
  assert.equal((await readFile(path.join(f.root, 'assets/model.bin'))).toString(), pointer(f.bytes));
});

test('CLI accepts one offline cache source and rejects conflicting, duplicate and malformed source options', async t => {
  const f = await fixture(t), source = await externalCache(f);
  const helper = fileURLToPath(new URL('../scripts/ci-lfs-assets.mjs', import.meta.url));
  const sourceOption = `--cache-source=${source}`, before = git(f.root, ['ls-files', '--stage', '-z']);
  for (const options of [['hydrate', '--cache-source='], ['hydrate', '--cache-source=relative'],
    ['hydrate', sourceOption, sourceOption], ['hydrate', sourceOption, '--fetch'], ['plan', sourceOption],
    ['hydrate', sourceOption, '--expected-head=invalid']]) {
    const result = spawnSync(process.execPath, [helper, ...options], { cwd: f.root, encoding: 'utf8', windowsHide: true });
    assert.equal(result.status, 1, result.stderr); assert.match(result.stderr, /Usage:/);
  }
  assert.equal(git(f.root, ['ls-files', '--stage', '-z']), before);
  assert.equal((await readFile(path.join(f.root, 'assets/model.bin'))).toString(), pointer(f.bytes));
  const result = spawnSync(process.execPath, [helper, 'hydrate', sourceOption], { cwd: f.root, encoding: 'utf8', windowsHide: true });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(JSON.parse(result.stdout).externalCacheSourceObjects, 2);
});
