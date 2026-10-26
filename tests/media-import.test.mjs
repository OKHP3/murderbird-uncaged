import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtemp, mkdir, copyFile, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

const python = process.env.PYTHON ?? (process.platform === 'win32' ? 'python' : 'python3');

async function fixture(t, count = 1) {
  const root = await mkdtemp(join(tmpdir(), 'murderbird-media-import-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  await mkdir(join(root, 'scripts'));
  await mkdir(join(root, 'provenance'));
  await copyFile(new URL('../scripts/verify-media-import.py', import.meta.url), join(root, 'scripts/verify-media-import.py'));
  const globalConfig = join(root, 'empty-global.gitconfig');
  await writeFile(globalConfig, '');
  const env = { ...process.env, GIT_CONFIG_GLOBAL: globalConfig, GIT_CONFIG_NOSYSTEM: '1' };
  delete env.GIT_DIR;
  delete env.GIT_WORK_TREE;
  const init = spawnSync('git', ['init', '--quiet'], { cwd: root, env });
  assert.equal(init.status, 0, init.stderr?.toString());
  await writeFile(join(root, '.gitattributes'), '*.bin -text\n');
  // Real fixture paths fit ordinary Windows limits. Git's newline/long-path
  // protocol is exercised separately without creating illegal NTFS names.
  const directory = 'assets/inventory spaces unicode-é/one/two/three';
  await mkdir(join(root, directory), { recursive: true });
  const bytes = Buffer.from('preserved source bytes');
  const sha256 = createHash('sha256').update(bytes).digest('hex');
  const files = [];
  for (let index = 0; index < count; index++) {
    const destination = `${directory}/${index}-spaces unicode-é-${'x'.repeat(48)}.bin`;
    await writeFile(join(root, destination), bytes);
    files.push({ destination, type: 'file', bytes: bytes.length, sha256 });
  }
  await writeFile(join(root, 'provenance/test-import-fixture.json'), JSON.stringify({ files }));
  return { root, env, files };
}

function verify({ root, env }) {
  const result = spawnSync(python, ['scripts/verify-media-import.py'], {
    cwd: root, env, encoding: 'utf8', timeout: 15_000, maxBuffer: 4 * 1024 * 1024,
  });
  assert.ifError(result.error);
  return { status: result.status, report: JSON.parse(result.stdout) };
}

test('large media inventory completes without pipe backpressure and preserves NUL-delimited paths', async (t) => {
  const data = await fixture(t, 2048);
  assert.ok(Buffer.byteLength(data.files.map(file => file.destination).join('\0')) > 200_000);
  const result = verify(data);
  assert.equal(result.status, 0);
  assert.equal(result.report.verified_entries, 2048);
  assert.equal(result.report.total_entries, 2048);
  assert.deepEqual(result.report.errors, []);
});

test('Git attribute protocol preserves long Unicode and newline paths on every platform', async (t) => {
  const data = await fixture(t);
  const paths = Array.from({ length: 1024 }, (_, index) =>
    `assets/${'long inventory segment '.repeat(7)}/${index}-unicode-é-newline\n${'x'.repeat(75)}.bin`);
  assert.ok(Buffer.byteLength(paths.join('\0')) > 200_000);
  const check = (input) => {
    const result = spawnSync(python, ['-c',
      "import json, runpy, sys; from pathlib import Path; check = runpy.run_path('scripts/verify-media-import.py')['text_attribute_errors']; print(json.dumps(check(Path.cwd(), json.load(sys.stdin))))"], {
      cwd: data.root, env: data.env, input: JSON.stringify(input), encoding: 'utf8', timeout: 15_000,
      maxBuffer: 4 * 1024 * 1024,
    });
    assert.ifError(result.error);
    assert.equal(result.status, 0, result.stderr);
    return JSON.parse(result.stdout);
  };
  assert.deepEqual(check(paths), []);
  await writeFile(join(data.root, '.gitattributes'), '*.bin text\n');
  const errors = check(paths.slice(0, 2));
  assert.equal(errors.length, 2);
  for (const [index, error] of errors.entries()) {
    assert.equal(error, `Imported file must have Git text=unset: ${paths[index]} (text=set)`);
  }
});

test('media verification still rejects text conversion attributes', async (t) => {
  const data = await fixture(t);
  await writeFile(join(data.root, '.gitattributes'), '*.bin text\n');
  const result = verify(data);
  assert.equal(result.status, 1);
  assert.match(result.report.errors.join('\n'), /must have Git text=unset/);
});

test('media verification still rejects altered source bytes', async (t) => {
  const data = await fixture(t);
  await writeFile(join(data.root, data.files[0].destination), 'altered source bytes!!');
  const result = verify(data);
  assert.equal(result.status, 1);
  assert.equal(result.report.verified_entries, 0);
  assert.ok(result.report.errors.some(error => error.includes(data.files[0].destination)));
});
