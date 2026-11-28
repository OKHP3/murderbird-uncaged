const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const {
  web: root,
  output,
  delay: sleep,
  serve,
  launch,
} = require("./common.cjs");
const server = serve({ cache: true });
let url, b;
const signed = () => ({
  bundle: crypto
    .createHash("sha256")
    .update(fs.readFileSync(path.resolve(root, "assets/study.js")))
    .digest("hex"),
  manifest: JSON.parse(fs.readFileSync(path.resolve(root, "../manifest.json")))
    .portable,
});
const results = {
  startUTC: new Date().toISOString(),
  source: signed(),
  workload:
    "Cold/warm pairs are sequential. Four focused headless contexts perform the dwell in parallel on the same host. A human cadence of 10 seconds between camera moves leaves the demand-rendered inspector idle between moves. All results describe this workload.",
};
async function start(ctx) {
  const page = await ctx.newPage();
  await page.goto(url);
  await page.locator("#load").click();
  await page.waitForFunction(
    () => window.murderBirdStudy?.snapshot().detail === "full",
    null,
    { timeout: 25000 },
  );
  return page;
}
const read = (p) =>
  p.evaluate(() => ({
    s: murderBirdStudy.snapshot(),
    visible: !document.hidden,
  }));
async function dwelling(era) {
  const ctx = await b.newContext({
    viewport: { width: 1152, height: 768 },
    reducedMotion: "reduce",
  });
  try {
    const p = await start(ctx);
    let results = { era, errors: [], samples: [] };
    p.on("pageerror", (e) => results.errors.push(String(e)));
    await p
      .locator('[data-era="' + (era === "idle" ? "maker" : era) + '"]')
      .click();
    const baseline = await read(p);
    if (era === "idle") {
      const t = Date.now();
      await sleep(60100);
      const after = await read(p);
      await p.locator("#canvas").press("ArrowRight");
      await p.locator("#canvas").press("+");
      const orbited = await read(p);
      return {
        ...results,
        elapsedMs: Date.now() - t,
        idlePoseUnchanged:
          JSON.stringify(baseline.s.joints) === JSON.stringify(after.s.joints),
        poseUnchangedAfterCamera:
          JSON.stringify(after.s.joints) === JSON.stringify(orbited.s.joints),
        autonomousCommandVisible: await p.locator("#approach").isVisible(),
        autonomousTime: after.s.time,
        playing: after.s.playing,
        muted: after.s.muted,
        documentVisible: after.visible,
      };
    }
    await p.locator("#open").click();
    await p.waitForFunction(() => murderBirdStudy.snapshot().open === 1);
    const t = Date.now();
    let n = 0;
    const startState = await read(p);
    while (Date.now() - t < 120000) {
      await sleep(Math.min(10000, Math.max(1, 120050 - (Date.now() - t))));
      n++;
      await p.locator("#canvas").press("Shift+ArrowRight");
      if (n === 4 || n === 8) await p.locator("#light").click();
      const snap = await read(p);
      results.samples.push({
        elapsedMs: Date.now() - t,
        ready: snap.s.ready,
        frame: snap.s.frames,
        open: snap.s.open,
        view: snap.s.view,
        azimuth: snap.s.azimuth,
        visible: snap.visible,
        intact:
          JSON.stringify(startState.s.joints) === JSON.stringify(snap.s.joints),
        matrixCount: Object.keys(snap.s.joints).length,
      });
    }
    const end = await read(p);
    await p.locator("#reset").click();
    const reseated = await read(p);
    return {
      ...results,
      elapsedMs: Date.now() - t,
      framesDrawn: end.s.frames - startState.s.frames,
      exactReset:
        JSON.stringify(baseline.s.joints) ===
          JSON.stringify(reseated.s.joints) && reseated.s.open === 0,
      fullDigest: reseated.s.modelDigest,
    };
  } finally {
    await ctx.close();
  }
}
async function cachePairs() {
  const rows = [];
  for (let i = 0; i < 3; i++) {
    const ctx = await b.newContext();
    try {
      for (const phase of ["cold", "warm"]) {
        const p = await ctx.newPage();
        await p.goto(url);
        const start = await p.evaluate(() => performance.now());
        await p.locator("#load").click();
        await p.waitForFunction(
          () => window.murderBirdStudy?.snapshot().detail === "full",
          null,
          { timeout: 30000, polling: 25 },
        );
        rows.push(
          await p.evaluate(
            ({ phase, start }) => ({
              phase,
              firstDrawMs: Math.round(
                murderBirdStudy.snapshot().readyAt - start,
              ),
              fullMs: Math.round(performance.now() - start),
              assets: performance
                .getEntriesByType("resource")
                .filter((r) => r.name.endsWith(".pack"))
                .map((r) => ({
                  key: r.name.split("/").at(-1),
                  transferBytes: r.transferSize,
                  decodedBytes: r.decodedBodySize,
                })),
            }),
            { phase, start },
          ),
        );
        await p.close();
      }
    } finally {
      await ctx.close();
    }
  }
  return rows;
}
(async () => {
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  url = "http://127.0.0.1:" + server.address().port + "/";
  try {
    b = await launch("chromium", [
      "--disable-background-timer-throttling",
      "--disable-backgrounding-occluded-windows",
    ]);
    results.version = b.version();
    results.cache = await cachePairs();
    results.dwell = await Promise.all(
      ["idle", "maker", "mechanic", "advanced"].map(async (era) => {
        try {
          return await dwelling(era);
        } catch (e) {
          return { era, failure: String(e) };
        }
      }),
    );
    results.finalSource = signed();
    fs.writeFileSync(
      path.join(output, "soak.json"),
      JSON.stringify(results, null, 2) + "\n",
    );
    console.log(
      results.dwell.map(
        ({ era, failure, elapsedMs, exactReset, idlePoseUnchanged }) => ({
          era,
          failure,
          elapsedMs,
          exactReset,
          idlePoseUnchanged,
        }),
      ),
    );
  } finally {
    await b?.close();
    server.close();
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
  server.close();
});
