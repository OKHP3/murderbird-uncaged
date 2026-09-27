import './style.css';
import './fallback.css';
import './media.css';
import { createIllustratedExhibit } from './scene/fallback.js';
import { createSoundscape } from './audio/soundscape.js';
import {
  chapterStills,
  ironVerdictTrack,
  murderBirdHero,
  firstChoicePilot,
} from './media.js';

const specimens = [
  {
    id: 'beak', number: '01', name: 'Hammered beak', era: 'I · THE MAKER',
    title: 'Built to break, built by hand.',
    description: 'The deep hooked bill and hand-worked bronze belong to the Bird’s earliest, deliberately made body. The story leaves the original mechanism unresolved.',
    observation: 'Look for the hooked profile and irregularly fitted plates.',
    sound: 'metal',
  },
  {
    id: 'joint', number: '02', name: 'Joint assembly', era: 'II · THE MECHANIC',
    title: 'Motion, repaired.',
    description: 'Industrial braces and bearings mark later repair. The Bird remains a floor-supported, flightless body; the ordinary workbench and CRT do not carry its weight.',
    observation: 'Inspect the reinforced joints above the planted talons.',
    sound: 'click',
  },
  {
    id: 'core', number: '03', name: 'Ceramic power core', era: 'III · THE BUILDER',
    title: 'Power is not a mind.',
    description: 'The modern Builder adds finite onboard energy and processing as separate systems. This exploratory section view is a power inspection, not a glowing reactor or proof of a completed mind.',
    observation: 'Open the Builder-era inspection to see a simplified, non-glowing study.',
    sound: 'pulse',
  },
  {
    id: 'eye', number: '04', name: 'The eye', era: 'III · THE BUILDER',
    title: 'One modern optic.',
    description: 'The circular amber optic belongs to the modern Builder-era study only. The inert Water stage and industrial Mechanic stage keep their eyes dark.',
    observation: 'This geometry does not animate an eye or represent a finished character rig.',
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
          <p class="intro-sub">In this fictional field exhibit, meet a floor-standing, flightless terrorbird: deep hooked bill, segmented crown, compact folded wings, and legs built to carry its weight. Follow its history without mistaking a study model for a finished rig.</p>
          <a class="text-link" href="#specimen">ENTER THE EXHIBIT <span>↓</span></a>
        </div>
        <figure class="intro-art">
          <img src="${murderBirdHero.src}" srcset="${murderBirdHero.srcset}" sizes="(max-width: 760px) 100vw, 52vw" alt="${murderBirdHero.alt}" fetchpriority="high" decoding="async">
          <figcaption><span>COMMON SILHOUETTE / MASTER STILL</span><span>Floor-supported · local preview</span></figcaption>
        </figure>
      </section>

      <section id="specimen" class="exhibit" aria-labelledby="exhibit-title">
        <div class="exhibit-heading"><div><p class="eyebrow">THE SPECIMEN / INTERACTIVE STUDY</p><h2 id="exhibit-title">A study—not the Bird.</h2></div><p>DRAG TO ROTATE &nbsp;·&nbsp; SCROLL TO ZOOM<br>SELECT A MARKER TO INSPECT</p></div>
        <div class="exhibit-grid">
          <div class="viewer-column">
            <div class="viewer" id="viewer">
              <div class="viewer-top"><span><i class="status-dot"></i> EXPLORATORY GEOMETRY</span><span>BUILDER ERA / DRAFT</span></div>
              <div id="scene" aria-label="Interactive procedural geometry study, not a finished MurderBird model"></div>
              <div id="hotspots" class="hotspots"></div>
              <div class="viewer-corner tl"></div><div class="viewer-corner tr"></div><div class="viewer-corner bl"></div><div class="viewer-corner br"></div>
              <div class="viewer-bottom"><span>NOT A CHARACTER RIG</span><span id="view-label">EXTERIOR VIEW</span></div>
            </div>
            <div class="toolbar" aria-label="Exhibit controls">
              <button id="section-toggle" class="control primary" type="button" aria-pressed="false"><span class="control-icon">◫</span> OPEN POWER INSPECTION <span class="control-arrow">↗</span></button>
              <button id="reset-view" class="control" type="button" title="Reset 3D view"><span class="control-icon">⟲</span> RESET VIEW</button>
              <button id="sound-toggle" class="control" type="button" aria-pressed="false"><span class="control-icon">♫</span> SOUNDSCAPE OFF</button>
            </div>
            <p class="viewer-note">This procedural geometry is an interaction sketch for the Builder stage, not a finished MurderBird model or rig. Scoped story stills and motion studies below provide local-preview visual references; listen to Iron Verdict in the player below.</p>
          </div>
          <aside class="inspector" aria-label="Specimen details">
            <div class="inspector-header"><span>STUDY INDEX</span><span>01 — 04</span></div>
            <div class="part-list" id="part-list"></div>
            <div id="detail" class="detail" aria-live="polite"></div>
            <div class="inspector-foot"><span>FICTIONAL HISTORY / WORKING STUDY</span><span>↘</span></div>
          </aside>
        </div>
      </section>

      <section class="timeline" id="field-notes" aria-labelledby="timeline-title">
        <div class="section-kicker"><span>FIELD NOTES</span><span>THE CONSTRUCTION RECORD / 01—03</span></div>
        <h2 id="timeline-title">Not born. <em>Built.</em></h2>
        <div class="eras">
          <article><span class="era-number">I / THE MAKER</span><div class="era-symbol">✳</div><h3>Hand-worked</h3><p>Bronze, peened pins, and an eagle commission shaped into a formidable terrestrial body. Its earliest mechanism remains a story mystery.</p></article>
          <article><span class="era-number">II / THE MECHANIC</span><div class="era-symbol">◎</div><h3>Repaired</h3><p>Industrial braces and bearings accumulate around the old body. Its weight stays on the floor or a credible assembly cradle.</p></article>
          <article><span class="era-number">III / THE BUILDER</span><div class="era-symbol">✺</div><h3>Power / processing</h3><p>Modern energy and processing are distinct additions. The Heart still is a power inspection—not a completed mind.</p></article>
        </div>
      </section>
      <section class="media-atlas" id="media-record" aria-labelledby="media-title">
        <div class="section-kicker"><span>SCOPED STORY STILLS</span><span>LOCAL PREVIEW / NOT RELEASE APPROVAL</span></div>
        <h2 id="media-title">Material, time, <em>repair.</em></h2>
        <p class="media-intro">These supplied images are reviewed for specific fictional story beats. They establish silhouette, material, and setting; they do not certify a finished model, exact anatomy, or hidden mechanism.</p>
        <div class="still-grid">
          ${chapterStills.map(still => `
            <figure class="still-card">
              <img src="${still.src}" alt="${still.alt}" loading="lazy" decoding="async">
              <figcaption><span class="still-era">${still.era}</span><strong>${still.title}</strong><span>${still.note}</span></figcaption>
            </figure>`).join('')}
        </div>
      </section>
      <section class="media-playback" id="motion-sound" aria-labelledby="playback-title">
        <div class="section-kicker"><span>OPTIONAL MEDIA</span><span>VISITOR-STARTED / NO AUTOPLAY</span></div>
        <h2 id="playback-title">Motion and <em>sound.</em></h2>
        <div class="playback-grid">
          <article class="playback-card">
            <p class="playback-kicker">CONTROLLED PILOT 03 / 8 SECONDS</p>
            <h3>First choice</h3>
            <video id="first-choice-video" controls playsinline preload="none" poster="${firstChoicePilot.poster}" aria-describedby="pilot-description">
              <source src="${firstChoicePilot.src}" type="video/mp4">
              <p>Your browser does not support this video. <a href="${firstChoicePilot.src}">Open the silent pilot file</a>.</p>
            </video>
            <p id="pilot-description" class="playback-description">Silent controlled motion study: the Bird shifts on its supported saddle and inspects the work while both feet, the floor, the CRT, and the stand remain fixed. It is a short 2D review clip, not a reconstructed 3D mechanism or a longer film. There is no audio track, dialogue, or implied sound.</p>
          </article>
          <article class="playback-card">
            <p class="playback-kicker">IRON VERDICT / INSTRUMENTAL DEMO</p>
            <h3>Visitor-controlled theme</h3>
            <audio id="iron-verdict-audio" controls preload="none" aria-label="Iron Verdict original programmed instrumental demo, without vocals">
              <source src="${ironVerdictTrack}" type="audio/mpeg">
              <a href="${ironVerdictTrack}">Open the Iron Verdict MP3</a>
            </audio>
            <p class="playback-description">An original programmed instrumental demo, not a live performance or a finished vocal recording. No singer has been recorded. A separate notated lyric/performance guide exists, but these lyrics are not sung in this track.</p>
          </article>
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
let soundscapeEnabled = false;

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
    const { createExhibit } = await import('./scene/exhibit.js');
    exhibit = createExhibit(sceneElement, updateMarker);
  } catch (error) {
    console.warn('3D renderer unavailable; switching to illustrated exhibit.', error);
    sceneElement.replaceChildren();
  }
}
if (!exhibit) {
  exhibit = createIllustratedExhibit(sceneElement, updateMarker);
  viewerElement.classList.add('fallback-active');
  document.querySelector('.viewer-top span:first-child').innerHTML = '<i class="status-dot"></i> SCOPED STORY ART';
  document.querySelector('.viewer-top span:last-child').textContent = 'LOCAL PREVIEW';
  document.querySelector('.exhibit-heading > p').textContent = 'SELECT A STUDY INDEX TO VIEW ITS SCOPED STILL';
  document.querySelector('#reset-view').hidden = true;
  document.querySelector('.viewer-note').textContent = 'Illustrated story art is shown because WebGL is unavailable here. Select a study index to view its scoped still. This is local-preview artwork, not final release art. The interactive 3D model requires WebGL; listen to Iron Verdict using the player below.';
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
    trackEvent('select_specimen', { specimen_id: item.id });
  }
}

partList.innerHTML = specimens.map(item => `<button type="button" data-part="${item.id}" aria-pressed="false"><span class="part-number">${item.number}</span><span>${item.name}</span><span class="part-arrow">↗</span></button>`).join('');
hotspotLayer.innerHTML = specimens.map(item => `<button class="marker" type="button" data-marker="${item.id}" aria-label="Inspect ${item.name}"${exhibit.supportsMarkers ? '' : ' hidden'}><span>${item.number}</span></button>`).join('');
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
  event.currentTarget.innerHTML = `<span class="control-icon">◫</span> ${sectionOpen ? 'CLOSE POWER INSPECTION' : 'OPEN POWER INSPECTION'} <span class="control-arrow">↗</span>`;
  document.querySelector('#view-label').textContent = sectionOpen ? 'POWER INSPECTION' : 'EXTERIOR VIEW';
  if (sectionOpen) renderSelection('core');
});
document.querySelector('#reset-view').addEventListener('click', () => {
  exhibit.reset();
  sound.effect('click');
  trackEvent('view_reset');
});
const soundButton = document.querySelector('#sound-toggle');
const mediaPlayers = [
  document.querySelector('#iron-verdict-audio'),
  document.querySelector('#garageband-audio'),
  document.querySelector('#first-choice-video'),
].filter(Boolean);
let themePlayer;

function syncSoundscapeButton() {
  soundButton.setAttribute('aria-pressed', String(soundscapeEnabled));
  soundButton.innerHTML = `<span class="control-icon">♫</span> SOUNDSCAPE ${soundscapeEnabled ? 'ON' : 'OFF'}`;
}

function stopSoundscape() {
  if (!soundscapeEnabled) return;
  soundscapeEnabled = sound.stop();
  syncSoundscapeButton();
}

function stopOtherMedia(currentMedia, stopTheme = true) {
  mediaPlayers.forEach(player => {
    if (player !== currentMedia) player.pause();
  });
  if (stopTheme) themePlayer?.pause();
  stopSoundscape();
}

mediaPlayers.forEach(player => {
  player.addEventListener('play', () => stopOtherMedia(player));
});

soundButton.addEventListener('click', async event => {
  const button = event.currentTarget;
  button.disabled = true;
  try {
    if (!soundscapeEnabled) stopOtherMedia(null);
    soundscapeEnabled = await sound.toggle();
    trackEvent('sound_toggle', { is_enabled: soundscapeEnabled });
    syncSoundscapeButton();
  } catch {
    soundscapeEnabled = sound.stop();
    button.setAttribute('aria-pressed', 'false');
    button.textContent = 'SOUNDSCAPE UNAVAILABLE';
  } finally {
    button.disabled = false;
  }
});

const { mountThemePlayer } = await import('./audio/theme-player.js');
themePlayer = mountThemePlayer(document.querySelector('.viewer-column'), sound, {
  onStart() {
    stopOtherMedia(null, false);
  },
});
renderSelection('beak', false);
new ResizeObserver(() => exhibit.resize()).observe(viewerElement);
