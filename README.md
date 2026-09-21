# MurderBird: Uncaged

An interactive teardown of **The MurderBird**: spin it, inspect its mechanisms, watch it choose. Built in the spirit of a science-museum exhibit (think *How It's Made*, not *Walking with Dinosaurs*), the goal is showing how the thing works across three eras of construction and repair, not staging a chase scene.

The canonical origin story lives at [overkillhill.com/writings/murderbird](https://overkillhill.com/writings/murderbird/). This repo is the companion interactive build: the 3D model, the exploded-view hotspots, the reactive sound design, and the bird's "uncaging" moment (its first autonomous choice) staged as a payoff rather than something you just read about.

## Status

Early scaffold. No working exhibit yet. This commit lays down repo structure, licensing, and asset conventions before any real 3D or audio work lands. Treat everything under `src/` as placeholder.

## Getting started

```
npm install
npm run dev
```

## Stack (assumed, open to change)

- [Vite](https://vitejs.dev/) for build/dev tooling, matching the main overkillhill.com site's pipeline
- [Three.js](https://threejs.org/) for the 3D scene, vanilla rather than a framework wrapper, kept deliberately light for a single-page exhibit
- Web Audio API for the layered theme-song bed, SFX ducking, and climax crossfade, `<audio>` tags won't do the mixing this needs
- Git LFS for binary assets (3D models, audio, video), see `.gitattributes`

None of this is locked in, it's a reasonable default so the scaffold isn't empty. Swap it if the actual build calls for something else.

## License

Split license, see [NOTICE.md](./NOTICE.md) for the full explanation:

- **Code**: MIT, see [LICENSE](./LICENSE)
- **The MurderBird itself** (name, character, story, art, model, music): all rights reserved, not covered by the MIT grant

## Structure

```
src/          application code (scene, audio engine, UI/hotspots)
public/       static passthrough files (favicon, etc.)
assets/       models, audio, reference images, see assets/README.md
docs/         design docs: hotspot map, audio brief, etc.
```

## Related

- Origin story: [overkillhill.com/writings/murderbird](https://overkillhill.com/writings/murderbird/)
- Main site repo is separate by design, keeps this exhibit's binary asset churn (models, audio, texture iterations) out of the canon content repo's git history
