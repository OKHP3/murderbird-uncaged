import './folio-style.css';
import './folio-fallback.css';
import './media.css';
import './folio.css';
import './review-navigation.css';
import { createIllustratedExhibit } from './scene/folio-fallback.js';
import { createSoundscape } from './audio/soundscape.js';
import { eras, specimens } from './folio-content.js';
import { vocalScore } from './vocal-score.js';
import {
  chapterStills,
  firstChoicePilot,
  garageBandTrack,
  ironVerdictTrack,
  murderBirdHero,
} from './media.js';

const app = document.querySelector('#app');
const escapeHtml = value => String(value).replace(/[&<>"']/g, character => ({
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
}[character]));

const lyricsMarkup = vocalScore.sections.map(section => `
  <section class="lyric-section">
    <h4>${escapeHtml(section.heading)}</h4>
    <p class="lyric-direction">${escapeHtml(section.direction)}</p>
    ${section.lines.length
      ? `<p class="lyric-lines">${section.lines.map(line => `<span>${escapeHtml(line)}</span>`).join('')}</p>`
      : '<p class="lyric-lines lyric-instrumental">[Instrumental; no vocal.]</p>'}
  </section>`).join('');

app.innerHTML = `
  <div class="site-shell">
    <header class="topbar">
      <a class="wordmark" href="#top" aria-label="MurderBird Uncaged home"><span class="mark">M<span class="mark-slash">/</span>B</span><span class="wordmark-text">MURDERBIRD <small>UNCAGED</small></span></a>
      <nav aria-label="Main navigation"><a href="./">Interactive exhibit</a><a href="./cg.html">Latest CG assessment</a><a href="#specimen">The folio</a><a href="#field-notes">Three eras</a><a href="#motion-sound">Motion and music</a><a class="nav-story" href="https://overkillhill.com/writings/murderbird/" target="_blank" rel="noopener noreferrer">Read the story ↗</a></nav>
    </header>

    <main id="top">
      <section class="intro">
        <div class="intro-copy">
          <p class="eyebrow"><span class="eyebrow-line"></span> AN INTERACTIVE MUSEUM FOLIO <span class="edition">/ 001</span></p>
          <h1>Meet the thing<br><em>that learned</em><br>to choose.</h1>
          <p class="intro-sub">A formidable, floor-standing mechanical terrorbird: hooked beak, heavy hips, long load-bearing legs, and compact folded wings. Explore the story, selected imagery and music here. The current three-era exterior and movement review is available in the <a href="./">3D exhibit</a>.</p>
          <a class="text-link" href="#specimen">ENTER THE FOLIO <span>↓</span></a>
        </div>
        <figure class="intro-art">
          <img src="${murderBirdHero.src}" srcset="${murderBirdHero.srcset}" sizes="(max-width: 760px) 100vw, 52vw" alt="${murderBirdHero.alt}" fetchpriority="high" decoding="async">
          <figcaption><span>COMMON SILHOUETTE / REFERENCE STILL</span><span>Floor-supported · development preview</span></figcaption>
        </figure>
      </section>

      <section id="specimen" class="exhibit" aria-labelledby="exhibit-title">
        <div class="exhibit-heading">
          <div><p class="eyebrow">EARLIER PROCEDURAL INTERPRETATION</p><h2 id="exhibit-title">Three eras. <em>Five systems.</em></h2></div>
          <p>ROTATE THE BODY<br>SELECT A PART TO FOLLOW ITS STORY</p>
        </div>
        <div class="exhibit-grid">
          <div class="viewer-column">
            <div class="era-chooser" role="group" aria-label="Choose an era layer">
              ${Object.entries(eras).map(([id, era]) => `
                <button type="button" data-era="${id}" aria-pressed="${id === 'builder'}">
                  <span>${era.number}</span><strong>${escapeHtml(era.label)}</strong><small>${escapeHtml(era.period)}</small>
                </button>`).join('')}
            </div>
            <p class="era-summary" id="era-summary" aria-live="polite">${escapeHtml(eras.builder.summary)} <a href="${eras.builder.storyHref}" target="_blank" rel="noopener noreferrer">Read this passage ↗</a></p>
            <div class="viewer" id="viewer">
              <div class="viewer-top"><span><i class="status-dot"></i> EARLIER PROCEDURAL MODEL</span><span id="scene-era-label">III / THE BUILDER</span></div>
              <div id="scene" aria-label="Earlier procedural MurderBird interpretation"></div>
              <div id="hotspots" class="hotspots" aria-label="Model inspection markers"></div>
              <div class="viewer-corner tl"></div><div class="viewer-corner tr"></div><div class="viewer-corner bl"></div><div class="viewer-corner br"></div>
              <div class="viewer-bottom"><span>HISTORICAL STUDY / NOT CURRENT MODEL</span><span id="view-label">BUILDER / EXTERIOR</span></div>
            </div>
            <p class="keyboard-hint" id="keyboard-hint">Drag or use arrow keys to rotate. Scroll or use + / − to zoom. Press Enter to trigger one brief reaction; R resets the view. Touch users can drag the model.</p>
            <div class="toolbar" aria-label="Exhibit controls">
              <button id="section-toggle" class="control primary" type="button" aria-pressed="false"><span class="control-icon">◫</span> OPEN HEART + MIND INSPECTION <span class="control-arrow">↗</span></button>
              <button id="poke-response" class="control" type="button"><span class="control-icon">↗</span> POKE / TEST RESPONSE</button>
              <button id="reset-view" class="control" type="button" title="Reset the model view"><span class="control-icon">⟲</span> RESET VIEW</button>
              <button id="sound-toggle" class="control" type="button" aria-pressed="false"><span class="control-icon">♫</span> SOUNDSCAPE OFF</button>
            </div>
            <p class="viewer-note">This earlier procedural interpretation is retained with the story folio. Its shape and movement do not represent the current exterior review, and its hidden machinery remains illustrative. <a href="./">Open the current three-era model</a> or explore the scoped references and music below. Artistic acceptance of the current model is pending.</p>
          </div>
          <aside class="inspector" aria-label="Anatomy and story index">
            <div class="inspector-header"><span>ANATOMY / STORY INDEX</span><span>01 — 05</span></div>
            <div class="part-list" id="part-list"></div>
            <div id="detail" class="detail" aria-live="polite"></div>
            <div class="inspector-foot"><span>ORIGIN · REPAIR · LIMIT</span><span>↘</span></div>
          </aside>
        </div>
      </section>

      <section class="timeline" id="field-notes" aria-labelledby="timeline-title">
        <div class="section-kicker"><span>THE CONSTRUCTION RECORD</span><span>THREE ERAS / WATER INTERLUDE</span></div>
        <h2 id="timeline-title">Not born. <em>Built, found, repaired.</em></h2>
        <div class="eras">
          <article><span class="era-number">I / THE MAKER</span><div class="era-symbol">✳</div><h3>Hand-worked</h3><p>Bronze, peened pins, and a commission shaped into a formidable terrestrial body. The first mechanism remains a story mystery.</p><a href="${eras.maker.storyHref}" target="_blank" rel="noopener noreferrer">Follow the Maker passage ↗</a></article>
          <article class="water-interlude"><span class="era-number">BETWEEN ERAS / WATER</span><div class="era-symbol">≈</div><h3>Inert. Preserved.</h3><p>Minerals and water mark an interval. The dark optic does not imply modern activation; incomplete fossils remain separate from the machine.</p><a href="https://overkillhill.com/writings/murderbird/#the-water" target="_blank" rel="noopener noreferrer">Follow the Water passage ↗</a></article>
          <article><span class="era-number">II / THE MECHANIC</span><div class="era-symbol">◎</div><h3>Recovered, repaired</h3><p>Found in 1853 and worked on in 1873: iron braces, brass bearings, and movement that borrows power from outside the body.</p><a href="${eras.mechanic.storyHref}" target="_blank" rel="noopener noreferrer">Follow the Mechanic passage ↗</a></article>
          <article><span class="era-number">III / THE BUILDER</span><div class="era-symbol">✺</div><h3>Power / learning</h3><p>Finite onboard energy and adaptive processing are separate additions. The inherited shoulder still limits the wing.</p><a href="${eras.builder.storyHref}" target="_blank" rel="noopener noreferrer">Follow the Builder passage ↗</a></article>
        </div>
      </section>

      <section class="media-atlas" id="media-record" aria-labelledby="media-title">
        <div class="section-kicker"><span>REFERENCE IMAGE RECORD</span><span>SUPPLIED STORY ART</span></div>
        <h2 id="media-title">Material, time, <em>repair.</em></h2>
        <p class="media-intro">Each image carries a specific story beat. They inform this preview; they do not certify a finished model, measured anatomy, or hidden mechanism.</p>
        <div class="still-grid">
          ${chapterStills.map(still => `
            <figure class="still-card">
              <img src="${still.src}" alt="${still.alt}" loading="lazy" decoding="async">
              <figcaption><span class="still-era">${still.era}</span><strong>${still.title}</strong><span>${still.note}</span></figcaption>
            </figure>`).join('')}
        </div>
      </section>

      <section class="media-playback" id="motion-sound" aria-labelledby="playback-title">
        <div class="section-kicker"><span>VISITOR-STARTED MEDIA</span><span>NO AUTOPLAY / ONE SOURCE AT A TIME</span></div>
        <h2 id="playback-title">Motion and <em>music.</em></h2>
        <div class="playback-grid">
          <article class="playback-card motion-card">
            <p class="playback-kicker">CONTROLLED PILOT 03 / 8 SECONDS / SILENT</p>
            <h3>First choice</h3>
            <video id="first-choice-video" controls playsinline preload="none" poster="${firstChoicePilot.poster}" aria-label="The first choice: a silent MurderBird motion study" aria-describedby="pilot-description">
              <source src="${firstChoicePilot.src}" type="video/mp4">
              <p>Your browser does not support this video. <a href="${firstChoicePilot.src}">Open the silent motion study</a>.</p>
            </video>
            <p id="pilot-description" class="playback-description">A controlled 2D study: the saddle and torso shift; the head lowers slightly. Both feet, the stand, floor, bench, and CRT stay fixed. This is not a reconstructed 3D mechanism or a longer film.</p>
            <details class="source-note">
              <summary>Motion source and approval scope</summary>
              <p>This exact eight-second delivery was approved for the MurderBird story page. It derives from an existing still; no Firefly generation was used. That approval does not extend to the rejected earlier pilots, a 3D rig, soundtrack, or planned longer film.</p>
            </details>
          </article>
          <div class="music-stack">
            <article class="playback-card">
              <p class="playback-kicker">IRON VERDICT / ORIGINAL PROGRAMMED DEMO</p>
              <h3>Custom-synthesis instrumental</h3>
              <audio id="iron-verdict-audio" controls preload="none" aria-label="Iron Verdict original custom-synthesis instrumental demo, no vocals">
                <source src="${ironVerdictTrack}" type="audio/mpeg">
                <a href="${ironVerdictTrack}">Open the original instrumental MP3</a>
              </audio>
              <p class="playback-description">104 BPM, 4/4, D minor; the 2:10 programmed instrumental. No live singer or recorded vocals.</p>
            </article>
            <article class="playback-card">
              <p class="playback-kicker">GARAGEBAND / ALTERNATE INSTRUMENT INTERPRETATION</p>
              <h3>A separate performance</h3>
              <audio id="garageband-audio" controls preload="none" aria-label="Iron Verdict separate GarageBand instrument interpretation, no vocals">
                <source src="${garageBandTrack}" type="audio/mpeg">
                <a href="${garageBandTrack}">Open the GarageBand interpretation MP3</a>
              </audio>
              <p class="playback-description">A visitor-controlled 192 kb/s listening copy of the separate GarageBand preview WAV; 2:16.6 including its instrument-effect tail. It is not the original custom-synthesis mix.</p>
              <details class="source-note">
                <summary>Source distinction</summary>
                <p>The GarageBand preview comes from native instrument patches and has a separate rights boundary from the original synthesis demo. The native session and stems are not loaded by this app.</p>
              </details>
            </article>
          </div>
        </div>

        <section class="vocal-score" aria-labelledby="vocal-score-title">
          <div class="vocal-score-heading"><div><p class="playback-kicker">VOCAL SCORE V2 / TEXT AND PERFORMANCE CONTEXT</p><h3 id="vocal-score-title">${escapeHtml(vocalScore.title)}</h3></div><span>NOT SUNG ON EITHER RECORDING</span></div>
          <p class="playback-description">${escapeHtml(vocalScore.tempo)} · ${escapeHtml(vocalScore.meter)} · ${escapeHtml(vocalScore.key)} · ${escapeHtml(vocalScore.bars)} · ${escapeHtml(vocalScore.range)} · ${escapeHtml(vocalScore.duration)}. ${escapeHtml(vocalScore.count)}.</p>
          <p class="playback-description">${escapeHtml(vocalScore.opening)} ${escapeHtml(vocalScore.ending)}</p>
          <p class="performance-direction">${escapeHtml(vocalScore.delivery)}</p>
          <details class="lyrics-details">
            <summary>Read the complete lyrics and section directions</summary>
            <p class="lyrics-status">${escapeHtml(vocalScore.status)}</p>
            <div class="lyrics-columns">${lyricsMarkup}</div>
          </details>
        </section>
      </section>

      <details class="production-note" id="production-note">
        <summary>Development production note</summary>
        <div class="production-note-body">
          <p>The procedural model uses a neck target of about half the torso length and load-bearing legs about torso length, with emu-informed joint placement and compact, deliberate weight transfer. These are visual targets, not measured or scientifically validated dimensions. It is not a finished model or production rig.</p>
          <p>The common master candidate anchors the silhouette and folded-wing contour. Story stills, the controlled silent pilot, the custom-synthesis demo, and the separate GarageBand interpretation retain distinct source and approval scopes. See <a href="https://overkillhill.com/writings/murderbird/" target="_blank" rel="noopener noreferrer">the complete story ↗</a> and the repository production map.</p>
        </div>
      </details>
      <section class="closing"><p class="eyebrow">THE STORY BEHIND THE SPECIMEN</p><h2>Every machine<br>has a <em>maker.</em></h2><a href="https://overkillhill.com/writings/murderbird/" target="_blank" rel="noopener noreferrer">READ THE COMPLETE STORY <span>↗</span></a></section>
    </main>
    <footer><span>© MURDERBIRD: UNCAGED</span><span>INTERACTIVE DEVELOPMENT PREVIEW</span><a href="#top">BACK TO TOP ↑</a></footer>
  </div>`;

const sceneElement = document.querySelector('#scene');
const viewerElement = document.querySelector('#viewer');
const hotspotLayer = document.querySelector('#hotspots');
const partList = document.querySelector('#part-list');
const detail = document.querySelector('#detail');
const sound = createSoundscape();
let selected = 'beak';
let activeEra = 'builder';
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
    console.warn('3D renderer unavailable; switching to the illustrated exhibit.', error);
    sceneElement.replaceChildren();
  }
}
if (!exhibit) {
  exhibit = createIllustratedExhibit(sceneElement);
  viewerElement.classList.add('fallback-active');
  document.querySelector('.viewer-top span:first-child').innerHTML = '<i class="status-dot"></i> SCOPED STORY ART';
  document.querySelector('.viewer-top span:last-child').textContent = 'LOCAL PREVIEW';
  document.querySelector('.exhibit-heading > p').textContent = 'SELECT AN ERA OR ANATOMY INDEX TO VIEW ITS STORY ART';
  document.querySelector('.keyboard-hint').textContent = 'WebGL is unavailable in this browser. Choose an era or anatomy index to view the matching supplied story art.';
  document.querySelector('#reset-view').hidden = true;
  document.querySelector('#poke-response').hidden = true;
  document.querySelector('.viewer-note').textContent = 'Scoped story art is shown because WebGL is unavailable. Choose an era or anatomy index to view its still. This folio preserves earlier study material; the current exterior review is linked above.';
}

function renderSelection(id, play = true) {
  const item = specimens.find(part => part.id === id);
  if (!item) return;
  selected = id;
  if ((id === 'heart' || id === 'mind') && activeEra === 'builder' && !sectionOpen) {
    setInspection(true);
  }
  partList.querySelectorAll('button').forEach(button => {
    const active = button.dataset.part === id;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
  hotspotLayer.querySelectorAll('button').forEach(button => button.classList.toggle('active', button.dataset.marker === id));
  detail.innerHTML = `
    <p class="detail-era">${escapeHtml(item.era)}</p>
    <h3>${escapeHtml(item.title)}</h3>
    <dl class="specimen-facts">
      <div><dt>ORIGIN</dt><dd>${escapeHtml(item.origin)}</dd></div>
      <div><dt>REPAIR</dt><dd>${escapeHtml(item.repair)}</dd></div>
      <div><dt>CONSTRAINT</dt><dd>${escapeHtml(item.constraint)}</dd></div>
    </dl>
    <blockquote class="story-passage">${escapeHtml(item.passage)}</blockquote>
    <a class="story-thread" href="${item.storyHref}" target="_blank" rel="noopener noreferrer">READ THE MATCHING STORY PASSAGE ↗</a>
    <p class="observation"><span>MODEL NOTE</span>${escapeHtml(item.observation)}</p>`;
  exhibit.select(id);
  if (play) {
    sound.effect(item.sound);
    trackEvent('select_specimen', { specimen_id: item.id });
  }
}

function setInspection(value) {
  sectionOpen = Boolean(value && activeEra === 'builder');
  exhibit.setSection(sectionOpen);
  const button = document.querySelector('#section-toggle');
  button.setAttribute('aria-pressed', String(sectionOpen));
  button.innerHTML = `<span class="control-icon">◫</span> ${sectionOpen ? 'CLOSE HEART + MIND INSPECTION' : 'OPEN HEART + MIND INSPECTION'} <span class="control-arrow">↗</span>`;
  document.querySelector('#view-label').textContent = sectionOpen ? 'BUILDER / HEART + MIND' : `${eras[activeEra].number} / ${activeEra.toUpperCase()} / EXTERIOR`;
}

partList.innerHTML = specimens.map(item => `
  <button type="button" data-part="${item.id}" aria-pressed="false">
    <span class="part-number">${item.number}</span><span>${escapeHtml(item.name)}</span><span class="part-arrow">↗</span>
  </button>`).join('');
hotspotLayer.innerHTML = specimens.map(item => `
  <button class="marker" type="button" data-marker="${item.id}" aria-label="Inspect ${escapeHtml(item.name)}" hidden>
    <span>${item.number}</span>
  </button>`).join('');

document.querySelectorAll('[data-era]').forEach(button => {
  button.addEventListener('click', () => {
    activeEra = button.dataset.era;
    sectionOpen = false;
    exhibit.setEra(activeEra);
    exhibit.setSection(false);
    document.querySelectorAll('[data-era]').forEach(tab => {
      tab.setAttribute('aria-pressed', String(tab.dataset.era === activeEra));
    });
    const era = eras[activeEra];
    document.querySelector('#era-summary').innerHTML = `${escapeHtml(era.summary)} <a href="${era.storyHref}" target="_blank" rel="noopener noreferrer">Read this passage ↗</a>`;
    document.querySelector('#scene-era-label').textContent = `${era.number} / ${era.label.toUpperCase()}`;
    document.querySelector('#section-toggle').disabled = activeEra !== 'builder';
    setInspection(false);
    renderSelection(era.firstPart, false);
    trackEvent('select_era', { era: activeEra });
  });
});

document.querySelector('#section-toggle').addEventListener('click', () => {
  if (activeEra !== 'builder') return;
  setInspection(!sectionOpen);
  if (sectionOpen) renderSelection('heart', false);
  sound.effect(sectionOpen ? 'open' : 'click');
  trackEvent('section_view_toggle', { is_open: sectionOpen });
});
document.querySelector('#poke-response').addEventListener('click', () => {
  exhibit.react();
  trackEvent('model_reaction');
});
document.querySelector('#reset-view').addEventListener('click', () => {
  exhibit.reset();
  sound.effect('click');
  trackEvent('view_reset');
});
partList.addEventListener('click', event => {
  const button = event.target.closest('[data-part]');
  if (button) renderSelection(button.dataset.part);
});
hotspotLayer.addEventListener('click', event => {
  const button = event.target.closest('[data-marker]');
  if (button) renderSelection(button.dataset.marker);
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
document.querySelector('#section-toggle').disabled = false;
renderSelection('beak', false);
if (activeEra !== 'builder') setInspection(false);
new ResizeObserver(() => exhibit.resize()).observe(viewerElement);
