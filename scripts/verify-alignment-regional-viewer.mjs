import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

assert.ok(process.argv[2], 'Pass the installed Playwright module path.');
const { chromium } = await import(pathToFileURL(process.argv[2]).href);
const base = process.env.UNCAGED_BASE_URL || 'http://127.0.0.1:5182/';
const output = process.env.UNCAGED_AUDIT;
assert.ok(output && /^[a-f0-9]{64}$/.test(process.env.UNCAGED_MODEL_SHA256 || ''), 'Provide audit directory and exact candidate SHA.');
await fs.mkdir(output, { recursive: false });
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const identity = await (await fetch(new URL('/__regional-review', base))).json();
assert.equal(identity.sha256, process.env.UNCAGED_MODEL_SHA256);
assert.ok(Array.isArray(identity.applicationSourceFiles) && identity.applicationSourceFiles.length > 0,
  'Review identity must bind application/controller source hashes.');
assert.ok(identity.activeApplicationAssets?.v4Model?.sha256 && identity.activeApplicationAssets.v4Fallbacks?.length === 3,
  'Review identity must record unchanged active V4 assets.');
for (const route of identity.routes) {
  assert.equal(route.overrideMode, 'in-memory response override');
  assert.equal(route.inputImportPath, route.url);
}
const receipt = { generatedAt: new Date().toISOString(), identity, status: 'running', responses: [], webgl: [], fallbacks: [], errors: [], externalRequests: [] };
for (const row of identity.routes) {
  const response = await fetch(new URL(row.url, base));
  const bytes = Buffer.from(await response.arrayBuffer());
  assert.equal(response.status, 200);
  assert.equal(sha(bytes), row.sha256);
  assert.equal(sha(await fs.readFile(row.source)), row.sha256);
  assert.equal(bytes.length, row.bytes);
  receipt.responses.push({ url: row.url, sha256: sha(bytes), bytes: bytes.length, status: response.status });
}
const browser = await chromium.launch({ headless: false });
receipt.browser = browser.version();
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
page.on('pageerror', error => receipt.errors.push(error.message));
page.on('request', request => {
  const url = new URL(request.url());
  if (!['127.0.0.1', 'localhost'].includes(url.hostname) && !['data:', 'blob:'].includes(url.protocol)) receipt.externalRequests.push(request.url());
});
async function screenshot(name) {
  const file = path.join(output, name + '.png');
  await page.locator('#viewer').screenshot({ path: file });
  return { path: file, sha256: sha(await fs.readFile(file)) };
}
try {
  const actualModel = page.waitForResponse(response => new URL(response.url()).pathname.endsWith('/murderbird-alignment-v4.glb'));
  await page.goto(base);
  await page.locator('#loading').waitFor({ state: 'hidden' });
  const modelResponse = await actualModel;
  assert.equal(sha(await modelResponse.body()), identity.sha256);
  receipt.actualBrowserModel = { url: modelResponse.url(), sha256: sha(await modelResponse.body()) };
  assert.equal(await page.locator('aside').first().innerText(), 'Local regional geometry review · revision required · comparison gallery · exact review identity');
  for (const era of ['maker', 'mechanic', 'builder']) {
    await page.locator(`[data-era=${era}]`).click();
    await page.waitForFunction(era => __uncaged.getSnapshot().era === era && !__uncaged.getSnapshot().pendingEra, era);
    await page.waitForTimeout(800);
    const metrics = await page.evaluate(() => __uncaged.metrics());
    assert.equal(metrics.kind, 'webgl');
    const bounds = await page.locator('#viewer canvas').boundingBox();
    assert.ok(bounds.width > 0 && bounds.height > 0);
    receipt.webgl.push({ era, bounds, metrics, screenshot: await screenshot(era + '-webgl') });
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(500);
  receipt.narrow = await page.evaluate(() => ({ clientWidth: document.documentElement.clientWidth, scrollWidth: document.documentElement.scrollWidth, canvas: (() => { const r = document.querySelector('#viewer canvas').getBoundingClientRect(); return { width: r.width, height: r.height }; })() }));
  assert.equal(receipt.narrow.clientWidth, receipt.narrow.scrollWidth);
  assert.ok(receipt.narrow.canvas.width > 0 && receipt.narrow.canvas.height > 0);
  receipt.narrow.screenshot = await screenshot('builder-webgl-narrow');
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto(new URL('?view=illustrated', base).href);
  await page.locator('#loading').waitFor({ state: 'hidden' });
  for (const era of ['maker', 'mechanic', 'builder']) {
    await page.locator(`[data-era=${era}]`).click();
    await page.waitForFunction(era => { const img = document.querySelector('.illustrated-view img'); return img?.src.includes(era + '-preview.png') && img.complete && img.naturalWidth > 0; }, era);
    const expectedCaption = `${({ maker: 'Maker', mechanic: 'Mechanic', builder: 'Advanced' })[era]} exterior study · fixed rendered view`;
    await page.waitForFunction(expected => document.querySelector('.illustrated-caption')?.textContent === expected, expectedCaption);
    assert.equal(await page.locator(`[data-era=${era}]`).getAttribute('aria-pressed'), 'true', `${era}: selected era button is not pressed`);
    for (const other of ['maker', 'mechanic', 'builder'].filter(value => value !== era)) {
      assert.equal(await page.locator(`[data-era=${other}]`).getAttribute('aria-pressed'), 'false', `${era}: stale selected state on ${other}`);
    }
    const state = await page.locator('.illustrated-view img').evaluate(img => { const r = img.getBoundingClientRect(); return { src: img.src, width: r.width, height: r.height, naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight }; });
    const response = await page.request.get(state.src);
    const expected = identity.routes.find(row => row.url.endsWith('/' + era + '-preview.png'));
    assert.equal(sha(await response.body()), expected.sha256);
    assert.ok(state.width > 0 && state.height > 0 && state.naturalWidth === 1100 && state.naturalHeight === 1100);
    receipt.fallbacks.push({ era, ...state, sha256: expected.sha256, caption: await page.locator('.illustrated-caption').innerText(), selectedButtons: await page.locator('[data-era]').evaluateAll(nodes => nodes.filter(node => node.getAttribute('aria-pressed') === 'true').map(node => node.dataset.era)), screenshot: await screenshot(era + '-candidate-fallback') });
  }
  assert.equal(receipt.errors.length, 0);
  assert.equal(receipt.externalRequests.length, 0, JSON.stringify(receipt.externalRequests));
  receipt.status = 'passed';
} finally {
  await browser.close();
  await fs.writeFile(path.join(output, 'viewer-validation.json'), JSON.stringify(receipt, null, 2) + '\n');
  await fs.copyFile(new URL(import.meta.url), path.join(output, 'executed-viewer-check.mjs.txt'));
}
console.log(JSON.stringify({ status: receipt.status, output, modelSha256: identity.sha256, webglEras: receipt.webgl.length, fallbackEras: receipt.fallbacks.length }));
