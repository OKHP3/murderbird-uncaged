const fs = require("node:fs");
const path = require("node:path");
const {
  web,
  output,
  digest: sha,
  manifest,
  serve,
  launch,
} = require("./common.cjs");
const result = {
  source: {
    hostedScriptSHA256: sha(path.join(web, "assets/study.js")),
    portableSha256: manifest.portable.sha256,
    startedUTC: new Date().toISOString(),
  },
};
const server = serve({
  fixture: (_mode, name) =>
    name === "assets/bird.pack" ? { delayMs: 1700 } : {},
});
(async () => {
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  try {
    for (const mode of ["disabled", "midflight", "contextLoss"]) {
      const b = await launch("chromium", [], mode === "disabled");
      try {
        const p = await b.newPage({ viewport: { width: 390, height: 844 } }),
          errors = [];
        p.on("pageerror", (e) => errors.push(String(e)));
        await p.goto("http://127.0.0.1:" + server.address().port + "/");
        const pending = p.waitForRequest(
          (r) => r.url().endsWith("/bird.pack"),
          { timeout: 20000 },
        );
        if (mode === "disabled") pending.catch(() => {});
        await p.locator("#load").click();
        if (mode !== "disabled") {
          await pending;
          if (mode === "contextLoss")
            await p.waitForFunction(
              () => murderBirdStudy.snapshot().ready,
              null,
              { timeout: 20000 },
            );
          await p
            .locator("#canvas")
            .evaluate((c) =>
              c
                .getContext("webgl2")
                .getExtension("WEBGL_lose_context")
                .loseContext(),
            );
        }
        await p.waitForTimeout(mode === "midflight" ? 3800 : 400);
        result[mode] = await p.evaluate(() => ({
          ready: murderBirdStudy.snapshot().ready,
          busy: murderBirdStudy.snapshot().busy,
          fallback: !document.getElementById("poster").hidden,
          status: document.getElementById("load-status").textContent,
          guideOpen: document.getElementById("guide").open,
          posterBytesDecoded:
            document.getElementById("poster").naturalWidth > 0,
          guideImageDecoded:
            document.getElementById("guide-image").naturalWidth > 0,
          canvasVisible: !document.querySelector("canvas").hidden,
          windowWidth: innerWidth,
          contentWidth: document.documentElement.scrollWidth,
        }));
        result[mode].errors = errors;
      } finally {
        await b.close();
      }
    }
    result.source.endHostedScriptSHA256 = sha(
      path.join(web, "assets/study.js"),
    );
    console.log(result);
    fs.writeFileSync(
      path.join(output, "failure-checks.json"),
      JSON.stringify(result, null, 2) + "\n",
    );
  } finally {
    server.close();
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
  server.close();
});
