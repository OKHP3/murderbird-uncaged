import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {COPY_FIXES, COPY_PATTERN_FIXES, applyCopyFixes, isCopyFixTarget} from '../scripts/final-copy-fixes.mjs';

const read = path => readFileSync(new URL(`../${path}`, import.meta.url), 'utf8');

test('main source already carries every copy fix', () => {
  for (const fix of COPY_FIXES) {
    const text = read(fix.source);
    assert.ok(!text.includes(fix.find), `${fix.source} still has: ${fix.find.slice(0, 50)}`);
    assert.ok(text.includes(fix.replace), `${fix.source} lacks: ${fix.replace.slice(0, 50)}`);
  }
  for (const fix of COPY_PATTERN_FIXES) {
    const text = read(fix.source);
    assert.equal((text.match(fix.find) || []).length, 0);
    assert.ok(text.includes(fix.marker));
  }
});

test('no pending-acceptance wording or pinned pre-flatten source path remains in published source', () => {
  for (const path of ['index.html', 'cg.html', 'src/main.js', 'src/cg-main.js', 'scripts/write-release-manifest.mjs']) {
    const text = read(path);
    assert.doesNotMatch(text, /acceptance (remains? )?pending|acceptance remain pending|ACCEPTANCE PENDING/i, path);
    assert.doesNotMatch(text, /e305989bff863aab827a0bdc4ee3395de32e0d61/, path);
  }
});

function liveLike() {
  const files = {};
  for (const fix of COPY_FIXES) {
    const path = fix.target.source.replace(/^\^|\$$/g, '').replace('\\.', '.').replace('assets\\/', 'assets/').replace('[A-Za-z0-9_-]+', 'Ab12');
    files[path] = (files[path] || '') + `<x>${fix.find}</x>\n`;
  }
  const pattern = COPY_PATTERN_FIXES[0];
  files['assets/cg-Ab12.js'] += 'o.href=`https://github.com/OKHP3/murderbird-uncaged/blob/e305989bff863aab827a0bdc4ee3395de32e0d61/assets/audit/cg-recursive-three-loop01/loop03/delivery/retained04/${s.value}/murderbird-recursive-${s.value}.blend`';
  assert.ok(pattern);
  return files;
}

test('fixes apply once to live-shaped files, keep the bundle variable, and refuse a second pass', () => {
  const files = liveLike();
  assert.deepEqual(applyCopyFixes(files), ['assets/cg-Ab12.js', 'assets/exhibit-Ab12.js', 'cg.html', 'index.html']);
  for (const fix of COPY_FIXES) assert.ok(Object.values(files).some(text => text.includes(fix.replace)));
  assert.match(files['assets/cg-Ab12.js'], /blob\/main\/media\/cg-retained04-\$\{s\.value\}-murderbird-recursive-\$\{s\.value\}\.blend/);
  assert.throws(() => applyCopyFixes(files), /already present/);
});

test('a missing or repeated anchor fails closed', () => {
  const missing = liveLike();
  missing['cg.html'] = '';
  assert.throws(() => applyCopyFixes(missing), /exactly once, found 0/);
  const doubled = liveLike();
  doubled['index.html'] += doubled['index.html'];
  assert.throws(() => applyCopyFixes(doubled), /exactly once, found 2/);
});

test('only the pages and bundles named by the fixes are targets', () => {
  assert.ok(isCopyFixTarget('index.html') && isCopyFixTarget('cg.html'));
  assert.ok(isCopyFixTarget('assets/exhibit-C4QPo_JQ.js') && isCopyFixTarget('assets/cg-D8bZ-tI0.js'));
  for (const path of ['folio.html', 'sitemap.xml', 'assets/folio-CiPzIS1z.js', 'assets/cg-DCq6Guii.css', 'plates/index.html', 'cg/retained04/builder/hero.png']) assert.ok(!isCopyFixTarget(path), path);
});
