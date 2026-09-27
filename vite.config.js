import { defineConfig } from 'vite';
import { createReadStream } from 'node:fs';
import { realpath, stat } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

// Explicit, loopback-only audition. Production sessions are never Vite assets.
function localThemePreview() {
  const routes = new Map([
    ['/__theme-preview/full.wav', fileURLToPath(new URL('./.local/theme-production/masters/iron-verdict-full.wav', import.meta.url))],
    ['/__theme-preview/loop.wav', fileURLToPath(new URL('./.local/theme-production/masters/iron-verdict-loop.wav', import.meta.url))],
  ]);
  return {
    name: 'local-theme-preview',
    apply: 'serve',
    configureServer(server) {
      if (!['127.0.0.1', 'localhost', '::1'].includes(server.config.server.host)) {
        throw new Error('Local theme preview requires a loopback host. Use --host 127.0.0.1.');
      }
      server.middlewares.use(async (request, response, next) => {
        const requestPath = request.url?.split('?')[0];
        if (!requestPath?.startsWith('/__theme-preview/')) return next();
        const address = request.socket.remoteAddress;
        const host = request.headers.host ?? '';
        const localHost = /^(localhost|127\.0\.0\.1|\[::1\])(?::\d+)?$/.test(host);
        const localAddress = ['127.0.0.1', '::1', '::ffff:127.0.0.1'].includes(address);
        const origin = request.headers.origin;
        const fetchSite = request.headers['sec-fetch-site'];
        const sameOrigin = !origin || origin === `http://${host}`;
        if (!localHost || !localAddress || !sameOrigin || (fetchSite && !['same-origin', 'none'].includes(fetchSite))) {
          response.writeHead(403).end('Local preview only.');
          return;
        }
        const file = routes.get(requestPath);
        if (!file) return response.writeHead(404).end('Unknown preview track.');
        if (!['GET', 'HEAD'].includes(request.method)) return response.writeHead(405, { Allow: 'GET, HEAD' }).end();
        try {
          // Never follow a substituted symlink out of the selected masters path.
          if (await realpath(file) !== file) return response.writeHead(403).end('Preview master must be a regular local file.');
          const info = await stat(file);
          if (!info.isFile()) return response.writeHead(404).end('Preview master is unavailable.');
          response.writeHead(200, {
            'Content-Type': 'audio/wav',
            'Content-Length': info.size,
            'Cache-Control': 'no-store',
            'Cross-Origin-Resource-Policy': 'same-origin',
            'X-Content-Type-Options': 'nosniff',
          });
          if (request.method === 'HEAD') return response.end();
          const stream = createReadStream(file);
          stream.on('error', () => response.destroy());
          response.on('close', () => stream.destroy());
          stream.pipe(response);
        } catch {
          response.writeHead(404, { 'Cache-Control': 'no-store' }).end('Preview master is not available yet.');
        }
      });
    },
  };
}

export default defineConfig(({ command, isPreview }) => {
  const localPreview = command === 'serve' && !isPreview && process.env.MURDERBIRD_THEME_PREVIEW === '1';
  return {
    base: './',
    define: { __LOCAL_THEME_PREVIEW__: JSON.stringify(localPreview) },
    plugins: localPreview ? [localThemePreview()] : [],
    server: {
      host: localPreview ? '127.0.0.1' : '0.0.0.0',
      allowedHosts: localPreview ? ['localhost', '127.0.0.1'] : true,
      cors: localPreview ? false : undefined,
      fs: { deny: ['.env', '.env.*', '*.{crt,pem}', '**/.git/**', '**/.local/**', '**/provenance/**'] },
    },
  };
});
