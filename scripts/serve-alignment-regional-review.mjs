/** Isolated loopback review derivative; never changes the app's asset imports. */
import { createServer } from 'vite';
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { parseArgs } from 'node:util';

const { values } = parseArgs({ options: {
  model: { type: 'string' }, sha256: { type: 'string' },
  audit: { type: 'string' }, port: { type: 'string', default: '5182' }
} });
assert.ok(values.model && values.audit && /^[a-f0-9]{64}$/.test(values.sha256 || ''), 'Provide --model, --sha256 and --audit containing the three exact native render sets.');
const root = process.cwd();
const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const hashFile = async file => {
  const bytes = await fs.readFile(file);
  return { path: path.relative(root, file).split(path.sep).join('/'), sha256: digest(bytes), bytes: bytes.length };
};
async function sourceInventory(directory) {
  const result = [];
  for (const entry of await fs.readdir(directory, { withFileTypes: true })) {
    const file = path.join(directory, entry.name);
    if (entry.isDirectory()) result.push(...await sourceInventory(file));
    else if (/\.(?:js|css)$/.test(entry.name)) result.push(await hashFile(file));
  }
  return result.sort((a, b) => a.path.localeCompare(b.path));
}
const model = await fs.readFile(values.model);
assert.equal(digest(model), values.sha256, 'Model hash differs from the review identity.');
const importedModelPath = '/assets/models/uncaged-alignment-v4/murderbird-alignment-v4.glb';
const routes = new Map([[importedModelPath, { bytes: model, mime: 'model/gltf-binary', source: values.model, sha256: values.sha256, role: 'GLB request from unchanged application import', inputImportPath: importedModelPath }]]);
for (const era of ['maker', 'mechanic', 'builder']) {
  const directory = path.join(values.audit, `native-${era}`);
  const receipt = JSON.parse(await fs.readFile(path.join(directory, 'views.json'), 'utf8'));
  assert.equal(receipt.model.sha256, values.sha256, 'Preview belongs to another candidate.');
  const image = receipt.views.find(row => row.image === 'full-three-quarter.png');
  assert.ok(image);
  const source = path.join(directory, image.image);
  const bytes = await fs.readFile(source);
  assert.equal(digest(bytes), image.sha256, 'Preview changed after rendering.');
  const importPath = `/assets/models/uncaged-alignment-v4/${era}-preview.png`;
  routes.set(importPath, { bytes, mime: 'image/png', source, sha256: image.sha256, role: 'illustrated fallback image request from unchanged application import', inputImportPath: importPath, renderReceipt: path.join(directory, 'views.json') });
}
const applicationSourceFiles = await sourceInventory(path.join(root, 'src'));
applicationSourceFiles.push(await hashFile(path.join(root, 'index.html')));
applicationSourceFiles.push(await hashFile(path.join(root, 'vite.config.js')));
applicationSourceFiles.sort((a, b) => a.path.localeCompare(b.path));
const activeV4Model = await hashFile(path.join(root, 'assets/models/uncaged-alignment-v4/murderbird-alignment-v4.glb'));
const activeV4Fallbacks = [];
for (const era of ['maker', 'mechanic', 'builder']) activeV4Fallbacks.push(await hashFile(path.join(root, `assets/models/uncaged-alignment-v4/${era}-preview.png`)));
const identity = {
  status: 'local regional review; revision required',
  model: values.model, sha256: values.sha256, bytes: model.length,
  scope: 'The app source imports remain unchanged. At those request paths, this local server explicitly overrides response bytes in memory with the review GLB and native illustrated previews. Native preview images omit runtime-generated mechanisms.',
  activeApplicationAssetUnchanged: true,
  applicationSourceFiles,
  activeApplicationAssets: { v4Model: activeV4Model, v4Fallbacks: activeV4Fallbacks,
    meaning: 'Exact unchanged V4 files present at review-server startup; request responses at these imported paths are separately overridden as listed below.' },
  analytics: 'Google Tag Manager loader removed from review HTML only',
  routes: [...routes].map(([url, row]) => ({ url, inputImportPath: row.inputImportPath, overrideMode: 'in-memory response override', role: row.role, source: row.source, sha256: row.sha256, bytes: row.bytes.length, ...(row.renderReceipt ? { renderReceipt: row.renderReceipt } : {}) }))
};
const server = await createServer({ root, server: {
  host: '127.0.0.1', port: Number(values.port), strictPort: true, allowedHosts: ['127.0.0.1', 'localhost'], cors: false
}, plugins: [{
  name: 'local-regional-review-only', apply: 'serve',
  transformIndexHtml(html) {
    return html.replace(/<script\b[^>]*src="https:\/\/www\.googletagmanager\.com\/[^\"]*"[^>]*><\/script>/g, '')
      .replace('<title>', '<title>Local regional review · ')
      .replace('<body>', '<body><aside style="background:#fff3d7;color:#292f2b;padding:8px 4%;font:13px/1.5 system-ui">Local regional geometry review · revision required · <a href="/assets/audit/alignment-v5-regional/index.html">comparison gallery</a> · <a href="/__regional-review">exact review identity</a></aside>');
  },
  configureServer(vite) {
    vite.middlewares.use((request, response, next) => {
      const pathname = request.url?.split('?')[0];
      if (pathname === '/__regional-review') {
        response.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
        return response.end(JSON.stringify(identity, null, 2));
      }
      const row = routes.get(pathname);
      if (!row) return next();
      if (!['GET', 'HEAD'].includes(request.method)) return response.writeHead(405).end();
      response.writeHead(200, { 'Content-Type': row.mime, 'Content-Length': row.bytes.length, 'Cache-Control': 'no-store', 'X-Regional-Review-SHA256': row.sha256 });
      response.end(request.method === 'HEAD' ? undefined : row.bytes);
    });
  }
}] });
await server.listen();
console.log(JSON.stringify({ url: `http://127.0.0.1:${values.port}/`, identity }, null, 2));
for (const signal of ['SIGTERM', 'SIGINT']) process.once(signal, async () => { await server.close(); process.exit(0); });
