const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const assert = require("node:assert/strict");
const { pathToFileURL } = require("node:url");
const { createHash } = crypto;
const { portable, output: resultDir, launch } = require("./common.cjs");
const output = path.join(resultDir, "gpu.json");
async function run() {
  const browser = await launch();
  const result = {
    portable: createHash("sha256")
      .update(fs.readFileSync(portable))
      .digest("hex"),
    browser: browser.version(),
    trials: [],
  };
  try {
    for (const failure of [false, true]) {
      const page = await browser.newPage({
        viewport: { width: 1000, height: 860 },
      });
      const log = [];
      page.on("pageerror", (e) => log.push("page error " + String(e)));
      page.on("console", (m) => {
        if (/INVALID_|WebGL warning|GL_INVALID|GL_OUT_OF_MEMORY/.test(m.text()))
          log.push(m.text());
      });
      await page.addInitScript(
        ({ failure }) => {
          const P = WebGL2RenderingContext.prototype,
            gpu = {
              sizes: new Map(),
              big: new Set(),
              uploads: [],
              injected: 0,
              gl: null,
              fail: failure,
            };
          window.qaGPU = gpu;
          const storage = P.texStorage2D,
            upload = P.texSubImage2D,
            getError = P.getError;
          P.texStorage2D = function (target, levels, format, width, height) {
            const res = storage.apply(this, arguments);
            if (target === this.TEXTURE_2D) {
              const texture = this.getParameter(this.TEXTURE_BINDING_2D);
              gpu.sizes.set(texture, [width, height, levels]);
              if (width === 768 && gpu.fail) {
                gpu.fail = false;
                gpu.pending = true;
                gpu.injected++;
              }
            }
            return res;
          };
          P.texSubImage2D = function (target, level, x, y, ...tail) {
            const r = upload.apply(this, arguments),
              src = tail[tail.length - 1],
              w = src?.width || (tail.length >= 5 ? tail[0] : 0);
            if (target === this.TEXTURE_2D && level === 0 && w === 768) {
              gpu.gl = this;
              const t = this.getParameter(this.TEXTURE_BINDING_2D);
              gpu.big.add(t);
              gpu.uploads.push(gpu.sizes.get(t) || null);
            }
            return r;
          };
          P.getError = function () {
            if (gpu.pending) {
              gpu.pending = false;
              return this.OUT_OF_MEMORY;
            }
            return getError.apply(this, arguments);
          };
        },
        { failure },
      );
      await page.goto(pathToFileURL(portable).href);
      await page.locator("#load").click();
      if (failure) {
        await page
          .getByRole("button", { name: "Retry full surfaces" })
          .waitFor({ timeout: 30000 });
        const pre = await page.evaluate(() => ({
          state: murderBirdStudy.snapshot().detail,
          ready: murderBirdStudy.snapshot().ready,
          errors: qaGPU.injected,
        }));
        assert.deepEqual(pre, { state: "first draw", ready: true, errors: 1 });
        await page.locator("#canvas").press("ArrowRight");
        await page.getByRole("button", { name: "Retry full surfaces" }).click();
      }
      await page.waitForFunction(
        () => window.murderBirdStudy?.snapshot().detail === "full",
        null,
        { timeout: 40000 },
      );
      await page.evaluate(
        () =>
          new Promise((resolve) =>
            requestAnimationFrame(() => requestAnimationFrame(resolve)),
          ),
      );
      const audit = await page.evaluate(() => {
        const g = qaGPU,
          gl = g.gl,
          renderer = gl.getParameter(
            gl.getExtension("WEBGL_debug_renderer_info")
              .UNMASKED_RENDERER_WEBGL,
          );
        const pending = [];
        for (let i = 0; i < 15; i++) {
          const e = gl.getError();
          if (!e) break;
          pending.push(e);
        }
        const old = gl.getParameter(gl.READ_FRAMEBUFFER_BINDING),
          fb = gl.createFramebuffer();
        const rows = [];
        try {
          gl.bindFramebuffer(gl.READ_FRAMEBUFFER, fb);
          for (const texture of g.big) {
            if (!gl.isTexture(texture)) continue;
            gl.framebufferTexture2D(
              gl.READ_FRAMEBUFFER,
              gl.COLOR_ATTACHMENT0,
              gl.TEXTURE_2D,
              texture,
              0,
            );
            const complete =
              gl.checkFramebufferStatus(gl.READ_FRAMEBUFFER) ===
              gl.FRAMEBUFFER_COMPLETE;
            const out = new Uint8Array(4 * 3);
            for (const [i, n] of [257, 515, 767].entries())
              gl.readPixels(
                n,
                n,
                1,
                1,
                gl.RGBA,
                gl.UNSIGNED_BYTE,
                out.subarray(i * 4, i * 4 + 4),
              );
            rows.push({
              alloc: g.sizes.get(texture),
              complete,
              pixels: Array.from(out),
              error: gl.getError(),
            });
          }
        } finally {
          gl.bindFramebuffer(gl.READ_FRAMEBUFFER, old);
          gl.deleteFramebuffer(fb);
        }
        return {
          renderer,
          firstDrawRejected: !!g.injected,
          uploads: g.uploads,
          preexistingErrors: pending,
          rows,
          stage: murderBirdStudy.snapshot().detail,
        };
      });
      result.trials.push({ failure, audit, log });
      {
        assert(audit.rows.length >= 26);
        assert(
          audit.rows.every(
            (r) =>
              r.alloc[0] === 768 &&
              r.alloc[1] === 768 &&
              r.complete &&
              r.error === 0 &&
              r.pixels.some((v, i) => i % 4 !== 3 && v > 0),
          ),
        );
        assert(audit.uploads.every((s) => s?.[0] === 768 && s?.[1] === 768));
        assert.equal(log.length, 0);
        assert.equal(audit.preexistingErrors.length, 0);
      }
      await page.close();
    }
  } finally {
    fs.writeFileSync(output, JSON.stringify(result, null, 2) + "\n");
    await browser.close();
  }
  console.log(
    result.trials.map((t) => ({
      renderer: t.audit.renderer,
      actual: t.audit.rows.length,
      first: t.audit.rows[0],
      injected: t.failure,
    })),
  );
}
run().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
