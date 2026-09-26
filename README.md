# MurderBird: Uncaged

An interactive teardown of **The MurderBird**: spin it, inspect its mechanisms, watch it choose. Built in the spirit of a science-museum exhibit (think *How It's Made*, not *Walking with Dinosaurs*), the goal is showing how the thing works across three eras of construction and repair, not staging a chase scene.

The canonical origin story lives at [overkillhill.com/writings/murderbird](https://overkillhill.com/writings/murderbird/). This repo is the companion interactive build: the 3D model, the exploded-view hotspots, the reactive sound design, and the bird's "uncaging" moment (its first autonomous choice) staged as a payoff rather than something you just read about.

## Status

Playable first-pass exhibit. The bird is a procedural Three.js construction study: drag to rotate, scroll to zoom, select anatomy markers, and open the chest section. The field notes follow the three-era outline in `docs/`. Sound is an optional synthesized Web Audio sketch, not the final song or recorded bird. No finished model, images, or videos are included yet; those require source assets. The original story remains on [overkillhill.com](https://overkillhill.com/writings/murderbird/).

## Getting started

```
npm install
npm run dev
```

## Stack

See the [complete technology inventory and update plan](docs/technology-stack.md) and [current/latest version table](docs/technology-versions.md). Refresh with `npm run technology:report`. Weekly Dependabot proposals and a technology freshness workflow are configured for activation on the default branch.

- [Vite](https://vitejs.dev/) for build/dev tooling, matching the main overkillhill.com site's pipeline
- [Three.js](https://threejs.org/) for the 3D scene, vanilla rather than a framework wrapper, kept deliberately light for a single-page exhibit
- Web Audio API for the opt-in synthesized bed and interaction effects; final stems and climax crossfade await media assets
- Git LFS for binary assets (3D models, audio, video), see `.gitattributes`

This is a static client-side SPA; it does not use a backend or secrets.

## GitHub Pages

The existing `.github/workflows/deploy.yml` builds `dist/` on pushes to `main` and uploads it to GitHub Pages. In the repository's **Settings → Pages**, choose **GitHub Actions** as the source. `vite.config.js` uses relative asset paths so the build works under a repository subpath. Deployment is performed by GitHub Actions, **not** Replit publishing.

To check the production bundle locally, run `npm run build` then `npm run preview`. The Replit dev preview, if running, is only a development view.

## Adding finished media

Place source material under `assets/` according to `assets/README.md`; browser-delivered static files belong in `public/` or can be imported from `src/`. Large binary assets are tracked with Git LFS, so confirm GitHub Pages can retrieve your LFS media before relying on it. The current UI does not pretend to play a song or video that has not been supplied.

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
