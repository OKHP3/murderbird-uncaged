/**
 * Browser QA for the three distinct construction eras. Uses an already installed
 * Playwright entry point supplied as argv[2]; it is not an app dependency.
 * Start the authorized local Vite dev server on 5174 and preview on 4176 first.
 * Do not launch it until root confirms the visual pass is ready.
 */
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

if (!process.argv[2]) throw new Error('Pass the existing Playwright entry module as argv[2].');
const { chromium } = await import(pathToFileURL(process.argv[2]).href);
const devUrl = process.env.UNCAGED_DEV_URL || 'http://127.0.0.1:5174/';
const productionUrl = process.env.UNCAGED_PROD_URL || 'http://127.0.0.1:4176/';
for (const value of [devUrl, productionUrl]) {
  if (!['127.0.0.1', 'localhost'].includes(new URL(value).hostname)) {
    throw new Error('Three-era browser QA may only use loopback previews.');
  }
}

const outputDir = path.resolve('assets/audit/three-era-review');
const reportPath = path.join(outputDir, 'browser-validation.json');
await mkdir(outputDir, { recursive: true });
const browser = await chromium.launch({ headless: false });
const report = {
  generatedAt: new Date().toISOString(),
  devUrl,
  productionUrl,
  browser: browser.version(),
  checks: [],
  errors: [],
  screenshots: [],
};
const pages = [];

function observe(page, label) {
  page.on('pageerror', error => report.errors.push({ page: label, type: 'pageerror', message: error.message }));
  page.on('console', message => {
    if (message.type() === 'error') report.errors.push({ page: label, type: 'console', message: message.text() });
  });
}

async function screenshot(page, name, selector = '#viewer') {
  const file = `${name}.png`;
  await page.locator(selector).screenshot({ path: path.join(outputDir, file) });
  report.screenshots.push(file);
}

async function check(page, name, fn) {
  console.log(`CHECK ${name}`);
  try {
    const detail = await fn();
    report.checks.push({ name, status: 'passed', detail });
  } catch (error) {
    const diagnostic = await page.evaluate(() => ({
      snapshot: window.__uncaged?.getSnapshot?.(),
      metrics: window.__uncaged?.metrics?.(),
    })).catch(() => null);
    const failedShot = `failure-${name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.png`;
    await screenshot(page, failedShot).catch(() => {});
    report.checks.push({ name, status: 'failed', error: error.message, diagnostic, screenshot: failedShot });
    throw error;
  }
}

async function setup(page, url = devUrl, label = 'dev') {
  observe(page, label);
  // Keep unrelated analytics outside this local QA run.
  await page.route('**/*googletagmanager.com/**', route => route.fulfill({ status: 200, contentType: 'text/javascript', body: '' }));
  await page.goto(url);
  await page.locator('#loading').waitFor({ state: 'hidden', timeout: 30000 });
}

async function waitEra(page, era) {
  await page.waitForFunction(target => {
    const snapshot = window.__uncaged?.getSnapshot?.();
    return snapshot?.era === target && !snapshot.pendingEra;
  }, era, { timeout: 15000 });
  await page.waitForFunction(() => {
    const metrics = window.__uncaged?.metrics?.();
    return metrics?.kind === 'illustrated' || metrics?.kind === 'webgl' && metrics.motion?.settled === true;
  }, undefined, { timeout: 10000 });
}

async function enterInspection(page, separation = 0) {
  await page.locator('#section-toggle').click();
  await page.waitForFunction(() => {
    const snapshot = window.__uncaged?.getSnapshot?.();
    const metrics = window.__uncaged?.metrics?.();
    return snapshot?.inspection === true && metrics?.open > .99
      && (metrics.kind === 'illustrated' || metrics.motion?.settled === true);
  }, undefined, { timeout: 12000 });
  if (separation > 0) {
    await page.locator('#separation').fill(String(separation));
    await page.waitForFunction(value => window.__uncaged?.metrics?.()?.separation >= value / 100 - .01,
      separation, { timeout: 6000 });
  }
}

function near(actual, expected, tolerance = 1e-5) {
  assert(Math.abs(actual - expected) <= tolerance, `expected ${actual} to be within ${tolerance} of ${expected}`);
}

try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  pages.push(page);
  await setup(page);

  await check(page, 'development hook, loaded 3D assembly, and accessible controls', async () => {
    assert.equal(await page.evaluate(() => typeof window.__uncaged), 'object');
    assert.equal(await page.locator('#scene canvas').count(), 1);
    assert.equal(await page.evaluate(() => __uncaged.metrics().kind), 'webgl');
    for (const [id, label] of [['leg', 'Lift left leg'], ['wing', 'Raise shield wing'], ['tail', 'Lift short tail'], ['neck', 'Turn neck'], ['jaw', 'Open mouth']]) {
      const input = page.locator(`#lever-${id}`);
      assert.equal(await input.getAttribute('aria-label'), label);
      assert.equal(await page.locator(`label[for="lever-${id}"]`).count(), 1);
    }
    assert.equal(await page.locator('#sound-toggle').getAttribute('aria-pressed'), 'false');
    return { title: await page.title(), model: await page.evaluate(() => __uncaged.metrics().kind) };
  });

  await check(page, 'advanced era screenshot and independent system visibility', async () => {
    await waitEra(page, 'builder');
    const metrics = await page.evaluate(() => __uncaged.metrics());
    assert.equal(metrics.nodes['winding-drive'], false);
    assert.equal(metrics.nodes['power-core'], true);
    assert.equal(metrics.nodes.processing, true);
    assert.deepEqual(metrics.mechanisms.visible, { maker: false, mechanic: false, builder: true });
    await screenshot(page, 'builder-era');
    return { era: metrics.era, nodes: metrics.nodes, mechanisms: metrics.mechanisms };
  });

  await check(page, 'Builder strike is interrupted safely by Maker reconstruction', async () => {
    await page.waitForFunction(() => __uncaged.getSnapshot().canReach, undefined, { timeout: 15000 });
    await page.locator('#reach').click();
    await page.waitForFunction(() => __uncaged.getSnapshot().state === 'strike', undefined, { polling: 10, timeout: 20000 });
    const camera = await page.evaluate(() => __uncaged.metrics().camera);
    await page.locator('[data-era="maker"]').click();
    await waitEra(page, 'maker');
    const result = await page.evaluate(() => ({ snapshot: __uncaged.getSnapshot(), metrics: __uncaged.metrics() }));
    near(result.metrics.motion.root.x, 0);
    near(result.metrics.motion.root.z, -.25);
    near(result.metrics.motion.root.yaw, 0);
    assert.equal(result.snapshot.state, 'puppet-rest');
    assert.equal(result.snapshot.visitorPresent, false);
    assert.equal(result.snapshot.canReach, false);
    assert(Object.values(result.metrics.motion.actualArticulation).every(value => value === 0));
    assert.equal(result.metrics.nodes['power-core'], false);
    assert.equal(result.metrics.mechanisms.visible.maker, true);
    assert.equal(result.metrics.mechanisms.visible.mechanic, false);
    assert.deepEqual(result.metrics.camera, camera, 'era reconstruction must preserve camera');
    await screenshot(page, 'maker-era');
    return result;
  });

  await check(page, 'Maker remains fixed; five outside controls articulate without autonomous behavior', async () => {
    const root = await page.evaluate(() => __uncaged.metrics().motion.root);
    await page.waitForTimeout(2000);
    let observed = await page.evaluate(() => ({ snapshot: __uncaged.getSnapshot(), root: __uncaged.metrics().motion.root }));
    assert.deepEqual(observed.root, root, 'Maker root changed while no control was operated');
    assert.equal(observed.snapshot.canReach, false);
    assert.equal(observed.snapshot.visitorPresent, false);
    for (const [id, property] of [['leg', 'leg'], ['wing', 'wing'], ['tail', 'tail'], ['neck', 'neck'], ['jaw', 'jaw']]) {
      const before = await page.evaluate(() => __uncaged.metrics().motion);
      await page.locator(`#lever-${id}`).fill('100');
      await page.waitForFunction(key => __uncaged.metrics().motion.actualArticulation[key] > .97, property, { timeout: 3000 });
      const after = await page.evaluate(() => __uncaged.metrics().motion);
      assert(after.maxFootError < .002, `foot solve error ${after.maxFootError} m exceeds 2 mm`);
      if (id === 'leg') {
        const leftBefore = before.feet.find(foot => foot.side === 'left');
        const leftAfter = after.feet.find(foot => foot.side === 'left');
        const rightAfter = after.feet.find(foot => foot.side === 'right');
        assert(leftAfter.actual[1] - leftBefore.actual[1] > .10, 'left foot did not visibly lift');
        assert.equal(rightAfter.swinging, false, 'support leg must remain planted');
        assert(Math.abs(rightAfter.actual[1] - before.feet.find(foot => foot.side === 'right').actual[1]) < .01);
      }
      assert.deepEqual(after.root, root, `${id} control moved the Maker root`);
      assert.equal(await page.evaluate(() => __uncaged.getSnapshot().canReach), false);
      await page.locator(`#lever-${id}`).fill('0');
      await page.waitForFunction(key => __uncaged.metrics().motion.actualArticulation[key] < .01, property, { timeout: 3000 });
    }
    await page.locator('#release-levers').click();
    observed = await page.evaluate(() => ({ snapshot: __uncaged.getSnapshot(), metrics: __uncaged.metrics() }));
    assert.deepEqual(observed.metrics.motion.root, root);
    assert(Object.values(observed.metrics.motion.actualArticulation).every(value => value < .01));
    return { root, actualArticulation: observed.metrics.motion.actualArticulation, feet: observed.metrics.motion.feet };
  });

  await check(page, 'Maker external inspection and assembly visibility', async () => {
    await enterInspection(page, 100);
    const result = await page.evaluate(() => ({ snapshot: __uncaged.getSnapshot(), metrics: __uncaged.metrics() }));
    assert.equal(result.metrics.nodes['winding-drive'], false);
    assert.equal(result.metrics.nodes['power-core'], false);
    assert.deepEqual(result.metrics.mechanisms.visible, { maker: true, mechanic: false, builder: false });
    assert.deepEqual(result.metrics.mechanisms.externalControlTargets, ['left-foot', 'right-mantle', 'compact-articulated-tail', 'neck', 'jaw']);
    assert.equal(result.snapshot.state, 'inspection');
    await screenshot(page, 'maker-inspection');
    return { open: result.metrics.open, separation: result.metrics.separation, mechanisms: result.metrics.mechanisms };
  });

  await check(page, 'Mechanic spring drive walks in constrained segments and stops on command', async () => {
    await page.locator('[data-era="mechanic"]').click();
    await waitEra(page, 'mechanic');
    const camera = await page.evaluate(() => __uncaged.metrics().camera);
    await screenshot(page, 'mechanic-era');
    const before = await page.evaluate(() => __uncaged.getSnapshot());
    assert.equal(before.capabilities.visitorTracking, false);
    assert.equal(before.capabilities.predatoryBehavior, false);
    assert.equal(before.visitorPresent, false);
    assert.equal(before.canReach, false);
    await page.locator('#run-mechanism').click();
    const states = new Set();
    const stages = new Set();
    let peak = { steps: 0, distance: 0, yaw: 0 };
    const started = Date.now();
    while (Date.now() - started < 12000) {
      const sample = await page.evaluate(() => ({ snapshot: __uncaged.getSnapshot(), motion: __uncaged.metrics().motion }));
      states.add(sample.snapshot.state);
      stages.add(sample.motion.mechanicalStage);
      peak.steps = Math.max(peak.steps, sample.motion.steps);
      peak.distance = Math.max(peak.distance, sample.motion.distance);
      peak.yaw = Math.max(peak.yaw, Math.abs(sample.motion.root.yaw));
      assert.equal(sample.snapshot.visitorPresent, false);
      assert.equal(sample.snapshot.canReach, false);
      assert(sample.motion.maxFootError < .002, `foot solve error ${sample.motion.maxFootError} m exceeds 2 mm`);
      await page.waitForTimeout(100);
    }
    const running = await page.evaluate(() => ({ snapshot: __uncaged.getSnapshot(), metrics: __uncaged.metrics() }));
    assert(peak.steps >= 2, `expected segmented steps, got ${peak.steps}`);
    assert(peak.distance > .25, `expected constrained traversal, got ${peak.distance}`);
    assert(peak.yaw > .25, `expected discrete turn, got ${peak.yaw}`);
    for (const stage of ['load', 'release', 'settle', 'dwell']) assert(stages.has(stage), `missing mechanical stage ${stage}`);
    assert(running.snapshot.energy < 1, 'spring charge did not decrease during the routine');
    assert.equal(running.metrics.nodes['winding-drive'], false, 'legacy winding mesh must stay hidden');
    assert.deepEqual(running.metrics.mechanisms.visible, { maker: false, mechanic: true, builder: false });
    await page.locator('#stop-mechanism').click();
    await page.waitForFunction(() => {
      const s = __uncaged.getSnapshot(), m = __uncaged.metrics().motion;
      return !s.routineRunning && s.state === 'mechanical-ready' && m.settled;
    }, undefined, { timeout: 6000 });
    const stopped = await page.evaluate(() => ({ snapshot: __uncaged.getSnapshot(), motion: __uncaged.metrics().motion }));
    assert(stopped.snapshot.energy < 1);
    assert(stopped.motion.feet.every(foot => !foot.swinging));
    await page.waitForTimeout(500);
    const stableRoot = await page.evaluate(() => __uncaged.metrics().motion.root);
    assert.deepEqual(stableRoot, stopped.motion.root, 'stopped Mechanic moved after settling');
    await page.locator('#wind-mechanism').click();
    near(await page.evaluate(() => __uncaged.getSnapshot().energy), 1);
    assert.deepEqual(await page.evaluate(() => __uncaged.metrics().camera), camera);
    return { states: [...states], stages: [...stages], peak, stopped: stopped.snapshot, rewoundEnergy: await page.evaluate(() => __uncaged.getSnapshot().energy) };
  });

  await check(page, 'Mechanic reduced-motion setting safely ends a running cycle', async () => {
    await page.locator('#run-mechanism').click();
    await page.waitForFunction(() => __uncaged.getSnapshot().routineRunning && __uncaged.metrics().motion.mechanicalPhase > .05,
      undefined, { timeout: 4000 });
    await page.locator('#reduced-motion').check();
    await page.waitForFunction(() => {
      const s = __uncaged.getSnapshot(), m = __uncaged.metrics().motion;
      return !s.routineRunning && ['mechanical-ready', 'mechanical-empty'].includes(s.state) && m.settled;
    }, undefined, { timeout: 6000 });
    const before = await page.evaluate(() => __uncaged.metrics().motion.root);
    await page.waitForTimeout(700);
    const after = await page.evaluate(() => __uncaged.metrics().motion.root);
    assert.deepEqual(after, before);
    assert.equal(await page.evaluate(() => __uncaged.getSnapshot().visitorPresent), false);
    await page.locator('#reduced-motion').uncheck();
    return { root: after, reducedMotion: false };
  });

  await check(page, 'Mechanic inspection exposes transmission; era switches reassemble and reset Maker pose', async () => {
    await enterInspection(page, 100);
    let metrics = await page.evaluate(() => __uncaged.metrics());
    assert.equal(metrics.nodes['winding-drive'], false);
    assert.equal(metrics.nodes['power-core'], false);
    assert.deepEqual(metrics.mechanisms.visible, { maker: false, mechanic: true, builder: false });
    assert.deepEqual(metrics.mechanisms.mechanicTargets, ['left-thigh/left-shin', 'right-thigh/right-shin']);
    await screenshot(page, 'mechanic-inspection');
    await page.locator('[data-era="maker"]').click();
    await waitEra(page, 'maker');
    metrics = await page.evaluate(() => __uncaged.metrics());
    assert.equal(metrics.open, 0);
    assert.equal(metrics.separation, 0);
    assert.deepEqual(metrics.motion.actualArticulation, { leg: 0, wing: 0, tail: 0, neck: 0, jaw: 0 });
    near(metrics.motion.root.x, 0);
    near(metrics.motion.root.z, -.25);
    near(metrics.motion.root.yaw, 0);
    assert.equal(metrics.nodes['power-core'], false);
    assert.deepEqual(metrics.mechanisms.visible, { maker: true, mechanic: false, builder: false });
    return { era: metrics.era, open: metrics.open, separation: metrics.separation, root: metrics.motion.root, visibility: metrics.mechanisms.visible };
  });

  await check(page, 'Builder inspection and exploded-era switch reassemble safely', async () => {
    await page.locator('[data-era="builder"]').click();
    await waitEra(page, 'builder');
    await enterInspection(page, 100);
    const builderBefore = await page.evaluate(() => __uncaged.metrics());
    assert.equal(builderBefore.nodes['power-core'], true);
    assert.equal(builderBefore.nodes.processing, true);
    assert.deepEqual(builderBefore.mechanisms.visible, { maker: false, mechanic: false, builder: true });
    await screenshot(page, 'builder-inspection');
    const camera = builderBefore.camera;
    await page.locator('[data-era="maker"]').click();
    await waitEra(page, 'maker');
    const after = await page.evaluate(() => ({ snapshot: __uncaged.getSnapshot(), metrics: __uncaged.metrics() }));
    assert.equal(after.metrics.open, 0);
    assert.equal(after.metrics.separation, 0);
    assert.equal(after.metrics.nodes['power-core'], false);
    assert.equal(after.metrics.nodes.processing, false);
    assert.deepEqual(after.metrics.mechanisms.visible, { maker: true, mechanic: false, builder: false });
    assert(Object.values(after.metrics.motion.actualArticulation).every(value => value === 0));
    near(after.metrics.motion.root.x, 0);
    near(after.metrics.motion.root.z, -.25);
    near(after.metrics.motion.root.yaw, 0);
    assert.deepEqual(after.metrics.camera, camera);
    return { open: after.metrics.open, separation: after.metrics.separation, root: after.metrics.motion.root, nodes: after.metrics.nodes };
  });

  const fallback = await browser.newPage({ viewport: { width: 1280, height: 960 } });
  pages.push(fallback);
  await setup(fallback, `${devUrl}${devUrl.includes('?') ? '&' : '?'}view=illustrated`, 'illustrated fallback');
  await check(fallback, 'illustrated fallback shows era-specific schematics and disables 3D levers', async () => {
    assert.match(await fallback.locator('#render-label').innerText(), /ILLUSTRATED/);
    assert.equal(await fallback.evaluate(() => __uncaged.metrics().kind), 'illustrated');
    assert(await fallback.locator('.illustrated-view img').evaluate(image => image.complete && image.naturalWidth > 0));
    await fallback.locator('[data-era="maker"]').click();
    await waitEra(fallback, 'maker');
    assert.equal(await fallback.locator('#lever-leg').isDisabled(), true);
    await enterInspection(fallback, 0);
    assert(await fallback.locator('.assembly-diagram').isVisible());
    const visible = async id => fallback.locator(`[data-schematic="${id}"]`).evaluate(node => getComputedStyle(node).display !== 'none');
    assert.equal(await visible('external'), true);
    assert.equal(await visible('transmission'), false);
    assert.equal(await visible('power'), false);
    assert.equal(await visible('mind'), false);
    assert.match(await fallback.locator('.diagram-note').innerText(), /outside operator.*cradle/i);
    await screenshot(fallback, 'illustrated-maker');
    await fallback.locator('[data-era="mechanic"]').click();
    await waitEra(fallback, 'mechanic');
    await enterInspection(fallback, 0);
    assert(await fallback.locator('.assembly-diagram').isVisible());
    assert.equal(await visible('external'), false);
    assert.equal(await visible('transmission'), true);
    assert.equal(await visible('power'), false);
    assert.equal(await visible('mind'), false);
    assert.match(await fallback.locator('.diagram-note').innerText(), /mainspring.*reduction gears.*cam/i);
    await screenshot(fallback, 'illustrated-mechanic');
    await fallback.locator('[data-era="builder"]').click();
    await waitEra(fallback, 'builder');
    await enterInspection(fallback, 0);
    assert(await fallback.locator('.assembly-diagram').isVisible());
    assert.equal(await visible('external'), false);
    assert.equal(await visible('transmission'), false);
    assert.equal(await visible('power'), true);
    assert.equal(await visible('mind'), true);
    assert.match(await fallback.locator('.diagram-note').innerText(), /abundant fictional supply.*sensing and processing/i);
    await screenshot(fallback, 'illustrated-builder');
    return { eras: ['maker', 'mechanic', 'builder'], makerLeversDisabled: await fallback.locator('#lever-leg').isDisabled() };
  });

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, hasTouch: true, isMobile: true });
  pages.push(mobile);
  await setup(mobile, devUrl, 'mobile dev');
  await check(mobile, '390x844 mobile controls, labels, touch, and no horizontal overflow', async () => {
    await mobile.locator('[data-era="maker"]').click();
    await waitEra(mobile, 'maker');
    assert(await mobile.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    for (const id of ['leg', 'wing', 'tail', 'neck', 'jaw']) {
      assert(await mobile.locator(`#lever-${id}`).isVisible());
      assert(await mobile.locator(`#lever-${id}`).getAttribute('aria-label'));
    }
    await mobile.locator('#lever-wing').fill('75');
    await mobile.waitForFunction(() => __uncaged.metrics().motion.actualArticulation.wing > .7);
    await mobile.locator('#release-levers').tap();
    await mobile.waitForFunction(() => __uncaged.metrics().motion.actualArticulation.wing < .01);
    await mobile.locator('#viewer').scrollIntoViewIfNeeded();
    await screenshot(mobile, 'mobile-maker');
    return { viewport: { width: 390, height: 844 }, scrollWidth: await mobile.evaluate(() => document.documentElement.scrollWidth) };
  });

  const production = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  pages.push(production);
  await setup(production, productionUrl, 'production preview');
  await check(production, 'production preview retains WebGL and excludes development QA hook', async () => {
    assert.equal(await production.evaluate(() => typeof window.__uncaged), 'undefined');
    assert.equal(await production.locator('#scene canvas').count(), 1);
    assert.equal(await production.locator('#render-label').innerText().then(text => text.startsWith('3D')), true);
    assert.equal(await production.locator('#sound-toggle').getAttribute('aria-pressed'), 'false');
    return { render: await production.locator('#render-label').innerText(), canvas: await production.locator('#scene canvas').count() };
  });

  await check(page, 'browser console and page error health', async () => {
    assert.deepEqual(report.errors, []);
    return { pages: pages.length, consoleErrors: report.errors.length };
  });
} catch (error) {
  report.failure = error.stack || error.message;
  process.exitCode = 1;
  console.error(error.message);
} finally {
  await browser.close();
  await writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`);
  console.log(JSON.stringify({ reportPath, checks: report.checks.map(({ name, status }) => ({ name, status })), errors: report.errors.length }, null, 2));
}
