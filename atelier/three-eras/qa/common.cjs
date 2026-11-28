const fs = require("node:fs");
const http = require("node:http");
const path = require("node:path");
const { createHash } = require("node:crypto");
const pw = require("playwright");

const app = fs.realpathSync(
  process.env.MB_QA_APP || path.join(__dirname, ".."),
);
const web = fs.realpathSync(path.join(app, "web"));
if (web !== path.join(app, "web"))
  throw new Error(
    "The web directory must resolve inside the selected application",
  );
const portable = path.join(app, "MurderBird-Three-Eras.html");
const manifest = JSON.parse(fs.readFileSync(path.join(app, "manifest.json")));
const output = path.join(__dirname, ".results");
const digest = (file) =>
  createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function launch(name = "chromium", extra = [], disabled = false) {
  const engine = {
    chromium: pw.chromium,
    chrome: pw.chromium,
    edge: pw.chromium,
    firefox: pw.firefox,
    webkit: pw.webkit,
  }[name];
  if (!engine) throw new Error("Unknown browser " + name);
  const executablePath = process.env["MB_QA_" + name.toUpperCase() + "_PATH"];
  const channel = executablePath
    ? undefined
    : { chromium: "chromium", chrome: "chrome", edge: "msedge" }[name];
  const gpu =
    process.platform === "darwin"
      ? ["--use-gl=angle", "--use-angle=metal"]
      : ["--enable-gpu"];
  const args =
    engine === pw.chromium
      ? [
          ...(disabled ? ["--disable-webgl", "--disable-gpu"] : gpu),
          "--disable-background-networking",
          ...extra,
        ]
      : [];
  return engine.launch({ headless: true, channel, executablePath, args });
}

const types = {
  ".html": "text/html",
  ".css": "text/css",
  ".js": "text/javascript",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".mp3": "audio/mpeg",
  ".mp4": "video/mp4",
  ".glb": "model/gltf-binary",
  ".webmanifest": "application/manifest+json",
};

function confinedFile(relativeName) {
  let file;
  try {
    file = fs.realpathSync(path.resolve(web, relativeName));
  } catch {
    return null;
  }
  const relative = path.relative(web, file);
  return relative &&
    !relative.startsWith(".." + path.sep) &&
    relative !== ".." &&
    !path.isAbsolute(relative) &&
    fs.statSync(file).isFile()
    ? file
    : null;
}

// Fixtures may delay, throttle or fail named files. All successful responses
// still read from the resolved web/ tree, including when symlinks are present.
function serve({
  withModes = false,
  cache = false,
  fixture = () => ({}),
} = {}) {
  const server = http.createServer(async (req, res) => {
    try {
      if (
        req.method !== "GET" ||
        req.headers.host !== "127.0.0.1:" + server.address().port
      ) {
        res.writeHead(403).end();
        return;
      }
      const url = new URL(req.url, "http://127.0.0.1");
      const parts = decodeURIComponent(url.pathname).split("/").filter(Boolean);
      const mode = withModes ? parts.shift() || "fast" : "";
      const relativeName = parts.join("/") || "index.html";
      const file = confinedFile(relativeName);
      const effect = fixture(mode, relativeName);
      if (!file || effect.missing) {
        res.writeHead(404).end("missing");
        return;
      }
      res.setHeader("Content-Length", fs.statSync(file).size);
      res.setHeader(
        "Content-Type",
        types[path.extname(file)] || "application/octet-stream",
      );
      res.setHeader(
        "Cache-Control",
        cache && !file.endsWith(".html") ? "public, max-age=600" : "no-store",
      );
      if (effect.delayMs) await delay(effect.delayMs);
      if (res.destroyed) return;
      const stream = fs.createReadStream(file, {
        highWaterMark: effect.chunkBytes || 65536,
      });
      res.on("close", () => stream.destroy());
      if (effect.chunkDelayMs) {
        for await (const chunk of stream) {
          if (res.destroyed) return;
          res.write(chunk);
          await delay(effect.chunkDelayMs);
        }
        res.end();
      } else {
        stream.on("error", () => res.destroy());
        stream.pipe(res);
      }
    } catch {
      if (!res.headersSent && !res.destroyed) res.writeHead(400);
      if (!res.destroyed) res.end();
    }
  });
  return server;
}

fs.mkdirSync(output, { recursive: true });
module.exports = {
  app,
  web,
  portable,
  manifest,
  output,
  digest,
  delay,
  launch,
  serve,
};
