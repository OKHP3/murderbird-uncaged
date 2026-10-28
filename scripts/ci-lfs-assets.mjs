/** Bounded CI hydration. Git metadata is authoritative; network requires --fetch. */
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';
import { appendFile, copyFile, lstat, mkdir, readFile, realpath, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const MAX_BYTES = 3_000_000_000;
const POINTER_PREFIX = 'version https://git-lfs.github.com/spec/v1';
const BUILD_MANIFESTS = [
  ['assets/review/cg-publication.json', 'assets', 'source'],
  ['assets/review/production-v37.json', 'assets', 'path'],
  ['provenance/story-media-publication-2026-09-27.json', 'assets', 'path'],
  ['provenance/iron-verdict-v3-release.json', 'assets', 'path'],
];
const CI_MANIFESTS = [...BUILD_MANIFESTS,
  ['provenance/presentation-package-2026-09-27.json', 'sources', 'path'],
  ['provenance/presentation-package-2026-09-27.json', 'outputs', 'path'],
];
const ACTIVE_SCRIPTS = new Set(['scripts/prepare-cg-release.mjs', 'scripts/verify-publication.mjs', 'scripts/verify-theme-release.mjs', 'scripts/verify-presentation.mjs']);
const BUILD_SOURCES = new Set(['scripts/prepare-cg-release.mjs', 'scripts/write-release-manifest.mjs', 'index.html', 'folio.html', 'cg.html']);
const binaryReference = /(['"`])((?:\.\.?\/)*(?:assets|context|public)\/[^'"`\r\n]+\.(?:glb|png|jpe?g|webp|avif|mp3|mp4|flac|wav|blend))\1/g;
const gitEnv = { ...process.env, GIT_LFS_SKIP_SMUDGE: '1', GIT_NO_LAZY_FETCH: '1', GIT_TERMINAL_PROMPT: '0', GCM_INTERACTIVE: 'never', GIT_OPTIONAL_LOCKS: '0' };
function git(root, args, input) {
  const result = spawnSync('git', ['-c', 'gc.auto=0', '-c', 'maintenance.auto=false', '-C', root, ...args], {
    env: gitEnv, input, maxBuffer: 32 * 1024 * 1024, windowsHide: true,
  });
  if (result.status !== 0) throw new Error(`git ${args[0]} failed: ${result.error?.message || result.stderr?.toString().trim()}`);
  return result.stdout;
}
export function safeRelative(value) {
  if (typeof value !== 'string' || !value || path.posix.isAbsolute(value) || /^[A-Za-z]:/.test(value)
      || /[\\\0\r\n]/.test(value) || value.split('/').some(p => !p || p === '.' || p === '..')) {
    throw new Error(`Unsafe asset path: ${JSON.stringify(value)}`);
  }
  return value;
}
export function parsePointer(bytes) {
  const text = bytes.toString('utf8');
  const match = /^version https:\/\/git-lfs\.github\.com\/spec\/v1\r?\noid sha256:([a-f0-9]{64})\r?\nsize (0|[1-9][0-9]*)\r?\n?$/.exec(text);
  if (!match) throw new Error('Expected a canonical Git LFS SHA-256 pointer');
  const size = Number(match[2]);
  if (!Number.isSafeInteger(size)) throw new Error('Invalid LFS object size');
  return { oid: match[1], size };
}
function checkScope(scope) {
  if (!['ci', 'build'].includes(scope)) throw new Error(`Unknown LFS scope: ${scope}`);
}
export function summarize(files, { scope = 'ci' } = {}) {
  checkScope(scope);
  const objects = new Map();
  for (const file of files) {
    safeRelative(file.path);
    if (!/^[a-f0-9]{64}$/.test(file.oid) || !Number.isSafeInteger(file.size) || file.size < 0) throw new Error('Invalid LFS object declaration');
    const object = objects.get(file.oid) || { oid: file.oid, size: file.size, paths: [] };
    if (object.size !== file.size) throw new Error(`Conflicting sizes for ${file.oid}`);
    object.paths.push(file.path); objects.set(file.oid, object);
  }
  const sorted = [...objects.values()].sort((a, b) => a.oid.localeCompare(b.oid));
  for (const object of sorted) object.paths.sort();
  const bytes = sorted.reduce((sum, object) => sum + object.size, 0);
  if (!Number.isSafeInteger(bytes) || bytes > MAX_BYTES) throw new Error(`CI LFS scope exceeds ${MAX_BYTES} bytes: ${bytes}`);
  const digest = createHash('sha256').update(sorted.map(o => `${o.oid} ${o.size}\n`).join('')).digest('hex');
  return { scope, files: [...files].sort((a, b) => a.path.localeCompare(b.path)), objects: sorted, bytes,
    objectCount: sorted.length, cacheKey: `ci-lfs-v2-${scope}-${digest}`, maxBytes: MAX_BYTES };
}
export async function createPlan(root, { scope = 'ci' } = {}) {
  checkScope(scope);
  const head = git(root, ['rev-parse', 'HEAD']).toString().trim();
  const tree = new Map(git(root, ['ls-tree', '-r', '-z', head]).toString().split('\0').filter(Boolean).map(line => {
    const split = line.indexOf('\t'), [mode, type, oid] = line.slice(0, split).split(' ');
    return [line.slice(split + 1), { mode, type, oid }];
  }));
  const readGit = name => {
    const entry = tree.get(safeRelative(name));
    if (!entry || entry.type !== 'blob' || !['100644', '100755'].includes(entry.mode)) throw new Error(`Missing regular tracked input: ${name}`);
    return git(root, ['cat-file', 'blob', entry.oid]);
  };
  const required = new Set(), declared = new Map();
  function add(name, metadata) {
    name = safeRelative(name); required.add(name);
    if (metadata && metadata.sha256 !== undefined && metadata.bytes !== undefined) {
      const previous = declared.get(name);
      if (previous && (previous.sha256 !== metadata.sha256 || previous.bytes !== metadata.bytes)) throw new Error(`Conflicting manifests: ${name}`);
      declared.set(name, metadata);
    }
  }
  const imports = scope === 'ci' ? [...tree.keys()].filter(p => /^provenance\/[^/]*-import-[^/]*\.json$/.test(p)) : [];
  if (scope === 'ci' && !imports.length) throw new Error('No import manifests found');
  for (const manifestPath of imports) {
    const manifest = JSON.parse(readGit(manifestPath));
    if (!Array.isArray(manifest.files)) throw new Error(`Invalid import manifest: ${manifestPath}`);
    for (const item of manifest.files) {
      safeRelative(item.destination);
      if (!['directory', 'symlink'].includes(item.type)) add(item.destination, item);
    }
  }
  for (const [manifestPath, collection, field] of scope === 'ci' ? CI_MANIFESTS : BUILD_MANIFESTS) {
    const items = JSON.parse(readGit(manifestPath))[collection];
    if (!Array.isArray(items) || !items.length) throw new Error(`Missing ${collection}: ${manifestPath}`);
    for (const item of items) add(item[field], item);
  }
  for (const name of tree.keys()) {
    if (name.startsWith('public/')) add(name);
    // Build uses runtime imports/publication selections. Full CI adds verifier
    // sources, imported masters and real test fixtures; preview needs none of those.
    const ciSource = scope === 'ci' && (/^tests\/.*\.test\.mjs$/.test(name) || ACTIVE_SCRIPTS.has(name));
    if (name !== 'tests/ci-lfs-assets.test.mjs' && (/^src\/.*\.[cm]?js$/.test(name) || BUILD_SOURCES.has(name) || ciSource)) {
      for (const match of readGit(name).toString().matchAll(binaryReference)) {
        if (match[2].includes('${')) throw new Error(`Dynamic binary reference needs an explicit manifest: ${name}: ${match[2]}`);
        const relative = match[2].startsWith('.') ? path.posix.normalize(path.posix.join(path.posix.dirname(name), match[2])) : match[2];
        // Tests also name fictitious evidence paths in validation assertions.
        // Only tracked binary references are fixtures; unchanged tests still
        // fail if a genuine required input is absent from the repository.
        if (name.startsWith('tests/') && !tree.has(relative)) continue;
        add(relative);
      }
    }
  }
  const paths = [...required].sort();
  for (const name of paths) {
    const entry = tree.get(name);
    if (!entry || entry.type !== 'blob' || !['100644', '100755'].includes(entry.mode)) throw new Error(`Missing regular required asset: ${name}`);
  }
  const attributes = git(root, ['check-attr', `--source=${head}`, '-z', 'filter', '--stdin'], Buffer.from(paths.join('\0') + '\0')).toString().split('\0');
  if (attributes.pop() !== '' || attributes.length !== paths.length * 3) throw new Error('Malformed Git attribute response');
  const selected = [], seen = new Set();
  for (let i = 0; i < attributes.length; i += 3) {
    const [name, attribute, filter] = attributes.slice(i, i + 3);
    if (!required.has(name) || seen.has(name) || attribute !== 'filter') throw new Error('Unexpected Git attribute response');
    seen.add(name);
    if (filter === 'lfs') selected.push(name);
  }
  const ids = [...new Set(selected.map(name => tree.get(name).oid))], blobs = new Map();
  const batch = ids.length ? git(root, ['cat-file', '--batch'], Buffer.from(ids.join('\n') + '\n')) : Buffer.alloc(0);
  let offset = 0;
  for (const id of ids) {
    const end = batch.indexOf(10, offset);
    const [oid, type, rawSize] = batch.subarray(offset, end).toString().split(' '), size = Number(rawSize);
    if (end < 0 || oid !== id || type !== 'blob' || !Number.isSafeInteger(size) || size < 0 || size > 1024 || batch[end + 1 + size] !== 10) throw new Error(`Invalid LFS pointer blob: ${id}`);
    blobs.set(id, parsePointer(batch.subarray(end + 1, end + 1 + size)));
    offset = end + 1 + size + 1;
  }
  if (offset !== batch.length) throw new Error('Unexpected Git batch output');
  const files = [];
  for (const name of selected) {
    const pointer = blobs.get(tree.get(name).oid);
    const metadata = declared.get(name);
    if (metadata && (metadata.sha256 !== pointer.oid || metadata.bytes !== pointer.size)) throw new Error(`Pointer differs from source manifest: ${name}`);
    files.push({ path: name, ...pointer });
  }
  return { schemaVersion: 2, head, ...summarize(files, { scope }) };
}
async function safeLocal(root, relative) {
  let current = root;
  for (const part of safeRelative(relative).split('/')) {
    current = path.join(current, part);
    try { if ((await lstat(current)).isSymbolicLink()) throw new Error(`Refusing symlink: ${current}`); }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
  }
  return current;
}
async function localCacheRoot(value) {
  // Inspect the supplied path before resolving it: realpath alone would hide a
  // junction/symlink. UNC shares are not an offline local source.
  if (typeof value !== 'string' || !path.isAbsolute(value) || /^[\\/]{2}/.test(value)
      || (process.platform === 'win32' && !/^[A-Za-z]:[\\/]/.test(value))
      || value.includes('\0') || value.split(/[\\/]/).some(part => part === '.' || part === '..')) {
    throw new Error('Cache source must be an absolute local directory without dot segments');
  }
  let current = path.parse(value).root;
  for (const part of value.slice(current.length).split(/[\\/]/).filter(Boolean)) {
    current = path.join(current, part);
    const info = await lstat(current);
    if (info.isSymbolicLink() || !info.isDirectory()) throw new Error(`Refusing non-directory or symlink cache source: ${current}`);
  }
  return realpath(current);
}
async function validatePayload(file, object) {
  let info;
  try { info = await lstat(file); } catch (error) { if (error.code === 'ENOENT') return 'missing'; throw error; }
  if (!info.isFile() || info.isSymbolicLink()) return 'not a regular file';
  if (info.size !== object.size) return `size ${info.size}, expected ${object.size}`;
  const hash = createHash('sha256'); let first = true;
  for await (const chunk of createReadStream(file)) {
    if (first && chunk.subarray(0, POINTER_PREFIX.length).toString() === POINTER_PREFIX) return 'LFS pointer instead of payload';
    first = false; hash.update(chunk);
  }
  return hash.digest('hex') === object.oid ? null : 'SHA-256 mismatch';
}
export function validateDownloadApproval(plan, { expectedHead, expectedPlanKey, maxDownloadBytes } = {}) {
  if (expectedHead !== plan.head) throw new Error('Download approval must name the exact current HEAD');
  if (expectedPlanKey !== plan.cacheKey) throw new Error('Download approval must name the exact current asset-plan key');
  if (!Number.isSafeInteger(maxDownloadBytes) || maxDownloadBytes < plan.bytes || maxDownloadBytes > MAX_BYTES) {
    throw new Error(`Download approval byte ceiling must cover ${plan.bytes} and not exceed ${MAX_BYTES}`);
  }
}
export async function hydrate(root, plan, { fetch = false, cacheSource, ...approval } = {}) {
  if (fetch && cacheSource !== undefined) throw new Error('Cache source is offline-only and cannot be combined with fetch');
  const externalCache = cacheSource === undefined ? null : await localCacheRoot(cacheSource);
  // Revalidate limits even for programmatic callers; CLI always regenerates its plan.
  plan = { ...plan, ...summarize(plan.files, { scope: plan.scope ?? 'ci' }) };
  if (!/^[a-f0-9]{40,64}$/.test(plan.head) || git(root, ['rev-parse', 'HEAD']).toString().trim() !== plan.head) throw new Error('Hydration plan must match current HEAD');
  const selected = new Set(plan.files.map(file => file.path));
  const indexBefore = git(root, ['ls-files', '--stage', '-z']);
  const staged = git(root, ['diff', '--cached', '--name-only', '--no-renames', '-z', 'HEAD']).toString().split('\0').filter(name => selected.has(name));
  if (staged.length) throw new Error(`Refusing selected staged changes: ${staged.join(', ')}`);
  const common = await realpath(git(root, ['rev-parse', '--path-format=absolute', '--git-common-dir']).toString().trim());
  const cacheFile = object => safeLocal(common, `lfs/objects/${object.oid.slice(0, 2)}/${object.oid.slice(2, 4)}/${object.oid}`);
  const pending = [], workingSources = new Map(), sources = new Map(), externalSources = new Set();
  for (const file of plan.files) {
    const target = await safeLocal(root, file.path);
    let info;
    try { info = await lstat(target); } catch (error) { if (error.code !== 'ENOENT') throw error; }
    if (info && !info.isFile()) throw new Error(`Refusing non-file asset: ${file.path}`);
    if (info && info.size <= 1024) {
      const bytes = await readFile(target);
      if (bytes.subarray(0, POINTER_PREFIX.length).toString() === POINTER_PREFIX) {
        const pointer = parsePointer(bytes);
        if (pointer.oid !== file.oid || pointer.size !== file.size) throw new Error(`Refusing edited pointer: ${file.path}`);
        pending.push({ file, target }); continue;
      }
    }
    if (info) {
      const reason = await validatePayload(target, file);
      if (reason) throw new Error(`Refusing edited non-pointer file: ${file.path} (${reason})`);
      workingSources.set(file.oid, target);
    } else pending.push({ file, target });
  }
  const inspectCache = async () => {
    const issues = [];
    for (const object of plan.objects) {
      // Existing local/Replit payloads need neither a cache entry nor a download.
      if (workingSources.has(object.oid)) { sources.set(object.oid, workingSources.get(object.oid)); continue; }
      let source = await cacheFile(object), reason = await validatePayload(source, object);
      // Only an absent local entry may use the explicit offline source. A
      // corrupt existing cache must stay visible for a separate repair.
      if (reason === 'missing' && externalCache) {
        source = await safeLocal(externalCache, `${object.oid.slice(0, 2)}/${object.oid.slice(2, 4)}/${object.oid}`);
        reason = await validatePayload(source, object);
        if (!reason) externalSources.add(object.oid);
        else reason = `external cache: ${reason}`;
      }
      if (reason) issues.push({ ...object, reason });
      else sources.set(object.oid, source);
    }
    return issues;
  };
  let issues = await inspectCache();
  // Even a warm-cache fill must match the reviewed revision, scope and ceiling.
  // Ordinary cache-only hydration needs no download approval.
  if (fetch) validateDownloadApproval(plan, approval);
  if (fetch && issues.length && issues.every(o => o.reason === 'missing')) {
    const includePaths = issues.map(o => o.paths[0]);
    for (const name of includePaths) if (/[,!*?\[\]]/.test(name) || name.trim() !== name) throw new Error(`Cannot fetch this path literally: ${name}`);
    for (let i = 0; i < includePaths.length; i += 40) {
      // Git LFS rejects zero and silently substitutes eight retries. One is its
      // supported minimum; allowance planning must include that possible retry.
      git(root, ['-c', 'lfs.fetchrecentalways=false', '-c', 'lfs.transfer.maxretries=1', '-c', 'lfs.concurrenttransfers=1',
        'lfs', 'fetch', `--include=${includePaths.slice(i, i + 40).join(',')}`, '--exclude=', 'origin', plan.head]);
    }
    issues = await inspectCache();
  }
  if (issues.length) throw new Error(`Missing/corrupt selected LFS objects: ${issues.length}/${plan.objects.length}. ${fetch ? 'Fetch did not supply verified objects; corrupt cache objects require explicit repair.' : 'No network requested; restore verified objects or explicitly use --fetch.'}\n${issues.slice(0, 20).map(o => `${o.oid} ${o.reason}: ${o.paths[0]}`).join('\n')}${issues.length > 20 ? '\nAdditional objects omitted from display.' : ''}`);
  // Complete all cache and destination checks before altering the working tree.
  for (const { file, target } of pending) {
    await mkdir(path.dirname(target), { recursive: true });
    await copyFile(sources.get(file.oid), target);
    const reason = await validatePayload(target, file);
    if (reason) throw new Error(`Hydrated asset verification failed: ${file.path} (${reason})`);
  }
  if (selected.size) {
    const names = [...selected], index = new Map(indexBefore.toString().split('\0').filter(Boolean).map(line => {
      const split = line.indexOf('\t'); return [line.slice(split + 1), line.slice(0, split).split(' ')[1]];
    }));
    const clean = ['-c', 'filter.lfs.process=git-lfs filter-process', '-c', 'filter.lfs.clean=git-lfs clean -- %f', '-c', 'filter.lfs.required=true', '-c', 'core.filemode=false'];
    // A stat-only refresh cannot correct a pointer-length index entry after
    // hydration. Prove the clean-filtered files equal the existing index, then
    // re-add only these literal paths to refresh their stat entries. This does
    // not change any staged content; assert every index OID/mode/stage afterward.
    const hashes = git(root, [...clean, 'hash-object', '--stdin-paths'], Buffer.from(names.map(name => JSON.stringify(name)).join('\n') + '\n')).toString().trim().split('\n');
    if (hashes.length !== names.length || names.some((name, i) => hashes[i].trim() !== index.get(name))) throw new Error('Clean-filtered selected assets differ from index; refusing refresh');
    if (!git(root, ['ls-files', '--stage', '-z']).equals(indexBefore)) throw new Error('Index changed during hydration; refusing index refresh');
    git(root, [...clean, 'add', '--pathspec-from-file=-', '--pathspec-file-nul'], Buffer.from(names.map(name => `:(literal)${name}`).join('\0') + '\0'));
  }
  if (!git(root, ['ls-files', '--stage', '-z']).equals(indexBefore)) throw new Error('Index content changed during refresh');
  return { scope: plan.scope, objects: plan.objectCount, bytes: plan.bytes, hydratedPaths: pending.length, alreadyHydratedPaths: plan.files.length - pending.length, workingTreeSourceObjects: workingSources.size, externalCacheSourceObjects: externalSources.size };
}
export async function main(args = process.argv.slice(2)) {
  const [command, ...options] = args;
  const approvalOptions = ['--expected-head=', '--expected-plan-key=', '--max-download-bytes='];
  const cacheSource = options.find(o => o.startsWith('--cache-source='))?.slice('--cache-source='.length);
  if (!['plan', 'hydrate'].includes(command) || options.some(o => !['--fetch', '--scope=ci', '--scope=build'].includes(o) && !['--cache-source=', ...approvalOptions].some(prefix => o.startsWith(prefix)))
      || ['--scope=', '--cache-source=', ...approvalOptions].some(prefix => options.filter(o => o.startsWith(prefix)).length > 1)
      || (cacheSource !== undefined && (!cacheSource || options.includes('--fetch') || !path.isAbsolute(cacheSource)))
      || (command === 'plan' && options.some(o => o === '--fetch' || ['--cache-source=', ...approvalOptions].some(prefix => o.startsWith(prefix))))
      || (!options.includes('--fetch') && options.some(o => approvalOptions.some(prefix => o.startsWith(prefix))))) {
    throw new Error('Usage: node scripts/ci-lfs-assets.mjs plan|hydrate [--scope=ci|--scope=build] [--cache-source=ABSOLUTE_LOCAL_OBJECTS_DIR | --fetch --expected-head=SHA --expected-plan-key=KEY --max-download-bytes=BYTES (hydrate only)]');
  }
  const scope = options.find(o => o.startsWith('--scope='))?.slice('--scope='.length) ?? 'ci';
  const root = await realpath(git(process.cwd(), ['rev-parse', '--show-toplevel']).toString().trim());
  const plan = await createPlan(root, { scope });
  const output = await safeLocal(root, '.local/ci-lfs-plan.json');
  await mkdir(path.dirname(output), { recursive: true });
  await writeFile(output, JSON.stringify(plan, null, 2) + '\n');
  if (process.env.GITHUB_OUTPUT) await appendFile(process.env.GITHUB_OUTPUT, `cache-key=${plan.cacheKey}\nbytes=${plan.bytes}\nobjects=${plan.objectCount}\n`);
  const value = prefix => options.find(o => o.startsWith(prefix))?.slice(prefix.length);
  const ceiling = value('--max-download-bytes=');
  const result = command === 'hydrate' ? await hydrate(root, plan, { fetch: options.includes('--fetch'), cacheSource,
    expectedHead: value('--expected-head='), expectedPlanKey: value('--expected-plan-key='),
    maxDownloadBytes: /^(0|[1-9][0-9]*)$/.test(ceiling ?? '') ? Number(ceiling) : NaN,
  }) : { head: plan.head, scope, objects: plan.objectCount, bytes: plan.bytes, paths: plan.files.length, cacheKey: plan.cacheKey };
  console.log(JSON.stringify(result));
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main().catch(error => { console.error(error.message); process.exitCode = 1; });
