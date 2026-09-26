# Technology inventory and update plan

Audited 2026-09-26 against local/GitHub main commit `05f17758f43d4d217a58e123cf23ef1c4e6426c8`. The checkout was clean before this work. Source inventory covers all tracked application files, manifests, lockfile, Replit configuration, and workflows. See [the generated version table](technology-versions.md) for exact package versions, official upstream links, and latest stable comparisons, including every optional platform package. [JSON evidence](technology-versions.json) is also available. New workflow dependencies are included in that report.

## Application and tooling

| Technology | In-place evidence | Latest / maintenance approach |
|---|---|---|
| JavaScript / ECMAScript modules | `.js` source; `type: module`; no explicit ECMAScript edition or browser support policy | Language features track browser support; not an npm version to upgrade. [ECMA-262](https://ecma-international.org/publications-and-standards/standards/ecma-262/) is the specification authority. |
| HTML | HTML5 doctype in `index.html` | [HTML Living Standard](https://html.spec.whatwg.org/); continuously maintained, no package version. |
| CSS | Native styles in `src/style.css` and `src/fallback.css` | Modular browser standards, no single CSS package version; [W3C CSS](https://www.w3.org/Style/CSS/). |
| Three.js | Exact locked `0.186.1` | Latest `0.186.1` at refresh; review scene rendering on future updates. |
| Vite | Exact locked `8.3.1` | Latest `8.3.1` at refresh; requires Node `^20.19.0 || >=22.12.0`. |
| WebGL / GPU shaders | Three.js WebGLRenderer; WebGL2/WebGL feature probe; illustrated fallback | [WebGL 2.0](https://www.khronos.org/webgl/) is the latest API generation. Browser/GPU implementation varies; no pinned driver or shader compiler. |
| Web Audio | Browser AudioContext with prefixed fallback; synthesized audio | Browser-managed. [W3C Web Audio](https://www.w3.org/TR/webaudio/) currently presents 1.1 work; a specification draft is not a package upgrade or guaranteed browser capability. |
| DOM, SVG and browser events | Browser UI and illustrated scene | Browser-managed standards; validate functionality in Chrome/Edge and mobile browsers. |
| Google Fonts | CSS API v2; DM Mono, DM Sans, Playfair Display | Hosted, unpinned fonts; exact served font revisions vary and are not recorded. [CSS API documentation](https://developers.google.com/fonts/docs/css2). Review typography/network behavior or self-host approved fonts for reproducibility. |
| Google Analytics 4 / Google tag | Added by the subsequent Replit commits through `35c15da`; hosted `gtag.js` and interaction events | Hosted, unpinned service script; no repository-controlled semantic version. This addition postdates the initial inventory snapshot. |
| JSON-LD / Schema.org, Open Graph, Web App Manifest, sitemap / robots | Metadata and assets added through `35c15da` | Web metadata formats and hosted vocabularies, not new installed npm packages. |
| Node.js | `.nvmrc` 24; Replit and deployment 24; CI 24/26; package engine `>=24 <27` | Node 24 LTS is the production line; Node 26 Current is the forward-compatibility CI lane. Node 20 reached EOL in March 2026. |
| npm | Local 11.6.2; lockfile format 3; CI uses Node-bundled npm | Version comes with Node; package dependencies are exactly pinned and reproducible via `npm ci`. |
| Python | Removed from Replit modules; no application use | No `.py`, pip manifest, Python build step, or Python runtime in the application. |
| Replit / Nix | `web`, `nodejs-24`; channel `stable-25_05` | Platform-managed module/channel identifiers. Runtime build was verified through Replit shell; exact Nix executable/channel patch remains platform-managed. [Configuration reference](https://docs.replit.com/features/project-setup/configuration). |
| Git / Git LFS | Local Git 2.55.0.windows.5 and LFS 3.7.1; media patterns in `.gitattributes` | Git for Windows 2.55.0 base; LFS 3.8.0. Host tooling, not shipped site dependencies; review packaging revisions separately. |
| GitHub Actions / Pages | checkout v7, setup-node v7, upload-pages-artifact v5.0.0, deploy-pages v5.0.1 | Current releases at refresh. Dependabot groups weekly action updates. Pages is hosted and has no project-controlled service version. |
| Ubuntu runner | `ubuntu-latest` | GitHub-managed moving image; exact OS/tool image requires a run's setup log. [Runner images](https://github.com/actions/runner-images). |
| JSON, YAML, TOML, Markdown | npm/lock files, Actions, `.replit`, documentation | Configuration/document formats, not separately installed runtime libraries. |

Transitive build tooling includes Rollup 4.63.4, esbuild 0.21.5, PostCSS 8.5.28, nanoid 3.3.19, picocolors 1.1.1, source-map-js 1.2.1, fsevents 2.3.3, ESTree types 1.0.9, an optional lzma binary, and all esbuild/Rollup platform binaries. The generated table enumerates them individually. Type declarations inside a dependency do not make this a TypeScript application. Some optional binaries are locked but are not installed on Windows.

**Absent:** TypeScript application/compiler, Tailwind, React, Next.js, Python application, database, backend server, container build, and an existing automated browser-test framework. Vite's internal CSS processing does not establish a Tailwind installation. Editors, ChatGPT, and the Replit agent are authoring tools; their installed app/model versions are not established by repository source and are not application dependencies.

## Update mechanism

1. `.github/dependabot.yml` checks npm and GitHub Actions weekly and proposes version/lockfile updates as pull requests. This includes major updates; Three.js 0.x minor changes deserve breaking-change review. Transitive constraints are resolved through the parent dependency, not arbitrary overrides. See [Dependabot version updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-version-updates).
2. `validate.yml` builds every PR on Node 24 LTS and Node 26 Current using `npm ci`. Deployment and Replit use Node 24 LTS. `.nvmrc` and `package.json` engines express the same compatibility boundary.
3. `technology-freshness.yml` checks official npm registries, Node releases, Python downloads, and GitHub release endpoints every Monday and on demand. It publishes the complete table in the run summary. Exit 0 means no detected drift, 1 means a lookup failed, and 2 means update candidates exist. GitHub failure notifications depend on the owner's notification settings. This is an alert/report, not an automatic deployment.
4. Run `npm run technology:report` to refresh the local Markdown/JSON inventory, or `npm run technology:check` to enforce freshness. Node 24 supplies its standard APIs. Reports carry a UTC timestamp and reflect the executing host, so CI host npm/LFS measurements differ from Windows. Unknown source lookups fail visibly. Major-only declarations cannot establish exact patch versions.
5. Monthly, inspect the Replit-supported modules/channel, runner image, browser support and fonts. Apply supported runtime changes on a branch, verify actual `node --version`, `npm --version`, and (if retained) `python --version` in Replit, then update the declarations and report. Dependabot does not update Replit modules, Node declarations, host software, fonts, or browser APIs. These remain explicit maintenance work.

## Upgrade acceptance

The Node 24/Vite 8/Three.js 0.186.1 and Actions upgrade is staged together on a review branch; the prior individual Dependabot PR builds passed on Node 20/24. The combined change is validated on Node 24/26, a fresh lockfile install, build, zero-vulnerability audit, and interactive Replit preview before merging.

For Three.js/Vite upgrades, verify rotation, zoom, all anatomy markers, chest opening, resize/mobile layout, console errors, and opt-in audio. Check both the illustrated no-WebGL fallback and a real WebGL2 scene: the repository's `.agents/memory/webgl-preview.md` records why Replit screenshots alone cannot validate 3D. A successful bundle is necessary but does not establish visual/audio equivalence. Merge only after these checks; the existing main-branch workflow then deploys. Recover regressions by reverting the upgrade commit and redeploying the previous lockfile.

## Activation and evidence limits

Local validation after upgrade: current version inventory refreshed with zero lookup failures; Vite 8.3.1 production build passes; `npm audit` reports zero vulnerabilities. A bundle size warning notes the app JavaScript chunk exceeds 500 kB; inspect Three.js loading or split the viewer if initial-load performance warrants it. Combined GitHub Node 24/26 checks and Pages deploy remain release gates.

The pre-upgrade lockfile's npm audit found moderate and high Vite/esbuild development-tool vulnerabilities. Upgrading to Vite 8.3.1 and regenerating the lockfile removes those findings; `npm audit` now reports zero vulnerabilities. The build warns that its JavaScript chunk is above 500 kB after minification, so visual/interaction validation remains necessary.

Weekly schedules and Dependabot are active on GitHub `main`; build checks run on each PR. Repository branch rules do not require these checks, so the merge gate must continue to inspect them explicitly. Updates remain reviewed, without blind auto-merging.

The Replit connector still requests reauthentication, but the authenticated Replit browser Shell previously proved clean parity with GitHub. Actual compatibility after changing its declared Node module must be separately confirmed by a successful Replit install/build. Nix/channel patch, hosted font revisions, and real visitor browser/GPU versions remain platform-managed.
