/** Verify the published CG route, native fallbacks and deliberately requested static models. */
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
const { chromium } = await import(pathToFileURL(process.argv[2]).href);
const base = process.env.CG_URL || 'http://127.0.0.1:4187/';
const out = process.env.CG_OUTPUT || '.local/publication/cg-browser';
await mkdir(out, { recursive: true });
const browser = await chromium.launch({ channel: 'chrome', headless: true, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
const page = await context.newPage();
const report = { url: base, generatedAt: new Date().toISOString(), browser: browser.version(), rendering: 'software ANGLE/SwiftShader; no hardware performance claim', checks: [], errors: [], consoleMessages: [], screenshots: [] };
const check = label => { report.checks.push(label); console.log(label); };
page.on('pageerror', error => report.errors.push(error.message));
page.on('console', message => { if (['error', 'warning'].includes(message.type())) report.consoleMessages.push({ level: message.type(), text: message.text() }); });
page.on('response', response => { if (response.status() >= 400 && response.url().startsWith(new URL(base).origin)) report.errors.push(`${response.status()} ${response.url()}`); });
const screenshot = async (label, locator = page) => { const path = `${out}/${label}.png`; await locator.screenshot({ path, fullPage: locator === page }); report.screenshots.push(path); };
const nativeReady = async selected => { await page.waitForFunction(e => { const image = document.querySelector('#cg-fallback'); return !image.hidden && image.complete && image.naturalWidth > 0 && image.src.includes('/' + e + '/'); }, selected); };
try {
  await page.goto(base); await page.locator('a[href="./cg.html"]').first().click();
  assert.match(await page.title(), /CG assessment/); assert.match(page.url(), /cg\.html$/);
  await nativeReady('builder'); assert.equal(await page.locator('#cg-webgl canvas').count(), 0); check('Homepage link opens meaningful CG assessment with native image and no automatic GLB download');
  assert.equal(await page.locator('vite-error-overlay').count(), 0); check('No framework error overlay');
  for (const selector of ['#comparisons', '#progress', '.cg-gallery', '.cg-references']) {
    await page.locator(selector).scrollIntoViewIfNeeded();
    await page.waitForFunction(selector => [...document.querySelector(selector).querySelectorAll('img')].every(image => image.complete && image.naturalWidth > 0), selector);
  }
  await page.evaluate(() => scrollTo(0, 0)); await screenshot('desktop-native');
  check('Original references and all default comparison/progress images visibly load on scroll');
  // A large model download can outlive several lighting selections.
  let releaseDownload, markRequested;
  const heldDownload = new Promise(resolve => { releaseDownload = resolve; });
  const modelRequested = new Promise(resolve => { markRequested = resolve; });
  const delayedModel = '**/cg/retained04/builder/murderbird-recursive-builder.glb';
  await page.route(delayedModel, async route => { markRequested(); await heldDownload; await route.continue(); });
  await page.locator('#cg-load').click(); await modelRequested;
  await page.locator('[data-light="exhibit"]').click();
  assert.equal(await page.locator('[data-light="exhibit"]').getAttribute('aria-pressed'), 'true');
  releaseDownload();
  await page.waitForFunction(() => document.querySelector('#cg-webgl').dataset.cg && !document.querySelector('#cg-webgl').hidden, null, { timeout: 90000 });
  assert.equal(JSON.parse(await page.locator('#cg-webgl').getAttribute('data-cg')).lighting, 'exhibit', 'Completed model must use the latest lighting selected during download');
  await page.unroute(delayedModel);
  check('Delayed model completion applies the lighting selected during its download');
  for (const selected of ['builder', 'maker', 'mechanic']) {
    await page.locator('#cg-era').selectOption(selected); await nativeReady(selected);
    assert.equal(await page.locator('#cg-webgl canvas').count(), 0, 'Previous model must be disposed when era changes');
    for (const lighting of ['neutral', 'exhibit']) {
      await page.locator(`[data-light="${lighting}"]`).click();
      await page.waitForFunction(mode => { const image = document.querySelector('#cg-fallback'); return image.complete && image.naturalWidth > 0 && image.src.includes('canon-' + (mode === 'exhibit' ? 'workshop' : 'neutral')); }, lighting);
      assert.equal(await page.locator(`[data-light="${lighting}"]`).getAttribute('aria-pressed'), 'true');
    }
    await page.locator('[data-light="neutral"]').click(); await page.locator('#cg-load').click();
    await page.waitForFunction(() => document.querySelector('#cg-webgl').dataset.cg && !document.querySelector('#cg-webgl').hidden, null, { timeout: 90000 });
    const initial = await page.locator('#cg-webgl').getAttribute('data-cg'); assert(JSON.parse(initial).triangles > 0);
    await page.locator('#cg-right').click(); assert.notEqual(await page.locator('#cg-webgl').getAttribute('data-cg'), initial);
    await page.locator('#cg-in').click(); assert(JSON.parse(await page.locator('#cg-webgl').getAttribute('data-cg')).zoom > 1);
    await page.locator('#cg-reset').click(); assert.equal(JSON.parse(await page.locator('#cg-webgl').getAttribute('data-cg')).zoom, 1);
    await page.locator('[data-light="exhibit"]').click(); assert.equal(JSON.parse(await page.locator('#cg-webgl').getAttribute('data-cg')).lighting, 'exhibit');
    await screenshot(selected + '-3d', page.locator('#cg-viewer'));
    await page.locator('#cg-native').click(); await nativeReady(selected); assert.equal(await page.locator('#cg-native').getAttribute('aria-pressed'), 'true');
    check(`${selected}: both native light rigs, requested GLB, orbit, zoom, reset, exhibit lighting and return to native`);
  }
  await page.locator('#cg-gallery-view').selectOption('details'); assert.equal(await page.locator('#cg-gallery-cards img').count(), 5);
  await page.locator('#cg-gallery-cards').scrollIntoViewIfNeeded();
  await page.waitForFunction(() => [...document.querySelectorAll('#cg-gallery-cards img')].every(image => image.complete && image.naturalWidth > 0)); check('Five exact native detail/hero views load');
  await page.locator('#cg-gallery-view').selectOption('turntable'); assert.equal(await page.locator('#cg-gallery-cards img').count(), 8);
  await page.waitForFunction(() => [...document.querySelectorAll('#cg-gallery-cards img')].every(image => image.complete && image.naturalWidth > 0)); check('Eight native turntable angles load');
  await page.setViewportSize({ width: 390, height: 844 }); await page.locator('#cg-era').selectOption('builder'); await nativeReady('builder');
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await page.locator('#cg-controls').scrollIntoViewIfNeeded(); await screenshot('mobile-native'); check('390px mobile controls and comparisons have no horizontal clipping');
  await page.locator('#cg-load').click(); await page.waitForFunction(() => !!document.querySelector('#cg-webgl').dataset.cg, null, { timeout: 90000 });
  await page.locator('#cg-in').click(); await page.locator('#cg-reset').click(); await screenshot('mobile-3d', page.locator('#cg-viewer')); check('Mobile requested 3D, zoom, reset and responsive framing');
  const failure = await context.newPage(); await failure.route('**/cg/retained04/**/*.glb', route => route.fulfill({ status: 503, body: 'Unavailable' })); await failure.goto(new URL('cg.html', base).href);
  await failure.locator('#cg-load').click(); await failure.waitForFunction(() => document.querySelector('#cg-status').textContent.includes('3D is unavailable'));
  assert.equal(await failure.locator('#cg-fallback').isVisible(), true); assert.match(await failure.locator('#cg-load').textContent(), /Retry/); await screenshot('failed-load-native', failure.locator('#cg-viewer')); check('HTTP model failure leaves readable exact native fallback and Retry');
  const noWebGL = await context.newPage(); await noWebGL.addInitScript(() => { const original = HTMLCanvasElement.prototype.getContext; HTMLCanvasElement.prototype.getContext = function(type, ...args) { return /^(webgl2?|experimental-webgl)$/.test(type) ? null : original.call(this, type, ...args); }; });
  await noWebGL.goto(new URL('cg.html', base).href); await noWebGL.locator('#cg-load').click(); await noWebGL.waitForFunction(() => document.querySelector('#cg-status').textContent.includes('3D is unavailable'));
  assert.equal(await noWebGL.locator('#cg-fallback').isVisible(), true); check('WebGL-unavailable path retains exact native fallback and controls');
  const manifest = JSON.parse(await readFile('assets/review/cg-publication.json', 'utf8'));
  for (const asset of manifest.assets.filter(asset => asset.role === 'static-model' || asset.role.endsWith('reference') || asset.role === 'full-bird-canon')) {
    const response = await page.request.get(new URL(asset.publicPath, base).href); assert.equal(response.status(), 200); const bytes = await response.body();
    assert.equal(bytes.length, asset.bytes); assert.equal(createHash('sha256').update(bytes).digest('hex'), asset.sha256);
  }
  check('Served static models and pinned originals match byte counts and SHA-256 allowlist');
  assert.deepEqual(report.errors, []); assert.equal(report.consoleMessages.filter(message => message.level === 'error').length, 0); check('No unexpected app errors in the console'); report.status = 'PASS';
} catch (error) { report.status = 'FAIL'; report.failure = error.stack; throw error; }
finally { await writeFile(`${out}/receipt.json`, JSON.stringify(report, null, 2) + '\n'); await browser.close(); }
