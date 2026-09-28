/** Loopback-only failure fixture for manual/Codex browser verification. */
import http from 'node:http';
import assert from 'node:assert/strict';

const upstream = new URL(process.env.UNCAGED_UPSTREAM || 'http://127.0.0.1:5183');
assert(['127.0.0.1', 'localhost'].includes(upstream.hostname) && upstream.protocol === 'http:');
const port = Number(process.env.UNCAGED_FIXTURE_PORT || 5184);
assert(Number.isInteger(port) && port > 1024 && port < 65536);
const events = [];
let modelRequests = 0;
function upstreamTarget(requestUrl) {
  const requested = new URL(requestUrl, upstream);
  const target = new URL(`${requested.pathname}${requested.search}`, upstream);
  assert.equal(target.origin, upstream.origin, 'fixture forwarding must remain on its configured loopback origin');
  return target;
}
const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://127.0.0.1');
  if (url.pathname === '/__qa/status') {
    res.writeHead(200, { 'content-type': 'application/json', 'cache-control': 'no-store' });
    res.end(JSON.stringify({ kind: 'controlled-local-failure-fixture', upstream: upstream.href, modelRequests, events }));
    return;
  }
  const fail = url.pathname.endsWith('.glb') ? ++modelRequests <= 2 : /\/maker-preview\.png$/.test(url.pathname);
  if (fail) {
    events.push({ at: new Date().toISOString(), path: url.pathname, status: 503, reason: url.pathname.endsWith('.glb') ? 'First two model requests fail; later retries pass' : 'Maker preview intentionally unavailable' });
    res.writeHead(503, { 'content-type': 'text/plain', 'cache-control': 'no-store' });
    res.end('Controlled local QA failure');
    return;
  }
  const outgoing = http.request(upstreamTarget(req.url), { method: req.method, headers: { ...req.headers, host: upstream.host } }, response => {
    res.writeHead(response.statusCode, { ...response.headers, 'cache-control': 'no-store' });
    response.pipe(res);
  });
  outgoing.on('error', error => { res.writeHead(502, { 'content-type': 'text/plain' }); res.end(`Local fixture upstream unavailable: ${error.message}`); });
  req.pipe(outgoing);
});
// Preserve the local development connection; no remote destination is accepted.
server.on('upgrade', (req, socket, head) => {
  const outgoing = http.request(upstreamTarget(req.url), { headers: { ...req.headers, host: upstream.host } });
  outgoing.on('upgrade', (response, upstreamSocket, upstreamHead) => {
    socket.write(`HTTP/1.1 ${response.statusCode} ${response.statusMessage}\r\n${Object.entries(response.headers).map(([key, value]) => `${key}: ${value}`).join('\r\n')}\r\n\r\n`);
    if (head.length) upstreamSocket.write(head);
    if (upstreamHead.length) socket.write(upstreamHead);
    upstreamSocket.pipe(socket); socket.pipe(upstreamSocket);
    socket.on('error', () => upstreamSocket.destroy());
    upstreamSocket.on('error', () => socket.destroy());
  });
  outgoing.on('error', () => socket.destroy()); outgoing.end();
});
server.listen(port, '127.0.0.1', () => console.log(`Local recovery fixture: http://127.0.0.1:${port}/`));
