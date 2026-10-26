/** Local QA evidence receiver. Never part of the exhibit or public build. */
import http from 'node:http';
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { homedir } from 'node:os';

const root = resolve(homedir(), 'OKH-Local/01_ChatGPT_Exports/murderbird-uncaged/evidence/visual-technical-acceptance');
await mkdir(root, { recursive: true });
const server = http.createServer(async (request, response) => {
  const origin = request.headers.origin;
  const allowed = ['http://127.0.0.1:4176', 'http://127.0.0.1:4177', 'http://127.0.0.1:5176'];
  if (origin && !allowed.includes(origin)) { response.writeHead(403).end(); return; }
  if (origin) response.setHeader('Access-Control-Allow-Origin', origin);
  if (request.method === 'GET') {
    const candidate = /^\/exact-normal-candidate\/(maker|mechanic|builder)\/murderbird-recursive-\1\.glb$/.test(request.url ?? '');
    if (request.url !== '/review.html' && !candidate) { response.writeHead(404).end(); return; }
    try {
      const body = await readFile(resolve(root, request.url.slice(1)));
      response.setHeader('Content-Type', candidate ? 'model/gltf-binary' : 'text/html; charset=utf-8');
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
