# MurderBird: Uncaged

**Current shared goal:** read the root-level [goal.md](goal.md) before assigning, reviewing or starting work. Its YAML front matter records `last_updated`; use GitHub `main` for the latest shared revision. Cross-system review and commentary: [issue #14](https://github.com/OKHP3/murderbird-uncaged/issues/14).

**One inherited body. Three eras. An interactive mechanical-creature exhibit.**

![MurderBird: Uncaged — mechanical bird reference art, with the interactive exhibit labeled under assessment](public/social-preview.png)

**[Assess the latest CG character](https://okhp3.github.io/murderbird-uncaged/cg.html)** · **[Enter the interactive exhibit](https://okhp3.github.io/murderbird-uncaged/)** · **[Read the origin story](https://overkillhill.com/writings/murderbird/)**

Meet a flightless mechanical creature whose construction changes across centuries. Orbit its enclosure, operate the Maker's external controls, engage the Mechanic's limited walking routine, and encounter the Advanced bird's attention, strikes, jump, and shield thrust. Open its assemblies to explore the machinery beneath the armor.

**Two selected packages are retained:** the static CG assessment and the V37 interactive movement exhibit. Their editable sources, usable exports, receipts and acceptance limits are listed under [Selected deliverables](#selected-deliverables). The banner is reference artwork.

## Three eras, three ways to move

| Era | What you can do | Construction |
| --- | --- | --- |
| **I · Maker** | Operate the leg, wing, tail, neck, and jaw controls. The supported body stays anchored. | External levers, rods, and lines; no autonomous movement or internal powered system. |
| **II · Mechanic** | Wind and engage a slow routine of short steps, pauses, and segmented turns. | A proposed spring, reduction-gear, and cam transmission with finite stored energy. |
| **III · Advanced** | Observe pacing and attention, choose a position at the rail, reach and retreat, or trigger a power jump and shield thrust. | Coordinated actuators, sensing, processing, and a separate fictional power supply. |

The wings are flightless guards for balance and shielding. The repaired anatomical left shoulder retains limited travel. New hidden mechanisms are proposed reconstructions. Current exhibit directions and the original story are recorded separately where they differ.

## Explore the exhibit

- **Look around:** drag to orbit; scroll or pinch to zoom. Camera buttons and keyboard controls are also available.
- **Choose an era:** the controls, movement, and visible construction change together.
- **Look inside:** open for inspection, select an assembly, center it, and adjust separation. Reassemble to return to the encounter.
- **Control the experience:** pause, reduce motion, toggle labels, and choose whether to start sound. Iron Verdict plays only after you press Play.
- **Without WebGL:** an illustrated view preserves era-specific explanations; it does not simulate the full 3D encounter.

The [story and media folio](https://okhp3.github.io/murderbird-uncaged/folio.html) preserves the illustrated narrative, motion study, and earlier model context. The **main exhibit above is the current interactive implementation**; the folio's earlier construction study is historical context.

## Selected deliverables

Use these existing packages as the entry point; their source trees and filenames stay intact.

| Package | Editable native | Usable export / evidence | Current status |
|---|---|---|---|
| CG Maker, retained04 | [Blender source](assets/audit/cg-recursive-three-loop01/loop03/delivery/retained04/maker/murderbird-recursive-maker.blend) | [GLB](assets/audit/cg-recursive-three-loop01/loop03/delivery/retained04/maker/murderbird-recursive-maker.glb), [native views and receipt](assets/audit/cg-recursive-three-loop01/loop03/delivery/retained04/maker/) | Static assessment; no skins or animations. |
| CG Mechanic, retained04 | [Blender source](assets/audit/cg-recursive-three-loop01/loop03/delivery/retained04/mechanic/murderbird-recursive-mechanic.blend) | [GLB](assets/audit/cg-recursive-three-loop01/loop03/delivery/retained04/mechanic/murderbird-recursive-mechanic.glb), [native views and receipt](assets/audit/cg-recursive-three-loop01/loop03/delivery/retained04/mechanic/) | Static assessment; no skins or animations. |
| CG Advanced, retained04 (source folder: builder) | [Blender source](assets/audit/cg-recursive-three-loop01/loop03/delivery/retained04/builder/murderbird-recursive-builder.blend) | [GLB](assets/audit/cg-recursive-three-loop01/loop03/delivery/retained04/builder/murderbird-recursive-builder.glb), [native views and receipt](assets/audit/cg-recursive-three-loop01/loop03/delivery/retained04/builder/) | Static assessment; no skins or animations. |
| V37 interactive exhibit | [Blender source](assets/models/whole-character-v37/attempt-release02/murderbird-whole-character-v37.blend) | [GLB](assets/models/whole-character-v37/attempt-release02/murderbird-whole-character-v37.glb), [era previews and package](assets/models/whole-character-v37/attempt-release02/), [release record](docs/production-v37.md) | Owner-authorized exhibit with kinematic movement, inspection, sound and illustrated fallbacks. |

The [CG selection manifest](assets/review/cg-publication.json) and [V37 runtime manifest](assets/review/production-v37.json) pin the browser assets. The [CG import ledger](provenance/cg-production-import-2026-10-04.json) and [release handoff](docs/handoffs/cg-production-release-2026-10-04-01.md) retain source paths, hashes and delivery evidence. Native sources, packed textures, views and receipts remain in their established packages; public copies are generated only from explicit publication selections.

These are selected deliverables, not final artistic acceptance. CG source likeness remains **UNMET**, owner acceptance **PENDING**, and strict native/export normal parity remains **FAIL** at **2e-5** ([diagnosis](assets/audit/delegation-series-2026-10-05/packets/mb-p04/normal-diagnosis.json)). The CG candidate retains shorter breast courses, local underlaps, articulated toe detail and a restrained crown finish change. V37 remains the separate movement exhibit; construction is rigid, motion is kinematic, and physical engineering is not established.

For story, artwork, audio and historical source packages, use the [media catalog](docs/media-catalog.md). Historical variants and their source refs remain recoverable; do not promote them by age or filename. Machine-local recovery archives and worktree ownership records belong outside publication paths. The verified owner staging archive is separate from this repository and is not an independent backup. Repository navigation or tracked-file cleanup does not purge hosted Git LFS objects.

## One release source

**GitHub `main` is the integration and deployment source.** GitHub Actions builds the current exhibit and story folio together and publishes one GitHub Pages artifact.

- [Build checks](https://github.com/OKHP3/murderbird-uncaged/actions/workflows/validate.yml)
- [Validated Pages deployment](https://github.com/OKHP3/murderbird-uncaged/actions/workflows/validate.yml)
- [Live release manifest](https://okhp3.github.io/murderbird-uncaged/release.json): exact source revision and SHA-256 hashes for the published files.
- [Release and reconciliation guide](docs/release-source-of-truth.md)

A local preview is a checkout, not a second authority. Replit is development preview only. Other machines and Replit must verify their own commit against `origin/main`; this repository does not imply that an inaccessible checkout is synchronized.

## Run locally

Use a supported Node.js version from `package.json`, Python 3, and Git LFS for the model and media files.

```sh
git lfs install --local --skip-smudge
node scripts/ci-lfs-assets.mjs plan --scope=build
node scripts/ci-lfs-assets.mjs hydrate --scope=build
npm ci
npm run dev -- --host 127.0.0.1
```

Hydration verifies existing local payloads and fails clearly when required content is missing. For a new checkout, clone with `git -c filter.lfs.smudge= -c filter.lfs.process= -c filter.lfs.required=false clone https://github.com/OKHP3/murderbird-uncaged.git` to retain pointers initially. See [bounded LFS downloads](docs/lfs-downloads.md) before explicitly fetching missing assets; ordinary development and synchronization do not automatically retrieve the archive.

Create and inspect the production release:

```sh
node scripts/ci-lfs-assets.mjs hydrate
npm run build
node --test tests/*.test.mjs
node scripts/verify-theme-release.mjs
node scripts/verify-publication.mjs
node scripts/verify-presentation.mjs
python3 scripts/verify-media-import.py
npm run preview -- --host 127.0.0.1
```

`npm run build` includes the manifest-selected review gallery and writes `dist/release.json`. Local modified builds are marked as such. The publication verifier checks emitted media and file hashes. Full validation requires the default CI asset scope, including imported source originals and test fixtures; a preview needs only `--scope=build`. CI restores verified cached objects and validates Node 24 and 26; network hydration requires an explicit manual request. See the [technology inventory](docs/technology-stack.md) for maintenance details.

The application uses **Vite, Three.js, and Web Audio**, with no application backend. Existing Google Analytics is loaded by the page; audio remains visitor-controlled. Do not put credentials or private files into browser assets.

## Sources, privacy, and ownership

This is the canonical repository for MurderBird creative production and the interactive exhibit. The published original story remains on OverKill Hill. FoundRy is an incubation/routing space, and Replit is a preview environment.

| Location | Purpose |
| --- | --- |
| `src/` | Active exhibit, era movement, folio, and audio code |
| `assets/models/` | Versioned editable models, exports, maps, and preview renders |
| `assets/murderbird/`, `assets/img/` | Preserved creative sources and production history |
| `content/story/` | Provenance-linked story snapshots; not a live-page claim |
| `docs/`, `provenance/` | Requirements, decisions, source lineage, and validation boundaries |
| `public/` | Deliberately approved browser-delivered files |
| `.local/` | Ignored private archives and machine-local verification |

Original names, source trees, and historical candidates are preserved. Only explicit runtime references and the reviewed publication allowlist enter the website build. Private session archives are never staged or published. Read the [repository boundaries](docs/repository-boundaries.md), [asset guide](assets/current-deliverables.md), [media catalog](docs/media-catalog.md), and [agent guidance](AGENTS.md) before contributing.

## License and credits

Created and directed by **Jamie Hill / OverKill Hill P³**.

**Code:** [MIT](LICENSE). **MurderBird creative content:** all rights reserved, including the character, likeness, story, imagery, models, music, and lyrics. The code license does not grant reuse rights to the creature. See [NOTICE.md](NOTICE.md).
