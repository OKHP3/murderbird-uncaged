const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");

const { pathToFileURL } = require("node:url");
const {
  web: base,
  portable,
  output,
  digest,
  manifest,
  serve,
  launch,
} = require("./common.cjs");
const result = {
  started: new Date().toISOString(),
  transferBytes: fs.statSync(path.join(base, "assets/bird.pack")).size,
  transferSHA256: digest(path.join(base, "assets/bird.pack")),
  runs: [],
  detailTier: manifest["detail.pack"],
  portable: { bytes: fs.statSync(portable).size, sha256: digest(portable) },
  hostedScriptSHA256: digest(path.join(base, "assets/study.js")),
};
assert.deepEqual(result.portable, manifest.portable);
const resetSave = () =>
  fs.writeFileSync(
    path.join(output, "runtime-checks.json"),
    JSON.stringify(result, null, 2) + "\n",
  );
let flakyCount = 0,
  flakyDetailCount = 0;
const server = serve({
  withModes: true,
  fixture(mode, rel) {
    if (mode === "retrydetail" && rel === "assets/detail.pack")
      return { missing: flakyDetailCount++ === 0 };
    if (mode === "retry" && rel === "assets/bird.pack")
      return { missing: flakyCount++ === 0 };
    if (mode === "fail" && rel === "assets/bird.pack") return { missing: true };
    if (
      mode === "slow" &&
      ["assets/bird.pack", "assets/detail.pack"].includes(rel)
    )
      return { delayMs: 120, chunkBytes: 250000, chunkDelayMs: 50 };
    return {};
  },
});
let url;
async function run(browser, name, mode, details) {
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    reducedMotion: "reduce",
    offline: mode === "portable",
  });
  const page = await context.newPage();
  page.setDefaultTimeout(12000);
  const errors = [],
    requests = [],
    missing = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("request", (r) => {
    if (r.url().startsWith("http")) requests.push(new URL(r.url()).pathname);
  });
  page.on("response", (r) => {
    if (r.status() >= 400)
      missing.push({ name: new URL(r.url()).pathname, status: r.status() });
  });
  const row = { name, engineVersion: browser.version(), mode, errors, missing };
  result.runs.push(row);
  try {
    const address =
      mode === "portable"
        ? pathToFileURL(portable).href
        : url + "/" + mode + "/";
    const w = Date.now();
    await page.goto(address, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForFunction(() => window.murderBirdStudy);
    await page.waitForTimeout(100);
    row.firstUIWallMs = Date.now() - w;
    row.payload = JSON.parse(
      fs.readFileSync(path.resolve(base, "../manifest.json")),
    )["bird.pack"];
    row.preEntryRequests = [...requests];
    row.preEntryTransferredBytes = await page.evaluate(
      () =>
        performance
          .getEntriesByType("resource")
          .reduce((sum, e) => sum + (e.encodedBodySize || 0), 0) +
        (performance.getEntriesByType("navigation")[0]?.encodedBodySize || 0),
    );
    row.entryName = await page
      .getByRole("button", { name: "Enter 3D exhibit" })
      .textContent();
    const state = () => page.evaluate(() => murderBirdStudy.snapshot());
    const start = await page.evaluate(() => performance.now());
    await page.locator("#load").focus();
    await page.keyboard.press("Enter");
    await page.waitForFunction(
      () =>
        murderBirdStudy.snapshot().ready ||
        document.getElementById("load").textContent.includes("Retry"),
      null,
      { timeout: 75000 },
    );
    const ready = await state();
    row.ready = ready.ready;
    row.focusAfterLoad = await page.evaluate(
      () => document.activeElement.id || document.activeElement.tagName,
    );
    row.status = await page.locator("#load-status").textContent();
    row.optInToReadyMs = ready.ready ? Math.round(ready.readyAt - start) : null;
    if (!ready.ready) {
      row.fallback = {
        walkthroughOpen: await page.locator("#guide").evaluate((x) => x.open),
        poster: await page
          .locator("#poster")
          .evaluate((x) => x.complete && x.naturalWidth > 0),
        guide: await page
          .locator("#guide-image")
          .evaluate((x) => x.complete && x.naturalWidth > 0),
      };
      if (mode === "retry") {
        await page.getByRole("button", { name: "Retry 3D" }).click();
        try {
          await page.waitForFunction(
            () => window.murderBirdStudy?.snapshot()?.ready,
            null,
            { timeout: 8000 },
          );
          row.retrySingleActionRecovered = true;
        } catch {
          row.retrySingleActionRecovered = false;
        }
      }
      return;
    }
    row.initialStationary =
      ready.playing === false && ready.time === 0 && ready.muted === true;
    if (mode === "retrydetail") {
      await page.waitForFunction(
        () =>
          document.getElementById("surface")?.textContent ===
            "Retry full surfaces" && !document.getElementById("surface").hidden,
        null,
        { timeout: 12000 },
      );
      row.beforeDetailRetry = {
        ready: (await state()).ready,
        detail: (await state()).detail,
        resetEnabled: await page.locator("#reset").isEnabled(),
      };
      await page.locator("#surface").click();
    }
    await page.waitForFunction(
      () => murderBirdStudy.snapshot().detail === "full",
      null,
      { timeout: 60000, polling: 25 },
    );
    row.optInToFullMs = Math.round(
      (await page.evaluate(() => performance.now())) - start,
    );
    row.verifiedFullDigest = (await state()).modelDigest;

    if (details) {
      row.ax = await page.locator("main").ariaSnapshot();
      row.renderer = await page.locator("#canvas").evaluate((canvas) => {
        const gl = canvas.getContext("webgl2");
        const dbg = gl?.getExtension("WEBGL_debug_renderer_info");
        return dbg
          ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL)
          : gl?.getParameter(gl.RENDERER);
      });
      row.accessibility = await page.evaluate(() => ({
        unnamedButtons: [...document.querySelectorAll("button")]
          .filter(
            (b) =>
              b.offsetWidth &&
              !b.innerText.trim() &&
              !b.getAttribute("aria-label"),
          )
          .map((b) => b.id),
        unnamedInputs: [...document.querySelectorAll("input")]
          .filter((n) => !n.labels?.length && !n.getAttribute("aria-label"))
          .map((n) => n.id),
        canvasTabIndex: document.querySelector("canvas").tabIndex,
        canvasName: document.querySelector("canvas").getAttribute("aria-label"),
        landmarkCounts: [
          document.querySelectorAll("main").length,
          document.querySelectorAll("nav[aria-label]").length,
        ],
      }));
      const initial = await state();
      await page.locator("#canvas").focus();
      await page.keyboard.press("ArrowRight");
      const rotated = await state();
      row.keyboardOrbitDegrees =
        ((rotated.azimuth - initial.azimuth) * 180) / Math.PI;
      row.pressedViewAfterKeyboardOrbit = await page
        .locator("[data-view][aria-pressed=true]")
        .allTextContents();
      await page.keyboard.press("Home");
      row.exactCameraHome = (await state()).azimuth === initial.azimuth;
      await page.locator("#open").focus();
      await page.keyboard.press("Enter");
      const opened = await state();
      row.reducedMotionOpen = opened.open;
      row.openAria = await page.locator("#open").getAttribute("aria-expanded");
      await page.locator("#reset").focus();
      await page.keyboard.press("Enter");
      const reset = await state();
      row.closedExact =
        reset.open === 0 &&
        JSON.stringify(reset.joints) === JSON.stringify(initial.joints);
      for (const era of ["maker", "mechanic", "advanced"]) {
        await page.locator("[data-era=" + era + "]").focus();
        await page.keyboard.press("Enter");
        if (await page.locator("#cut-fraction").count()) {
          const panel = page.locator("#cut-fraction");
          await panel.focus();
          await panel.press("Home");
          for (let i = 0; i < 5; i++) await panel.press("PageUp");
          let c = +(await panel.inputValue());
          for (let i = 0; i < Math.abs(c - 50); i++)
            await panel.press(c < 50 ? "ArrowRight" : "ArrowLeft");
          row[era + "HalfCutaway"] = {
            open: (await state()).open,
            announced: await panel.getAttribute("aria-valuetext"),
            label: await page.locator("#cutaway").textContent(),
          };
          await panel.press("End");
          row[era + "FullCutaway"] = (await state()).open;
          await panel.press("Home");
          row[era + "ClosedCutaway"] = (await state()).open;
        }
        if (era === "maker") {
          if (!(await page.locator("#handle").isVisible()))
            throw Error("Maker handle not visible");
          await page.locator("#handle").focus();
          await page.keyboard.press("End");
          row.makerAtEnd = await page.locator("#handle").inputValue();
          await page.keyboard.press("Home");
        } else {
          await page.locator("#position").focus();
          await page.keyboard.press("End");
          row[era + "EndTime"] = (await state()).time;
          await page.keyboard.press("Home");
        }
      }
      await page.setViewportSize({ width: 390, height: 844 });
      if (await page.locator("#patrol").count()) {
        await page.locator("#patrol").focus();
        await page.keyboard.press("Enter");
        await page.waitForFunction(
          () =>
            murderBirdStudy.snapshot().mode === "patrol" &&
            murderBirdStudy.snapshot().time > 0.18,
        );
        await page.locator("#position").press("End");
        row.patrolDuration = (await state()).time;
        await page.locator("#reset").click();
      }
      row.narrowLayout = await page.evaluate(() => ({
        viewport: innerWidth,
        docWidth: document.documentElement.scrollWidth,
        overflow: document.documentElement.scrollWidth > innerWidth,
        canvasWidth: document.getElementById("canvas").clientWidth,
      }));
    }
  } catch (e) {
    row.failure = String(e).slice(0, 550);
  } finally {
    row.httpCount = requests.length;
    await context.close();
    resetSave();
    console.log(name, mode, row.ready, row.optInToReadyMs, row.failure || "");
  }
}
(async () => {
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  url = "http://127.0.0.1:" + server.address().port;

  const names = process.argv.slice(2).length
    ? process.argv.slice(2)
    : ["chromium", "webkit", "firefox", "edge"];
  for (const name of names) {
    let b;
    try {
      b = await launch(name);
      const modes =
        name === "chromium"
          ? [
              "fast",
              "fast",
              "fast",
              "slow",
              "slow",
              "slow",
              "fail",
              "retry",
              "retrydetail",
              "portable",
            ]
          : ["fast", "portable"];
      for (let i = 0; i < modes.length; i++)
        await run(b, name, modes[i], i === 0 || modes[i] === "portable");
    } catch (error) {
      result[name + "LaunchFailure"] = error.message;
      process.exitCode = 1;
    } finally {
      await b?.close();
    }
  }
  resetSave();
  server.close();
  assert(
    !result.runs.some((row) => row.failure),
    "A runtime case failed; inspect runtime-checks.json",
  );
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
  server.close();
});
