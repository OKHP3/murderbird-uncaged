/**
 * Focused T14 failure/recovery checks for the current exhibit.
 * Run against loopback dev preview with the already installed Playwright module:
 *   node scripts/verify-recovery-v4.mjs /absolute/path/to/playwright/index.mjs
 * Optional UNCAGED_URL selects another loopback preview. This is QA tooling,
 * not an application dependency.
 */
import assert from 'node:assert/strict';
import { createHash, randomUUID } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

if (!process.argv[2]) throw new Error('Pass the already installed Playwright entry module as argv[2].');
const { chromium } = await import(pathToFileURL(process.argv[2]).href);
const base = process.env.UNCAGED_URL || 'http://127.0.0.1:5174/';
if (!['127.0.0.1', 'localhost'].includes(new URL(base).hostname)) {
  throw new Error('Recovery QA is restricted to a loopback preview.');
}

const out = path.resolve(process.env.UNCAGED_RECOVERY_AUDIT || 'assets/audit/regression-v4');
const modelPath = process.env.UNCAGED_MODEL || 'assets/models/uncaged-alignment-v3/murderbird-alignment-v3.glb';
const sourcePaths = [modelPath, 'package-lock.json', 'src/main.js', 'src/scene/fallback.js',
  'src/scene/presence-exhibit.js', 'src/scene/exhibit.js', 'src/audio/theme-player.js',
  'scripts/verify-recovery-v4.mjs'];
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const sourceHashes = async () => Object.fromEntries(await Promise.all(sourcePaths.map(async file => [file, hash(await readFile(file))])));
const sourceSha256 = await sourceHashes();
await mkdir(out, { recursive: true });
const browser = await chromium.launch({
  headless: true,
  args: process.env.UNCAGED_SOFTWARE_GL === '1'
    ? ['--enable-webgl', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader']
    : [],
});
const report = {
  generatedAt: new Date().toISOString(),
  url: base,
  browser: browser.version(),
  node: process.version,
  softwareGlRequested: process.env.UNCAGED_SOFTWARE_GL === '1',
  sourceSha256,
  servedModels: [],
  browserEvents: [],
  forcedFailures: [],
  checks: [],
  errors: [],
  limits: 'Automated loopback regression only; no physical-device, screen-reader, human media or deployment acceptance.',
};
const pages = [];
const pendingModelReads = [];

function observe(page, label) {
  page.on('pageerror', error => report.errors.push({ page: label, type: 'pageerror', message: error.message }));
  page.on('console', message => {
    const location = message.location()?.url;
    if (message.type() === 'error') {
      report.browserEvents.push({ page: label, type: 'console', message: message.text(), url: location });
    }
  });
  page.on('requestfailed', request => {
    // Retain every resource error, including failures forced by this test.
    // Do not suppress later real failures merely because a URL failed earlier.
    report.browserEvents.push({ page: label, type: 'requestfailed', url: request.url(), error: request.failure()?.errorText });
  });
  page.on('response', response => {
    if (new URL(response.url()).pathname.endsWith('.glb') && response.ok()) {
      pendingModelReads.push(response.body().then(bytes => {
        const sha256 = hash(bytes);
        report.servedModels.push({ page: label, url: response.url(), sha256, bytes: bytes.length });
        assert.equal(sha256, sourceSha256[modelPath], 'served GLB does not match the declared local candidate');
      }).catch(error => report.errors.push({ page: label, type: 'model-identity', message: error.message })));
    }
  });
}

function recordForcedFailure(request, reason) {
  report.forcedFailures.push({ at: new Date().toISOString(), url: request.url(), reason });
}

async function setup(page, label) {
  pages.push(page);
  observe(page, label);
  await page.route('**/*googletagmanager.com/**', route => route.fulfill({ status: 200, contentType: 'text/javascript', body: '' }));
  await page.goto(base);
  await page.locator('#loading').waitFor({ state: 'hidden', timeout: 30000 });
}

async function check(name, fn) {
  try {
    const detail = await fn();
    report.checks.push({ name, status: 'passed', detail });
  } catch (error) {
    report.checks.push({ name, status: 'failed', error: error.message });
    throw error;
  }
}

try {
  const model = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  let modelAttempts = 0;
  await model.route('**/*.glb', async (route, request) => {
    modelAttempts++;
    if (modelAttempts <= 2) {
      recordForcedFailure(request, 'first two model loads fail');
      await route.abort('failed');
    }
    else await route.continue();
  });
  await setup(model, 'repeated-model-failure');
  await check('model failure remains usable through a later successful retry', async () => {
    assert.match(await model.locator('#render-label').innerText(), /ILLUSTRATED/);
    assert.equal(await model.locator('#retry').isVisible(), true);
    assert.equal(await model.locator('#focus-part').isDisabled(), true);
    await model.locator('[data-part="guard"]').click();
    assert.match(await model.locator('#detail').innerText(), /flightless/i);
    await model.locator('#retry').click();
    await model.locator('#loading').waitFor({ state: 'hidden', timeout: 30000 });
    assert.match(await model.locator('#render-label').innerText(), /ILLUSTRATED/);
    assert.equal(await model.locator('#retry').isVisible(), true);
    assert.equal(await model.locator('#focus-part').isDisabled(), true);
    await model.locator('#retry').click();
    await model.locator('#loading').waitFor({ state: 'hidden', timeout: 30000 });
    await model.waitForFunction(() => document.querySelector('#scene canvas') && window.__uncaged?.metrics().kind === 'webgl');
    await model.locator('[data-part="guard"]').click();
    assert.equal(await model.locator('#focus-part').isDisabled(), false);
    assert.equal(await model.locator('#retry').isHidden(), true);
    return { failedLoads: 2, recoveredRenderer: await model.evaluate(() => window.__uncaged.metrics().kind) };
  });

  const image = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await image.route('**/*.glb', async (route, request) => { recordForcedFailure(request, 'force illustrated view'); await route.abort('failed'); });
  await image.route('**/*maker-preview*', async (route, request) => { recordForcedFailure(request, 'Maker preview unavailable'); await route.abort('failed'); });
  await setup(image, 'fallback-image-failure');
  await check('failed fallback artwork explains its absence and supporting content still opens', async () => {
    await image.locator('[data-era="maker"]').click();
    const preview = image.locator('.illustrated-view img');
    await image.waitForFunction(() => document.querySelector('.illustrated-view img')?.naturalWidth === 0
      && document.querySelector('.illustrated-view img')?.hidden === true);
    assert.match(await image.locator('.illustrated-caption').innerText(), /preview unavailable/i);
    const imageHidden = await preview.evaluate(element => element.hidden);
    assert.match(await image.locator('#viewer-note').innerText(), /component descriptions remain available/i);
    assert.equal(await image.locator('#retry').isVisible(), true);
    await image.locator('#section-toggle').click();
    await image.waitForFunction(() => document.querySelector('#separation')?.disabled === false, null, { timeout: 15000 });
    await image.locator('#separation').fill('75');
    await image.waitForFunction(() => window.__uncaged?.metrics().open === true
      && window.__uncaged.metrics().separation === .75, null, { timeout: 10000 });
    assert.match(await image.locator('.illustrated-caption').innerText(), /preview unavailable/i);
    await image.getByRole('link', { name: /story & media folio/i }).click();
    await image.waitForURL(url => url.pathname.endsWith('/folio.html'));
    const folioHeading = (await image.locator('h1').first().innerText()).replace(/\s+/g, ' ');
    assert.match(folioHeading, /Meet the thing that learned to choose\./i);
    assert.equal(await image.getByRole('link', { name: 'Current 3D review', exact: true }).count(), 1);
    return { imageHidden, supportingPage: new URL(image.url()).pathname };
  });

  const media = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await setup(media, 'theme-media-failure');
  let failTrack = true;
  await media.route('**/audio/iron-verdict-v3/full-song.mp3', async route => {
    if (failTrack) {
      recordForcedFailure(route.request(), 'theme fetch returns 503');
      await route.fulfill({ status: 503, contentType: 'text/plain', body: 'forced test failure' });
    }
    else await route.continue();
  });
  await check('theme audio reports fetch failure and can be retried', async () => {
    await media.locator('#theme-mute').click();
    assert.equal(await media.locator('#theme-mute').getAttribute('aria-pressed'), 'true');
    await media.locator('#theme-play').click();
    await media.waitForFunction(() => /could not be loaded.*press play to retry/i.test(document.querySelector('#theme-status').textContent), null, { timeout: 15000 });
    assert.equal(await media.locator('#theme-play').innerText(), 'Play');
    assert.equal(await media.locator('.theme-player').getAttribute('aria-busy'), 'false');
    failTrack = false;
    await media.locator('#theme-play').click();
    await media.waitForFunction(() => document.querySelector('#theme-play').textContent === 'Pause', null, { timeout: 20000 });
    assert.match(await media.locator('#theme-status').innerText(), /loaded.*playing/i);
    await media.locator('#theme-play').click();
    assert.equal(await media.locator('#theme-play').innerText(), 'Play');
    return { failureWasRecoverable: true, playControlRestored: true };
  });

  const unavailable = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await unavailable.addInitScript(() => {
    const nativeGetContext = HTMLCanvasElement.prototype.getContext;
    window.__nativeGetContext = nativeGetContext;
    HTMLCanvasElement.prototype.getContext = function (type, ...args) {
      if (type === 'webgl' || type === 'webgl2' || type === 'experimental-webgl') return null;
      return nativeGetContext.call(this, type, ...args);
    };
  });
  await setup(unavailable, 'webgl-unavailable-retry');
  await check('unavailable WebGL has a truthful fallback and a working retry', async () => {
    assert.match(await unavailable.locator('#render-label').innerText(), /ILLUSTRATED/);
    assert.equal(await unavailable.locator('#retry').isVisible(), true);
    assert.equal(await unavailable.locator('#focus-part').isDisabled(), true);
    assert.match(await unavailable.locator('#viewer-note').innerText(), /WebGL is unavailable/i);
    await unavailable.evaluate(() => { HTMLCanvasElement.prototype.getContext = window.__nativeGetContext; });
    await unavailable.locator('#retry').click();
    await unavailable.locator('#loading').waitFor({ state: 'hidden', timeout: 30000 });
    await unavailable.waitForFunction(() => window.__uncaged.metrics().kind === 'webgl', null, { timeout: 30000 });
    await unavailable.locator('[data-part="guard"]').click();
    assert.equal(await unavailable.locator('#focus-part').isDisabled(), false);
    return { rendererAfterRetry: await unavailable.evaluate(() => window.__uncaged.metrics().kind) };
  });

  const context = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await setup(context, 'context-loss-retry');
  await check('context loss enters labeled fallback and repeated retries restore 3D controls', async () => {
    assert.equal(await context.evaluate(() => window.__uncaged.metrics().kind), 'webgl');
    for (let cycle = 1; cycle <= 2; cycle++) {
      await context.evaluate(() => {
        const gl = document.querySelector('#scene canvas')?.getContext('webgl2');
        const lose = gl?.getExtension('WEBGL_lose_context');
        if (!lose) throw new Error('WEBGL_lose_context is unavailable in this browser.');
        lose.loseContext();
      });
      await context.waitForFunction(() => document.querySelector('#render-label').textContent.includes('ILLUSTRATED'), null, { timeout: 15000 });
      assert.equal(await context.locator('#retry').isVisible(), true);
      assert.equal(await context.locator('#focus-part').isDisabled(), true);
      assert.match(await context.locator('#viewer-note').innerText(), /retry 3D/i);
      await context.locator('#retry').click();
      await context.locator('#loading').waitFor({ state: 'hidden', timeout: 30000 });
      await context.waitForFunction(() => document.querySelector('#scene canvas') && window.__uncaged?.metrics().kind === 'webgl', null, { timeout: 30000 });
      await context.locator('[data-part="guard"]').click();
      assert.equal(await context.locator('#focus-part').isDisabled(), false);
    }
    return { lossCycles: 2, renderer: 'webgl', developmentHookAvailable: true };
  });

  await check('no uncaught page errors and successful models match declared candidate', async () => {
    await Promise.all(pendingModelReads);
    assert.ok(report.servedModels.length > 0, 'no successful model bytes were verified');
    assert.deepEqual(await sourceHashes(), sourceSha256, 'local candidate changed during the browser run');
    assert.deepEqual(report.errors, []);
    return { errors: report.errors, resourceAndConsoleEventsRetainedForReview: true };
  });
} catch (error) {
  report.failure = String(error?.stack || error);
  process.exitCode = 1;
} finally {
  await browser.close();
  await writeFile(path.join(out, `recovery-v4-${randomUUID()}.json`), `${JSON.stringify(report, null, 2)}\n`, { flag: 'wx' });
  console.log(JSON.stringify({ status: report.failure ? 'failed' : 'passed', checks: report.checks, failure: report.failure }, null, 2));
}
