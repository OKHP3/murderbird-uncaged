import hero480 from '../assets/img/webp/murderbird-unified-master-03-2026-09-06-480.webp';
import hero960 from '../assets/img/webp/murderbird-unified-master-03-2026-09-06-960.webp';
import hero1536 from '../assets/img/webp/murderbird-unified-master-03-2026-09-06-1536.webp';
import maker from '../assets/img/webp/murderbird-unified-maker-clean-2026-09-06-960.webp';
import water from '../assets/img/webp/murderbird-unified-water-2026-09-06-960.webp';
import mechanic from '../assets/img/webp/murderbird-unified-mechanic-2026-09-06-960.webp';
import heart from '../assets/img/webp/murderbird-unified-heart-2026-09-06-960.webp';
import sentinel from '../assets/img/webp/murderbird-unified-sentinel-2026-09-06-960.webp';
import pilotPoster from '../assets/img/murderbird-first-choice-poster.jpg';
import pilotVideo from '../assets/video/murderbird-first-choice-635f0e15.mp4';
import ironVerdictTrack from '../assets/murderbird/production/audio/iron-verdict/murderbird-iron-verdict.mp3';

export const murderBirdHero = {
  src: hero960,
  srcset: `${hero480} 480w, ${hero960} 960w, ${hero1536} 1536w`,
  alt: 'A large mechanical bird stands on both taloned feet on the workshop floor beside a workbench and CRT.',
};

export const chapterStills = [
  {
    era: 'I / THE MAKER',
    title: 'A quiet inspection',
    src: maker,
    alt: 'A hooded Maker stands beside the floor-standing bronze Bird during a quiet inspection; the hammer is lowered and intact.',
    note: 'Local-preview still; not the later hammer-breaking scene.',
  },
  {
    era: 'BETWEEN ERAS / WATER',
    title: 'An inert body',
    src: water,
    alt: 'The Bird lies still and partly submerged among sediment, roots, and mineral deposits.',
    note: 'Dark eye and mineral history; no modern activation is implied.',
  },
  {
    era: 'II / THE MECHANIC',
    title: 'Repair around the old body',
    src: mechanic,
    alt: 'A mechanic works beside the floor-supported Bird among workshop tools and visible repair supports.',
    note: 'Industrial repair; no autonomous modern mind is implied.',
  },
  {
    era: 'III / THE BUILDER',
    title: 'Power inspection',
    src: heart,
    alt: 'A builder examines the Bird’s opened chest assembly in a workshop.',
    note: 'Power inspection only; this image does not depict a completed mind.',
  },
  {
    era: 'III / THE BUILDER',
    title: 'The Sentinel',
    src: sentinel,
    alt: 'The Bird stands on the workshop floor beside an operator and a CRT computer.',
    note: 'The computer is nearby; it does not support the Bird.',
  },
];

export const firstChoicePilot = {
  src: pilotVideo,
  poster: pilotPoster,
};

export { ironVerdictTrack };