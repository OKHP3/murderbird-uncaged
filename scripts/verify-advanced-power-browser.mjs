/**
 * Browser QA for the advanced-only jump and shield-thrust actions.
 * Uses an already installed Playwright entry point passed as argv[2], never an
 * app dependency. Run only after root confirms the local visual pass is ready.
 */
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

if (!process.argv[2]) throw new Error('Pass the existing Playwright entry module as argv[2].');
const { chromium } = await import(pathToFileURL(process.argv[2]).href);
const devUrl = process.env.UNCAGED_DEV_URL || 'http://127.0.0.1:5174/';
for (const value of [devUrl]) {
  if (!['127.0.0.1', 'localhost'].includes(new URL(value).hostname)) {
    throw new Error('Advanced power-move QA may only use a loopback preview.');
  }
}

const outputDir = path.resolve(process.env.UNCAGED_AUDIT || 'assets/audit/structural-reconciliation-v1');
const reportPath = path.join(outputDir, 'power-browser-validation.json');
await mkdir(outputDir, { recursive: true });
const browser = await chromium.launch({ headless: false });
const report = { generatedAt: new Date().toISOString(), devUrl, browser: browser.version(), checks: [], errors: [], screenshots: [] };
const pages = [];

function observe(page, label) {
  page.on('pageerror', error => report.errors.push({ page: label, type: 'pageerror', message: error.message }));
  page.on('console', message => {
    if (message.type() === 'error') report.errors.push({ page: label, type: 'console', message: message.text() });
  });
}

async function screenshot(page, name) {
  const file = `${name}.png`;
  await page.locator('#viewer').screenshot({ path: path.join(outputDir, file) });
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
    const failureShot = `failure-power-${name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.png`;
    await screenshot(page, failureShot).catch(() => {});
    report.checks.push({ name, status: 'failed', error: error.message, diagnostic, screenshot: failureShot });
    throw error;
  }
}

async function setup(page, url = devUrl, label = 'power dev') {
  observe(page, label);
  await page.route('**/*googletagmanager.com/**', route => route.fulfill({ status: 200, contentType: 'text/javascript', body: '' }));
  await page.goto(url);
  await page.locator('#loading').waitFor({ state: 'hidden', timeout: 30000 });
}

async function waitEra(page, era) {
  await page.waitForFunction(target => {
    const snapshot = window.__uncaged?.getSnapshot?.();
    return snapshot?.era === target && !snapshot.pendingEra;
  }, era, { timeout: 15000 });
  if (era === 'builder') {
    await page.waitForFunction(() => window.__uncaged?.metrics?.()?.kind === 'webgl', undefined, { timeout: 10000 });
  }
}

async function waitReady(page, timeout = 20000) {
  await page.waitForFunction(() => {
    const snapshot = window.__uncaged?.getSnapshot?.();
    const metrics = window.__uncaged?.metrics?.();
    return snapshot?.era === 'builder' && !snapshot.pendingEra && snapshot.canReach
      && !snapshot.visitorPresent && !snapshot.powerMove && !snapshot.inspection
      && metrics?.kind === 'webgl' && !metrics.motion?.powerMove;
  }, undefined, { timeout });
}

async function waitMoveStart(page, kind) {
  await page.waitForFunction(target => window.__uncaged?.getSnapshot?.()?.powerMove?.kind === target,
    kind, { timeout: 4000 });
  return page.evaluate(() => ({ snapshot: __uncaged.getSnapshot(), metrics: __uncaged.metrics() }));
}

async function waitPhase(page, kind, minimum, maximum) {
  await page.waitForFunction(({ target, min, max }) => {
    const snapshot = window.__uncaged?.getSnapshot?.();
    const move = snapshot?.powerMove;
    return move?.kind === target && move.phase >= min && move.phase <= max;
  }, { target: kind, min: minimum, max: maximum }, { polling: 10, timeout: 4000 });
  return page.evaluate(() => ({ snapshot: __uncaged.getSnapshot(), metrics: __uncaged.metrics() }));
}

function near(actual, expected, tolerance = .005) {
  assert(Math.abs(actual - expected) <= tolerance, `expected ${actual} within ${tolerance} of ${expected}`);
}

function assertGrounded(motion, referenceGround, tolerance = .005) {
  assert(motion.feet.every(foot => !foot.swinging), 'feet should be planted');
  for (const foot of motion.feet) {
    const baseline = referenceGround.find(item => item.side === foot.side);
    near(foot.groundMin, baseline.groundMin, tolerance);
    assert(foot.solveError < .002, `foot solve error ${foot.solveError} m exceeds 2 mm`);
  }
}

async function captureMoveTrace(page, finish, timeout = 6000) {
  const samples = [];
  const started = Date.now();
  while (Date.now() - started < timeout) {
    const sample = await page.evaluate(() => ({ snapshot: __uncaged.getSnapshot(), motion: __uncaged.metrics().motion }));
    samples.push({ era: sample.snapshot.era, pendingEra: sample.snapshot.pendingEra, snapshotMove: sample.snapshot.powerMove, motionMove: sample.motion.powerMove });
    if (finish(sample)) return samples;
    await page.waitForTimeout(10);
  }
  assert.fail(`power-move transition did not finish within ${timeout} ms`);
}

try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  pages.push(page);
  await setup(page);
  await check(page, 'advanced actions are present, named, and gated until a ready Builder state', async () => {
    assert.equal(await page.evaluate(() => typeof window.__uncaged), 'object');
    assert.equal(await page.locator('#scene canvas').count(), 1);
    for (const [selector, text] of [['#power-jump', 'Power jump'], ['#shield-thrust', 'Shield thrust']]) {
      assert.equal(await page.locator(selector).innerText(), text);
      assert.equal(await page.locator(selector).getAttribute('data-capability'), 'advanced');
      assert(await page.locator(selector).isVisible());
    }
    await waitReady(page);
    assert.equal(await page.locator('#power-jump').isDisabled(), false);
    assert.equal(await page.locator('#shield-thrust').isDisabled(), false);
    return { era: await page.evaluate(() => __uncaged.getSnapshot().era), kind: await page.evaluate(() => __uncaged.metrics().kind) };
  });

  await check(page, 'power jump loads grounded, clears the floor, peaks, and lands planted', async () => {
    const before = await page.evaluate(() => ({
      snapshot: __uncaged.getSnapshot(),
      metrics: __uncaged.metrics(),
    }));
    const referenceGround = before.metrics.motion.feet.map(({ side, groundMin }) => ({ side, groundMin }));
    const root = before.metrics.motion.root;
    await page.locator('#power-jump').click();
    const start = await waitMoveStart(page, 'jump');
    near(start.snapshot.powerMove.duration, 1.4, .001);
    assert(start.snapshot.powerMove.phase < .08, `jump did not begin in its load phase (${start.snapshot.powerMove.phase})`);
    assert(start.metrics.motion.powerMove?.grounded, 'jump load phase should still be grounded');
    const peak = await waitPhase(page, 'jump', .40, .44);
    const pose = peak.metrics.motion.powerMove;
    assert.equal(pose.stage, 'airborne');
    assert.equal(pose.grounded, false);
    assert(pose.height > .25, `jump height too small: ${pose.height} m`);
    assert(peak.metrics.motion.feet.every(foot => foot.groundMin - referenceGround.find(ref => ref.side === foot.side).groundMin > .20),
      'actual foot geometry did not clear the floor during flight');
    assert(peak.metrics.motion.maxFootError < .002);
    await screenshot(page, 'advanced-power-jump-peak');
    await page.waitForFunction(() => {
      const s = __uncaged.getSnapshot(), m = __uncaged.metrics().motion;
      return !s.powerMove && !m.powerMove && s.canReach && m.settled;
    }, undefined, { timeout: 5000 });
    const landed = await page.evaluate(() => ({ snapshot: __uncaged.getSnapshot(), motion: __uncaged.metrics().motion }));
    assertGrounded(landed.motion, referenceGround);
    near(landed.motion.root.x, root.x);
    near(landed.motion.root.z, root.z);
    near(landed.motion.root.yaw, root.yaw);
    return { start: start.snapshot.powerMove, peak: pose, landed: landed.motion.feet, root: landed.motion.root };
  });

  await check(page, 'shield thrust braces on the floor and drives the shoulder and elbow', async () => {
    await waitReady(page);
    const before = await page.evaluate(() => __uncaged.metrics());
    const referenceGround = before.motion.feet.map(({ side, groundMin }) => ({ side, groundMin }));
    const root = before.motion.root;
    await page.locator('#shield-thrust').click();
    const start = await waitMoveStart(page, 'thrust');
    near(start.snapshot.powerMove.duration, 1.1, .001);
    assert(start.snapshot.powerMove.phase < .08);
    const drive = await waitPhase(page, 'thrust', .49, .52);
    const pose = drive.metrics.motion.powerMove;
    assert.equal(pose.stage, 'brace');
    assert.equal(pose.grounded, true);
    near(pose.height, 0, .001);
    assertGrounded(drive.metrics.motion, referenceGround);
    assert(Math.abs(drive.metrics.wingAngles.rightShoulder - before.wingAngles.rightShoulder) > .25,
      'right shoulder did not drive the shield');
    assert(Math.abs(drive.metrics.wingAngles.rightElbow - before.wingAngles.rightElbow) > .35,
      'right elbow did not drive the armored forewing');
    near(drive.metrics.motion.root.x, root.x);
    near(drive.metrics.motion.root.z, root.z);
    await screenshot(page, 'advanced-shield-thrust-drive');
    await page.waitForFunction(() => {
      const s = __uncaged.getSnapshot(), m = __uncaged.metrics().motion;
      return !s.powerMove && !m.powerMove && s.canReach && m.settled;
    }, undefined, { timeout: 5000 });
    const after = await page.evaluate(() => __uncaged.metrics().motion);
    assertGrounded(after, referenceGround);
    near(after.root.x, root.x);
    near(after.root.z, root.z);
    return { start: start.snapshot.powerMove, drive: pose, shoulder: drive.metrics.wingAngles.rightShoulder, elbow: drive.metrics.wingAngles.rightElbow };
  });

  await check(page, 'actions hide outside Builder and reduced motion blocks them', async () => {
    await page.locator('[data-era="maker"]').click();
    await waitEra(page, 'maker');
    for (const selector of ['#power-jump', '#shield-thrust']) {
      assert.equal(await page.locator(selector).isVisible(), false);
      assert.equal(await page.locator(selector).isDisabled(), true);
    }
    await page.locator('[data-era="mechanic"]').click();
    await waitEra(page, 'mechanic');
    for (const selector of ['#power-jump', '#shield-thrust']) {
      assert.equal(await page.locator(selector).isVisible(), false);
      assert.equal(await page.locator(selector).isDisabled(), true);
    }
    await page.locator('[data-era="builder"]').click();
    await waitEra(page, 'builder');
    await waitReady(page);
    await page.locator('#reduced-motion').check();
    assert.equal(await page.locator('#power-jump').isDisabled(), true);
    assert.equal(await page.locator('#shield-thrust').isDisabled(), true);
    const moveBefore = await page.evaluate(() => __uncaged.getSnapshot().powerMove);
    await page.waitForTimeout(400);
    assert.deepEqual(await page.evaluate(() => __uncaged.getSnapshot().powerMove), moveBefore);
    await page.locator('#reduced-motion').uncheck();
    await waitReady(page);
    return { hiddenForMakerAndMechanic: true, reducedMotionBlocked: true };
  });

  await check(page, 'era switch requested during airborne phase waits for a controlled landing', async () => {
    await waitReady(page);
    const reference = await page.evaluate(() => ({
      root: __uncaged.metrics().motion.root,
      feet: __uncaged.metrics().motion.feet.map(({ side, groundMin }) => ({ side, groundMin })),
    }));
    await page.locator('#power-jump').click();
    const airborne = await waitPhase(page, 'jump', .40, .44);
    assert(airborne.metrics.motion.powerMove.height > .25);
    await page.locator('[data-era="maker"]').click();
    const trace = await captureMoveTrace(page, sample => sample.snapshot.era === 'maker' && !sample.snapshot.pendingEra, 7000);
    const previous = trace.findLast(sample => sample.snapshotMove?.kind === 'jump');
    assert(previous, 'jump trace disappeared before the era transition completed');
    assert(trace.some(sample => sample.snapshotMove?.kind === 'jump'
      && sample.motionMove?.stage === 'landing' && sample.motionMove.grounded), 'transition omitted a grounded landing phase');
    assert(previous.motionMove.height <= .005, `era switched before landing: ${previous.motionMove.height} m`);
    const final = await page.evaluate(() => ({ snapshot: __uncaged.getSnapshot(), metrics: __uncaged.metrics() }));
    assert.equal(final.snapshot.era, 'maker');
    assert.equal(final.metrics.motion.powerMove, null);
    assertGrounded(final.metrics.motion, reference.feet);
    near(final.metrics.motion.root.x, 0);
    near(final.metrics.motion.root.z, -.25);
    assert.equal(final.snapshot.canReach, false);
    await screenshot(page, 'advanced-jump-era-transition-landed');
    return { airbornePhase: airborne.snapshot.powerMove.phase, transitionSamples: trace.length, finalEra: final.snapshot.era, root: final.metrics.motion.root };
  });

  await check(page, 'inspection requested midair opens only after the jump has landed', async () => {
    await page.locator('[data-era="builder"]').click();
    await waitEra(page, 'builder');
    await waitReady(page);
    const reference = await page.evaluate(() => __uncaged.metrics().motion.feet.map(({ side, groundMin }) => ({ side, groundMin })));
    await page.locator('#power-jump').click();
    const airborne = await waitPhase(page, 'jump', .40, .44);
    assert(airborne.metrics.motion.powerMove.height > .25);
    await page.locator('#section-toggle').click();
    const trace = await captureMoveTrace(page, sample => sample.snapshot.inspection === true && sample.snapshot.era === 'builder'
      && sample.motion.powerMove === null, 7000);
    assert(trace.some(sample => sample.motionMove?.stage === 'landing' && sample.motionMove.grounded),
      'inspection transition skipped its grounded landing phase');
    await page.waitForFunction(() => __uncaged.metrics().open > .99, undefined, { timeout: 6000 });
    const final = await page.evaluate(() => ({ snapshot: __uncaged.getSnapshot(), metrics: __uncaged.metrics() }));
    assert.equal(final.snapshot.inspection, true);
    assert(final.metrics.open > .99);
    assertGrounded(final.metrics.motion, reference);
    await screenshot(page, 'advanced-jump-inspection-landed');
    return { airbornePhase: airborne.snapshot.powerMove.phase, transitionSamples: trace.length, inspection: final.snapshot.inspection, open: final.metrics.open };
  });

  const fallback = await browser.newPage({ viewport: { width: 1280, height: 960 } });
  pages.push(fallback);
  observe(fallback, 'illustrated fallback');
  await fallback.route('**/*googletagmanager.com/**', route => route.fulfill({ status: 200, contentType: 'text/javascript', body: '' }));
  await fallback.goto(`${devUrl}${devUrl.includes('?') ? '&' : '?'}view=illustrated`);
  await fallback.locator('#loading').waitFor({ state: 'hidden', timeout: 30000 });
  await check(fallback, 'power actions remain unavailable in illustrated fallback', async () => {
    assert.equal(await fallback.evaluate(() => __uncaged.metrics().kind), 'illustrated');
    for (const selector of ['#power-jump', '#shield-thrust']) {
      assert(await fallback.locator(selector).isVisible());
      assert.equal(await fallback.locator(selector).isDisabled(), true);
    }
    return { fallback: await fallback.locator('#render-label').innerText(), actionsDisabled: true };
  });

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, hasTouch: true, isMobile: true, reducedMotion: 'no-preference' });
  pages.push(mobile);
  await setup(mobile, devUrl, 'mobile advanced actions');
  await check(mobile, 'mobile power controls fit and remain labelled', async () => {
    await waitReady(mobile);
    assert(await mobile.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    for (const [selector, expected] of [['#power-jump', 'Power jump'], ['#shield-thrust', 'Shield thrust']]) {
      const button = mobile.locator(selector);
      assert(await button.isVisible());
      assert.equal((await button.innerText()).trim(), expected);
      assert(await button.getAttribute('aria-label') || (await button.innerText()).trim());
    }
    await mobile.locator('#controls').scrollIntoViewIfNeeded();
    await screenshot(mobile, 'mobile-advanced-power-controls');
    return { viewport: { width: 390, height: 844 }, scrollWidth: await mobile.evaluate(() => document.documentElement.scrollWidth) };
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
