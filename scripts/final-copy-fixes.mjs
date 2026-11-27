/**
 * v1.1 final copy fixes (owner direction, November 27, 2026: "Keep v1.1 final").
 *
 * Each fix states one exact published string and its replacement. The same fixes are already
 * applied to the source on main, so a later standard publication carries them on its own. Until
 * then the plates overlay applies them to the live base release, which needs no Git LFS:
 * every fix must match exactly once in the one live file its target pattern selects, or the
 * publication stops. No fix changes likeness, model, motion or publication status. They only
 * replace "acceptance pending" wording with the recorded disposition (frozen at v1.0, likeness
 * parked, not accepted), name era III as Advanced in the exhibit, and repoint links to files
 * the November 19 flatten moved or retired.
 */

const REPO = 'https://github.com/OKHP3/murderbird-uncaged/blob';
const PINNED = `${REPO}/e305989bff863aab827a0bdc4ee3395de32e0d61/assets/audit/cg-recursive-three-loop01/loop03`;
const PARKED = 'frozen at v1.0 with source likeness parked';

const INDEX = /^index\.html$/;
const CG_PAGE = /^cg\.html$/;
const EXHIBIT_JS = /^assets\/exhibit-[A-Za-z0-9_-]+\.js$/;
const CG_JS = /^assets\/cg-[A-Za-z0-9_-]+\.js$/;

export const COPY_FIXES = Object.freeze([
  {target: INDEX, source: 'index.html', find: 'Explore exterior proposals, era-specific movement and inspection. Artistic acceptance remains pending.', replace: `Explore exterior proposals, era-specific movement and inspection. The study is ${PARKED}.`},
  {target: INDEX, source: 'index.html', find: 'Interactive inspection and review evidence; artistic acceptance pending.', replace: `Interactive inspection and review evidence, ${PARKED}.`},
  {target: INDEX, source: 'index.html', find: 'Maker, Mechanic and Advanced states; artistic acceptance pending.', replace: `Maker, Mechanic and Advanced states, ${PARKED}.`},
  {target: INDEX, source: 'index.html', find: 'construction proposals, with artistic acceptance pending.', replace: `construction proposals, ${PARKED}.`},
  {target: INDEX, source: 'index.html', find: 'og:image:alt" content="MurderBird: Uncaged — one inherited body, three eras. Mechanical bird reference art; interactive exhibit under assessment."', replace: 'og:image:alt" content="MurderBird: Uncaged. One inherited body, three eras. Mechanical bird reference art; interactive exhibit frozen at v1.0."'},
  {target: INDEX, source: 'index.html', find: 'twitter:image:alt" content="MurderBird: Uncaged — one inherited body, three eras. Mechanical bird reference art; interactive exhibit under assessment."', replace: 'twitter:image:alt" content="MurderBird: Uncaged. One inherited body, three eras. Mechanical bird reference art; interactive exhibit frozen at v1.0."'},
  {target: CG_PAGE, source: 'cg.html', find: 'and exhibit renders. Source likeness and owner artistic acceptance remain pending.">', replace: 'and exhibit renders. Frozen at v1.0; source likeness is parked, not accepted.">'},
  {target: CG_PAGE, source: 'cg.html', find: 'Published for assessment; artistic acceptance pending.', replace: 'Frozen at v1.0; source likeness parked, not accepted.'},
  {target: CG_PAGE, source: 'cg.html', find: '<h1>MurderBird CG assessment</h1><p>Source likeness and owner artistic acceptance remain pending.', replace: '<h1>MurderBird CG assessment</h1><p>Frozen at v1.0. Source likeness is parked, not accepted.'},
  {target: EXHIBIT_JS, source: 'src/main.js', find: '<span id="era-label">III · BUILDER</span>', replace: '<span id="era-label">III · ADVANCED</span>'},
  {target: EXHIBIT_JS, source: 'src/main.js', find: '<span>III / BUILDER</span>', replace: '<span>III / ADVANCED</span>'},
  {target: EXHIBIT_JS, source: 'src/main.js', find: 'these CG surfaces have no animation or mechanism rig. Source likeness and owner artistic acceptance remain pending.', replace: 'these CG surfaces have no animation or mechanism rig. The study is frozen at v1.0. Source likeness is parked, not accepted.'},
  {target: CG_JS, source: 'src/cg-main.js', find: '<strong>Published for assessment. Source likeness and owner artistic acceptance remain pending.</strong>', replace: '<strong>Frozen at v1.0. Source likeness is parked, not accepted.</strong>'},
  {target: CG_JS, source: 'src/cg-main.js', find: 'ASSESSMENT CANDIDATE · ARTISTIC ACCEPTANCE PENDING', replace: 'FROZEN AT V1.0 · LIKENESS PARKED'},
  {target: CG_JS, source: 'src/cg-main.js', find: 'lighting. Source likeness and owner acceptance pending.', replace: 'lighting. Source likeness parked, not accepted.'},
  {target: CG_JS, source: 'src/cg-main.js', find: `${PINNED}/delivery/retained04/builder/murderbird-recursive-builder.blend`, replace: `${REPO}/main/media/cg-retained04-builder-murderbird-recursive-builder.blend`},
  {target: CG_JS, source: 'src/cg-main.js', find: `${PINNED}/final-adjudication.json`, replace: `${REPO}/archive/pre-flatten-2026-11-19/assets/audit/cg-recursive-three-loop01/loop03/final-adjudication.json`},
  {target: CG_JS, source: 'src/cg-main.js', find: 'issues/14">Cross-system review ↗</a>', replace: 'issues/14">Cross-system review record (closed) ↗</a>'},
]);

// The era-specific source link is built at runtime. Its bundled form names a minified variable,
// so it is matched as a pattern; the published replacement keeps whatever name the bundle uses.
export const COPY_PATTERN_FIXES = Object.freeze([
  {
    target: CG_JS,
    source: 'src/cg-main.js',
    find: new RegExp(`${PINNED.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&')}/delivery/retained04/\\$\\{([A-Za-z_$][\\w$]*(?:\\.[A-Za-z_$][\\w$]*)*)\\}/murderbird-recursive-\\$\\{\\1\\}\\.blend`, 'g'),
    replace: (_, era) => `${REPO}/main/media/cg-retained04-\${${era}}-murderbird-recursive-\${${era}}.blend`,
    marker: `${REPO}/main/media/cg-retained04-\${`,
  },
]);

function count(text, needle) {
  let n = 0;
  for (let at = text.indexOf(needle); at !== -1; at = text.indexOf(needle, at + needle.length)) n += 1;
  return n;
}

/**
 * Applies every fix to a map of {path: text}. Each required fix must match exactly once across
 * the files its target selects. A fix whose replacement is already present, or whose anchor is
 * missing or repeated, stops with an error. Returns the paths that changed.
 */
export function applyCopyFixes(files) {
  const changed = new Set();
  const paths = Object.keys(files);
  for (const fix of COPY_FIXES) {
    const hits = paths.filter(path => fix.target.test(path)).map(path => [path, count(files[path], fix.find)]).filter(([, n]) => n > 0);
    const total = hits.reduce((sum, [, n]) => sum + n, 0);
    if (total !== 1) {
      const already = paths.some(path => fix.target.test(path) && files[path].includes(fix.replace));
      throw new Error(already ? `Copy fix already present: ${fix.replace.slice(0, 60)}` : `Copy fix must match exactly once, found ${total}: ${fix.find.slice(0, 60)}`);
    }
    const [path] = hits[0];
    files[path] = files[path].replace(fix.find, () => fix.replace);
    changed.add(path);
  }
  for (const fix of COPY_PATTERN_FIXES) {
    const hits = paths.filter(path => fix.target.test(path)).map(path => [path, (files[path].match(fix.find) || []).length]).filter(([, n]) => n > 0);
    const total = hits.reduce((sum, [, n]) => sum + n, 0);
    if (total !== 1) throw new Error(`Copy pattern fix must match exactly once, found ${total}.`);
    const [path] = hits[0];
    files[path] = files[path].replace(fix.find, fix.replace);
    changed.add(path);
  }
  return [...changed].sort();
}

/** True when a published path may receive a copy fix. */
export function isCopyFixTarget(path) {
  return [...COPY_FIXES, ...COPY_PATTERN_FIXES].some(fix => fix.target.test(path));
}
