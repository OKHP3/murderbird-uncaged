import './style.css';
import './fallback.css';
import { createExhibit } from './scene/exhibit.js';
import { createIllustratedExhibit } from './scene/fallback.js';
import { createSoundscape } from './audio/soundscape.js';

const specimens = [
  {
    id: 'beak', number: '01', name: 'Hammered beak', era: 'I · THE MAKER',
    title: 'Built to break, built by hand.',
    description: 'The bronze beak bears the marks of its first maker. Its overlapping plates suggest a tool assembled piece by piece, rather than a creature born whole.',
    observation: 'Look for the segmented bronze at the front of the skull.',
    sound: 'metal',
  },
  {
    id: 'joint', number: '02', name: 'Joint assembly', era: 'II · THE MECHANIC',
    title: 'Motion, repaired.',
    description: 'The leg joints expose bearing surfaces and restoration-era repair. These mechanisms translate the weight of the body into a deliberate, uneasy stance.',
    observation: 'Inspect the rings and pins above the talons.',
    sound: 'click',
  },
  {
    id: 'core', number: '03', name: 'Ceramic power core', era: 'III · THE BUILDER',
    title: 'Something under the armor.',
    description: 'Behind the breastplate sits a sealed ceramic core and processing lattice. Open the chest to study the part that changed the bird from mechanism to possibility.',
    observation: 'Use the section-view control to expose the cavity.',
    sound: 'pulse',
  },
  {
    id: 'eye', number: '04', name: 'The eye', era: 'III · THE BUILDER',
    title: 'The moment it chooses.',
    description: 'Its eye is not just a sensor. In the story of the MurderBird, this is where observation becomes decision—the first sign that the cage is no longer in control.',
    observation: 'The lens follows the exhibit light, even when the body is still.',
    sound: 'chirp',
  },
];

const app = document.querySelector('#app');
app.innerHTML = `
  <div class="site-shell">
    <header class="topbar">
      <a class="wordmark" href="#top" aria-label="MurderBird Uncaged home"><span class="mark">M<span class="mark-slash">/</span>B</span><span class="wordmark-text">MURDERBIRD <small>UNCAGED</small></span></a>
      <nav aria-label="Main navigation"><a href="#specimen">The specimen</a><a href="#field-notes">Field notes</a><a class="nav-story" href="https://overkillhill.com/writings/murderbird/" target="_blank" rel="noopener noreferrer">Read the origin ↗</a></nav>
    </header>

    <main id="top">
      <section class="intro">
        <div class="intro-copy"><p class="eyebrow"><span class="eyebrow-line"></span> AN INTERACTIVE FIELD EXHIBIT <span class="edition">/ 001</span></p>
          <h1>Meet the thing<br><em>that learned</em><br>to choose.</h1>
          <p class="intro-sub">Part artifact. Part animal. Entirely unexpected. Turn the MurderBird, inspect its construction, and follow the three eras that brought it to life.</p>
          <a class="text-link" href="#specimen">ENTER THE EXHIBIT <span>↓</span></a>
        </div>
        <div class="intro-index"><span>THE MURDERBIRD</span><span>SPECIMEN NO. 001</span><span>ANATOMY OF AN IMPOSSIBILITY</span></div>
      </section>

      <section id="specimen" class="exhibit" aria-labelledby="exhibit-title">
        <div class="exhibit-heading"><div><p class="eyebrow">THE SPECIMEN / INTERACTIVE STUDY</p><h2 id="exhibit-title">A creature in parts.</h2></div><p>DRAG TO ROTATE &nbsp;·&nbsp; SCROLL TO ZOOM<br>SELECT A MARKER TO INSPECT</p></div>
        <div class="exhibit-grid">
          <div class="viewer-column">
            <div class="viewer" id="viewer">
              <div class="viewer-top"><span><i class="status-dot"></i> SPECIMEN ACTIVE</span><span>MB–001 / MODEL STUDY</span></div>
              <div id="scene" aria-label="Interactive 3D model of the MurderBird"></div>
              <div id="hotspots" class="hotspots"></div>
              <div class="viewer-corner tl"></div><div class="viewer-corner tr"></div><div class="viewer-corner bl"></div><div class="viewer-corner br"></div>
              <div class="viewer-bottom"><span>FIG. 01 / CONSTRUCTION STUDY</span><span id="view-label">EXTERIOR VIEW</span></div>
            </div>
            <div class="toolbar" aria-label="Exhibit controls">
              <button id="section-toggle" class="control primary" type="button" aria-pressed="false"><span class="control-icon">◫</span> OPEN SECTION VIEW <span class="control-arrow">↗</span></button>
              <button id="reset-view" class="control" type="button" title="Reset 3D view"><span class="control-icon">⟲</span> RESET VIEW</button>
              <button id="sound-toggle" class="control" type="button" aria-pressed="false"><span class="control-icon">♫</span> SOUND OFF</button>
            </div>
            <p class="viewer-note">This is a procedural study model and synthesized soundscape. Final model, song, stills, and video have not been supplied.</p>
          </div>
          <aside class="inspector" aria-label="Specimen details">
            <div class="inspector-header"><span>ANATOMY INDEX</span><span>01 — 04</span></div>
            <div class="part-list" id="part-list"></div>
            <div id="detail" class="detail" aria-live="polite"></div>
            <div class="inspector-foot"><span>THREE ERAS. ONE IMPOSSIBLE BIRD.</span><span>↘</span></div>
          </aside>
        </div>
      </section>

      <section class="timeline" id="field-notes" aria-labelledby="timeline-title">
        <div class="section-kicker"><span>FIELD NOTES</span><span>THE CONSTRUCTION RECORD / 01—03</span></div>
        <h2 id="timeline-title">Not born. <em>Built.</em></h2>
        <div class="eras">
          <article><span class="era-number">I / THE MAKER</span><div class="era-symbol">✳</div><h3>Forged</h3><p>Bronze, heat, and a maker’s hand. The earliest form was an object with a purpose.</p></article>
          <article><span class="era-number">II / THE MECHANIC</span><div class="era-symbol">◎</div><h3>Repaired</h3><p>Bearings and joints brought motion back to a body that had learned to wear down.</p></article>
          <article><span class="era-number">III / THE BUILDER</span><div class="era-symbol">✺</div><h3>Awakened</h3><p>A sealed core and a new kind of processing. The first choice belonged to the bird.</p></article>
        </div>
      </section>
      <section class="closing"><p class="eyebrow">THE STORY BEHIND THE SPECIMEN</p><h2>Every machine<br>has a <em>maker.</em></h2><a href="https://overkillhill.com/writings/murderbird/" target="_blank" rel="noopener noreferrer">READ THE ORIGIN STORY <span>↗</span></a></section>
    </main>
    <footer><span>© MURDERBIRD: UNCAGED</span><span>AN INTERACTIVE CONSTRUCTION STUDY</span><a href="#top">BACK TO TOP ↑</a></footer>
  </div>`;

const sceneElement = document.querySelector('#scene');
const viewerElement = document.querySelector('#viewer');
const hotspotLayer = document.querySelector('#hotspots');
const partList = document.querySelector('#part-list');
const detail = document.querySelector('#detail');
const sound = createSoundscape();
let selected = 'beak';
let sectionOpen = false;
let interactionCount = 0;

function trackEvent(name, parameters = {}) {
  if (typeof window.gtag === 'function') window.gtag('event', name, parameters);
}

const updateMarker = (id, x, y, visible) => {
  const marker = hotspotLayer.querySelector(`[data-marker="${id}"]`);
  if (!marker) return;
  marker.style.left = `${x}px`;
  marker.style.top = `${y}px`;
  marker.hidden = !visible;
};
const probe = document.createElement('canvas');
const hasWebGL = Boolean(probe.getContext('webgl2') || probe.getContext('webgl'));
let exhibit;
if (hasWebGL) {
  try {
    exhibit = createExhibit(sceneElement, updateMarker);
  } catch (error) {
    console.warn('3D renderer unavailable; switching to illustrated exhibit.', error);
    sceneElement.replaceChildren();
  }
}
if (!exhibit) {
  exhibit = createIllustratedExhibit(sceneElement, updateMarker);
  document.querySelector('.viewer-note').textContent = 'Illustrated interactive view shown because WebGL is unavailable here. The procedural 3D model runs in browsers with WebGL support; final media has not been supplied.';
}

function renderSelection(id, play = true) {
  selected = id;
  const item = specimens.find(part => part.id === id);
  partList.querySelectorAll('button').forEach(button => {
    const active = button.dataset.part === id;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
  hotspotLayer.querySelectorAll('button').forEach(button => button.classList.toggle('active', button.dataset.marker === id));
  detail.innerHTML = `<p class="detail-era">${item.era}</p><h3>${item.title}</h3><p>${item.description}</p><div class="observation"><span>OBSERVATION NOTE</span>${item.observation}</div>`;
  exhibit.select(id);
  if (play) {
    sound.effect(item.sound);
    interactionCount++;
    trackEvent('select_specimen', { specimen_id: item.id });
    if (interactionCount === 7) exhibit.react();
  }
}

partList.innerHTML = specimens.map(item => `<button type="button" data-part="${item.id}" aria-pressed="false"><span class="part-number">${item.number}</span><span>${item.name}</span><span class="part-arrow">↗</span></button>`).join('');
hotspotLayer.innerHTML = specimens.map(item => `<button class="marker" type="button" data-marker="${item.id}" aria-label="Inspect ${item.name}"><span>${item.number}</span></button>`).join('');
exhibit.resize();
partList.addEventListener('click', event => {
  const button = event.target.closest('[data-part]');
  if (button) renderSelection(button.dataset.part);
});
hotspotLayer.addEventListener('click', event => {
  const button = event.target.closest('[data-marker]');
  if (button) renderSelection(button.dataset.marker);
});
document.querySelector('#section-toggle').addEventListener('click', event => {
  sectionOpen = !sectionOpen;
  exhibit.setSection(sectionOpen);
  sound.effect(sectionOpen ? 'open' : 'click');
  trackEvent('section_view_toggle', { is_open: sectionOpen });
  event.currentTarget.setAttribute('aria-pressed', String(sectionOpen));
  event.currentTarget.innerHTML = `<span class="control-icon">◫</span> ${sectionOpen ? 'CLOSE SECTION VIEW' : 'OPEN SECTION VIEW'} <span class="control-arrow">↗</span>`;
  document.querySelector('#view-label').textContent = sectionOpen ? 'SECTION VIEW / CORE EXPOSED' : 'EXTERIOR VIEW';
  if (sectionOpen) renderSelection('core');
});
document.querySelector('#reset-view').addEventListener('click', () => {
  exhibit.reset();
  sound.effect('click');
  trackEvent('view_reset');
});
document.querySelector('#sound-toggle').addEventListener('click', async event => {
  const enabled = await sound.toggle();
  trackEvent('sound_toggle', { is_enabled: enabled });
  event.currentTarget.setAttribute('aria-pressed', String(enabled));
  event.currentTarget.innerHTML = `<span class="control-icon">♫</span> SOUND ${enabled ? 'ON' : 'OFF'}`;
});
renderSelection('beak', false);
new ResizeObserver(() => exhibit.resize()).observe(viewerElement);