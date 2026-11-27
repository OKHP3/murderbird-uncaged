import test from 'node:test';
import assert from 'node:assert/strict';
import {BASE_PATCHES, applyBasePatch, revertBasePatch} from '../scripts/plates-overlay-patch.mjs';

const samples = {
  'index.html': '<body>\n    <div id="app"></div>\n</body>\n',
  'folio.html': '<body>\n    <div id="app"></div>\n</body>\n',
  'sitemap.xml': `<urlset>\n${BASE_PATCHES['sitemap.xml'].anchor}</urlset>\n`,
};

test('revertBasePatch restores the exact base text an earlier overlay patched', () => {
  for (const [path, base] of Object.entries(samples)) {
    assert.equal(revertBasePatch(path, applyBasePatch(path, base)), base, path);
  }
});

test('revertBasePatch refuses text without exactly one earlier patch', () => {
  assert.throws(() => revertBasePatch('index.html', samples['index.html']), /exactly once, found 0/);
  const twice = applyBasePatch('index.html', samples['index.html']).replace('</body>', `${BASE_PATCHES['index.html'].anchor}${BASE_PATCHES['index.html'].insert}</body>`);
  assert.throws(() => revertBasePatch('index.html', twice), /exactly once, found 2/);
  assert.throws(() => revertBasePatch('cg.html', 'x'), /No overlay patch/);
});
