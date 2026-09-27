import { chapterStills, murderBirdHero } from '../media.js';

const fallbackArt = {
  beak: { ...murderBirdHero, era: 'COMMON SILHOUETTE', title: 'Master still' },
  joint: chapterStills[2],
  core: chapterStills[3],
  eye: chapterStills[4],
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
  return {
    supportsMarkers: false,
    resize() {},
    select(id) {
      if (id === selected) return;
      selected = id;
      const still = fallbackArt[id];
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
    },
    setSection(value) {
      if (value) this.select('core');
    },
    react() {},
    reset() {},
  };
}