/** Exercise the built or published review through public controls, without dev hooks. */
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

if (!process.argv[2]) throw new Error('Pass the installed Playwright entry module as argv[2].');
const { chromium } = await import(pathToFileURL(process.argv[2]).href);
const base = new URL(process.env.PUBLICATION_URL || 'http://127.0.0.1:4176/');
assert(['http:', 'https:'].includes(base.protocol));
if (!base.pathname.endsWith('/')) base.pathname += '/';
const modelSha256 = '3ec668b0b9bbaf1cb546ec2e04b09030c5f45b0f0893adc5b7fe5aa57baacdc5';
const local = ['127.0.0.1', 'localhost'].includes(base.hostname);
const target = local ? 'local' : 'published';
const output = path.resolve('.local/publication');
execFileSync('git', ['check-ignore', '--quiet', path.join(output, 'browser-probe.json')]);
const run = `${target}-${new Date().toISOString().replace(/[:.]/g, '-')}`;
const captureDirectory = path.join(output, run);
await mkdir(captureDirectory, { recursive: true });
const browser = await chromium.launch({ headless: process.env.PUBLICATION_HEADLESS === '1' });
const report = {
  generatedAt: new Date().toISOString(), baseUrl: base.href, status: 'running',
  browser: browser.version(), viewport: { width: 1440, height: 1000, deviceScaleFactor: 1 },
  headless: process.env.PUBLICATION_HEADLESS === '1',
  scope: 'Built DOM controls and served assets; not physical simulation or artistic acceptance.',
  checks: [], screenshots: [], renderers: [], responses: [], errors: [], requestFailures: [], analyticsStubs: [],
};
let activePage;

async function newPage(label, fallback = false) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  page.setDefaultTimeout(30000);
  page.on('pageerror', error => report.errors.push({ page: label, type: 'pageerror', message: error.message }));
  page.on('console', message => {
    if (message.type() === 'error') report.errors.push({ page: label, type: 'console', message: message.text() });
  });
  page.on('response', response => {
    const url = new URL(response.url());
    if (url.origin === base.origin) report.responses.push({ page: label, url: response.url(), status: response.status(), type: response.request().resourceType() });
  });
  page.on('requestfailed', request => report.requestFailures.push({ page: label, url: request.url(), failure: request.failure()?.errorText }));
  // Only analytics is stubbed. Fonts, first-party assets and media use actual responses.
  await page.route('**/*', route => {
    const url = new URL(route.request().url());
    if (['www.googletagmanager.com', 'www.google-analytics.com', 'region1.google-analytics.com'].includes(url.hostname)) {
      report.analyticsStubs.push({ page: label, url: url.href });
      return route.fulfill({ status: 200, contentType: 'application/javascript', body: '' });
    }
    return route.continue();
  });
  if (fallback) {
    await page.addInitScript(() => {
      const original = HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext = function (type, ...args) {
        if (/^(webgl2?|experimental-webgl)$/.test(type)) return null;
        return original.call(this, type, ...args);
      };
    });
  }
  activePage = page;
  return page;
}

async function check(name, fn) {
  console.log(`CHECK ${name}`);
  try {
    const detail = await fn();
    report.checks.push({ name, status: 'passed', detail });
    return detail;
  } catch (error) {
    const filename = `failure-${name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.png`;
    await activePage?.screenshot({ path: path.join(captureDirectory, filename) }).catch(() => {});
    report.checks.push({ name, status: 'failed', message: error.message, screenshot: `${run}/${filename}` });
    throw error;
  }
}

async function capture(page, name, viewer = true) {
  const file = `${name}.png`;
  await (viewer ? page.locator('#viewer') : page).screenshot({ path: path.join(captureDirectory, file) });
  report.screenshots.push({ file: `${run}/${file}`, url: page.url() });
}

async function renderer(page, label) {
  const value = await page.locator('#scene canvas').evaluate(canvas => {
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
    const extension = gl.getExtension('WEBGL_debug_renderer_info');
    return {
      renderer: extension ? gl.getParameter(extension.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER),
      vendor: extension ? gl.getParameter(extension.UNMASKED_VENDOR_WEBGL) : gl.getParameter(gl.VENDOR),
      version: gl.getParameter(gl.VERSION), width: canvas.width, height: canvas.height,
      devicePixelRatio: devicePixelRatio,
    };
  });
  report.renderers.push({ page: label, ...value });
  return value;
}

async function rootReady(page, illustrated = false) {
  await page.goto(new URL(illustrated ? '?view=illustrated' : './', base).href);
  await page.locator('#loading').waitFor({ state: 'hidden', timeout: 120000 });
  assert.equal(await page.evaluate(() => typeof window.__uncaged), 'undefined', 'Must inspect a production build.');
  assert.equal(await page.locator('#scene canvas').count(), illustrated ? 0 : 1);
}

async function rootEra(page, era) {
  await page.locator(`[data-era="${era}"]`).click();
  await page.waitForFunction(value => {
    const button = document.querySelector(`[data-era="${value}"]`);
    return button?.getAttribute('aria-pressed') === 'true' &&
      document.querySelector('#era-transition')?.hidden &&
      !document.querySelector('#section-toggle')?.disabled &&
      document.querySelector('#viewer')?.dataset.mode === 'encounter';
  }, era, { timeout: 30000 });
}

async function rootInspection(page, label) {
  await page.locator('#section-toggle').click();
  await page.waitForFunction(() => document.querySelector('#viewer').dataset.mode === 'inspection' && !document.querySelector('#separation').disabled);
  await page.locator('#separation').fill('100');
  await page.waitForFunction(() => document.querySelector('#separation-value').textContent === '100%');
  await page.waitForTimeout(1200);
  await capture(page, `${label}-exploded`);
  await page.locator('#reassemble').click();
  await page.waitForFunction(() => document.querySelector('#viewer').dataset.mode === 'encounter' && !document.querySelector('#encounter-status').textContent.includes('Reassembling'));
  assert.equal(await page.locator('#separation').inputValue(), '0');
  assert.equal(await page.locator('#section-toggle').getAttribute('aria-pressed'), 'false');
}

async function mobile(page, label) {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => scrollTo(0, 0));
  const result = await page.evaluate(() => ({
    width: innerWidth, scrollWidth: document.documentElement.scrollWidth,
    links: [...document.querySelectorAll('.topbar nav a')].map(a => {
      const rect = a.getBoundingClientRect();
      return { text: a.textContent, href: a.href, width: rect.width, left: rect.left, right: rect.right, display: getComputedStyle(a).display };
    }),
  }));
  assert(result.scrollWidth <= result.width, `${label} overflows at 390px`);
  for (const link of result.links) {
    assert(link.width > 0 && link.display !== 'none', `${label} navigation hidden: ${link.text}`);
    assert(link.left >= 0 && link.right <= 391, `${label} navigation outside viewport: ${link.text}`);
  }
  await capture(page, `${label}-mobile-navigation`, false);
  await page.setViewportSize({ width: 1440, height: 1000 });
  return result;
}

async function mediaState(page) {
  return page.evaluate(() => ({
    players: [...document.querySelectorAll('audio,video')].map(media => ({
      id: media.id, paused: media.paused, currentTime: media.currentTime, duration: Number.isFinite(media.duration) ? media.duration : null,
      readyState: media.readyState, autoplay: media.autoplay, error: media.error?.message || null,
    })),
    theme: document.querySelector('#theme-play')?.getAttribute('aria-pressed'),
    soundscape: document.querySelector('#sound-toggle')?.getAttribute('aria-pressed'),
  }));
}

async function startNativeMedia(page, id) {
  console.log(`MEDIA native Play: ${id}`);
  const control = page.locator(`#${id}`);
  await control.scrollIntoViewIfNeeded();
  const tag = await control.evaluate(element => element.tagName);
  await control.hover();
  const bounds = await control.boundingBox();
  // Chromium's native lower-left play control, exercised with a real pointer click.
  await control.click({ position: { x: 24, y: tag === 'VIDEO' ? bounds.height - 49 : bounds.height / 2 } });
  await page.waitForFunction(value => {
    const media = document.getElementById(value);
    return !media.paused && media.currentTime > 0 && media.readyState >= 2;
  }, id, { timeout: 90000 });
}

try {
  const root = await newPage('root');
  await check('root served model and WebGL', async () => {
    await rootReady(root);
    const modelUrl = await root.evaluate(() => performance.getEntriesByType('resource').map(resource => resource.name).find(name => /murderbird-exterior-v1[^/]*\.glb(?:\?|$)/.test(name)));
    assert(modelUrl, 'Loaded GLB must appear in actual browser resource timing.');
    const response = await root.request.get(modelUrl);
    assert(response.ok(), `GLB response ${response.status()}`);
    const data = await response.body();
    const actual = createHash('sha256').update(data).digest('hex');
    assert.equal(actual, modelSha256);
    report.servedModel = { url: modelUrl, bytes: data.length, sha256: actual };
    await capture(root, 'root-initial');
    return { ...report.servedModel, renderer: await renderer(root, 'root') };
  });
  await check('root three eras, controls and inspection', async () => {
    const eras = [];
    for (const era of ['maker', 'mechanic', 'builder']) {
      await rootEra(root, era);
      await capture(root, `root-${era}`);
      if (era === 'maker') {
        for (const control of ['leg', 'wing', 'tail', 'neck', 'jaw']) {
          await root.locator(`#lever-${control}`).fill('100');
          await root.waitForFunction(() => document.querySelector('#viewer').dataset.behavior === 'puppet-articulation');
          await root.locator('#release-levers').click();
        }
        await root.waitForFunction(() => document.querySelector('#viewer').dataset.behavior === 'puppet-rest');
      } else if (era === 'mechanic') {
        await root.locator('#run-mechanism').click();
        await root.waitForFunction(() => document.querySelector('#viewer').dataset.behavior === 'mechanical-run');
        await root.waitForTimeout(3500);
        await capture(root, 'root-mechanic-running');
        await root.locator('#stop-mechanism').click();
        await root.waitForFunction(() => !document.querySelector('#run-mechanism').disabled);
      }
      await rootInspection(root, `root-${era}`);
      eras.push({ era, label: await root.locator('#era-label').textContent(), inspectionReassembled: true });
    }
    return eras;
  });
  await check('root jump and shield thrust complete', async () => {
    const moves = [];
    for (const [id, behavior] of [['power-jump', 'power-jump'], ['shield-thrust', 'power-thrust']]) {
      await root.locator(`#${id}`).click();
      await root.waitForFunction(value => document.querySelector('#viewer').dataset.behavior === value, behavior);
      await capture(root, `root-${id}`);
      await root.waitForFunction(value => document.querySelector('#viewer').dataset.behavior !== value, behavior, { timeout: 30000 });
      await root.waitForFunction(value => !document.getElementById(value).disabled, id);
      moves.push({ action: id, enteredBehavior: behavior, completed: true });
    }
    return moves;
  });
  await check('root mobile navigation', () => mobile(root, 'root'));
  await root.close();

  const rootFallback = await newPage('root-fallback');
  await check('root illustrated fallback three eras', async () => {
    await rootReady(rootFallback, true);
    const eras = [];
    for (const era of ['maker', 'mechanic', 'builder']) {
      await rootEra(rootFallback, era);
      await rootFallback.waitForFunction(value => {
        const image = document.querySelector('.illustrated-view img');
        return image?.complete && image.naturalWidth > 0 && image.src.includes(`/${value}-`);
      }, era);
      eras.push(await rootFallback.locator('.illustrated-view img').evaluate(image => ({ src: image.src, width: image.naturalWidth, height: image.naturalHeight, alt: image.alt })));
      await capture(rootFallback, `root-fallback-${era}`);
    }
    await rootInspection(rootFallback, 'root-fallback-builder');
    return { condition: 'Public ?view=illustrated option', eras };
  });
  await rootFallback.close();

  const folio = await newPage('folio');
  await check('folio earlier WebGL model and era controls', async () => {
    await folio.goto(new URL('folio.html', base).href);
    await folio.locator('#scene canvas').waitFor({ state: 'visible', timeout: 60000 });
    await folio.locator('#theme-play').waitFor();
    assert.match(await folio.locator('.viewer-note').textContent(), /earlier|Earlier/);
    assert.equal(await folio.evaluate(() => typeof window.__uncaged), 'undefined');
    const eras = [];
    for (const era of ['maker', 'mechanic', 'builder']) {
      await folio.locator(`[data-era="${era}"]`).click();
      assert.equal(await folio.locator(`[data-era="${era}"]`).getAttribute('aria-pressed'), 'true');
      eras.push({ era, label: await folio.locator('#scene-era-label').textContent() });
    }
    // Builder's first story part is Heart, which opens inspection on era entry.
    if (await folio.locator('#section-toggle').getAttribute('aria-pressed') !== 'true') await folio.locator('#section-toggle').click();
    assert.equal(await folio.locator('#section-toggle').getAttribute('aria-pressed'), 'true');
    await capture(folio, 'folio-earlier-model-open');
    await folio.locator('#section-toggle').click();
    return { eras, renderer: await renderer(folio, 'folio') };
  });
  await check('folio no autoplay and one source at a time', async () => {
    const initial = await mediaState(folio);
    assert(initial.players.every(player => player.paused && player.currentTime === 0 && !player.autoplay));
    assert.equal(initial.theme, 'false');
    assert.equal(initial.soundscape, 'false');
    const transitions = [];
    await folio.locator('#sound-toggle').click();
    await folio.waitForFunction(() => document.querySelector('#sound-toggle').getAttribute('aria-pressed') === 'true');
    transitions.push({ action: 'soundscape native button', ...await mediaState(folio) });
    await startNativeMedia(folio, 'iron-verdict-audio');
    let state = await mediaState(folio);
    assert.equal(state.soundscape, 'false');
    assert(state.players.filter(player => !player.paused).every(player => player.id === 'iron-verdict-audio'));
    transitions.push({ action: 'original audio native play', ...state });
    await startNativeMedia(folio, 'garageband-audio');
    state = await mediaState(folio);
    assert.equal(state.players.find(player => player.id === 'iron-verdict-audio').paused, true);
    transitions.push({ action: 'GarageBand native play pauses original', ...state });
    await startNativeMedia(folio, 'first-choice-video');
    state = await mediaState(folio);
    assert(state.players.filter(player => player.id !== 'first-choice-video').every(player => player.paused));
    assert(state.players.find(player => player.id === 'first-choice-video').duration >= 7.9);
    transitions.push({ action: 'pilot native play pauses audio', ...state });
    await folio.locator('#theme-play').click();
    await folio.waitForFunction(() => document.querySelector('#theme-play').getAttribute('aria-pressed') === 'true', undefined, { timeout: 120000 });
    state = await mediaState(folio);
    assert(state.players.every(player => player.paused));
    transitions.push({ action: 'theme Play pauses native media', ...state });
    await folio.locator('#sound-toggle').click();
    await folio.waitForFunction(() => document.querySelector('#sound-toggle').getAttribute('aria-pressed') === 'true');
    assert.equal((await mediaState(folio)).theme, 'false');
    await folio.locator('#sound-toggle').click();
    state = await mediaState(folio);
    assert.equal(state.soundscape, 'false');
    assert.equal(state.theme, 'false');
    assert(state.players.every(player => player.paused && !player.error));
    transitions.push({ action: 'soundscape pauses theme; final sound off', ...state });
    await capture(folio, 'folio-media-controls', false);
    return { initial, transitions, input: 'Actual DOM buttons and Chromium native media play controls' };
  });
  await check('folio mobile navigation', () => mobile(folio, 'folio'));
  await folio.close();

  const folioFallback = await newPage('folio-fallback', true);
  await check('folio fallback scoped story art', async () => {
    await folioFallback.goto(new URL('folio.html', base).href);
    await folioFallback.locator('.fallback-image').waitFor();
    assert.equal(await folioFallback.locator('#scene canvas').count(), 0);
    const eras = [];
    for (const era of ['maker', 'mechanic', 'builder']) {
      await folioFallback.locator(`[data-era="${era}"]`).click();
      await folioFallback.waitForFunction(() => {
        const image = document.querySelector('.fallback-image');
        return image.complete && image.naturalWidth > 0;
      });
      eras.push(await folioFallback.locator('.fallback-image').evaluate(image => ({ src: image.src, width: image.naturalWidth, height: image.naturalHeight, alt: image.alt })));
      await capture(folioFallback, `folio-fallback-${era}`);
    }
    assert.equal(new Set(eras.map(era => era.src)).size, 3);
    return { condition: 'WebGL context creation disabled before page load', eras };
  });
  await folioFallback.close();

  const review = await newPage('review');
  await check('published review images, motion and links', async () => {
    await review.goto(new URL('review/', base).href);
    await review.locator('details').evaluateAll(elements => elements.forEach(element => { element.open = true; }));
    await review.locator('img').evaluateAll(images => images.forEach(image => { image.loading = 'eager'; }));
    await review.waitForFunction(() => [...document.images].every(image => image.complete && image.naturalWidth > 0), undefined, { timeout: 120000 });
    const images = await review.locator('img').evaluateAll(elements => elements.map(image => ({ src: image.src, width: image.naturalWidth, height: image.naturalHeight })));
    assert(images.length >= 50);
    assert(images.every(image => new URL(image.src).origin === base.origin));
    await review.waitForFunction(() => document.querySelector('video').readyState >= 1, undefined, { timeout: 120000 });
    const video = await review.locator('video').evaluate(media => ({ src: media.currentSrc, duration: media.duration, width: media.videoWidth, height: media.videoHeight, paused: media.paused, error: media.error?.message || null }));
    assert(video.duration > 100 && video.width > 0 && video.height > 0 && video.paused && !video.error);
    assert.equal(new URL(video.src).origin, base.origin);
    await review.locator('video').evaluate(media => { media.currentTime = 85; });
    await review.waitForFunction(() => document.querySelector('video').currentTime >= 84.9 && !document.querySelector('video').seeking);
    const links = await review.locator('a').evaluateAll(elements => [...new Set(elements.map(anchor => anchor.href))]);
    const localLinks = links.filter(link => new URL(link).origin === base.origin);
    const linkResponses = [];
    for (const link of localLinks) {
      const response = await review.request.head(link);
      linkResponses.push({ url: link, status: response.status() });
      assert(response.ok(), `${link} returned ${response.status()}`);
    }
    assert(links.every(link => !/127\.0\.0\.1|localhost/.test(link) || local), 'Published gallery contains loopback links');
    await review.locator('details').evaluateAll(elements => elements.forEach(element => { element.open = false; }));
    await review.evaluate(() => scrollTo(0, 0));
    await capture(review, 'review-desktop', false);
    await review.setViewportSize({ width: 390, height: 844 });
    assert(await review.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Review gallery mobile overflow');
    await capture(review, 'review-mobile', false);
    return { images, video, localLinks: linkResponses, repositoryLinks: links.filter(link => new URL(link).origin !== base.origin) };
  });
  await review.close();
  await check('no page, console or first-party HTTP errors', async () => {
    assert.deepEqual(report.errors, []);
    const failedResponses = report.responses.filter(response => response.status >= 400);
    assert.deepEqual(failedResponses, []);
    const unexpectedFailures = report.requestFailures.filter(request => !/ERR_ABORTED|cancelled/i.test(request.failure || ''));
    assert.deepEqual(unexpectedFailures, []);
    return { responseCount: report.responses.length, canceledRequests: report.requestFailures.length, analyticsStubCount: report.analyticsStubs.length };
  });
  report.status = 'passed';
} catch (error) {
  report.status = 'failed';
  report.failure = { message: error.message, stack: error.stack };
  process.exitCode = 1;
} finally {
  await browser.close();
  report.completedAt = new Date().toISOString();
  await writeFile(path.join(output, `browser-${run}.json`), JSON.stringify(report, null, 2) + '\n');
  await writeFile(path.join(output, `browser-${target}.json`), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ status: report.status, checks: report.checks.map(({ name, status }) => ({ name, status })), servedModel: report.servedModel, errorCount: report.errors.length, failure: report.failure?.message, receipt: path.join(output, `browser-${target}.json`) }, null, 2));
}
