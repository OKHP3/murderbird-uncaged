import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

assert.ok(process.argv[2], 'Pass the installed Playwright module path.');
const { chromium } = await import(pathToFileURL(process.argv[2]).href);

const root = process.cwd();
const base = process.env.REVIEW_BASE || 'http://127.0.0.1:5177';
const gallery = process.env.REVIEW_PATH || '/assets/audit/alignment-v5-regional/index.html';
const output = path.resolve(process.env.REVIEW_AUDIT || 'assets/audit/alignment-v5-regional/gallery-checks-candidate02');
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
await fs.mkdir(output, { recursive: true });
const receipt = { status: 'running', url: base + gallery, htmlSha256: sha(await fs.readFile(path.join(root, gallery))), viewports: [], errors: [], scope: 'Gallery rendering and resource availability only; no model or motion acceptance.' };
const browser = await chromium.launch({ headless: false });
try {
  receipt.browser = browser.version();
  for (const viewport of [{ width: 1440, height: 1000 }, { width: 390, height: 844 }]) {
    const page = await browser.newPage({ viewport, deviceScaleFactor: 1 });
    page.on('pageerror', error => receipt.errors.push(error.message));
    await page.goto(receipt.url, { waitUntil: 'networkidle' });
    for (const image of await page.locator('img').all()) {
      await image.scrollIntoViewIfNeeded();
      await image.evaluate(element => element.decode());
    }
    const state = await page.evaluate(() => ({
      images: [...document.images].map(img => ({ src: img.getAttribute('src'), naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight, width: img.getBoundingClientRect().width, height: img.getBoundingClientRect().height })),
      links: [...new Set([...document.querySelectorAll('a[href],video[src]')].map(el => el.href || el.src))],
      scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth,
      comparisonColumns: getComputedStyle(document.querySelector('.comparison')).gridTemplateColumns
    }));
    assert.equal(state.scrollWidth, state.clientWidth, 'Horizontal overflow');
    assert.ok(state.images.length >= 18 && state.images.every(img => img.naturalWidth > 0 && img.naturalHeight > 0 && img.width > 0 && img.height > 0));
    for (const url of state.links) {
      const response = await page.request.head(url);
      assert.equal(response.status(), 200, url);
    }
    await page.evaluate(() => scrollTo(0, 0));
    await page.screenshot({ path: path.join(output, `gallery-${viewport.width}.png`) });
    receipt.viewports.push({ viewport, ...state, linksChecked: state.links.length });
    await page.close();
  }
  assert.equal(receipt.errors.length, 0);
  receipt.status = 'passed';
} finally {
  await browser.close();
  await fs.writeFile(path.join(output, 'gallery-validation.json'), JSON.stringify(receipt, null, 2) + '\n');
  await fs.copyFile(new URL(import.meta.url), path.join(output, 'executed-gallery-check.mjs.txt'));
}
console.log(JSON.stringify({ status: receipt.status, images: receipt.viewports.map(v => v.images.length), output }));
