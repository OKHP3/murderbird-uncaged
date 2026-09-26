import { readFile, readdir, writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';

const root = new URL('../', import.meta.url);
const read = (path) => readFile(new URL(path, root), 'utf8');
const stable = (v) => /^v?\d+\.\d+\.\d+$/.test(v);
const parts = (v) => v.replace(/^v/, '').split('.').map(Number);
const compare = (a, b) => { const x = parts(a), y = parts(b); for (let i = 0; i < 3; i++) { if (x[i] !== y[i]) return x[i] - y[i]; } return 0; };
const rows = [];
async function fetchData(url, json = true) {
  const headers = { 'User-Agent': 'murderbird-technology-audit' };
  if (url.startsWith('https://api.github.com/') && process.env.GITHUB_TOKEN) headers.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;
  const response = await fetch(url, { headers, signal: AbortSignal.timeout(30000) });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return json ? response.json() : response.text();
}
async function record(name, current, source, lookup, scope) {
  try {
    const latest = await lookup();
    if (!stable(latest)) throw new Error('No stable semantic version returned');
    const normalized = current.replace(/^v/, '');
    const status = stable(current) ? (compare(latest, current) > 0 ? 'update available' : compare(latest, current) < 0 ? 'ahead of upstream latest' : 'current') : latest.replace(/^v/, '').startsWith(`${normalized}.`) ? 'same line; exact patch unknown' : 'review declared line';
    rows.push({ name, current, latest, status, scope, source });
  } catch (error) { rows.push({ name, current, latest: 'unknown', status: `lookup failed: ${error.message}`, scope, source }); }
}
const lock = JSON.parse(await read('package-lock.json'));
const pkg = JSON.parse(await read('package.json'));
const direct = { ...pkg.dependencies, ...pkg.devDependencies };
const entries = Object.entries(lock.packages).filter(([path]) => path);
// Include optional binaries for every platform and nested versions, not just this host.
for (let i = 0; i < entries.length; i += 6) {
  await Promise.all(entries.slice(i, i + 6).map(async ([path, info]) => {
    const name = path.split('node_modules/').at(-1);
    const source = `https://registry.npmjs.org/${encodeURIComponent(name)}/latest`;
    await record(name, info.version, source, async () => (await fetchData(source)).version,
      direct[name] ? `direct (${direct[name]})` : `transitive${info.optional ? ', optional' : ''}; ${path}`);
  }));
}
const replit = await read('.replit');
const nodeSource = 'https://nodejs.org/dist/index.json';
let nodeReleases;
const getNodes = async () => nodeReleases ??= await fetchData(nodeSource);
await record('Node.js (Replit declaration)', replit.match(/nodejs-(\d+)/)?.[1] ?? 'unknown', nodeSource,
  async () => (await getNodes()).filter(r => r.lts && stable(r.version)).sort((a,b) => compare(b.version,a.version))[0].version, 'latest LTS target; hosted patch unverified');
await record('Node.js (local audit host)', process.versions.node, nodeSource,
  async () => (await getNodes()).filter(r => stable(r.version)).sort((a,b) => compare(b.version,a.version))[0].version, 'latest stable Current; prefer LTS for production');
const npmSource = 'https://registry.npmjs.org/npm/latest';
await record('npm (audit host)', process.env.npm_config_user_agent?.match(/npm\/([^ ]+)/)?.[1] ?? 'unknown', npmSource, async () => (await fetchData(npmSource)).version, 'not pinned by project');
for (const file of await readdir(new URL('.github/workflows/', root))) {
  const content = await read(`.github/workflows/${file}`);
  for (const match of content.matchAll(/uses:\s*([\w.-]+\/[\w.-]+)@(v[\d.]+)/g)) {
    const source = `https://api.github.com/repos/${match[1]}/releases/latest`;
    await record(match[1], match[2], source, async () => (await fetchData(source)).tag_name, file);
  }
  const versions = [...content.matchAll(/node-version:\s*['"]?(\d+(?:\.\d+){0,2})/g)].map(m => m[1]);
  if (content.includes('matrix.node')) versions.push(...(content.match(/node:\s*\[([^\]]+)\]/)?.[1] ?? '').split(',').map(v => v.trim()).filter(Boolean));
  for (const version of versions) {
    await record(`Node.js (CI: ${file})`, version, nodeSource, async () => (await getNodes()).filter(r => r.lts && stable(r.version)).sort((a,b) => compare(b.version,a.version))[0].version, 'latest LTS target');
  }
}
const pythonSource = 'https://www.python.org/downloads/';
await record('Python (Replit tooling only)', replit.match(/python-base-([\d.]+)/)?.[1] ?? 'not declared', pythonSource, async () => {
  const html = await fetchData(pythonSource, false);
  const versions = [...html.matchAll(/(?:Download Python|Latest Python 3 Release - Python)\s+(\d+\.\d+\.\d+)(?![\w.])/g)].map(m => m[1]);
  if (!versions.length) throw new Error('Stable download marker missing');
  return versions.sort((a,b) => compare(b,a))[0];
}, 'no Python source or dependency manifest');
for (const [name, repo, command, args, regex] of [
  ['Git for Windows', 'git-for-windows/git', 'git', ['--version'], /([\d]+\.[\d]+\.[\d]+(?:\.windows\.\d+)?)/],
  ['Git LFS', 'git-lfs/git-lfs', 'git', ['lfs', 'version'], /git-lfs\/([\d.]+)/],
]) {
  if (name === 'Git for Windows' && process.platform !== 'win32') continue;
  const source = `https://api.github.com/repos/${repo}/releases/latest`;
  let current = 'unavailable';
  try { current = execFileSync(command, args, { encoding: 'utf8' }).match(regex)?.[1] ?? current; } catch {}
  const packaging = current;
  current = current.replace(/\.windows\.\d+$/, '');
  await record(name, current, source, async () => (await fetchData(source)).tag_name.replace(/\.windows\.\d+$/, ''), `audit host tooling (${packaging}); Windows packaging revisions require manual review`);
}
rows.sort((a,b) => a.name.localeCompare(b.name) || a.current.localeCompare(b.current));
const result = { checkedAt: new Date().toISOString(), rows };
const escape = (s) => String(s).replaceAll('|', '\\|').replaceAll('\n', ' ');
const markdown = `# Technology version snapshot\n\nChecked: ${result.checkedAt}. Generated from the committed manifests and official registries.\n\nLatest means the publisher's stable/latest channel; transitive updates must be resolved through their parent packages. Host versions are measurements of the machine running this report.\n\n| Technology | In place | Latest stable / target | Status | Scope | Source |\n|---|---|---|---|---|---|\n${rows.map(r => `| ${[r.name,r.current,r.latest,r.status,r.scope].map(escape).join(' | ')} | [upstream](${r.source}) |`).join('\n')}\n`;
await writeFile(new URL('docs/technology-versions.json', root), JSON.stringify(result, null, 2) + '\n');
await writeFile(new URL('docs/technology-versions.md', root), markdown);
console.log(`${rows.length} records; ${rows.filter(r => r.status === 'update available' || r.status === 'review declared line').length} update candidates; ${rows.filter(r => r.latest === 'unknown').length} lookup failures.`);
if (rows.some(r => r.latest === 'unknown')) process.exitCode = 1;
else if (process.argv.includes('--check') && rows.some(r => ['update available', 'review declared line'].includes(r.status))) process.exitCode = 2;
