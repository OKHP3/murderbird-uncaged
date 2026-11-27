/**
 * Allowlisted base-file patches for the Living Plates overlay.
 *
 * The overlay republishes the live base release unchanged except for these three files,
 * which gain a route to Living Plates. Each patch inserts fixed text after one exact anchor.
 * A missing or repeated anchor, or text that is already present, stops the publication.
 */

const SITE = 'https://okhp3.github.io/murderbird-uncaged';

// Runs after the deployed module script renders its navigation. It appends one link to the
// existing "Main navigation" and restores it if the application re-renders the header. If no
// navigation appears, it adds a small fixed link so the route is never missing.
const NAV_SCRIPT = `    <script data-plates-navigation>
      (function () {
        function addToNav() {
          var nav = document.querySelector('nav[aria-label="Main navigation"]');
          if (!nav) return false;
          if (!nav.querySelector('a[href="./plates/"]')) {
            var link = document.createElement('a');
            link.href = './plates/';
            link.textContent = 'Living Plates';
            nav.appendChild(link);
          }
          return true;
        }
        function addFallback() {
          if (document.querySelector('a[href="./plates/"]')) return;
          var link = document.createElement('a');
          link.href = './plates/';
          link.textContent = 'Living Plates';
          link.setAttribute('style', 'position:fixed;left:12px;bottom:12px;z-index:2147483000;padding:6px 10px;background:#171a17;color:#e8dcc8;border:1px solid #a76a46;border-radius:4px;font:14px/1.3 system-ui,sans-serif;text-decoration:underline');
          document.body.appendChild(link);
        }
        var found = addToNav();
        var app = document.getElementById('app');
        if (app && window.MutationObserver) {
          new MutationObserver(function () { if (addToNav()) found = true; }).observe(app, {childList: true, subtree: true});
        }
        setTimeout(function () { if (!found && !addToNav()) addFallback(); }, 6000);
      })();
    </script>
`;

const SITEMAP_CG = `  <url>
    <loc>${SITE}/cg.html</loc>
  </url>
`;
const SITEMAP_ADDITION = `  <url>
    <loc>${SITE}/folio.html</loc>
  </url>
  <url>
    <loc>${SITE}/plates/</loc>
  </url>
`;

const APP_ANCHOR = '    <div id="app"></div>\n';

export const BASE_PATCHES = Object.freeze({
  'index.html': {anchor: APP_ANCHOR, insert: NAV_SCRIPT, marker: 'data-plates-navigation'},
  'folio.html': {anchor: APP_ANCHOR, insert: NAV_SCRIPT, marker: 'data-plates-navigation'},
  'sitemap.xml': {anchor: SITEMAP_CG, insert: SITEMAP_ADDITION, marker: `${SITE}/plates/`},
});

function occurrences(text, needle) {
  let count = 0;
  for (let at = text.indexOf(needle); at !== -1; at = text.indexOf(needle, at + needle.length)) count += 1;
  return count;
}

/** Returns the patched text for an allowlisted path. Throws unless the anchor occurs exactly once. */
export function applyBasePatch(path, text) {
  const patch = BASE_PATCHES[path];
  if (!patch) throw new Error(`No overlay patch is allowlisted for ${path}`);
  if (text.includes(patch.marker)) throw new Error(`${path} already contains the Living Plates route; the base release has changed.`);
  const count = occurrences(text, patch.anchor);
  if (count !== 1) throw new Error(`${path}: expected the patch anchor exactly once, found ${count}.`);
  const at = text.indexOf(patch.anchor) + patch.anchor.length;
  return text.slice(0, at) + patch.insert + text.slice(at);
}

/**
 * Undoes applyBasePatch on a file an earlier overlay already published, so a later overlay can
 * rebuild from the verified base. Throws unless the inserted text follows its anchor exactly once.
 * The caller must still verify the result against the base release record.
 */
export function revertBasePatch(path, text) {
  const patch = BASE_PATCHES[path];
  if (!patch) throw new Error(`No overlay patch is allowlisted for ${path}`);
  const patched = patch.anchor + patch.insert;
  const count = occurrences(text, patched);
  if (count !== 1) throw new Error(`${path}: expected the earlier overlay patch exactly once, found ${count}.`);
  const at = text.indexOf(patched) + patch.anchor.length;
  return text.slice(0, at) + text.slice(at + patch.insert.length);
}
