# Technology inventory and update plan

Audited 2026-09-26 against local/GitHub main commit `05f17758f43d4d217a58e123cf23ef1c4e6426c8`. The checkout was clean before this work. Source inventory covers all tracked application files, manifests, lockfile, Replit configuration, and workflows. See [the generated version table](technology-versions.md) for exact package versions, official upstream links, and latest stable comparisons, including every optional platform package. [JSON evidence](technology-versions.json) is also available. New workflow dependencies are included in that report.

## Application and tooling

| Technology | In-place evidence | Latest / maintenance approach |
|---|---|---|
| JavaScript / ECMAScript modules | `.js` source; `type: module`; no explicit ECMAScript edition or browser support policy | Language features track browser support; not an npm version to upgrade. [ECMA-262](https://ecma-international.org/publications-and-standards/standards/ecma-262/) is the specification authority. |
| HTML | HTML5 doctype in `index.html` | [HTML Living Standard](https://html.spec.whatwg.org/); continuously maintained, no package version. |
| CSS | Native styles in `src/style.css` and `src/fallback.css` | Modular browser standards, no single CSS package version; [W3C CSS](https://www.w3.org/Style/CSS/). |
| Three.js | Exact locked `0.169.0`; range `^0.169.0` | Latest `0.186.1` at audit; review migration notes and rendered scene. |
| Vite | Exact locked `5.4.21`; range `^5.4.21` | Latest `8.3.1`; major migration requires newer Node and build/browser checks. |
| WebGL / GPU shaders | Three.js WebGLRenderer; WebGL2/WebGL feature probe; illustrated fallback | [WebGL 2.0](https://www.khronos.org/webgl/) is the latest API generation. Browser/GPU implementation varies; no pinned driver or shader compiler. |
| Web Audio | Browser AudioContext with prefixed fallback; synthesized audio | Browser-managed. [W3C Web Audio](https://www.w3.org/TR/webaudio/) currently presents 1.1 work; a specification draft is not a package upgrade or guaranteed browser capability. |
| DOM, SVG and browser events | Browser UI and illustrated scene | Browser-managed standards; validate functionality in Chrome/Edge and mobile browsers. |
| Google Fonts | CSS API v2; DM Mono, DM Sans, Playfair Display | Hosted, unpinned fonts; exact served font revisions vary and are not recorded. [CSS API documentation](https://developers.google.com/fonts/docs/css2). Review typography/network behavior or self-host approved fonts for reproducibility. |
| Google Analytics 4 / Google tag | Added by the subsequent Replit commits through `35c15da`; hosted `gtag.js` and interaction events | Hosted, unpinned service script; no repository-controlled semantic version. This addition postdates the initial inventory snapshot. |
| JSON-LD / Schema.org, Open Graph, Web App Manifest, sitemap / robots | Metadata and assets added through `35c15da` | Web metadata formats and hosted vocabularies, not new installed npm packages. |
| Node.js | CI 20, Replit `nodejs-20`; local 24.11.1 | Latest stable Current 26.10.0; LTS 24.21.0. Prefer LTS for this project; exact hosted patches unknown. |
| npm | Local 11.6.2; lockfile format 3; CI uses Node-bundled npm | Latest 12.1.0; not explicitly pinned. Check supported Node engines before moving npm majors. |
| Python | Replit `python-base-3.13` only | Latest stable 3.14.7. No `.py`, pip manifest, Python build step, or Python runtime in the application. Retain or remove/update tooling deliberately after checking Replit usage. |
| Replit / Nix | `web`, `nodejs-20`, `python-base-3.13`; channel `stable-25_05` | Platform-managed module/channel identifiers, not upstream Nix versions. Exact Nix executable and newest Replit-supported channel unverified. [Configuration reference](https://docs.replit.com/features/project-setup/configuration). Do not infer an available Replit module from an upstream release. |
| Git / Git LFS | Local Git 2.55.0.windows.5 and LFS 3.7.1; media patterns in `.gitattributes` | Git for Windows 2.55.0 base; LFS 3.8.0. Host tooling, not shipped site dependencies; review packaging revisions separately. |
| GitHub Actions / Pages | checkout v4, setup-node v4, upload-pages-artifact v3, deploy-pages v4 | Latest releases 7.0.1, 7.0.0, 5.0.0, 5.0.1 respectively. Dependabot proposes workflow updates. Pages is hosted and has no project-controlled service version. |
| Ubuntu runner | `ubuntu-latest` | GitHub-managed moving image; exact OS/tool image requires a run's setup log. [Runner images](https://github.com/actions/runner-images). |
| JSON, YAML, TOML, Markdown | npm/lock files, Actions, `.replit`, documentation | Configuration/document formats, not separately installed runtime libraries. |

Transitive build tooling includes Rollup 4.63.4, esbuild 0.21.5, PostCSS 8.5.28, nanoid 3.3.19, picocolors 1.1.1, source-map-js 1.2.1, fsevents 2.3.3, ESTree types 1.0.9, an optional lzma binary, and all esbuild/Rollup platform binaries. The generated table enumerates them individually. Type declarations inside a dependency do not make this a TypeScript application. Some optional binaries are locked but are not installed on Windows.

**Absent:** TypeScript application/compiler, Tailwind, React, Next.js, Python application, database, backend server, container build, and an existing automated browser-test framework. Vite's internal CSS processing does not establish a Tailwind installation. Editors, ChatGPT, and the Replit agent are authoring tools; their installed app/model versions are not established by repository source and are not application dependencies.

## Update mechanism

1. `.github/dependabot.yml` checks npm and GitHub Actions weekly and proposes version/lockfile updates as pull requests. This includes major updates; Three.js 0.x minor changes deserve breaking-change review. Transitive constraints are resolved through the parent dependency, not arbitrary overrides. See [Dependabot version updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-version-updates).
2. `validate.yml` builds every PR on Node 20 (existing deployment) and Node 24 (migration target) using `npm ci`. Deployment now also uses `npm ci` so it builds the reviewed lockfile. Once Node migration is complete, remove Node 20 from the matrix and update deployment and Replit together.
3. `technology-freshness.yml` checks official npm registries, Node releases, Python downloads, and GitHub release endpoints every Monday and on demand. It publishes the complete table in the run summary. Exit 0 means no detected drift, 1 means a lookup failed, and 2 means update candidates exist. GitHub failure notifications depend on the owner's notification settings. This is an alert/report, not an automatic deployment.
4. Run `npm run technology:report` to refresh the local Markdown/JSON inventory, or `npm run technology:check` to enforce freshness. No package installation is required for the checker itself; Node 20+ supplies its standard APIs. Reports carry a UTC timestamp and reflect the executing host, so CI host npm/LFS measurements will differ from Windows. Unknown source lookups fail visibly. Major-only declarations cannot establish exact patch versions.
5. Monthly, inspect the Replit-supported modules/channel, runner image, browser support and fonts. Apply supported runtime changes on a branch, verify actual `node --version`, `npm --version`, and (if retained) `python --version` in Replit, then update the declarations and report. Dependabot does not update Replit modules, Node declarations, host software, fonts, or browser APIs. These remain explicit maintenance work.

## Initial migration sequence and acceptance

First move CI/deployment and Replit to supported Node 24 LTS, after verifying Replit offers that module. Then upgrade Vite following each major's migration guide and regenerate the lockfile; update Three.js in a separate change with its migration guide. Upgrade Actions through their release notes, respecting runner requirements. Evaluate Python tooling separately because the site does not depend on it. Use `npm ci`, `npm run build`, and review `npm audit` advisories on each candidate.

For Three.js/Vite upgrades, verify rotation, zoom, all anatomy markers, chest opening, resize/mobile layout, console errors, and opt-in audio. Check both the illustrated no-WebGL fallback and a real WebGL2 scene: the repository's `.agents/memory/webgl-preview.md` records why Replit screenshots alone cannot validate 3D. A successful bundle is necessary but does not establish visual/audio equivalence. Merge only after these checks; the existing main-branch workflow then deploys. Recover regressions by reverting the upgrade commit and redeploying the previous lockfile.

## Activation and evidence limits

Local validation: `npm ci` and `npm run build` passed on Node 24.11.1 / npm 11.6.2; checker syntax and `git diff --check` passed. The live freshness run produced 77 records, 68 candidate rows (including repeated workflow references and platform binaries), zero lookup failures, and the expected exit code 2. These are not 68 independent application technologies. GitHub workflow execution and Node 20 matrix execution are not yet verified.

`npm audit` reported two vulnerable packages: Vite (high) and its esbuild dependency (moderate). The report identifies Vite 8.3.1 as its proposed major-version fix. These are development/build-tool findings, not evidence of compromise of the static Pages site. Prioritize the Node/Vite migration above. Advisories: [esbuild development server](https://github.com/advisories/GHSA-67mh-4wv8-2f99), [Vite source-map traversal](https://github.com/advisories/GHSA-4w7w-66w2-5vf9), [Windows UNC handling](https://github.com/advisories/GHSA-v6wh-96g9-6wx3), and [Windows deny bypass](https://github.com/advisories/GHSA-fx2h-pf6j-xcff). No force-fix was applied.

Weekly schedules and Dependabot become active when this configuration reaches GitHub's default branch, subject to repository settings. Build checks are not automatically required branch rules. The plan uses reviewed updates, not blind auto-merging. The follow-up synchronization integrates this audit with the Replit work through `35c15da`; no application dependency upgrade is included.

The GitHub connector confirmed the original source commit. The separate Replit connector requested reauthentication. During follow-up synchronization, the authenticated Replit browser Shell successfully fetched GitHub and proved clean `main` at `35c15da`, with `0/0` divergence; refreshing the stale Git panel cleared its incorrect three-unpushed-commit count. This does not repair the separate connector authentication. Nix/channel availability, hosted font revisions, and actual browser/runner versions remain explicit unknowns rather than invented versions.
