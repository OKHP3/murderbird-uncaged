import { chapterStills, murderBirdHero } from '../media.js';

const fallbackArt = {
  beak: { ...murderBirdHero, era: 'COMMON SILHOUETTE', title: 'Master still' },
  shoulder: chapterStills[2],
  ankle: chapterStills[4],
  heart: chapterStills[3],
  mind: chapterStills[4],
};

// Use the scoped story art when WebGL is unavailable; do not substitute
// symmetric placeholder geometry for the character reference.
export function createIllustratedExhibit(container) {
  container.innerHTML = `
    <figure class="fallback-scene">
      <img class="fallback-image" src="${murderBirdHero.src}" srcset="${murderBirdHero.srcset}" sizes="100vw" alt="${murderBirdHero.alt}" decoding="async">
      <figcaption class="fallback-caption">COMMON SILHOUETTE / LOCAL-PREVIEW MASTER STILL</figcaption>
    </figure>`;
  const image = container.querySelector('.fallback-image');
  const caption = container.querySelector('.fallback-caption');
  let selected = null;
  let activeEra = 'builder';
  const eraArt = {
    maker: chapterStills[0],
    mechanic: chapterStills[2],
    builder: chapterStills[4],
  };
  function showStill(still) {
    if (!still) return;
    image.src = still.src;
    if (still.srcset) {
      image.srcset = still.srcset;
      image.sizes = '100vw';
    } else {
      image.removeAttribute('srcset');
      image.removeAttribute('sizes');
    }
    image.alt = still.alt;
    caption.textContent = `${still.era} / ${still.title} / LOCAL PREVIEW`;
  }
  return {
    supportsMarkers: false,
    resize() {},
    select(id) {
      if (id === selected) return;
      selected = id;
      const still = activeEra === 'maker'
        ? eraArt.maker
        : activeEra === 'mechanic'
          ? eraArt.mechanic
          : fallbackArt[id];
      showStill(still);
    },
    setEra(era) {
      activeEra = era;
      selected = null;
      showStill(eraArt[era]);
    },
    setSection(value) {
      selected = null;
      showStill(value ? fallbackArt.heart : eraArt[activeEra]);
    },
    react() {},
    reset() {},
  };
}