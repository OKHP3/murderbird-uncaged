import test from 'node:test';
import assert from 'node:assert/strict';
import {BASE_PATCHES, applyBasePatch} from '../scripts/plates-overlay-patch.mjs';

const page = '<!doctype html>\n<html>\n  <body>\n    <div id="app"></div>\n  </body>\n</html>\n';
const sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url>\n    <loc>https://okhp3.github.io/murderbird-uncaged/</loc>\n  </url>\n  <url>\n    <loc>https://okhp3.github.io/murderbird-uncaged/cg.html</loc>\n  </url>\n</urlset>';

test('allowlist names exactly the three base files', () => {
  assert.deepEqual(Object.keys(BASE_PATCHES).sort(), ['folio.html', 'index.html', 'sitemap.xml']);
});

test('pages gain the Living Plates route once, after the app root', () => {
  for (const path of ['index.html', 'folio.html']) {
    const out = applyBasePatch(path, page);
    assert.ok(out.startsWith(page.slice(0, page.indexOf('  </body>'))));
    assert.equal(out.split('data-plates-navigation').length, 2);
    assert.match(out, /href = '\.\/plates\/'/);
    assert.ok(out.endsWith('  </body>\n</html>\n'));
  }
});

test('sitemap gains folio and plates entries after the CG entry', () => {
  const out = applyBasePatch('sitemap.xml', sitemap);
  const cg = out.indexOf('/cg.html</loc>');
  assert.ok(cg > 0 && out.indexOf('/folio.html</loc>') > cg && out.indexOf('/plates/</loc>') > cg);
  assert.ok(out.endsWith('</urlset>'));
});

test('missing anchor fails closed', () => {
  assert.throws(() => applyBasePatch('index.html', page.replace('<div id="app"></div>', '<main></main>')), /exactly once, found 0/);
  assert.throws(() => applyBasePatch('sitemap.xml', sitemap.replace('cg.html', 'other.html')), /exactly once, found 0/);
});

test('duplicated anchor fails closed', () => {
  const doubled = page.replace('    <div id="app"></div>\n', '    <div id="app"></div>\n    <div id="app"></div>\n');
  assert.throws(() => applyBasePatch('folio.html', doubled), /exactly once, found 2/);
});

test('already patched or non-allowlisted input fails closed', () => {
  assert.throws(() => applyBasePatch('index.html', applyBasePatch('index.html', page)), /already contains/);
  assert.throws(() => applyBasePatch('cg.html', page), /No overlay patch is allowlisted/);
});
