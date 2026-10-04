import './style.css';
import './review-navigation.css';
import './cg.css';

const labels = { maker: 'I · Maker', mechanic: 'II · Mechanic', builder: 'III · Advanced' };
const descriptions = {
  maker: 'Newly fabricated metal; dark, non-awakened optics.',
  mechanic: 'Inherited worn surfaces and distinct repairs; dark optics.',
  builder: 'Inherited surfaces with selective upgrades and restrained awakened orange optics.',
};
const asset = path => `./cg/${path}`;
const app = document.querySelector('#app');
app.innerHTML = `<a class="skip-link" href="#cg-controls">Skip to CG controls</a><div class="site-shell cg-shell">
<header class="topbar"><a class="wordmark" href="./"><span class="mark">M/B</span><span>MURDERBIRD<small>UNCAGED</small></span></a><nav aria-label="Main navigation"><a href="./">Interactive exhibit</a><a href="./folio.html">Story &amp; media folio</a><a href="#comparisons">Source comparisons</a><a href="#progress">Retained progress</a></nav><span class="edition">CG ASSESSMENT / LOOP 03</span></header>
<main><section class="cg-intro" aria-labelledby="cg-title"><p class="eyebrow">THE RETAINED CG CHARACTER</p><h1 id="cg-title">One inherited body.<br><em>Three eras in metal.</em></h1><p class="cg-lead">Inspect the latest retained CG candidate and compare it with the sources that control its appearance.</p><p class="cg-notice"><strong>Published for assessment. Source likeness and owner artistic acceptance remain pending.</strong> The retained work improves breast courses, local joins, toes and crown response. Head shape and enclosure gaps remain open.</p></section>
<section class="cg-assessment" aria-labelledby="candidate-title"><div class="cg-section-heading"><div><p class="eyebrow">LOOP 03 · RETAINED 04</p><h2 id="candidate-title">The current <em>candidate.</em></h2></div><p id="era-description">${descriptions.builder}</p></div>
<div id="cg-controls" class="cg-controls" tabindex="-1"><label for="cg-era">Era<select id="cg-era"><option value="maker">I · Maker</option><option value="mechanic">II · Mechanic</option><option value="builder" selected>III · Advanced</option></select></label><fieldset><legend>Lighting</legend><button type="button" data-light="neutral" aria-pressed="true">Neutral</button><button type="button" data-light="exhibit" aria-pressed="false">Exhibit</button></fieldset><button type="button" id="cg-load" class="cg-primary">Load interactive 3D · 75 MB</button><button type="button" id="cg-native" aria-pressed="true">Native render</button></div>
<div class="cg-viewer" id="cg-viewer" aria-busy="false"><div id="cg-webgl" hidden></div><img id="cg-fallback" src="${asset('retained04/builder/canon-neutral.png')}" alt="Advanced retained Loop 03 candidate, fixed native neutral render"><span class="cg-view-tag" id="cg-view-tag">FIXED NATIVE RENDER / ADVANCED</span></div>
<output id="cg-status" class="cg-status" aria-live="polite" aria-atomic="true">Fixed native render. Interactive 3D loads only when requested.</output>
<div class="cg-view-controls" role="group" aria-label="3D camera controls"><button type="button" id="cg-left" disabled>Orbit left</button><button type="button" id="cg-right" disabled>Orbit right</button><button type="button" id="cg-in" disabled>Zoom in</button><button type="button" id="cg-out" disabled>Zoom out</button><button type="button" id="cg-reset" disabled>Reset view</button></div>
<p class="cg-note">In 3D, drag to orbit and scroll or pinch to zoom. Keyboard: focus the model, use arrow keys, + / −, and R to reset. The native image is a fixed Blender render. Browser framing adapts to your screen; browser lighting and native workshop lighting differ, so their pixels are not equivalent.</p>
<nav class="cg-file-links" aria-label="Selected candidate files"><a id="cg-model-link" href="./cg/retained04/builder/murderbird-recursive-builder.glb">Selected static GLB</a><a id="cg-source-link" href="https://github.com/OKHP3/murderbird-uncaged/blob/e305989bff863aab827a0bdc4ee3395de32e0d61/assets/audit/cg-recursive-three-loop01/loop03/delivery/retained04/builder/murderbird-recursive-builder.blend">Editable native source ↗</a></nav>
<p class="cg-note">These static CG models contain no animation or mechanism rig. <a href="./">The V37 interactive exhibit</a> retains era movement, encounters, inspection and its illustrated fallback.</p></section>
<section class="cg-comparisons" id="comparisons" aria-labelledby="compare-title"><div class="cg-section-heading"><div><p class="eyebrow">SOURCE → BEFORE → CURRENT</p><h2 id="compare-title">Judge the <em>whole bird.</em></h2></div><p>Open an image for its original resolution.</p></div><div class="cg-card-grid" id="cg-comparison-cards"></div><p class="cg-note">The before and current native views use the fixed checkpoint09 camera and their saved neutral or workshop light rig. The original canon JPEG is unchanged. These comparisons preserve the visible differences; they do not establish likeness acceptance.</p></section>
<section class="cg-progress" id="progress" aria-labelledby="progress-title"><div class="cg-section-heading"><div><p class="eyebrow">RETAINED IN THE CURRENT MODEL</p><h2 id="progress-title">Small gains, <em>kept together.</em></h2></div></div><div class="cg-progress-grid" id="cg-progress-cards"></div></section>
<section class="cg-gallery" aria-labelledby="gallery-title"><div class="cg-section-heading"><div><p class="eyebrow">FIXED CAMERA RECORD</p><h2 id="gallery-title">Around the <em>candidate.</em></h2></div><label for="cg-gallery-view">View set<select id="cg-gallery-view"><option value="turntable">Eight angles</option><option value="details">Head, body &amp; feet</option></select></label></div><div class="cg-gallery-grid" id="cg-gallery-cards"></div><p class="cg-note" id="cg-gallery-note">Eight fixed views follow the selected lighting. Detail images retain their original saved lighting.</p></section>
<section class="cg-references" aria-labelledby="references-title"><div class="cg-section-heading"><div><p class="eyebrow">REFERENCE AUTHORITY</p><h2 id="references-title">Each source has <em>a scope.</em></h2></div></div><div class="cg-reference-grid">${card('Prior common body direction', 'references/candidate03.png', 'Candidate03 prior body direction with compact folded shield wings', 'Candidate03 records the prior common body and compact shield-wing direction. The owner-locked composite above controls full-bird canon.')}${card('July · head identity only', 'references/july-head.png', 'July head identity reference; its body and long hanging wings are excluded', 'Deep hooked bill, swept crown, recessed optic and cheek opening. The July body and long hanging wings are excluded.')}</div><p class="cg-note"><a href="./folio.html#motion-sound">First Choice video and theme in the folio</a> · The pinned video informs surface continuity and screen presence. <a href="https://github.com/OKHP3/murderbird-uncaged/blob/e305989bff863aab827a0bdc4ee3395de32e0d61/assets/audit/cg-recursive-three-loop01/loop03/final-adjudication.json">Source review record ↗</a> · <a href="https://github.com/OKHP3/murderbird-uncaged/issues/14">Cross-system review ↗</a></p></section>
</main><footer><span>© Jamie Hill / OverKill Hill P³ · MurderBird creative content: all rights reserved.</span><span>ASSESSMENT CANDIDATE · ARTISTIC ACCEPTANCE PENDING</span></footer></div>`;

function card(title, path, alt, note = '', lazy = true) {
  const url = asset(path);
  return `<figure class="cg-card"><figcaption><strong>${title}</strong></figcaption><a href="${url}" aria-label="Open ${title} at original resolution"><img src="${url}" alt="${alt}" ${lazy ? 'loading="lazy"' : ''} decoding="async"></a><p class="cg-image-state" aria-live="polite"></p>${note ? `<p class="cg-card-note">${note}</p>` : ''}</figure>`;
}
const $ = id => document.getElementById(id);
const era = $('cg-era'), status = $('cg-status'), host = $('cg-webgl'), fallback = $('cg-fallback');
let lighting = 'neutral', viewer = null, request = null, generation = 0, loading = false, preferNative = true, failed = false;
const profile = () => lighting === 'exhibit' ? 'workshop' : 'neutral';
// Rounded decimal download sizes from the three pinned manifest byte counts.
const modelMB = { builder: Math.ceil(74983972 / 1e6), maker: Math.ceil(63979404 / 1e6), mechanic: Math.ceil(76271784 / 1e6) };
function registerImages(root) {
  for (const img of root.querySelectorAll('.cg-card img')) {
    const message = img.closest('figure').querySelector('.cg-image-state');
    const describe = () => { message.textContent = img.complete && !img.naturalWidth ? 'This exact image is unavailable.' : ''; };
    img.addEventListener('error', describe); img.addEventListener('load', describe); describe();
  }
}
function renderComparisons() {
  const name = labels[era.value], mode = profile();
  $('cg-comparison-cards').innerHTML = [
    card('Locked Sept22 · full-bird canon', 'references/locked-canon.jpg', 'Owner-locked September22 full-bird canon composite', 'Controls common full-bird likeness across all three eras. Original source pixels remain unchanged.'),
    card(`${name} · era finish source`, `references/${era.value}.png`, `Pinned ${name} finish reference`, 'Controls this era’s finish, alongside the locked full-bird canon.'),
    card('Checkpoint09 · before', `checkpoint09/${era.value}/canon-${mode}.png`, `${name} checkpoint09 matched baseline, fixed ${mode} native view`, 'Matched receiving baseline before the three retained loops.'),
    card('Loop03 · retained current', `retained04/${era.value}/canon-${mode}.png`, `${name} retained Loop03, fixed ${mode} native view`, 'Cumulative breast, join, toe and crown changes. Head shape and enclosure gaps remain open.'),
  ].join('');
  $('cg-progress-cards').innerHTML = [
    card('01 · Shorter breast courses', `loop01/${era.value}/canon-${mode}.png`, `${name} retained Loop01, fixed ${mode} native view`, 'Shorter breast courses retained. Receiving head and finish held.'),
    card('02 · Underlaps, joints & toes', `loop02/${era.value}/canon-${mode}.png`, `${name} retained Loop02, fixed ${mode} native view`, 'Three breast underlaps and articulated toe/joint successors retained. Progress remains modest.'),
    card('03 · Crown colour response', `retained04/${era.value}/canon-${mode}.png`, `${name} retained Loop03, fixed ${mode} native view`, 'Cooler crown colour/roughness response with the original normal texture; earlier gains preserved.'),
  ].join('');
  registerImages($('cg-comparison-cards')); registerImages($('cg-progress-cards')); renderGallery();
}
function renderGallery() {
  const details = $('cg-gallery-view').value === 'details';
  const views = details ? [['head-neck', 'Head & neck'], ['body-detail', 'Body detail'], ['feet-detail', 'Feet detail'], ['side-profile', 'Side profile'], ['hero', 'Exhibit hero']] : Array.from({ length: 8 }, (_, index) => [`${profile()}-${String(index * 45).padStart(3, '0')}`, `${index * 45}°`]);
  $('cg-gallery-cards').innerHTML = views.map(([file, label]) => card(label, `retained04/${era.value}/${file}.png`, `${labels[era.value]} retained candidate ${label}, fixed native render`)).join('');
  registerImages($('cg-gallery-cards'));
}
function display() {
  const native = preferNative || !viewer;
  fallback.hidden = !native; host.hidden = native;
  $('cg-native').setAttribute('aria-pressed', String(native));
  $('cg-viewer').setAttribute('aria-busy', String(loading));
  $('cg-view-tag').textContent = `${native ? 'FIXED NATIVE RENDER' : 'STATIC 3D CANDIDATE'} / ${labels[era.value]}`;
  $('cg-load').disabled = loading;
  $('cg-load').textContent = loading ? 'Loading interactive 3D…' : viewer ? 'Show interactive 3D' : `${failed ? 'Retry' : 'Load'} interactive 3D · ${modelMB[era.value]} MB`;
  for (const id of ['cg-left', 'cg-right', 'cg-in', 'cg-out', 'cg-reset']) $(id).disabled = !viewer || native;
}
function showStatus() {
  status.textContent = preferNative || !viewer ? `${labels[era.value]} · ${fallback.complete && !fallback.naturalWidth ? 'exact native render unavailable' : 'fixed native ' + profile() + ' render'}. ${viewer ? 'The loaded 3D view is available.' : failed ? '3D is unavailable; use Retry to reload.' : 'Interactive 3D loads only when requested.'}` : `${labels[era.value]} · static 3D candidate · ${lighting} lighting. Source likeness and owner acceptance pending.`;
}
function updateFiles() {
  fallback.src = asset(`retained04/${era.value}/canon-${profile()}.png`);
  fallback.alt = `${labels[era.value]} retained candidate, fixed native ${profile()} render`;
  $('era-description').textContent = descriptions[era.value];
  $('cg-model-link').href = asset(`retained04/${era.value}/murderbird-recursive-${era.value}.glb`);
  $('cg-source-link').href = `https://github.com/OKHP3/murderbird-uncaged/blob/e305989bff863aab827a0bdc4ee3395de32e0d61/assets/audit/cg-recursive-three-loop01/loop03/delivery/retained04/${era.value}/murderbird-recursive-${era.value}.blend`;
  renderComparisons(); display();
}
function unload() { generation++; request?.abort(); request = null; viewer?.dispose(); viewer = null; loading = false; }
async function load() {
  if (viewer) { preferNative = false; display(); showStatus(); return; }
  unload(); const current = generation, selected = era.value; request = new AbortController();
  const signal = request.signal; loading = true; failed = false; preferNative = true; display();
  status.textContent = `Loading ${labels[selected]} static 3D candidate… Native views remain available.`;
  try {
    const { createCGViewer } = await import('./scene/cg-viewer.js'); if (current !== generation) return;
    // Keep the host measurable while the native image covers the loading canvas.
    host.hidden = false; host.style.visibility = 'hidden';
    const loaded = await createCGViewer(host, asset(`retained04/${selected}/murderbird-recursive-${selected}.glb`), {
      lighting, signal,
      onProgress: percent => { if (current === generation) status.textContent = `${labels[selected]} · downloading static 3D model ${percent}%…`; },
      onContextLost: () => { unload(); failed = true; preferNative = true; host.style.visibility = ''; display(); status.textContent = '3D graphics context was lost. The exact native render remains available; retry to reload 3D.'; },
    });
    if (current !== generation) { loaded.dispose(); return; }
    loaded.setLighting(lighting);
    viewer = loaded; host.style.visibility = ''; loading = false; preferNative = false; display(); showStatus();
  } catch (error) {
    if (current !== generation) return;
    host.style.visibility = ''; loading = false; failed = true; preferNative = true; display();
    status.textContent = `3D is unavailable: ${error.message}. The exact native render and source comparisons remain available. Use Retry to try again.`;
  }
}
era.addEventListener('change', () => { unload(); failed = false; preferNative = true; updateFiles(); showStatus(); });
for (const button of document.querySelectorAll('[data-light]')) button.addEventListener('click', () => {
  lighting = button.dataset.light; viewer?.setLighting(lighting);
  for (const light of document.querySelectorAll('[data-light]')) light.setAttribute('aria-pressed', String(light === button));
  updateFiles(); if (!loading) showStatus();
});
$('cg-load').addEventListener('click', load);
$('cg-native').addEventListener('click', () => { preferNative = true; display(); if (!loading) showStatus(); });
for (const [id, action] of [['cg-left', () => viewer.orbit(.2)], ['cg-right', () => viewer.orbit(-.2)], ['cg-in', () => viewer.zoom(1.2)], ['cg-out', () => viewer.zoom(1 / 1.2)], ['cg-reset', () => { viewer.resetView(); status.textContent = `${labels[era.value]} · 3D view reset.`; }]]) $(id).addEventListener('click', action);
$('cg-gallery-view').addEventListener('change', renderGallery);
fallback.addEventListener('error', () => { status.textContent = 'The exact native render is unavailable. Source comparisons and the Retry 3D control remain available.'; });
window.addEventListener('pagehide', unload);
window.addEventListener('pageshow', () => { preferNative = true; display(); showStatus(); });
registerImages(app); updateFiles(); showStatus();
