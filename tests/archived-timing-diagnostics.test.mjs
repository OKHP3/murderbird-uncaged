import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import {
  archivedBrowserCaptureConditionsDigest,
  archivedBrowserTimingDigest,
} from '../scripts/validate-device-performance-receipt.mjs';

const validator = fileURLToPath(new URL('../scripts/validate-device-performance-receipt.mjs', import.meta.url));
const acceptedReceipt = fileURLToPath(new URL(
  '../assets/audit/exterior-v1/geometry-correction-2026-09-27/browser-validation.json',
  import.meta.url,
));
const reportPath = (name) => `assets/audit/${name}/browser-validation.json`;

async function createArchive(t, reports) {
  const root = await mkdtemp(join(tmpdir(), 'archived-timing-diagnostics-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  const timing = {};
  const conditions = {};
  const inputs = {};

  async function writeJson(path, value) {
    const absolute = join(root, path);
    await mkdir(dirname(absolute), { recursive: true });
    const bytes = JSON.stringify(value);
    await writeFile(absolute, bytes);
    inputs[absolute] = bytes;
  }

  for (const [name, report] of Object.entries(reports)) {
    const path = reportPath(name);
    await writeJson(path, report);
    timing[path] = archivedBrowserTimingDigest(report);
    conditions[path] = archivedBrowserCaptureConditionsDigest(report);
  }
  await writeJson('tests/fixtures/archived-browser-timing-baseline.json', timing);
  await writeJson('tests/fixtures/archived-browser-capture-conditions-baseline.json', conditions);
  return { root, inputs };
}

function runValidator(cwd) {
  return spawnSync(process.execPath, [validator, acceptedReceipt], { cwd, encoding: 'utf8' });
}

test('archived context gaps produce advisory counts and leave evidence untouched', async (t) => {
  const { root, inputs } = await createArchive(t, {
    legacy: {
      browser: 'Chromium',
      renderer: 'UNKNOWN (renderer was never logged)',
      checks: [
        { name: 'Model turn', fpsP50: 40, frameMsP95: 25 },
        { scenario: 'Not recorded', frameTimeMs: 22, viewport: { width: 0, height: 900 } },
        { fps: 'not measured' },
      ],
    },
    complete: {
      browser: 'Chromium 152.0.0.0',
      webglRenderer: 'ANGLE',
      viewportCssPixels: { width: 1440, height: 900 },
      checkpoints: [{ stage: 'Reframe', performance: { frameTimeMs: 15 } }],
    },
    unmeasured: { status: 'NOT RUN', performance: { frameTimeMs: null } },
  });

  const result = runValidator(root);
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /^PASS /m);
  assert.deepEqual(result.stderr.trim().split('\n'), [
    'WARN assets/audit/legacy/browser-validation.json: archived timing context; '
      + 'browserVersion missing in 2 timing record(s); renderer unknown in 2 timing record(s); '
      + 'viewport missing in 1 timing record(s); viewport unknown in 1 timing record(s); '
      + 'workload unknown in 1 timing record(s).',
  ]);
  for (const [path, original] of Object.entries(inputs)) {
    assert.equal(await readFile(path, 'utf8'), original);
  }
});

test('a changed archived measurement still fails the frozen baseline check', async (t) => {
  const { root } = await createArchive(t, { legacy: { fps: 40 } });
  const report = join(root, reportPath('legacy'));
  await writeFile(report, '{"fps":41}');

  const result = runValidator(root);
  assert.equal(result.status, 1, result.stderr);
  assert.match(result.stderr, /timing values differ from the frozen baseline/);
  assert.doesNotMatch(result.stderr, /^WARN /m);
  assert.doesNotMatch(result.stdout, /^PASS /m);
  assert.equal(await readFile(report, 'utf8'), '{"fps":41}');
});
