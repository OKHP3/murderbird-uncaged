/** Local QA evidence receiver. Never part of the exhibit or public build. */
import http from 'node:http';
import { mkdir, writeFile, readFile, realpath } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve, relative, isAbsolute, extname } from 'node:path';
import { homedir } from 'node:os';

const evidenceBase = resolve(homedir(), 'OKH-Local/01_ChatGPT_Exports/murderbird-uncaged/evidence/visual-technical-acceptance');
const session = process.argv[2] ?? '';
if (!['', 'connected-head-correction', 'optic-bill-refinement', 'tab-sliver-correction', 'bill-root-optic-gap-correction', 'root-optic-continuity'].includes(session)) throw new Error('Unknown acceptance session');
const correctionSession = ['optic-bill-refinement', 'tab-sliver-correction', 'bill-root-optic-gap-correction', 'root-optic-continuity'].includes(session);
const root = resolve(evidenceBase, correctionSession ? `connected-head-correction/${session}` : session);
await mkdir(root, { recursive: true });
const server = http.createServer(async (request, response) => {
  const origin = request.headers.origin;
  const allowed = ['http://127.0.0.1:4176', 'http://127.0.0.1:4177', 'http://127.0.0.1:5176'];
  if (origin && !allowed.includes(origin)) { response.writeHead(403).end(); return; }
  if (origin) response.setHeader('Access-Control-Allow-Origin', origin);
  if (request.method === 'GET') {
    const baseline = /^\/exact-normal-candidate\/(maker|mechanic|builder)\/murderbird-recursive-\1\.glb$/.test(request.url ?? '');
    const corrected = session === 'connected-head-correction'
      && /^\/attempt-01\/(maker|mechanic|builder)\/murderbird-recursive-\1\.glb$/.test(request.url ?? '');
    const refined = correctionSession
      && /^\/candidate\/(maker|mechanic|builder)\/murderbird-recursive-\1\.glb$/.test(request.url ?? '');
    const checkpoint = correctionSession
      && /^\/checkpoint\/(maker|mechanic|builder)\/murderbird-recursive-\1\.glb$/.test(request.url ?? '');
    const seatingRepair = session === 'tab-sliver-correction'
      && /^\/seating-repair\/(maker|mechanic|builder)\/murderbird-recursive-\1\.glb$/.test(request.url ?? '');
    const candidate = baseline || corrected || refined || checkpoint || seatingRepair;
    if (request.url !== '/review.html' && !candidate) { response.writeHead(404).end(); return; }
    try {
      const file = checkpoint
        ? resolve(evidenceBase, ['tab-sliver-correction', 'bill-root-optic-gap-correction', 'root-optic-continuity'].includes(session)
          ? 'connected-head-correction/optic-bill-refinement/candidate' : 'connected-head-correction/attempt-01',
          request.url.slice('/checkpoint/'.length))
        : resolve(baseline ? evidenceBase : root, request.url.slice(1));
      const body = await readFile(file);
      response.setHeader('Content-Type', candidate ? 'model/gltf-binary' : 'text/html; charset=utf-8');
      response.setHeader('Cache-Control', 'no-store');
      response.setHeader('Content-Length', body.length);
      response.end(body);
    } catch { response.writeHead(404).end(); }
    return;
  }
  if (!origin) { response.writeHead(403).end(); return; }
  response.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  response.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (request.method === 'OPTIONS') { response.writeHead(204).end(); return; }
  const name = request.url?.slice(1);
  if (request.method !== 'POST' || !/^[a-z0-9-]+\.(json|png)$/.test(name ?? '')) {
    response.writeHead(400).end(); return;
  }
  try {
    const chunks = []; let bytes = 0;
    for await (const chunk of request) {
      bytes += chunk.length;
      if (bytes > 8 * 1024 * 1024) throw new Error('Evidence exceeds 8 MiB');
      chunks.push(chunk);
    }
    const body = Buffer.concat(chunks);
    if (name.endsWith('.json')) JSON.parse(body.toString('utf8'));
    else if (!body.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]))) {
      throw new Error('Not PNG');
    }
    await writeFile(resolve(root, name), body, { flag: 'wx' });
    response.writeHead(201).end('Recorded');
  } catch (error) { response.writeHead(409).end(error.message); }
});
server.listen(4177, '127.0.0.1', () => console.log(`Evidence receiver: ${root}`));

// Serve the existing build directly; inject QA observation before app startup
// only on the explicitly requested local test route. No dist file is changed.
const buildRoot = await realpath(resolve('dist'));
const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript',
  '.css': 'text/css', '.json': 'application/json', '.glb': 'model/gltf-binary',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml' };
http.createServer(async (request, response) => {
  if (request.method !== 'GET') { response.writeHead(405).end(); return; }
  try {
    const url = new URL(request.url, 'http://127.0.0.1:4176');
    const name = url.pathname === '/' ? 'index.html' : decodeURIComponent(url.pathname).slice(1);
    const file = await realpath(resolve(buildRoot, name)), inside = relative(buildRoot, file);
    if (inside.startsWith('..') || isAbsolute(inside)) { response.writeHead(403).end(); return; }
    let body = await readFile(file);
    if (name === 'index.html' && url.searchParams.get('acceptance-probe') === '1') {
      const probe = await readFile(resolve('scripts/asus-browser-probe.js'), 'utf8');
      body = Buffer.from(body.toString('utf8').replace('<head>', `<head><script>${probe}</script>`));
      response.setHeader('X-Acceptance-Probe-Sha256', createHash('sha256').update(probe).digest('hex'));
    }
    response.setHeader('Cache-Control', 'no-store');
    response.setHeader('Content-Type', types[extname(file)] || 'application/octet-stream');
    response.setHeader('Content-Length', body.length);
    response.end(body);
  } catch { response.writeHead(404).end(); }
}).listen(4176, '127.0.0.1', () => console.log('Instrumented local build: http://127.0.0.1:4176/?acceptance-probe=1'));
